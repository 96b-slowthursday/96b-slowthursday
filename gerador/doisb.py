# A 2B em células de código, porte do doisB() do shader ("versão 3", 24/09):
# só o tom, em quatro glifos (ponto, traço, cruz, quadrado), e uma faixa que
# desce decodificando a cada 8 s, trocando glifos por dentro. Mais o glitch raro.
# A imagem é a mesma do Terminal: ~/.claude/terminal-yorha/2b-codigo.png,
# copiada para gerador/2b-codigo.png.

import math
import re
from pathlib import Path

from PIL import Image

from comum import *
from texto import texto

W = H = 480
IMAGEM = Path(__file__).resolve().parent / "2b-codigo.png"
CEL = 6                      # px inteiros, como no shader (round(0,55u))
ALT = 414                    # altura da caixa da imagem
PERIODO = 8.0                # a faixa desce a cada 8 s
QUADROS = 2                  # quadros de embaralhamento, trocados a 14 por segundo


def amostra(img, u, v):
    """Leitura bilinear em uv, como o SampleLevel do shader."""
    w, h = img.size
    x, y = u * w - 0.5, v * h - 0.5
    x0, y0 = math.floor(x), math.floor(y)
    fx, fy = x - x0, y - y0
    p = lambda i, j: img.getpixel((min(w - 1, max(0, i)), min(h - 1, max(0, j)))) / 255
    return ((p(x0, y0) * (1 - fx) + p(x0 + 1, y0) * fx) * (1 - fy)
            + (p(x0, y0 + 1) * (1 - fx) + p(x0 + 1, y0 + 1) * fx) * fy)


def glifo(Lg, x, y):
    """Subcaminho do glifo da célula com canto em (x, y)."""
    c = CEL / 2
    cx, cy = x + c, y + c
    b = 0.36 * CEL
    if 0.06 <= Lg < 0.28:
        return f"M{n(cx - 0.8)} {n(cy - 0.8)}h1.6v1.6h-1.6z"
    if 0.28 <= Lg < 0.48:
        return f"M{n(cx - b)} {n(cy - 0.75)}h{n(2 * b)}v1.5h{n(-2 * b)}z"
    if 0.48 <= Lg < 0.68:
        return (f"M{n(cx - b)} {n(cy - 0.75)}h{n(2 * b)}v1.5h{n(-2 * b)}z"
                f"M{n(cx - 0.75)} {n(cy - b)}h1.5v{n(2 * b)}h-1.5z")
    if Lg >= 0.68:
        s = 0.38 * CEL
        return f"M{n(cx - s)} {n(cy - s)}h{n(2 * s)}v{n(2 * s)}h{n(-2 * s)}z"
    return ""


def relativo(d):
    """Troca os M absolutos por m relativos: todo subcaminho fecha com z e volta
    ao próprio início, então o próximo anda só a diferença. Corta ~40% do peso."""
    partes = re.split(r"M(-?[\d.]+) (-?[\d.]+)", d)
    saida, ant = [], None
    for k in range(1, len(partes), 3):
        x, y = float(partes[k]), float(partes[k + 1])
        saida.append(f"M{n(x)} {n(y)}" if ant is None else f"m{n(x - ant[0])} {n(y - ant[1])}")
        saida.append(partes[k + 2])
        ant = (x, y)
    return "".join(saida)


def tom(L, extra=0.0):
    base = mistura(tuple(c * 2 for c in SEPIA), CREME, min(1.0, L * 1.2))
    return cor(base, 0.45 + 0.60 * L + extra)


