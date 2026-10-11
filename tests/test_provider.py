from pathlib import Path
import unittest

from cli.core import load_contract
from cli.providers.openproject import ProjectMember, TargetConfig, new_state, plan


ROOT = Path(__file__).parents[1]


class ProviderPlanTests(unittest.TestCase):
    def test_development_plans_project_team_and_quality_requirements(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        config = TargetConfig(
            "openproject", "test", "http://example.test", type_href="/api/v3/types/1"
        )
        members = [
            ProjectMember("software-engineer", "engineer@example.test", "Member"),
            ProjectMember("quality-lead", "quality@example.test", "Member"),
            ProjectMember(
                "engineering-manager", "manager@example.test", "Project admin"
            ),
        ]

        operations = plan(bundle, new_state("test"), config, members)

        self.assertEqual(
            [item.kind for item in operations[:5]],
            [
                "QualityContract",
                "KanbanBoard",
                "ProjectMember",
                "ProjectMember",
                "ProjectMember",
            ],
        )
        self.assertEqual(operations[0].subject, "Payment API")
        self.assertEqual(
            [item.kind for item in operations[5:]],
            ["QualityRequirement", "QualityRequirement"],
        )
        self.assertNotIn("CodeReviewer", [item.kind for item in operations])
