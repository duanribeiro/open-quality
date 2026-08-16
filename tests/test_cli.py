from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory
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

    def test_plan_selects_provider_role_from_project_file(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "project.yaml").write_text(
                'specVersion: "0.1"\n'
                "kind: Project\n"
                "metadata: {id: payment-api, name: Payment API}\n"
                "spec:\n"
                "  workflow: release\n"
                "  quality:\n"
                "    - characteristic: reliability\n"
                "      subcharacteristics:\n"
                "        - subcharacteristic: availability\n"
                "          requirements: [api-availability]\n"
                "providers:\n"
                "  workManagement:\n"
                "    provider: openproject\n"
                "    config:\n"
                "      baseURL: http://localhost:8080\n"
                "      workPackageTypeHref: /api/v3/types/1\n"
            )
            (root / "workflow.yaml").write_text(
                'specVersion: "0.1"\n'
                "kind: Workflow\n"
                "metadata: {id: release, name: Release}\n"
                "spec: {stages: [development]}\n"
            )
            (root / "stage.yaml").write_text(
                'specVersion: "0.1"\n'
                "kind: Stage\n"
                "metadata: {id: development, name: Development}\n"
                "spec: {}\n"
            )
            (root / "requirement.yaml").write_text(
                'specVersion: "0.1"\n'
                "kind: QualityRequirement\n"
                "metadata: {id: api-availability, name: API availability}\n"
                "spec:\n"
                "  statement: Service remains available.\n"
                "  priority: high\n"
                "  qualityMeasures:\n"
                "    - qualityMeasure: response-time\n"
                "      target: {operator: lessThanOrEqual, value: 500, unit: ms}\n"
            )
            (root / "measure.yaml").write_text(
                'specVersion: "0.1"\n'
                "kind: QualityMeasure\n"
                "metadata: {id: response-time, name: Response time}\n"
                "spec: {unit: ms}\n"
            )
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    run(
                        [
                            "plan",
                            "--target",
                            str(root / "project.yaml"),
                            "--provider-role",
                            "workManagement",
                            str(root),
                        ]
                    ),
                    0,
                )
            self.assertIn("Role: workManagement", output.getvalue())
