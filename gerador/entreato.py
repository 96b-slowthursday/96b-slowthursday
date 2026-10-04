# O tempo próprio do Entreato. Começa quando o relógio nasceu no shader
# (24/09/2026, 00:00 de Brasília) e anda com o nosso, menos às quintas, quando
# passa na metade da velocidade (a mesma regra do tema-hacking.ps1).
# Sem estado guardado: a conta sai inteira da data.

from datetime import datetime, timedelta, timezone

BRT = timezone(timedelta(hours=-3))      # Brasília não tem horário de verão desde 2019
NASCEU = datetime(2026, 9, 24, tzinfo=BRT)
CICLO = 429.4967296


def agora():
    return datetime.now(BRT)


def velocidade(dt):
    return 0.5 if dt.astimezone(BRT).weekday() == 3 else 1.0


def segundos(dt):
    """Segundos do Entreato entre o nascimento e dt."""
    dt = dt.astimezone(BRT)
    total, dia = 0.0, NASCEU
    while dia < dt:
        fim = min(dia + timedelta(days=1), dt)
        total += (fim - dia).total_seconds() * velocidade(dia)
        dia += timedelta(days=1)
    return total


def fase(dt):
    s = segundos(dt) / CICLO
    return s - int(s)


def legivel(segs):
    d, r = divmod(int(segs), 86400)
    h, r = divmod(r, 3600)
    return f"{d:03d}d {h:02d}h {r // 60:02d}m"
