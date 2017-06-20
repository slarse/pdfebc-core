# -*- coding: utf-8 -*-
"""Module containing util functions relating to the configuration of pdfebc.

The SMTP server and port are configured in the config.cnf file.

Requires a config file called 'config.cnf' in the user conf directory specified by appdirs. In the
case of Arch Linux, this is '$HOME/.config/pdfebc/config.cnf', but this may vary with distributions.
The config file should have the following format:

| [EMAIL]
| user = <sender_email>
| pass = <password>
| receiver = <receiver_email>
| smtp_server = <smtp_server>
| smtp_port = <smtp_port>
| 
| [DEFAULTS]
| gs_binary = <ghostscript_binary>
| src = <source_dir>
| out = <out_dir>

.. module:: config_utils
    :platform: Unix
    :synopsis: Configuration utility functions.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import os
import configparser
from collections import defaultdict
import appdirs

CONFIG_FILENAME = 'config.cnf'
CONFIG_PATH = os.path.join(appdirs.user_config_dir('pdfebc'), CONFIG_FILENAME)
EMAIL_SECTION_KEY = "EMAIL"
PASSWORD_KEY = "pass"
USER_KEY = "user"
RECEIVER_KEY = "receiver"
DEFAULT_SMTP_SERVER = "smtp.gmail.com"
DEFAULT_SMTP_PORT = 587
SMTP_SERVER_KEY = "smtp_server"
SMTP_PORT_KEY = "smtp_port"
EMAIL_SECTION_KEYS = {USER_KEY, PASSWORD_KEY, RECEIVER_KEY, SMTP_SERVER_KEY, SMTP_PORT_KEY}
DEFAULT_SECTION_KEY = "DEFAULTS"
GS_DEFAULT_BINARY_KEY = "gs_binary"
SRC_DEFAULT_DIR_KEY = "src"
OUT_DEFAULT_DIR_KEY = "out"
DEFAULT_SECTION_KEYS = {GS_DEFAULT_BINARY_KEY, SRC_DEFAULT_DIR_KEY, OUT_DEFAULT_DIR_KEY}
SECTION_KEYS = {EMAIL_SECTION_KEY: EMAIL_SECTION_KEYS,
                DEFAULT_SECTION_KEY: DEFAULT_SECTION_KEYS}

class ConfigurationError(configparser.ParsingError):
    """Error thrown whenever something is wrong with the configuration file."""
    pass

def create_config(sections, section_contents):
    """Create a config file from the provided sections and key value pairs.

    Args:
        sections (List[str]): A list of section keys.
        key_value_pairs (Dict[str, str]): A list of of dictionaries. Must be as long as
        the list of sections. That is to say, if there are two sections, there should be two
        dicts.
    Returns:
        configparser.ConfigParser: A ConfigParser.
    Raises:
        ValueError
    """
    sections_length, section_contents_length = len(sections), len(section_contents)
    if sections_length != section_contents_length:
        raise ValueError("Mismatch between argument lengths.\n"
                         "len(sections) = {}\n"
                         "len(section_contents) = {}"
                         .format(sections_length, section_contents_length))
    config = configparser.ConfigParser()
    for section, section_content in zip(sections, section_contents):
        config[section] = section_content
    return config

def write_config(config, config_path=CONFIG_PATH):
    """Write the config to the output path.
    Creates the necessary directories if they aren't there.

    Args:
        config (configparser.ConfigParser): A ConfigParser.
    """
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path))
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)

def read_config(config_path=CONFIG_PATH):
    """Read the config information from the config file.

    Args:
        config_path (str): Relative path to the email config file.
    Returns:
        defaultdict: A defaultdict with the config information.
    Raises:
        IOError
    """
    if not os.path.isfile(config_path):
        raise IOError("No config file found at %s" % config_path)
    config_parser = configparser.ConfigParser()
    config_parser.read(config_path)
    config = _config_parser_to_defaultdict(config_parser)
    return config

def check_config(config):
    """Check that all sections of the config contain the keys that they should.

    Args:
        config (defaultdict): A defaultdict.
    Raises:
        ConfigurationError
    """
    for section, expected_section_keys in SECTION_KEYS.items():
        section_content = config.get(section)
        if not section_content:
            raise ConfigurationError("Config file badly formed! Section {} is missing."
                                     .format(section))
        elif not _section_is_healthy(section_content, expected_section_keys):
            raise ConfigurationError("The {} section of the configuration file is badly formed!"
                                     .format(section))

def run_config_diagnostics(config_path=CONFIG_PATH):
    """Run diagnostics on the configuration file.

    Args:
        config_path (str): Path to the configuration file.
    Returns:
        str, Set[str], dict(str, Set[str]): The path to the configuration file, a set of missing
        sections and a dict that maps each section to the entries that have either missing or empty
        options.
    """
    config = read_config(config_path)
    missing_sections = set()
    malformed_entries = defaultdict(set)
    for section, expected_section_keys in SECTION_KEYS.items():
        section_content = config.get(section)
        if not section_content:
            missing_sections.add(section)
        else:
            for option in expected_section_keys:
                option_value = section_content.get(option)
                if not option_value:
                    malformed_entries[section].add(option)
    return config_path, missing_sections, malformed_entries

def get_attribute_from_config(config, section, attribute):
    """Try to parse an attribute of the config file.

    Args:
        config (defaultdict): A defaultdict.
        section (str): The section of the config file to get information from.
        attribute (str): The attribute of the section to fetch.
    Returns:
        str: The string corresponding to the section and attribute.
    Raises:
        ConfigurationError
    """
    section = config.get(section)
    if section:
        option = section.get(attribute)
        if option:
            return option
    raise ConfigurationError("Config file badly formed!\n"
                             "Failed to get attribute '{}' from section '{}'!"
                             .format(attribute, section))

def valid_config_exists(config_path=CONFIG_PATH):
    """Verify that a valid config file exists.

    Args:
        config_path (str): Path to the config file.

    Returns:
        boolean: True if there is a valid config file, false if not.
    """
    if os.path.isfile(config_path):
        try:
            config = read_config(config_path)
            check_config(config)
        except (ConfigurationError, IOError):
            return False
    else:
        return False
    return True

def config_to_string(config):
    """Nice output string for the config, which is a nested defaultdict.

    Args:
        config (defaultdict(defaultdict)): The configuration information.
    Returns:
        str: A human-readable output string detailing the contents of the config.
    """
    output = []
    for section, section_content in config.items():
        output.append("[{}]".format(section))
        for option, option_value in section_content.items():
            output.append("{} = {}".format(option, option_value))
    return "\n".join(output)

def _config_parser_to_defaultdict(config_parser):
    """Convert a ConfigParser to a defaultdict.

    Args:
        config_parser (ConfigParser): A ConfigParser.
    """
    config = defaultdict(defaultdict)
    for section, section_content in config_parser.items():
        if section != 'DEFAULT':
            for option, option_value in section_content.items():
                config[section][option] = option_value
    return config

def _section_is_healthy(section, expected_keys):
    """Check that the section contains all keys it should.

    Args:
        section (defaultdict): A defaultdict.
        expected_keys (Iterable): A Set of keys that should be contained in the section.
    Returns:
        boolean: True if the section is healthy, false if not.
    """
    return set(section.keys()) == set(expected_keys)
