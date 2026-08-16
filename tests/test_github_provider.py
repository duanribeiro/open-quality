from pathlib import Path
import re
import unittest
from unittest.mock import Mock

from cli.core import load_contract
from cli.providers import github


ROOT = Path(__file__).parents[1]


class GitHubProviderTests(unittest.TestCase):
    def test_missing_repository_is_created_as_private(self) -> None:
        config = github.GitHubConfig("test", "duanribeiro", "payment-api", "TOKEN")
        client = github.GitHubClient(config, "token")
        client.request = Mock(side_effect=[
            ValueError("GitHub returned 404: Not Found"),
            {"login": "duanribeiro"},
            {"name": "payment-api", "default_branch": "main"},
        ])

        repository = client.ensure_repository()

        self.assertEqual(repository["name"], "payment-api")
        self.assertEqual(client.request.call_args_list[2].args, ("POST", "/user/repos", {"name": "payment-api", "private": True}))

    def test_ruleset_includes_all_required_pull_request_parameters(self) -> None:
        config = github.GitHubConfig("test", "duanribeiro", "payment-api", "TOKEN")
        client = github.GitHubClient(config, "token")
        client.request = Mock(side_effect=[[], {}])

        client.upsert_ruleset("Open Quality: development", "main")

        rules = client.request.call_args_list[1].args[2]["rules"]
        self.assertEqual(rules[0]["parameters"], {
            "dismiss_stale_reviews_on_push": False,
            "require_code_owner_review": False,
            "require_last_push_approval": False,
            "required_approving_review_count": 0,
            "required_review_thread_resolution": False,
        })
        self.assertEqual(rules[1]["type"], "required_status_checks")
        self.assertNotIn("commit_message_pattern", [rule["type"] for rule in rules])

    def test_member_invitation_uses_username_and_permission(self) -> None:
        config = github.GitHubConfig("test", "duanribeiro", "payment-api", "TOKEN")
        client = github.GitHubClient(config, "token")
        client.request = Mock(return_value={})

        client.invite_member(github.GitHubMember("software-engineer", "octocat", "push"))

        self.assertEqual(client.request.call_args.args, ("PUT", "/repos/duanribeiro/payment-api/collaborators/octocat", {"permission": "push"}))

    def test_development_policy_compiles_to_enforced_rules(self) -> None:
        config = github.GitHubConfig(
            "sourceControl", "duanribeiro", "payment-api", development_policy={
                "branch": {"pattern": "feature/{issueKey}-{slug}"},
                "commits": {"pattern": "{issueKey}: {type}({scope}): {description}", "requiredTypes": ["feat"]},
                "pullRequest": {"required": ["linkedIssue"]},
            },
        )
        policy = github.policy(config)

        self.assertIsNotNone(policy)
        self.assertTrue(re.fullmatch(str(policy["branch"]), "feature:INVALID") is None)
        self.assertTrue(re.fullmatch(str(policy["branch"]), "feature/PAY-123-add-health-check"))
        self.assertTrue(re.fullmatch(str(policy["commits"]), "PAY-123: feat(api): add health check"))
        self.assertFalse(re.fullmatch(str(policy["commits"]), "add health check"))
        self.assertNotIn("(?:", str(policy["commits"]))
        self.assertNotIn(r"\d", str(policy["commits"]))

        rendered = github.workflow(policy)
        self.assertIn("Open Quality source control policy", rendered)
        self.assertIn("REQUIRE_LINKED_ISSUE: 'true'", rendered)

if __name__ == "__main__":
    unittest.main()
