# Cabeçalho do perfil: a flor de mira (emblema do prompt), a designação 96B
# com o glitch de faixas do shader, e um boot no jeito do BUNKER OS do
# PowerShell, que digita uma vez quando a página abre. Os valores do boot
# vêm do perfil.py (tempo do Entreato, velocidade do dia, data da sincronia).

import math

from comum import *
from texto import caminho, largura, texto

W, H = 960, 240


def regua(y):
    x0, x1 = W * 0.18, W * 0.62
    marcas = "".join(f"M{n(x)} {n(y)}v{n(4 if k % 5 else 7)}" for k, x in enumerate(
        x0 + i * U for i in range(int((x1 - x0) / U) + 1)))
    return (f'<path d="M{n(x0)} {n(y)}H{n(x1)}{marcas}" stroke="{cor(GRAFITE)}" '
            f'stroke-opacity="0.8" stroke-width="1" fill="none"/>')


def brilho_def(id_, cx, cy, raio, periodo, a, b):
    # faixa de brilho na diagonal (faixaBrilho do shader), em coordenadas de tela
    paradas = []
    for k in range(9):
        t = -0.8 + 1.6 * k / 8
        paradas.append(f'<stop offset="{k / 8:.3f}" stop-color="{cor(mistura(a, b, math.exp(-t * t * 10)))}"/>')
    d = 0.8 * raio
    return (f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" x1="{n(cx - d)}" y1="{n(cy + d)}" '
            f'x2="{n(cx + d)}" y2="{n(cy - d)}">{"".join(paradas)}'
            f'<animateTransform attributeName="gradientTransform" type="translate" '
            f'values="{n(-2 * raio)} {n(2 * raio)};{n(2 * raio)} {n(-2 * raio)}" dur="{periodo}s" repeatCount="indefinite"/>'
            f'</linearGradient>')


def emblema(cx, cy, r):
    # emblemaSDF com espessura 0,075: anel, a diagonal da mira e quatro pétalas
    # vazadas no miolo
    k = 1 / math.sqrt(2)
    d = (f"M{n(cx + 0.58 * r * k)} {n(cy - 0.58 * r * k)}L{n(cx + 1.02 * r * k)} {n(cy - 1.02 * r * k)}"
         f"M{n(cx - 0.58 * r * k)} {n(cy + 0.58 * r * k)}L{n(cx - 1.02 * r * k)} {n(cy + 1.02 * r * k)}")
    petalas = "".join(
        f'<ellipse cx="{n(cx + px * r)}" cy="{n(cy + py * r)}" rx="{n(rx * r)}" ry="{n(ry * r)}"/>'
        for px, py, rx, ry in ((0, -0.36, 0.14, 0.30), (0, 0.36, 0.14, 0.30), (-0.36, 0, 0.30, 0.14), (0.36, 0, 0.30, 0.14)))
    defs = (brilho_def("brilho-emblema", cx, cy, r, 3.4, tuple(c * 0.9 for c in DOURADO), tuple(min(255, c * 1.1) for c in CREME))
            + f'<mask id="miolo"><rect width="{W}" height="{H}" fill="#fff"/><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(0.09 * r)}"/></mask>')
    corpo = (f'<g fill="url(#brilho-emblema)" stroke="url(#brilho-emblema)">'
             f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(0.84 * r)}" fill="none" stroke-width="{n(0.15 * r)}"/>'
             f'<path d="{d}" fill="none" stroke-width="{n(0.12 * r)}"/>'
             f'<g stroke="none" mask="url(#miolo)">{petalas}</g></g>')
    return defs, corpo


