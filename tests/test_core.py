from pathlib import Path
import unittest

from cli.core import evaluate, load_contract, parse, validate


ROOT = Path(__file__).parents[1]


class CoreTests(unittest.TestCase):
    def test_fixture_contract_validates_and_evaluates(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        self.assertEqual(validate(bundle), [])
        report = evaluate(
            bundle,
            {
                "metrics": {},
                "stages": {},
                "approvals": {},
                "documentation": {},
            },
        )
        self.assertFalse(report.ready)

    def test_parser_rejects_unknown_field(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown field"):
            parse(
                'specVersion: "0.1"\nkind: QualityMeasure\nmetadata: {id: latency, name: Latency}\nspec: {unit: ms, typo: true}\n'
            )

    def test_quality_measure_element_requires_timestamped_measurements(self) -> None:
        with self.assertRaisesRegex(ValueError, "measurements"):
            parse(
                'specVersion: "0.1"\nkind: QualityMeasureElement\n'
                "metadata: {id: covered-lines, name: Covered lines}\n"
                "spec: {unit: lines, measurementMethod: manual-entry}\n"
            )

    def test_quality_measure_element_requires_an_iso_timestamp(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not match"):
            parse(
                'specVersion: "0.1"\nkind: QualityMeasureElement\n'
                "metadata: {id: covered-lines, name: Covered lines}\n"
                "spec:\n"
                "  measurementMethod: manual-entry\n"
                "  measurements: [{value: 10, measuredAt: yesterday}]\n"
            )

    def test_project_accepts_root_providers(self) -> None:
        project = parse(
            'specVersion: "0.1"\n'
            "kind: QualityContract\n"
            "metadata: {id: payment-api, name: Payment API}\n"
            "spec:\n"
            "  workflow: standard-release\n"
            "  quality:\n"
            "    - characteristic: reliability\n"
            "      requirements: [api-availability]\n"
            "providers:\n"
            "  workManagement:\n"
            "    provider: openproject\n"
            "    config: {baseURL: http://localhost:8080}\n"
        )

        self.assertEqual(project.providers["workManagement"]["provider"], "openproject")

    def test_project_quality_characteristic_can_reference_requirements_directly(self) -> None:
        project = parse(
            'specVersion: "0.1"\n'
            "kind: QualityContract\n"
            "metadata: {id: payment-api, name: Payment API}\n"
            "spec:\n"
            "  workflow: standard-release\n"
            "  quality:\n"
            "    - characteristic: security\n"
            "      requirements: [api-security]\n"
        )

        self.assertEqual(project.spec["quality"][0]["requirements"], ["api-security"])

    def test_providers_are_not_allowed_on_non_project_resources(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown field"):
            parse(
                'specVersion: "0.1"\n'
                "kind: QualityMeasure\n"
                "metadata: {id: latency, name: Latency}\n"
                "spec: {unit: ms}\n"
                "providers: {}\n"
            )

    def test_validator_detects_cycle(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        bundle.stages["business-refinement"].spec["dependsOn"] = [
            "continuous-integration"
        ]
        bundle.stages["development"].spec["dependsOn"] = ["technical-refinement"]
        self.assertTrue(
            any("stage dependency cycle" in error for error in validate(bundle))
        )

    def test_evaluation_reports_parallel_active_stages(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        bundle.stages["continuous-integration"].spec["dependsOn"] = ["technical-refinement"]
        report = evaluate(
            bundle,
            {
                "metrics": {},
                "stages": {
                    "technical-refinement": "completed",
                    "development": "running",
                    "continuous-integration": "running",
                },
                "approvals": {},
                "documentation": {},
            },
        )

        self.assertEqual(
            report.current_stage, "Development, Continuous integration"
        )

    def test_validator_requires_an_absolute_artifact_link(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        bundle.artifacts["business-requirements"].spec["externalLink"] = "requirements"

        errors = validate(bundle)

        self.assertTrue(
            any("externalLink must be an absolute URL" in error for error in errors)
        )

    def test_pipeline_is_not_a_supported_stage_field(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown field"):
            parse(
                'specVersion: "0.1"\nkind: Stage\nmetadata: {id: delivery, name: Delivery}\n'
                "spec: {pipeline: [{id: deploy}]}\n"
            )
