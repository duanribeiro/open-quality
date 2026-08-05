from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import unittest

from cli.cli import run


ROOT = Path(__file__).parents[1]


class CliTests(unittest.TestCase):
    def test_validate_and_evaluate_cli(self) -> None:
        quality = str(ROOT / "examples/payment-api/quality")
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(run(["validate", quality]), 0)
        self.assertIn("PASS Payment API", output.getvalue())
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                run(
                    ["evaluate", quality, str(ROOT / "examples/payment-api/state.yaml")]
                ),
                0,
            )
        self.assertIn("READY", output.getvalue())
