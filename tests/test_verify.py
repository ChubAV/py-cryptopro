import pytest

@pytest.mark.run(order=600)
def test_verify_f2f_ok(test_app, test_files_data, thumbprint, test_api_key):
    """
    Проверка отсоединенной подписи у файла.
    Входные данные: 
    - Данные в виде файла
    - Подпись в виде файла
    Подпись корректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for file_data in test_files_data:
        with open(file_data['value'], "rb") as f, \
             open(file_data['sign_deattach']['file'], "rb") as s:
            
            response = test_app.post(
                "/api/verify/f2f/",
                files={
                    "file": ("test.pdf", f),
                    "sign": ("test.pdf.sig", s)
                },
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["result"] == "success"
            assert "details" in data
            assert "singer" in data["details"] 
            assert "thumbprint" in data["details"]["singer"]
            assert data["details"]["singer"]["thumbprint"] == thumbprint

@pytest.mark.run(order=601)
def test_verify_f2f_invalid_other_file(test_app, test_files_data, test_api_key):
    """
    Проверка отсоединенной подписи у файла.
    Входные данные: 
    - Данные в виде файла
    - Подпись в виде файла
    Подпись некорректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    assert len(test_files_data) >= 2
    with open(test_files_data[0]['value'], "rb") as f, \
         open(test_files_data[-1]['sign_deattach']['file'], "rb") as s:
        
        response = test_app.post(
            "/api/verify/f2f/",
            files={
                "file": ("test.pdf", f),
                "sign": ("test.pdf.sig", s)
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "error"
        assert "details" in data
        assert "code" in data["details"]
        assert data["details"]["code"] == "0x80091007"

@pytest.mark.run(order=602)
def test_verify_f2s_ok(test_app, test_files_data, thumbprint, test_api_key):
    """
    Проверка отсоединенной подписи у файла.
    Входные данные: 
    - Данные в виде файла
    - Подпись в виде строки
    Подпись корректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for file_data in test_files_data:
        with open(file_data['value'], "rb") as f:
            response = test_app.post(
                "/api/verify/f2s/",
                files={
                "file": ("test.pdf", f)
            },
            data={
                "sign": file_data['sign_deattach']['string']
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "details" in data
        assert "singer" in data["details"] 
        assert "thumbprint" in data["details"]["singer"]
        assert data["details"]["singer"]["thumbprint"] == thumbprint

@pytest.mark.run(order=603)
def test_verify_f2s_invalid(test_app, test_files_data, test_api_key):
    """
    Проверка отсоединенной подписи у файла.
    Входные данные: 
    - Данные в виде файла
    - Подпись в виде строки
    Подпись некорректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    assert len(test_files_data) >= 2
    with open(test_files_data[0]['value'], "rb") as f:
        response = test_app.post(
            "/api/verify/f2s/",
            files={
                "file": ("test.pdf", f)
            },
            data={
                "sign": "Invalid sign"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "error"
        assert "details" in data


@pytest.mark.run(order=604)
def test_verify_f_ok(test_app, test_files_data, thumbprint, test_api_key):
    """
    Проверка присоединенной подписи у файла.
    Входные данные: 
    - Файл с присоединенной подписью
    Подпись корректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for file_data in test_files_data:
        print(file_data['sign_attach']['file'])
        with open(file_data['sign_attach']['file'], "rb") as f:
            response = test_app.post(
                "/api/verify/f/",
                files={
                    "file": ("test.pdf.sig", f)
                },
                headers=headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "details" in data
        assert "singer" in data["details"] 
        assert "thumbprint" in data["details"]["singer"]
        assert data["details"]["singer"]["thumbprint"] == thumbprint

@pytest.mark.run(order=605)
def test_verify_f_invalid(test_app, test_files_data, test_api_key):
    """
    Проверка присоединенной подписи у файла.
    Входные данные: 
    - Файл с присоединенной подписью
    Подпись некорректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    assert len(test_files_data) >= 1
    with open(test_files_data[0]['value'], "rb") as f:
        response = test_app.post(
            "/api/verify/f/",
            files={
                "file": ("test.pdf.sig", f)
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "error"
        assert "details" in data

@pytest.mark.run(order=606)
def test_verify_s2s_ok(test_app, test_strings_data, thumbprint, test_api_key):
    """
    Проверка отсоединенной подписи у файла.
    Входные данные: 
    - Данные в виде строки  
    - Подпись в виде строки
    Подпись корректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for string_data in test_strings_data:
        response = test_app.post(
            "/api/verify/s2s/",
            data={
                "data": string_data['value'],
                "sign": string_data['sign_deattach']['string']
            },
            headers=headers
        )
    
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "details" in data
        assert "singer" in data["details"] 
        assert "thumbprint" in data["details"]["singer"]
        assert data["details"]["singer"]["thumbprint"] == thumbprint


@pytest.mark.run(order=607)
def test_verify_s2s_invalid_sign(test_app, test_strings_data, test_api_key):
    """
    Проверка отсоединенной подписи у файла.
    Входные данные: 
    - Данные в виде строки  
    - Подпись в виде строки
    Подпись некорректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    assert len(test_strings_data) >= 2
    response = test_app.post(   
        "/api/verify/s2s/",
        data={
            "data": test_strings_data[0]['value'],
            "sign": "Invalid sign"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "error"
    assert "details" in data

@pytest.mark.run(order=608)
def test_verify_s_ok(test_app, test_strings_data, thumbprint, test_api_key):
    """
    Проверка присоединенной подписи у строки.
    Входные данные: 
    - данные и подпись в виде строки  
    Подпись корректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for string_data in test_strings_data:
        response = test_app.post(
            "/api/verify/s/",
            data={
                "data": string_data['sign_attach']['string']
            },
            headers=headers
        )
    
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "details" in data
        assert "singer" in data["details"] 
        assert "thumbprint" in data["details"]["singer"]
        assert data["details"]["singer"]["thumbprint"] == thumbprint


@pytest.mark.run(order=609)
def test_verify_s_invalid_sign(test_app, test_strings_data, test_api_key):
    """
    Проверка присоединенной подписи у строки.
    Входные данные: 
    - данные и подпись в виде строки  
    Подпись некорректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    assert len(test_strings_data) >= 1
    response = test_app.post(
        "/api/verify/s/",
        data={
            "data": test_strings_data[0]['value']
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "error"
    assert "details" in data


@pytest.mark.run(order=610)
def test_verify_xml2f_ok(test_app, test_xml_data, thumbprint, test_api_key):
    """
    Проверка  подписи XML файла.
    Входные данные:
    - XML файл с подписью
    Подпись корректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for xml_data in test_xml_data:
        with open(xml_data['sign_attach']['file'], 'rb') as f:
            response = test_app.post(
                "/api/verify/xml2f/",
                files={
                    "file": ("test.xml", f)
                },
                headers=headers
            )
    
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "success"
    assert "details" in data
    assert "singer" in data["details"] 
    assert "thumbprint" in data["details"]["singer"]
    assert data["details"]["singer"]["thumbprint"] == thumbprint

@pytest.mark.run(order=611)
def test_verify_xml2f_invalid_file(test_app, test_xml_data, test_api_key):
    """
    Проверка отсоединенной подписи XML файла.
    Входные данные:
    - некорректный XML файл
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    assert len(test_xml_data) >= 1
    with open(test_xml_data[0]['value'], 'rb') as f:
        response = test_app.post(
            "/api/verify/xml2f/",
            files={
                "file": ("test.xml", f)
            },
            headers=headers
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "error" 
    assert "details" in data


@pytest.mark.run(order=612)
def test_verify_hash2s_ok(test_app, test_all_data, thumbprint, test_api_key):
    """
    Проверка отсоединенной подписи у хэша.
    Входные данные: 
    - Хэш в виде строки  
    - Подпись в виде строки
    Подпись корректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for test_data in test_all_data:
        response = test_app.post(
            "/api/verify/hash2s/",
            data={
                "hash": test_data['hash'],
                "sign": test_data['sign_hash']['string']
            },
            headers=headers
        )
    
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "details" in data
        assert "singer" in data["details"] 
        assert "thumbprint" in data["details"]["singer"]
        assert data["details"]["singer"]["thumbprint"] == thumbprint

@pytest.mark.run(order=613)
def test_verify_hash2f_ok(test_app, test_all_data, thumbprint, test_api_key):
    """
    Проверка отсоединенной подписи у хэша.
    Входные данные: 
    - Хэш в виде строки  
    - Подпись в виде строки
    Подпись корректная
    """
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for test_data in test_all_data:
        with open(test_data['sign_hash']['file'], 'rb') as f:
            response = test_app.post(
                "/api/verify/hash2f/",
                data={
                    "hash": test_data['hash'],
                    
                },
                files={
                    "sign": ("test.sig", f)
                },
                headers=headers
            )
    
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "details" in data
        assert "singer" in data["details"] 
        assert "thumbprint" in data["details"]["singer"]
        assert data["details"]["singer"]["thumbprint"] == thumbprint