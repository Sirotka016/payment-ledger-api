from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_installs_project_and_runs_app():
    text = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.11-slim" in text
    assert "pip install --no-cache-dir -e ." in text
    assert 'CMD ["python", "-m", "app.main"]' in text


def test_docker_compose_defines_app_and_db_services():
    text = (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "services:" in text
    assert "db:" in text
    assert "app:" in text
    assert "postgres:16-alpine" in text
    assert "DATABASE_URL:" in text
    assert "alembic upgrade head" in text


def test_dockerignore_excludes_local_files():
    text = (PROJECT_ROOT / ".dockerignore").read_text(encoding="utf-8")

    assert ".venv" in text
    assert ".env" in text
    assert "00_Project" in text
    assert "tests" in text
