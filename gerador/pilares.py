# As três: o retrato dela (imagem de verdade, tratada na paleta: foto.py), o
# selo com a peça dela no relógio (copiada do relogio.py, não redesenhada) e
# a fala. Cada uma se mexe do jeito da ficha
# (~/.claude/skills/bastidor/references/fichas-pilares.md):
#   Kurenai  o eixo. Imóvel; nada nela anima.
#   Ryuuko   espasmódica, a 12 quadros por segundo, com a cor desalinhada de
#            quadrinho no nome.
#   Chitose  lenta: ondas abrindo do lago e uma luz que desce pelo retrato.

from comum import *
from foto import data_uri
from relogio import R, ponteiro
from texto import largura, texto

W, H = 960, 510
COL = W / 3
LADO = 250                     # retrato na tela; o JPEG vai em 1,5x para tela densa
RY = 72                        # topo dos retratos

FALAS = {
    "kurenai": ["Does it hold when it's used?", "Show me. Spare me the speech."],
    "ryuuko": ["BORING is the only bug", "i can't forgive!! make it", "weird. make it YOURS"],
    "chitose": ["Everything you build, you keep.", "So build only what you can", "keep. There is no hurry."],
}


def tranco():
    # 24 quadros a 12 por segundo: quase sempre parada, de repente pula
    saltos = []
    for k in range(24):
        if hash21(k, 7.7) > 0.62:
            saltos.append(f"{n((hash21(k, 1.3) - 0.5) * 9)} {n((hash21(k, 2.9) - 0.5) * 7)}")
        else:
            saltos.append("0 0")
    return (f'<animateTransform attributeName="transform" type="translate" values="{";".join(saltos)}" '
            f'calcMode="discrete" dur="2s" repeatCount="indefinite"/>')


def retrato(i, dona):
    x = i * COL + (COL - LADO) / 2
    s = (f'<image x="{n(x)}" y="{RY}" width="{LADO}" height="{LADO}" href="{data_uri(dona, round(LADO * 1.5))}"/>'
         f'<rect x="{n(x)}" y="{RY}" width="{LADO}" height="{LADO}" fill="url(#scan)"/>')
    # cantoneiras pequenas em volta, como as do cartão
    m, b = -6, 18
    x0, y0, x1, y1 = x + m, RY + m, x + LADO - m, RY + LADO - m
    d = (f"M{n(x0)} {n(y0 + b)}V{n(y0)}H{n(x0 + b)}M{n(x1 - b)} {n(y0)}H{n(x1)}V{n(y0 + b)}"
         f"M{n(x1)} {n(y1 - b)}V{n(y1)}H{n(x1 - b)}M{n(x0 + b)} {n(y1)}H{n(x0)}V{n(y1 - b)}")
    s += f'<path d="{d}" fill="none" stroke="{cor(CREME)}" stroke-opacity="0.35" stroke-width="1"/>'
    s += texto(f"UNIT FILE · 0{i + 1}", x, RY - 14, 8.5, cor(GRAFITE, 1.7), espaco=2)
    return s


def selo(dona, cx, cy):
    k = 0.46                                          # o relógio tem R = 140; o selo é menor
    if dona == "kurenai":
        return (f'<circle cx="{cx}" cy="{cy}" r="13" fill="{cor(KURENAI_PRETO)}" stroke="{cor(KURENAI_BRANCO, 0.7)}" stroke-width="1.2"/>'
                f'<circle cx="{cx}" cy="{cy}" r="4" fill="{cor(KURENAI_SANGUE, 1.2)}"/>')
    if dona == "chitose":
        g = (f'<path d="{ponteiro(0.78, 0.022)}" fill="{cor(CHITOSE_BRANCO, 0.85)}"/>'
             f'<circle cy="{n(-0.62 * R)}" r="{n(0.05 * R)}" fill="none" stroke="{cor(CHITOSE_LAGO)}" stroke-width="{n(0.016 * R)}"/>'
             f'<circle cy="{n(0.14 * R)}" r="{n(0.035 * R)}" fill="{cor(CHITOSE_CARMIM, 1.4)}"/>')
        return f'<g transform="translate({cx} {cy + 8}) rotate(-52) scale({k})">{g}</g>'
    # ryuuko: o ponteiro curto, a ponta em losango e o botão em X
    lx, ly, cyl = 0.05 * R, 0.08 * R, -0.60 * R
    br, by = 0.055 * R, 0.16 * R
    g = (f'<path d="{ponteiro(0.55, 0.035)}" fill="{cor(RYUUKO_TEAL, 1.3)}"/>'
         f'<path d="M0 {n(cyl - ly)}L{n(lx)} {n(cyl)}L0 {n(cyl + ly)}L{n(-lx)} {n(cyl)}Z" fill="{cor(RYUUKO_VERMELHO)}"/>'
         f'<circle cy="{n(by)}" r="{n(br)}" fill="{cor(RYUUKO_BOTAO)}"/>'
         f'<path d="M{n(-br * 0.7)} {n(by - br * 0.7)}L{n(br * 0.7)} {n(by + br * 0.7)}M{n(br * 0.7)} {n(by - br * 0.7)}'
         f'L{n(-br * 0.7)} {n(by + br * 0.7)}" stroke="{cor(KURENAI_PRETO)}" stroke-width="{n(1.4 / k)}"/>')
    return f'<g transform="translate({cx} {cy + 4}) rotate(38) scale({k})">{g}</g>'


