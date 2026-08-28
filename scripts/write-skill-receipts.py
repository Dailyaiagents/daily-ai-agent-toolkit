from __future__ import annotations
import hashlib, json
from datetime import date
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for skill in sorted((root / "skills").iterdir()):
    if not skill.is_dir():
        continue
    files = {}
    for path in sorted(skill.rglob("*")):
        if path.is_file() and path.name != "verification.json":
            files[str(path.relative_to(skill))] = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = {
        "schema_version": "dailyai.agent-skill-verification/v1",
        "name": skill.name,
        "version": "0.1.0",
        "license": "Apache-2.0",
        "verified_at": date.today().isoformat(),
        "source": "https://github.com/Dailyaiagents/daily-ai-agent-toolkit",
        "supported_clients": ["clients supporting the portable Agent Skills directory format"],
        "limitations": ["Client installation paths and optional fields vary; inspect current client documentation."],
        "files": files,
    }
    (skill / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
