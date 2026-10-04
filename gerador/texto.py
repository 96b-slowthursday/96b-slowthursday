# Texto virado contorno, na Cascadia Mono do Terminal (OFL, em fonte/).
# SVG dentro de <img> não carrega fonte de fora, e a monoespaçada de cada
# sistema é outra; em contorno, todo navegador desenha igual.

from functools import lru_cache
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

PASTA = Path(__file__).resolve().parent / "fonte"


@lru_cache(None)
def _fonte(peso):
    f = TTFont(PASTA / f"CascadiaMono-{peso}.ttf")
    return f, f.getGlyphSet(), f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm


def largura(s, tam, peso="Regular", espaco=0.0):
    f, gs, cmap, hmtx, em = _fonte(peso)
    k = tam / em
    return sum(hmtx[cmap.get(ord(c), ".notdef")][0] * k + espaco for c in s) - (espaco if s else 0)


def caminho(s, x, y, tam, peso="Regular", ancora="start", espaco=0.0):
    """Path d do texto com a linha de base em y. ancora: start | middle | end."""
    f, gs, cmap, hmtx, em = _fonte(peso)
    k = tam / em
    w = largura(s, tam, peso, espaco)
    x -= {"start": 0, "middle": w / 2, "end": w}[ancora]
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    for c in s:
        nome = cmap.get(ord(c), ".notdef")
        if c != " ":
            gs[nome].draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
        x += hmtx[nome][0] * k + espaco
    return pen.getCommands()


def texto(s, x, y, tam, cor, peso="Regular", ancora="start", espaco=0.0, extra=""):
    d = caminho(s, x, y, tam, peso, ancora, espaco)
    return f'<path d="{d}" fill="{cor}"{" " + extra if extra else ""}/>' if d else ""
