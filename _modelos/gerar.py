#!/usr/bin/env python3
"""Gera uma prévia de site a partir de um modelo, uma logo e os dados da escola.

Uso:
  python3 _modelos/gerar.py --modelo rei-leao --logo logo.png --dados dados.json [--slug nome-da-escola]

dados.json (só "nome" e "whatsapp" são obrigatórios):
  {
    "nome": "Creche Escola Pinguinho de Gente",
    "nome_curto": "Pinguinho de Gente",        # opcional (padrão: nome sem "Creche", "Escola"...)
    "whatsapp": "21 99999-0000",               # celular com DDD
    "telefone": "21 3333-0000",                # opcional (fixo)
    "endereco": "R. Exemplo, 123",              # opcional
    "bairro": "Bangu", "cidade": "Rio de Janeiro",
    "instagram": "pinguinhodegente",           # opcional, sem @
    "horario": "Segunda a sexta, das 7h às 19h",  # opcional
    "nota": "4,8", "avaliacoes": "32",         # opcional (Google)
    "cores": ["#e63946", "#1d3557", "#f1c40f"]  # opcional: força as cores em vez de tirar da logo
  }

Saída: previas/<slug>/ pronto para publicar no GitHub Pages.
Os modelos ficam em _modelos/<id>/ (a pasta com "_" não é publicada pelo GitHub Pages).
"""
import argparse, colorsys, json, re, shutil, sys, unicodedata, datetime
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "_modelos"
PREVIAS = RAIZ / "previas"
BASE_URL = "https://levytikus.github.io/B2B-novo/previas/"


# ---------- utilidades ----------
def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def digits(s):
    return re.sub(r"\D", "", s or "")


def fmt_tel(s):
    d = digits(s)
    if d.startswith("55") and len(d) in (12, 13):
        d = d[2:]
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return s or ""


def wa_num(s):
    d = digits(s)
    if not d:
        return ""
    return d if d.startswith("55") and len(d) >= 12 else "55" + d


def nome_curto(nome):
    s = re.sub(r"^(creche\s+e\s+escola|creche[\s-]+escola|escola[\s-]+creche|centro\s+educacional|jardim\s+escola|"
               r"espa[cç]o\s+infantil|creche|escola|col[eé]gio|ber[cç][aá]rio)\s+(infantil\s+)?", "", nome.strip(), flags=re.I)
    return s or nome


# ---------- cores ----------
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in c)


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contraste(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def escurecer_ate(c, alvo=4.5, fundo=(255, 255, 255)):
    """Escurece a cor até dar contraste com o fundo (para texto/botão)."""
    out = c
    for _ in range(30):
        if contraste(out, fundo) >= alvo:
            break
        out = mix(out, (0, 0, 0), 0.08)
    return out


def cores_da_logo(path, n=3):
    im = Image.open(path).convert("RGBA")
    im.thumbnail((240, 240))
    dados_px = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
    px = [p[:3] for p in dados_px if p[3] > 200]
    if not px:
        return ["#ef4f86", "#3f9df0", "#f5a623"]
    # agrupa por matiz (12 faixas) + faixa de cinza/escuro, pondera por saturação
    faixas = {}
    for c in px:
        h, s, v = colorsys.rgb_to_hsv(*(x / 255 for x in c))
        if v < 0.12 or (s < 0.22) or (v > 0.95 and s < 0.12):
            continue                     # preto, branco, cinza
        k = int(h * 12) % 12
        f = faixas.setdefault(k, [0, 0, 0, 0, 0.0])
        peso = 0.35 + s * v
        f[0] += c[0] * peso; f[1] += c[1] * peso; f[2] += c[2] * peso; f[3] += peso; f[4] += 1
    cand = []
    for k, (r, g, b, w, cnt) in faixas.items():
        if cnt < len(px) * 0.004:
            continue
        c = (r / w, g / w, b / w)
        cand.append((w, k, c))
    cand.sort(reverse=True)
    escolhidas = []
    for _, k, c in cand:
        if all(min(abs(k - k2), 12 - abs(k - k2)) >= 1 for k2, _ in escolhidas):
            escolhidas.append((k, c))
        if len(escolhidas) == n:
            break
    cores = [rgb2hex(c) for _, c in escolhidas]
    # completa com variações se a logo tiver poucas cores
    padrao = ["#f5a623", "#3f9df0", "#7cbf2f"]
    while len(cores) < n:
        if cores:
            h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in hex2rgb(cores[0])))
            h2 = (h + (0.5 if len(cores) == 1 else 0.15)) % 1
            cores.append(rgb2hex([v * 255 for v in colorsys.hls_to_rgb(h2, min(max(l, .45), .6), max(s, .6))]))
        else:
            cores.append(padrao[len(cores)])
    return cores


