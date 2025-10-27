import json
from pathlib import Path

import pytest

import plex_leon.shared.read_video_resolution as read_resolution_mod
from plex_leon.shared.read_video_resolution import read_video_resolution


class DummyCompletedProcess:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_read_video_resolution_prefers_ffprobe_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    file_path = tmp_path / "video.mkv"
    file_path.write_bytes(b"")
    payload = json.dumps({"streams": [{"width": 1920, "height": 1080}]})

    def fake_run(cmd, **kwargs):  # type: ignore[override]
        return DummyCompletedProcess(0, stdout=payload)

    monkeypatch.setattr(read_resolution_mod.subprocess, "run", fake_run)

    assert read_video_resolution(file_path) == (1920, 1080)


def test_read_video_resolution_falls_back_to_mediainfo(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    file_path = tmp_path / "video.mkv"
    file_path.write_bytes(b"")
    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):  # type: ignore[override]
        calls.append(cmd)
        if cmd[0] == "ffprobe":
            raise FileNotFoundError
        media_payload = json.dumps(
            {
                "media": {
                    "track": [
                        {"@type": "Video", "Width": "1920 pixels", "Height": "1080"}
                    ]
                }
            }
        )
        return DummyCompletedProcess(0, stdout=media_payload)

    monkeypatch.setattr(read_resolution_mod.subprocess, "run", fake_run)

    assert read_video_resolution(file_path) == (1920, 1080)
    assert any(cmd[0] == "mediainfo" for cmd in calls)


def test_read_video_resolution_returns_none_on_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    file_path = tmp_path / "video.mkv"
    file_path.write_bytes(b"")

    def fake_run(cmd, **kwargs):  # type: ignore[override]
        if cmd[0] == "ffprobe" and "json" in "".join(cmd).lower():
            return DummyCompletedProcess(0, stdout="{}")
        if cmd[0] == "ffprobe":
            return DummyCompletedProcess(0, stdout="garbage")
        raise FileNotFoundError

    monkeypatch.setattr(read_resolution_mod.subprocess, "run", fake_run)

    assert read_video_resolution(file_path) is None
