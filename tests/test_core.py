from pathlib import Path
import unittest

from cli.core import evaluate, load_contract, parse, validate


ROOT = Path(__file__).parents[1]


class CoreTests(unittest.TestCase):
    def test_fixture_contract_validates_and_evaluates(self) -> None:
        bundle = load_contract(ROOT / "examples/payment-api/quality")
        self.assertEqual(validate(bundle), [])
        report = evaluate(
            bundle,
            {
                "metrics": {},
                "stages": {},
                "approvals": {},
                "documentation": {},
                "reports": {},
            },
        )
        self.assertFalse(report.ready)

    def test_parser_rejects_unknown_field(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown field"):
            parse(
                'specVersion: "0.1"\nkind: Metric\nmetadata: {id: latency, name: Latency}\nspec: {type: duration, typo: true}\n'
            )

    def test_validator_detects_cycle(self) -> None:
        bundle = load_contract(ROOT / "examples/payment-api/quality")
        bundle.stages["design-review"].spec["dependsOn"] = ["release-approval"]
        self.assertTrue(
            any("stage dependency cycle" in error for error in validate(bundle))
        )

    def test_validator_rejects_report_in_documentation(self) -> None:
        bundle = load_contract(ROOT / "examples/payment-api/quality")
        bundle.project.spec["documentation"] = ["automated-test-report"]
        self.assertTrue(
            any("must be documentation" in error for error in validate(bundle))
        )

    def test_validator_rejects_mismatched_quality_subcharacteristic(self) -> None:
        bundle = load_contract(ROOT / "examples/payment-api/quality")
        bundle.requirements["api-availability"].spec[
            "qualitySubcharacteristic"
        ] = "security-resistance"
        self.assertTrue(
            any(
                "does not match its subcharacteristic" in error
                for error in validate(bundle)
            )
        )
