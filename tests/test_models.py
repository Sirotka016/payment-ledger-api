from decimal import Decimal

from sqlalchemy import Numeric

from app.models import Account, Admin, Base, Payment, User


def test_models_are_registered_in_metadata():
    assert set(Base.metadata.tables) == {"users", "admins", "accounts", "payments"}


def test_unique_fields_are_configured():
    assert User.__table__.columns["email"].unique is True
    assert Admin.__table__.columns["email"].unique is True
    assert Payment.__table__.columns["transaction_id"].unique is True


def test_money_columns_use_numeric_type():
    balance_type = Account.__table__.columns["balance"].type
    amount_type = Payment.__table__.columns["amount"].type

    assert isinstance(balance_type, Numeric)
    assert balance_type.precision == 12
    assert balance_type.scale == 2
    assert isinstance(amount_type, Numeric)
    assert amount_type.precision == 12
    assert amount_type.scale == 2


def test_account_default_balance_is_zero():
    assert Account.__table__.columns["balance"].default.arg == Decimal("0.00")
