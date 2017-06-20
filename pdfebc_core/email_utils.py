# -*- coding: utf-8 -*-
"""Module containing email util functions for the pdfebc program.

The SMTP server and port are configured in the config.cnf file, see the config_utils module
for more information.

.. module:: utils
    :platform: Unix
    :synopsis: Email utility functions for pdfebc.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from .config_utils import (EMAIL_SECTION_KEY, USER_KEY, RECEIVER_KEY, PASSWORD_KEY, SMTP_PORT_KEY,
                           SMTP_SERVER_KEY, get_attribute_from_config, read_config, CONFIG_PATH,
                           ConfigurationError, check_config)
from .misc_utils import if_callable_call_with_formatted_string


SENDING_PRECONF = """Sending files ...
From: {}
To: {}
SMTP Server: {}
SMTP Port: {}

Files:
{}"""
FILES_SENT = "Files successfully sent!"""

def send_with_attachments(subject, message, filepaths, config):
    """Send an email from the user (a gmail) to the receiver.

    Args:
        subject (str): Subject of the email.
        message (str): A message.
        filepaths (list(str)): Filepaths to files to be attached.
        config (defaultdict): A defaultdict.
    """
    email_ = MIMEMultipart()
    email_.attach(MIMEText(message))
    email_["Subject"] = subject
    email_["From"] = get_attribute_from_config(config, EMAIL_SECTION_KEY, USER_KEY)
    email_["To"] = get_attribute_from_config(config, EMAIL_SECTION_KEY, RECEIVER_KEY)
    _attach_files(filepaths, email_)
    _send_email(email_, config)


def _attach_files(filepaths, email_):
    """Take a list of filepaths and attach the files to a MIMEMultipart.

    Args:
        filepaths (list(str)): A list of filepaths.
        email_ (email.MIMEMultipart): A MIMEMultipart email_.
    """
    for filepath in filepaths:
        base = os.path.basename(filepath)
        with open(filepath, "rb") as file:
            part = MIMEApplication(file.read(), Name=base)
            part["Content-Disposition"] = 'attachment; filename="%s"' % base
            email_.attach(part)

def _send_email(email_, config):
    """Send an email.

    Args:
        email_ (email.MIMEMultipart): The email to send.
        config (defaultdict): A defaultdict.
    """
    smtp_server = get_attribute_from_config(config, EMAIL_SECTION_KEY, SMTP_SERVER_KEY)
    smtp_port = int(get_attribute_from_config(config, EMAIL_SECTION_KEY, SMTP_PORT_KEY))
    user = get_attribute_from_config(config, EMAIL_SECTION_KEY, USER_KEY)
    password = get_attribute_from_config(config, EMAIL_SECTION_KEY, PASSWORD_KEY)
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(user, password)
    server.send_message(email_)
    server.quit()

def send_files_preconf(filepaths, config_path=CONFIG_PATH, status_callback=None):
    """Send files using the config.ini settings.

    Args:
        filepaths (list(str)): A list of filepaths.
    """
    config = read_config(config_path)
    subject = "PDF files from pdfebc"
    message = ""
    args = (get_attribute_from_config(config, EMAIL_SECTION_KEY, USER_KEY),
            get_attribute_from_config(config, EMAIL_SECTION_KEY, RECEIVER_KEY),
            get_attribute_from_config(config, EMAIL_SECTION_KEY, SMTP_SERVER_KEY),
            get_attribute_from_config(config, EMAIL_SECTION_KEY, SMTP_PORT_KEY),
            '\n'.join(filepaths))
    if_callable_call_with_formatted_string(status_callback, SENDING_PRECONF, *args)
    send_with_attachments(subject, message, filepaths, config)
    if_callable_call_with_formatted_string(status_callback, FILES_SENT)
