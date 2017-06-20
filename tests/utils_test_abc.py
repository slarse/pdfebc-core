# -*- coding: utf-8 -*-
"""Module containing an abstract base class for the utils test classes.

Author: Simon Larsén
"""
import unittest
import tempfile
import os
import configparser
from abc import ABCMeta
from .context import pdfebc_core

class UtilsTestABC(unittest.TestCase, metaclass=ABCMeta):
    NUM_ATTACHMENT_FILENAMES = 10

    @classmethod
    def setUpClass(cls):
        cls.user = 'test_user'
        cls.password = 'test_password'
        cls.receiver = 'test_receiver'
        cls.smtp_server = 'test_server'
        cls.smtp_port = 999
        cls.user_key = pdfebc_core.config_utils.USER_KEY
        cls.password_key = pdfebc_core.config_utils.PASSWORD_KEY
        cls.receiver_key = pdfebc_core.config_utils.RECEIVER_KEY
        cls.smtp_server_key = pdfebc_core.config_utils.SMTP_SERVER_KEY
        cls.smtp_port_key = pdfebc_core.config_utils.SMTP_PORT_KEY
        cls.gs_binary_default_key = pdfebc_core.config_utils.GS_DEFAULT_BINARY_KEY
        cls.out_dir_default_key = pdfebc_core.config_utils.OUT_DEFAULT_DIR_KEY
        cls.src_dir_default_key = pdfebc_core.config_utils.SRC_DEFAULT_DIR_KEY
        cls.email_section_key = pdfebc_core.config_utils.EMAIL_SECTION_KEY
        cls.default_section_key = pdfebc_core.config_utils.DEFAULT_SECTION_KEY
        cls.email_section_keys = {cls.user_key, cls.password_key, cls.receiver_key,
                                  cls.smtp_server_key, cls.smtp_port_key}
        cls.default_section_keys = {cls.gs_binary_default_key, cls.src_dir_default_key,
                                    cls.out_dir_default_key}
        cls.section_keys = {cls.email_section_key: cls.email_section_keys,
                            cls.default_section_key: cls.default_section_keys}
        cls.gs_binary_default = 'gs'
        cls.src_dir_default = '.'
        cls.out_dir_default = 'pdfebc_out'

    @classmethod
    def setUp(cls):
        cls.temp_config_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        cls.attachment_filenames = []
        for _ in range(cls.NUM_ATTACHMENT_FILENAMES):
            file = tempfile.NamedTemporaryFile(
                encoding='utf-8', suffix=pdfebc_core.compress.PDF_EXTENSION, mode='w', delete=False)
            cls.attachment_filenames.append(file.name)
            file.close()
        cls.valid_config = configparser.ConfigParser()
        cls.valid_config[pdfebc_core.config_utils.EMAIL_SECTION_KEY] = ({
            cls.user_key: cls.user,
            cls.password_key: cls.password,
            cls.receiver_key: cls.receiver,
            cls.smtp_server_key: cls.smtp_server,
            cls.smtp_port_key: cls.smtp_port})
        cls.valid_config[pdfebc_core.config_utils.DEFAULT_SECTION_KEY] = {
            cls.gs_binary_default_key: cls.gs_binary_default,
            cls.src_dir_default_key: cls.src_dir_default,
            cls.out_dir_default_key: cls.out_dir_default}
        cls.invalid_config = configparser.ConfigParser()
        cls.invalid_config[pdfebc_core.config_utils.EMAIL_SECTION_KEY] = {
            cls.user_key: cls.user,
            cls.password_key: cls.password}

    @classmethod
    def tearDown(cls):
        cls.temp_config_file.close()
        os.unlink(cls.temp_config_file.name)
        for filename in cls.attachment_filenames:
            os.unlink(filename)
