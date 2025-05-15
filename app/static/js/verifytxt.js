var global_selectbox_container = new Array();
var global_selectbox_container_thumbprint = new Array();
var global_selectbox_counter = 0;
var global_isFromCont = new Array();



function onCertificateSelected(event) {
    cadesplugin.async_spawn(function *(args) {
        var selectedCertID = args[0][args[0].selectedIndex].value;
        var certificate = global_selectbox_container[selectedCertID];
        // FillCertInfo_Async(certificate, event.target.boxId, global_isFromCont[selectedCertID]);
    }, event.target);//cadesplugin.async_spawn
  }


function CertStatusEmoji(isValid, hasPrivateKey) {
    var _emoji = "";
    if (isValid) {
        _emoji = "\u2705";
    } else {
        _emoji = "\u274C";
    }
    //if (hasPrivateKey) {
    //    _emoji += "\uD83D\uDD11";
    //} else {
    //    _emoji += String.fromCodePoint(0x1F6AB);
    //}
    return _emoji;
  }

// function FillCertList_Async(lstId, lstId2, rootStore, selectedIndex) {
function FillCertList_Async(lstId, rootStore, selectedIndex) {
  var cadesplugin = window.cadesplugin;
  cadesplugin.async_spawn(function* () {
    console.log("Идет перечисление объектов плагина");
    var MyStoreExists = true;
    try {
      var oStore = yield cadesplugin.CreateObjectAsync("CAdESCOM.Store");
      if (!oStore) {
        alert("Create store failed");
        console.log("Ошибка при перечислении объектов плагина");
        return;
      }
      if (rootStore) {
        yield oStore.Open(
          cadesplugin.CADESCOM_CURRENT_USER_STORE,
          "Root",
          cadesplugin.CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED
        );
      } else yield oStore.Open();
    } catch (ex) {
      MyStoreExists = false;
      console.log(ex);
    }

    var lst = document.getElementById(lstId);
    if(!lst)
    {
        console.log("Ошибка при перечислении объектов плагина");
        return;
    }
    lst.onchange = onCertificateSelected;
    lst.boxId = lstId;


    if (MyStoreExists) {
      try {
        var certs = yield oStore.Certificates;
        var certCnt = yield certs.Count;
      } catch (ex) {
        alert(
          "Ошибка при получении Certificates или Count: " +
            cadesplugin.getLastError(ex)
        );
        console.log("Ошибка при перечислении объектов плагина");
        return;
      }
      for (var i = 1; i <= certCnt; i++) {
        try {
          var cert = yield certs.Item(i);
        } catch (ex) {
          alert(
            "Ошибка при перечислении сертификатов: " +
              cadesplugin.getLastError(ex)
          );
          console.log("Ошибка при перечислении объектов плагина");
          return;
        }

        try {
          var certThumbprint = yield cert.Thumbprint;
          var foundIndex =
            global_selectbox_container_thumbprint.indexOf(certThumbprint);
          if (foundIndex > -1) {
            continue;
          }
          var oOpt = document.createElement("OPTION");
          try {
            var ValidFromDate = new Date(yield cert.ValidFromDate);
            var ValidToDate = new Date(yield cert.ValidToDate);
            var IsValid = ValidToDate > Date.now();
            var emoji = CertStatusEmoji(IsValid);
            oOpt.text = emoji + new CertificateAdjuster().GetCertInfoString(yield cert.SubjectName, ValidFromDate);
          } catch (ex) {
            alert(
              "Ошибка при получении свойства SubjectName: " +
                cadesplugin.getLastError(ex)
            );
          }
          oOpt.value = global_selectbox_counter;
          lst.options.add(oOpt);

          global_selectbox_container.push(cert);
          global_selectbox_container_thumbprint.push(certThumbprint);
          global_isFromCont.push(false);
          global_selectbox_counter++;
        } catch (ex) {
          alert(
            "Ошибка при получении свойства Thumbprint: " +
              cadesplugin.getLastError(ex)
          );
        }
      }
      yield oStore.Close();
    }

    if (rootStore) {
      console.log("Перечисление объектов плагина завершено");
      return;
    }

    //В версии плагина 2.0.13292+ есть возможность получить сертификаты из
    //закрытых ключей и не установленных в хранилище
    try {
      yield oStore.Open(cadesplugin.CADESCOM_CONTAINER_STORE);
      try {
        var certs = yield oStore.Certificates;
        var certCnt = yield certs.Count;
      } catch (ex) {
        alert(
          "Ошибка при получении Certificates или Count: " +
            cadesplugin.getLastError(ex)
        );
        console.log("Ошибка при перечислении объектов плагина");
        return;
      }
      for (var i = 1; i <= certCnt; i++) {
        try {
          var cert = yield certs.Item(i);
        } catch (ex) {
          alert(
            "Ошибка при перечислении сертификатов: " +
              cadesplugin.getLastError(ex)
          );
          console.log("Ошибка при перечислении объектов плагина");
          return;
        }

        try {
          var certThumbprint = yield cert.Thumbprint;
          var foundIndex =
            global_selectbox_container_thumbprint.indexOf(certThumbprint);
          if (foundIndex > -1) {
            continue;
          }
          var oOpt = document.createElement("OPTION");
          try {
            var ValidFromDate = new Date(yield cert.ValidFromDate);
            var ValidToDate = new Date(yield cert.ValidToDate);
            var IsValid = ValidToDate > Date.now();
            var emoji = CertStatusEmoji(IsValid);
            oOpt.text = emoji + new CertificateAdjuster().GetCertInfoString(yield cert.SubjectName, ValidFromDate);
          } catch (ex) {
            alert(
              "Ошибка при получении свойства SubjectName: " +
                cadesplugin.getLastError(ex)
            );
          }
          oOpt.value = global_selectbox_counter;
          lst.options.add(oOpt);

          global_selectbox_container.push(cert);
          global_selectbox_container_thumbprint.push(certThumbprint);
          global_isFromCont.push(true);
          global_selectbox_counter++;
        } catch (ex) {
          alert(
            "Ошибка при получении свойства Thumbprint: " +
              cadesplugin.getLastError(ex)
          );
        }
      }
      yield oStore.Close();
    } catch (ex) {}

    if (global_selectbox_container.length != 0) {
      document.getElementById("CertListBox").style.display = "block";
    } else {
      document.getElementById("CertListBox").style.display = "none";
    }
    // if ((selectedIndex != -1 && selectedIndex) || selectedIndex === 0) {
    //   document.getElementById(lstId).selectedIndex = selectedIndex;
    //   var certificate = global_selectbox_container[selectedIndex];
    //   FillCertInfo_Async(certificate);
    // }
    console.log(
      "Перечисление объектов плагина завершено"
    );
  });
}

