"""Interactive scaffolding for a first Open Quality contract."""

from __future__ import annotations

import math
import re
import unicodedata
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import yaml

from .providers.jira_cloud import validate_project_key


CHARACTERISTICS = (
    "functional-suitability",
    "performance-efficiency",
    "compatibility",
    "interaction-capability",
    "reliability",
    "security",
    "maintainability",
    "flexibility",
    "safety",
    "beneficialness",
    "freedom-from-risk",
    "acceptability",
)

WORK_MANAGEMENT_PROVIDERS = (
    ("openproject", "OpenProject"),
    ("jira-cloud", "Jira Cloud"),
    ("github-projects", "GitHub Projects"),
)

SOURCE_CONTROL_PROVIDERS = (
    ("github-repository", "GitHub"),
    ("gitlab", "GitLab"),
)

OPERATORS = (
    "exists",
    "approved",
    "greaterThanOrEqual",
    "greaterThan",
    "lessThanOrEqual",
    "lessThan",
    "equals",
    "notEquals",
)


def _slug(value: str) -> str:
    """Convert a human-readable name to a schema-compatible resource ID."""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode().lower()
    result = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    if result and not result[0].isalpha():
        result = f"project-{result}"
    return result


def _prompt(
    input_fn: Callable[[str], str],
    label: str,
    default: str | None = None,
    *,
    required: bool = True,
) -> str:
    """Read one value, showing a default and repeating when required."""
    while True:
        suffix = f" [{default}]" if default else ""
        answer = input_fn(f"{label}{suffix}: ").strip()
        if not answer and default is not None:
            return default
        if answer or not required:
            return answer
        print("Informe um valor para continuar.")


def _prompt_id(
    input_fn: Callable[[str], str], label: str, default: str
) -> str:
    """Prompt for an ID and normalize it to the format accepted by the schema."""
    while True:
        value = _prompt(input_fn, label, default)
        identifier = _slug(value)
        if identifier:
            return identifier
        print("O ID precisa conter pelo menos uma letra ou número.")


def _select_many(
    input_fn: Callable[[str], str],
    title: str,
    options: tuple[str, ...],
    *,
    required: bool,
) -> list[str]:
    """Select options by their displayed number or full identifier."""
    print(title)
    for index, option in enumerate(options, 1):
        print(f"  {index}. {option}")
    print("Digite os números separados por vírgula; Enter seleciona nenhum.")
    while True:
        answer = input_fn("Seleção: ").strip()
        if not answer:
            if not required:
                return []
            print("Escolha pelo menos uma opção.")
            continue
        selected: list[str] = []
        invalid: list[str] = []
        for item in (part.strip() for part in answer.split(",")):
            if not item:
                continue
            if item.isdigit() and 1 <= int(item) <= len(options):
                value = options[int(item) - 1]
            elif item in options:
                value = item
            else:
                invalid.append(item)
                continue
            if value not in selected:
                selected.append(value)
        if invalid:
            print("Opções desconhecidas: " + ", ".join(invalid))
            continue
        if selected or not required:
            return selected
        print("Escolha pelo menos uma opção.")


def _select_one(
    input_fn: Callable[[str], str],
    title: str,
    options: tuple[tuple[str, str], ...],
) -> str | None:
    """Select at most one provider by number or identifier; blank means none."""
    print(title)
    for index, (_, label) in enumerate(options, 1):
        print(f"  {index}. {label}")
    print("Digite o número ou identificador; Enter seleciona nenhum.")
    while True:
        answer = input_fn("Seleção: ").strip()
        if not answer:
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1][0]
        for identifier, _ in options:
            if answer == identifier:
                return identifier
        print("Escolha inválida; selecione uma opção ou pressione Enter.")


def _humanize(identifier: str) -> str:
    return " ".join(word.capitalize() for word in identifier.split("-"))


