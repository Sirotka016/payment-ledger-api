import importlib.util
from pathlib import Path

from app.models import Base

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INITIAL_MIGRATION = (
    PROJECT_ROOT
    / "migrations"
    / "versions"
    / "20260603_0001_create_initial_tables.py"
)


def load_initial_migration():
    spec = importlib.util.spec_from_file_location(
        "initial_migration",
        INITIAL_MIGRATION,
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_initial_migration_exists():
    assert INITIAL_MIGRATION.exists()


def test_initial_migration_is_first_revision():
    migration = load_initial_migration()

    assert migration.revision == "0001"
    assert migration.down_revision is None


def test_initial_migration_contains_project_tables():
    text = INITIAL_MIGRATION.read_text(encoding="utf-8")

    for table_name in Base.metadata.tables:
        assert f'"{table_name}"' in text


def test_initial_migration_contains_default_data():
    migration = load_initial_migration()

    assert migration.DEFAULT_USER_EMAIL == "user@example.com"
    assert migration.DEFAULT_ADMIN_EMAIL == "admin@example.com"
    assert migration.DEFAULT_USER_PASSWORD_HASH.startswith("pbkdf2_sha256$")
    assert migration.DEFAULT_ADMIN_PASSWORD_HASH.startswith("pbkdf2_sha256$")


def test_initial_migration_updates_seeded_table_sequences():
    text = INITIAL_MIGRATION.read_text(encoding="utf-8")

    assert "pg_get_serial_sequence('users', 'id')" in text
    assert "pg_get_serial_sequence('admins', 'id')" in text
    assert "pg_get_serial_sequence('accounts', 'id')" in text
