# O relógio do Entreato em SVG animado, para o perfil do GitHub.
# Porte do relogio() de ~/.claude/terminal-yorha/hacking.hlsl: mesma geometria,
# mesmas cores, mesmas velocidades. O shader é a casa do desenho; se ele mudar,
# este arquivo segue.
#
# O GitHub tira JS e CSS do README, mas um SVG servido como imagem anima por
# SMIL. Tudo aqui é função do tempo desde a abertura da página, deslocado pela
# fase do Entreato (begin negativo), então cada geração começa de onde o tempo
# de lá estava.
#
# Uso: python relogio.py [--fase 0..1] [--velocidade 1.0|0.5] [--saida caminho]

import argparse
import math
import time
from pathlib import Path

from comum import *          # paleta, n(), cor(), hash21(), cartao()...

CICLO = 429.4967296          # o serrote do Time do Terminal; aqui só fixa os períodos
R = 140.0                    # raio do mostrador em px (no shader: 13u, u = altura/100)
LADO = 480                   # o cartão é quadrado


def polar(r, volta):
    """Ângulo em voltas a partir de +x, crescendo no sentido horário (y para baixo)."""
    return r * math.cos(volta * TAU), r * math.sin(volta * TAU)


def anima_giro(graus_por_ciclo, inicio, dur=CICLO):
    return (f'<animateTransform attributeName="transform" type="rotate" '
            f'from="0" to="{n(graus_por_ciclo)}" dur="{dur:.4f}s" '
            f'begin="{-inicio:.3f}s" repeatCount="indefinite"/>')


# ---- peças ----

def tracos_andantes(vel, inicio):
    # 60 traços radiais virados para fora, padrão longo/curto/médio/curto,
    # girando no sentido HORÁRIO, contra os ponteiros
    raio = 1.08 * R
    d = []
    for i in range(60):
        comp = {0: 0.17, 2: 0.11}.get(i % 4, 0.06)
        v = (i + 0.5) / 60
        x0, y0 = polar(raio, v)
        x1, y1 = polar(raio * (1 + comp), v)
        d.append(f"M{n(x0)} {n(y0)}L{n(x1)} {n(y1)}")
    giro = round(20 * vel) / 15 * 360
    return (f'<g>{anima_giro(giro, inicio)}<path d="{"".join(d)}" stroke="{cor(GRAFITE, 1.5)}" '
            f'stroke-width="1.4"/></g>')


def tracejado(vel, inicio):
    # seis arcos a 1,42 R, girando anti-horário; o que passa sob a Chitose
    # acende em azul-lago e apaga devagar (ela vendo o tempo passar)
    raio = 1.42 * R
    m = round(14 * vel)
    giro = -m / 6 * 360
    rel = m / 6 - 1                       # voltas do anel relativas à Chitose, por ciclo
    periodo = CICLO / rel
    # luz em função de s = frac(fase_Chitose - fase_arco)
    amostras = [(0.0, 1.0)]
    for k in range(1, 9):
        s = 0.08 * k / 8
        amostras.append((s, (1 - s / 0.08) ** 2))
    amostras.append((0.97, 0.0))
    for k in range(1, 6):
        s = 0.97 + 0.03 * k / 5
        amostras.append((min(s, 1.0), (1 - (1 - s) / 0.03) ** 2))
    chaves = ";".join(f"{s:.4f}" for s, _ in amostras)
    valores = ";".join(f"{v:.3f}" for _, v in amostras)
    base, luz = [], []
    for j in range(6):
        a0, a1 = (j + 0.5) / 6, (j + 0.9) / 6
        x0, y0 = polar(raio, a0)
        x1, y1 = polar(raio, a1)
        arco = f"M{n(x0)} {n(y0)}A{n(raio)} {n(raio)} 0 0 1 {n(x1)} {n(y1)}"
        base.append(arco)
        c_j = frac(-0.25 - (j + 0.7) / 6)
        luz.append(f'<path d="{arco}" opacity="0"><animate attributeName="opacity" '
                   f'values="{valores}" keyTimes="{chaves}" dur="{periodo:.4f}s" '
                   f'begin="{-(inicio + c_j * periodo):.3f}s" repeatCount="indefinite"/></path>')
    return (f'<g fill="none" stroke-width="1.2">{anima_giro(giro, inicio)}'
            f'<path d="{"".join(base)}" stroke="{cor(GRAFITE, 0.9)}"/>'
            f'<g stroke="{cor(CHITOSE_LAGO, 0.7)}">{"".join(luz)}</g></g>')


