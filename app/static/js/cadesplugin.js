"use strict";



var chrome_ext_id = "iifchhfnnmpdbibifmljnfjhpififfog";
var opera_ext_id = "epebfcehmdedogndhlcacafjaacknbcm";
var global_selectbox_container = new Array();
var global_selectbox_container_thumbprint = new Array();
var global_selectbox_counter = 0;
var global_isFromCont = new Array();

var Colors = {
  ERROR: {value:'red'},     // неисправимая ошибка
  FAIL: {value:'red'},      // ошибка с решением
  INFO: {value:'yellow'},   // информация для пользователя
  UPDATE: {value:'yellow'}, // уведомление о новой версии
  SUCCESS: {value:'green'}, // завершенное действие
  WAIT: {value:'grey'}      // ожидание загрузки
};

var extImg = Colors.FAIL;
var extTxt = "Расширение не загружено";

var plgImg = Colors.WAIT;
var plgTxt = "Плагин: ожидание загрузки расширения";

var cspImg = Colors.WAIT;
var cspTxt = "КриптоПро CSP: ожидание загрузки плагина";

var objImg = Colors.WAIT;
var objTxt = "Объекты плагина: ожидание загрузки провайдера";

var browserSpecs = check_browser();


function setImgSrcAttribute(id, color) {
  var elem = document.getElementById(id);
  var colorString = color.value ? color.value : 'red';
  if (elem) elem.className = "dot " + colorString;
}

function setInnerText(id, value, noescape) {
  var elem = document.getElementById(id);
  if (elem) elem.innerHTML = noescape === true ? value : escapeHtml(value);
}

function setHref(id, value) {
  var elem = document.getElementById(id);
  if (elem) elem.href = value;
}

function setStateForObjects(img, txt) {
  setImgSrcAttribute("ObjectsLoadedImg", img);
  setInnerText("ObjectsLoadedTxt", txt);
  objImg = img;
  objTxt = txt;
  if (objImg === Colors.FAIL) {
    setInnerText("ObjectsSolution", "<a href='javascript:window.location.reload();'>Обновите страницу</a> или <a href='https://support.cryptopro.ru/'>обратитесь в техподдержку</a>", true);
  } else {
    setInnerText("ObjectsSolution", "");
  }
}

function setStateForExtension(img, txt) {
  setImgSrcAttribute("ExtensionEnabledImg", img);
  setInnerText("ExtensionEnabledTxt", txt);
  extImg = img;
  extTxt = txt;
  if (extImg === Colors.FAIL) {
    // ставим значение по умолчанию в зависимости от системы
    var extUrl = "https://docs.cryptopro.ru/cades/plugin/plugin-installation-windows";
    if (platformCheck() === "macOS") {
      extUrl = "https://docs.cryptopro.ru/cades/plugin/plugin-installation-macos";
    } else if (platformCheck() === "Linux") {
      extUrl = "https://docs.cryptopro.ru/cades/plugin/plugin-installation-unix";
    }
    // ставим нужную ссылку если узнали какой браузер
    if (browserSpecs.name === 'Chrome'){
      extUrl = "https://chrome.google.com/webstore/detail/cryptopro-extension-for-c/iifchhfnnmpdbibifmljnfjhpififfog";
    } else if (browserSpecs.name === 'YaBrowser' | browserSpecs.name === 'Opera') {
      extUrl = "https://addons.opera.com/en/extensions/details/cryptopro-extension-for-cades-browser-plug-in";
    } else if (browserSpecs.name === 'Firefox') {
      extUrl = "https://www.cryptopro.ru/sites/default/files/products/cades/extensions/firefox_cryptopro_extension_latest.xpi";
    }
    setInnerText("ExtensionSolution", "<a href='" + extUrl + "'>Загрузить</a>", true);
  } else {
    setInnerText("ExtensionSolution","");
  }
}

function setStateForCSP(img, txt) {
  setImgSrcAttribute("CspEnabledImg", img);
  setInnerText("CspEnabledTxt", txt);
  cspImg = img;
  cspTxt = txt;
  if (cspImg === Colors.FAIL) {
    setInnerText("CspSolution", "<a href='https://cryptopro.ru/products/csp?csp=download'>Загрузите CSP</a> и обновите страницу", true);
  } else {
    setInnerText("CspSolution", "");
  }
}