def boot(linhas, x, y0, passo):
    """Linhas (rótulo, valor, cor do valor) digitando em sequência, uma vez."""
    tam = 12.5
    col = 33                                  # colunas até o valor, com pontinhos
    defs, corpo = [], []
    t = 0.6
    for i, (rot, val, cv) in enumerate(linhas):
        y = y0 + i * passo
        pontos = "." * max(2, col - len(rot) - len(val) - 1)
        linha = f"> {rot} {pontos} "
        wl = largura(linha, tam)
        wv = largura(val, tam)
        chars = len(linha) + len(val)
        dur = chars * 0.028
        passo_w = (wl + wv) / chars
        vals = ";".join(n(passo_w * c) for c in range(chars + 1))
        defs.append(f'<clipPath id="boot{i}"><rect x="{n(x)}" y="{n(y - tam)}" width="0" height="{n(tam * 1.5)}">'
                    f'<animate attributeName="width" values="{vals}" calcMode="discrete" dur="{dur:.3f}s" '
                    f'begin="{t:.2f}s" fill="freeze"/></rect></clipPath>')
        corpo.append(f'<g clip-path="url(#boot{i})">'
                     + texto(linha, x, y, tam, cor(CREME, 0.62))
                     + texto(val, x + wl, y, tam, cv) + "</g>")
        t += dur + 0.18
    # o cursor, piscando depois da última linha
    y = y0 + len(linhas) * passo
    corpo.append(f'<rect x="{n(x)}" y="{n(y - tam * 0.8)}" width="{n(tam * 0.6)}" height="{n(tam * 0.95)}" '
                 f'fill="{cor(CREME, 0.8)}" opacity="0">'
                 f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;0.5;1" calcMode="discrete" '
                 f'dur="1.1s" begin="{t:.2f}s" repeatCount="indefinite"/></rect>')
    return "".join(defs), "".join(corpo)


def svg(entreato_t, velocidade, sincronia):
    de, emb = emblema(112, 122, 62)
    titulo = (emb
              + texto("96B", 206, 132, 80, cor(CREME), "Bold", espaco=4)
              + texto("YoRHa  No.96  Type B", 210, 164, 15, cor(DOURADO), espaco=2.6)
              + texto("designation  KURO", 210, 190, 11, cor(GRAFITE, 1.9), espaco=2.2)
              + texto("[ 9·6 → ku·ro ]", 210 + largura("designation  KURO", 11, espaco=2.2) + 16, 190, 11,
                      cor(GRAFITE, 1.35), espaco=1.2))
    # glitch de hacking (o do shader é a cada 40 s; aqui a cada 9 s, por 0,16 s):
    # faixas do título deslocadas para os lados
    faixas = []
    for k, (y, h, dx) in enumerate(((52, 26, 14), (96, 12, -22), (150, 18, 9), (178, 10, -12))):
        faixas.append(f'<clipPath id="fx{k}"><rect x="0" y="{y}" width="{W * 0.56}" height="{h}"/></clipPath>')
    glitch = ("".join(f'<g clip-path="url(#fx{k})"><rect x="0" y="0" width="{W * 0.56}" height="{H}" fill="{FUNDO}"/>'
                      f'<use href="#titulo" x="{dx}"/></g>'
                      for k, (y, h, dx) in enumerate(((52, 26, 14), (96, 12, -22), (150, 18, 9), (178, 10, -12)))))
    glitch = (f'<g opacity="0"><animate attributeName="opacity" values="0;1" keyTimes="0;0.982" calcMode="discrete" '
              f'dur="9s" begin="3s" repeatCount="indefinite"/>{glitch}</g>')

    quinta = velocidade < 0.99
    ok = cor(RYUUKO_VERDE, 0.85)
    linhas = [("BUNKER LINK", "SECURE", ok),
              ("UNIT STATUS", "NOMINAL", ok),
              ("ENTREATO T+", entreato_t, cor(DOURADO)),
              ("TIME FLOW", "x0.5 · THU" if quinta else "x1.0", cor(CHITOSE_LAGO, 0.9) if quinta else cor(DOURADO)),
              ("LAST SYNC", sincronia, cor(CREME, 0.85))]
    db, corpo_boot = boot(linhas, 600, 70, 26)
    rotulo = texto("BUNKER OS", 600, 42, 10, cor(GRAFITE, 1.9), espaco=3.2)

    defs = de + "".join(faixas) + db + f'<g id="titulo">{titulo}</g>'
    corpo = (regua(13) + regua(H - 17) + f'<use href="#titulo"/>' + glitch
             + f'<path d="M572 40V206" stroke="{cor(GRAFITE)}" stroke-width="1"/>'
             + rotulo + corpo_boot)
    return cartao(W, H, "96B · YoRHa No.96 Type B", corpo, defs)
