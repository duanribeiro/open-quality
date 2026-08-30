from pathlib import Path
import unittest

from cli.core import load_contract
from cli.provider import ProjectMember, TargetConfig, new_state, plan


ROOT = Path(__file__).parents[1]


class ProviderPlanTests(unittest.TestCase):
    def test_development_provisions_project_team_and_code_reviewers(self) -> None:
        bundle = load_contract(ROOT / "examples/minimal")
        config = TargetConfig("openproject", "test", "http://example.test", type_href="/api/v3/types/1")
        members = [
            ProjectMember("software-engineer", "engineer@example.test", "Member"),
            ProjectMember("quality-lead", "quality@example.test", "Member"),
            ProjectMember("engineering-manager", "manager@example.test", "Project admin"),
        ]

        operations = plan(bundle, new_state("test"), config, members)

        self.assertEqual([item.kind for item in operations[:5]], [
            "QualityContract", "KanbanBoard", "ProjectMember", "ProjectMember", "ProjectMember",
        ])
        self.assertEqual(operations[0].subject, "Payment API")
        reviewers = [item.subject for item in operations if item.kind == "CodeReviewer"]
        self.assertEqual(reviewers, ["engineer@example.test", "quality@example.test"])
