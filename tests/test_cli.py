from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import unittest

from cli.cli import run
from cli import renderer
from cli.core import load_contract


ROOT = Path(__file__).parents[1]


class CliTests(unittest.TestCase):
    def test_ascii_graph_does_not_imply_sequential_stage_order(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")

        graph = renderer.ascii(bundle)

        self.assertIn("list order does not define execution order", graph)
        self.assertNotIn("▼", graph)
        self.assertIn("[Continuous integration] (after code-review)", graph)

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