def _unique_id(base: str, used_ids: set[str]) -> str:
    """Return `base` or the first numbered variant not in `used_ids`."""
    candidate = base
    suffix = 2
    while candidate in used_ids:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def _provider_config(
    provider: str, input_fn: Callable[[str], str]
) -> dict[str, Any]:
    """Prompt for provider fields required by its adapter."""
    if provider == "openproject":
        config = {
            "baseURL": _prompt(
                input_fn,
                "URL da instância OpenProject",
                "https://openproject.example.com",
            ),
        }
    elif provider == "jira-cloud":
        base_url = _prompt(
            input_fn, "URL do Jira Cloud", "https://your-domain.atlassian.net"
        )
        project_key = _prompt(input_fn, "Chave do projeto Jira", "PROJ")
        while True:
            try:
                validate_project_key(project_key)
                break
            except ValueError as error:
                print(error)
                project_key = _prompt(input_fn, "Chave do projeto Jira", "PROJ")
        config = {
            "baseURL": base_url,
            "projectKey": project_key,
        }
    elif provider == "github-projects":
        owner = _prompt(input_fn, "Organização ou usuário do GitHub")
        owner_type = _prompt(
            input_fn, "Tipo do owner (organization/user)", "organization"
        )
        while owner_type not in {"organization", "user"}:
            print("Tipo de owner inválido.")
            owner_type = _prompt(
                input_fn, "Tipo do owner (organization/user)", "organization"
            )
        config = {
            "owner": owner,
            "project": _prompt(input_fn, "Nome do quadro GitHub Projects"),
            "ownerType": owner_type,
        }
        provider = "github"
    elif provider == "github-repository":
        owner = _prompt(input_fn, "Organização ou usuário do GitHub")
        owner_type = _prompt(input_fn, "Tipo do owner (organization/user)", "user")
        while owner_type not in {"organization", "user"}:
            print("Tipo de owner inválido.")
            owner_type = _prompt(
                input_fn, "Tipo do owner (organization/user)", "user"
            )
        visibility = _prompt(input_fn, "Visibilidade (private/public)", "private")
        while visibility not in {"private", "public"}:
            print("Visibilidade inválida.")
            visibility = _prompt(
                input_fn, "Visibilidade (private/public)", "private"
            )
        config = {
            "owner": owner,
            "ownerType": owner_type,
            "repository": _prompt(input_fn, "Nome do repositório"),
            "visibility": visibility,
        }
        provider = "github"
    else:
        config = {
            "baseURL": _prompt(
                input_fn, "URL da API GitLab", "https://gitlab.com/api/v4"
            ),
            "project": _prompt(input_fn, "Caminho do projeto (grupo/projeto)"),
        }
    return {"provider": provider, "config": config}


