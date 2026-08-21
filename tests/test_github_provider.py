import unittest
from unittest.mock import Mock, patch

from cli.providers import github


class GitHubProviderTests(unittest.TestCase):
    def test_missing_repository_is_created_as_private(self) -> None:
        config = github.GitHubConfig("test", "duanribeiro", "payment-api")
        client = github.GitHubClient(config, "token")
        client.request = Mock(side_effect=[
            ValueError("GitHub returned 404: Not Found"),
            {"login": "duanribeiro"},
            {"name": "payment-api"},
        ])

        repository = client.ensure_repository()

        self.assertEqual(repository["name"], "payment-api")
        self.assertEqual(client.request.call_args_list[2].args, ("POST", "/user/repos", {"name": "payment-api", "private": True}))

    def test_member_invitation_uses_username_and_permission(self) -> None:
        config = github.GitHubConfig("test", "duanribeiro", "payment-api")
        client = github.GitHubClient(config, "token")
        client.request = Mock(return_value={})

        client.invite_member(github.GitHubMember("software-engineer", "octocat", "push"))

        self.assertEqual(client.request.call_args.args, ("PUT", "/repos/duanribeiro/payment-api/collaborators/octocat", {"permission": "push"}))

    def test_apply_never_writes_a_workflow_or_ruleset(self) -> None:
        config = github.GitHubConfig("test", "duanribeiro", "payment-api")
        client = github.GitHubClient(config, "token")
        client.ensure_repository = Mock(return_value={"name": "payment-api"})
        client.invite_member = Mock()
        original = github.GitHubClient
        try:
            github.GitHubClient = Mock(return_value=client)
            with patch.object(github.GitHubConfig, "token", return_value="token"):
                github.apply(config, [github.GitHubMember("software-engineer", "octocat", "push")])
        finally:
            github.GitHubClient = original

        client.ensure_repository.assert_called_once()
        client.invite_member.assert_called_once()

if __name__ == "__main__":
    unittest.main()