def bloco_cores(cores):
    linhas = []
    for i, h in enumerate(cores[:3], 1):
        c = hex2rgb(h)
        forte = escurecer_ate(c, 4.5)              # versão segura para texto sobre branco
        ink = (255, 255, 255) if contraste((255, 255, 255), c) >= contraste((27, 27, 27), c) else (27, 27, 27)
        linhas += [
            f"--marca-{i}:{h};",
            f"--marca-{i}-forte:{rgb2hex(forte)};",
            f"--marca-{i}-ink:{rgb2hex(ink)};",
            f"--marca-{i}-claro:{rgb2hex(mix(c, (255, 255, 255), .82))};",
            f"--marca-{i}-escuro:{rgb2hex(mix(c, (0, 0, 0), .35))};",
        ]
    return "/*MARCA*/:root{" + "".join(linhas) + "}/*/MARCA*/"


# ---------- montagem ----------
def campos(d):
    nome = d["nome"].strip()
    wa = wa_num(d.get("whatsapp"))
    end_full = ", ".join(x for x in [d.get("endereco"), d.get("bairro"), d.get("cidade") or "Rio de Janeiro"] if x)
    msg = f"Olá! Vi o site da {nome} e gostaria de mais informações."
    f = {
        "nome": nome,
        "nome_curto": d.get("nome_curto") or nome_curto(nome),
        "whatsapp": wa,
        "whatsapp_fmt": fmt_tel(d.get("whatsapp")),
        "wa_link": f"https://wa.me/{wa}?text={quote(msg)}" if wa else "#contato",
        "telefone_fmt": fmt_tel(d.get("telefone") or d.get("whatsapp")),
        "telefone": "+" + wa_num(d.get("telefone") or d.get("whatsapp")),
        "endereco": d.get("endereco", ""),
        "bairro": d.get("bairro", ""),
        "cidade": d.get("cidade") or "Rio de Janeiro",
        "endereco_completo": end_full,
        "maps_q": quote(f"{nome}, {end_full}"),
        "instagram": (d.get("instagram") or "").lstrip("@").strip("/"),
        "horario": d.get("horario", ""),
        "nota": d.get("nota", ""),
        "avaliacoes": d.get("avaliacoes", ""),
        "ano": str(datetime.date.today().year),
    }
    return f


def preencher(html, f):
    soup = BeautifulSoup(html, "html.parser")
    # remove blocos opcionais sem dado: data-opcional="instagram endereco"
    for el in soup.select("[data-opcional]"):
        if getattr(el, "decomposed", False) or el.attrs is None:
            continue
        need = (el.get("data-opcional") or "").split()
        if any(not f.get(k) for k in need):
            el.decompose()
    for el in soup.select("[data-opcional]"):
        del el["data-opcional"]
    html = str(soup)

    def rep(m):
        k = m.group(1)
        return str(f.get(k, m.group(0)))
    html = re.sub(r"\{\{\s*([a-z_]+)\s*\}\}", rep, html)
    sobrou = re.findall(r"\{\{\s*[a-z_]+\s*\}\}", html)
    if sobrou:
        print("AVISO: campos sem valor:", sorted(set(sobrou)), file=sys.stderr)
    return html


def gerar(modelo, logo, dados, slug=None, saida=None):
    src = MODELOS / modelo
    if not (src / "index.html").exists():
        sys.exit(f"Modelo '{modelo}' não existe. Modelos: {', '.join(listar())}")
    f = campos(dados)
    slug = slug or slugify(f["nome"])
    dst = Path(saida) if saida else PREVIAS / slug
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("modelo.json", "*.md", "logo.*"))
    # logo
    im = Image.open(logo)
    im = im.convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    im.thumbnail((800, 800))
    im.save(dst / "logo.png", optimize=True)
    cores = dados.get("cores") or cores_da_logo(logo)
    bloco = bloco_cores(cores)
    for page in dst.rglob("*.html"):
        html = page.read_text(encoding="utf-8")
        html = re.sub(r"/\*MARCA\*/.*?/\*/MARCA\*/", lambda m: bloco, html, flags=re.S)
        html = preencher(html, f)
        page.write_text(html, encoding="utf-8")
    url = BASE_URL + slug + "/"
    return {"slug": slug, "url": url, "pasta": str(dst), "cores": cores}


def listar():
    return sorted(p.name for p in MODELOS.iterdir() if (p / "index.html").exists())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo")
    ap.add_argument("--logo")
    ap.add_argument("--dados")
    ap.add_argument("--slug")
    ap.add_argument("--saida")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--cores", help="só mostra as cores tiradas da logo")
    a = ap.parse_args()
    if a.listar:
        for m in listar():
            j = MODELOS / m / "modelo.json"
            info = json.loads(j.read_text()) if j.exists() else {}
            print(f"{m}: {info.get('descricao', '')}")
        sys.exit()
    if a.cores:
        print(cores_da_logo(a.cores))
        sys.exit()
    dados = json.loads(Path(a.dados).read_text(encoding="utf-8"))
    print(json.dumps(gerar(a.modelo, a.logo, dados, a.slug, a.saida), ensure_ascii=False, indent=2))