def ouro_gradiente():
    # a faixa de brilho que corre na diagonal, como nas letras do Claude pensando
    a = 0.8
    paradas = []
    for k in range(9):
        t = -a + 2 * a * k / 8
        b = math.exp(-t * t * 10)
        paradas.append(f'<stop offset="{(t + a) / (2 * a):.3f}" stop-color="{cor(mistura(DOURADO, CREME, b * 0.7))}"/>')
    return (f'<linearGradient id="ouro" gradientUnits="userSpaceOnUse" '
            f'x1="{n(-a * R)}" y1="{n(a * R)}" x2="{n(a * R)}" y2="{n(-a * R)}">{"".join(paradas)}'
            f'<animateTransform attributeName="gradientTransform" type="translate" '
            f'values="{n(-2 * R)} {n(2 * R)};{n(2 * R)} {n(-2 * R)}" dur="6s" repeatCount="indefinite"/>'
            f'</linearGradient>')


def mostrador():
    d = []
    for k in range(60):
        maior = k % 5 == 0
        v = k / 60 - 0.25
        x0, y0 = polar(0.80 * R, v)
        x1, y1 = polar((0.88 if maior else 0.855) * R, v)
        d.append((maior, f"M{n(x0)} {n(y0)}L{n(x1)} {n(y1)}"))
    maiores = "".join(s for m, s in d if m)
    menores = "".join(s for m, s in d if not m)
    k = 1 / math.sqrt(2)
    diag = (f"M{n(0.99 * R * k)} {n(-0.99 * R * k)}L{n(1.14 * R * k)} {n(-1.14 * R * k)}"
            f"M{n(-0.99 * R * k)} {n(0.99 * R * k)}L{n(-1.14 * R * k)} {n(1.14 * R * k)}")
    corpo = (f'<circle r="{n(0.895 * R)}"/><circle r="{n(0.945 * R)}"/>'
             f'<path d="{maiores}" stroke-width="2"/><path d="{menores}" stroke-width="1"/>'
             f'<path d="{diag}" stroke-width="2.8"/>')
    return (f'<g fill="none" stroke="url(#ouro)" stroke-width="1.4">'
            f'<g filter="url(#halo-ouro)" opacity="0.5">{corpo}</g>'
            f'<g opacity="0.55">{corpo}</g></g>')


def engrenagem(cx, cy, raio, dentes, alto, giro):
    rt, rr = raio * (1 + alto) * R, raio * R
    p = []
    for i in range(dentes):
        a0, a1, a2 = i / dentes, (i + 0.5) / dentes, (i + 1) / dentes
        x, y = polar(rt, a0)
        p.append(f"{'M' if i == 0 else 'L'}{n(x)} {n(y)}")
        x, y = polar(rt, a1)
        p.append(f"A{n(rt)} {n(rt)} 0 0 1 {n(x)} {n(y)}")
        x, y = polar(rr, a1)
        p.append(f"L{n(x)} {n(y)}")
        x, y = polar(rr, a2)
        p.append(f"A{n(rr)} {n(rr)} 0 0 1 {n(x)} {n(y)}")
    return (f'<path transform="translate({n(cx * R)} {n(cy * R)}) rotate({n(-math.degrees(giro))})" '
            f'd="{"".join(p)}Z"/>')


def pontilhado(cx, cy, rr, pontos):
    c = TAU * rr * R / (2 * pontos)
    return (f'<circle cx="{n(cx * R)}" cy="{n(cy * R)}" r="{n(rr * R)}" '
            f'stroke-dasharray="{c:.3f} {c:.3f}"/>')


def norm(x, y):
    L = math.hypot(x, y)
    return x / L, y / L


