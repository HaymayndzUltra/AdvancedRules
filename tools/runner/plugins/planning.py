#!/usr/bin/env python3
import re
from pathlib import Path
from tools.runner.io_utils import write_text, MB


def _extract_project_title(brief_content: str) -> str:
    """Extract a project title from the client brief.

    - Prefer a line like 'Project Brief: <Title>'
    - Fallback to first non-empty non-bullet line
    """
    lines = [l.strip() for l in (brief_content or '').splitlines()]
    for l in lines:
        if l.lower().startswith('project brief:'):
            title = l.split(':', 1)[-1].strip() or ''
            if title:
                return title
    for l in lines:
        if l and not l.startswith(('#', '-', '*')):
            return l
    return 'Project'


def _slug(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return re.sub(r'-+', '-', s).strip('-') or 'item'


def _parse_backlog_to_epics(backlog_text: str):
    """Parse markdown-like backlog content into epics -> tasks -> acceptance.

    The backlog is stored with a .yaml extension but contains markdown headings.
    """
    epics = []
    current_epic = None
    collecting_acceptance = False
    lines = backlog_text.splitlines()

    for raw in lines:
        line = raw.strip()

        # Epic header
        m_epic = re.match(r'^##\s+Epic:\s*(.+)$', line)
        if m_epic:
            # Flush previous epic
            if current_epic:
                epics.append(current_epic)
            title = m_epic.group(1).strip()
            current_epic = {"id": _slug(title), "title": title, "tasks": []}
            collecting_acceptance = False
            continue

        # User Story header
        m_story = re.match(r'^###\s+User Story\s+\d+:\s*(.+)$', line)
        if m_story and current_epic is not None:
            title = m_story.group(1).strip()
            current_epic["tasks"].append({
                "id": _slug(title),
                "desc": title,
                "acceptance": []
            })
            collecting_acceptance = False
            continue

        # Acceptance Criteria start
        if current_epic and 'Acceptance Criteria' in line:
            collecting_acceptance = True
            continue

        # Acceptance items
        if collecting_acceptance and current_epic and current_epic["tasks"]:
            m_bullet = re.match(r'^-\s*(?:\[\s*\]\s*)?(.*)$', line)
            if m_bullet:
                text = m_bullet.group(1).strip()
                if text:
                    current_epic["tasks"][-1]["acceptance"].append(text)
                continue
            # stop collection at blank line
            if not line:
                collecting_acceptance = False

    if current_epic:
        epics.append(current_epic)
    return epics


def _render_task_breakdown_yaml(project: str, epics: list) -> str:
    out = []
    out.append('schema_version: "1.0.0"\n')
    out.append(f'project: "{project}"\n\n')
    out.append('epics:\n')
    for e in epics:
        out.append(f'  - id: {e["id"]}\n')
        out.append(f'    title: {e["title"]}\n')
        out.append('    tasks:\n')
        for t in e.get('tasks', []):
            out.append(f'      - id: {t["id"]}\n')
            out.append(f'        desc: {t["desc"]}\n')
            if t.get('acceptance'):
                out.append('        acceptance:\n')
                for a in t['acceptance']:
                    out.append(f'          - {a}\n')
    return ''.join(out)


def run() -> None:
    plan_dir = MB / "plan"
    backlog_path = plan_dir / "product_backlog.yaml"
    acc_path = plan_dir / "acceptance_criteria.json"
    brief_path = plan_dir / "client_brief.md"

    if not backlog_path.exists():
        raise SystemExit("product_backlog.yaml missing")
    if not acc_path.exists():
        raise SystemExit("acceptance_criteria.json missing")

    # Read brief title (optional)
    brief_text = brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""
    project = _extract_project_title(brief_text)

    # Read backlog text and build breakdown
    backlog_text = backlog_path.read_text(encoding="utf-8")
    epics = _parse_backlog_to_epics(backlog_text)
    # Fallback skeleton if parse yields nothing
    if not epics:
        epics = [{"id": "planning", "title": "Planning", "tasks": [{"id": "review-backlog", "desc": "Review backlog items", "acceptance": []}]}]

    breakdown_yaml = _render_task_breakdown_yaml(project, epics)

    # Emit artifacts
    write_text(plan_dir / "Action_Plan.md", "# Action Plan\n", role="planning_ai")
    write_text(plan_dir / "technical_plan.md", "# Technical Plan\n", role="planning_ai")
    write_text(plan_dir / "task_breakdown.yaml", breakdown_yaml, role="planning_ai")

