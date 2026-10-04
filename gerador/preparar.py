# Prepara as imagens de origem para virarem células de código: só o tom, em
# cinza, com as bordas sumindo no fundo. Rodar de novo se trocar uma origem:
#   python preparar.py
#
# 2B: a "#1" escolhida pelo Kuro em 04/10 (origens/2b.jpg), foto inteira, sem
# recorte: tom esticado pelos percentis, meios-tons clareados (gama 0,8) e uma
# vinheta que apaga as bordas. A do Terminal segue sendo outra
# (~/.claude/terminal-yorha/2b-codigo.png).

from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps

PASTA = Path(__file__).resolve().parent


def vinheta(w, h, borda=0.22):
    v = Image.new("L", (w, h))
    for y in range(h):
        for x in range(w):
            d = max(abs((x - w / 2) / (w / 2)), abs((y - h / 2) / (h / 2)) * 0.9)
            v.putpixel((x, y), round(255 * max(0.0, min(1.0, (1 - d) / borda))))
    return v


def doisb():
    im = Image.open(PASTA / "origens" / "2b.jpg").convert("L")
    im = im.resize((200, round(im.height * 200 / im.width)), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=(2, 0.5))
    im = im.point(lambda v: round(255 * (v / 255) ** 0.8))
    saida = ImageChops.multiply(im.filter(ImageFilter.SHARPEN), vinheta(*im.size))
    saida.save(PASTA / "2b-codigo.png")
    print("2b-codigo.png", saida.size)


if __name__ == "__main__":
    doisb()