def coluna(i, dona, nome, papel, alcunha, cor_nome):
    x = i * COL + (COL - LADO) / 2
    yn = RY + LADO + 50
    nome_s = texto(nome, x, yn, 26, cor_nome, "Bold", espaco=3.5)
    if dona == "ryuuko":                              # a cor desalinhada de quadrinho
        nome_s = (texto(nome, x - 2, yn + 1, 26, cor(RYUUKO_VERMELHO), "Bold", espaco=3.5, extra='opacity="0.6"')
                  + texto(nome, x + 2, yn - 1, 26, cor(RYUUKO_TEAL, 1.3), "Bold", espaco=3.5, extra='opacity="0.6"') + nome_s)
    topo = retrato(i, dona) + nome_s + selo(dona, round(x + LADO - 14), yn - 10)
    s = f'<g>{tranco()}{topo}</g>' if dona == "ryuuko" else topo
    s += texto(papel, x, yn + 24, 10.5, cor(DOURADO), espaco=3)
    s += texto(alcunha, x + largura(papel, 10.5, espaco=3) + 12, yn + 24, 10.5, cor(GRAFITE, 1.7), espaco=1.5)
    for k, linha in enumerate(FALAS[dona]):
        s += texto(linha, x, yn + 60 + k * 20, 13, cor(CREME, 0.82), "Light")
    if dona == "ryuuko":                              # a estrelinha do fim (a Cascadia não tem ✦)
        ex, ey, t = x + largura(FALAS[dona][-1], 13, "Light") + 12, yn + 60 + 2 * 20 - 4.5, 6.5
        w = t * 0.22
        s += (f'<path d="M{n(ex + t)} {n(ey)}L{n(ex + w)} {n(ey + w)}L{n(ex)} {n(ey + t)}L{n(ex - w)} {n(ey + w)}'
              f'L{n(ex - t)} {n(ey)}L{n(ex - w)} {n(ey - w)}L{n(ex)} {n(ey - t)}L{n(ex + w)} {n(ey - w)}Z" '
              f'fill="{cor(RYUUKO_BOTAO)}"/>')
    if dona == "chitose":                             # ondas do lago e a luz que desce, devagar
        cx, cy = round(x + LADO - 14), yn - 10
        for k in range(3):
            s += (f'<circle cx="{cx}" cy="{cy}" r="4" fill="none" stroke="{cor(CHITOSE_LAGO)}" stroke-width="1" opacity="0">'
                  f'<animate attributeName="r" values="4;26" dur="9s" begin="{k * 3}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="0.6;0" dur="9s" begin="{k * 3}s" repeatCount="indefinite"/></circle>')
        s += (f'<rect x="{n(x)}" width="{LADO}" height="70" fill="url(#luz-lago)" clip-path="url(#clip-chitose)">'
              f'<animate attributeName="y" values="{RY - 70};{RY + LADO}" dur="12s" repeatCount="indefinite"/></rect>')
    return s


def svg():
    xc = 2 * COL + (COL - LADO) / 2
    defs = (f'<pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse">'
            f'<rect width="4" height="1" fill="{FUNDO}" fill-opacity="0.32"/></pattern>'
            f'<linearGradient id="luz-lago" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{cor(CHITOSE_LAGO)}" stop-opacity="0"/>'
            f'<stop offset="0.5" stop-color="{cor(CHITOSE_LAGO)}" stop-opacity="0.10"/>'
            f'<stop offset="1" stop-color="{cor(CHITOSE_LAGO)}" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="clip-chitose"><rect x="{n(xc)}" y="{RY}" width="{LADO}" height="{LADO}"/></clipPath>')
    rotulo = (texto("PILLAR UNITS", 34, 30, 10, cor(GRAFITE, 1.9), espaco=3.2)
              + texto("// who judges what i build", 34 + largura("PILLAR UNITS", 10, espaco=3.2) + 14, 30, 10,
                      cor(GRAFITE, 1.35), espaco=1.2))
    seps = "".join(f'<path d="M{n(i * COL)} 56V{H - 24}" stroke="{cor(GRAFITE)}" stroke-width="1"/>' for i in (1, 2))
    corpo = (rotulo + seps
             + coluna(0, "kurenai", "KURENAI", "STRUCTURE", "the anchor", cor(KURENAI_BRANCO))
             + coluna(1, "ryuuko", "RYUUKO", "AESTHETICS", "golden script", cor(CREME))
             + coluna(2, "chitose", "CHITOSE", "VIABILITY", "the flow", cor(CHITOSE_BRANCO, 0.92)))
    return cartao(W, H, "Kurenai · Ryuuko · Chitose", corpo, defs)


if __name__ == "__main__":
    from pathlib import Path
    saida = Path(__file__).resolve().parent.parent / "assets" / "pilares.svg"
    saida.write_text(svg(), encoding="utf-8")
    print(f"{saida}  ({saida.stat().st_size // 1024} KB)")
