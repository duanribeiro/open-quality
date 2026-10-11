from pathlib import Path
import unittest

import yaml

from cli.core import evaluate, load_contract, parse, validate


ROOT = Path(__file__).parents[1]


class CoreTests(unittest.TestCase):
    def test_team_round_trip_and_role_references(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        self.assertEqual(
            bundle.project.team[1],
            {
                "email": "lead@example.com",
                "roles": ["quality-lead", "engineering-manager"],
            },
        )
        self.assertEqual(validate(bundle), [])
        bundle.project.team[0]["roles"] = ["missing-role"]
        self.assertTrue(any("missing-role" in error for error in validate(bundle)))

    def test_team_rejects_duplicate_emails_ignoring_case(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        bundle.project.team.append(
            {"email": "ENGINEER@example.com", "roles": ["quality-lead"]}
        )
        self.assertIn("duplicate team email 'ENGINEER@example.com'", validate(bundle))

    def test_team_allows_shared_roles(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        bundle.project.team.append(
            {"email": "another@example.com", "roles": ["software-engineer"]}
        )
        self.assertEqual(validate(bundle), [])

    def test_team_is_optional(self) -> None:
        payload = yaml.safe_load(
            (ROOT / "examples/minimal/quality-contract.yaml").read_text()
        )
        payload.pop("team")
        self.assertEqual(parse(yaml.safe_dump(payload)).team, [])
        payload["team"] = []
        self.assertEqual(parse(yaml.safe_dump(payload)).team, [])

    def test_team_rejects_invalid_members(self) -> None:
        payload = yaml.safe_load(
            (ROOT / "examples/minimal/quality-contract.yaml").read_text()
        )
        invalid_teams = [
            None,
            {},
            ["engineer@example.com"],
            [{"roles": ["software-engineer"]}],
            [{"email": "engineer@example.com"}],
            [{"email": "invalid", "roles": ["software-engineer"]}],
            [{"email": "user @example.com", "roles": ["software-engineer"]}],
            [{"email": "user@@example.com", "roles": ["software-engineer"]}],
            [{"email": "engineer@example.com", "roles": []}],
            [{"email": "engineer@example.com", "roles": ["Invalid Role"]}],
            [
                {
                    "email": "engineer@example.com",
                    "roles": ["software-engineer", "software-engineer"],
                }
            ],
            [
                {
                    "email": "engineer@example.com",
                    "roles": ["software-engineer"],
                    "typo": True,
                }
            ],
        ]
        for team in invalid_teams:
            with self.subTest(team=team):
                payload["team"] = team
                with self.assertRaises(ValueError):
                    parse(yaml.safe_dump(payload))

    def test_team_is_only_allowed_on_quality_contract(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown field"):
            parse(
                'specVersion: "0.1"\nkind: Role\n'
                "metadata: {id: engineer, name: Engineer}\nspec: {}\nteam: []\n"
            )

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

    def test_project_quality_characteristic_can_reference_requirements_directly(
        self,
    ) -> None:
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
        bundle.stages["continuous-integration"].spec["dependsOn"] = [
            "technical-refinement"
        ]
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

        self.assertEqual(report.current_stage, "Development, Continuous integration")

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
