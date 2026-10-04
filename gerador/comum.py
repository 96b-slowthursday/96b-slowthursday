# O que todas as peças do perfil dividem: a paleta do shader, números curtos,
# o hash, a grade do 9S e as cantoneiras do HUD. Casa da paleta:
# ~/.claude/terminal-yorha/hacking.hlsl; aqui é cópia.

import math

TAU = 2 * math.pi
U = 140.0 / 13.0             # a unidade de desenho do shader (u = altura/100), no tamanho do relógio

FUNDO = "#0A0A09"           # mais fundo que o do shader (#141412): escolha dele para o perfil, 03/10
SEPIA = (0x3A, 0x35, 0x2B)
GRAFITE = (0x4A, 0x46, 0x3C)
DOURADO = (0xC9, 0xA2, 0x56)
CREME = (0xED, 0xE7, 0xD6)
CHITOSE_CARMIM = (0x8B, 0x12, 0x33)
CHITOSE_LAGO = (0x53, 0xD4, 0xEC)
CHITOSE_BRANCO = (0xE6, 0xFC, 0xFD)
RYUUKO_TEAL = (0x54, 0x8A, 0x84)
RYUUKO_VERDE = (0x5C, 0xC9, 0xA0)
RYUUKO_VERMELHO = (0xE0, 0x40, 0x4A)
RYUUKO_BOTAO = (0xD9, 0xB2, 0x4A)
KURENAI_PRETO = (0x12, 0x11, 0x12)
KURENAI_BRANCO = (0xF1, 0xE8, 0xE0)
KURENAI_SANGUE = (0xB5, 0x04, 0x1F)


def cor(rgb, k=1.0):
    return "#" + "".join(f"{min(255, round(c * k)):02X}" for c in rgb)


def mistura(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def n(x):
    """Número curto para o SVG."""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def frac(x):
    return x - math.floor(x)


def hash21(px, py):
    px, py = frac(px * 123.34), frac(py * 456.21)
    d = px * (px + 45.32) + py * (py + 45.32)
    px, py = px + d, py + d
    return frac(px * py)


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def grade_def():
    # pontos a cada 2,6u e uma cruz a cada 4 células, como no fundo do shader
    passo = 2.6 * U
    bloco = passo * 4
    pontos = []
    for i in range(4):
        for j in range(4):
            cx, cy = (i + 0.5) * passo, (j + 0.5) * passo
            pontos.append(f'<rect x="{n(cx - 0.6)}" y="{n(cy - 0.6)}" width="1.2" height="1.2"/>')
    cx = cy = 0.5 * passo
    cruz = (f'<path d="M{n(cx - 3)} {n(cy)}H{n(cx + 3)}M{n(cx)} {n(cy - 3)}V{n(cy + 3)}" '
            f'stroke="{cor(GRAFITE)}" stroke-opacity="0.55" stroke-width="1"/>')
    return (f'<pattern id="grade" width="{n(bloco)}" height="{n(bloco)}" patternUnits="userSpaceOnUse">'
            f'<g fill="{cor(GRAFITE)}" fill-opacity="0.35">{"".join(pontos)}</g>{cruz}</pattern>')


def cantoneiras(w, h, m=1.2 * U, b=5.0 * U):
    d = (f"M{n(m)} {n(m + b)}V{n(m)}H{n(m + b)}"
         f"M{n(w - m - b)} {n(m)}H{n(w - m)}V{n(m + b)}"
         f"M{n(w - m)} {n(h - m - b)}V{n(h - m)}H{n(w - m - b)}"
         f"M{n(m + b)} {n(h - m)}H{n(m)}V{n(h - m - b)}")
    return f'<path d="{d}" fill="none" stroke="{cor(CREME)}" stroke-opacity="0.45" stroke-width="1.2"/>'


def cartao(w, h, titulo, corpo, defs="", grade=True):
    """Um painel do HUD: fundo, grade, cantoneiras e o que vier dentro."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<title>{titulo}</title><defs>{grade_def() if grade else ""}{defs}</defs>'
            f'<rect width="{w}" height="{h}" fill="{FUNDO}"/>'
            + (f'<rect width="{w}" height="{h}" fill="url(#grade)"/>' if grade else "")
            + f'{cantoneiras(w, h)}{corpo}</svg>')
