import os
import sys
import tempfile
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch


CONFIG_PATH = Path(__file__).resolve().parents[1] / "app" / "core" / "config.py"
SPEC = spec_from_file_location("config_under_test", CONFIG_PATH)
CONFIG_MODULE = module_from_spec(SPEC)
sys.modules[SPEC.name] = CONFIG_MODULE
SPEC.loader.exec_module(CONFIG_MODULE)


class RequiredTests(unittest.TestCase):
    def test_required_returns_existing_value(self) -> None:
        with patch.dict(os.environ, {"POSTGRES_HOST": "localhost"}, clear=True):
            self.assertEqual(CONFIG_MODULE.required("POSTGRES_HOST"), "localhost")

    def test_required_raises_for_missing_value(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "POSTGRES_HOST"):
                CONFIG_MODULE.required("POSTGRES_HOST")

    def test_required_raises_for_empty_value(self) -> None:
        with patch.dict(os.environ, {"POSTGRES_HOST": ""}, clear=True):
            with self.assertRaisesRegex(ValueError, "POSTGRES_HOST"):
                CONFIG_MODULE.required("POSTGRES_HOST")


class ToIntTests(unittest.TestCase):
    def test_to_int_converts_existing_value(self) -> None:
        with patch.dict(os.environ, {"POSTGRES_PORT": "5432"}, clear=True):
            self.assertEqual(CONFIG_MODULE.to_int("POSTGRES_PORT"), 5432)

    def test_to_int_raises_for_non_integer_value(self) -> None:
        with patch.dict(os.environ, {"POSTGRES_PORT": "not-a-number"}, clear=True):
            with self.assertRaisesRegex(ValueError, "POSTGRES_PORT"):
                CONFIG_MODULE.to_int("POSTGRES_PORT")


class ConfigTests(unittest.TestCase):
    def test_from_env_loads_values_and_converts_port(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text(
                "\n".join(
                    [
                        "POSTGRES_HOST=localhost",
                        "POSTGRES_PORT=5432",
                        "POSTGRES_DB=web-chat-server-db",
                        "POSTGRES_USER=Taha",
                        "POSTGRES_PASSWORD=taha2003",
                    ]
                ),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                config = CONFIG_MODULE.Config.from_env(env_file)

            self.assertEqual(config.POSTGRES_HOST, "localhost")
            self.assertEqual(config.POSTGRES_PORT, 5432)
            self.assertEqual(config.POSTGRES_DB, "web-chat-server-db")
            self.assertEqual(config.POSTGRES_USER, "Taha")
            self.assertEqual(config.POSTGRES_PASSWORD, "taha2003")
