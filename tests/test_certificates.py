import pytest


@pytest.mark.run(order=400)
def test_post_certificate_ok(test_app, path_to_cert_file, test_api_key):
    """
    Импорт сертификата в хранилище.
    Входные данные:
    - store: My
    - file: test.cer
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    with open(path_to_cert_file, 'rb') as f:
        response = test_app.post(
            "/api/certificates/",
            params={"store": "My"},
            files={"file": ("test.cer", f)},
            headers=headers
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "success"
    assert "details" in data
    assert data["details"] == True


@pytest.mark.run(order=401)
def test_get_certificates_ok(test_app, test_api_key):
    """
    Получение списка сертификатов.
    Входные данные:
    - store: All
    - offset: 0 
    - limit: 100
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    response = test_app.get(
        "/api/certificates/",
        params={
            "store": "All",
            "offset": 0,
            "limit": 100
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "success"
    assert "details" in data
    assert "data" in data["details"]
    assert "count" in data["details"]
    assert "offset" in data["details"]
    assert data["details"]["count"] > 0


@pytest.mark.run(order=402)
def test_get_certificate_by_thumbprint_ok(test_app, thumbprint, test_api_key):
    """
    Получение сертификата по отпечатку.
    Входные данные:
    - thumbprint
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    response = test_app.get(
        f"/api/certificates/{thumbprint}/",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "success"
    assert "details" in data
    assert data["details"]["thumbprint"] == thumbprint
    assert data["details"]["has_private_key"] == True
    # print(data["details"])
