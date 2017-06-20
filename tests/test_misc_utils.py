# -*- coding: utf-8 -*-
"""Unit tests for the utils module.

Author: Simon Larsén
"""
from unittest.mock import patch, Mock
from .context import pdfebc_core
from .utils_test_abc import UtilsTestABC

class MiscUtilsTest(UtilsTestABC):
    def test_if_callable_call_with_formatted_string_too_few_args(self):
        three_args_formattable_string = "test {} test {} test {}"
        mock_callback = Mock(return_value=None)
        args = ("test", "test")
        with self.assertRaises(ValueError):
            pdfebc_core.misc_utils.if_callable_call_with_formatted_string(
                mock_callback,
                three_args_formattable_string,
                *args)

    def test_if_callable_call_with_formatted_string_valid_args(self):
        three_args_formattable_string = "test {} test {} test {}"
        args = ("test", "test", "test")
        mock_callback = Mock(return_vale=None)
        pdfebc_core.misc_utils.if_callable_call_with_formatted_string(
            mock_callback,
            three_args_formattable_string,
            *args)
        mock_callback.assert_called_once_with(
            three_args_formattable_string.format(*args))

    @patch('pdfebc_core.misc_utils.callable', return_value=False)
    def test_if_callable_call_with_formatted_string_not_callable_too_few_args(self, mock_callable):
        three_args_formattable_string = "test {} test {} test {}"
        args = ("test", "test")
        mock_callback = Mock(return_value=None)
        with self.assertRaises(ValueError):
            pdfebc_core.misc_utils.if_callable_call_with_formatted_string(
                mock_callback,
                three_args_formattable_string,
                *args)

    @patch('pdfebc_core.misc_utils.callable', return_value=False)
    def test_if_callable_call_with_formatted_string_not_callable_valid_args(self, mock_callable):
        three_args_formattable_string = "test {} test {} test {}"
        args = ("test", "test", "test")
        mock_callback = Mock(return_value=None)
        pdfebc_core.misc_utils.if_callable_call_with_formatted_string(
            mock_callback,
            three_args_formattable_string,
            *args)
        self.assertFalse(mock_callback.called)
