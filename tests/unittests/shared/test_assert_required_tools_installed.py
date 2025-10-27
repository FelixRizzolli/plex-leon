import pytest

import plex_leon.shared.assert_required_tools_installed as assert_tools_mod
from plex_leon.shared.assert_required_tools_installed import (
    assert_required_tools_installed,
)


def test_assert_required_tools_installed_all_present(monkeypatch: pytest.MonkeyPatch):
    """Simulate both required binaries being on PATH and ensure no error is raised."""
    calls: list[str] = []

    def fake_which(name: str) -> str:
        calls.append(name)
        return f"/usr/bin/{name}"

    monkeypatch.setattr(assert_tools_mod.shutil, "which", fake_which)

    assert_required_tools_installed()
    assert set(calls) == {"ffprobe", "mediainfo"}


def test_assert_required_tools_installed_missing_tool(monkeypatch: pytest.MonkeyPatch):
    """Ensure a RuntimeError is raised when mediainfo is reported missing."""
    def fake_which(name: str) -> str | None:
        return None if name == "mediainfo" else f"/usr/bin/{name}"

    monkeypatch.setattr(assert_tools_mod.shutil, "which", fake_which)

    with pytest.raises(RuntimeError) as exc:
        assert_required_tools_installed()
    assert "mediainfo" in str(exc.value)
