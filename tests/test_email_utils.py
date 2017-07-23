# -*- coding: utf-8 -*-
"""Unit tests for the email_utils module.

Author: Simon Larsén
"""
import os
import email
import asyncio
import asynctest
from email.mime.multipart import MIMEMultipart
from unittest.mock import patch, Mock
from .utils_test_abc import UtilsTestABC
from .context import pdfebc_core

class EmailUtilsTest(UtilsTestABC):
    def set_up_smtp_instance_mock(self, mock_smtp):
        mock_smtp_instance = mock_smtp()
        mock_smtp_instance.connect = asynctest.CoroutineMock()
        mock_smtp_instance.starttls = asynctest.CoroutineMock()
        mock_smtp_instance.login = asynctest.CoroutineMock()
        mock_smtp_instance.quit = asynctest.CoroutineMock()
        mock_smtp_instance.send_message = asynctest.CoroutineMock()
        return mock_smtp_instance

    def test_attach_valid_files(self):
        email_ = MIMEMultipart()
        pdfebc_core.email_utils._attach_files(self.attachment_filenames, email_)
        expected_filenames = list(self.attachment_filenames)
        part_dispositions = [part.get('Content-Disposition')
                             for part in email.message_from_bytes(email_.as_bytes()).walk()
                             if part.get_content_maintype() == 'application']
        for filename_base in map(os.path.basename, self.attachment_filenames):
            self.assertTrue(
                any(map(lambda disp: filename_base in disp, part_dispositions)))

    @asynctest.patch('aiosmtplib.SMTP', autospec=True)
    def test_send_valid_email(self, mock_smtp):
        subject = "Test e-mail"
        email_ = MIMEMultipart()
        email_['From'] = self.user
        email_['To'] = self.receiver
        email_['Subject'] = subject
        mock_smtp_instance = self.set_up_smtp_instance_mock(mock_smtp)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            pdfebc_core.email_utils._send_email(email_, self.valid_config._sections))
        mock_smtp.assert_any_call(
            hostname=self.smtp_server, port=self.smtp_port, loop=loop, use_tls=False)
        mock_smtp_instance.connect.assert_called_once()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once_with(email_)
        mock_smtp_instance.quit.assert_called_once()

    @asynctest.patch('aiosmtplib.SMTP')
    def test_send_valid_email_with_attachments(self, mock_smtp):
        subject = "Test e-mail"
        message = "Test e-mail body"
        mock_smtp_instance = self.set_up_smtp_instance_mock(mock_smtp)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            pdfebc_core.email_utils.send_with_attachments(subject, message, self.attachment_filenames,
                                                          self.valid_config._sections))
        mock_smtp.assert_any_call(
            hostname=self.smtp_server, port=self.smtp_port, loop=loop, use_tls=False)
        mock_smtp_instance.connect.assert_called_once()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()

    @asynctest.patch('aiosmtplib.SMTP')
    def test_send_files_preconf_valid_files(self, mock_smtp):
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        mock_smtp_instance = self.set_up_smtp_instance_mock(mock_smtp)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            pdfebc_core.email_utils.send_files_preconf(self.attachment_filenames,
                                                       config_path=self.temp_config_file.name))
        mock_smtp.assert_any_call(
            hostname=self.smtp_server, port=self.smtp_port, loop=loop, use_tls=False)
        mock_smtp_instance.connect.assert_called_once()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()
