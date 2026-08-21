import unittest
from unittest.mock import Mock, patch

from cli.providers import gitlab


class GitLabProviderTests(unittest.TestCase):
    def test_apply_only_provisions_members(self) -> None:
        config = gitlab.GitLabConfig("sourceControl", "https://gitlab.com/api/v4", "group/payment-api")
        client = gitlab.GitLabClient(config, "token")
        client.project = Mock(return_value={"id": 42})
        client.invite_member = Mock()
        original = gitlab.GitLabClient
        try:
            gitlab.GitLabClient = Mock(return_value=client)
            with patch.object(gitlab.GitLabConfig, "token", return_value="token"):
                gitlab.apply(config, [gitlab.GitLabMember("software-engineer", "octocat", "developer")])
        finally:
            gitlab.GitLabClient = original

        client.invite_member.assert_called_once_with(42, gitlab.GitLabMember("software-engineer", "octocat", "developer"))
