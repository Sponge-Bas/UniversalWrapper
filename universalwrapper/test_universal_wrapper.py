# Copyright 2022 by Bas de Bruijne
# All rights reserved.
# Universal Wrapper comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this module.
#
# Any changes made to UniversalWrapper must be covered by one of the unit tests
# below. Expected outputs can not be changed to accommodate for new changes.
# To run the unittests:
# $ pip install -e .
# $ cd universalwrapper
# $ python3 -m coverage run -m unittest
# $ python3 -m coverage report --include universal_wrapper.py

import asyncio
import subprocess
import unittest
import universalwrapper

from mock import patch, AsyncMock, ANY, Mock


class TestUniversalWrapper(unittest.TestCase):
    @patch("universalwrapper.UniversalWrapper._raise_or_return")
    @patch("universalwrapper.subprocess.Popen")
    def test_basic_cases(self, mock_Popen, mock_raise_or_return):
        from universalwrapper import uw_test

        proc = Mock()
        proc.communicate.return_value = (1, 1)
        mock_Popen.return_value = proc

        uw_test("a")
        mock_Popen.assert_called_with(
            ["uw-test", "a"], stdout=ANY, stderr=ANY, cwd=None, env=None
        )
        uw_test.run("a")
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a"], stdout=ANY, stderr=ANY, cwd=None, env=None
        )
        uw_test.run("a", b=True)
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "-b"], stdout=ANY, stderr=ANY, cwd=None, env=None
        )
        uw_test.run("a", bar=True)
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "--bar"], stdout=ANY, stderr=ANY, cwd=None, env=None
        )
        uw_test.run("a", bar=[True, True])
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "--bar", "--bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run("a", b="foo")
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "-b", "foo"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run("a", bar="foo")
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "--bar", "foo"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run("a", bar=["foo", "bar"])
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "--bar", "foo", "--bar", "bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run.runs("a", "b")
        mock_Popen.assert_called_with(
            ["uw-test", "run", "runs", "a", "b"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run.runs("a", "b", _root=True)
        mock_Popen.assert_called_with(
            ["sudo", "uw-test", "run", "runs", "a", "b"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run.runs("a", "b")
        mock_Popen.assert_called_with(
            ["uw-test", "run", "runs", "a", "b"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run.runs("arg with space")
        mock_Popen.assert_called_with(
            ["uw-test", "run", "runs", "'arg with space'"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.a.b.c.d.e.f.g.h.i.j.k.l.m()
        mock_Popen.assert_called_with(
            [
                "uw-test",
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
                "h",
                "i",
                "j",
                "k",
                "l",
                "m",
            ],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.uw_settings.double_dash = False
        uw_test.run("a", bar=["foo", "bar"])
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "-bar", "foo", "-bar", "bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )

        run = uw_test.run
        run("a", bar=["foo", "bar"])
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "-bar", "foo", "-bar", "bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )

    @patch("universalwrapper.UniversalWrapper._raise_or_return")
    @patch("universalwrapper.subprocess.Popen")
    def test_input_add(self, mock_Popen, mock_raise_or_return):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (1, 1)
        mock_Popen.return_value = proc

        uw_test.uw_settings.input_add = {"bar": -1}
        uw_test.run.runs("a", "b")
        mock_Popen.assert_called_with(
            ["uw-test", "run", "runs", "a", "b", "bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.uw_settings.input_add = {"--bar": -1, "foo": 0}
        uw_test.run("a", "b")
        mock_Popen.assert_called_with(
            ["foo", "uw-test", "run", "a", "b", "--bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run("a", "b", bar=False)
        mock_Popen.assert_called_with(
            ["foo", "uw-test", "run", "a", "b"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.uw_settings.input_add = {"--bar foo": -1, "--barfoo bar": -1}
        uw_test.run("a", "b")
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "b", "--bar", "foo", "--barfoo", "bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run("a", "b", bar=False)
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "b", "--barfoo", "bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run("a", "b", barfoo=False)
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "b", "--bar", "foo"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.uw_settings.input_add = {"--bar": -1, "--barfoo bar": -1}
        uw_test.run("a", "b")
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "b", "--bar", "--barfoo", "bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run("a", "b", bar=False)
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "b", "--barfoo", "bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run("a", "b", barfoo=False)
        mock_Popen.assert_called_with(
            ["uw-test", "run", "a", "b", "--bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )

        uw_test.uw_settings.input_add = {"--bar foo": -1}
        uw_test.run(bar="bar")
        mock_Popen.assert_called_with(
            ["uw-test", "run", "--bar", "bar", "--bar", "foo"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.run(bar=[False, "bar"])
        mock_Popen.assert_called_with(
            ["uw-test", "run", "--bar", "bar"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )

    @patch("universalwrapper.UniversalWrapper._raise_or_return")
    @patch("universalwrapper.subprocess.Popen")
    def test_input_move(self, mock_Popen, mock_raise_or_return):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (1, 1)
        mock_Popen.return_value = proc

        uw_test.uw_settings.input_move = {"runs": 0}
        uw_test.run.runs("a", "b")
        mock_Popen.assert_called_with(
            ["runs", "uw-test", "run", "a", "b"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.uw_settings.input_move = {"uw-test": -1}
        uw_test.run.runs("a", "b")
        mock_Popen.assert_called_with(
            ["run", "runs", "a", "b", "uw-test"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )
        uw_test.uw_settings.input_move = {"--bar": 1}
        uw_test.run.runs("a", bar="foo")
        mock_Popen.assert_called_with(
            ["uw-test", "--bar", "foo", "run", "runs", "a"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )

        uw_test.uw_settings.input_move = {}
        uw_test.uw_settings.input_custom = ["command.reverse()"]
        uw_test.run.runs("a", "b")
        mock_Popen.assert_called_with(
            ["b", "a", "runs", "run", "uw-test"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )

        universalwrapper.run_command("a")
        mock_Popen.assert_called_with(
            ["run-command", "a"], stdout=ANY, stderr=ANY, cwd=None, env=None
        )

    @patch("universalwrapper.UniversalWrapper._raise_or_return")
    @patch("universalwrapper.subprocess.Popen")
    def test_dividers(self, mock_Popen, mock_raise_or_return):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (1, 1)
        mock_Popen.return_value = proc

        uw_test.uw_settings.class_divider = "~"
        uw_test.uw_settings.divider = " "
        uw_test.uw_settings.flag_divider = "bar"
        uw_test.run.runs("a", "b", bar_foo=True)
        mock_Popen.assert_called_with(
            ["uw", "test~run~runs", "a", "b", "--barbarfoo"],
            stdout=ANY,
            stderr=ANY,
            cwd=None,
            env=None,
        )

    @patch("universalwrapper.print")
    @patch("universalwrapper.subprocess.Popen")
    def test_debug(self, mock_Popen, mock_print):
        uw_test = universalwrapper.uw_test
        uw_test.uw_settings.class_divider = "~"
        uw_test.uw_settings.divider = " "
        uw_test.uw_settings.flag_divider = "bar"
        uw_test.uw_settings.debug = True
        uw_test.run.runs("a", "b", bar_foo=True)
        mock_Popen.assert_not_called()
        mock_print.assert_called_with(
            "Generated command:\n['uw', 'test~run~runs', 'a', 'b', '--barbarfoo']"
        )

    def test_change_settings(self):
        uw_test = universalwrapper.uw_test
        uw_test.uw_settings.debug = True
        with self.assertRaises(Exception) as context:
            uw_test.uw_settings.non_existant_setting = True

        self.assertTrue("Valid settings are limited to" in str(context.exception))

    def test_set_settings(self):
        uw_test = universalwrapper.uw_test
        uw_test.uw_settings.divider = "foo"
        self.assertEqual(uw_test.uw_settings.divider, "foo")
        with self.assertRaises(Exception) as context:
            uw_test = universalwrapper.uw_test
            uw_test.uw_settings.bar = "foo"

        self.assertTrue("Valid settings are limited to" in str(context.exception))

    @patch("universalwrapper.subprocess.Popen")
    def test_parse_yaml(self, mock_Popen):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (
            b"""\
- foo: bar
  config:
    bar: foo""",
            "",
        )
        proc.returncode = 0
        mock_Popen.return_value = proc

        uw_test.uw_settings.output_parser = "yaml"
        result = uw_test()
        self.assertEqual(result, [{"foo": "bar", "config": {"bar": "foo"}}])

    @patch("universalwrapper.subprocess.Popen")
    def test_parse_yaml_auto(self, mock_Popen):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (
            b"""\
- foo: bar
  config:
    bar: foo""",
            "",
        )
        proc.returncode = 0
        mock_Popen.return_value = proc

        uw_test.uw_settings.output_parser = "auto"
        result = uw_test()
        self.assertEqual(result, [{"foo": "bar", "config": {"bar": "foo"}}])

    @patch("universalwrapper.subprocess.Popen")
    def test_parse_yaml_depricated(self, mock_Popen):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (
            """\
- foo: bar
  config:
    bar: foo""",
            "",
        )
        proc.returncode = 0
        mock_Popen.return_value = proc

        uw_test.uw_settings.output_decode = False
        uw_test.uw_settings.output_yaml = True
        result = uw_test()
        self.assertEqual(result, [{"foo": "bar", "config": {"bar": "foo"}}])

    @patch("universalwrapper.subprocess.Popen")
    def test_parse_json(self, mock_Popen):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (
            b'{"foo": "bar", "config": {"bar": "foo"}}',
            "",
        )
        proc.returncode = 0
        mock_Popen.return_value = proc

        uw_test.uw_settings.output_parser = "json"
        result = uw_test()
        self.assertEqual(result, {"foo": "bar", "config": {"bar": "foo"}})

    @patch("universalwrapper.subprocess.Popen")
    def test_parse_json_auto(self, mock_Popen):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (
            b'{"foo": "bar", "config": {"bar": "foo"}}',
            "",
        )
        proc.returncode = 0
        mock_Popen.return_value = proc

        uw_test.uw_settings.output_parser = "auto"
        result = uw_test()
        self.assertEqual(result, {"foo": "bar", "config": {"bar": "foo"}})

    @patch("universalwrapper.subprocess.Popen")
    def test_parse_json_depricated(self, mock_Popen):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = ('{"foo": "bar", "config": {"bar": "foo"}}', "")
        proc.returncode = 0
        mock_Popen.return_value = proc

        uw_test.uw_settings.output_decode = False
        uw_test.uw_settings.output_json = True
        result = uw_test()
        self.assertEqual(result, {"foo": "bar", "config": {"bar": "foo"}})

    @patch("universalwrapper.subprocess.Popen")
    def test_parse_newline(self, mock_Popen):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (b"a\nb\nc", "")
        proc.returncode = 0
        mock_Popen.return_value = proc

        uw_test.uw_settings.output_parser = "splitlines"
        result = uw_test()
        self.assertEqual(result, ["a", "b", "c"])

    @patch("universalwrapper.subprocess.Popen")
    def test_parse_newline_auto(self, mock_Popen):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (b"a\nb\nc", "")
        proc.returncode = 0
        mock_Popen.return_value = proc

        uw_test.uw_settings.output_parser = "auto"
        result = uw_test()
        self.assertEqual(result, "a\nb\nc")

    @patch("universalwrapper.subprocess.Popen")
    def test_parse_newline_depricated(self, mock_Popen):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = ("a\nb\nc", "")
        proc.returncode = 0
        mock_Popen.return_value = proc

        uw_test.uw_settings.output_decode = False
        uw_test.uw_settings.output_splitlines = True
        result = uw_test()
        self.assertEqual(result, ["a", "b", "c"])

    @patch("universalwrapper.subprocess.Popen")
    def test_parse_wrong_parser(self, mock_Popen):
        uw_test = universalwrapper.uw_test
        proc = Mock()
        proc.communicate.return_value = (b"a\nb\nc", "")
        proc.returncode = 0
        mock_Popen.return_value = proc

        uw_test.uw_settings.output_parser = "foobar"

        with self.assertRaises(ValueError):
            result = uw_test()

    def test_load_settings(self):
        uw_test = universalwrapper.uw_test
        uw_test.uw_settings.divider = " "
        self.assertEqual(uw_test.uw_settings.divider, " ")

    def test_async(self):
        asyncio.run(self._test_async())

    @patch("universalwrapper.asyncio.create_subprocess_exec")
    async def _test_async(self, mock_cse):
        proc = AsyncMock()
        proc.returncode = 0
        proc.communicate.return_value = (b"output", b"")
        mock_cse.return_value = proc

        uw_test = universalwrapper.uw_test
        output = await uw_test.test(_enable_async=True)
        await output
        mock_cse.assert_called_with(
            "uw-test", "test", stdout=ANY, stderr=ANY, cwd=None, env=None
        )

        uw_test = universalwrapper.uw_test
        uw_test.uw_settings.enable_async = True
        output = await uw_test.test2(_enable_async=True)
        await output
        mock_cse.assert_called_with(
            "uw-test", "test2", stdout=ANY, stderr=ANY, cwd=None, env=None
        )

        uw_test = universalwrapper.uw_test
        uw_test.uw_settings.enable_async = True
        output = await uw_test.test3()
        await output
        mock_cse.assert_called_with(
            "uw-test", "test3", stdout=ANY, stderr=ANY, cwd=None, env=None
        )

        uw_test = universalwrapper.uw_test
        uw_test.uw_settings.enable_async = True
        output = await uw_test.a.b.c(_enable_async=True)
        await output
        mock_cse.assert_called_with(
            "uw-test", "a", "b", "c", stdout=ANY, stderr=ANY, cwd=None, env=None
        )

        proc.returncode = 1
        with self.assertRaises(
            subprocess.CalledProcessError,
        ):
            output = await uw_test.a.b.c(_enable_async=True)
            await output

    def test_basic_commands(self):
        from universalwrapper import ls, mkdir, touch, rm, grep

        try:
            rm("__uwunittest", recursive=True)
        except subprocess.CalledProcessError:
            pass

        mkdir("__uwunittest")
        touch("__uwunittest/a.test")
        touch("__uwunittest/b.test")

        self.assertEqual(ls("__uwunittest").strip(), "a.test\nb.test")
        self.assertEqual(
            ls("__uwunittest", _output_splitlines=True), ["a.test", "b.test"]
        )

        # with self.assertRaises(
        #     UserWarning,
        # ):
        #     grep("aasdfs", recursive=True)
        rm("__uwunittest", recursive=True)
        self.assertTrue("__uwunittest" not in ls())

    def test_async_basic_commands(self):
        asyncio.run(self._test_async())

    async def _test_basic_commands(self):
        from universalwrapper import ls, mkdir, touch, rm

        ls.uw_settings.enable_async = True
        mkdir.uw_settings.enable_async = True

        try:
            rm("__uwunittest", recursive=True)
        except subprocess.CalledProcessError:
            pass

        await mkdir("__uwunittest")
        touch("__uwunittest/a.test")
        touch("__uwunittest/b.test")

        files = await ls("__uwunittest")

        self.assertEqual(await files, "a.test\nb.test\n")

        rm("__uwunittest", recursive=True)
        self.assertTrue("__uwunittest" not in ls(_enable_async=False))


if __name__ == "__main__":
    unittest.main()
