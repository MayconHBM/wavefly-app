# -*- coding: utf-8 -*-
"""'Combina com você': sugestões de músicas a partir do que já foi baixado. Tudo local, sem conta."""
import os
import random
import re
import threading
import time

_LOCK = threading.Lock()
_POOL = {"itens": [], "t": 0, "vistos": set(), "sementes": set()}

_RUIDO = re.compile(r"[\(\[][^\)\]]*[\)\]]|\b(official|video|vídeo|oficial|lyrics|letra|audio|áudio|clipe|hd|4k|ft\.?|feat\.?)\b", re.I)


def _limpo(nome):
    t = os.path.splitext(nome)[0]
    t = _RUIDO.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip(" -_.")


def _biblioteca(w):
    """Arquivos de áudio da biblioteca, mais recentes primeiro."""
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


def _ja_tenho(w, arqs):
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
    nomes = {w._norm(_limpo(os.path.basename(c))) for c in arqs}
    return ids, nomes


def _preencher(w, arqs):
    """Busca mais candidatos usando algumas músicas da biblioteca como ponto de partida."""
    candidatos = [c for c in arqs[:60]]
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
        for e in res[:6]:
            _POOL["itens"].append(dict(e, motivo=sem))
            novos += 1
        if novos >= 24:
            break
    return novos


def sugestoes(w, pg=0, n=5):
    """Devolve a página `pg` (n sugestões) sem repetir nada que o usuário já tenha."""
    with _LOCK:
        arqs = _biblioteca(w)
        if not arqs:
            return {"itens": [], "vazio": True, "mais": False}
        ids, nomes = _ja_tenho(w, arqs)
        if time.time() - _POOL["t"] > 6 * 3600:
            _POOL.update(itens=[], vistos=set(), sementes=set())
        _POOL["t"] = time.time() if not _POOL["itens"] else _POOL["t"]

        def validos():
            out, vistos = [], set()
            for e in _POOL["itens"]:
                if e["id"] in ids or e["id"] in vistos:
                    continue
                nt = w._norm(_limpo(e.get("titulo", "")))
                if not nt or nt in nomes or any(nt in x or (len(x) > 6 and x in nt) for x in nomes):
                    continue
                d = e.get("dur") or 0
                if d and (d < 90 or d > 600):
                    continue
                vistos.add(e["id"])
                out.append(e)
            return out

        v = validos()
        tentativas = 0
        while len(v) < (pg + 1) * n and tentativas < 3:
            tentativas += 1
            if not _preencher(w, arqs):
                break
            v = validos()
        pagina = v[pg * n:(pg + 1) * n]
        itens = [{"id": e["id"], "titulo": e.get("titulo", ""), "canal": e.get("canal", ""), "dur": e.get("dur") or 0,
                  "motivo": e.get("motivo", "")} for e in pagina]
        return {"itens": itens, "vazio": False, "mais": len(v) > (pg + 1) * n or tentativas < 3}
