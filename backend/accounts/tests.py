from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthenticationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "newuser", "password": "StrongTestPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username="newuser")

        # Verify password is hashed
        self.assertNotEqual(user.password, "StrongTestPassword123!")

        self.assertTrue(user.check_password("StrongTestPassword123!"))

    def test_login_with_valid_credentials(self):
        user = User.objects.create_user(
            username="testuser", password="StrongTestPassword123!"
        )

        response = self.client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "StrongTestPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        # Verify Django created a session
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_login_with_invalid_credentials(self):
        User.objects.create_user(username="testuser", password="StrongTestPassword123!")

        response = self.client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "WrongPassword"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_logout(self):
        user = User.objects.create_user(
            username="testuser", password="StrongTestPassword123!"
        )

        self.client.force_login(user)

        response = self.client.post("/api/auth/logout/")

        self.assertEqual(response.status_code, 200)

        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unauthenticated_logout(self):
        response = self.client.post("/api/auth/logout/")

        self.assertEqual(response.status_code, 403)


class CSRFSecurityTests(TestCase):

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def test_csrf_enpoint_sets_cookie(self):
        response = self.client.get("/api/auth/csrf/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)

    def test_login_without_csrf_is_rejected(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "testuser1", "password": "TestPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_login_with_valid_csrf(self):
        user = User.objects.create_user(
            username="testuser", password="StrongTestPassword123!"
        )

        self.client.get("/api/auth/csrf/")

        csrf_token = self.client.cookies["csrftoken"].value

        response = self.client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "StrongTestPassword123!"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))
