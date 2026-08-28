#!/usr/bin/env python3
"""Render the public sub-three-minute demo with local macOS speech and ffmpeg.

Development requirements: Pillow, ffmpeg, and the macOS `say` command.
Displayed receipt values are loaded from the executable demo sequence.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "demo" / "daily-ai-agent-toolkit-demo-v0.1.0.mp4"
CAPTIONS = ROOT / "demo" / "daily-ai-agent-toolkit-demo-v0.1.0.srt"
WIDTH, HEIGHT = 1920, 1080
BG = "#08111f"
PANEL = "#101d31"
TEXT = "#eef4ff"
MUTED = "#a9bad3"
BLUE = "#63a7ff"
GREEN = "#61d095"
RED = "#ff7185"
AMBER = "#f7c66b"
FONT = "/System/Library/Fonts/SFNSMono.ttf"


def _demo_evidence() -> dict[str, object]:
    completed = subprocess.run(
        ["python3", str(ROOT / "scripts" / "demo-sequence.py"), "--json"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    result = json.loads(completed.stdout)
    if result.get("status") != "PASS":
        raise RuntimeError("executable demo sequence did not pass")
    return result


EVIDENCE = _demo_evidence()
FIRST = EVIDENCE["first"]
BLOCKERS = EVIDENCE["blockers"]
SECOND = EVIDENCE["second"]
RECEIPT = EVIDENCE["receipt"]


SCENES = [
    {
        "duration": 18,
        "title": "Proof should travel with the work",
        "status": "DAILY AI AGENT TOOLKIT  ·  v0.1.0",
        "body": [
            "Two local MCP servers  ·  Eight deterministic tools",
            "Six portable Agent Skills  ·  No model or network calls",
            "",
            "Failure → explicit blocker → repair → retained receipt",
        ],
        "accent": BLUE,
        "narration": (
            "AI systems can say work is complete before the evidence is retained. "
            "I built the Daily AI Agent Toolkit to make that boundary explicit. "
            "It provides two local MCP servers, eight deterministic tools, and six portable Agent Skills."
        ),
    },
    {
        "duration": 28,
        "title": "1  Incomplete evidence is rejected",
        "status": "FAIL",
        "body": [
            '$ dailyai-evidence-gate --root "$WORKSPACE"',
            "verify_artifact: release-report.md",
            "",
            f'"bytes": {FIRST["artifact"]["bytes"]}',
            f'"code": "{FIRST["findings"][0]["code"]}"',
            f'"code": "{FIRST["findings"][1]["code"]}"',
            '"term": "Verification: PASS"',
        ],
        "accent": RED,
        "narration": (
            "Evidence Gate checks a file beneath an operator supplied root. "
            "This synthetic report exists, but it is empty and fails the declared required-text rule. "
            "The result is fail, with machine-readable findings. This is a bounded local receipt, not a semantic judgment."
        ),
    },
    {
        "duration": 24,
        "title": "2  Turn failure into an actionable blocker",
        "status": "BLOCKED",
        "body": [
            "format_blockers:",
            "",
            f'"requirement_id": "{BLOCKERS["findings"][0]["requirement_id"]}"',
            f'"state": "{BLOCKERS["findings"][0]["state"]}"',
            f'"reason": "{BLOCKERS["findings"][0]["reason"]}"',
            f'"repair": "{BLOCKERS["findings"][0]["repair"]}"',
        ],
        "accent": AMBER,
        "narration": (
            "Release Gate converts the failed finding into an explicit blocker. "
            "The requirement, observed state, reason, and repair remain visible. "
            "Missing or invalid evidence does not become an optimistic pass, and the next action is inspectable."
        ),
    },
    {
        "duration": 28,
        "title": "3  Repair, then rerun the identical rule",
        "status": "PASS",
        "body": [
            '$ printf "Verification: PASS\\nScope: local demo.\\n" > release-report.md',
            "$ rerun verify_artifact with the same required term",
            "",
            f'"bytes": {SECOND["artifact"]["bytes"]}',
            f'"status": "{SECOND["status"]}"',
            f'"sha256": "{SECOND["artifact"]["sha256"][:8]}…{SECOND["artifact"]["sha256"][-9:]}"',
            "",
            "File properties passed; factual truth was not assessed.",
        ],
        "accent": GREEN,
        "narration": (
            "I add the qualifying evidence and rerun the identical check. "
            "It now passes and records a byte count and SHA two fifty six digest for the retained artifact. "
            "That proves this file met this declared rule. It does not prove every statement in the report."
        ),
    },
    {
        "duration": 30,
        "title": "4  Retain the release receipt",
        "status": "PASS",
        "body": [
            "build_release_receipt:",
            "",
            f'"path": "{RECEIPT["artifacts"][0]["path"]}"',
            f'"status": "{RECEIPT["status"]}"',
            f'"bytes": {RECEIPT["artifacts"][0]["bytes"]}',
            f'"sha256": "{RECEIPT["artifacts"][0]["sha256"][:8]}…{RECEIPT["artifacts"][0]["sha256"][-9:]}"',
            "",
            '"A release receipt does not publish, deploy, or approve the release."',
        ],
        "accent": GREEN,
        "narration": (
            "Release Gate then hashes the repaired artifact into a retained release receipt. "
            "The check status, relative path, byte count, digest, and limitation travel together. "
            "The receipt does not publish, deploy, or approve anything. It gives a reviewer reproducible evidence for the next controlled decision."
        ),
    },
    {
        "duration": 26,
        "title": "5  Fixed examples prevent hand-picked proof",
        "status": "20 / 20 MATCHED",
        "body": [
            "$ python scripts/run-examples.py",
            "",
            "All 8 MCP tools exercised",
            "PASS  ·  FAIL  ·  BLOCKED  ·  UNVERIFIED",
            "19 / 19 Python tests passed",
            "6 / 6 Agent Skill self-tests passed",
        ],
        "accent": BLUE,
        "narration": (
            "A single demonstration can be hand picked, so the repository includes twenty declared-outcome examples across all eight tools. "
            "They cover pass, fail, blocked, and unverified states. The same catalog runs in the test suite, alongside nineteen Python tests and six deterministic skill self-tests."
        ),
    },
    {
        "duration": 25,
        "title": "Inspect the evidence. Keep the boundary.",
        "status": "APACHE-2.0  ·  LOCAL  ·  DETERMINISTIC",
        "body": [
            "github.com/Dailyaiagents/daily-ai-agent-toolkit",
            "",
            "dailyaiagents-evidence-gate  ·  PyPI",
            "dailyaiagents-release-gate   ·  PyPI",
            "io.github.dailyaiagents/evidence-gate  ·  MCP Registry",
            "io.github.dailyaiagents/release-gate   ·  MCP Registry",
            "",
            "A local PASS is not semantic truth or release authority.",
        ],
        "accent": BLUE,
        "narration": (
            "The Daily AI Agent Toolkit is open source, local, and deterministic. "
            "Its job is narrow: make evidence, blockers, uncertainty, and immutable artifact identity easier to inspect before release. "
            "A local pass is never represented as semantic truth, production proof, or publication authority."
        ),
    },
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size)


def _render_scene(scene: dict[str, object], index: int, target: Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    accent = str(scene["accent"])
    draw.rounded_rectangle((110, 100, WIDTH - 110, HEIGHT - 120), radius=34, fill=PANEL)
    draw.rectangle((110, 100, 128, HEIGHT - 120), fill=accent)
    draw.text((170, 155), str(scene["title"]), font=_font(54), fill=TEXT)
    status_font = _font(30)
    status_width = draw.textbbox((0, 0), str(scene["status"]), font=status_font)[2]
    status_right = min(WIDTH - 170, 240 + status_width)
    draw.rounded_rectangle((170, 255, status_right, 330), radius=18, fill=accent)
    draw.text((200, 272), str(scene["status"]), font=status_font, fill=BG)
    y = 390
    for line in scene["body"]:  # type: ignore[index]
        color = MUTED
        if '"status": "PASS"' in line or "20 / 20" in line:
            color = GREEN
        elif "FAIL" in line or "empty_artifact" in line or "required_term_missing" in line:
            color = RED
        elif "BLOCKED" in line:
            color = AMBER
        draw.text((190, y), str(line), font=_font(30), fill=color)
        y += 58
    progress_left = 110
    progress_right = WIDTH - 110
    progress = (index + 1) / len(SCENES)
    draw.rectangle((progress_left, HEIGHT - 92, progress_right, HEIGHT - 78), fill="#23334a")
    draw.rectangle((progress_left, HEIGHT - 92, progress_left + int((progress_right - progress_left) * progress), HEIGHT - 78), fill=accent)
    total_duration = sum(int(scene["duration"]) for scene in SCENES)
    draw.text((WIDTH - 320, 42), f"{sum(int(s['duration']) for s in SCENES[:index]):02d}s / {total_duration}s", font=_font(22), fill=MUTED)
    image.save(target)


def _run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> int:
    for binary in ("ffmpeg", "say"):
        if not shutil.which(binary):
            raise SystemExit(f"missing required command: {binary}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dailyai-demo-render-") as temporary:
        work = Path(temporary)
        concat_lines: list[str] = []
        for index, scene in enumerate(SCENES):
            png = work / f"scene-{index:02d}.png"
            aiff = work / f"scene-{index:02d}.aiff"
            segment = work / f"scene-{index:02d}.mp4"
            _render_scene(scene, index, png)
            _run(["say", "-v", "Samantha", "-r", "145", "-o", str(aiff), str(scene["narration"])])
            _run([
                "ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", str(png), "-i", str(aiff),
                "-vf", "format=yuv420p", "-af", "apad", "-t", str(scene["duration"]),
                "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "160k", str(segment),
            ])
            concat_lines.append(f"file '{segment}'")
        concat = work / "concat.txt"
        concat.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
        _run([
            "ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-i", str(CAPTIONS),
            "-map", "0:v", "-map", "0:a", "-map", "1:0", "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
            "-metadata:s:s:0", "language=eng", "-movflags", "+faststart", str(OUTPUT),
        ])
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
