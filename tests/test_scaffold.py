from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

import yaml

from cli.cli import run
from cli.core import load_contract, validate


ROOT = Path(__file__).parents[1]


class TeamScaffoldTests(unittest.TestCase):
    def test_add_role_and_team_commands_create_valid_resources(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory) / ".quality"
            copytree(ROOT / "examples/minimal", root)
            original = load_contract(root)
            with (
                redirect_stdout(StringIO()),
                patch(
                    "builtins.input",
                    side_effect=[
                        "security-reviewer",
                        "Security Reviewer",
                        "Reviews security evidence.",
                        "Review risks; Approve evidence; Review risks",
                    ],
                ),
            ):
                self.assertEqual(run(["add", "role", str(root)]), 0)
            bundle = load_contract(root)
            self.assertEqual(validate(bundle), [])
            self.assertEqual(bundle.project.team, original.project.team)
            self.assertIn("security-reviewer", bundle.project.spec["roles"])
            self.assertEqual(
                bundle.roles["security-reviewer"].spec["responsibilities"],
                ["Review risks", "Approve evidence"],
            )
            self.assertTrue((root / "roles/security-reviewer.yaml").exists())
            with (
                redirect_stdout(StringIO()),
                patch(
                    "builtins.input",
                    side_effect=[
                        "security@example.com",
                        "security-reviewer,quality-lead",
                        "yes",
                        "another@example.com",
                        "security-reviewer",
                        "",
                    ],
                ),
            ):
                self.assertEqual(run(["add", "team", str(root)]), 0)
            bundle = load_contract(root)
            self.assertEqual(validate(bundle), [])
            self.assertEqual(bundle.project.team[:2], original.project.team)
            self.assertEqual(
                bundle.project.team[2:],
                [
                    {
                        "email": "security@example.com",
                        "roles": ["security-reviewer", "quality-lead"],
                    },
                    {"email": "another@example.com", "roles": ["security-reviewer"]},
                ],
            )
            self.assertEqual(bundle.project.providers, original.project.providers)

    def test_add_team_reprompts_for_invalid_email_and_roles(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            copytree(ROOT / "examples/minimal", root, dirs_exist_ok=True)
            with (
                redirect_stdout(StringIO()),
                patch(
                    "builtins.input",
                    side_effect=[
                        "invalid",
                        "ENGINEER@example.com",
                        "new@example.com",
                        "",
                        "missing-role",
                        "1,3,1",
                        "",
                    ],
                ),
            ):
                self.assertEqual(run(["add", "team", str(root)]), 0)
            bundle = load_contract(root)
            self.assertEqual(validate(bundle), [])
            self.assertEqual(
                bundle.project.team[-1],
                {
                    "email": "new@example.com",
                    "roles": ["engineering-manager", "software-engineer"],
                },
            )

    def test_add_team_requires_roles_before_prompting_or_writing(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "quality-contract.yaml"
            original = (
                'specVersion: "0.1"\nkind: QualityContract\n'
                "metadata: {id: test, name: Test}\nspec: {quality: []}\n"
            )
            path.write_text(original)
            with patch("builtins.input") as prompt:
                with self.assertRaisesRegex(ValueError, "oq add role"):
                    run(["add", "team", str(root)])
                prompt.assert_not_called()
            self.assertEqual(path.read_text(), original)

    def test_add_role_reprompts_for_ids_used_by_any_resource(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            copytree(ROOT / "examples/minimal", root, dirs_exist_ok=True)
            existing = (root / "roles/role-engineer.yaml").read_text()
            with (
                redirect_stdout(StringIO()),
                patch(
                    "builtins.input",
                    side_effect=[
                        "payment-api",
                        "software-engineer",
                        "new-role",
                        "",
                        "",
                        "",
                    ],
                ),
            ):
                self.assertEqual(run(["add", "role", str(root)]), 0)
            self.assertEqual((root / "roles/role-engineer.yaml").read_text(), existing)
            self.assertEqual(validate(load_contract(root)), [])

    def test_add_role_refuses_existing_file_without_changing_contract(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            copytree(ROOT / "examples/minimal", root, dirs_exist_ok=True)
            path = root / "quality-contract.yaml"
            original = path.read_text()
            collision = root / "roles/new-role.yaml"
            collision.write_text("# Existing file\n")
            with (
                redirect_stdout(StringIO()),
                patch("builtins.input", side_effect=["new-role", "", "", ""]),
            ):
                with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                    run(["add", "role", str(root)])
            self.assertEqual(path.read_text(), original)
            self.assertEqual(collision.read_text(), "# Existing file\n")

    def test_add_team_creates_missing_team_list(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            copytree(ROOT / "examples/minimal", root, dirs_exist_ok=True)
            path = root / "quality-contract.yaml"
            contract = yaml.safe_load(path.read_text())
            contract.pop("team")
            path.write_text(yaml.safe_dump(contract))
            with (
                redirect_stdout(StringIO()),
                patch(
                    "builtins.input",
                    side_effect=["new@example.com", "software-engineer", ""],
                ),
            ):
                self.assertEqual(run(["add", "team", str(root)]), 0)
            bundle = load_contract(root)
            self.assertEqual(validate(bundle), [])
            self.assertEqual(len(bundle.project.team), 1)
