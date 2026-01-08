import pytest

@pytest.mark.run(order=500)
def test_sign_f2f_ok(test_app, test_files_data, thumbprint, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for file_data in test_files_data:
        with open(file_data['value'], 'rb') as f:
            response = test_app.post(
                "/api/sign/f2f/",
                files={"file": ('test.pdf', f)},
                data={"thumbprint": thumbprint},
                headers=headers
            )
        
        assert response.status_code == 200
        
        # Save signed file
        signed_file_path = f"{file_data['value']}_file_deattach.sig"
        with open(signed_file_path, 'wb') as f:
            f.write(response.content)
        file_data['sign_deattach']['file'] = signed_file_path

@pytest.mark.run(order=501)
def test_sign_f2s_ok(test_app, test_files_data, thumbprint, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for file_data in test_files_data:
        with open(file_data['value'], 'rb') as f:
            response = test_app.post(
                "/api/sign/f2s/",
                files={"file": ('test.pdf', f)},
                data={"thumbprint": thumbprint},
                headers=headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "details" in data
        file_data['sign_deattach']['string'] = data['details']


@pytest.mark.run(order=502)
def test_sign_f_ok(test_app, test_files_data, thumbprint, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for file_data in test_files_data:
        with open(file_data['value'], 'rb') as f:
            response = test_app.post(
                "/api/sign/f/",
                files={"file": ('test.pdf', f)},
                data={"thumbprint": thumbprint},
                headers=headers
            )
        
        assert response.status_code == 200
        
        # Save signed file
        signed_file_path = f"{file_data['value']}_file_attach.sig"
        with open(signed_file_path, 'wb') as f:
            f.write(response.content)
        file_data['sign_attach']['file'] = signed_file_path

@pytest.mark.run(order=503)
def test_sign_s2s_ok(test_app, test_strings_data, thumbprint, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for string_data in test_strings_data:
        response = test_app.post(
            "/api/sign/s2s/",
            data={
                "data": string_data['value'],
                "thumbprint": thumbprint
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "details" in data
        string_data['sign_deattach']['string'] = data['details']

@pytest.mark.run(order=504)
def test_sign_s_ok(test_app, test_strings_data, thumbprint, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for string_data in test_strings_data:
        response = test_app.post(
            "/api/sign/s/",
            data={
                "data": string_data['value'],
                "thumbprint": thumbprint
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "details" in data
        string_data['sign_attach']['string'] = data['details']



@pytest.mark.run(order=506)
def test_sign_xml_ok(test_app, test_xml_data, thumbprint, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for xml_data in test_xml_data:
        with open(xml_data['value'], 'rb') as f:
            response = test_app.post(
                "/api/sign/xml2f/",
                files={
                    "file": ("test.xml", f)
                },
                data={
                    "thumbprint": thumbprint
                },
                headers=headers
            )
        
        assert response.status_code == 200
        
        # Save signed file
        signed_file_path = xml_data['value'] + '.sig'
        with open(signed_file_path, 'wb') as f:
            f.write(response.content)
            
        xml_data['sign_attach']['file'] = signed_file_path


@pytest.mark.run(order=507)
def test_sign_hash2s_ok(test_app, test_all_data, thumbprint, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for test_data in test_all_data:

        response = test_app.post(
            "/api/sign/hash2s/",
            data={
                "hash": test_data['hash'],
                "thumbprint": thumbprint
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "details" in data
        test_data['sign_hash']['string'] = data['details']

@pytest.mark.run(order=508)
def test_sign_hash2f_ok(test_app, test_all_data, thumbprint, test_api_key):
    headers = {"X-API-Key": test_api_key} if test_api_key else {}
    for i, test_data in enumerate(test_all_data):
        response = test_app.post(
            "/api/sign/hash2f/",
            data={
                "hash": test_data['hash'],
                "thumbprint": thumbprint
            },
            headers=headers
        )
        
        assert response.status_code == 200
        
        # Save signed file
        signed_file_path = f'tests/files/sing_hash_{i}.sig'
        with open(signed_file_path, 'wb') as f:
            f.write(response.content)
            
        test_data['sign_hash']['file'] = signed_file_path