# Como um site vira modelo de prévia

Cada modelo fica em `_modelos/<id>/` e é preenchido pelo `_modelos/gerar.py`
com a logo e os dados de uma escola nova. A prévia gerada vai para `previas/<slug>/`.
O objetivo é a prévia sair em poucos minutos e parecer feita sob medida para a escola.

## Arquivos do modelo
- `index.html` (e outras páginas .html, se o site tiver), `img/` com as imagens, e `modelo.json`:
  `{"id": "...", "nome": "Modelo Rei Leão", "descricao": "uma linha: estilo e para que escola combina", "baseado_em": "previas/..."}`
- Sem arquivos `logo.*` na pasta: o gerador grava `logo.png` com a logo da escola nova.
- Nada de imagens em data: URI dentro do HTML. Extraia para `img/` (webp, até ~250 KB cada).

## Campos trocáveis (escreva `{{campo}}` no HTML)
| campo | exemplo |
|---|---|
| `{{nome}}` | Creche Escola Pinguinho de Gente |
| `{{nome_curto}}` | Pinguinho de Gente |
| `{{whatsapp_fmt}}` | (21) 99999-0000 |
| `{{wa_link}}` | link wa.me pronto, com mensagem (use em TODOS os botões de contato/matrícula/agendar) |
| `{{telefone_fmt}}` / `{{telefone}}` | (21) 3333-0000 / +552133330000 (para tel:) |
| `{{endereco}}`, `{{bairro}}`, `{{cidade}}`, `{{endereco_completo}}` | R. Exemplo, 123 / Bangu / Rio de Janeiro / tudo junto |
| `{{maps_q}}` | já codificado para URL: use em `https://maps.google.com/maps?q={{maps_q}}&output=embed` |
| `{{instagram}}` | usuário sem @ |
| `{{horario}}` | Segunda a sexta, das 7h às 19h |
| `{{nota}}`, `{{avaliacoes}}` | 4,8 / 32 (Google) |
| `{{ano}}` | 2026 |

Campos que podem faltar: marque o elemento que depende deles com `data-opcional="campo"`
(pode listar vários: `data-opcional="endereco bairro"`). Se o campo vier vazio, o gerador
apaga o elemento inteiro. Obrigatório sempre: `nome` e `whatsapp`. Opcionais: todo o resto.
Ex.: o mapa e a linha de endereço → `data-opcional="endereco"`; selo de nota do Google →
`data-opcional="nota avaliacoes"`; link do Instagram → `data-opcional="instagram"`.

## Logo
Todo lugar onde aparecia a logo/nome desenhado da escola antiga vira
`<img src="logo.png" alt="{{nome}}" class="...">` (em subpáginas também `logo.png`, mesma pasta).
A logo nova pode ser larga, quadrada ou redonda: o CSS precisa caber qualquer proporção
(`max-height` + `width:auto`, `object-fit:contain`), sem selo/fundo atrás que dependa da logo antiga.
Se o design tinha um mascote/selo próprio da escola antiga (o leão, o girassol, o globo...), tire
ou troque por um elemento neutro.

## Cores
O site passa a usar as cores da logo nova. No começo do `<style>` coloque exatamente:

```
/*MARCA*/:root{--marca-1:#f0bd2b;--marca-1-forte:#8a6a00;--marca-1-ink:#1b1b1b;--marca-1-claro:#fdf3d6;--marca-1-escuro:#9c7a1c;
--marca-2:#1352bf;--marca-2-forte:#1352bf;--marca-2-ink:#ffffff;--marca-2-claro:#d4e0f4;--marca-2-escuro:#0c357c;
--marca-3:#f42031;--marca-3-forte:#c8101f;--marca-3-ink:#ffffff;--marca-3-claro:#fdd6d9;--marca-3-escuro:#9e1520;}/*/MARCA*/
```
(valores de exemplo; o gerador substitui o bloco inteiro). Depois, as cores de identidade do
site (botões, títulos coloridos, faixas, ícones, rodapé, destaques) passam a sair dessas variáveis.
`--marca-1` é a cor mais forte da logo, `--marca-2` e `--marca-3` as seguintes.
Regras de legibilidade, porque a cor pode ser qualquer uma (até amarelo-claro):
- texto sobre fundo `--marca-N` usa `--marca-N-ink`;
- texto colorido sobre fundo claro usa `--marca-N-forte`;
- fundos suaves usam `--marca-N-claro`; rodapé/faixas escuras podem usar `--marca-N-escuro` com texto branco.
Cores neutras (fundo, texto corrido) podem continuar fixas. Mantenha o tema que o site já tinha
(claro/escuro) e não quebre o modo escuro se existir.

## Conteúdo
- Nada da escola antiga pode sobrar: nome, telefone, endereço, Instagram, nota, unidades,
  números do Censo, "Tia Rafa", "Tijuca", "Bangu", etc. Busque no HTML e nas imagens.
- Textos viram genéricos e bons para qualquer creche/escola infantil (acolhimento, rotina,
  segurança, alimentação, desenvolvimento, berçário/maternal/pré). Sem inventar fatos verificáveis
  (prêmios, anos de história, número de alunos, metragem, certificações). Use `{{nome_curto}}` no texto
  onde fizer sentido para parecer sob medida.
- Mantenha o layout, as seções, as animações e a qualidade visual do site original. É o mesmo site,
  só que preenchível.
- Mantenha `<meta name="robots" content="noindex">` e a assinatura no rodapé:
  `Prévia criada pela <a href="https://levytikus.github.io/B2B-novo/" target="_blank" rel="noopener">Business 2 Brothers</a>`.
- `<title>{{nome}}</title>` (pode ter complemento: `{{nome}} | Creche e pré-escola`).

## Imagens
Fotos e ilustrações genéricas de crianças, salas e atividades podem ficar.
Imagem com nome, logo, mascote ou tema específico da escola antiga (leão, girassol, globo/mundo,
fachada com placa) precisa ser trocada por uma imagem neutra no mesmo estilo, gerada no Canva.
Padrão de qualidade alto: nada de clip-art pobre ou ícone genérico de banco.

## Teste
```
python3 _modelos/gerar.py --modelo <id> --logo <logo de teste> --dados _modelos/teste.json --saida /tmp/teste-<id>
```
Abra o resultado num navegador headless (playwright) em 1280px e 390px, e confira: logo nova
aparece e cabe, cores trocaram, nada da escola antiga, nenhum `{{` sobrando, nada estourando.
Teste com duas logos de cores bem diferentes (ex.: uma amarela/azul/vermelha e uma verde escura).
