"""Debtors report tests (Part 1.3): GET /debtors?month=YYYY-MM."""


def _create(client, name, phone, monthly):
    resp = client.post(
        "/students",
        json={"name": name, "phone": phone, "group_name": "G-1", "monthly_amount": monthly},
    )
    assert resp.status_code == 201
    return resp.json()


def _pay(client, student_id, amount, paid_at):
    assert client.post(
        "/payments", json={"student_id": student_id, "amount": amount, "paid_at": paid_at}
    ).status_code == 201


def test_no_payments_full_debt(client):
    s = _create(client, "Aziz", "+998901111111", 400000)
    resp = client.get("/debtors", params={"month": "2026-10"})
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "student_id": s["id"],
            "name": "Aziz",
            "phone": "+998901111111",
            "group_name": "G-1",
            "monthly_amount": 400000,
            "paid_in_month": 0,
            "debt": 400000,
        }
    ]


def test_partial_payment_shows_remaining_debt(client):
    s = _create(client, "Aziz", "+998901111111", 400000)
    _pay(client, s["id"], 150000, "2026-10-10")
    row = client.get("/debtors", params={"month": "2026-10"}).json()[0]
    assert row["paid_in_month"] == 150000
    assert row["debt"] == 250000


def test_fully_paid_excluded(client):
    s = _create(client, "Aziz", "+998901111111", 400000)
    _pay(client, s["id"], 200000, "2026-10-01")
    _pay(client, s["id"], 200000, "2026-10-31")
    assert client.get("/debtors", params={"month": "2026-10"}).json() == []


def test_overpaid_excluded(client):
    s = _create(client, "Aziz", "+998901111111", 400000)
    _pay(client, s["id"], 500000, "2026-10-05")
    assert client.get("/debtors", params={"month": "2026-10"}).json() == []


def test_only_selected_month_counts(client):
    s = _create(client, "Aziz", "+998901111111", 400000)
    _pay(client, s["id"], 400000, "2026-09-30")  # previous month, last day
    _pay(client, s["id"], 100000, "2026-11-01")  # next month, first day
    rows = client.get("/debtors", params={"month": "2026-10"}).json()
    assert rows[0]["paid_in_month"] == 0
    assert rows[0]["debt"] == 400000


def test_month_boundaries_inclusive(client):
    s = _create(client, "Aziz", "+998901111111", 400000)
    # 2026-02 has 28 days: first + last day of the month must both be inside
    _pay(client, s["id"], 200000, "2026-02-01")
    _pay(client, s["id"], 200000, "2026-02-28")
    assert client.get("/debtors", params={"month": "2026-02"}).json() == []
    # March has no payments — the full amount is debt again
    row = client.get("/debtors", params={"month": "2026-03"}).json()[0]
    assert row["debt"] == 400000


def test_invalid_month_format(client):
    assert client.get("/debtors", params={"month": "10-2026"}).status_code == 422
    assert client.get("/debtors", params={"month": "2026-13"}).status_code == 400
    assert client.get("/debtors").status_code == 422