def chave():
    # argola de quatro lóbulos, aro, haste e dois dentes (proposta c)
    ax, ay = 0.44, -0.30
    dx, dy = norm(-1.0, 0.9)
    comp, k = 1.00, 0.85
    s = []
    for i in range(4):
        v = i / 4 - 1 / 8
        x, y = polar(0.075 * k, v)
        s.append(f'<circle cx="{n((ax + x) * R)}" cy="{n((ay + y) * R)}" r="{n(0.045 * k * R)}"/>')
    s.append(f'<circle cx="{n(ax * R)}" cy="{n(ay * R)}" r="{n(0.035 * k * R)}"/>')
    # haste: contorno de cápsula de meia-largura 0,012k
    w = 0.012 * k
    px, py = -dy, dx
    a = (ax + dx * 0.12 * k, ay + dy * 0.12 * k)
    b = (ax + dx * comp, ay + dy * comp)
    pts = lambda P, sx: (n((P[0] + px * w * sx) * R), n((P[1] + py * w * sx) * R))
    a1, b1, b2, a2 = pts(a, 1), pts(b, 1), pts(b, -1), pts(a, -1)
    s.append(f'<path d="M{a1[0]} {a1[1]}L{b1[0]} {b1[1]}A{n(w * R)} {n(w * R)} 0 0 0 {b2[0]} {b2[1]}'
             f'L{a2[0]} {a2[1]}A{n(w * R)} {n(w * R)} 0 0 0 {a1[0]} {a1[1]}Z"/>')
    # dentes, no referencial da haste
    ox, oy = b[0] - dx * 0.10 * k, b[1] - dy * 0.10 * k
    m = f"matrix({n(px)} {n(py)} {n(dx)} {n(dy)} {n(ox * R)} {n(oy * R)})"
    for cx, cy, hx, hy in ((0.05, 0, 0.04, 0.018), (0.035, -0.07, 0.025, 0.018)):
        s.append(f'<rect transform="{m}" x="{n((cx - hx) * k * R)}" y="{n((cy - hy) * k * R)}" '
                 f'width="{n(2 * hx * k * R)}" height="{n(2 * hy * k * R)}"/>')
    return "".join(s)


def brilho4(cx, cy, tam):
    w = tam * 0.16
    c = [(tam, 0), (w, w), (0, tam), (-w, w), (-tam, 0), (-w, -w), (0, -tam), (w, -w)]
    return "M" + "L".join(f"{n((cx + x) * R)} {n((cy + y) * R)}" for x, y in c) + "Z"


def miolo():
    # a "F5" (25/09): quadro inclinado, trio encaixado, engrenagem no canto,
    # a chave atravessando o eixo, pontilhados, traços longos e brilhos. Parado.
    c1x, c1y, k = -0.30, -0.34, 0.72
    v2 = norm(1.0, -0.55)
    v3 = norm(-0.35, 1.0)
    trio = (engrenagem(c1x, c1y, 0.20 * k, 14, 0.12, 0.0)
            + engrenagem(c1x + v2[0] * 0.345 * k, c1y + v2[1] * 0.345 * k, 0.12 * k, 9, 0.16, 0.22)
            + engrenagem(c1x + v3[0] * 0.30 * k, c1y + v3[1] * 0.30 * k, 0.08 * k, 7, 0.20, 0.35)
            + engrenagem(0.42, 0.42, 0.09, 8, 0.2, 0.4))
    hx, hy, i = 0.30 * R, 0.44 * R, 0.025 * R
    quadro = (f'<g transform="translate({n(0.03 * R)} {n(0.05 * R)}) rotate({n(-math.degrees(0.35))})">'
              f'<rect x="{n(-hx)}" y="{n(-hy)}" width="{n(2 * hx)}" height="{n(2 * hy)}"/>'
              f'<rect x="{n(-hx + i)}" y="{n(-hy + i)}" width="{n(2 * (hx - i))}" height="{n(2 * (hy - i))}"/></g>')
    linhas = (f"M{n(-0.62 * R)} {n(0.42 * R)}L{n(0.10 * R)} {n(-0.25 * R)}"
              f"M{n(0.22 * R)} {n(0.70 * R)}L{n(0.62 * R)} {n(-0.08 * R)}")
    brilhos = brilho4(0.52, 0.10, 0.06) + brilho4(-0.50, 0.32, 0.05) + brilho4(0.05, -0.64, 0.05)
    return (f'<g fill="none" stroke="url(#ouro)">'
            f'<g stroke-opacity="0.28" stroke-width="1">{quadro}</g>'
            f'<g stroke-opacity="0.42" stroke-width="1.2">{trio}</g>'
            f'<g stroke-opacity="0.24" stroke-width="1">{pontilhado(c1x, c1y, 0.22, 36)}{pontilhado(0.42, 0.42, 0.16, 28)}</g>'
            f'<g stroke-opacity="0.50" stroke-width="1.2">{chave()}</g></g>'
            f'<path d="{linhas}" stroke="{cor(GRAFITE, 1.6)}" stroke-width="0.8"/>'
            f'<path d="{brilhos}" fill="{cor(CREME)}" fill-opacity="0.6"/>')


