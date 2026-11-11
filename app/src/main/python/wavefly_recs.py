# -*- coding: utf-8 -*-
"""'Combina com você': sugestões de músicas a partir do que já foi baixado. Tudo local, sem conta."""
import json
import os
import random
import re
import threading
import time
import unicodedata

_LOCK = threading.Lock()
_POOL = {"itens": [], "t": 0, "sementes": set(), "vistos": None}

_BRACKETS = re.compile(r"[\(\[\{][^\)\]\}]*[\)\]\}]")
_RUIDO = {
    "official", "oficial", "video", "videoclipe", "clipe", "lyrics", "lyric", "letra", "audio", "hd", "4k", "hq", "ft", "feat",
    "featuring", "part", "parte", "ao", "vivo", "live", "remix", "cover", "acoustic", "acustico", "acustica", "karaoke",
    "instrumental", "versao", "version", "remastered", "remasterizado", "remaster", "legendado", "traducao", "tradução",
    "session", "sessions", "full", "album", "completo", "mix", "dj", "the", "a", "o", "de", "da", "do", "e", "and", "x", "with", "com",
    "bonus", "extended", "radio", "edit", "videoaula", "visualizer", "topic",
}


def _sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def _tokens(nome):
    t = os.path.splitext(nome)[0] if re.search(r"\.\w{2,4}$", nome) else nome
    t = _BRACKETS.sub(" ", t)
    t = _sem_acento(t.lower())
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return frozenset(x for x in t.split() if x not in _RUIDO and len(x) > 0)


def _limpo(nome):
    t = os.path.splitext(nome)[0]
    t = _BRACKETS.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip(" -_.")


def _parece(a, b):
    """True se os dois títulos são (versões de) a mesma música."""
    if not a or not b:
        return False
    if a == b:
        return True
    menor, maior = (a, b) if len(a) <= len(b) else (b, a)
    if len(menor) >= 2 and menor <= maior:
        return True
    if len(menor) == 1 and menor <= maior and len(maior) <= 3:
        return True
    inter = len(a & b)
    return inter / float(len(a | b)) >= 0.6


def _biblioteca(w):
    r = w.raiz()
    arqs = []
    try:
        for c in w.listar_mp3(r, w.AUDIO_EXTS):
            try:
                arqs.append((os.path.getmtime(c), c))
            except OSError:
                pass
    except Exception:
        pass
    arqs.sort(reverse=True)
    return [c for _, c in arqs]


def _ids_que_tenho(w):
    ids = set()
    for vid, d in list(w.INDEX.items()):
        for kind in ("a", "v"):
            ps = d.get(kind) if isinstance(d, dict) else None
            if isinstance(ps, str):
                ps = [ps]
            for p in ps or []:
                if p and os.path.isfile(p):
                    ids.add(vid)
    with w.LOCK:
        for i in w.ITENS:
            try:
                ids.add(w.chave(i["url"]))
            except Exception:
                pass
    return ids


def _arq_vistos(w):
    return os.path.join(w.BASE, "recs_vistos.json")


def _carregar_vistos(w):
    if _POOL["vistos"] is None:
        try:
            with open(_arq_vistos(w), encoding="utf-8") as f:
                _POOL["vistos"] = list(json.load(f))
        except Exception:
            _POOL["vistos"] = []
    return _POOL["vistos"]


def _gravar_vistos(w):
    try:
        with open(_arq_vistos(w), "w", encoding="utf-8") as f:
            json.dump(_POOL["vistos"][-1500:], f)
    except Exception:
        pass


def _preencher(w, arqs):
    candidatos = list(arqs[:80])
    random.shuffle(candidatos)
    novos = 0
    for c in candidatos:
        sem = _limpo(os.path.basename(c))
        if len(sem) < 4 or sem in _POOL["sementes"]:
            continue
        _POOL["sementes"].add(sem)
        try:
            res = w._buscar_bruto("musica", sem + " música parecida", 12)
        except Exception:
            continue
        for e in res[:7]:
            _POOL["itens"].append(dict(e, motivo=sem))
            novos += 1
        if novos >= 24:
            break
    return novos


def proximas(w, n=4):
    """As próximas `n` sugestões nunca mostradas, que não sejam nenhuma versão de uma música que o usuário já tem."""
    with _LOCK:
        arqs = _biblioteca(w)
        if not arqs:
            return {"itens": [], "vazio": True}
        vistos = _carregar_vistos(w)
        vset = set(vistos)
        ids = _ids_que_tenho(w)
        minhas = [_tokens(os.path.basename(c)) for c in arqs]
        if time.time() - _POOL["t"] > 6 * 3600:
            _POOL.update(itens=[], sementes=set(), t=time.time())

        def escolher():
            out, usados = [], set()
            for e in _POOL["itens"]:
                if e["id"] in ids or e["id"] in vset or e["id"] in usados:
                    continue
                tk = _tokens(e.get("titulo", ""))
                if not tk:
                    continue
                d = e.get("dur") or 0
                if d and (d < 90 or d > 600):
                    continue
                if any(_parece(tk, m) for m in minhas):
                    continue
                if any(_parece(tk, _tokens(x.get("titulo", ""))) for x in out):   # duas versões da mesma música na mesma rodada
                    continue
                usados.add(e["id"])
                out.append(e)
                if len(out) >= n:
                    break
            return out

        achados = escolher()
        tentativas = 0
        while len(achados) < n and tentativas < 4:
            tentativas += 1
            if not _preencher(w, arqs):
                break
            achados = escolher()
        for e in achados:
            vistos.append(e["id"])
        _gravar_vistos(w)
        return {"itens": [{"id": e["id"], "titulo": e.get("titulo", ""), "canal": e.get("canal", ""),
                           "dur": e.get("dur") or 0} for e in achados], "vazio": False}