def _quality_resources(
    input_fn: Callable[[str], str],
    characteristics: list[str],
    reserved_ids: set[str],
) -> tuple[
    list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]
]:
    """Create one requirement and measure scaffold for every selected characteristic."""
    quality: list[dict[str, Any]] = []
    requirements: dict[str, dict[str, Any]] = {}
    measures: dict[str, dict[str, Any]] = {}
    used_ids = set(reserved_ids)

    for characteristic in characteristics:
        label = _humanize(characteristic)
        requirement_id = _prompt_id(
            input_fn,
            f"ID do requisito para {label}",
            _unique_id(f"{characteristic}-requirement", used_ids),
        )
        while requirement_id in used_ids:
            print(f"O ID {requirement_id!r} já está em uso.")
            requirement_id = _prompt_id(
                input_fn,
                f"ID do requisito para {label}",
                _unique_id(f"{characteristic}-requirement", used_ids),
            )
        used_ids.add(requirement_id)
        metric_id = _prompt_id(
            input_fn,
            f"ID da medida para {label}",
            _unique_id(f"{characteristic}-measure", used_ids),
        )
        while metric_id in used_ids:
            print(f"O ID {metric_id!r} já está em uso.")
            metric_id = _prompt_id(
                input_fn,
                f"ID da medida para {label}",
                _unique_id(f"{characteristic}-measure", used_ids),
            )
        used_ids.add(metric_id)

        statement = _prompt(
            input_fn,
            f"Requisito de qualidade para {label}",
            f"TODO: defina um critério mensurável para {label.lower()}.",
        )
        priority = _prompt(input_fn, "Prioridade (low/medium/high/critical)", "medium")
        while priority not in {"low", "medium", "high", "critical"}:
            print("Prioridade inválida.")
            priority = _prompt(
                input_fn, "Prioridade (low/medium/high/critical)", "medium"
            )

        unit = _prompt(input_fn, "Unidade da medida", "value")
        operator_label = "Operador do alvo (" + ", ".join(OPERATORS) + ")"
        operator = _prompt(input_fn, operator_label, "exists")
        while operator not in OPERATORS:
            print("Operador inválido.")
            operator = _prompt(input_fn, operator_label, "exists")
        default_target = "true" if operator in {"exists", "approved"} else "1"
        while True:
            raw_target = _prompt(input_fn, "Valor esperado do alvo", default_target)
            try:
                target_value = yaml.safe_load(raw_target)
            except yaml.YAMLError:
                target_value = None
            if isinstance(target_value, (str, int, float, bool)) and not (
                isinstance(target_value, float) and not math.isfinite(target_value)
            ):
                break
            print("O valor do alvo precisa ser texto, número ou booleano.")

        target: dict[str, Any] = {"operator": operator, "value": target_value}
        if operator not in {"exists", "approved"}:
            target["unit"] = unit
        quality.append(
            {"characteristic": characteristic, "requirements": [requirement_id]}
        )
        requirements[requirement_id] = {
            "specVersion": "0.1",
            "kind": "QualityRequirement",
            "metadata": {"id": requirement_id, "name": f"{label} requirement"},
            "spec": {
                "statement": statement,
                "priority": priority,
                "qualityMeasures": [
                    {"qualityMeasure": metric_id, "target": target}
                ],
            },
        }
        measures[metric_id] = {
            "specVersion": "0.1",
            "kind": "QualityMeasure",
            "metadata": {"id": metric_id, "name": f"{label} measure"},
            "spec": {
                "unit": unit,
                "description": f"Measurement used by the {label.lower()} requirement.",
            },
        }

    return quality, requirements, measures


def _render_yaml(document: dict[str, Any]) -> str:
    return yaml.safe_dump(
        document,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=100,
    )


def _stage_ids(value: str) -> list[str]:
    """Normalize comma-separated stage names and remove duplicate IDs."""
    return list(
        dict.fromkeys(
            identifier
            for part in value.split(",")
            if (identifier := _slug(part.strip()))
        )
    )


def _read_contract(root: Path) -> tuple[Path, dict[str, Any], dict[Path, Any], set[str]]:
    """Load the contract and YAML documents without requiring a complete scaffold."""
    if not root.is_dir():
        raise ValueError(f"quality directory {root} does not exist")
    yaml_paths = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix in {".yaml", ".yml"}
    )
    documents: dict[Path, Any] = {}
    contract_paths: list[Path] = []
    reserved_ids: set[str] = set()
    for path in yaml_paths:
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as error:
            raise ValueError(f"{path}: {error}") from error
        documents[path] = document
        if not isinstance(document, dict):
            continue
        if document.get("kind") == "QualityContract":
            contract_paths.append(path)
        metadata = document.get("metadata")
        if isinstance(metadata, dict) and isinstance(metadata.get("id"), str):
            reserved_ids.add(metadata["id"])

    if len(contract_paths) != 1:
        raise ValueError(
            f"expected exactly one QualityContract in {root}, found {len(contract_paths)}"
        )
    contract_path = contract_paths[0]
    contract = documents[contract_path]
    if not isinstance(contract.get("spec"), dict):
        raise ValueError("QualityContract.spec must be a mapping")
    return contract_path, contract, documents, reserved_ids


def _contract_spec(contract: dict[str, Any]) -> dict[str, Any]:
    spec = contract.get("spec")
    if not isinstance(spec, dict):
        raise ValueError("QualityContract.spec must be a mapping")
    return spec


def _reference_list(spec: dict[str, Any], key: str) -> list[str]:
    values = spec.get(key) or []
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ValueError(f"QualityContract.spec.{key} must be a list of IDs")
    return values


