import pytest


@pytest.mark.run(order=200)
def test_set_license_bad(test_app, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    response = test_app.post(
        f"/api/set_license/?license=00000-00000-00000-00000-00000",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("result") == "success"
    assert data.get("details") is False

@pytest.mark.run(order=201)
def test_set_license_ok(test_app, test_license, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    response = test_app.post(
        f"/api/set_license/?license={test_license}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("result") == "success"
    assert data.get("details") is True

@pytest.mark.run(order=202)
def test_get_systeminfo(test_app, test_license, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    response = test_app.get("/api/systeminfo/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data.get("result") == "success"
    assert data.get("details").get("csp_version") is not None
    assert data.get("details").get("sdk_version") is not None
    assert data.get("details").get("pycades_version") is not None
    assert data.get("details").get("python_version") is not None
    assert data.get("details").get("platform_version") is not None
    assert test_license.replace("-", "").lower() in data.get("details").get("license_crypto_pro").lower()



    

   
