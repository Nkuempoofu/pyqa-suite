"""API test cases against the JSONPlaceholder REST API.

Covers the four core HTTP methods plus response schema
and error-handling checks - no browser required.
"""
import allure
import pytest

from utils.api_client import ApiClient


@pytest.fixture(scope="module")
def api():
    return ApiClient()


@allure.feature("REST API")
@pytest.mark.api
class TestApi:

    @allure.story("Read")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_all_posts_returns_200_and_full_list(self, api):
        """GET /posts returns 200 with the complete list of 100 posts."""
        response = api.get("/posts")

        assert response.status_code == 200
        assert len(response.json()) == 100

    @allure.story("Read")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_get_single_post_has_expected_schema(self, api):
        """GET /posts/1 returns a post with all required fields."""
        response = api.get("/posts/1")

        assert response.status_code == 200
        post = response.json()
        for field in ("userId", "id", "title", "body"):
            assert field in post, f"Response is missing the '{field}' field"
        assert post["id"] == 1

    @allure.story("Error handling")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_nonexistent_post_returns_404(self, api):
        """GET on an ID that does not exist returns 404, not a server error."""
        response = api.get("/posts/99999")

        assert response.status_code == 404

    @allure.story("Create")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_create_post_returns_201_with_new_id(self, api):
        """POST /posts creates a resource and echoes it back with an ID."""
        payload = {"title": "QA test post", "body": "Created by PyQA Suite", "userId": 1}
        response = api.post("/posts", payload)

        assert response.status_code == 201
        created = response.json()
        assert created["title"] == payload["title"]
        assert "id" in created

    @allure.story("Update")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_update_post_returns_200_with_changes(self, api):
        """PUT /posts/1 updates the resource and returns the new values."""
        payload = {"id": 1, "title": "Updated by PyQA Suite", "body": "New body", "userId": 1}
        response = api.put("/posts/1", payload)

        assert response.status_code == 200
        assert response.json()["title"] == "Updated by PyQA Suite"

    @allure.story("Delete")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_delete_post_returns_200(self, api):
        """DELETE /posts/1 completes without error."""
        response = api.delete("/posts/1")

        assert response.status_code == 200

    @allure.story("Performance")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    def test_response_time_is_acceptable(self, api):
        """GET /posts responds within 3 seconds."""
        response = api.get("/posts")

        assert response.elapsed.total_seconds() < 3