def _write_resources(
    root: Path,
    contract_path: Path,
    contract: dict[str, Any],
    resources: dict[Path, dict[str, Any]],
) -> None:
    """Write new resources and update the contract, refusing path collisions."""
    output_paths = [root / relative_path for relative_path in resources]
    collisions = [path for path in output_paths if path.exists()]
    if collisions:
        raise ValueError(
            "refusing to overwrite existing resource file(s): "
            + ", ".join(str(path) for path in collisions)
        )
    for relative_path, resource in resources.items():
        output_path = root / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(_render_yaml(resource), encoding="utf-8")
    contract_path.write_text(_render_yaml(contract), encoding="utf-8")


def _print_next_steps(root: Path, contract: dict[str, Any]) -> None:
    """Explain which required pieces are still missing before validation."""
    spec = _contract_spec(contract)
    missing: list[str] = []
    if not spec.get("workflow"):
        missing.append("workflow")
    if missing:
        print("Ainda falta adicionar: " + " e ".join(missing) + ".")
        for resource in missing:
            print(f"  oq add {resource} {root}")
    else:
        print(f"Próximo passo: oq validate {root}")


def initialize(
    directory: str | Path,
    *,
    input_fn: Callable[[str], str] | None = None,
) -> int:
    """Interactively create a base contract in an empty directory."""
    input_fn = input_fn or input
    root = Path(directory)
    if root.exists() and not root.is_dir():
        raise ValueError(f"{root} already exists and is not a directory")
    if root.exists() and any(root.iterdir()):
        raise ValueError(f"{root} is not empty; choose an empty directory")

    default_name = _humanize(_slug(root.name) or "quality-project")
    name = _prompt(input_fn, "Nome do projeto", default_name)
    project_id = _prompt_id(
        input_fn, "ID do projeto", _slug(name) or "quality-project"
    )
    description = _prompt(input_fn, "Descrição", "", required=False)

    providers: dict[str, dict[str, Any]] = {}
    work_management = _select_one(
        input_fn,
        "Qual provedor usar para gestão de trabalho (workManagement)?",
        WORK_MANAGEMENT_PROVIDERS,
    )
    if work_management:
        providers["workManagement"] = _provider_config(work_management, input_fn)

    source_control = _select_one(
        input_fn,
        "Qual provedor usar para controle de código (sourceControl)?",
        SOURCE_CONTROL_PROVIDERS,
    )
    if source_control:
        providers["sourceControl"] = _provider_config(source_control, input_fn)

    workflow_id, workflow_resources = _workflow_resources(
        input_fn, {project_id}
    )

    contract: dict[str, Any] = {
        "specVersion": "0.1",
        "kind": "QualityContract",
        "metadata": {"id": project_id, "name": name},
        "spec": {"quality": [], "workflow": workflow_id},
    }
    if description:
        contract["metadata"]["description"] = description
    if providers:
        contract["providers"] = providers

    root.mkdir(parents=True, exist_ok=True)
    contract_path = root / "quality-contract.yaml"
    _write_resources(root, contract_path, contract, workflow_resources)

    print(f"Base do contrato criada em {root}.")
    print("Características de qualidade são opcionais.")
    print("Próximo passo:")
    print(f"  oq validate {root}")
    print("Se quiser adicionar características específicas:")
    print(f"  oq add characteristic {root}")
    if providers:
        print(
            "As credenciais são lidas de variáveis de ambiente ao executar `oq apply`; "
            "nenhum segredo foi gravado nos YAMLs."
        )
    return 0


