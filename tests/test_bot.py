"""Bot formatting/parsing helpers + /debt handler tests."""
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from bot.formatting import (
    current_month,
    format_amount,
    format_debtors,
    parse_pay_args,
)
from bot.handlers import cmd_debt


def test_format_amount():
    assert format_amount(400000) == "400 000"
    assert format_amount(950000) == "950 000"
    assert format_amount(0) == "0"


def test_current_month():
    assert current_month(date(2026, 3, 15)) == "2026-03"
    assert current_month(date(2026, 12, 1)) == "2026-12"


def test_format_debtors_empty():
    text = format_debtors("2026-10", [])
    assert "qarzdorlar yo'q" in text


def test_format_debtors_lists_debts_and_total():
    debtors = [
        {
            "student_id": 1,
            "name": "Aziz",
            "phone": "+998901111111",
            "group_name": "A-101",
            "monthly_amount": 400000,
            "paid_in_month": 150000,
            "debt": 250000,
        }
    ]
    text = format_debtors("2026-10", debtors)
    assert "Aziz" in text
    assert "250 000 so'm" in text
    assert "Jami qarz: <b>250 000 so'm</b>" in text


@pytest.mark.parametrize(
    "text, expected",
    [
        ("/pay 3 200000", (3, 200000)),
        ("/pay 42 1000", (42, 1000)),
        ("/pay", "parse_error"),
        ("/pay 3", "parse_error"),
        ("/pay 3 200000 5", "parse_error"),
        ("/pay abc 100", "not_int"),
        ("/pay 3 -5", "non_positive"),
        ("/pay 3 0", "non_positive"),
    ],
)
def test_parse_pay_args(text, expected):
    result = parse_pay_args(text)
    if expected == "parse_error":
        assert isinstance(result, str) and "/pay <student_id> <summa>" in result
    elif expected == "not_int":
        assert isinstance(result, str) and "butun son" in result
    elif expected == "non_positive":
        assert isinstance(result, str) and "musbat" in result
    else:
        assert result == expected


async def test_cmd_debt_replies_report(client, monkeypatch):
    """Handler returns the same data the API produces for the current month."""
    # create a student with no payments -> debtor
    resp = client.post(
        "/students",
        json={
            "name": "Aziz",
            "phone": "+998901111111",
            "group_name": "A-101",
            "monthly_amount": 400000,
        },
    )
    assert resp.status_code == 201

    # handler uses SessionLocal (real module DB); point it at the test session
    from app import db as db_module

    class FakeSession:
        def __init__(self, real):
            self._real = real

        def execute(self, *a, **kw):
            return self._real.execute(*a, **kw)

        def close(self):
            pass

    update = SimpleNamespace(
        effective_chat=SimpleNamespace(id=1),
        message=SimpleNamespace(reply_text=AsyncMock()),
    )
    with patch("bot.handlers.SessionLocal") as sl, patch(
        "bot.handlers.current_month", return_value="2026-10"
    ):
        # reuse the dependency-overridden session the TestClient uses
        from tests.conftest import app  # same app object

        dep = app.dependency_overrides[db_module.get_db]()
        session = next(dep)
        sl.return_value = FakeSession(session)

        await cmd_debt(update, context=None)

    text = update.message.reply_text.call_args.args[0]
    assert "Aziz" in text
    assert "400 000 so'm" in text
