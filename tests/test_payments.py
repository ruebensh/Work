"""Payments tests (Part 1.2): add payment, list by student."""


def test_create_payment(client, student):
    resp = client.post(
        "/payments",
        json={"student_id": student["id"], "amount": 200000, "paid_at": "2026-10-15"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body == {
        "id": body["id"],
        "student_id": student["id"],
        "amount": 200000,
        "paid_at": "2026-10-15",
    }


def test_create_payment_unknown_student(client):
    resp = client.post(
        "/payments", json={"student_id": 999, "amount": 50000, "paid_at": "2026-10-15"}
    )
    assert resp.status_code == 404


def test_payment_amount_must_be_positive(client, student):
    resp = client.post(
        "/payments", json={"student_id": student["id"], "amount": 0, "paid_at": "2026-10-15"}
    )
    assert resp.status_code == 422


def test_list_payments_by_student(client, student):
    other = client.post(
        "/students",
        json={
            "name": "Begzod",
            "phone": "+998999999999",
            "group_name": "C-303",
            "monthly_amount": 500000,
        },
    ).json()
    client.post("/payments", json={"student_id": student["id"], "amount": 100000, "paid_at": "2026-10-01"})
    client.post("/payments", json={"student_id": student["id"], "amount": 250000, "paid_at": "2026-10-20"})
    client.post("/payments", json={"student_id": other["id"], "amount": 90000, "paid_at": "2026-10-10"})

    resp = client.get("/payments", params={"student_id": student["id"]})
    assert resp.status_code == 200
    amounts = [p["amount"] for p in resp.json()]
    assert amounts == [250000, 100000]  # newest first
    assert all(p["student_id"] == student["id"] for p in resp.json())


def test_list_payments_requires_student_id(client):
    assert client.get("/payments").status_code == 422


def test_list_payments_unknown_student(client):
    assert client.get("/payments", params={"student_id": 999}).status_code == 404
