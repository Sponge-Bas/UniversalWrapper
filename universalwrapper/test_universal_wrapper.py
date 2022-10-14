# Copyright 2022 by Bas de Bruijne
# All rights reserved.
# Universal Wrapper comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this module.
#
# Any changes made to UniversalWrapper must be covered by one of the unit tests
# below. Expected outputs can not be changed to accommodate for new changes.
# To run the unittests:
# $ python3 -m coverage run -m unittest
# $ python3 -m coverage report --include universal_wrapper.py

import asyncio
import subprocess
import unittest
import universal_wrapper

from mock import patch, AsyncMock, ANY
from universal_wrapper import UniversalWrapper


class TestUniversalWrapper(unittest.TestCase):
    @patch("universal_wrapper.subprocess.check_output")
    def test_basic_cases(self, mock_check_output):
        uw_test = UniversalWrapper("uw_test")

        uw_test("a")
        mock_check_output.assert_called_with(["uw-test", "a"])
        uw_test.run("a")
        mock_check_output.assert_called_with(["uw-test", "run", "a"])
        uw_test.run("a", b=True)
        mock_check_output.assert_called_with(["uw-test", "run", "a", "-b"])
        uw_test.run("a", bar=True)
        mock_check_output.assert_called_with(["uw-test", "run", "a", "--bar"])
        uw_test.run("a", bar=[True, True])
        mock_check_output.assert_called_with(["uw-test", "run", "a", "--bar", "--bar"])
        uw_test.run("a", b="foo")
        mock_check_output.assert_called_with(["uw-test", "run", "a", "-b", "foo"])
        uw_test.run("a", bar="foo")
        mock_check_output.assert_called_with(["uw-test", "run", "a", "--bar", "foo"])
        uw_test.run("a", bar=["foo", "bar"])
        mock_check_output.assert_called_with(
            ["uw-test", "run", "a", "--bar", "foo", "--bar", "bar"]
        )
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with(["uw-test", "run", "runs", "a", "b"])
        uw_test.run.runs("a", "b", root=True)
        mock_check_output.assert_called_with(
            ["sudo", "uw-test", "run", "runs", "a", "b"]
        )
        uw_test.run.runs("arg with space")
        mock_check_output.assert_called_with(
            ["uw-test", "run", "runs", "arg with space"]
        )
        uw_test.a.b.c.d.e.f.g.h.i.j.k.l.m()
        mock_check_output.assert_called_with(
            ['uw-test', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']
        )
        uw_test.uw_settings.double_dash = False
        uw_test.run("a", bar=["foo", "bar"])
        mock_check_output.assert_called_with(
            ["uw-test", "run", "a", "-bar", "foo", "-bar", "bar"]
        )

    @patch("universal_wrapper.subprocess.check_output")
    def test_input_add(self, mock_check_output):
        uw_test = UniversalWrapper("uw_test")
        uw_test.uw_settings.input_add = {"bar": -1}
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with(
            ["uw-test", "run", "runs", "a", "b", "bar"]
        )
        uw_test.uw_settings.input_add = {"--bar": -1, "foo": 0}
        uw_test.run("a", "b")
        mock_check_output.assert_called_with(
            ["foo", "uw-test", "run", "a", "b", "--bar"]
        )
        uw_test.run("a", "b", bar=False)
        mock_check_output.assert_called_with(["foo", "uw-test", "run", "a", "b"])
        uw_test.uw_settings.input_add = {"--bar foo": -1, "--barfoo bar": -1}
        uw_test.run("a", "b")
        mock_check_output.assert_called_with(
            ["uw-test", "run", "a", "b", "--bar", "foo", "--barfoo", "bar"]
        )
        uw_test.run("a", "b", bar=False)
        mock_check_output.assert_called_with(
            ["uw-test", "run", "a", "b", "--barfoo", "bar"]
        )
        uw_test.run("a", "b", barfoo=False)
        mock_check_output.assert_called_with(
            ["uw-test", "run", "a", "b", "--bar", "foo"]
        )
        uw_test.uw_settings.input_add = {"--bar": -1, "--barfoo bar": -1}
        uw_test.run("a", "b")
        mock_check_output.assert_called_with(
            ["uw-test", "run", "a", "b", "--bar", "--barfoo", "bar"]
        )
        uw_test.run("a", "b", bar=False)
        mock_check_output.assert_called_with(
            ["uw-test", "run", "a", "b", "--barfoo", "bar"]
        )
        uw_test.run("a", "b", barfoo=False)
        mock_check_output.assert_called_with(["uw-test", "run", "a", "b", "--bar"])

        uw_test.uw_settings.input_add = {"--bar foo": -1}
        uw_test.run(bar="bar")
        mock_check_output.assert_called_with(
            ["uw-test", "run", "--bar", "bar", "--bar", "foo"]
        )
        uw_test.run(bar=[False, "bar"])
        mock_check_output.assert_called_with(["uw-test", "run", "--bar", "bar"])

    @patch("universal_wrapper.subprocess.check_output")
    def test_input_move(self, mock_check_output):
        uw_test = UniversalWrapper("uw_test")
        uw_test.uw_settings.input_move = {"runs": 0}
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with(["runs", "uw-test", "run", "a", "b"])
        uw_test.uw_settings.input_move = {"uw-test": -1}
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with(["run", "runs", "a", "b", "uw-test"])
        uw_test.uw_settings.input_move = {"--bar": 1}
        uw_test.run.runs("a", bar="foo")
        mock_check_output.assert_called_with(
            ["uw-test", "--bar", "foo", "run", "runs", "a"]
        )

        uw_test.uw_settings.input_move = {}
        uw_test.uw_settings.input_custom = ["command.reverse()"]
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with(["b", "a", "runs", "run", "uw-test"])

        universal_wrapper.run_command("a")
        mock_check_output.assert_called_with(["run-command", "a"])

    @patch("universal_wrapper.subprocess.check_output")
    def test_dividers(self, mock_check_output):
        uw_test = UniversalWrapper(
            "uw_test", class_divider="~", divider=" ", flag_divider="bar"
        )
        uw_test.run.runs("a", "b", bar_foo=True)
        mock_check_output.assert_called_with(
            ["uw", "test~run~runs", "a", "b", "--barbarfoo"]
        )

    @patch("universal_wrapper.print")
    @patch("universal_wrapper.subprocess.check_output")
    def test_debug(self, mock_check_output, mock_print):
        uw_test = UniversalWrapper(
            "uw_test", class_divider="~", divider=" ", flag_divider="bar"
        )
        uw_test.uw_settings.debug = True
        uw_test.run.runs("a", "b", bar_foo=True)
        mock_check_output.assert_not_called()
        mock_print.assert_called_with(
            "Generated command:\n['uw', 'test~run~runs', 'a', 'b', '--barbarfoo']"
        )

    def test_change_settings(self):
        uw_test = UniversalWrapper("uw_test")
        uw_test.uw_settings.debug = True
        with self.assertRaises(Exception) as context:
            uw_test.uw_settings.non_existant_setting = True

        self.assertTrue("Valid settings are limited to" in str(context.exception))

    def test_set_settings(self):
        uw_test = UniversalWrapper("uw_test", divider="foo")
        self.assertEqual(uw_test.uw_settings.divider, "foo")
        with self.assertRaises(Exception) as context:
            uw_test = UniversalWrapper("uw_test", bar="foo")

        self.assertTrue("Valid settings are limited to" in str(context.exception))

    @patch("universal_wrapper.subprocess.check_output")
    def test_parse_yaml(self, mock_check_output):
        uw_test = UniversalWrapper("uw_test")
        uw_test.uw_settings.output_decode = False
        uw_test.uw_settings.output_yaml = True
        mock_check_output.return_value = """\
- foo: bar
  config:
    bar: foo"""
        result = uw_test()
        self.assertEqual(result, [{"foo": "bar", "config": {"bar": "foo"}}])

    @patch("universal_wrapper.subprocess.check_output")
    def test_parse_json(self, mock_check_output):
        uw_test = UniversalWrapper("uw_test")
        uw_test.uw_settings.output_decode = False
        uw_test.uw_settings.output_json = True
        mock_check_output.return_value = '{"foo": "bar", "config": {"bar": "foo"}}'
        result = uw_test()
        self.assertEqual(result, {"foo": "bar", "config": {"bar": "foo"}})

    @patch("universal_wrapper.subprocess.check_output")
    def test_parse_json(self, mock_check_output):
        uw_test = UniversalWrapper("uw_test")
        uw_test.uw_settings.output_decode = False
        uw_test.uw_settings.output_splitlines = True
        mock_check_output.return_value = "a\nb\nc"
        result = uw_test()
        self.assertEqual(result, ["a", "b", "c"])

    def test_load_settings(self):
        uw_test = UniversalWrapper("uw_test", divider=" ")
        self.assertEqual(uw_test.uw_settings.divider, " ")

    @patch("universal_wrapper.asyncio.create_subprocess_exec")
    def test_async(self, mock_cse):
        proc = AsyncMock()
        proc.returncode = 0
        proc.communicate.return_value = (b"output", b"")
        mock_cse.return_value = proc

        loop = asyncio.new_event_loop()
        uw_test = UniversalWrapper("uw_test")
        loop.run_until_complete(uw_test.async_test())

        mock_cse.assert_called_with("uw-test", "test", stdout=ANY, stderr=ANY)

        uw_test = UniversalWrapper("uw_test")
        uw_test.uw_settings.enable_async = True
        loop.run_until_complete(uw_test.async_test2())

        mock_cse.assert_called_with("uw-test", "test2", stdout=ANY, stderr=ANY)

        uw_test = UniversalWrapper("uw_test")
        uw_test.uw_settings.enable_async = True
        loop.run_until_complete(uw_test.test3())

        mock_cse.assert_called_with("uw-test", "test3", stdout=ANY, stderr=ANY)

        uw_test = UniversalWrapper("uw_test")
        uw_test.uw_settings.enable_async = True
        loop.run_until_complete(uw_test.async_a.b.async_c())

        mock_cse.assert_called_with("uw-test", "a", "b", "c", stdout=ANY, stderr=ANY)

        proc.returncode = 1
        with self.assertRaises(
            subprocess.CalledProcessError,
        ):
            loop.run_until_complete(uw_test.async_a.b.async_c())

        loop.close()


if __name__ == "__main__":
    unittest.main()