def add_characteristic(
    directory: str | Path,
    *,
    input_fn: Callable[[str], str] | None = None,
) -> int:
    """Add quality characteristics and their requirement/measure resources."""
    input_fn = input_fn or input
    root = Path(directory)
    contract_path, contract, documents, reserved_ids = _read_contract(root)
    spec = _contract_spec(contract)
    existing_quality = spec.get("quality") or []
    if not isinstance(existing_quality, list):
        raise ValueError("QualityContract.spec.quality must be a list")
    existing = {
        entry.get("characteristic")
        for entry in existing_quality
        if isinstance(entry, dict)
    }
    available = tuple(item for item in CHARACTERISTICS if item not in existing)
    if not available:
        raise ValueError("all supported quality characteristics are already included")

    selected = _select_many(
        input_fn,
        "Quais características de qualidade quer adicionar?",
        available,
        required=True,
    )
    quality, requirements, measures = _quality_resources(
        input_fn, selected, reserved_ids
    )
    spec["quality"] = [*existing_quality, *quality]
    metric_ids = _reference_list(spec, "metrics")
    for metric_id in measures:
        if metric_id not in metric_ids:
            metric_ids.append(metric_id)
    if metric_ids:
        spec["metrics"] = metric_ids

    resources: dict[Path, dict[str, Any]] = {}
    for requirement_id, resource in requirements.items():
        resources[Path("quality-requirements") / f"{requirement_id}.yaml"] = resource
    for metric_id, resource in measures.items():
        resources[Path("quality-measures") / f"{metric_id}.yaml"] = resource
    _write_resources(root, contract_path, contract, resources)
    print(f"Características adicionadas ao contrato em {root}.")
    _print_next_steps(root, contract)
    return 0


def add_documentation(
    directory: str | Path,
    *,
    input_fn: Callable[[str], str] | None = None,
) -> int:
    """Add a documentation Artifact and reference it from the contract."""
    input_fn = input_fn or input
    root = Path(directory)
    contract_path, contract, _, reserved_ids = _read_contract(root)
    spec = _contract_spec(contract)
    artifact_id = _prompt_id(
        input_fn,
        "ID da documentação",
        _unique_id("project-documentation", reserved_ids),
    )
    while artifact_id in reserved_ids:
        print(f"O ID {artifact_id!r} já está em uso.")
        artifact_id = _prompt_id(
            input_fn,
            "ID da documentação",
            _unique_id("project-documentation", reserved_ids),
        )
    name = _prompt(input_fn, "Nome da documentação", _humanize(artifact_id))
    external_link = _prompt(input_fn, "URL da documentação")
    while not (urlparse(external_link).scheme and urlparse(external_link).netloc):
        print("Informe uma URL absoluta, incluindo esquema e domínio.")
        external_link = _prompt(input_fn, "URL da documentação")
    required_answer = _prompt(input_fn, "Obrigatória? (yes/no)", "no").lower()
    while required_answer not in {"yes", "no", "y", "n"}:
        print("Responda yes ou no.")
        required_answer = _prompt(input_fn, "Obrigatória? (yes/no)", "no").lower()

    artifact_spec: dict[str, Any] = {
        "category": "documentation",
        "externalLink": external_link,
        "required": required_answer in {"yes", "y"},
    }
    content_type = _prompt(
        input_fn, "Content type", "text/markdown", required=False
    )
    if content_type:
        artifact_spec["contentType"] = content_type
    spec["documentation"] = [*_reference_list(spec, "documentation"), artifact_id]
    resource = {
        "specVersion": "0.1",
        "kind": "Artifact",
        "metadata": {"id": artifact_id, "name": name},
        "spec": artifact_spec,
    }
    _write_resources(
        root,
        contract_path,
        contract,
        {Path("artifacts") / f"{artifact_id}.yaml": resource},
    )
    print(f"Documentação {artifact_id} adicionada ao contrato em {root}.")
    _print_next_steps(root, contract)
    return 0