function setStateForPlugin(img, txt) {
  setImgSrcAttribute("PluginEnabledImg", img);
  setInnerText("PluginEnabledTxt", txt);
  plgImg = img;
  plgTxt = txt;
  if (plgImg === Colors.UPDATE) {
    setInnerText("PluginSolution", "<a href='https://cryptopro.ru/products/cades/plugin/get_2_0'>Обновить</a>", true);
  } else if (plgImg === Colors.FAIL) {
    setInnerText("PluginSolution", "<a href='https://cryptopro.ru/products/cades/plugin/get_2_0'>Загрузите плагин</a> и обновите страницу", true);
  } else {
    setInnerText("PluginSolution", "");
  }

}



function ShowEdgeNotSupported() {
  setStateForPlugin(Colors.ERROR, "К сожалению, браузер Edge не поддерживается, обновитесь до Edge версии >= 79");
}


function cadesPluginUUID() {
  if (!localStorage.hasOwnProperty("cadesPluginUUID")) {
      var uuid = createUUID();
      localStorage.setItem("cadesPluginUUID", uuid);
      return uuid;
  } else {
      var uuid = localStorage.getItem("cadesPluginUUID");
      return uuid;
  }
}

function getTelemetryData(pluginVersion, cspVersion) {
  var osName = platformCheck();
  var uuid = cadesPluginUUID();
  
  return {
      plugin: pluginVersion,
      csp: cspVersion,
      os: osName,
      uuid: uuid,
  };
}

