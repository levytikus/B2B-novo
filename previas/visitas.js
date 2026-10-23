/*
  Contador de visitas das prévias da Business 2 Brothers.
  Registra no banco (Supabase, esquema b2b) cada abertura de uma prévia, com data e hora.
  O Painel B2B mostra esses registros na aba Sites.

  - Não guarda nome, IP nem nada pessoal: só a prévia, a hora e o tipo de aparelho.
  - Aberturas repetidas da mesma pessoa em menos de 30 minutos contam uma vez só.
  - Quem abre uma prévia com ?equipe=1 no link fica marcado como equipe naquele
    navegador e nunca mais é contado (os botões do Painel já fazem isso).
    Para desmarcar: abrir qualquer prévia com ?equipe=0.
  - ?r=algo no link fica gravado como origem (ex.: ?r=whatsapp).
*/
(function () {
  var URL_BANCO = "https://rnmheimtltpowpjadugu.supabase.co/rest/v1/rpc/b2b_registrar_visita";
  var CHAVE = "sb_publishable_bi4S4LPNPDHhVcpZZVkESg_iVeEzreY";
  var JANELA_MS = 30 * 60 * 1000;

  try {
    var m = location.pathname.match(/\/previas\/([a-z0-9][a-z0-9-]{1,80})(\/|$)/);
    if (!m) return;
    var previa = m[1];
    var params = new URLSearchParams(location.search);

    var marca = params.get("equipe");
    if (marca !== null) {
      try {
        if (marca === "0") localStorage.removeItem("b2b-equipe");
        else localStorage.setItem("b2b-equipe", "1");
      } catch (e) {}
      params.delete("equipe");
      var resto = params.toString();
      history.replaceState(null, "", location.pathname + (resto ? "?" + resto : "") + location.hash);
      if (marca !== "0") return;
    }

    try { if (localStorage.getItem("b2b-equipe") === "1") return; } catch (e) {}
    if (navigator.webdriver) return;
    if (/bot|crawl|spider|slurp|preview|whatsapp|facebookexternalhit|headless|lighthouse/i.test(navigator.userAgent)) return;

    var chaveUltima = "b2b-visita-" + previa;
    try {
      var ultima = Number(localStorage.getItem(chaveUltima) || 0);
      if (Date.now() - ultima < JANELA_MS) return;
    } catch (e) {}

    var toque = window.matchMedia && matchMedia("(pointer: coarse)").matches;
    var largura = Math.min(screen.width || 0, screen.height || 0) || window.innerWidth;
    var dispositivo = !toque ? "computador" : (largura >= 700 ? "tablet" : "celular");

    var enviar = function () {
      try { localStorage.setItem(chaveUltima, String(Date.now())); } catch (e) {}
      fetch(URL_BANCO, {
        method: "POST",
        keepalive: true,
        headers: { "apikey": CHAVE, "Content-Type": "application/json" },
        body: JSON.stringify({ p_previa: previa, p_ref: params.get("r"), p_dispositivo: dispositivo })
      }).catch(function () {});
    };

    // Só conta quando a página aparece de fato na tela (evita pré-carregamentos).
    if (document.visibilityState === "visible") enviar();
    else document.addEventListener("visibilitychange", function aoVer() {
      if (document.visibilityState !== "visible") return;
      document.removeEventListener("visibilitychange", aoVer);
      enviar();
    });
  } catch (e) {}
})();
