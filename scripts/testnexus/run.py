"""Adapt the upstream application/tests to disposable TestNexus services.

Credentials are resolved by the worker and assembled only in process memory.
No .env file or secret-bearing command is written into the shared checkout.
Use only isolated test databases: upstream pytest fixtures remove application data.
"""
import argparse
import os
from pathlib import Path
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
PYTHON = '/workspace/venv/bin/python'


def environment():
    """Map per-run service addresses to upstream settings without exposing passwords."""
    env = os.environ.copy()
    host = env['TESTNEXUS_SERVICE_DATABASE_HOST']
    port = env['TESTNEXUS_SERVICE_DATABASE_PORT']
    user = quote(env.get('APP_DATABASE_USER', 'testnexus_fixture'), safe='')
    password = quote(env['TEST_DATABASE_PASSWORD'], safe='')
    database = quote(env.get('APP_DATABASE_NAME', 'testnexus_fixture'), safe='')
    env['DATABASE_URL'] = f'postgresql+psycopg://{user}:{password}@{host}:{port}/{database}'
    env['FASTAPI_ENV'] = 'development'
    base_url = env['TESTNEXUS_BASE_URL']
    env['FRONTEND_HOST'] = base_url
    env['PLAYWRIGHT_BASE_URL'] = base_url
    env['VITE_API_URL'] = base_url
    env['SMTP_HOST'] = env['TESTNEXUS_SERVICE_MAIL_HOST']
    env['SMTP_PORT'] = '1025'
    env['SMTP_TLS'] = 'false'
    env['SMTP_SSL'] = 'false'
    env['MAILPIT_HOST'] = env['TESTNEXUS_SERVICE_MAIL_URL']
    return env


def command(args, directory, env):
    """Run a foreground command and preserve its exit status for TestNexus."""
    return subprocess.run(args, cwd=ROOT / directory, env=env, check=False).returncode


def main():
    """Start the app or execute its backend/browser tests with fresh XML evidence."""
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['start', 'backend', 'system', 'browser'])
    mode = parser.parse_args().mode
    env = environment()
    if mode == 'start':
        result = command(['/workspace/venv/bin/alembic', 'upgrade', 'head'], 'backend', env)
        if result:
            return result
        result = command([PYTHON, '-m', 'app.initial_data'], 'backend', env)
        if result:
            return result
        os.chdir(ROOT / 'backend')
        os.execve(PYTHON, [PYTHON, '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000'], env)
    if mode == 'backend':
        result = command([PYTHON, '-m', 'coverage', 'run', '-m', 'pytest', 'tests', '--basetemp=/workspace/pytest-tmp', '--junitxml=test-results/backend.xml'], 'backend', env)
        coverage_result = command([PYTHON, '-m', 'coverage', 'xml', '-o', 'test-results/coverage.xml'], 'backend', env)
        return result or coverage_result
    # Backend fixture teardown deletes users. Restore the browser login account.
    result = command([PYTHON, '-m', 'app.initial_data'], 'backend', env)
    if result:
        return result
    if mode == 'system':
        return command([PYTHON, '-m', 'pytest', 'scripts/testnexus/test_system.py', '--basetemp=/workspace/system-tmp', '--junitxml=test-results/system.xml'], '.', env)
    env['PLAYWRIGHT_JUNIT_OUTPUT_NAME'] = 'test-results/browser.xml'
    return command(['bunx', '--no-install', 'playwright', 'test', '--project=chromium', '--workers=1', '--reporter=line,junit'], 'frontend', env)


if __name__ == '__main__':
    raise SystemExit(main())