function isExtensionNeeded() {
    if (isIE()) return false;
    if (browserSpecs.name == 'Edge') { return true; }
    if (browserSpecs.name == 'Opera') { if (browserSpecs.version >= 33) { return true; } else { return false; } }
    if (browserSpecs.name == 'Firefox') { if (browserSpecs.version >= 52) { return true; } else { return false; } }
    if (browserSpecs.name == 'Chrome') { if (browserSpecs.version >= 42) { return true; } else { return false; } }
    if (browserSpecs.name == 'Safari') { if (browserSpecs.version >= 11) { return true; } else { return false; } }
    return true;
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

function ClearCertInfo(field_prefix) {
  document.getElementById(field_prefix + "subject").innerHTML = "Владелец:";
  document.getElementById(field_prefix + "issuer").innerHTML = "Издатель:";
  document.getElementById(field_prefix + "from").innerHTML = "Выдан:";
  document.getElementById(field_prefix + "till").innerHTML = "Действителен до:";
  document.getElementById(field_prefix + "provname").innerHTML = "Криптопровайдер:";
  document.getElementById(field_prefix + "privateKeyLink").innerHTML = "Ссылка на закрытый ключ:";
  document.getElementById(field_prefix + "algorithm").innerHTML = "Алгоритм ключа:";
  document.getElementById(field_prefix + "status").innerHTML = "Статус:";
  document.getElementById(field_prefix + "location").innerHTML = "Установлен в хранилище:";
  document.getElementById(field_prefix + "certlicense").innerHTML = "";
}

function FillCertInfo_Async(certificate, certBoxId, isFromContainer)
{
    var BoxId;
    var field_prefix;
    if(typeof(certBoxId) == 'undefined' || certBoxId == "CertListBox")
    {
        BoxId = 'cert_info';
        field_prefix = '';
    }else if (certBoxId == "CertListBox1") {
        BoxId = 'cert_info1';
        field_prefix = 'cert_info1';
    } else if (certBoxId == "CertListBox2") {
        BoxId = 'cert_info2';
        field_prefix = 'cert_info2';
    } else {
        BoxId = certBoxId;
        field_prefix = certBoxId;
    }
    cadesplugin.async_spawn (function*(args) {
        ClearCertInfo(field_prefix);
        var Adjust = new CertificateAdjuster();

        document.getElementById(args[1]).style.display = '';
        document.getElementById(args[2] + "subject").innerHTML = "Владелец: <b>" + escapeHtml(Adjust.GetCertName(yield args[0].SubjectName)) + "<b>";
        document.getElementById(args[2] + "issuer").innerHTML = "Издатель: <b>" + escapeHtml(Adjust.GetIssuer(yield args[0].IssuerName)) + "<b>";

        var ValidToDate = new Date((yield args[0].ValidToDate));
        var ValidFromDate = new Date((yield args[0].ValidFromDate));

        document.getElementById(args[2] + "from").innerHTML = "Выдан: <b>" + escapeHtml(Adjust.GetCertDate(ValidFromDate)) + " UTC<b>";
        document.getElementById(args[2] + "till").innerHTML = "Действителен до: <b>" + escapeHtml(Adjust.GetCertDate(ValidToDate)) + " UTC<b>";

        var hasPrivateKey = yield args[0].HasPrivateKey();
        var Now = new Date();

        var pubKey = yield args[0].PublicKey();
        var algo = yield pubKey.Algorithm;
        var fAlgoName = yield algo.FriendlyName;

        var isRootExport = location.pathname.indexOf("cades_root_export.html") >= 0

        document.getElementById(args[2] + "algorithm").innerHTML = "Алгоритм ключа: <b>" + escapeHtml(fAlgoName) + "<b>";
        if (hasPrivateKey) {
            var oPrivateKey = yield args[0].PrivateKey;
            var sProviderName = yield oPrivateKey.ProviderName;
            document.getElementById(args[2] + "provname").innerHTML = "Криптопровайдер: <b>" + escapeHtml(sProviderName) + "<b>";
            try {
                var sPrivateKeyLink = yield oPrivateKey.UniqueContainerName;
                document.getElementById(args[2] + "privateKeyLink").innerHTML = "Ссылка на закрытый ключ: <b>" + escapeHtml(sPrivateKeyLink) + "<b>";
            } catch (e) {
                document.getElementById(args[2] + "privateKeyLink").innerHTML = "Ссылка на закрытый ключ: <b>" + escapeHtml(cadesplugin.getLastError(e)) + "<b>";
            }
        } else if (!isRootExport) {
            document.getElementById(args[2] + "provname").innerHTML = "Криптопровайдер:<b>";
            document.getElementById(args[2] + "privateKeyLink").innerHTML = "Ссылка на закрытый ключ:<b>";
        }
        var certIsValid = false;
        if(Now < ValidFromDate) {
            document.getElementById(args[2] + "status").innerHTML = "Статус: <b class=\"error\">Срок действия не наступил</b>";
        } else if( Now > ValidToDate){
            document.getElementById(args[2] + "status").innerHTML = "Статус: <b class=\"error\">Срок действия истек</b>";
        } else if( !hasPrivateKey ){
            if (isRootExport) {
                document.getElementById(args[2] + "status").innerHTML = "Статус: <b>Нет привязки к закрытому ключу</b>";
            } else {
            document.getElementById(args[2] + "status").innerHTML = "Статус: <b class=\"error\">Нет привязки к закрытому ключу</b>";
            }
        } else {
            //если попадется сертификат с неизвестным алгоритмом
            //тут будет исключение. В таком сертификате просто пропускаем такое поле
            try {
                var Validator = yield args[0].IsValid();
                certIsValid = yield Validator.Result;
            } catch(e) {
                certIsValid = false;
            }
            if(certIsValid){
                document.getElementById(args[2] + "status").innerHTML = "Статус: <b> Действителен<b>";
            } else {
                var isValidInfo = "";
                try { 
                    isValidInfo = "Статус: <b class=\"error\">Не действителен</b><br/>";
                    isValidInfo += "Цепочка для сертификата:"
                    var oChainCerts = yield Validator.ValidationCertificates;
                    var oErrorStatuses = yield Validator.ErrorStatuses;
                    var chainCount = yield oChainCerts.Count;
                    for (var j = 1; j <= chainCount; j++) {
                        var oChainCert = yield oChainCerts.Item(j);
                        var chainSN = escapeHtml(Adjust.GetCertName(yield oChainCert.SubjectName));
                        var status = yield oErrorStatuses.Item(chainCount - j + 1);
                        var sStatus = "";
                        if (status) {
                            sStatus = " <b class=\"error\">";
                            if (status & cadesplugin.CERT_TRUST_IS_NOT_TIME_VALID) sStatus += "Истек/не наступил срок действия сертификата; ";
                            if (status & cadesplugin.CERT_TRUST_IS_REVOKED) sStatus += "Сертификат отозван; ";
                            if (status & cadesplugin.CERT_TRUST_IS_NOT_SIGNATURE_VALID) sStatus += "Сертификат не имеет действительной подписи; ";
                            if (status & cadesplugin.CERT_TRUST_IS_NOT_VALID_FOR_USAGE) sStatus += "Сертификат не предназначен для такого использования; ";
                            if (status & cadesplugin.CERT_TRUST_IS_UNTRUSTED_ROOT) sStatus += "Нет доверия к корневому сертификату; ";
                            if (status & cadesplugin.CERT_TRUST_REVOCATION_STATUS_UNKNOWN) sStatus += "Статус сертификата неизвестен; ";
                            if (status & cadesplugin.CERT_TRUST_IS_CYCLIC) sStatus += "Кольцевая зависимость для издателей сертификатов; ";
                            if (status & cadesplugin.CERT_TRUST_INVALID_EXTENSION) sStatus += "Одно из расширений сертификата недействительно; ";
                            if (status & cadesplugin.CERT_TRUST_INVALID_POLICY_CONSTRAINTS) sStatus += "Некорректные ограничения для сертификата; ";
                            if (status & cadesplugin.CERT_TRUST_INVALID_BASIC_CONSTRAINTS) sStatus += "Некорректные ограничения для сертификата; ";
                            if (status & cadesplugin.CERT_TRUST_INVALID_NAME_CONSTRAINTS) sStatus += "Некорректные ограничения для сертификата; ";
                            if (status & cadesplugin.CERT_TRUST_HAS_NOT_SUPPORTED_NAME_CONSTRAINT) sStatus += "Некорректные ограничения для сертификата; ";
                            if (status & cadesplugin.CERT_TRUST_HAS_NOT_DEFINED_NAME_CONSTRAINT) sStatus += "Некорректные ограничения для сертификата; ";
                            if (status & cadesplugin.CERT_TRUST_HAS_NOT_PERMITTED_NAME_CONSTRAINT) sStatus += "Некорректные ограничения для сертификата; ";
                            if (status & cadesplugin.CERT_TRUST_HAS_EXCLUDED_NAME_CONSTRAINT) sStatus += "Некорректные ограничения для сертификата; ";
                            if (status & cadesplugin.CERT_TRUST_IS_OFFLINE_REVOCATION) sStatus += "Статус сертификата на отзыв либо устарел, либо проверка производится оффлайн; ";
                            if (status & cadesplugin.CERT_TRUST_NO_ISSUANCE_CHAIN_POLICY) sStatus += "Конечный сертификат не имеет результирующей политики выдачи, а один из сертификатов выдающего центра сертификации имеет расширение ограничений политики, требующее этого; ";
                            if (status & cadesplugin.CERT_TRUST_IS_EXPLICIT_DISTRUST) sStatus += "Явное недоверие к сертификату ";
                            if (status & cadesplugin.CERT_TRUST_HAS_NOT_SUPPORTED_CRITICAL_EXT) sStatus += "Сертификат не поддерживает критическое расширение; ";
                            if (status & cadesplugin.CERT_TRUST_HAS_WEAK_SIGNATURE) sStatus += "При подписи сертификата использован недостаточно стойкий алгоритм; ";
                            if (sStatus) {
                                sStatus = sStatus.substring(0, sStatus.length - 2);
                            }
                            sStatus += "</b> ";
                        }
                    isValidInfo += "<br/>• <b>" + chainSN + "</b>" + sStatus;
                    }
                }
                catch (e) {
                    isValidInfo = "Статус: <b class=\"error\">Ошибка при проверке цепочки сертификатов. Возможно, на компьютере не установлены сертификаты УЦ, выдавшего ваш сертификат</b>";
                }
                document.getElementById(args[2] + "status").innerHTML = isValidInfo;
            }
            try {
                var oExts = yield args[0].Extensions();
                var extCount = yield oExts.Count;
                for (i = 1; i <= extCount; i++) {
                    var oExt = yield oExts.Item(i);
                    var oOID = yield oExt.OID;
                    var oidValue = yield oOID.Value;
                    if (oidValue == "1.2.643.2.2.49.2") {
                        document.getElementById(args[2] + "certlicense").innerHTML = "Лицензия CSP в сертификате: <b>Да</b>";
                        break;
                    }
                }
            }
            catch (e) { }
        }

        if(args[3])
        {
            if (certIsValid) {
                document.getElementById(field_prefix + "location").innerHTML = "Установлен в хранилище: <span><b class=\"warning\">Нет. При такой конфигурации не все приложения и порталы могут работать</b><br/><a style=\"cursor: pointer\" onclick=\"Common_InstallCertificate('"+ escapeHtml(certBoxId) +"');\">Установить</a></span>";
            } else {
                document.getElementById(field_prefix + "location").innerHTML = "Установлен в хранилище: <b>Нет</b>";
            }
        } else {
            document.getElementById(field_prefix + "location").innerHTML = "Установлен в хранилище: <b>Да</b>";
        }
        if ((window.innerHeight + Math.round(window.scrollY)) >= document.body.offsetHeight) {
            var footer = document.getElementById('footer')
            if (footer) {
                var h = footer.offsetHeight;
                window.scrollBy(0, -1 * h);
            }
        }
    }, certificate, BoxId, field_prefix, isFromContainer);//cadesplugin.async_spawn
}

function onCertificateSelected(event) {
  cadesplugin.async_spawn(function *(args) {
      var selectedCertID = args[0][args[0].selectedIndex].value;
      var certificate = global_selectbox_container[selectedCertID];
      FillCertInfo_Async(certificate, event.target.boxId, global_isFromCont[selectedCertID]);
  }, event.target);//cadesplugin.async_spawn
}

function FillCertList_Async(lstId, lstId2, rootStore, selectedIndex) {
  cadesplugin.async_spawn(
    function *() {
      setStateForObjects(Colors.INFO, "Идет перечисление объектов плагина");
      var MyStoreExists = true;
      try {
          var oStore = yield cadesplugin.CreateObjectAsync("CAdESCOM.Store");
          if (!oStore) {
              alert("Create store failed");
              setStateForObjects(Colors.FAIL, "Ошибка при перечислении объектов плагина");
              return;
          }
          if (rootStore) {
              yield oStore.Open(
                  cadesplugin.CADESCOM_CURRENT_USER_STORE,
                  "Root",
                  cadesplugin.CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED
              );
          } else yield oStore.Open()
      }
      catch (ex) {
          MyStoreExists = false;
      }

      var lst = document.getElementById(lstId);
      if(!lst)
      {
          setStateForObjects(Colors.FAIL, "Ошибка при перечислении объектов плагина");
          return;
      }
      lst.onchange = onCertificateSelected;
      lst.boxId = lstId;

      // второй список опционален
      var lst2 = document.getElementById(lstId2);
      if(lst2)
      {
          lst2.onchange = onCertificateSelected;
          lst2.boxId = lstId2;
      }

      if (MyStoreExists) {
          try {
              var certs = yield oStore.Certificates;
              var certCnt = yield certs.Count;
          }
          catch (ex) {
              alert("Ошибка при получении Certificates или Count: " + cadesplugin.getLastError(ex));
              setStateForObjects(Colors.FAIL, "Ошибка при перечислении объектов плагина");
              return;
          }
          for (var i = 1; i <= certCnt; i++) {
              try {
                  var cert = yield certs.Item(i);
              }
              catch (ex) {
                  alert("Ошибка при перечислении сертификатов: " + cadesplugin.getLastError(ex));
                  setStateForObjects(Colors.FAIL, "Ошибка при перечислении объектов плагина");
                  return;
              }

              try {
                  var certThumbprint = yield cert.Thumbprint;
                  var foundIndex = global_selectbox_container_thumbprint.indexOf(certThumbprint);
                  if (foundIndex > -1) {
                      continue;
                  }
                  var oOpt = document.createElement("OPTION");
                  try {
                      var ValidFromDate = new Date((yield cert.ValidFromDate));
                      var ValidToDate = new Date(yield cert.ValidToDate);
                      var IsValid = ValidToDate > Date.now();
                      var emoji = CertStatusEmoji(IsValid);
                      oOpt.text = emoji + new CertificateAdjuster().GetCertInfoString(yield cert.SubjectName, ValidFromDate);
                  }
                  catch (ex) {
                      alert("Ошибка при получении свойства SubjectName: " + cadesplugin.getLastError(ex));
                  }
                  oOpt.value = global_selectbox_counter;
                  lst.options.add(oOpt);
                  if (lst2) {
                      var oOpt2 = document.createElement("OPTION");
                      oOpt2.text = oOpt.text;
                      oOpt2.value = oOpt.value;
                      lst2.options.add(oOpt2);
                  }
                  global_selectbox_container.push(cert);
                  global_selectbox_container_thumbprint.push(certThumbprint);
                  global_isFromCont.push(false);
                  global_selectbox_counter++;
              }
              catch (ex) {
                  alert("Ошибка при получении свойства Thumbprint: " + cadesplugin.getLastError(ex));
              }
          }
          yield oStore.Close();
      }

      if (rootStore) {
          setStateForObjects(Colors.SUCCESS, "Перечисление объектов плагина завершено");
          return
      }

      //В версии плагина 2.0.13292+ есть возможность получить сертификаты из 
      //закрытых ключей и не установленных в хранилище
      try {
          yield oStore.Open(cadesplugin.CADESCOM_CONTAINER_STORE);
          try {
              var certs = yield oStore.Certificates;
              var certCnt = yield certs.Count;
          }
          catch (ex) {
              alert("Ошибка при получении Certificates или Count: " + cadesplugin.getLastError(ex));
              setStateForObjects(Colors.FAIL, "Ошибка при перечислении объектов плагина");
              return;
          }
          for (var i = 1; i <= certCnt; i++) {
              try {
                  var cert = yield certs.Item(i);
              }
              catch (ex) {
                  alert("Ошибка при перечислении сертификатов: " + cadesplugin.getLastError(ex));
                  setStateForObjects(Colors.FAIL, "Ошибка при перечислении объектов плагина");
                  return;
              }

              try {
                  var certThumbprint = yield cert.Thumbprint;
                  var foundIndex = global_selectbox_container_thumbprint.indexOf(certThumbprint);
                  if (foundIndex > -1) {
                      continue;
                  }
                  var oOpt = document.createElement("OPTION");
                  try {
                      var ValidFromDate = new Date((yield cert.ValidFromDate));
                      var ValidToDate = new Date(yield cert.ValidToDate);
                      var IsValid = ValidToDate > Date.now();
                      var emoji = CertStatusEmoji(IsValid);
                      oOpt.text = emoji + new CertificateAdjuster().GetCertInfoString(yield cert.SubjectName, ValidFromDate);
                  }
                  catch (ex) {
                      alert("Ошибка при получении свойства SubjectName: " + cadesplugin.getLastError(ex));
                  }
                  oOpt.value = global_selectbox_counter;
                  lst.options.add(oOpt);
                  if (lst2) {
                      var oOpt2 = document.createElement("OPTION");
                      oOpt2.text = oOpt.text;
                      oOpt2.value = oOpt.value;
                      lst2.options.add(oOpt2);
                  }
                  global_selectbox_container.push(cert);
                  global_selectbox_container_thumbprint.push(certThumbprint);
                  global_isFromCont.push(true);
                  global_selectbox_counter++;
              }
              catch (ex) {
                  alert("Ошибка при получении свойства Thumbprint: " + cadesplugin.getLastError(ex));
              }
          }
          yield oStore.Close();

      }
      catch (ex) {
      }
      if(global_selectbox_container.length != 0) {
          document.getElementById("CertListBox").style.display = 'block';
      }
      else {
        document.getElementById("CertListBox").style.display = 'none';

      }
      if (selectedIndex != -1 && selectedIndex || selectedIndex === 0) {
          document.getElementById(lstId).selectedIndex = selectedIndex;
          var certificate = global_selectbox_container[selectedIndex];
          FillCertInfo_Async(certificate);
      }
      setStateForObjects(Colors.SUCCESS, "Перечисление объектов плагина завершено");
 
    });//cadesplugin.async_spawn

}

function CheckForPlugIn_Async() {
  function VersionCompare_Async(StringVersion, CurrentVersion)
  {
      // on error occurred suppose that current is actual
      var isActualVersion = true;

      if(typeof(CurrentVersion) === "string")
          return;

      var arr = StringVersion.split('.');
      var NewVersion = {
          MajorVersion: parseInt(arr[0]), 
          MinorVersion: parseInt(arr[1]), 
          BuildVersion: parseInt(arr[2])
      };
      cadesplugin.async_spawn(function *() {
          if(NewVersion.MajorVersion > (yield CurrentVersion.MajorVersion)) {
              isActualVersion = false;
          } else if(NewVersion.MinorVersion > (yield CurrentVersion.MinorVersion)) {
              isActualVersion = false;
          } else if(NewVersion.BuildVersion > (yield CurrentVersion.BuildVersion)) {
              isActualVersion = false;
          }

          if(!isActualVersion) {
              setStateForPlugin(Colors.UPDATE, "Плагин загружен, но есть более свежая версия.");
          }
          return;
      });
  }

  function CheckUpdateServer(CurrentPluginVersion, versionStruct) {
      var telemetryData = getTelemetryData(versionStruct.plugin, versionStruct.csp);
      var paramsArray = [];
      var params = "?";
      for (var property in telemetryData) {
          paramsArray.push(property + "=" + telemetryData[property].toLowerCase());
      }
      params += paramsArray.join('&');
      try {
          var xmlhttp = getXmlHttp();
          xmlhttp.onreadystatechange = function() {
              if (xmlhttp.readyState === 4) {
                  if(xmlhttp.status === 200) {
                      var jsonResponse = JSON.parse(xmlhttp.responseText);
                      var versions = jsonResponse.versions;
                      for (var i = 0; i < versions.length; i++) {
                          VersionCompare_Async(versions[i].version, CurrentPluginVersion);
                      }
                  }
              }
          }
          xmlhttp.open("GET", "https://api.cryptopro.ru/v1/cades/getState" + params, true);
          xmlhttp.send(null);
      }
      catch (exception) {
          // check version failed, nothing to do
      }
  }

  function ext_version_loaded_callback(ext_version) {
      document.getElementById('ExtVersionTxt').innerHTML = escapeHtml("Версия расширения: " + ext_version);
  }

  var extStore = "";
  function ext_id_loaded_callback(ext_id) {
      var OperaStoreExtId = "epebfcehmdedogndhlcacafjaacknbcm";
      var ChromeStoreExtId = "iifchhfnnmpdbibifmljnfjhpififfog";
      if (extStore !== "")
          extStore += ", ";
      if (ext_id === OperaStoreExtId)
          extStore += "Opera Store";
      else if (ext_id === ChromeStoreExtId)
          extStore += "Chrome Store";
      document.getElementById('ExtStoreTxt').innerHTML = escapeHtml("Магазин расширений: " + extStore);
  }

  var versionStruct = {csp: null, os: null, plugin: null, uuid: null};
  setStateForCSP(Colors.INFO, "КриптоПро CSP не загружен");
  cadesplugin.async_spawn(function *() {
      var oAbout = yield cadesplugin.CreateObjectAsync("CAdESCOM.About");
      cadesplugin.get_extension_version(ext_version_loaded_callback);
      cadesplugin.get_extension_id(ext_id_loaded_callback);
      var CurrentPluginVersion = yield oAbout.PluginVersion;
      versionStruct.plugin = yield CurrentPluginVersion.toString();
      document.getElementById('PlugInVersionTxt').innerHTML = escapeHtml("Версия плагина: " + (versionStruct.plugin));
      setStateForPlugin(Colors.SUCCESS, "Плагин загружен");
      var ver = yield oAbout.CSPVersion("", 80);
      versionStruct.csp = (yield ver.MajorVersion) + "." + (yield ver.MinorVersion) + "." + (yield ver.BuildVersion);
      document.getElementById('CSPVersionTxt').innerHTML = escapeHtml("Версия криптопровайдера: " + versionStruct.csp);
      try {
          var sCSPName = yield oAbout.CSPName(80);
          setStateForCSP(Colors.SUCCESS, "Криптопровайдер загружен");
          document.getElementById('CSPNameTxt').innerHTML = escapeHtml("Криптопровайдер: " + sCSPName);
      }
      catch (err) { }
      try {
          var oLicense = yield cadesplugin.CreateObjectAsync("CAdESCOM.CPLicense");
          var cspValidTo = escapeHtml(yield oLicense.ValidTo());
          var tspValidTo = escapeHtml(yield oLicense.ValidTo(cadesplugin.CADESCOM_PRODUCT_TSP));
          var ocspValidTo = escapeHtml(yield oLicense.ValidTo(cadesplugin.CADESCOM_PRODUCT_OCSP));
          try {
              if (!(yield oLicense.IsValid(cadesplugin.CADESCOM_PRODUCT_CSP))) {
                  cspValidTo = addLicensePrompt(cadesplugin.CADESCOM_PRODUCT_CSP, cspValidTo);
              }
              if (!(yield oLicense.IsValid(cadesplugin.CADESCOM_PRODUCT_TSP))) {
                  tspValidTo = addLicensePrompt(cadesplugin.CADESCOM_PRODUCT_TSP, tspValidTo);
              }
              if (!(yield oLicense.IsValid(cadesplugin.CADESCOM_PRODUCT_OCSP))) {
                  ocspValidTo = addLicensePrompt(cadesplugin.CADESCOM_PRODUCT_OCSP, ocspValidTo);
              }
          }
          catch (err) { }
          cspValidTo += "<br/>\tДата первой установки: " +
              (yield oLicense.FirstInstallDate(cadesplugin.CADESCOM_PRODUCT_CSP));
          cspValidTo += "<br/>\tТип лицензии: " +
              (yield oLicense.Type(cadesplugin.CADESCOM_PRODUCT_CSP));
          tspValidTo += "<br/>\tДата первой установки: " +
              (yield oLicense.FirstInstallDate(cadesplugin.CADESCOM_PRODUCT_TSP));
          tspValidTo += "<br/>\tТип лицензии: " +
              (yield oLicense.Type(cadesplugin.CADESCOM_PRODUCT_TSP));
          ocspValidTo += "<br/>\tДата первой установки: " +
              (yield oLicense.FirstInstallDate(cadesplugin.CADESCOM_PRODUCT_OCSP));
          ocspValidTo += "<br/>\tТип лицензии: " +
              (yield oLicense.Type(cadesplugin.CADESCOM_PRODUCT_OCSP));

          document.getElementById('CspLicense').innerHTML = "Лицензия CSP: " + cspValidTo;
          if (bShowTspLicenseInfo) {
              document.getElementById('TspLicense').innerHTML = "Лицензия TSP: " + tspValidTo;
          }
          if (bShowOcspLicenseInfo) {
              document.getElementById('OcspLicense').innerHTML = "Лицензия OCSP: " + ocspValidTo;
          }
      }
      catch (err) { }
      CheckUpdateServer(CurrentPluginVersion, versionStruct);
      // if (location.pathname.indexOf("symalgo_sample.html")>=0) {
      //     FillCertList_Async('CertListBox1', 'CertListBox2');
      //  }else if (location.pathname.indexOf("cades_root_export.html")>=0) {
      //     FillCertList_Async('CertListBox', undefined, true);
      // } else if (location.pathname.indexOf("verify.html") >= 0) {
      //     return;
      // } else {
          FillCertList_Async('CertListBox');
      // }
  }); //cadesplugin.async_spawn
}


function Common_CheckForPlugIn() {
//   cadesplugin.set_log_level(cadesplugin.LOG_LEVEL_DEBUG);
  var canAsync = !!cadesplugin.CreateObjectAsync;
  return CheckForPlugIn_Async();

}

function extensionLoadedCallback() {
  setStateForExtension(Colors.SUCCESS, "Расширение загружено");
  window.cadesplugin_extension_loaded = true;
}

function load_extension() {

  setStateForExtension(extImg, extTxt);

   setStateForPlugin(plgImg, plgTxt);
  
   setStateForCSP(cspImg, cspTxt);
  
   setStateForObjects(objImg, objTxt);
    setInnerText("Platform", "Платформа: " + platformCheck());
    setInnerText("UserAgent", "UserAgent: " + navigator.userAgent);
    var canPromise = !!window.Promise;
    if (isEdge()) {
        setStateForExtension(Colors.ERROR, "Расширение не загружено");
        ShowEdgeNotSupported();
        // console.log("Расширение не загружено")
      } else {
        if (canPromise) {
          cadesplugin.then(
            function () {
              
              Common_CheckForPlugIn();
              
              
            },
            function (error) {
              
              if (window.cadesplugin_extension_loaded) {
                setStateForPlugin(Colors.FAIL, error);
              }
              if (isYandex()) {
                var fileref = document.createElement('script');
                fileref.setAttribute("type", "text/javascript");
                fileref.setAttribute("src", "chrome-extension://iifchhfnnmpdbibifmljnfjhpififfog/nmcades_plugin_api.js");
                fileref.onload = function () {
                  try {
                    window.addEventListener('load', function () {
                      cadesplugin.get_extension_id(function (ext_id) {
                        if (ext_id === chrome_ext_id) {
                          setStateForExtension(Colors.UPDATE,
                            "Для работы в Yandex Browser требуется расширение из Opera Store");
                          extUrl = "https://addons.opera.com/en/extensions/details/cryptopro-extension-for-cades-browser-plug-in";
                          setInnerText("ExtensionSolution", "<a href='" + extUrl + "'>Загрузить</a>", true);
                        }
                      });
                    })
                  }
                  catch (err) { }
                };
                document.getElementsByTagName("head")[0].appendChild(fileref);
              }
            }
          );
        } else {
          window.addEventListener(
            "message",
            function (event) {
              if (event.data == "cadesplugin_loaded") {
                CheckForPlugIn_NPAPI();
              } else if (event.data == "cadesplugin_load_error") {
                if (window.cadesplugin_extension_loaded) {
                  setStateForPlugin(Colors.FAIL, "Плагин не загружен");
                }
              }
            },
            false
          );
          window.postMessage("cadesplugin_echo_request", "*");
        }
      }

}

window.onload = () => {
        // finalLoad()
        const btn = document.getElementById('mainButton')
        btn.addEventListener('click', ()=>{
            window.cadesplugin_extension_loaded_callback = extensionLoadedCallback
              
              createCadesplugin()
              load_extension()

             

        })
    }