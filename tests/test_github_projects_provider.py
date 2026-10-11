import unittest
from unittest.mock import Mock

from cli.providers.github_projects import Client, Config


class GitHubProjectsTests(unittest.TestCase):
    def client(self, owner_type: str = "user") -> Client:
        client = Client(
            Config("workManagement", "octocat", "Quality", owner_type), "token"
        )
        client.query = Mock(return_value={"node": {"views": {"nodes": []}}})
        client.rest = Mock(return_value={})
        return client

    def test_personal_board_uses_owner_login(self) -> None:
        client = self.client()
        client.ensure_board_view("PVT_project", 7, {"databaseId": 123}, 456)
        client.rest.assert_called_once_with(
            "POST",
            "/users/octocat/projectsV2/7/views",
            {
                "name": "Open Quality workflow",
                "layout": "board",
                "vertical_group_by": [456],
            },
        )

    def test_organization_board_uses_organization_route(self) -> None:
        client = self.client("organization")
        client.ensure_board_view("PVT_project", 7, {"databaseId": 123}, 456)
        self.assertEqual(
            client.rest.call_args.args[1], "/orgs/octocat/projectsV2/7/views"
        )

    def test_existing_graphql_board_is_reused(self) -> None:
        client = self.client()
        client.query.return_value = {
            "node": {
                "views": {
                    "nodes": [
                        {"name": "Open Quality workflow", "layout": "BOARD_LAYOUT"}
                    ]
                }
            }
        }
        client.ensure_board_view("PVT_project", 7, {}, 456)
        client.rest.assert_not_called()

    def test_unrelated_board_does_not_skip_creation(self) -> None:
        client = self.client()
        client.query.return_value = {
            "node": {
                "views": {"nodes": [{"name": "Other board", "layout": "BOARD_LAYOUT"}]}
            }
        }
        client.ensure_board_view("PVT_project", 7, {}, 456)
        client.rest.assert_called_once()

    def test_creation_error_preserves_api_error_and_route_context(self) -> None:
        client = self.client()
        client.rest.side_effect = ValueError("GitHub returned 404: Not Found")
        with self.assertRaisesRegex(
            ValueError, "/users/octocat/projectsV2/7/views"
        ) as error:
            client.ensure_board_view("PVT_project", 7, {}, 456)
        self.assertIn("GitHub returned 404", str(error.exception))
        self.assertIn("rerun oq apply", str(error.exception))
