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
                'specVersion: "0.1"\nkind: QualityMeasure\nmetadata: {id: latency, name: Latency}\nspec: {type: duration, typo: true}\n'
            )

    def test_validator_detects_cycle(self) -> None:
        bundle = load_contract(ROOT / "examples/payment-api/quality")
        bundle.stages["technical-refinement"].spec["dependsOn"] = [
            "release-approval"
        ]
        self.assertTrue(
            any("stage dependency cycle" in error for error in validate(bundle))
        )

    def test_evaluation_reports_parallel_active_stages(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        bundle.stages["release-approval"].spec["dependsOn"] = [
            "technical-refinement"
        ]
        report = evaluate(
            bundle,
            {
                "metrics": {},
                "stages": {
                    "technical-refinement": "completed",
                    "continuous-integration": "running",
                    "release-approval": "running",
                },
                "approvals": {},
                "documentation": {},
                "reports": {},
            },
        )

        self.assertEqual(
            report.current_stage, "Continuous integration, Release approval"
        )

    def test_validator_rejects_unknown_stage_type(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        stage = bundle.stages["continuous-integration"]
        stage.spec["type"] = "custom-review"

        errors = validate(bundle)

        self.assertTrue(any("invalid type 'custom-review'" in error for error in errors))

    def test_validator_rejects_legacy_security_review_type(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        stage = bundle.stages["security-review"]
        stage.spec["type"] = "security-review"

        errors = validate(bundle)

        self.assertTrue(any("invalid type 'security-review'" in error for error in errors))

    def test_validator_rejects_legacy_release_approval_type(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        stage = bundle.stages["release-approval"]
        stage.spec["type"] = "release-approval"

        errors = validate(bundle)

        self.assertTrue(any("invalid type 'release-approval'" in error for error in errors))

    def test_business_refinement_requires_owners_and_documentation(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        stage = bundle.stages["business-refinement"]
        stage.spec.pop("owners")
        stage.spec.pop("documentation")

        errors = validate(bundle)

        self.assertTrue(any("requires at least one owner" in error for error in errors))
        self.assertTrue(
            any("requires at least one documentation reference" in error for error in errors)
        )

    def test_technical_refinement_requires_owners_and_documentation(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        stage = bundle.stages["technical-refinement"]
        stage.spec.pop("owners")
        stage.spec.pop("documentation")

        errors = validate(bundle)

        self.assertTrue(any("requires at least one owner" in error for error in errors))
        self.assertTrue(
            any("requires at least one documentation reference" in error for error in errors)
        )

    def test_validator_requires_an_absolute_artifact_link(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        bundle.artifacts["business-requirements"].spec["externalLink"] = "requirements"

        errors = validate(bundle)

        self.assertTrue(
            any("externalLink must be an absolute URL" in error for error in errors)
        )

    def test_validator_rejects_activity_for_wrong_stage_type(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        stage = bundle.stages["continuous-integration"]
        stage.spec["type"] = "review"

        errors = validate(bundle)

        self.assertTrue(
            any("unsupported activities for 'review'" in error for error in errors)
        )

    def test_review_requires_a_free_form_scope(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        stage = bundle.stages["code-review"]
        stage.spec.pop("reviewScope")

        errors = validate(bundle)

        self.assertTrue(any("requires reviewScope" in error for error in errors))

    def test_review_requires_an_approval_policy(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        stage = bundle.stages["code-review"]
        stage.spec.pop("approvalPolicy")

        errors = validate(bundle)

        self.assertTrue(any("requires approvalPolicy" in error for error in errors))

    def test_deploy_requires_a_free_form_environment(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        stage = bundle.stages["deploy-staging"]
        stage.spec.pop("environment")

        errors = validate(bundle)

        self.assertTrue(any("requires environment" in error for error in errors))

    def test_validator_rejects_legacy_validation_type(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        stage = bundle.stages["release-approval"]
        stage.spec["type"] = "validation"

        errors = validate(bundle)

        self.assertTrue(any("invalid type 'validation'" in error for error in errors))

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
