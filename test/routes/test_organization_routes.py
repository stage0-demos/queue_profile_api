"""
Unit tests for Organization routes.

These tests validate the Flask route layer for the Organization domain, using the
generated blueprint factory and mocking out the underlying service and
token/breadcrumb helpers from api_utils.
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.organization_routes import create_organization_routes


class TestOrganizationRoutes(unittest.TestCase):
    """Test cases for Organization routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_organization_routes(),
            url_prefix="/api/organization",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.organization_routes.create_flask_token")
    @patch("src.routes.organization_routes.create_flask_breadcrumb")
    @patch("src.routes.organization_routes.OrganizationService.create_organization")
    @patch("src.routes.organization_routes.OrganizationService.get_organization")
    def test_create_organization_success(
        self,
        mock_get_organization,
        mock_create_organization,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/organization for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_organization.return_value = "123"
        mock_get_organization.return_value = {
            "_id": "123",
            "name": "test-organization",
            "status": "active",
        }

        response = self.client.post(
            "/api/organization",
            json={"name": "test-organization", "status": "active"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_create_organization.assert_called_once()
        mock_get_organization.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.organization_routes.create_flask_token")
    @patch("src.routes.organization_routes.create_flask_breadcrumb")
    @patch("src.routes.organization_routes.OrganizationService.get_organizations")
    def test_get_organizations_no_filter(
        self,
        mock_get_organizations,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/organization without name filter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_organizations.return_value = {
            "items": [
                {"_id": "123", "name": "organization1"},
                {"_id": "456", "name": "organization2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/organization")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_organizations.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.organization_routes.create_flask_token")
    @patch("src.routes.organization_routes.create_flask_breadcrumb")
    @patch("src.routes.organization_routes.OrganizationService.get_organizations")
    def test_get_organizations_with_name_filter(
        self,
        mock_get_organizations,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/organization with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_organizations.return_value = {
            "items": [{"_id": "123", "name": "test-organization"}],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/organization?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        mock_get_organizations.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name="test",
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.organization_routes.create_flask_token")
    @patch("src.routes.organization_routes.create_flask_breadcrumb")
    @patch("src.routes.organization_routes.OrganizationService.get_organization")
    def test_get_organization_success(
        self,
        mock_get_organization,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/organization/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_organization.return_value = {
            "_id": "123",
            "name": "organization1",
        }

        response = self.client.get("/api/organization/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_organization.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.organization_routes.create_flask_token")
    @patch("src.routes.organization_routes.create_flask_breadcrumb")
    @patch("src.routes.organization_routes.OrganizationService.get_organization")
    def test_get_organization_not_found(
        self,
        mock_get_organization,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/organization/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_organization.side_effect = HTTPNotFound(
            "Organization 999 not found"
        )

        response = self.client.get("/api/organization/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Organization 999 not found")

    @patch("src.routes.organization_routes.create_flask_token")
    def test_create_organization_unauthorized(self, mock_create_token):
        """Test POST /api/organization when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.post(
            "/api/organization",
            json={"name": "test"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
