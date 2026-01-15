import unittest
from app import create_app, db

class TestMechanics(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

        self.mechanic_payload = {
            "name": "Test Mechanic",
            "email": "test@shop.com",
            "password": "password123",
            "salary": 50000,
            "phone": "904-555-1234",
            "address": "123 Test St"
        }

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # -----------------------------
    # Helper
    # -----------------------------
    def create_mechanic_and_login(self):
        create_res = self.client.post(
            "/mechanics/",
            json=self.mechanic_payload
        )
        mechanic_id = create_res.get_json()["id"]

        login_res = self.client.post(
            "/mechanics/login",
            json={
                "email": self.mechanic_payload["email"],
                "password": self.mechanic_payload["password"]
            }
        )
        token = login_res.get_json()["token"]
        return token, mechanic_id

    # -----------------------------
    # Tests
    # -----------------------------
    def test_create_mechanic(self):
        res = self.client.post("/mechanics/", json=self.mechanic_payload)
        self.assertEqual(res.status_code, 201)

    def test_get_mechanics(self):
        self.client.post("/mechanics/", json=self.mechanic_payload)
        res = self.client.get("/mechanics/")
        self.assertEqual(res.status_code, 200)

    def test_login_mechanic(self):
        self.client.post("/mechanics/", json=self.mechanic_payload)
        res = self.client.post(
            "/mechanics/login",
            json={
                "email": self.mechanic_payload["email"],
                "password": self.mechanic_payload["password"]
            }
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.get_json())

    def test_update_mechanic(self):
        token, mechanic_id = self.create_mechanic_and_login()

        res = self.client.put(
            f"/mechanics/{mechanic_id}",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)

    def test_delete_mechanic(self):
        token, mechanic_id = self.create_mechanic_and_login()

        res = self.client.delete(
            f"/mechanics/{mechanic_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)
