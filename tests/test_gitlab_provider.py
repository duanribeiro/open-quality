from pathlib import Path
import unittest

from cli.providers import gitlab


ROOT = Path(__file__).parents[1]


class GitLabProviderTests(unittest.TestCase):
    def test_development_policy_generates_gitlab_pipeline(self) -> None:
        config = gitlab.GitLabConfig(
            "sourceControl", "https://gitlab.com/api/v4", "group/payment-api",
            development_policy={
                "branch": {"pattern": "feature/{issueKey}-{slug}"},
                "commits": {"pattern": "{issueKey}: {type}({scope}): {description}", "requiredTypes": ["feat"]},
            },
        )
        policy = gitlab.policy(config)
        self.assertIsNotNone(policy)
        rendered = gitlab.pipeline(policy)
        self.assertIn("open_quality_development_policy", rendered)
        self.assertIn("CI_MERGE_REQUEST_SOURCE_BRANCH_NAME", rendered)
        self.assertIn("commit violates Open Quality policy", rendered)
