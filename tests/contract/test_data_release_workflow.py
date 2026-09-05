from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/data-release.yml"


def test_data_release_workflow_is_path_scoped_and_checks_exact_pr_head():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert 'pull_request:' in workflow
    assert 'branches: [main]' in workflow
    assert '"data/curation/manifests/**"' in workflow
    assert '"data/curation/releases/**"' in workflow
    assert '"data/reference/parameter_registry_v1.json"' in workflow
    assert '".github/workflows/data-release.yml"' in workflow
    assert 'ref: ${{ github.event.pull_request.head.sha }}' in workflow
    assert 'repository: ${{ github.event.pull_request.head.repo.full_name }}' in workflow


def test_data_release_workflow_uses_disposable_outputs_and_no_promotion():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "runner.temp" in workflow
    assert "--no-promote" in workflow
    assert "--qualification" in workflow
    assert "upload-artifact@v4" in workflow
    assert "current_release" in workflow
    assert "rglob" not in workflow
    assert "glob(" not in workflow
