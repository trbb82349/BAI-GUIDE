#!/usr/bin/env python3
"""Create a local BAI feed config file without printing secrets."""

from __future__ import annotations

import argparse
import getpass
from pathlib import Path


DEFAULT_BASE_URL = "https://bai.haiinu.com"


def write_config(path: Path, base_url: str, name: str, password: str, api_key: str) -> None:
    lines = [
        "# Local BAI feed settings. Do not commit this file.",
        f"BAI_FEED_BASE_URL={base_url}",
    ]
    if name:
        lines.append(f"BAI_FEED_NAME={name}")
    if password:
        lines.append(f"BAI_FEED_PASSWORD={password}")
    if api_key:
        lines.append(f"BAI_FEED_API_KEY={api_key}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create ~/.bai-feed.env for /goodbai.")
    parser.add_argument("--path", default=str(Path.home() / ".bai-feed.env"))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--name")
    auth = parser.add_mutually_exclusive_group()
    auth.add_argument("--api-key", action="store_const", dest="auth", const="api-key", help="Prompt for API key. This is the default.")
    auth.add_argument("--password", action="store_const", dest="auth", const="password", help="Prompt for password for the legacy login flow.")
    parser.set_defaults(auth="api-key")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing config file.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    path = Path(args.path).expanduser()
    if path.exists() and not args.force:
        print(f"Config already exists: {path}")
        print("Use --force to overwrite it.")
        return 1

    name = args.name or input("BAI feed name: ").strip()
    password = ""
    api_key = ""
    print("참고: API key/비밀번호는 PowerShell 화면에 보이지 않습니다. 붙여넣고 Enter를 누르면 입력됩니다.")
    if args.auth == "api-key":
        api_key = getpass.getpass("BAI feed API key (화면에 보이지 않습니다): ").strip()
    else:
        password = getpass.getpass("BAI feed password (화면에 보이지 않습니다): ").strip()

    write_config(path, args.base_url.strip(), name, password, api_key)
    print(f"Saved local config: {path}")
    print("Secret values were not printed. This file is ignored by the workspace git rules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
