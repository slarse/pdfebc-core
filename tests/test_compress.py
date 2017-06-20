# -*- coding: utf-8 -*-
"""Unit tests for the compress module.

Author: Simon Larsén
"""
import unittest
import tempfile
import os
from unittest.mock import Mock, patch
from .context import pdfebc_core

PDF_FILE_EXTENSION = '.pdf'
OTHER_FILE_EXTENSIONS = ['.png', '.bmp', '.txt', '.sh', '.py']

class ExitTestException(Exception):
    pass

def create_temporary_files_with_suffixes(directory, suffixes=[PDF_FILE_EXTENSION],
                                         files_per_suffix=20, delete=False):
    """Create an arbitrary amount of tempfile.NamedTemporaryFile files with given suffixes.
    Note that the files are NOT deleted automatically, so should be used in a tempfile.TemporaryDirectory
    context to avoid having to clean them up manually.

    Args:
        directory (str): Path to the directory to create the files in.
        suffixes ([str]): List of suffixes of the files to create.
        files_per_suffix (int): Amount of files to create per suffix.

    Returns:
        [tempfile.NamedTemporaryFile]: A list of tempfile.NamedTemporaryFile.
    """
    files = [tempfile.NamedTemporaryFile(suffix=suffix, dir=directory, delete=delete)
                 for i in range(files_per_suffix) for suffix in suffixes]
    return files

class CoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_size_lower_limit = pdfebc_core.compress.FILE_SIZE_LOWER_LIMIT
        cls.gs_binary = 'gs'

    @classmethod
    def setUp(cls):
        cls.trash_can = tempfile.TemporaryDirectory()
        cls.default_trash_file = os.path.join(cls.trash_can.name, 'default')
        pdfebc_core.compress.FILE_SIZE_LOWER_LIMIT = cls.file_size_lower_limit


    def test_get_pdf_filenames_from_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepaths = pdfebc_core.compress._get_pdf_filenames_at(tmpdir)
            self.assertFalse(filepaths)

    def test_get_pdf_filenames_from_dir_with_only_pdfs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = create_temporary_files_with_suffixes(tmpdir)
            filepaths = pdfebc_core.compress._get_pdf_filenames_at(tmpdir)
            self.assert_filepaths_match_file_names(filepaths, files)

    def test_get_pdf_filenames_from_dir_with_only_other_extensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = create_temporary_files_with_suffixes(tmpdir, suffixes=OTHER_FILE_EXTENSIONS)
            filepaths = pdfebc_core.compress._get_pdf_filenames_at(tmpdir)
            self.assertFalse(filepaths)

    def test_get_pdf_filenames_from_dir_that_does_not_exist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # TemporaryDirectory is deleted upon exiting with-context
            path_to_dir = tmpdir
        with self.assertRaises(ValueError) as context:
            pdfebc_core.compress._get_pdf_filenames_at(path_to_dir)

    def test_get_pdf_filenames_from_dir_with_mixed_file_extensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            amount_of_pdfs = 10
            pdf_files = create_temporary_files_with_suffixes(tmpdir, files_per_suffix=amount_of_pdfs)
            non_pdf_files = create_temporary_files_with_suffixes(tmpdir, suffixes=OTHER_FILE_EXTENSIONS)
            filepaths = pdfebc_core.compress._get_pdf_filenames_at(tmpdir)
            self.assert_filepaths_match_file_names(filepaths, pdf_files)

    def test_compress_non_pdf_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            non_pdf_file = create_temporary_files_with_suffixes(tmpdir,
                                                                suffixes=OTHER_FILE_EXTENSIONS,
                                                                files_per_suffix=1).pop()
            non_pdf_filename = non_pdf_file.name
            with self.assertRaises(ValueError) as context:
                pdfebc_core.compress.compress_pdf(non_pdf_filename,
                                         self.default_trash_file,
                                         self.gs_binary)

    def test_compress_pdf_that_does_not_exist(self):
        with tempfile.NamedTemporaryFile() as file:
            filename = file.name
        with self.assertRaises(ValueError) as context:
            pdfebc_core.compress.compress_pdf(filename, self.default_trash_file, self.gs_binary)

    def test_compress_too_small_pdf(self):
        with tempfile.TemporaryDirectory(dir=self.trash_can.name) as tmpoutdir:
            mock_status_callback = Mock(return_value=None)
            pdf_file = create_temporary_files_with_suffixes(self.trash_can.name,
                                                            files_per_suffix=1)[0]
            pdf_file.close()
            output_path = os.path.join(tmpoutdir, os.path.basename(pdf_file.name))
            pdfebc_core.compress.compress_pdf(pdf_file.name, output_path,
                                              self.gs_binary, mock_status_callback)
            expected_not_compressing_message = pdfebc_core.compress.NOT_COMPRESSING.format(
                pdf_file.name, 0,
                pdfebc_core.compress.FILE_SIZE_LOWER_LIMIT)
            expected_done_message = pdfebc_core.compress.FILE_DONE.format(output_path)
            mock_status_callback.assert_any_call(expected_not_compressing_message)
            mock_status_callback.assert_any_call(expected_done_message)

    @patch('subprocess.Popen', autospec=True)
    def test_compress_adequately_sized_pdf(self, mock_popen):
        # change the lower limit for file size, is reset in the setUp method
        pdfebc_core.compress.FILE_SIZE_LOWER_LIMIT = 0
        with tempfile.TemporaryDirectory(dir=self.trash_can.name) as tmpoutdir:
            mock_status_callback = Mock(return_value=None)
            pdf_file = create_temporary_files_with_suffixes(self.trash_can.name,
                                                            files_per_suffix=1)[0]
            pdf_file.close()
            output_path = os.path.join(tmpoutdir, os.path.basename(pdf_file.name))
            pdfebc_core.compress.compress_pdf(pdf_file.name, output_path,
                                              self.gs_binary, mock_status_callback)
            mock_popen.assert_called_once()
            mock_popen_instance = mock_popen([])
            mock_popen_instance.communicate.assert_called_once()
            mock_status_callback.assert_called()
            expected_compressing_message = pdfebc_core.compress.COMPRESSING.format(pdf_file.name)
            expected_done_message = pdfebc_core.compress.FILE_DONE.format(output_path)
            mock_status_callback.assert_any_call(expected_compressing_message)
            mock_status_callback.assert_any_call(expected_done_message)

    def test_compress_multiple_pdfs_with_missing_source_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir_path = tmpdir
        with self.assertRaises(ValueError):
            pdfebc_core.compress.compress_multiple_pdfs(src_dir_path, self.trash_can.name,
                                                        self.gs_binary)

    @patch('pdfebc_core.compress.compress_pdf')
    def test_compress_multiple_pdfs_that_dont_exist(self, mock_compress):
        with tempfile.TemporaryDirectory() as tmp_src_dir:
            files = create_temporary_files_with_suffixes(tmp_src_dir, delete=True)
            filenames = [file.name for file in files]
            for file in files:
                file.close()
            with tempfile.TemporaryDirectory() as tmp_out_dir:
                pdfebc_core.compress.compress_multiple_pdfs(tmp_src_dir, tmp_out_dir,
                                                            self.gs_binary)
        self.assertFalse(mock_compress.called)

    @patch('sys.exit', side_effect=ExitTestException())
    @patch('subprocess.Popen', side_effect=FileNotFoundError(), autospec=True)
    def test_compress_pdf_gs_binary_not_found(self, mock_popen, mock_sys_exit):
        # change the lower limit for file size, is reset in the setUp method
        pdfebc_core.compress.FILE_SIZE_LOWER_LIMIT = 0
        with tempfile.TemporaryDirectory(dir=self.trash_can.name) as tmpoutdir:
            mock_status_callback = Mock(return_value=None)
            pdf_file = create_temporary_files_with_suffixes(self.trash_can.name,
                                                            files_per_suffix=1)[0]
            pdf_file.close()
            output_path = os.path.join(tmpoutdir, os.path.basename(pdf_file.name))
            with self.assertRaises(ExitTestException):
                pdfebc_core.compress.compress_pdf(pdf_file.name, output_path,
                                                  self.gs_binary, mock_status_callback)

    @patch('pdfebc_core.compress.compress_pdf', autospec=True)
    def test_compress_multiple_valid_pdfs(self, mock_compress):
        # change the lower limit for file size, is reset in the setUp method
        pdfebc_core.compress.FILE_SIZE_LOWER_LIMIT = 0
        with tempfile.TemporaryDirectory(dir=self.trash_can.name) as tmpoutdir:
            pdf_files = create_temporary_files_with_suffixes(self.trash_can.name)
            source_paths = list()
            output_paths = list()
            for file in pdf_files:
                file.close()
                source_paths.append(file.name)
                output_path = os.path.join(tmpoutdir, os.path.basename(file.name))
                output_paths.append(output_path)
            pdfebc_core.compress.compress_multiple_pdfs(self.trash_can.name, tmpoutdir,
                                                        self.gs_binary)
            for source_path, output_path in zip(source_paths, output_paths):
                mock_compress.assert_any_call(source_path, output_path, self.gs_binary, None)

    def assert_filepaths_match_file_names(self, filepaths, temporary_files):
        """Assert that a list of filepaths match a list of temporary files.

        Args:
            filepaths ([str]): A list of filepaths.
            temporary_files (tempfile.NamedTemporaryFile): A list of tempfile.NamedTemporaryFile.
        """
        self.assertEqual(len(temporary_files), len(filepaths))
        sorted_filepaths = sorted(filepaths)
        sorted_temporary_files = sorted(temporary_files, key=lambda tmpfile: tmpfile.name)
        for filepath, tmpfile in zip(sorted_filepaths, sorted_temporary_files):
            self.assertEqual(filepath, tmpfile.name)
