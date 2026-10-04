# Painel de dados: as contribuições do último ano como células de código (os
# mesmos glifos da 2B: ponto, traço, cruz, quadrado), uma varredura de leitura,
# e a Lilith como arquivo selado: existe, está em andamento, e só.

from datetime import date

from comum import *
from texto import largura, texto

W, H = 960, 250
PASSO = 12.4
GX, GY = 40, 74
MESES = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()


def glifo(nivel, x, y):
    c = PASSO / 2
    cx, cy = x + c, y + c
    if nivel == 0:
        return f"M{n(cx - 0.8)} {n(cy - 0.8)}h1.6v1.6h-1.6z"
    if nivel == 1:
        return f"M{n(cx - 3)} {n(cy - 0.75)}h6v1.5h-6z"
    if nivel == 2:
        return f"M{n(cx - 3)} {n(cy - 0.75)}h6v1.5h-6zM{n(cx - 0.75)} {n(cy - 3)}h1.5v6h-1.5z"
    s = 3 if nivel == 3 else 4.2
    return f"M{n(cx - s)} {n(cy - s)}h{n(2 * s)}v{n(2 * s)}h{n(-2 * s)}z"


TONS = {0: cor(GRAFITE, 1.25), 1: cor(DOURADO, 0.6), 2: cor(DOURADO, 0.85),
        3: cor(mistura(DOURADO, CREME, 0.5)), 4: cor(CREME)}


def sequencias(dias):
    atual = maior = corrida = 0
    for _, qtd, _ in dias:
        corrida = corrida + 1 if qtd else 0
        maior = max(maior, corrida)
    for _, qtd, _ in reversed(dias):
        if not qtd:
            break
        atual += 1
    # hoje sem nada ainda não quebra a sequência de ontem
    if dias and not dias[-1][1]:
        for _, qtd, _ in reversed(dias[:-1]):
            if not qtd:
                break
            atual += 1
    return atual, maior


def grade_contribuicoes(dias):
    """dias: [(date, quantidade, nível 0..4)], do mais antigo ao de hoje."""
    grupos = {k: [] for k in range(5)}
    semana0 = dias[0][0]
    desloca = (semana0.weekday() + 1) % 7          # a coluna começa no domingo
    meses = []
    hoje = None
    for idx, (d, qtd, nivel) in enumerate(dias):
        k = idx + desloca
        col, lin = k // 7, k % 7
        x, y = GX + col * PASSO, GY + lin * PASSO
        grupos[nivel].append(glifo(nivel, x, y))
        if lin == 0 and d.day <= 7:              # a primeira coluna de cada mês ganha o nome
            meses.append((x, MESES[d.month - 1]))
        hoje = (x, y)
    s = "".join(f'<path d="{"".join(g)}" fill="{TONS[k]}"/>' for k, g in grupos.items() if g)
    s += "".join(texto(m, x, GY - 10, 8.5, cor(GRAFITE, 1.7), espaco=1.2) for x, m in meses)
    # hoje: a moldura pisca, como o cursor
    hx, hy = hoje
    s += (f'<rect x="{n(hx + 0.5)}" y="{n(hy + 0.5)}" width="{n(PASSO - 1)}" height="{n(PASSO - 1)}" fill="none" '
          f'stroke="{cor(CHITOSE_LAGO, 0.9)}" stroke-width="1"><animate attributeName="opacity" values="1;0" '
          f'calcMode="discrete" dur="1.1s" repeatCount="indefinite"/></rect>')
    largura_grade = (len(dias) + desloca + 6) // 7 * PASSO
    # a varredura de leitura do 9S, da esquerda para a direita
    s += (f'<rect y="{GY - 3}" width="2" height="{n(7 * PASSO + 6)}" fill="{cor(CREME)}" opacity="0.35">'
          f'<animate attributeName="x" values="{GX - 4};{n(GX + largura_grade + 4)}" dur="6s" repeatCount="indefinite"/></rect>')
    return s, largura_grade


def estatistica(x, y, rotulo, valor):
    return (texto(rotulo, x, y, 9, cor(GRAFITE, 1.8), espaco=2)
            + texto(str(valor), x, y + 22, 17, cor(CREME), "Bold", espaco=1))


