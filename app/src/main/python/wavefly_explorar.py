# -*- coding: utf-8 -*-
"""Aba Explorar: descobrir músicas e estilos novos, transmitir sem baixar e guardar favoritas. Tudo local, sem conta."""
import json
import os
import random
import threading
import time

_LOCK = threading.Lock()
_CACHE = {}
_STREAM = {}

# gênero -> (rótulo pt, consultas). O rótulo é traduzido pela interface.
GENEROS = {
    "surpresa": ("Surpreenda-me", []),
    "funk": ("Funk", ["funk brasileiro hits", "funk carioca novos", "funk consciente", "funk melody"]),
    "sertanejo": ("Sertanejo", ["sertanejo universitário hits", "sertanejo raiz clássicos", "modão sertanejo"]),
    "pop": ("Pop", ["pop hits internacionais", "new pop songs", "pop brasileiro"]),
    "rock": ("Rock", ["rock clássico hits", "rock nacional anos 90", "indie rock novo", "rock alternativo"]),
    "rap": ("Rap e Hip-hop", ["rap nacional", "hip hop clássicos", "trap brasil", "boom bap"]),
    "mpb": ("MPB", ["mpb clássicos", "mpb novos artistas", "bossa nova", "samba de raiz"]),
    "eletronica": ("Eletrônica", ["música eletrônica melhores", "house music mix", "synthwave", "drum and bass", "ambient música"]),
    "lofi": ("Lo-fi e Chill", ["lofi hip hop", "chill música relaxante", "música para estudar", "jazz lofi"]),
    "jazz": ("Jazz e Blues", ["jazz clássicos", "blues guitarra", "smooth jazz", "jazz moderno"]),
    "latina": ("Latina", ["reggaeton hits", "salsa clásicos", "bachata románticas", "cumbia", "música latina nueva"]),
    "kpop": ("K-pop e J-pop", ["kpop hits", "jpop hits", "city pop japonês", "k-indie"]),
    "reggae": ("Reggae", ["reggae clássicos", "reggae brasileiro", "dub reggae", "ska"]),
    "forro": ("Forró e Pagode", ["forró pé de serra", "pagode anos 90", "pagode novo", "axé clássicos"]),
    "classica": ("Clássica", ["música clássica melhores", "piano clássico", "trilhas de cinema orquestra", "ópera árias"]),
    "mundo": ("Do mundo", ["afrobeat hits", "música africana", "música indiana clássica", "fado português", "música árabe moderna", "música celta folk"]),
}
_MODS = ["", " novos", " melhores", " raros", " essenciais", " playlist", " 2025", " 2026"]


def generos():
    return [{"k": k, "t": v[0]} for k, v in GENEROS.items()]


def _consulta(genero, pagina, semente):
    rnd = random.Random("%s|%s|%s" % (genero, semente, pagina))
    if genero == "surpresa" or genero not in GENEROS:
        k = rnd.choice([g for g in GENEROS if g != "surpresa"])
    else:
        k = genero
    q = rnd.choice(GENEROS[k][1])
    return q + rnd.choice(_MODS)


def lista(w, genero="surpresa", pagina=0, semente="0", busca=""):
    pagina = max(0, min(int(pagina or 0), 6))
    if busca:
        q, n, ini = busca.strip()[:80] + " música", 12 * (pagina + 1), 12 * pagina
    elif genero == "surpresa":
        q, n, ini = _consulta("surpresa", pagina, semente), 14, 0
    else:
        q, n, ini = _consulta(genero, 0, semente), 12 * (pagina + 1), 12 * pagina
    chave = (q, n)
    agora = time.time()
    with _LOCK:
        c = _CACHE.get(chave)
    if c and agora - c[0] < 900:
        bruto = c[1]
    else:
        bruto = w._buscar_bruto("musica", q, n)
        with _LOCK:
            _CACHE[chave] = (agora, bruto)
            if len(_CACHE) > 60:
                for k in sorted(_CACHE, key=lambda x: _CACHE[x][0])[:20]:
                    _CACHE.pop(k, None)
    itens = []
    for e in bruto[ini:]:
        d = e.get("dur") or 0
        if d and (d < 60 or d > 1200):
            continue
        itens.append({"id": e["id"], "titulo": e["titulo"], "canal": e.get("canal", ""), "dur": d})
    return {"itens": itens, "mais": len(bruto) >= n and pagina < 6, "consulta": q}


def stream(w, vid, video=True, fresh=False):
    """Endereço direto para tocar sem baixar. Vídeo: até 360p com áudio. Vale algumas horas."""
    chave = (vid, bool(video))
    agora = time.time()
    with _LOCK:
        c = None if fresh else _STREAM.get(chave)
    if c and agora - c[0] < 3 * 3600:
        return c[1]
    fmt = ("best[height<=360][vcodec!=none][acodec!=none]/best[height<=480][vcodec!=none][acodec!=none]/18/best"
           if video else "bestaudio[ext=m4a]/bestaudio/best")
    opts = dict(w.OPTS, format=fmt, skip_download=True, noplaylist=True, socket_timeout=15)
    with w.yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info("https://www.youtube.com/watch?v=" + vid, download=False)
    if info.get("is_live"):
        raise RuntimeError("AO_VIVO")
    url = info.get("url") or ""
    if not url:
        for f in reversed(info.get("requested_formats") or info.get("formats") or []):
            if f.get("url") and (not video or f.get("acodec") not in (None, "none")):
                url = f["url"]
                break
    if not url:
        raise RuntimeError("sem endereço de reprodução")
    res = {"url": url, "dur": info.get("duration") or 0, "titulo": info.get("title") or "",
           "canal": info.get("channel") or info.get("uploader") or ""}
    with _LOCK:
        _STREAM[chave] = (agora, res)
        if len(_STREAM) > 40:
            for k in sorted(_STREAM, key=lambda x: _STREAM[x][0])[:15]:
                _STREAM.pop(k, None)
    return res


# ---------- favoritas ----------
def _arq(w):
    return os.path.join(w.BASE, "favoritas.json")


def favoritas(w):
    try:
        with open(_arq(w), "r", encoding="utf-8") as f:
            d = json.load(f)
        return [x for x in d if isinstance(x, dict) and len(x.get("id", "")) == 11]
    except Exception:
        return []


def _salvar(w, itens):
    p = _arq(w)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(itens, f, ensure_ascii=False)
    os.replace(p + ".tmp", p)


def fav_mudar(w, add=None, remover=None):
    with _LOCK:
        itens = favoritas(w)
        if add and len(add.get("id", "")) == 11 and not any(x["id"] == add["id"] for x in itens):
            itens.insert(0, {"id": add["id"], "titulo": (add.get("titulo") or "")[:200], "canal": (add.get("canal") or "")[:100],
                             "dur": int(add.get("dur") or 0)})
        if remover:
            rm = set(remover)
            itens = [x for x in itens if x["id"] not in rm]
        _salvar(w, itens)
        return itens
