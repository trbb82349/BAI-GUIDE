import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from scripts import bai_feed_save


def test_parse_env_file_masks_secrets(tmp_path):
    config_path = tmp_path / ".bai-feed.env"
    config_path.write_text(
        "BAI_FEED_BASE_URL=https://example.test\n"
        "BAI_FEED_NAME=학생\n"
        "BAI_FEED_PASSWORD=secret\n",
        encoding="utf-8",
    )

    config = bai_feed_save.parse_env_file(config_path)

    assert config["BAI_FEED_NAME"] == "학생"
    assert bai_feed_save.mask_config(config)["BAI_FEED_PASSWORD"] == "***"


def test_workspace_config_overrides_home_config(tmp_path, monkeypatch):
    home = tmp_path / "home"
    workspace = tmp_path / "workspace"
    home.mkdir()
    workspace.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    (home / ".bai-feed.env").write_text(
        "BAI_FEED_BASE_URL=https://bai.haiinu.com\nBAI_FEED_API_KEY=home-key\n",
        encoding="utf-8",
    )
    (workspace / ".bai-feed.env").write_text(
        "BAI_FEED_BASE_URL=http://127.0.0.1:5066\nBAI_FEED_API_KEY=workspace-key\n",
        encoding="utf-8",
    )

    config, used = bai_feed_save.load_config(workspace)

    assert [path.name for path in used] == [".bai-feed.env", ".bai-feed.env"]
    assert config["BAI_FEED_BASE_URL"] == "http://127.0.0.1:5066"
    assert config["BAI_FEED_API_KEY"] == "workspace-key"


def test_dry_run_payload_from_json(tmp_path, capsys):
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(
        json.dumps({"did": "작업", "learned": "배움", "blocked": "질문", "project_id": ""}, ensure_ascii=False),
        encoding="utf-8",
    )

    code = bai_feed_save.main(["--input-json", str(payload_path)])

    out = capsys.readouterr().out
    assert code == 0
    assert "Dry-run only" in out
    assert '"project_id": null' in out


def test_payload_requires_all_progress_fields(tmp_path, capsys):
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(
        json.dumps({"did": "작업", "learned": "배움", "blocked": ""}, ensure_ascii=False),
        encoding="utf-8",
    )

    code = bai_feed_save.main(["--input-json", str(payload_path)])

    err = capsys.readouterr().err
    assert code == 2
    assert "missing required progress fields: blocked" in err


def test_detect_cloudflare_1010():
    body = b"HTTP 403 / Cloudflare Error 1010\nbrowser_signature_banned"

    message = bai_feed_save.detect_cloudflare_error(body, 403)

    assert "Cloudflare Error 1010" in message
    assert "Do not retry repeatedly" in message


class FakeBaiHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        data = json.loads(body.decode("utf-8"))
        if self.path == "/api/login":
            if data.get("name") == "학생" and data.get("password") == "pw":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", "session=fake")
                self.end_headers()
                self.wfile.write(json.dumps({"id": 1, "name": "학생", "role": "student"}).encode("utf-8"))
            else:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "invalid credentials"}).encode("utf-8"))
            return
        if self.path == "/api/web/post":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"id": 7, "url": "/post/7"}).encode("utf-8"))
            return
        if self.path == "/api/post":
            if self.headers.get("X-API-Key") != "api-secret":
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "invalid api key"}).encode("utf-8"))
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"id": 8, "url": "/post/8"}).encode("utf-8"))
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def test_send_login_flow():
    server = HTTPServer(("127.0.0.1", 0), FakeBaiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        config = {
            "BAI_FEED_BASE_URL": f"http://127.0.0.1:{server.server_port}",
            "BAI_FEED_NAME": "학생",
            "BAI_FEED_PASSWORD": "pw",
        }
        payload = {"did": "작업", "learned": "", "blocked": "", "tags": "테스트", "links": "", "project_id": None}

        result = bai_feed_save.send_payload(config, payload, "login")

        assert result["id"] == 7
        assert result["absolute_url"].endswith("/post/7")
    finally:
        server.shutdown()


def test_auto_auth_prefers_api_key():
    server = HTTPServer(("127.0.0.1", 0), FakeBaiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        config = {
            "BAI_FEED_BASE_URL": f"http://127.0.0.1:{server.server_port}",
            "BAI_FEED_NAME": "학생",
            "BAI_FEED_PASSWORD": "pw",
            "BAI_FEED_API_KEY": "api-secret",
        }
        payload = {"did": "작업", "learned": "", "blocked": "", "tags": "테스트", "links": "", "project_id": None}

        result = bai_feed_save.send_payload(config, payload, "auto")

        assert result["id"] == 8
        assert result["absolute_url"].endswith("/post/8")
    finally:
        server.shutdown()