def ponteiro(comp, larg):
    # apontando para as 12h; vai de -0,08 a comp e afina até 30% na ponta
    w0, w1 = larg * R, larg * 0.3 * R
    y0, y1 = 0.08 * R, -comp * R
    return (f"M{n(-w0)} {n(y0)}L{n(-w1)} {n(y1)}A{n(w1)} {n(w1)} 0 0 1 {n(w1)} {n(y1)}"
            f"L{n(w0)} {n(y0)}A{n(w0)} {n(w0)} 0 0 1 {n(-w0)} {n(y0)}Z")


def chitose(inicio):
    # longa, lenta e contínua; uma volta por ciclo, anti-horário; não desacelera na quinta
    return (f'<g>{anima_giro(-360, inicio)}'
            f'<path d="{ponteiro(0.78, 0.022)}" fill="{cor(CHITOSE_BRANCO, 0.85)}"/>'
            f'<circle cy="{n(-0.62 * R)}" r="{n(0.05 * R)}" fill="none" stroke="{cor(CHITOSE_LAGO)}" '
            f'stroke-width="{n(0.016 * R)}" filter="url(#halo-lago)" opacity="0.6"/>'
            f'<circle cy="{n(-0.62 * R)}" r="{n(0.05 * R)}" fill="none" stroke="{cor(CHITOSE_LAGO)}" '
            f'stroke-opacity="0.95" stroke-width="{n(0.016 * R)}"/>'
            f'<circle cy="{n(0.14 * R)}" r="{n(0.035 * R)}" fill="{cor(CHITOSE_CARMIM, 1.4)}"/></g>')


def unidades_ryuuko(t, passos):
    # um passo por ~segundo, tamanho sorteado, a mola, e no 7º passo um para trás
    passo = math.floor(t)
    p = passo % passos
    kk = p % 7
    base = passo - 2.0 * (kk >= 6) + (hash21(p, 3.3) - 0.5) * 0.4
    fr = t - passo
    mola = math.exp(-fr * 7) * math.sin(fr * 20) * 0.18
    return base - mola


def ryuuko(vel, inicio):
    passos = 240 if vel < 0.99 else 420
    chaves, valores = [], []
    for p in range(passos):
        for fr in (0.0, 0.078, 0.236, 0.40, 0.999):
            t = p + fr
            chaves.append(t / passos)
            valores.append(-unidades_ryuuko(t, passos) * 6)
    chaves.append(1.0)
    valores.append(valores[-1])
    anim = (f'<animateTransform attributeName="transform" type="rotate" '
            f'values="{";".join(f"{v:.2f}" for v in valores)}" '
            f'keyTimes="{";".join(f"{c:.6f}" for c in chaves)}" '
            f'dur="{CICLO:.4f}s" begin="{-inicio:.3f}s" repeatCount="indefinite"/>')
    lx, ly = 0.05 * R, 0.08 * R
    cy = -0.60 * R
    losango = f"M0 {n(cy - ly)}L{n(lx)} {n(cy)}L0 {n(cy + ly)}L{n(-lx)} {n(cy)}Z"
    br, by = 0.055 * R, 0.16 * R
    xis = (f"M{n(-br)} {n(by - br)}L{n(br)} {n(by + br)}M{n(br)} {n(by - br)}L{n(-br)} {n(by + br)}")
    mao = ponteiro(0.55, 0.035)
    return (f'<g>{anim}'
            f'<g filter="url(#halo-ryuuko)" fill="{cor(RYUUKO_VERDE)}" opacity="0.45"><path d="{mao}"/><path d="{losango}"/></g>'
            f'<path d="{mao}" fill="{cor(RYUUKO_TEAL, 1.3)}"/>'
            f'<path d="{losango}" fill="{cor(RYUUKO_VERMELHO)}"/>'
            f'<circle cy="{n(by)}" r="{n(br)}" fill="{cor(RYUUKO_BOTAO)}"/>'
            f'<path d="{xis}" stroke="{cor(KURENAI_PRETO)}" stroke-width="1.4" clip-path="url(#botao)"/></g>')