function extensionLoadedCallback() {
  window.cadesplugin.then(() => {
    FillCertList_Async("CertListBox");
  });
}

function SignCreate(thumbprint, dataInBase64, format_sign=0) {
    return new Promise(function (resolve, reject) {
        var cadesplugin = window.cadesplugin
        cadesplugin.async_spawn(function* (args) {
            var oStore = yield cadesplugin.CreateObjectAsync("CAdESCOM.Store");
            yield oStore.Open(cadesplugin.CAPICOM_CURRENT_USER_STORE, cadesplugin.CAPICOM_MY_STORE,
            cadesplugin.CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED);

            var oStoreCerts = yield oStore.Certificates;
            var oCertificates = yield oStoreCerts.Find(
            cadesplugin.CAPICOM_CERTIFICATE_FIND_SHA1_HASH, thumbprint);
            var certsCount = yield oCertificates.Count;
            if (certsCount === 0) {
                err = "Certificate not found: " + thumbprint;
                alert(err);
                return args[1](err);
            }
            var oCertificate = yield oCertificates.Item(1);
            var oSigner = yield cadesplugin.CreateObjectAsync("CAdESCOM.CPSigner");
            yield oSigner.propset_Certificate(oCertificate);
            yield oSigner.propset_CheckCertificate(true);

            var oSignedData = yield cadesplugin.CreateObjectAsync("CAdESCOM.CadesSignedData");
            // Значение свойства ContentEncoding должно быть задано
            // до заполнения свойства Content
            yield oSignedData.propset_ContentEncoding(cadesplugin.CADESCOM_BASE64_TO_BINARY);
            yield oSignedData.propset_Content(dataInBase64);

            var sSignedMessage = "";
            try {
                
              if (format_sign == 0){
                sSignedMessage = yield oSignedData.SignCades(oSigner, cadesplugin.CADESCOM_CADES_BES, true);
              } else
              {
                sSignedMessage = yield oSignedData.SignCades(oSigner, cadesplugin.CADESCOM_CADES_BES, false);

              }
            
            } catch (err) {
                e = cadesplugin.getLastError(err);
                alert("Failed to create signature. Error: " + e);
                return args[1](e);
            }

            yield oStore.Close();
            return args[0](sSignedMessage);
        }, resolve, reject);
    });
}




window.onload = () => {
  document.body.addEventListener("htmx:afterSwap", function (evt) {
    evt.detail.elt.innerHTML = JSON.stringify(
      JSON.parse(evt.detail.elt.innerHTML),
      null,
      4
    );
    evt.detail.elt.innerText = JSON.stringify(
      JSON.parse(evt.detail.elt.innerText),
      null,
      4
    );
  });
  
    document.getElementById("client1").addEventListener('click', (event) => {
    var idSelectedCert =  document.getElementById("CertListBox").value
    var data = btoa(unescape(encodeURIComponent(document.getElementById("data").value)));
    console.log(data)
    // var data = "U29tZSBEYXRhLg=="
    if (!idSelectedCert || !data) {
        return;
    }  
    var thumbprint_cert = global_selectbox_container_thumbprint[idSelectedCert]
    const format_sign = document.getElementById("format-sign").value
    SignCreate(thumbprint_cert, data, format_sign).then(
        function (signedMessage) {
            document.getElementById("sign1").value = signedMessage;
            // console.log(signedMessage)
        },
        function (err) {
            // document.getElementById("signature").innerHTML = err;
            console.log(err)
        }
    )
  })
  
  
  window.cadesplugin_extension_loaded_callback = extensionLoadedCallback;
  createCadesplugin();
};
