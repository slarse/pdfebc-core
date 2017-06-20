# -*- coding: utf-8 -*-
"""Unit tests for the email_utils module.

Author: Simon Larsén
"""
import os
import email
from email.mime.multipart import MIMEMultipart
from unittest.mock import patch, Mock
from .utils_test_abc import UtilsTestABC
from .context import pdfebc_core

class EmailUtilsTest(UtilsTestABC):
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

    @patch('smtplib.SMTP')
    def test_send_valid_email(self, mock_smtp):
        subject = "Test e-mail"
        email_ = MIMEMultipart()
        email_['From'] = self.user
        email_['To'] = self.receiver
        email_['Subject'] = subject
        pdfebc_core.email_utils._send_email(email_, self.valid_config._sections)
        mock_smtp.assert_called_once_with(self.smtp_server, self.smtp_port)
        mock_smtp_instance = mock_smtp()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once_with(email_)
        mock_smtp_instance.quit.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_valid_email_with_attachments(self, mock_smtp):
        subject = "Test e-mail"
        message = "Test e-mail body"
        pdfebc_core.email_utils.send_with_attachments(subject, message, self.attachment_filenames,
                                                      self.valid_config._sections)
        mock_smtp.assert_called_once_with(self.smtp_server, self.smtp_port)
        mock_smtp_instance = mock_smtp()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_files_preconf_valid_files(self, mock_smtp):
        mock_smtp_instance = mock_smtp()
        mock_status_callback = Mock(return_value=None)
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        pdfebc_core.email_utils.send_files_preconf(self.attachment_filenames,
                                                   config_path=self.temp_config_file.name,
                                                   status_callback=mock_status_callback)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()
        expected_send_message = pdfebc_core.email_utils.SENDING_PRECONF.format(
            self.user, self.receiver,
            self.smtp_server, self.smtp_port, '\n'.join(self.attachment_filenames))
        expected_sent_message = pdfebc_core.email_utils.FILES_SENT
        mock_status_callback.assert_any_call(expected_send_message)
        mock_status_callback.assert_any_call(expected_sent_message)
