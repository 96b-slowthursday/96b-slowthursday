# As três em imagem de verdade, tratadas para morar no HUD (escolha dele,
# 04/10: "mapa" nas três). A luz da imagem vira o degradê da dona; só os
# acentos dela (vermelho, e o amarelo da Ryuuko) sobrevivem com cor. Imagem
# sem cor fica só no degradê: nada de cor inventada. A borda some no fundo;
# fundo claro (papel, branco) é apagado a partir das bordas.
# As scanlines ficam no SVG, por cima: mais nítidas e mais leves que no JPEG.

import base64
import colorsys
import io
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

from comum import *

ORIGENS = Path(__file__).resolve().parent / "origens"
FUNDO_RGB = tuple(int(FUNDO[i:i + 2], 16) for i in (1, 3, 5))

PALETAS = {
    "kurenai": {"degrade": [(0x2A, 0x27, 0x26), (0x8A, 0x84, 0x80), KURENAI_BRANCO],
                "vermelho": tuple(min(255, c * 1.3) for c in KURENAI_SANGUE), "amarelo": None},
    "ryuuko": {"degrade": [(0x1F, 0x3A, 0x37), tuple(c * 1.3 for c in RYUUKO_TEAL), RYUUKO_VERDE, (0xD8, 0xF0, 0xE4)],
               "vermelho": RYUUKO_VERMELHO, "amarelo": RYUUKO_BOTAO},
    "chitose": {"degrade": [(0x17, 0x3A, 0x44), tuple(c * 0.8 for c in CHITOSE_LAGO), CHITOSE_BRANCO],
                "vermelho": tuple(min(255, c * 1.5) for c in CHITOSE_CARMIM), "amarelo": None},
}

# recorte (esquerda, topo, direita, base) em frações, quadrado em pixels
ESCOLHIDAS = {
    "ryuuko": ("ryuuko.jpg", (0.03, 0.03, 0.97, 0.97)),      # Guita.jpg: o busto com os botões em X
    "kurenai": ("kurenai.jpg", (0.20, 0.0, 0.95, 0.487)),     # download (3).jpg: rosto, ombro e lâmina
    "chitose": ("chitose.jpg", (0.10, 0.10, 1.0, 1.0)),       # s3.jpg: o rosto e o cabelo em fluxo
}


def degrade(pontos, t):
    t = min(1.0, max(0.0, t)) * (len(pontos) - 1)
    i = min(int(t), len(pontos) - 2)
    return mistura(pontos[i], pontos[i + 1], t - i)


def mapa(img, dona):
    pal = PALETAS[dona]
    pontos = [FUNDO_RGB] + pal["degrade"]
    cinza = ImageOps.autocontrast(img.convert("L"), cutoff=(1, 1))
    out = Image.new("RGB", img.size)
    for y in range(img.height):
        for x in range(img.width):
            c = img.getpixel((x, y))
            base = degrade(pontos, (cinza.getpixel((x, y)) / 255) ** 0.9)
            h, s, v = colorsys.rgb_to_hsv(*(k / 255 for k in c))
            peso, acento = 0.0, None
            if v > 0.25:
                if pal["vermelho"] and (h < 0.05 or h > 0.95):
                    acento, peso = pal["vermelho"], min(1, max(0, (s - 0.35) / 0.25))
                elif pal["amarelo"] and 0.09 < h < 0.18:
                    acento, peso = pal["amarelo"], min(1, max(0, (s - 0.40) / 0.25))
            if acento:
                base = mistura(base, tuple(k * (0.55 + 0.6 * v) for k in acento), peso)
            out.putpixel((x, y), tuple(min(255, round(k)) for k in base))
    return out


def fundo_claro(img):
    """Máscara do fundo claro que encosta na borda (papel branco), suavizada."""
    w, h = img.size
    claro = img.convert("L").point(lambda v: 255 if v > 214 else 0).convert("RGB")
    for x, y in [(x, 0) for x in range(0, w, 7)] + [(x, h - 1) for x in range(0, w, 7)] + \
                [(0, y) for y in range(0, h, 7)] + [(w - 1, y) for y in range(0, h, 7)]:
        if claro.getpixel((x, y)) == (255, 255, 255):
            ImageDraw.floodfill(claro, (x, y), (255, 0, 0))
    r, g, _ = claro.split()
    m = ImageChops.subtract(r, g)                     # só o que foi pintado: (255, 0, 0)
    return m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(3))


def tratar(dona, lado):
    arquivo, (l, t, r, b) = ESCOLHIDAS[dona]
    img = Image.open(ORIGENS / arquivo).convert("RGB")
    w, h = img.size
    img = img.crop((round(l * w), round(t * h), round(r * w), round(b * h))).resize((lado, lado), Image.LANCZOS)
    tratada = mapa(img, dona)
    w, h = tratada.size
    alfa = Image.new("L", tratada.size)
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - w / 2) / (w / 2), (y - h / 2) / (h / 2)) / 1.08
            alfa.putpixel((x, y), round(255 * min(1.0, max(0.0, (1 - d) / 0.30))))
    fc = fundo_claro(img)
    alfa = Image.composite(Image.new("L", img.size, 0), alfa, fc)
    return Image.composite(tratada, Image.new("RGB", img.size, FUNDO_RGB), alfa)


def data_uri(dona, lado):
    buf = io.BytesIO()
    tratar(dona, lado).save(buf, "JPEG", quality=84, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
