# Command API Contract: Consumed HTTP

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Name** | `Consumed HTTP` |
| **Protocol** | `http` |
| **Direction** | `consumed` |
| **Spec File** | `spec/api/consumed_http.md` |
| **Provider / Consumer Boundary** | `oq apply` calls the REST APIs of OpenProject, GitHub, GitLab and Jira Cloud. Base URL comes from the provider target (`config.baseURL`; GitHub defaults to `https://api.github.com`). The CLI provides no HTTP API. |
| **Client / Transport / Handler** | `urllib.request.urlopen` (30 s timeout) wrapped by `OpenProjectClient._request`, `GitHubClient.request`, `GitLabClient.request`, `JiraClient.request` |

---

## 2. Endpoint Catalog

| ID | Protocol | Operation / Method | Path / Module / Topic | Response Digest | Source | Description |
|----|----------|--------------------|-----------------------|-----------------|--------|-------------|
| API-001 | HTTP | `GET` | `/repos/{owner}/{repo}` | status: 200 -> repository JSON; 404 -> create | `cli/providers/github/__init__.py:150` | Check whether the GitHub repository exists |
| API-002 | HTTP | `GET` | `/user` | fields: login | `cli/providers/github/__init__.py:154` | Decide user vs organization repository creation |
| API-003 | HTTP | `POST` | `/user/repos` | fields: name, private; returns created repository | `cli/providers/github/__init__.py:160` | Create a repository under the authenticated user |
| API-004 | HTTP | `POST` | `/orgs/{owner}/repos` | fields: name, private; returns created repository | `cli/providers/github/__init__.py:161` | Create a repository in an organization |
| API-005 | HTTP | `PUT` | `/repos/{owner}/{repo}/collaborators/{username}` | fields: permission; returns invitation result | `cli/providers/github/__init__.py:167` | Invite a collaborator with a permission |
| API-006 | HTTP | `GET` | `/projects/{project}` | fields: id; project JSON | `cli/providers/gitlab/__init__.py:113` | Fetch the configured GitLab project (URL-encoded path) |
| API-007 | HTTP | `GET` | `/users?username={username}` | list of users; empty -> error "GitLab user not found" | `cli/providers/gitlab/__init__.py:117` | Resolve a GitLab user id |
| API-008 | HTTP | `POST` | `/projects/{id}/members` | fields: user_id, access_level; returns member JSON | `cli/providers/gitlab/__init__.py:122` | Add a project member with an access level |
| API-009 | HTTP | `GET` | `/rest/api/3/project/{key}` | status: 200 -> project JSON; error otherwise | `cli/providers/jira_cloud/__init__.py:274` | Look up the Jira project |
| API-010 | HTTP | `POST` | `/rest/api/3/project` | created project; request fields: key, leadAccountId | `cli/providers/jira_cloud/__init__.py:360` | Create the Jira project from a template |
| API-011 | HTTP | `GET` | `/rest/api/3/myself` | fields: accountId | `cli/providers/jira_cloud/__init__.py:366` | Obtain the project lead account |
| API-012 | HTTP | `POST` | `/rest/api/3/user` | fields: accountId; invited or existing user | `cli/providers/jira_cloud/__init__.py:285` | Invite a user by email |
| API-013 | HTTP | `GET` | `/rest/api/3/user/assignable/search?project={key}` | fields: accountId; list of users | `cli/providers/jira_cloud/__init__.py:293` | Find an existing assignable user |
| API-014 | HTTP | `GET` | `/rest/api/3/project/{key}/role` | map: role name -> role URL | `cli/providers/jira_cloud/__init__.py:378` | Discover project roles |
| API-015 | HTTP | `POST` | `{role url}` | fields: user; role actor update | `cli/providers/jira_cloud/__init__.py:396` | Add a user to a project role |
| API-016 | HTTP | `POST` | `/rest/api/3/issue` | fields: id; created issue | `cli/providers/jira_cloud/__init__.py:403` | Create an issue for a planned resource |
| API-017 | HTTP | `GET` | `/rest/agile/1.0/board?projectKeyOrId={key}` | fields: id, self; boards list | `cli/providers/jira_cloud/__init__.py:308` | Find an existing Kanban board |
| API-018 | HTTP | `GET` | `/rest/agile/1.0/board/{id}` | fields: id, self; board JSON | `cli/providers/jira_cloud/__init__.py:316` | Read a board |
| API-019 | HTTP | `POST` | `/rest/api/3/filter` | fields: id; created filter | `cli/providers/jira_cloud/__init__.py:320` | Create the board filter |
| API-020 | HTTP | `POST` | `/rest/agile/1.0/board` | fields: id, self; created Kanban board | `cli/providers/jira_cloud/__init__.py:328` | Create a Kanban board |
| API-021 | HTTP | `GET` | `/api/v3/projects/{identifier}` | fields: id, href; 404 -> not found | `cli/providers/openproject/__init__.py:432` | Find an existing OpenProject project |
| API-022 | HTTP | `POST` | `/api/v3/projects` | fields: id, _links.self.href; created project | `cli/providers/openproject/__init__.py:650` | Create the project |
| API-023 | HTTP | `GET` | `/api/v3/users?pageSize=1000` | _embedded.elements: users | `cli/providers/openproject/__init__.py:453` | Resolve users by email |
| API-024 | HTTP | `POST` | `/api/v3/users` | fields: id; invited user | `cli/providers/openproject/__init__.py:460` | Invite a missing user |
| API-025 | HTTP | `GET` | `/api/v3/roles?pageSize=1000` | _embedded.elements: roles | `cli/providers/openproject/__init__.py:479` | Resolve role hrefs |
| API-026 | HTTP | `GET` | `/api/v3/statuses` | _embedded.elements: statuses | `cli/providers/openproject/__init__.py:488` | Resolve Kanban status columns |
| API-027 | HTTP | `POST` | `/api/v3/grids/form` | fields: validated payload for grid creation | `cli/providers/openproject/__init__.py:587` | Validate a Kanban board grid |
| API-028 | HTTP | `POST` | `/api/v3/grids` | fields: id, _links.self.href; created board | `cli/providers/openproject/__init__.py:589` | Create the Kanban board |
| API-029 | HTTP | `POST` | `/api/v3/memberships` | fields: id, _links.self.href; membership | `cli/providers/openproject/__init__.py:623` | Add a project member |
| API-030 | HTTP | `POST` | `/api/v3/projects/{id}/work_packages?notify={bool}` | fields: id, _links.self.href; created work package | `cli/providers/openproject/__init__.py:657` | Create requirement/stage/reviewer work packages |

### Unresolved Operation Candidates

| Candidate ID | Protocol | Fallback Operation / Method | Fallback Path / Module / Topic | Unresolved Reason |
|--------------|----------|-----------------------------|--------------------------------|-------------------|
| UNRESOLVED-001 | HTTP | `PATCH` | `{grid href}` | `[NEEDS_REVIEW:api_path]` Board href is read from the create/GET response at runtime (rename and column updates) |
| UNRESOLVED-002 | HTTP | `PATCH` | `{work package href}` | `[NEEDS_REVIEW:api_path]` Work package href comes from the stored provider state |
| UNRESOLVED-003 | HTTP | `POST` | `{work package href}/watchers` | `[NEEDS_REVIEW:api_path]` Work package href comes from the stored provider state; adds a code reviewer as watcher |

---

<!-- Template: skill-spec-base/templates/command/api.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**

