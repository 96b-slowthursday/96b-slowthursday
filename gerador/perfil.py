# Gera todas as peças do perfil em assets/. Roda na Action uma vez por dia
# (logo depois da meia-noite de Brasília, para a quinta pegar o dia inteiro)
# e pode rodar aqui na máquina do mesmo jeito.
#
# Token: GITHUB_TOKEN do ambiente (a Action) ou o do gh logado (aqui).

import json
import os
import subprocess
import urllib.request
from datetime import date
from pathlib import Path

import cabecalho
import doisb
import entreato
import painel
import pilares
import relogio

USUARIO = "96b-slowthursday"
ASSETS = Path(__file__).resolve().parent.parent / "assets"
NIVEIS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def token():
    t = os.environ.get("GITHUB_TOKEN")
    if t:
        return t
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def contribuicoes():
    consulta = """query($u: String!) { user(login: $u) { contributionsCollection { contributionCalendar {
        weeks { contributionDays { date contributionCount contributionLevel } } } } } }"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": consulta, "variables": {"u": USUARIO}}).encode(),
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        dados = json.load(r)
    if "errors" in dados:
        raise RuntimeError(dados["errors"])
    semanas = dados["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(date.fromisoformat(d["date"]), d["contributionCount"], NIVEIS[d["contributionLevel"]])
            for s in semanas for d in s["contributionDays"]]


def main():
    agora = entreato.agora()
    vel = entreato.velocidade(agora)
    segs = entreato.segundos(agora)
    ASSETS.mkdir(exist_ok=True)
    pecas = {
        "cabecalho.svg": cabecalho.svg(entreato.legivel(segs), vel, agora.strftime("%Y-%m-%d")),
        "relogio.svg": relogio.svg(entreato.fase(agora), vel),
        "2b.svg": doisb.svg(),
        "pilares.svg": pilares.svg(),
        "painel.svg": painel.svg(contribuicoes()),
    }
    for nome, conteudo in pecas.items():
        (ASSETS / nome).write_text(conteudo, encoding="utf-8")
        print(f"{nome:16} {len(conteudo.encode()) // 1024:4} KB")
    print(f"Entreato T+ {entreato.legivel(segs)} · velocidade x{vel}")


if __name__ == "__main__":
    main()
