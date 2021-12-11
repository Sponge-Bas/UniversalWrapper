import unittest
from mock import patch, Mock, mock_open, call, MagicMock
from universal_wrapper import UniversalWrapper
import universal_wrapper

class TestUniversalWrapper(unittest.TestCase):

    @patch("universal_wrapper.subprocess.check_output")
    def test_cases(self, mock_check_output):
        uw_test = UniversalWrapper("uw_test")

        uw_test("a")
        mock_check_output.assert_called_with('uw-test a', shell=True)
        uw_test.run("a")
        mock_check_output.assert_called_with('uw-test run a', shell=True)
        uw_test.run("a", b=True)
        mock_check_output.assert_called_with('uw-test run a -b', shell=True)
        uw_test.run("a", bar=True)
        mock_check_output.assert_called_with('uw-test run a --bar', shell=True)
        uw_test.run("a", bar=[True, True])
        mock_check_output.assert_called_with('uw-test run a --bar --bar', shell=True)
        uw_test.run("a", b="foo")
        mock_check_output.assert_called_with('uw-test run a -b foo', shell=True)
        uw_test.run("a", bar="foo")
        mock_check_output.assert_called_with('uw-test run a --bar foo', shell=True)
        uw_test.run("a", bar=["foo", "bar"])
        mock_check_output.assert_called_with('uw-test run a --bar foo --bar bar', shell=True)
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with('uw-test run runs a b', shell=True)

        uw_test.uw_settings["input_modifiers"]["add"] = {"bar": -1}
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with('uw-test run runs a b  bar', shell=True)
        uw_test.uw_settings["input_modifiers"]["add"] = {"--bar": -1, "foo": 0}
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with('foo uw-test run runs a b  --bar', shell=True)
        uw_test.run.runs("a", "b", bar=False)
        mock_check_output.assert_called_with('foo uw-test run runs a b', shell=True)

        uw_test.uw_settings["input_modifiers"]["add"] = {}
        uw_test.uw_settings["input_modifiers"]["move"] = {"runs": 0}
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with('runs uw-test run a b', shell=True)
        uw_test.uw_settings["input_modifiers"]["move"] = {"uw-test": -1}
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with('run runs a b  uw-test', shell=True)
        uw_test.uw_settings["input_modifiers"]["move"] = {"--bar": 1}
        uw_test.run.runs("a", bar="foo")
        mock_check_output.assert_called_with('uw-test --bar foo run runs a', shell=True)

        uw_test.uw_settings["input_modifiers"]["move"] = {}
        uw_test.uw_settings["input_modifiers"]["custom"] = ["command.reverse()"]
        uw_test.run.runs("a", "b")
        mock_check_output.assert_called_with('b a runs run uw-test', shell=True)

if __name__ == '__main__':
    unittest.main()