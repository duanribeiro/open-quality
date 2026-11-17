"""GitLab provider for development-stage policies."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

ACCESS_LEVELS = {"guest": 10, "reporter": 20, "developer": 30, "maintainer": 40}


@dataclass(frozen=True)
class GitLabConfig:
    name: str
    base_url: str
    project: str = ""
    group: str = ""
    board_name: str = "Open Quality workflow"

    def token(self) -> str:
        """Return the GITLAB_TOKEN environment variable, or raise if unset."""
        token = os.getenv("GITLAB_TOKEN")
        if not token:
            raise ValueError("environment variable GITLAB_TOKEN is empty")
        return token


@dataclass(frozen=True)
class GitLabMember:
    role: str
    username: str
    access_level: str


def load_config(source: str | Path | dict, role: str = "") -> GitLabConfig:
    """Load and validate a GitLab provider target from a path or inline mapping."""
    try:
        raw = (
            source
            if isinstance(source, dict)
            else yaml.safe_load(Path(source).read_text())
        ) or {}
        cfg = raw.get("config") or {}
        if raw.get("provider") != "gitlab":
            raise ValueError("provider must be gitlab")
        if set(raw) - {"provider", "config", "description", "workflow"}:
            raise ValueError("target has an unknown field")
        allowed = {
            "baseURL",
            "project",
            "group",
            "owner",
            "repository",
            "ownerType",
            "visibility",
            "members",
            "boardName",
        }
        if set(cfg) - allowed:
            raise ValueError("GitLab config has an unknown field")
        selected_role = role or raw["provider"]
        base_url = cfg.get("baseURL", "https://gitlab.com/api/v4")
        project = cfg.get("project", "")
        group_value = cfg.get("group", "")
        group = str(group_value) if group_value else ""
        board_name = cfg.get("boardName", cfg.get("project", "Open Quality workflow"))
        if selected_role == "sourceControl":
            if group:
                raise ValueError("group is only supported for GitLab work management")
            if not project and cfg.get("owner") and cfg.get("repository"):
                project = f"{cfg['owner']}/{cfg['repository']}"
            if not project:
                raise ValueError(
                    "project or owner and repository are required for GitLab source control"
                )
        if selected_role == "workManagement":
            if not cfg.get("owner"):
                raise ValueError("owner is required for GitLab work management")
            if not group:
                raise ValueError("group is required for GitLab work management")
            if not board_name:
                raise ValueError("project is required for GitLab work management")
        return GitLabConfig(selected_role, base_url, project, group, board_name)
    except Exception as error:
        raise ValueError(f"target {source}: {error}") from error


def load_members(raw: dict) -> list[GitLabMember]:
    """Parse the inline `members` list of a GitLab target config."""
    members = []
    for item in raw.get("members", []):
        if set(item) - {"role", "usernames", "accessLevel"}:
            raise ValueError("GitLab member contains an unknown field")
        role, usernames, access = (
            item.get("role"),
            item.get("usernames"),
            item.get("accessLevel"),
        )
        if (
            not isinstance(role, str)
            or not isinstance(usernames, list)
            or access not in ACCESS_LEVELS
        ):
            raise ValueError("GitLab member requires role, usernames and accessLevel")
        if not all(isinstance(username, str) and username for username in usernames):
            raise ValueError("GitLab usernames must be non-empty strings")
        members.extend(GitLabMember(role, username, access) for username in usernames)
    return members


class GitLabClient:
    def __init__(self, config: GitLabConfig, token: str):
        """Store the target config and API token used by every request."""
        self.config, self.token = config, token

    def request(self, method: str, path: str, body: dict | None = None) -> dict | list:
        """Send one authenticated GitLab REST API request and return its JSON body."""
        request = Request(
            self.config.base_url.rstrip("/") + path,
            method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"PRIVATE-TOKEN": self.token, "Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read()
                return json.loads(payload) if payload else {}
        except HTTPError as error:
            raise ValueError(
                f"GitLab returned {error.code}: {error.read().decode()}"
            ) from error

    @property
    def project_path(self) -> str:
        """Return the API path for the configured project."""
        return "/projects/" + quote(self.config.project, safe="")

    @property
    def group_path(self) -> str:
        """Return the API path for the configured group."""
        return "/groups/" + quote(self.config.group, safe="")

    def project(self) -> dict:
        """Fetch the configured GitLab project."""
        return self.request("GET", self.project_path)  # type: ignore[return-value]

    def get_all(self, path: str) -> list[dict]:
        """Fetch all pages of a GitLab collection using its REST pagination."""
        items = []
        page = 1
        while True:
            result = self.request(
                "GET", f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}"
            )
            if not isinstance(result, list):
                raise ValueError("GitLab returned an invalid collection response")
            items.extend(result)
            if len(result) < 100:
                return items
            page += 1

    def invite_member(self, project_id: int, member: GitLabMember) -> None:
        """Add `member` to the project at the given access level."""
        users = self.request("GET", f"/users?username={quote(member.username)}")
        if not isinstance(users, list) or not users:
            raise ValueError(f"GitLab user not found: {member.username}")
        self.request(
            "POST",
            f"/projects/{project_id}/members",
            {
                "user_id": users[0]["id"],
                "access_level": ACCESS_LEVELS[member.access_level],
            },
        )

    def ensure_workflow_board(self, stage_ids: list[str]) -> bool:
        """Ensure an issue board has one label list for each workflow stage."""
        resource_path = self.group_path if self.config.group else self.project_path
        labels = self.get_all(f"{resource_path}/labels")
        label_ids = {label["name"]: label["id"] for label in labels}
        for stage_id in stage_ids:
            if stage_id not in label_ids:
                label = self.request(
                    "POST",
                    f"{resource_path}/labels",
                    {"name": stage_id, "color": "#428BCA"},
                )
                label_ids[stage_id] = label["id"]

        boards = self.get_all(f"{resource_path}/boards")
        board = next(
            (item for item in boards if item.get("name") == self.config.board_name),
            None,
        )
        if board is None and self.config.group and len(boards) == 1:
            # GitLab Free has one group board; reuse it instead of trying to
            # create another board, which requires a paid tier.
            board = boards[0]
        if board is None:
            board = self.request(
                "POST",
                f"{resource_path}/boards",
                {"name": self.config.board_name},
            )
        board_id = board["id"]
        lists_path = f"{resource_path}/boards/{board_id}/lists"
        board_lists = self.get_all(lists_path)
        existing = {
            item.get("label", {}).get("name"): item
            for item in board_lists
            if item.get("label")
        }
        for stage_id in stage_ids:
            if stage_id not in existing:
                self.request("POST", lists_path, {"label_id": label_ids[stage_id]})
        # GitLab rejects some list moves on group boards with "List could not be
        # moved!". New lists are appended in workflow order; report when existing
        # lists still need manual ordering instead of failing the whole apply.
        board_lists = self.get_all(lists_path)
        stage_order = [
            item.get("label", {}).get("name")
            for item in sorted(board_lists, key=lambda item: item.get("position", 0))
            if item.get("label", {}).get("name") in stage_ids
        ]
        return stage_order == stage_ids


def apply(config: GitLabConfig, members: list[GitLabMember]) -> int:
    """Ensure the project exists and invite every member; return projects touched."""
    client = GitLabClient(config, config.token())
    project = client.project()
    for member in members:
        client.invite_member(project["id"], member)
    return 1


def apply_work_management(config: GitLabConfig, stage_ids: list[str]) -> bool:
    """Ensure the GitLab Issue Board reflects the workflow stages."""
    client = GitLabClient(config, config.token())
    return client.ensure_workflow_board(stage_ids)