def svg():
    img = Image.open(IMAGEM).convert("L")
    iw, ih = img.size
    larg = round(ALT * iw / ih)
    cols, linhas = larg // CEL, ALT // CEL
    larg, alt = cols * CEL, linhas * CEL
    ox, oy = (W - larg) // 2 + 10, H - alt - 22

    # células agrupadas por tom (16 degraus): um path por cor, em vez de milhares
    base, embaralho = {}, [dict() for _ in range(QUADROS)]
    fundos = [[] for _ in range(QUADROS)]
    soltas = []
    for j in range(linhas):
        for i in range(cols):
            L = amostra(img, (i + 0.5) / cols, (j + 0.5) / linhas)
            x, y = ox + i * CEL, oy + j * CEL
            q = round(L * 16) / 16
            g = glifo(L, x, y)
            if g:
                base.setdefault(q, []).append(g)
            if L > 0.08:
                for k in range(QUADROS):
                    if hash21(i + 31.0 * k, j + 17.0) > 0.68:
                        Lg = hash21(i * 1.7 + k, j * 1.7 + 5.0)
                        fundos[k].append(f"M{x} {y}h{CEL}v{CEL}h-{CEL}z")
                        embaralho[k].setdefault(q, []).append(glifo(Lg, x, y))
                if hash21(i + 0.37, j + 91.0) > 0.994:
                    soltas.append((i, j, x, y, L, q))

    def camada(grupos, extra=0.0):
        return "".join(f'<path d="{relativo("".join(d))}" fill="{tom(q, extra)}"/>' for q, d in sorted(grupos.items()) if d)

    # a faixa: gaussiana de largura 1/14 da altura, descendo de -0,15 a 1,15
    sig = alt / 14
    paradas = "".join(f'<stop offset="{k / 12:.3f}" stop-color="#fff" stop-opacity="{math.exp(-((k / 12 - 0.5) * 6) ** 2):.3f}"/>'
                      for k in range(13))
    hf = sig * 6
    y0, y1 = oy - 0.15 * alt - hf / 2, oy + 1.15 * alt - hf / 2
    anima = lambda alt_rect: (f'<animate attributeName="y" from="{n(y0 + (hf - alt_rect) / 2)}" '
                              f'to="{n(y1 + (hf - alt_rect) / 2)}" dur="{PERIODO}s" repeatCount="indefinite"/>')
    dura = 2 * 0.084 * alt      # onde faixa > 0,25: lá dentro as células trocam
    defs = (f'<linearGradient id="gfaixa" x1="0" y1="0" x2="0" y2="1">{paradas}</linearGradient>'
            f'<mask id="faixa" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<rect x="0" width="{W}" height="{n(hf)}" fill="url(#gfaixa)">{anima(hf)}</rect></mask>'
            f'<mask id="nucleo" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<rect x="0" width="{W}" height="{n(dura)}" fill="#fff">{anima(dura)}</rect></mask>')

    quadros = []
    for k in range(QUADROS):
        vals = ";".join("1" if m == k else "0" for m in range(QUADROS))
        quadros.append(f'<g opacity="{1 if k == 0 else 0}">'
                       f'<animate attributeName="opacity" values="{vals}" dur="{QUADROS / 14:.4f}s" '
                       f'calcMode="discrete" repeatCount="indefinite"/>'
                       f'<path d="{relativo("".join(fundos[k]))}" fill="{FUNDO}"/>{camada(embaralho[k], 0.45)}</g>')

    # glitch solto: poucas células que piscam outro glifo, cada uma no seu tempo
    raras = []
    for i, j, x, y, L, q in soltas:
        Lg = hash21(i * 3.1, j * 0.7)
        periodo = 9 + 14 * hash21(i, j + 2.0)
        ini = periodo * hash21(j, i + 4.0)
        raras.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" keyTimes="0;0.01;0.04" '
                     f'calcMode="discrete" dur="{periodo:.2f}s" begin="{-ini:.2f}s" repeatCount="indefinite"/>'
                     f'<rect x="{x}" y="{y}" width="{CEL}" height="{CEL}" fill="{FUNDO}"/>'
                     f'<path d="{glifo(Lg, x, y)}" fill="{tom(q, 0.3)}"/></g>')

    rotulo = (texto("VISUAL ARCHIVE", 34, 44, 11, cor(CREME, 0.75), "Regular", espaco=2.2)
              + texto("// 2B · DECODING", 34, 60, 9, cor(GRAFITE, 1.6), "Regular", espaco=1.6))
    # dentro da faixa, a mesma camada mais clara (filtro, não cópia: metade do peso)
    defs += (f'<g id="base">{camada(base)}</g>'
             '<filter id="clareia"><feComponentTransfer><feFuncR type="linear" slope="1.7"/>'
             '<feFuncG type="linear" slope="1.7"/><feFuncB type="linear" slope="1.7"/></feComponentTransfer></filter>')
    corpo = (rotulo + '<use href="#base"/>'
             + '<g mask="url(#faixa)"><use href="#base" filter="url(#clareia)"/></g>'
             + f'<g mask="url(#nucleo)">{"".join(quadros)}</g>'
             + "".join(raras))
    return cartao(W, H, "2B em células de código", corpo, defs)


if __name__ == "__main__":
    saida = Path(__file__).resolve().parent.parent / "assets" / "2b.svg"
    saida.write_text(svg(), encoding="utf-8")
    print(f"{saida}  ({saida.stat().st_size // 1024} KB)")
