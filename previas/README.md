# Prévias de sites para prospecção

Cada pasta aqui é uma prévia de site feita para uma escola do Painel B2B, para o Nathan mandar junto da mensagem.

- Endereço: `https://sites.business2brothers.com/previas/<id-da-escola>/`
- O nome da pasta é o mesmo id da escola no painel (por exemplo `creche-escola-mundo-baby`).
- Cada prévia é um `index.html` só, com estilos no próprio arquivo, `<meta name="robots" content="noindex">` e uma faixa discreta no rodapé: "Prévia criada pela Business 2 Brothers".
- Não mexa em nada fora desta pasta: o resto do repositório é o site da agência.
- Toda prévia carrega `/previas/visitas.js`, o contador de visitas: cada abertura vai para o banco com data e hora e aparece no Painel B2B, aba Sites. O `gerar.py` já coloca o contador sozinho; numa prévia feita à mão, inclua `<script src="/previas/visitas.js" defer></script>` antes do `</body>`.
- Para abrir uma prévia sem ser contado, use o link com `?equipe=1` (basta uma vez por navegador; os botões do Painel já fazem isso). `?equipe=0` desfaz.
