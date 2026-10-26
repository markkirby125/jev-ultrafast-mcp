"""The Cloudflare backup asks wrangler for its token, and names the right key on a 401.

No network: subprocess.run is replaced.
"""
import subprocess

import pytest

from jev_ultrafast_mcp import policy


class _Done:
    def __init__(self, stdout):
        self.stdout = stdout


def test_token_comes_from_wrangler_without_the_env_override(monkeypatch):
    seen = {}

    def fake_run(argv, env, **kwargs):
        seen.update(argv=argv, env=env)
        return _Done('{"type": "oauth", "token": "fresh"}')

    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "stale")
    monkeypatch.setattr(policy.subprocess, "run", fake_run)
    assert policy._cloudflare_token("stale") == "fresh"
    assert seen["argv"] == ["wrangler", "auth", "token", "--json"]
    assert "CLOUDFLARE_API_TOKEN" not in seen["env"]


@pytest.mark.parametrize("error", [OSError("no wrangler"), subprocess.CalledProcessError(1, "w")])
def test_token_falls_back_to_the_env_key_when_wrangler_fails(monkeypatch, error):
    def boom(*args, **kwargs):
        raise error

    monkeypatch.setattr(policy.subprocess, "run", boom)
    assert policy._cloudflare_token("env-key") == "env-key"


def test_token_falls_back_when_wrangler_prints_no_token(monkeypatch):
    monkeypatch.setattr(policy.subprocess, "run", lambda *a, **k: _Done('{"type": "oauth"}'))
    assert policy._cloudflare_token("env-key") == "env-key"


def test_backup_401_names_cloudflare_not_the_typesafe_key():
    assert "TYPESAFE_API_KEY" in policy._http_reason(401)
    assert "Cloudflare backup rejected" in policy._http_reason(401, backup=True)
    assert "TYPESAFE_API_KEY" not in policy._http_reason(401, backup=True)
