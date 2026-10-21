"""Students CRUD tests (Part 1.1)."""


def _payload(**over):
    base = {
        "name": "Malika Yusupova",
        "phone": "+998930001122",
        "group_name": "B-202",
        "monthly_amount": 350000,
    }
    base.update(over)
    return base


def test_create_student(client):
    resp = client.post("/students", json=_payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["name"] == "Malika Yusupova"
    assert body["monthly_amount"] == 350000


def test_phone_normalized_to_digits(client):
    resp = client.post("/students", json=_payload(phone="+998 (93) 000-11-22"))
    assert resp.status_code == 201
    assert resp.json()["phone"] == "+998930001122"


def test_duplicate_phone_rejected(client):
    assert client.post("/students", json=_payload()).status_code == 201
    resp = client.post("/students", json=_payload(name="Boshqa"))
    assert resp.status_code == 409


def test_invalid_payload_rejected(client):
    assert client.post("/students", json=_payload(monthly_amount=0)).status_code == 422
    assert client.post("/students", json=_payload(name="  ")).status_code == 422
    assert client.post("/students", json=_payload(phone="123")).status_code == 422


def test_list_students(client, student):
    client.post("/students", json=_payload())
    resp = client.get("/students")
    assert resp.status_code == 200
    assert {s["id"] for s in resp.json()} >= {student["id"]}


def test_get_student(client, student):
    resp = client.get(f"/students/{student['id']}")
    assert resp.status_code == 200
    assert resp.json()["phone"] == student["phone"]


def test_get_student_404(client):
    assert client.get("/students/999").status_code == 404


def test_update_student(client, student):
    resp = client.patch(f"/students/{student['id']}", json={"group_name": "A-102"})
    assert resp.status_code == 200
    assert resp.json()["group_name"] == "A-102"
    # untouched fields stay
    assert resp.json()["phone"] == student["phone"]


def test_update_404_and_conflict(client, student):
    assert client.patch("/students/999", json={"name": "X"}).status_code == 404
    client.post("/students", json=_payload())  # second student
    resp = client.patch(f"/students/{student['id']}", json={"phone": "+998930001122"})
    assert resp.status_code == 409


def test_delete_student(client, student):
    resp = client.delete(f"/students/{student['id']}")
    assert resp.status_code == 204
    assert client.get(f"/students/{student['id']}").status_code == 404


def test_delete_student_cascades_payments(client, student):
    client.post(
        "/payments",
        json={"student_id": student["id"], "amount": 100000, "paid_at": "2026-10-05"},
    )
    assert client.delete(f"/students/{student['id']}").status_code == 204
    assert client.get("/payments", params={"student_id": student["id"]}).status_code == 404
