from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_video_renderer_uses_executable_demo_receipts() -> None:
    spec = importlib.util.spec_from_file_location(
        "render_demo_video", ROOT / "scripts" / "render-demo-video.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.EVIDENCE["status"] == "PASS"
    assert module.SECOND["artifact"]["sha256"] in str(module.EVIDENCE)
    flattened = "\n".join(
        str(line) for scene in module.SCENES for line in scene["body"]
    )
    assert str(module.SECOND["artifact"]["bytes"]) in flattened
    assert module.SECOND["artifact"]["sha256"][:8] in flattened
    assert "19 / 19 Python tests passed" in flattened
    assert "20 / 20 MATCHED" in str([scene["status"] for scene in module.SCENES])
    assert "Six portable Agent Skills" in flattened
    assert sum(scene["duration"] for scene in module.SCENES) < 180
