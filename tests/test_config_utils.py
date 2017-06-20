"""Tests for the config_util module.

Author: Simon Larsén
"""
import tempfile
import configparser
import os
from unittest.mock import patch, Mock
from .utils_test_abc import UtilsTestABC
from .context import pdfebc_core

class ConfigUtilsTest(UtilsTestABC):
    def test_create_config(self):
        sections = self.section_keys.keys()
        section_contents = [{
            self.user_key: self.user,
            self.password_key: self.password,
            self.receiver_key: self.receiver,
            self.smtp_server_key: pdfebc_core.config_utils.DEFAULT_SMTP_SERVER,
            self.smtp_port_key: str(pdfebc_core.config_utils.DEFAULT_SMTP_PORT)},
           {self.gs_binary_default_key: self.gs_binary_default,
            self.src_dir_default_key: self.src_dir_default,
            self.out_dir_default_key: self.out_dir_default}]
        config = pdfebc_core.config_utils.create_config(sections, section_contents)
        for section, section_content in zip(sections, section_contents):
            config_section = config[section]
            for section_content_key, section_content_value in section_content.items():
                self.assertEqual(section_content_value, config_section[section_content_key])

    def test_create_config_too_few_sections(self):
        sections = ["EMAIL"]
        section_contents = [{1: 2, 3: 4}, {1: 2}]
        with self.assertRaises(ValueError):
            pdfebc_core.config_utils.create_config(sections, section_contents)

    def test_write_valid_email_config(self):
        self.temp_config_file.close()
        pdfebc_core.config_utils.write_config(self.valid_config, self.temp_config_file.name)
        config = configparser.ConfigParser()
        with open(self.temp_config_file.name) as file:
            config.read_file(file)
        section = config[pdfebc_core.config_utils.EMAIL_SECTION_KEY]
        self.assertEqual(self.user, section[self.user_key])
        self.assertEqual(self.password, section[self.password_key])
        self.assertEqual(self.receiver, section[self.receiver_key])

    @patch('os.makedirs', return_value=None)
    @patch('pdfebc_core.config_utils.open')
    def test_write_email_config_missing_dir(self, mock_open, mock_makedirs):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = tempfile.NamedTemporaryFile(dir=tmpdir).name
        mock_open.return_value.__enter__.return_value.name = 'badonkadonk'
        mock_config = Mock()
        pdfebc_core.config_utils.write_config(mock_config, config_path)
        mock_makedirs.assert_called_once_with(os.path.dirname(config_path))
        mock_open.assert_called_once_with(config_path, 'w', encoding='utf-8')

    def test_read_valid_email_config(self):
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.flush()
        self.temp_config_file.close()
        email_section = pdfebc_core.config_utils.read_config(self.temp_config_file.name)[
            pdfebc_core.config_utils.EMAIL_SECTION_KEY]
        actual_user = email_section[self.user_key]
        actual_password = email_section[self.password_key]
        actual_receiver = email_section[self.receiver_key]
        actual_smtp_server = email_section[self.smtp_server_key]
        actual_smtp_port = int(email_section[self.smtp_port_key])
        self.assertEqual(self.user, actual_user)
        self.assertEqual(self.password, actual_password)
        self.assertEqual(self.receiver, actual_receiver)
        self.assertEqual(self.smtp_server, actual_smtp_server)
        self.assertEqual(self.smtp_port, actual_smtp_port)

    def test_read_config_no_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            config_path = tmp.name
        with self.assertRaises(IOError):
            pdfebc_core.config_utils.read_config(config_path)

    def test_create_email_config(self):
        section_key = pdfebc_core.config_utils.EMAIL_SECTION_KEY
        user_key = self.user_key
        password_key = self.password_key
        receiver_key = self.receiver_key
        actual_user = self.valid_config[section_key][user_key]
        actual_password = self.valid_config[section_key][password_key]
        actual_receiver = self.valid_config[section_key][receiver_key]
        self.assertEqual(self.user, actual_user)
        self.assertEqual(self.password, actual_password)
        self.assertEqual(self.receiver, actual_receiver)

    def test_valid_config_exists_no_config(self):
        with tempfile.NamedTemporaryFile() as file:
            config_path = file.name
        self.assertFalse(pdfebc_core.config_utils.valid_config_exists(config_path))

    def test_valid_config_exists_with_valid_config(self):
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        config_path = self.temp_config_file.name
        self.assertTrue(pdfebc_core.config_utils.valid_config_exists(config_path))

    def test_valid_config_exists_with_invalid_config(self):
        self.invalid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        config_path = self.temp_config_file.name
        self.assertFalse(pdfebc_core.config_utils.valid_config_exists(config_path))

    def test_valid_config_exists_with_only_sections(self):
        sections_string = "[{}]\n[{}]".format(self.email_section_key,
                                              self.default_section_key)
        self.temp_config_file.write(sections_string)
        self.temp_config_file.close()
        self.assertFalse(pdfebc_core.config_utils.valid_config_exists(self.temp_config_file.name))

    def test_run_config_diagnostics_valid_config(self):
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        config_path, missing_sections, malformed_entries = pdfebc_core.config_utils.run_config_diagnostics(
            self.temp_config_file.name)
        self.assertEqual(self.temp_config_file.name, config_path)
        self.assertFalse(missing_sections)
        self.assertFalse(malformed_entries)

    def test_run_config_diagnostics_empty_config(self):
        config = configparser.ConfigParser()
        config.write(self.temp_config_file)
        config_path, missing_sections, malformed_entries = pdfebc_core.config_utils.run_config_diagnostics(
            self.temp_config_file.name)
        self.assertEqual(self.temp_config_file.name, config_path)
        self.assertEqual(self.section_keys.keys(), missing_sections)
        self.assertFalse(malformed_entries)

    def test_run_config_diagnostics_empty_sections(self):
        config = configparser.ConfigParser()
        for section in self.section_keys.keys():
            config[section] = {}
        config.write(self.temp_config_file)
        config_path, missing_sections, malformed_entries = pdfebc_core.config_utils.run_config_diagnostics(
            self.temp_config_file.name)
        self.assertEqual(self.temp_config_file.name, config_path)
        self.assertEqual(self.section_keys.keys(), missing_sections)
        self.assertFalse(malformed_entries)

    def test_run_config_diagnostics_missing_section_and_options(self):
        self.invalid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        config_path, missing_sections, malformed_entries = pdfebc_core.config_utils.run_config_diagnostics(
            self.temp_config_file.name)
        self.assertEqual(self.temp_config_file.name, config_path)
        expected_missing_email_options = self.email_section_keys - {self.user_key, self.password_key}
        self.assertEqual({self.default_section_key}, missing_sections)
        self.assertEqual(expected_missing_email_options, malformed_entries[self.email_section_key])

    def test_config_to_string(self):
        gs_binary_default = "gs"
        section_string = "[{}]"
        option_string = "{} = {}"
        config = {self.default_section_key: {self.gs_binary_default_key: gs_binary_default},
                  self.email_section_key: {self.user_key: self.user, self.password_key: self.password}}
        expected_output = "\n".join([section_string.format(self.default_section_key),
                                     option_string.format(self.gs_binary_default_key, gs_binary_default),
                                     section_string.format(self.email_section_key),
                                     option_string.format(self.user_key, self.user),
                                     option_string.format(self.password_key, self.password)])
        print(expected_output)
        actual_output = pdfebc_core.config_utils.config_to_string(config)
        self.assertEqual(expected_output, actual_output)

    def test_get_attribute_from_config_from_missing_section(self):
        config_dict = {self.email_section_key: {self.user_key: self.user}}
        non_existing_section = "This section does not exist"
        equally_non_existing_attribute = "This attribute doesn't exist either"
        with self.assertRaises(pdfebc_core.config_utils.ConfigurationError):
            pdfebc_core.config_utils.get_attribute_from_config(config_dict, non_existing_section,
                                                  equally_non_existing_attribute)

    def test_get_attribute_from_config_from_section_with_missing_attribute(self):
        config_dict = {self.email_section_key: {self.user_key: self.user}}
        non_existing_section = "Badonkadonk. This doesn't exist"
        with self.assertRaises(pdfebc_core.config_utils.ConfigurationError):
            pdfebc_core.config_utils.get_attribute_from_config(config_dict, self.email_section_key,
                                                  non_existing_section)
