#!/usr/bin/env python3
"""Post a BAI progress update from Codex.

Default behavior is dry-run. Use --send only after the user confirms.
Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://bai.haiinu.com"
DEFAULT_USER_AGENT = "BAI-Goodbai-Codex/1.0 (+https://bai.haiinu.com)"
CONFIG_FILENAMES = (".bai-feed.env",)
REQUIRED_FIELDS = ("did", "learned", "blocked")


class BaiFeedError(Exception):
    """User-facing error for BAI feed save failures."""


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def config_paths(workspace: Path) -> list[Path]:
    paths: list[Path] = []
    paths.extend(Path.home() / name for name in CONFIG_FILENAMES)
    paths.extend(workspace / name for name in CONFIG_FILENAMES)
    override = os.environ.get("BAI_FEED_CONFIG")
    if override:
        paths.append(Path(override).expanduser())
    return paths


def load_config(workspace: Path) -> tuple[dict[str, str], list[Path]]:
    config: dict[str, str] = {}
    used: list[Path] = []
    for path in config_paths(workspace):
        if path.exists():
            config.update(parse_env_file(path))
            used.append(path)
    for key, value in os.environ.items():
        if key.startswith("BAI_FEED_"):
            config[key] = value
    config.setdefault("BAI_FEED_BASE_URL", DEFAULT_BASE_URL)
    return config, used


def mask_config(config: dict[str, str]) -> dict[str, str]:
    masked: dict[str, str] = {}
    for key, value in sorted(config.items()):
        if key in {"BAI_FEED_PASSWORD", "BAI_FEED_API_KEY"} and value:
            masked[key] = "***"
        elif key.startswith("BAI_FEED_"):
            masked[key] = value or "(empty)"
    return masked


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if args.input_json:
        path = Path(args.input_json)
        try:
            payload.update(json.loads(path.read_text(encoding="utf-8-sig")))
        except FileNotFoundError as exc:
            raise BaiFeedError(f"input json not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise BaiFeedError(f"input json is invalid: {path}: {exc}") from exc

    for key in ("did", "learned", "blocked", "tags", "links"):
        value = getattr(args, key)
        if value is not None:
            payload[key] = value
    if args.project_id is not None:
        payload["project_id"] = args.project_id

    normalized = {
        "did": str(payload.get("did") or "").strip(),
        "learned": str(payload.get("learned") or "").strip(),
        "blocked": str(payload.get("blocked") or "").strip(),
        "tags": str(payload.get("tags") or "").strip(),
        "links": str(payload.get("links") or "").strip(),
        "project_id": normalize_project_id(payload.get("project_id")),
    }
    missing = [field for field in REQUIRED_FIELDS if not normalized[field]]
    if missing:
        raise BaiFeedError("missing required progress fields: " + ", ".join(missing))
    return normalized


def normalize_project_id(value: Any) -> int | None:
    if value in (None, "", "null", "None", "none", "연결 안 함"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise BaiFeedError(f"invalid project_id: {value}") from exc


def require_config(config: dict[str, str], auth_mode: str) -> str:
    if not config.get("BAI_FEED_BASE_URL"):
        raise BaiFeedError("missing BAI_FEED_BASE_URL")

    has_login = bool(config.get("BAI_FEED_NAME") and config.get("BAI_FEED_PASSWORD"))
    has_key = bool(config.get("BAI_FEED_API_KEY"))

    if auth_mode == "login" and not has_login:
        raise BaiFeedError("missing BAI_FEED_NAME or BAI_FEED_PASSWORD")
    if auth_mode == "api-key" and not has_key:
        raise BaiFeedError("missing BAI_FEED_API_KEY")
    if auth_mode == "auto":
        if has_key:
            return "api-key"
        if has_login:
            return "login"
        raise BaiFeedError("missing login credentials or BAI_FEED_API_KEY")
    return auth_mode


def absolute_url(base_url: str, path: str) -> str:
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def post_json(
    opener: urllib.request.OpenerDirector,
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
    user_agent: str = DEFAULT_USER_AGENT,
) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "User-Agent": user_agent,
            **(headers or {}),
        },
    )
    try:
        with opener.open(request, timeout=20) as response:
            return parse_response(response.read(), response.status, url)
    except urllib.error.HTTPError as exc:
        data = exc.read()
        cloudflare_error = detect_cloudflare_error(data, exc.code)
        if cloudflare_error:
            raise BaiFeedError(cloudflare_error) from exc
        parsed = parse_response(data, exc.code, url, allow_error=True)
        detail = parsed.get("error") or parsed.get("message") or parsed
        raise BaiFeedError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise BaiFeedError(f"request failed for {url}: {exc.reason}") from exc


def parse_response(data: bytes, status: int, url: str, allow_error: bool = False) -> dict[str, Any]:
    text = data.decode("utf-8", errors="replace")
    try:
        parsed = json.loads(text) if text else {}
    except json.JSONDecodeError as exc:
        raise BaiFeedError(f"non-json response from {url} (HTTP {status}): {text[:200]}") from exc
    if not allow_error and status >= 400:
        raise BaiFeedError(f"HTTP {status} from {url}: {parsed}")
    if not isinstance(parsed, dict):
        raise BaiFeedError(f"unexpected response from {url}: {parsed}")
    return parsed


def detect_cloudflare_error(data: bytes, status: int) -> str | None:
    text = data.decode("utf-8", errors="replace")
    lower = text.lower()
    if status == 403 and ("cloudflare" in lower or "error 1010" in lower or "browser_signature_banned" in lower):
        details = []
        if "error 1010" in lower:
            details.append("Cloudflare Error 1010")
        if "browser_signature_banned" in lower:
            details.append("browser_signature_banned")
        summary = " / ".join(details) or "Cloudflare 403"
        return (
            f"{summary}: BAI site security blocked this Python API request before it reached Flask. "
            "Do not retry repeatedly. Ask the site owner to allow the automation endpoint "
            "or use an approved API-key path/User-Agent."
        )
    return None


def send_payload(config: dict[str, str], payload: dict[str, Any], auth_mode: str) -> dict[str, Any]:
    selected_auth = require_config(config, auth_mode)
    base_url = config["BAI_FEED_BASE_URL"].rstrip("/")
    user_agent = config.get("BAI_FEED_USER_AGENT") or DEFAULT_USER_AGENT
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    if selected_auth == "login":
        login_url = absolute_url(base_url, "/api/login")
        post_url = absolute_url(base_url, "/api/web/post")
        post_json(
            opener,
            login_url,
            {
                "name": config["BAI_FEED_NAME"],
                "password": config["BAI_FEED_PASSWORD"],
            },
            user_agent=user_agent,
        )
        result = post_json(opener, post_url, payload, user_agent=user_agent)
    else:
        post_url = absolute_url(base_url, "/api/post")
        result = post_json(
            opener,
            post_url,
            payload,
            {"X-API-Key": config["BAI_FEED_API_KEY"]},
            user_agent=user_agent,
        )

    if "url" in result:
        result["absolute_url"] = absolute_url(base_url, str(result["url"]))
    return result


def print_json(label: str, data: dict[str, Any]) -> None:
    print(label)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Save a Codex progress update to the BAI feed.")
    parser.add_argument("--input-json", help="Path to a JSON payload file.")
    parser.add_argument("--did", help="한 일/결과")
    parser.add_argument("--learned", help="배운 것")
    parser.add_argument("--blocked", help="막힌 점/질문")
    parser.add_argument("--tags", help="Codex가 수집한 태그")
    parser.add_argument("--links", help="Codex가 수집한 산출물 링크")
    parser.add_argument("--project-id", help="Codex가 선택한 BAI project_id. Omit for no project.")
    parser.add_argument("--auth", choices=("login", "api-key", "auto"), default="auto")
    parser.add_argument("--workspace", default=".", help="Workspace root for local config lookup.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print payload without posting. This is the default.")
    parser.add_argument("--send", action="store_true", help="Actually post to BAI. Omit for dry-run.")
    parser.add_argument("--show-config", action="store_true", help="Print masked config summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workspace = Path(args.workspace).resolve()
    try:
        config, used_paths = load_config(workspace)
        payload = load_payload(args)
        if args.show_config:
            print_json("Config:", mask_config(config))
            if used_paths:
                print("Config files:")
                for path in used_paths:
                    print(f"- {path}")
        print_json("Payload:", payload)

        if not args.send:
            print("Dry-run only. Add --send after user confirmation to post to BAI.")
            return 0

        result = send_payload(config, payload, args.auth)
        print_json("Posted:", result)
        return 0
    except BaiFeedError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