def kurenai():
    # o eixo: preto e imóvel; em volta o brilho morre; anel branco fino, ponto vermelho
    paradas = []
    for k in range(9):
        r = 0.20 * k / 8
        paradas.append(f'<stop offset="{k / 8:.3f}" stop-color="{FUNDO}" '
                       f'stop-opacity="{0.85 * (1 - smoothstep(0.05, 0.20, r)):.3f}"/>')
    grad = f'<radialGradient id="apaga" r="{n(0.20 * R)}" cx="0" cy="0" gradientUnits="userSpaceOnUse">{"".join(paradas)}</radialGradient>'
    return grad, (f'<circle r="{n(0.20 * R)}" fill="url(#apaga)"/>'
                  f'<circle r="{n(0.06 * R)}" fill="{cor(KURENAI_PRETO)}" stroke="{cor(KURENAI_BRANCO, 0.7)}" stroke-width="1.1"/>'
                  f'<circle r="{n(0.018 * R)}" fill="{cor(KURENAI_SANGUE, 1.2)}"/>')


def pulso(vel, inicio):
    # o mostrador e o miolo respiram: 0,85 a 1,0
    m = round(41 * vel)
    periodo = CICLO / m
    vals = ";".join(f"{0.85 + 0.15 * math.sin(TAU * k / 12):.3f}" for k in range(13))
    return (f'<animate attributeName="opacity" values="{vals}" dur="{periodo:.4f}s" '
            f'begin="{-inicio:.3f}s" repeatCount="indefinite"/>')


def svg(fase, vel):
    inicio = fase * CICLO
    grad_k, corpo_k = kurenai()
    c = LADO / 2
    defs = (ouro_gradiente() + grad_k
            + '<filter id="halo-ouro" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="7"/></filter>'
            + '<filter id="halo-lago" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="5"/></filter>'
            + '<filter id="halo-ryuuko" x="-100%" y="-50%" width="300%" height="200%"><feGaussianBlur stdDeviation="4.5"/></filter>'
            + f'<clipPath id="botao"><circle cy="{n(0.16 * R)}" r="{n(0.055 * R)}"/></clipPath>')
    corpo = (f'<g transform="translate({n(c)} {n(c)})" stroke-linecap="butt">'
             f'{tracos_andantes(vel, inicio)}{tracejado(vel, inicio)}'
             f'<g>{pulso(vel, inicio)}{mostrador()}{miolo()}</g>'
             f'{chitose(inicio)}{ryuuko(vel, inicio)}{corpo_k}</g>')
    return cartao(LADO, LADO, "Relógio do Entreato", corpo, defs)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fase", type=float, default=None, help="0..1; padrão: deriva do relógio do sistema")
    ap.add_argument("--velocidade", type=float, default=1.0)
    ap.add_argument("--saida", default=str(Path(__file__).resolve().parent.parent / "assets" / "relogio.svg"))
    a = ap.parse_args()
    fase = a.fase if a.fase is not None else frac(time.time() / CICLO)
    saida = Path(a.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(svg(fase, a.velocidade), encoding="utf-8")
    print(f"{saida}  ({saida.stat().st_size // 1024} KB, fase {fase:.3f}, velocidade {a.velocidade})")
