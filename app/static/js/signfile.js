


function VerifySign(data, sign, format_sign) {
    return new Promise(function (resolve, reject) {
        var cadesplugin = window.cadesplugin
        cadesplugin.async_spawn(function* (args) {
            var oSignedData = yield cadesplugin.CreateObjectAsync("CAdESCOM.CadesSignedData");


            try {

                
                if (format_sign == 0) {
                    yield oSignedData.propset_Content(data);
                    yield oSignedData.VerifyCades(sign, cadesplugin.CADESCOM_CADES_BES, true);
                } else if (format_sign == 1) {
                    yield oSignedData.VerifyCades(sign, cadesplugin.CADESCOM_CADES_BES);
                }


                var oSigners = yield oSignedData.Signers;
                var nSigners = yield oSigners.Count;
                var certThumbprints = [];
                var result = "";
                result += "Подписанты: <b>" + nSigners + "</b><br/>"
                var Adjust = new CertificateAdjuster();
                for (var i = 1; i <= nSigners; i++) {
                    var oSigner = yield oSigners.Item(i);
                    var oCert = yield oSigner.Certificate;
                    var oSignStatus = yield oSigner.SignatureStatus;
                    var isValidSignStatus = yield oSignStatus.IsValid;
                    var isValidSign = "Ошибка при проверке подписи";
                    if (isValidSignStatus) {
                        isValidSign = "Подпись проверена успешно";
                    }
                    var isValidCertStatus = yield oCert.IsValid();
                    isValidCertStatus = yield isValidCertStatus.Result;
                    var isValidCert = "Ошибка при проверке статуса сертификата";
                    if (isValidCertStatus) {
                        isValidCert = "Сертификат действителен";
                    }

                    var subject = "-";
                    var issuer = "-";
                    var validFrom = "-";
                    var validTo = "-";
                    var thumbprint = "-";
                    var signingTime = "-";
                    try {
                        subject = escapeHtml(Adjust.GetCertName(yield oCert.SubjectName));
                        issuer = escapeHtml(Adjust.GetIssuer(yield oCert.IssuerName));
                        validFrom = escapeHtml(Adjust.GetCertDate(yield oCert.ValidFromDate)) + " UTC";
                        validTo = escapeHtml(Adjust.GetCertDate(yield oCert.ValidToDate)) + " UTC";
                        thumbprint = yield oCert.Thumbprint;
                        certThumbprints.push(thumbprint);
                        signingTime = escapeHtml(Adjust.GetCertDate(yield oSigner.SigningTime)) + " UTC";
                    }
                    catch (ex) { }
                    result += i + ". Владелец: <b>" + subject + "</b><br/>";
                    result += "&emsp;Издатель: <b>" + issuer + "</b><br/>";
                    result += "&emsp;Выдан: <b>" + validFrom + "</b><br/>";
                    result += "&emsp;Действителен до: <b>" + validTo + "</b><br/>";
                    result += "&emsp;Отпечаток: <b>" + thumbprint + "</b><br/>";
                    result += "&emsp;Статус сертификата: <b>" + isValidCert + "</b><br/>";
                    result += "&emsp;Дата подписи: <b>" + signingTime + "</b><br/>";
                    result += "&emsp;Статус подписи: <b>" + isValidSign + "</b><br/><br/>";
                }


            var resultExt = "";
            try {
                var oCerts = yield oSignedData.Certificates;
                var nCerts = yield oCerts.Count;
                var certIndex = 0;
                for (var i = 1; i <= nCerts; i++) {
                    var oCert = yield oCerts.Item(i);
                    var thumbprint = yield oCert.Thumbprint;
                    if (certThumbprints.indexOf(thumbprint) >= 0)
                        continue;
                    var isValidCertStatus = yield oCert.IsValid();
                    isValidCertStatus = yield isValidCertStatus.Result;
                    var isValidCert = "Ошибка при проверке статуса сертификата";
                    if (isValidCertStatus) {
                        isValidCert = "Сертификат действителен";
                    }

                    var subject = "-";
                    var issuer = "-";
                    var validFrom = "-";
                    var validTo = "-";
                    var signingTime = "-";
                    try {
                        subject = escapeHtml(Adjust.GetCertName(yield oCert.SubjectName));
                        issuer = escapeHtml(Adjust.GetIssuer(yield oCert.IssuerName));
                        validFrom = escapeHtml(Adjust.GetCertDate(yield oCert.ValidFromDate)) + " UTC";
                        validTo = escapeHtml(Adjust.GetCertDate(yield oCert.ValidToDate)) + " UTC";
                        certThumbprints.push(thumbprint);
                    }
                    catch (ex) { }

                    resultExt += ++certIndex + ". Владелец: <b>" + subject + "</b><br/>";
                    resultExt += "&emsp;Издатель: <b>" + issuer + "</b><br/>";
                    resultExt += "&emsp;Выдан: <b>" + validFrom + "</b><br/>";
                    resultExt += "&emsp;Действителен до: <b>" + validTo + "</b><br/>";
                    resultExt += "&emsp;Отпечаток: <b>" + thumbprint + "</b><br/>";
                    resultExt += "&emsp;Статус сертификата: <b>" + isValidCert + "</b><br/><br/>";
                }
                if (resultExt != "") {
                    resultExt = "Другие сертификаты из подписи: <br />" + resultExt;
                    // document.getElementById('toggle_extended_text').style.display = '';
                    document.getElementById('result_client_ex').innerHTML = resultExt;
                }
            }
            catch (ex) { }
            }
            catch (err) {
                var e = cadesplugin.getLastError(err);
                alert("Failed to verify signature. Error: " + e);
                return args[1](e);
            }

            return args[0](result);
        }, resolve, reject);
    });
}
window.onload = () => {
    createCadesplugin();
    document.getElementById("client1").addEventListener('click', (event) => {
        const sign = document.getElementById("hresult").value
        const data  = document.getElementById("data").value
        const format_sign = document.getElementById("format-sign").value

        VerifySign(data, sign).then(
            function (result) {
                document.getElementById("result_client").innerHTML = result;

            },
            function (err) {
                // document.getElementById("signature").innerHTML = err;
                console.log(err)
            }
        )

    })


}