def add_metrics(
    directory: str | Path,
    *,
    input_fn: Callable[[str], str] | None = None,
) -> int:
    """Add a QualityMeasure and reference it from the contract."""
    input_fn = input_fn or input
    root = Path(directory)
    contract_path, contract, _, reserved_ids = _read_contract(root)
    spec = _contract_spec(contract)
    metric_id = _prompt_id(
        input_fn,
        "ID da métrica",
        _unique_id("custom-measure", reserved_ids),
    )
    while metric_id in reserved_ids:
        print(f"O ID {metric_id!r} já está em uso.")
        metric_id = _prompt_id(
            input_fn,
            "ID da métrica",
            _unique_id("custom-measure", reserved_ids),
        )
    name = _prompt(input_fn, "Nome da métrica", _humanize(metric_id))
    unit = _prompt(input_fn, "Unidade da métrica", "value")
    description = _prompt(input_fn, "Descrição da métrica", "", required=False)
    source_hint = _prompt(input_fn, "Fonte dos dados", "", required=False)

    metric_spec: dict[str, Any] = {"unit": unit}
    if description:
        metric_spec["description"] = description
    if source_hint:
        metric_spec["sourceHint"] = source_hint
    resource = {
        "specVersion": "0.1",
        "kind": "QualityMeasure",
        "metadata": {"id": metric_id, "name": name},
        "spec": metric_spec,
    }
    metric_ids = _reference_list(spec, "metrics")
    metric_ids.append(metric_id)
    spec["metrics"] = metric_ids
    _write_resources(
        root,
        contract_path,
        contract,
        {Path("quality-measures") / f"{metric_id}.yaml": resource},
    )
    print(f"Métrica {metric_id} adicionada ao contrato em {root}.")
    _print_next_steps(root, contract)
    return 0


def _default_stages(reserved_ids: set[str]) -> str:
    preferred = [
        stage_id
        for stage_id in ("planning", "development", "review")
        if stage_id not in reserved_ids
    ]
    return ",".join(preferred or [_unique_id("stage", reserved_ids)])


def _workflow_resources(
    input_fn: Callable[[str], str], reserved_ids: set[str]
) -> tuple[str, dict[Path, dict[str, Any]]]:
    """Prompt for a workflow and build its workflow and stage YAML resources."""
    workflow_id = _prompt_id(
        input_fn,
        "ID do workflow",
        _unique_id("standard-release", reserved_ids),
    )
    while workflow_id in reserved_ids:
        print(f"O ID {workflow_id!r} já está em uso.")
        workflow_id = _prompt_id(
            input_fn,
            "ID do workflow",
            _unique_id("standard-release", reserved_ids),
        )
    reserved_ids.add(workflow_id)

    default_stages = _default_stages(reserved_ids)
    raw_stages = _prompt(
        input_fn,
        "Etapas do workflow (IDs separados por vírgula)",
        default_stages,
    )
    stage_ids = _stage_ids(raw_stages)
    while not stage_ids or any(stage_id in reserved_ids for stage_id in stage_ids):
        collisions = sorted(set(stage_ids) & reserved_ids)
        if collisions:
            print("IDs de etapa já usados: " + ", ".join(collisions))
        else:
            print("O workflow precisa ter pelo menos uma etapa.")
        default_stages = _default_stages(reserved_ids)
        raw_stages = _prompt(
            input_fn,
            "Etapas do workflow (IDs separados por vírgula)",
            default_stages,
        )
        stage_ids = _stage_ids(raw_stages)

    resources: dict[Path, dict[str, Any]] = {
        Path("workflows") / f"{workflow_id}.yaml": {
            "specVersion": "0.1",
            "kind": "Workflow",
            "metadata": {"id": workflow_id, "name": _humanize(workflow_id)},
            "spec": {"stages": stage_ids},
        }
    }
    previous_stage: str | None = None
    for stage_id in stage_ids:
        stage_spec: dict[str, Any] = {}
        if previous_stage:
            stage_spec["dependsOn"] = [previous_stage]
        resources[Path("stages") / f"{stage_id}.yaml"] = {
            "specVersion": "0.1",
            "kind": "Stage",
            "metadata": {"id": stage_id, "name": _humanize(stage_id)},
            "spec": stage_spec,
        }
        previous_stage = stage_id
    return workflow_id, resources


def add_workflow(
    directory: str | Path,
    *,
    input_fn: Callable[[str], str] | None = None,
) -> int:
    """Add a Workflow and its Stage resources, then select it in the contract."""
    input_fn = input_fn or input
    root = Path(directory)
    contract_path, contract, _, reserved_ids = _read_contract(root)
    spec = _contract_spec(contract)
    workflow_id, resources = _workflow_resources(input_fn, reserved_ids)
    spec["workflow"] = workflow_id
    _write_resources(root, contract_path, contract, resources)
    print(f"Workflow {workflow_id} adicionado ao contrato em {root}.")
    _print_next_steps(root, contract)
    return 0
