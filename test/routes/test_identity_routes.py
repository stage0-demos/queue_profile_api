"""
Unit tests for Identity routes (consume-style, read-only).
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.identity_routes import create_identity_routes


class TestIdentityRoutes(unittest.TestCase):
    """Test cases for Identity routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_identity_routes(),
            url_prefix="/api/identity",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["developer"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.identity_routes.create_flask_token")
    @patch("src.routes.identity_routes.create_flask_breadcrumb")
    @patch("src.routes.identity_routes.IdentityService.get_identitys")
    def test_get_identitys_success(
        self,
        mock_get_identitys,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/identity for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_identitys.return_value = {
            "items": [
                {"_id": "123", "name": "identity1"},
                {"_id": "456", "name": "identity2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/identity")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_identitys.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.identity_routes.create_flask_token")
    @patch("src.routes.identity_routes.create_flask_breadcrumb")
    @patch("src.routes.identity_routes.IdentityService.get_identitys")
    def test_get_identitys_with_name_filter(
        self,
        mock_get_identitys,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/identity with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_identitys.return_value = {
            "items": [{"_id": "123", "name": "test-identity"}],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/identity?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        mock_get_identitys.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name="test",
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.identity_routes.create_flask_token")
    @patch("src.routes.identity_routes.create_flask_breadcrumb")
    @patch("src.routes.identity_routes.IdentityService.get_identity")
    def test_get_identity_success(
        self,
        mock_get_identity,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/identity/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_identity.return_value = {
            "_id": "123",
            "name": "identity1",
        }

        response = self.client.get("/api/identity/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_identity.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.identity_routes.create_flask_token")
    @patch("src.routes.identity_routes.create_flask_breadcrumb")
    @patch("src.routes.identity_routes.IdentityService.get_identity")
    def test_get_identity_not_found(
        self,
        mock_get_identity,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/identity/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_identity.side_effect = HTTPNotFound(
            "Identity 999 not found"
        )

        response = self.client.get("/api/identity/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Identity 999 not found")

    @patch("src.routes.identity_routes.create_flask_token")
    def test_get_identitys_unauthorized(self, mock_create_token):
        """Test GET /api/identity when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.get("/api/identity")

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
