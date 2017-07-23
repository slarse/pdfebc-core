# -*- coding: utf-8 -*-
"""This module contains the PDF manipulation functions of the pdfebc program. Ghostscript is used to
compress PDF files.

.. module:: compress
    :platform: Unix
    :synopsis: PDF maniupulation functions using Ghostscript.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import os
import sys
import subprocess
import daiquiri
from .misc_utils import if_callable_call_with_formatted_string

BYTES_PER_MEGABYTE = 1024**2
FILE_SIZE_LOWER_LIMIT = BYTES_PER_MEGABYTE
PDF_EXTENSION = ".pdf"

COMPRESSING_MULTIPLE = """Source directory: '{}'
Output directory: '{}'
Found '{}' PDF files. Starting compression ..."""
ALL_FILES_DONE = """All files done!
Results saved to '{}'"""
COMPRESSING = "Compressing '{}' ..."
FILE_DONE = "File done! Result saved to '{}'"
NOT_COMPRESSING = """Not compressing '{}'
Reason: Actual file size is {} bytes,
lower limit for compression is {} bytes"""
GS_NOT_INSTALLED = """Ghostscript not installed or not aliased to '{}'.
Exiting ..."""

LOGGER = daiquiri.getLogger(__name__)

def _get_pdf_filenames_at(source_directory):
    """Find all PDF files in the specified directory.

    Args:
        source_directory (str): The source directory.

    Returns:
        list(str): Filepaths to all PDF files in the specified directory.

    Raises:
        ValueError
    """
    if not os.path.isdir(source_directory):
        raise ValueError("%s is not a directory!" % source_directory)
    return [os.path.join(source_directory, filename)
            for filename in os.listdir(source_directory)
            if filename.endswith(PDF_EXTENSION)]

def compress_pdf(filepath, output_path, ghostscript_binary):
    """Compress a single PDF file.

    Args:
        filepath (str): Path to the PDF file.
        output_path (str): Output path.
        ghostscript_binary (str): Name/alias of the Ghostscript binary.

    Raises:
        ValueError
        FileNotFoundError
    """
    if not filepath.endswith(PDF_EXTENSION):
        raise ValueError("Filename must end with .pdf!\n%s does not." % filepath)
    try:
        file_size = os.stat(filepath).st_size
        if file_size < FILE_SIZE_LOWER_LIMIT:
            LOGGER.info(NOT_COMPRESSING.format(filepath, file_size, FILE_SIZE_LOWER_LIMIT))
            process = subprocess.Popen(['cp', filepath, output_path])
        else:
            LOGGER.info(COMPRESSING.format(filepath))
            process = subprocess.Popen(
                [ghostscript_binary, "-sDEVICE=pdfwrite",
                 "-dCompatabilityLevel=1.4", "-dPDFSETTINGS=/ebook",
                 "-dNOPAUSE", "-dQUIET", "-dBATCH",
                 "-sOutputFile=%s" % output_path, filepath]
                )
    except FileNotFoundError:
        msg = GS_NOT_INSTALLED.format(ghostscript_binary)
        raise FileNotFoundError(msg)
    process.communicate()
    LOGGER.info(FILE_DONE.format(output_path))

def compress_multiple_pdfs(source_directory, output_directory, ghostscript_binary):
    """Compress all PDF files in the current directory and place the output in the
    given output directory. This is a generator function that first yields the amount
    of files to be compressed, and then yields the output path of each file.

    Args:
        source_directory (str): Filepath to the source directory.
        output_directory (str): Filepath to the output directory.
        ghostscript_binary (str): Name of the Ghostscript binary.

    Returns:
        list(str): paths to outputs.
    """
    source_paths = _get_pdf_filenames_at(source_directory)
    yield len(source_paths)
    for source_path in source_paths:
        output = os.path.join(output_directory, os.path.basename(source_path))
        compress_pdf(source_path, output, ghostscript_binary)
        yield output
