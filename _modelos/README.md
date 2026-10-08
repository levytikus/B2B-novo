# Modelos de prévia

Pasta não publicada (o GitHub Pages ignora pastas com "_").
Regras para criar um modelo: CONTRATO.md. Para gerar uma prévia:

    python3 _modelos/gerar.py --listar
    python3 _modelos/gerar.py --modelo rei-leao --logo logo.png --dados dados.json

A prévia sai em previas/<slug-do-nome>/. Depois é só commit + push.