def arquivo_lilith(x, y, w, h):
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{cor(GRAFITE, 1.3)}" '
         f'stroke-width="1" stroke-dasharray="4 3"/>')
    s += texto("ARCHIVE // 0x4C1", x + 14, y + 22, 9, cor(GRAFITE, 1.9), espaco=2)
    linhas = [("PROJECT", "LILITH", cor(CREME)), ("STATUS", "ONGOING", cor(RYUUKO_VERDE, 0.85)),
              ("ACCESS", "RESTRICTED", cor(KURENAI_SANGUE, 1.35))]
    for k, (r, v, c) in enumerate(linhas):
        yy = y + 48 + k * 19
        s += texto(r, x + 14, yy, 10.5, cor(CREME, 0.55)) + texto(v, x + 86, yy, 10.5, c)
    # o conteúdo, ilegível de propósito: tarjas de censura, três versões se revezando
    versoes = []
    for v in range(3):
        d = []
        for k in range(3):
            xx, fim = x + 14, x + w - 16 - (40 if k == 2 else 0)
            while xx < fim - 8:
                lw = min(fim - xx, 10 + 46 * hash21(xx + v * 13.0, k + 3.0))
                d.append(f"M{n(xx)} {y + 110 + k * 15}h{n(lw)}v8h{n(-lw)}z")
                xx += lw + 5 + 6 * hash21(xx, k + v * 7.0)
        vals = ";".join("1" if m == v else "0" for m in range(3))
        versoes.append(f'<g opacity="{1 if v == 0 else 0}"><animate attributeName="opacity" values="{vals}" '
                       f'calcMode="discrete" dur="0.75s" repeatCount="indefinite"/>'
                       f'<path d="{"".join(d)}" fill="{cor(GRAFITE, 1.15)}"/></g>')
    s += "".join(versoes)
    # o selo
    sx, sy = x + w - 52, y + h - 30
    s += (f'<g transform="rotate(-9 {sx} {sy})">'
          f'<rect x="{sx - 40}" y="{sy - 13}" width="80" height="24" fill="{FUNDO}" fill-opacity="0.85" '
          f'stroke="{cor(KURENAI_SANGUE, 1.2)}" stroke-width="1.6"/>'
          + texto("SEALED", sx, sy + 4.5, 12, cor(KURENAI_SANGUE, 1.3), "Bold", ancora="middle", espaco=2.5) + "</g>")
    return s


def svg(dias):
    grade, lg = grade_contribuicoes(dias)
    total = sum(q for _, q, _ in dias)
    ativos = sum(1 for _, q, _ in dias if q)
    atual, maior = sequencias(dias)
    rotulo = (texto("ACTIVITY LOG", 34, 34, 10, cor(GRAFITE, 1.9), espaco=3.2)
              + texto("// last 52 weeks", 34 + largura("ACTIVITY LOG", 10, espaco=3.2) + 14, 34, 10,
                      cor(GRAFITE, 1.35), espaco=1.2))
    ys = 196
    stats = (estatistica(GX, ys, "CONTRIBUTIONS", total) + estatistica(GX + 160, ys, "ACTIVE DAYS", ativos)
             + estatistica(GX + 300, ys, "STREAK", atual) + estatistica(GX + 420, ys, "LONGEST", maior))
    corpo = rotulo + grade + stats + arquivo_lilith(728, 44, 196, 176)
    return cartao(W, H, "Activity log", corpo)


if __name__ == "__main__":
    # ensaio com dados inventados, só para ver o desenho
    from datetime import timedelta
    hoje = date.today()
    dias = []
    for k in range(364, -1, -1):
        d = hoje - timedelta(days=k)
        h = hash21(k, 4.4)
        q = 0 if h < 0.55 else int((h - 0.55) * 30)
        dias.append((d, q, min(4, (q + 2) // 3)))
    from pathlib import Path
    (Path(__file__).resolve().parent.parent / "assets" / "painel-ensaio.svg").write_text(svg(dias), encoding="utf-8")
