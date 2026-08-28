from __future__ import annotations

import importlib.util
from pathlib import Path
import urllib.error

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "pypi_publish_preflight", ROOT / "scripts" / "pypi-publish-preflight.py"
)
assert SPEC and SPEC.loader
PREFLIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREFLIGHT)


def payload(name: str, version: str, expected: dict[str, tuple[str, int]]) -> dict:
    rows = []
    for index, (filename, (sha256, size)) in enumerate(expected.items()):
        rows.append(
            {
                "filename": filename,
                "digests": {"sha256": sha256},
                "size": size,
                "packagetype": "bdist_wheel" if index == 0 else "sdist",
                "url": f"https://files.pythonhosted.org/{filename}",
            }
        )
    return {
        "info": {"version": version, "description": f"<!-- mcp-name: {name} -->"},
        "urls": rows,
    }


def test_exact_public_release_is_accepted() -> None:
    expected = {"package.whl": ("a" * 64, 10), "package.tar.gz": ("b" * 64, 20)}
    rows = PREFLIGHT.validate_payload(
        payload("io.github.Dailyaiagents/example", "0.1.1", expected),
        version="0.1.1",
        mcp_name="io.github.Dailyaiagents/example",
        expected=expected,
    )
    assert len(rows) == 2


@pytest.mark.parametrize(
    "field",
    [
        "marker",
        "marker_suffix",
        "digest",
        "size",
        "filenames",
        "url",
        "url_port",
        "yanked",
    ],
)
def test_conflicting_public_release_fails_closed(field: str) -> None:
    expected = {"package.whl": ("a" * 64, 10), "package.tar.gz": ("b" * 64, 20)}
    document = payload("io.github.Dailyaiagents/example", "0.1.1", expected)
    if field == "marker":
        document["info"]["description"] = "mcp-name: io.github.dailyaiagents/example"
    elif field == "marker_suffix":
        document["info"]["description"] = (
            "<!-- mcp-name: io.github.Dailyaiagents/example-pro -->"
        )
    elif field == "digest":
        document["urls"][0]["digests"]["sha256"] = "c" * 64
    elif field == "size":
        document["urls"][0]["size"] = 11
    elif field == "url":
        document["urls"][0]["url"] = "https://example.com/package.whl"
    elif field == "url_port":
        document["urls"][0]["url"] = (
            "https://files.pythonhosted.org:444/package.whl"
        )
    elif field == "yanked":
        document["urls"][0]["yanked"] = True
    else:
        document["urls"][0]["filename"] = "other.whl"
    with pytest.raises(ValueError):
        PREFLIGHT.validate_payload(
            document,
            version="0.1.1",
            mcp_name="io.github.Dailyaiagents/example",
            expected=expected,
        )


@pytest.mark.parametrize(
    ("url", "hostname"),
    [
        ("https://files.pythonhosted.org:444/package.whl", "files.pythonhosted.org"),
        ("https://example.com/package.whl", "files.pythonhosted.org"),
        ("http://pypi.org/project/json", "pypi.org"),
        ("https://user@pypi.org/project/json", "pypi.org"),
    ],
)
def test_final_response_url_must_remain_on_approved_endpoint(
    url: str, hostname: str
) -> None:
    with pytest.raises(ValueError):
        PREFLIGHT.validate_https_url(url, hostname, label="redirected response")


def test_absent_classification_revalidates_http_error_final_url() -> None:
    approved = urllib.error.HTTPError(
        "https://pypi.org/pypi/example/0.1.1/json", 404, "missing", {}, None
    )
    assert PREFLIGHT.is_absent_http_error(approved) is True

    redirected = urllib.error.HTTPError(
        "https://example.com/missing", 404, "missing", {}, None
    )
    with pytest.raises(ValueError):
        PREFLIGHT.is_absent_http_error(redirected)
