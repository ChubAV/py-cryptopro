import pytest


@pytest.mark.run(order=300)
def test_create_hash_text(test_app, test_strings_data, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for string_data in test_strings_data:
        response = test_app.post(
            "/api/hash/txt/",
            headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
            data={"text": string_data.get("value"), "algorithm": "101"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("result") == "success"
        assert "hash" in data.get("details")
        assert data.get("details").get("hash") == string_data.get("hash")


@pytest.mark.run(order=301)
def test_create_hash_file(test_app, test_files_data, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for file_data in test_files_data:
        with open(file_data.get("value"), "rb") as f:
            response = test_app.post(
                "/api/hash/file/",
                files={"file": ("test.pdf", f)},
                params={"algorithm": "101"},
                headers=headers
            )
        assert response.status_code == 200
        data = response.json()
        assert data.get("result") == "success" 
        assert "hash" in data.get("details")
        assert data.get("details").get("hash") == file_data.get("hash")
