


window.onload = () => {
    // finalLoad()
    createCadesplugin()
    const btn_client_txt = document.getElementById('client_txt')
    btn_client_txt.addEventListener('click', ()=>{

        window.cadesplugin.async_spawn(function* (args) {
            // Создаем объект CAdESCOM.HashedData
            var oHashedData = yield cadesplugin.CreateObjectAsync("CAdESCOM.HashedData");

            // Алгоритм хэширования нужно указать до того, как будут переданы данные
            oHashedData.propset_Algorithm(cadesplugin.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256);
            data=document.getElementById("data").value
            // Передаем данные
            yield oHashedData.Hash(data);

            // Вычисляем хэш-значение
            var sHashValue1 = yield oHashedData.Value;
            // Хэш-значение будет вычислено от данных в кодировке UCS2-LE
            // Для алгоритма SHA-1 хэш-значение будет совпадать с вычисленным при помощи CAPICOM
            result = {
                "result":"success",
                "details":{
                    "hash": sHashValue1,
                    "algorithm_code": cadesplugin.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256,
                    "algorithm_name": "CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256",
                    "source": 'text'
                }
            }
            
            result_el = document.getElementById("result_client_txt")
            result_el.innerHTML = JSON.stringify(result, null, 4)
            result_el.innerText = JSON.stringify(result, null, 4)

        });
    })
    const btn_client_file = document.getElementById('client_file')
    btn_client_file.addEventListener('click', (event)=>{
        event.preventDefault();
        var oFile = document.getElementById("file").files[0];
        var oFReader = new FileReader();
        oFReader.readAsDataURL(oFile);
        oFReader.onload = function (oFREvent) {
            window.cadesplugin.async_spawn(function* (args) {
                var header = ";base64,";
                var sFileData = oFREvent.target.result;
                var sBase64Data = sFileData.substr(sFileData.indexOf(header) + header.length);
                var oHashedData = yield cadesplugin.CreateObjectAsync("CAdESCOM.HashedData");
                yield oHashedData.propset_Algorithm(cadesplugin.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256);
                yield oHashedData.propset_DataEncoding(cadesplugin.CADESCOM_BASE64_TO_BINARY);
                yield oHashedData.Hash(sBase64Data);
            
                var result = {
                    "result":"success",
                    "details":{
                        "hash": yield oHashedData.Value,
                        "algorithm_code": cadesplugin.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256,
                        "algorithm_name": "CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256",
                        "source": 'file'
                    }
                }
                result_el = document.getElementById("result_client_file")
                result_el.innerHTML = JSON.stringify(result, null, 4)
                result_el.innerText = JSON.stringify(result, null, 4)

            })


        }
    })
}