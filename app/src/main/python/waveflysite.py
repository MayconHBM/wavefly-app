#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WaveFly YT - baixa musicas do YouTube em lote com interface web local.

Uso:   python wavefly_yt.py          ->  abre http://localhost:8773
       python wavefly_yt.py --port 8800
       python wavefly_yt.py --host 0.0.0.0   (acessar de outro aparelho da mesma rede)
       python wavefly_yt.py --servidor       (modo site: cada um recebe os arquivos no navegador, solto ou em ZIP)

Precisa de:  pip install -U yt-dlp   (+ ffmpeg instalado)
"""
import argparse, copy, hashlib, json, os, re, shutil, signal, subprocess, sys, threading, time, unicodedata, uuid, webbrowser, zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.request
from urllib.parse import parse_qs, quote, quote_plus, urlparse

try:
    import yt_dlp
except ImportError:
    sys.exit("Falta instalar o yt-dlp:  pip install -U yt-dlp")

BASE = os.environ.get("WAVEFLY_DATA") or os.path.dirname(os.path.abspath(__file__))
CFG_FILE = os.path.join(BASE, "wavefly_config.json")
FILA_FILE = os.path.join(BASE, "wavefly_fila.json")
INDEX_FILE = os.path.join(BASE, "wavefly_index.json")
PRIMEIRA = False
LOCK = threading.RLock()
LIBERADO = False
SERVIDOR = False
HORAS_SERVIDOR = 3
ZIP_DIR = os.path.join(BASE, ".wavefly_tmp")
CAPA_DIR = os.path.join(BASE, ".wavefly_capas")
APP_NOME = "WaveFly"
PASTA_NOME = "WaveFly"
MAX_LINKS = 1000
AUDIO_EXTS = (".mp3", ".m4a", ".webm", ".opus", ".ogg", ".aac")
VIDEO_EXTS = (".mp4", ".mkv")
EXTS = AUDIO_EXTS + VIDEO_EXTS
MIME = {".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".webm": "audio/webm", ".opus": "audio/ogg", ".ogg": "audio/ogg", ".aac": "audio/aac", ".mp4": "video/mp4", ".mkv": "video/x-matroska", ".zip": "application/zip"}

ANDROID = os.path.isdir("/storage/emulated/0") or bool(os.environ.get("WAVEFLY_DATA"))
PASTA_PADRAO = ("/storage/emulated/0/Download/" + PASTA_NOME) if ANDROID else os.path.join(os.path.expanduser("~"), "Music", PASTA_NOME)
PASTAS_PADRAO = {PASTA_NOME: PASTA_PADRAO}
CFG = {"pastas": dict(PASTAS_PADRAO), "atual": PASTA_NOME, "qualidade": 192, "formato": "mp3", "modo_playlist": "pasta",
       "lote": 40, "pausa_lote": 15, "res": 720}


def raiz():
    return CFG["pastas"][CFG["atual"]]


def migrar_antigos():
    for velho, novo in (("musicdl_config.json", CFG_FILE), ("musicdl_fila.json", FILA_FILE)):
        v = os.path.join(BASE, velho)
        if not os.path.exists(novo) and os.path.exists(v):
            try:
                shutil.copy2(v, novo)
            except OSError:
                pass


def carregar_cfg():
    global PRIMEIRA
    migrar_antigos()
    PRIMEIRA = not os.path.exists(CFG_FILE) and not SERVIDOR
    try:
        with open(CFG_FILE, encoding="utf-8") as f:
            CFG.update(json.load(f))
    except Exception:
        pass
    CFG["pastas"].setdefault(PASTA_NOME, PASTA_PADRAO)
    velho = CFG["pastas"].get("MusicDL")
    if CFG["atual"] == "MusicDL" and PASTA_NOME != "MusicDL" and velho and not (os.path.isdir(velho) and listar_mp3(velho)):
        CFG["atual"] = PASTA_NOME
    if SERVIDOR:
        CFG["pastas"] = {"Downloads": os.path.join(BASE, "wavefly_downloads")}
        CFG["atual"] = "Downloads"
    if CFG["atual"] not in CFG["pastas"]:
        CFG["atual"] = next(iter(CFG["pastas"]))
    try:
        os.makedirs(raiz(), exist_ok=True)
    except OSError as ex:
        print("Aviso: nao consegui criar a pasta:", ex)


def _gravar(caminho, dados):
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    os.replace(tmp, caminho)


def salvar_cfg():
    if SERVIDOR:
        return
    try:
        _gravar(CFG_FILE, CFG)
    except OSError:
        pass


URL_RE = re.compile(r"https?://.+?(?=https?://|\s|$)", re.I)
ID_RE = re.compile(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def chave(url):
    m = ID_RE.search(url)
    return m.group(1) if m else url


def eh_playlist(l):
    if "/playlist" in l:
        return True
    return "list=" in l and not re.search(r"[?&]list=(RD|UL)", l)


YT_RE = re.compile(r"^https?://([\w-]+\.)*(youtube\.com|youtu\.be|youtube-nocookie\.com)(/|$|\?)", re.I)


BARE_RE = re.compile(r"(^|[\s(<])((?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be)/)", re.I)


def extrair_links(texto):
    texto = BARE_RE.sub(r"\1https://\2", texto or "")
    vistos, out, rep, fora = set(), [], 0, 0
    for l in URL_RE.findall(texto or ""):
        l = l.rstrip(".,;)>]'\"")
        if not YT_RE.match(l):
            fora += 1
            continue
        k = chave(l)
        if k in vistos:
            rep += 1
            continue
        vistos.add(k)
        out.append(l)
    return out, rep, fora


def limpar_erro(ex):
    linhas = ANSI_RE.sub("", str(ex)).strip().splitlines()
    return linhas[-1] if linhas else "erro desconhecido"


def bloqueio_youtube(m):
    m = m.lower()
    return "not a bot" in m or "sign in to confirm" in m


def passageiro(m):
    m = m.lower()
    return bloqueio_youtube(m) or any(x in m for x in ("403", "timed out", "timeout", "connection", "temporar", "http error 5", "unable to download"))


def calcular_pausa(qtd):
    return 1 if qtd <= 30 else 2 if qtd <= 70 else 3 if qtd <= 120 else 5


def tam_fmt(b):
    if not b:
        return "0B"
    return f"{b/1048576:.1f}MB" if b >= 1048576 else f"{b/1024:.0f}KB"


def caminho_seguro(rel):
    r = os.path.realpath(raiz())
    p = os.path.realpath(os.path.join(r, rel))
    return p if p.startswith(r + os.sep) else None


FRAG_RE = re.compile(r"\.f\d+\.[a-z0-9]+$", re.I)


def listar_mp3(r, exts=EXTS):
    out = []
    r_abs = os.path.realpath(r)
    for d, _, ns in os.walk(r_abs):
        for n in ns:
            if n.lower().endswith(exts) and ".temp." not in n.lower() and not FRAG_RE.search(n):
                caminho_completo = os.path.join(d, n)
                # Garante que o arquivo pertence rigorosamente à pasta raiz atual
                if os.path.realpath(caminho_completo).startswith(r_abs + os.sep):
                    out.append(caminho_completo)
    return out


def limpar_pasta_vazia(arq):
    try:
        p = os.path.dirname(arq)
        if p and os.path.realpath(p) != os.path.realpath(raiz()) and os.path.isdir(p) and not os.listdir(p):
            os.rmdir(p)
    except OSError:
        pass


UNAV = ("private", "needs_auth", "subscriber_only", "premium_only")


def indisponivel(e):
    t = (e.get("title") or "").strip()
    if t.startswith("[") and t.endswith("]"):
        return True
    if not t and not e.get("duration"):
        return True
    return (e.get("availability") or "") in UNAV


OPTS = {
    "format": "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best",
    "outtmpl": "%(title)s.%(ext)s",
    "noplaylist": True, "quiet": True, "no_warnings": True,
    "remote_components": ["ejs:github"],
    "js_runtimes": {"deno": {}, "node": {}},
    "windowsfilenames": True, "retries": 3, "socket_timeout": 30,
}


if os.environ.get("WAVEFLY_FFMPEG"):
    OPTS["ffmpeg_location"] = os.environ["WAVEFLY_FFMPEG"]


DURS = {}


def est_bytes(dur, fmt, qual, res):
    if not dur:
        return 0
    if fmt == "mp3":
        kbps = int(qual or 192)
    elif fmt == "video":
        kbps = {360: 700, 720: 1800, 1080: 3500}.get(int(res or 720), 1800) + 128
    else:
        kbps = 128
    return int(dur * kbps * 125)


def expandir_playlist(url):
    opts = dict(OPTS, noplaylist=False, extract_flat=True, skip_download=True)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    titulo = re.sub(r'[\\/:*?"<>|]', "", info.get("title") or "Playlist").strip()[:50] or "Playlist"
    links, vistos = [], set()
    for ent in info.get("entries") or []:
        if not isinstance(ent, dict):
            continue
        vid = ent.get("id")
        if not vid or len(vid) != 11 or vid in vistos:
            continue
        if indisponivel(ent):
            continue
        vistos.add(vid)
        if ent.get("duration"):
            DURS[vid] = ent["duration"]
        guardar_tit(vid, ent)
        links.append(f"https://www.youtube.com/watch?v={vid}")
    if not links and ("v=" in url or "youtu.be/" in url):
        return titulo, [url]
    return titulo, links


def obter_info(url):
    with yt_dlp.YoutubeDL(OPTS) as ydl:
        info = ydl.extract_info(url, download=False)
        base = os.path.splitext(os.path.basename(ydl.prepare_filename(info)))[0]
    return info, info.get("title", "sem título"), base


def existe(r, nome, exts=None):
    alvos = {nome + e for e in (exts or EXTS)}
    try:
        return bool(alvos & set(os.listdir(r)))
    except OSError:
        return False


def proximo_livre(r, base, exts=None):
    n = 2
    while existe(r, f"{base} ({n})", exts):
        n += 1
    return f"{base} ({n})"


BUSCA = {}
BUSCA_LOCK = threading.Lock()
PL_CACHE = {}


def _buscar_bruto(tipo, termo, n):
    if tipo == "playlist":
        url = "https://www.youtube.com/results?search_query=" + quote_plus(termo) + "&sp=EgIQAw%3D%3D"
        opts = dict(OPTS, noplaylist=False, extract_flat=True, skip_download=True, playlistend=n)
    else:
        url = f"ytsearch{n}:{termo}"
        opts = dict(OPTS, extract_flat=True, skip_download=True)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    out, vistos = [], set()
    for e in info.get("entries") or []:
        if not isinstance(e, dict):
            continue
        if tipo == "playlist":
            m = re.search(r"list=([\w-]+)", e.get("url") or "")
            pid = m.group(1) if m else e.get("id")
            if not pid or len(pid) <= 11 or pid in vistos or not re.fullmatch(r"[\w-]+", pid):
                continue
            vistos.add(pid)
            th = e.get("thumbnails") or []
            thumb = (th[-1].get("url") if th and isinstance(th[-1], dict) else "") or ""
            out.append({"id": pid, "titulo": e.get("title") or "Playlist", "canal": e.get("channel") or e.get("uploader") or "",
                        "n": e.get("playlist_count") or e.get("n_entries") or 0,
                        "thumb": thumb if thumb.startswith("http") else ""})
        else:
            vid = e.get("id")
            if not vid or len(vid) != 11 or vid in vistos:
                continue
            vistos.add(vid)
            guardar_tit(vid, e)
            dur = e.get("duration") or 0
            views = e.get("view_count") or 0
            tam_est = est_bytes(dur, CFG["formato"], CFG["qualidade"], CFG.get("res", 720))
            out.append({"id": vid, "titulo": e.get("title") or "sem título", "dur": dur,
                        "canal": e.get("channel") or e.get("uploader") or "",
                        "views": f"{views:,}".replace(",", ".") if views else "",
                        "tamanho": tam_fmt(tam_est)})
    return out


def busca_paginada(tipo, termo, inicio, n=10):
    if tipo not in ("musica", "playlist"):
        tipo = "musica"
    k = (tipo, termo.lower())
    with BUSCA_LOCK:
        if inicio == 0:
            BUSCA.clear()
        c = BUSCA.get(k)
        if not c or time.time() - c["t"] > 900:
            c = BUSCA[k] = {"itens": [], "t": time.time(), "fim": False}
        if len(BUSCA) > 30:
            for kk in sorted(BUSCA, key=lambda x: BUSCA[x]["t"])[:10]:
                if kk != k:
                    BUSCA.pop(kk, None)
    fim_pag = inicio + n
    if len(c["itens"]) < fim_pag and not c["fim"]:
        antes = len(c["itens"])
        c["itens"] = _buscar_bruto(tipo, termo, ((fim_pag + 29) // 30) * 30)
        c["t"] = time.time()
        if len(c["itens"]) <= antes:
            c["fim"] = True
    mais = len(c["itens"]) > fim_pag or (not c["fim"] and len(c["itens"]) >= fim_pag)
    return {"itens": c["itens"][inicio:fim_pag], "mais": mais}


TIT_CACHE = {}


def short(u):
    """Nome curto para mensagens: titulo se ja conhecido, senao o link sem https://."""
    k = chave(str(u))
    t = TIT_CACHE.get(k)
    if t and t.get("titulo"):
        return t["titulo"][:60]
    return re.sub(r"^https?://(www\.)?", "", str(u))[:60]


def guardar_tit(vid, e):
    t = e.get("title")
    if t:
        if len(TIT_CACHE) > 6000:
            TIT_CACHE.clear()
        TIT_CACHE[vid] = {"titulo": t, "canal": e.get("channel") or e.get("uploader") or ""}


def eh_ao_vivo(vid):
    try:
        with yt_dlp.YoutubeDL(dict(OPTS, skip_download=True, socket_timeout=15, extract_flat=False)) as ydl:
            info = ydl.extract_info("https://www.youtube.com/watch?v=" + vid, download=False, process=False)
        return bool(info.get("is_live") or info.get("live_status") in ("is_live", "is_upcoming"))
    except Exception:
        return False


def titulo_rapido(vid, checar_live=False):
    if not re.fullmatch(r"[\w-]{11}", vid or ""):
        raise ValueError("Vídeo inválido")
    if vid in TIT_CACHE and (not checar_live or "live" in TIT_CACHE[vid]):
        return TIT_CACHE[vid]
    url = "https://www.youtube.com/watch?v=" + vid
    t = None
    try:
        u = "https://www.youtube.com/oembed?format=json&url=" + quote_plus(url)
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=8) as r:
            d = json.load(r)
        if d.get("title"):
            t = {"titulo": d["title"], "canal": d.get("author_name") or ""}
    except Exception:
        pass
    if not t:
        try:
            with yt_dlp.YoutubeDL(dict(OPTS, skip_download=True, socket_timeout=15)) as ydl:
                info = ydl.extract_info(url, download=False)
            if info.get("duration"):
                DURS[vid] = info["duration"]
            t = {"titulo": info.get("title") or "", "canal": info.get("channel") or info.get("uploader") or ""}
        except Exception:
            return {"titulo": "", "canal": ""}
    if not t["titulo"]:
        return t
    if checar_live:
        t["live"] = eh_ao_vivo(vid)
    if len(TIT_CACHE) > 3000:
        TIT_CACHE.clear()
    TIT_CACHE[vid] = t
    return t


def listar_playlist(pid):
    if not re.fullmatch(r"[\w-]{12,}", pid or ""):
        raise ValueError("Playlist inválida")
    c = PL_CACHE.get(pid)
    if c and time.time() - c["t"] < 900:
        return c["d"]
    opts = dict(OPTS, noplaylist=False, extract_flat=True, skip_download=True)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info("https://www.youtube.com/playlist?list=" + pid, download=False)
    itens, vistos = [], set()
    for e in info.get("entries") or []:
        if not isinstance(e, dict):
            continue
        vid = e.get("id")
        if not vid or len(vid) != 11 or vid in vistos or indisponivel(e):
            continue
        vistos.add(vid)
        if e.get("duration"):
            DURS[vid] = e["duration"]
        guardar_tit(vid, e)
        dur = e.get("duration") or 0
        views = e.get("view_count") or 0
        tam_est = est_bytes(dur, CFG["formato"], CFG["qualidade"], CFG.get("res", 720))
        itens.append({"id": vid, "titulo": e.get("title") or "sem título", "dur": dur,
                      "canal": e.get("channel") or e.get("uploader") or "",
                      "views": f"{views:,}".replace(",", ".") if views else "",
                      "tamanho": tam_fmt(tam_est)})
    d = {"titulo": info.get("title") or "Playlist", "canal": info.get("uploader") or info.get("channel") or "", "itens": itens}
    if len(PL_CACHE) > 20:
        PL_CACHE.clear()
    PL_CACHE[pid] = {"t": time.time(), "d": d}
    return d


def _norm(t):
    return re.sub(r"[\W_]+", "", _sem_acento(t or "").lower())


INDEX = {}
NOMES = {"k": None, "t": 0, "s": set()}
REV = {}


def carregar_index():
    try:
        with open(INDEX_FILE, encoding="utf-8") as f:
            INDEX.update(json.load(f))
    except Exception:
        pass


def registrar(vid, caminho, kind):
    with LOCK:
        d = INDEX.setdefault(vid, {})
        cur = d.get(kind)
        if isinstance(cur, list):
            if caminho not in cur:
                cur.append(caminho)
        elif isinstance(cur, str):
            d[kind] = [cur, caminho] if cur != caminho else [cur]
        else:
            d[kind] = [caminho]
        NOMES["k"] = None
        REV.clear()
        try:
            _gravar(INDEX_FILE, INDEX)
        except OSError:
            pass


def kind_atual():
    return "v" if CFG["formato"] == "video" else "a"


def nomes_pasta(kind, r=None):
    r = r or raiz()
    k = (r, kind)
    if NOMES["k"] == k and time.time() - NOMES["t"] < 4:
        return NOMES["s"]
    exts = VIDEO_EXTS if kind == "v" else AUDIO_EXTS
    try:
        files = [f for f in os.listdir(os.path.realpath(r)) if f.lower().endswith(exts)]
    except OSError:
        files = []
    sset = {_norm(os.path.splitext(f)[0]) for f in files}
    NOMES.update(k=k, t=time.time(), s=sset)
    return sset


def ja_existe(vid, kind=None, pasta=None, sub=""):
    kind = kind or kind_atual()
    base = os.path.realpath(pasta or raiz())
    dest = os.path.realpath(os.path.join(base, sub)) if sub else base
    pths = (INDEX.get(vid) or {}).get(kind)
    if isinstance(pths, str):
        pths = [pths]
    for pth in (pths or []):
        if pth and os.path.isfile(pth):
            rp = os.path.realpath(pth)
            # só conta se estiver direto na pasta de destino (mesma pasta)
            if os.path.dirname(rp) == dest:
                return True
    t = TIT_CACHE.get(vid)
    if t and t.get("titulo"):
        n = _norm(t["titulo"])
        return bool(n) and n in nomes_pasta(kind, dest)
    return False


def _ss(b):
    return ((b[0] & 127) << 21) | ((b[1] & 127) << 14) | ((b[2] & 127) << 7) | (b[3] & 127)


def capa_mp3(pth):
    try:
        with open(pth, "rb") as f:
            h = f.read(10)
            if h[:3] != b"ID3":
                return None
            ver, flags = h[3], h[5]
            tag = f.read(min(_ss(h[6:10]), 8 * 1024 * 1024))
        pos = 0
        if flags & 0x40 and len(tag) >= 4:
            pos = _ss(tag[:4]) if ver == 4 else int.from_bytes(tag[:4], "big") + 4
        while pos + 10 <= len(tag):
            fid = tag[pos:pos + 4]
            if not fid.strip(b"\x00"):
                break
            raw = tag[pos + 4:pos + 8]
            n = _ss(raw) if ver == 4 else int.from_bytes(raw, "big")
            dados = tag[pos + 10:pos + 10 + n]
            pos += 10 + n
            if fid == b"APIC" and dados:
                enc = dados[0]
                i = dados.index(b"\x00", 1)
                j = i + 2
                if enc in (1, 2):
                    while j + 1 < len(dados) and dados[j:j + 2] != b"\x00\x00":
                        j += 2
                    j += 2
                else:
                    j = dados.index(b"\x00", j) + 1
                img = dados[j:]
                if img[:4] == b"\x89PNG":
                    return "image/png", img
                if img[:4] == b"RIFF":
                    return "image/webp", img
                return "image/jpeg", img
    except Exception:
        pass
    return None


FFMPEG = shutil.which("ffmpeg")
CAPA_LOCK = threading.Lock()
CAPA_NEG = {}


def _mime_img(b):
    if b[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if b[:4] == b"\x89PNG":
        return "image/png"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        return "image/webp"
    return None


def capa_mp4(pth):
    """Capa embutida em m4a/mp4 (atom covr)."""
    try:
        tam = os.path.getsize(pth)
        with open(pth, "rb") as f:
            buf = f.read(3 * 1024 * 1024)
            if b"covr" not in buf and tam > len(buf):
                f.seek(max(0, tam - 3 * 1024 * 1024))
                buf = f.read()
        i = buf.find(b"covr")
        d = buf.find(b"data", i) if i >= 0 else -1
        if d < 0 or d - i > 16:
            return None
        size = int.from_bytes(buf[d - 4:d], "big")
        img = buf[d + 12:d - 4 + size]
        m = _mime_img(img)
        return (m, img) if m else None
    except Exception:
        return None


def _cache_capa(pth):
    return os.path.join(CAPA_DIR, hashlib.sha1(os.path.realpath(pth).encode("utf-8", "ignore")).hexdigest() + ".jpg")


def _vid_do_arquivo(pth):
    if not REV:
        with LOCK:
            for v, d in INDEX.items():
                for p in d.values():
                    REV[os.path.realpath(p)] = v
    return REV.get(os.path.realpath(pth))


def _baixar_thumb(vid):
    for q in ("mqdefault", "hqdefault"):
        try:
            req = urllib.request.Request(f"https://i.ytimg.com/vi/{vid}/{q}.jpg", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                b = r.read()
            if len(b) > 2000 and _mime_img(b):
                return b
        except Exception:
            continue
    return None


def _vid_por_nome(pth):
    nome = re.sub(r"\s*\(\d+\)$", "", os.path.splitext(os.path.basename(pth))[0]).strip()
    if len(nome) < 3:
        return None
    with yt_dlp.YoutubeDL(dict(OPTS, extract_flat=True, skip_download=True, socket_timeout=10)) as ydl:
        info = ydl.extract_info(f"ytsearch1:{nome}", download=False)
    for e in info.get("entries") or []:
        if isinstance(e, dict) and len(e.get("id") or "") == 11:
            return e["id"]
    return None


def capa_de(pth):
    """Devolve (mime, bytes) da capa de um arquivo, ou None. Ordem:
    1) embutida no arquivo  2) imagem ao lado  3) cache  4) miniatura do YouTube  5) quadro do vídeo."""
    ext = os.path.splitext(pth)[1].lower()
    img = capa_mp3(pth) if ext == ".mp3" else capa_mp4(pth) if ext in (".m4a", ".mp4", ".aac") else None
    if img and img[1]:
        return img
    base = os.path.splitext(pth)[0]
    for e, m in ((".jpg", "image/jpeg"), (".jpeg", "image/jpeg"), (".png", "image/png"), (".webp", "image/webp")):
        if os.path.isfile(base + e):
            with open(base + e, "rb") as f:
                return m, f.read()
    cache = _cache_capa(pth)
    if os.path.isfile(cache):
        with open(cache, "rb") as f:
            return "image/jpeg", f.read()
    if CAPA_NEG.get(pth, 0) > time.time():
        return None
    eh_video = ext in VIDEO_EXTS
    vid = _vid_do_arquivo(pth)
    dados = _baixar_thumb(vid) if vid else None
    if not dados and eh_video and FFMPEG:
        try:
            r = subprocess.run([FFMPEG, "-y", "-v", "error", "-ss", "1", "-i", pth, "-vframes", "1", "-vf", "scale=480:-2",
                                "-c:v", "mjpeg", "-f", "image2pipe", "-"], capture_output=True, timeout=20)
            if len(r.stdout) > 1000 and _mime_img(r.stdout):
                dados = r.stdout
        except Exception:
            pass
    if not dados and not vid:
        with CAPA_LOCK:  # arquivos antigos sem ID: descobre pelo nome, um por vez
            if os.path.isfile(cache):
                with open(cache, "rb") as f:
                    return "image/jpeg", f.read()
            try:
                vid = _vid_por_nome(pth)
                time.sleep(0.3)
            except Exception:
                vid = None
            if vid:
                registrar(vid, os.path.realpath(pth), "v" if eh_video else "a")
                dados = _baixar_thumb(vid)
    if dados:
        try:
            os.makedirs(CAPA_DIR, exist_ok=True)
            with open(cache + ".tmp", "wb") as f:
                f.write(dados)
            os.replace(cache + ".tmp", cache)
        except OSError:
            pass
        return "image/jpeg", dados
    CAPA_NEG[pth] = time.time() + 600
    return None


ITENS = []
GEN = [0]
SESS = {"inicio": None, "fim": None, "tempo_dl": 0.0, "aviso": ""}
_prox = [1]
SOBRAS = re.compile(r"^\.(?:f\d+\.)?(?:temp\.)?(?:mp3|m4a|webm|mp4|opus|ogg|aac)(?:\.part(?:-Frag\d+)?)?(?:\.ytdl)?$|^\.(?:part.*|ytdl)$")


def aviso(m):
    SESS["aviso"] = m


def novo_item(url, sub="", forcar=False, pasta=None, fmt=None, qual=None, res=None, titulo=""):
    with LOCK:
        it = {"id": _prox[0], "url": url, "titulo": titulo or "", "status": "fila", "erro": "", "sub": sub, "forcar": forcar,
              "pct": 0, "vel": "Lendo título…", "cancel": False, "auto": False, "nome": None, "destino": None,
              "pasta": pasta or raiz(), "fmt": fmt or CFG["formato"], "qual": qual or CFG["qualidade"],
              "res": res or CFG.get("res", 720), "arq": "", "dur": DURS.get(chave(url), 0)}
        _prox[0] += 1
        ITENS.append(it)
        return it


def salvar_fila():
    with LOCK:
        pend = [{"url": i["url"], "sub": i["sub"], "forcar": i["forcar"], "pasta": i["pasta"],
                 "fmt": i["fmt"], "qual": i["qual"], "res": i["res"]}
                for i in ITENS if i["status"] in ("fila", "baixando")]
    try:
        _gravar(FILA_FILE, pend)
    except OSError:
        pass


def restaurar_fila():
    try:
        with open(FILA_FILE, encoding="utf-8") as f:
            pend = json.load(f)
    except Exception:
        return
    for p in pend:
        novo_item(p["url"], p.get("sub", ""), p.get("forcar", False), p.get("pasta"),
                  p.get("fmt"), p.get("qual"), p.get("res"))
    if pend:
        aviso(f"♻️ Fila restaurada automaticamente com {len(pend)} link(s). Continuando de onde parou.")


def nova_sessao():
    ITENS[:] = [i for i in ITENS if i["status"] == "falha"]
    SESS.update(inicio=None, fim=None, tempo_dl=0.0, aviso="")


def _pos(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def adicionar(texto, modo, de=None, ate=None, listas=None, titulos=None):
    g0 = GEN[0]
    links, rep, fora = extrair_links(texto)
    cortados = max(0, len(links) - MAX_LINKS)
    links = links[:MAX_LINKS]
    res = {"add": 0, "rep": rep, "fora": fora, "ja": 0, "playlists": 0, "erros": [], "cortados": cortados, "avisos": []}
    with LOCK:
        if not any(i["status"] in ("fila", "baixando") for i in ITENS):
            nova_sessao()
        ativos = {chave(i["url"]) for i in ITENS if i["status"] in ("fila", "baixando")}
    
    for l in links:
        if GEN[0] != g0:
            break
        if eh_playlist(l):
            try:
                titulo, urls = expandir_playlist(l)
            except Exception as ex:
                res["erros"].append(limpar_erro(ex)[:120])
                continue
            if not urls:
                res["erros"].append("Playlist vazia ou privada")
                continue
            if de is not None or ate is not None:
                urls = urls[max(0, (de or 1) - 1):(ate or None)]
                if not urls:
                    res["erros"].append("Esse intervalo está fora da playlist")
                    continue
            res["playlists"] += 1
            sub = titulo if modo == "pasta" else ""
        else:
            urls, sub = [l], ""
            
        for u in urls:
            if GEN[0] != g0:
                break
            k = chave(u)
            if k in ativos:
                res["rep"] += 1
                # sem nome - front mostra só a contagem
                continue
            if re.fullmatch(r"[\w-]{11}", k) and ja_existe(k, pasta=raiz(), sub=""):
                res["ja"] += 1
                # sem nome - front mostra só a contagem
                continue
            ativos.add(k)
            novo_item(u, sub, titulo=(titulos or {}).get(u) or (titulos or {}).get(chave(u)) or (TIT_CACHE.get(chave(u)) or {}).get('titulo') or '')
            res["add"] += 1
            
    for L in listas or []:
        ids = [v for v in (L.get("ids") or []) if re.fullmatch(r"[\w-]{11}", str(v))][:MAX_LINKS]
        if not ids:
            continue
        titulo = re.sub(r'[\\/:*?"<>|]', "", L.get("titulo") or "Playlist").strip()[:50] or "Playlist"
        sub = titulo if modo == "pasta" else ""
        res["playlists"] += 1
        for vid in ids:
            if GEN[0] != g0:
                break
            if vid in ativos:
                res["rep"] += 1
                # sem nome
                continue
            if ja_existe(vid, pasta=raiz(), sub=sub):
                res["ja"] += 1
                # sem nome
                continue
            ativos.add(vid)
            novo_item("https://www.youtube.com/watch?v=" + vid, sub, titulo=(titulos or {}).get(vid) or (titulos or {}).get("https://www.youtube.com/watch?v=" + vid) or (TIT_CACHE.get(vid) or {}).get("titulo") or "")
            res["add"] += 1
    salvar_fila()
    return res


def matar_ffmpeg():
    if not os.path.isdir("/proc"):
        return
    meu = os.getpid()
    for n in os.listdir("/proc"):
        if not n.isdigit():
            continue
        try:
            with open(f"/proc/{n}/stat") as f:
                if int(f.read().rsplit(")", 1)[1].split()[1]) != meu:
                    continue
            with open(f"/proc/{n}/cmdline", "rb") as f:
                if "ffmpeg" in f.read().decode(errors="ignore"):
                    os.kill(int(n), signal.SIGTERM)
        except Exception:
            pass


def limpar_cancelado(it):
    d, nome = it.get("destino"), it.get("nome")
    if not d or not nome or not os.path.isdir(d):
        return
    midia = VIDEO_EXTS if it.get("fmt") == "video" else AUDIO_EXTS
    finais = {e.lower() for e in midia + (".jpg", ".jpeg", ".png", ".webp")}
    try:
        for a in os.listdir(d):
            resto = a[len(nome):]
            if a.startswith(nome) and (SOBRAS.match(resto) or resto.lower() in finais):
                try:
                    os.remove(os.path.join(d, a))
                except OSError:
                    pass
    except OSError:
        pass
    limpar_pasta_vazia(os.path.join(d, nome))


def marcar(it, status, erro=""):
    with LOCK:
        it["status"], it["erro"] = status, erro
        if status == "ok":
            it["pct"] = 100
    salvar_fila()


def baixar(it, info, nome, destino):
    os.makedirs(destino, exist_ok=True)

    def hook(d):
        if it["cancel"]:
            raise RuntimeError("cancelado_pelo_usuario")
        if d["status"] == "downloading":
            it.setdefault("_td", time.monotonic())
            tot = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            it["pct"] = round((d.get("downloaded_bytes") or 0) / tot * 100) if tot else 0
            it["vel"] = tam_fmt(d.get("speed") or 0) + "/s"
        elif d["status"] == "finished":
            it.setdefault("_tf", time.monotonic())
            it["pct"], it["vel"] = 100, ("convertendo…" if it["fmt"] == "mp3" else "juntando…" if it["fmt"] == "video" else "")
            if it.get("_rap") and it.get("_rede"):
                rede_soltar(it)     # a rede já está livre: o próximo download pode começar enquanto este converte
                conv_pegar(it)

    ext_orig = (info.get("ext") or "").lower()

    def tentar(com_capa):
        opts = dict(OPTS, progress_hooks=[hook], concurrent_fragments=4, fragment_retries=3,
                    outtmpl=os.path.join(destino, nome.replace("%", "%%") + ".%(ext)s"))
        pps = []
        if it["fmt"] == "video":
            h = int(it.get("res") or 720)
            opts["format"] = (f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={h}]+bestaudio/"
                              f"best[height<={h}]/best")
            opts["merge_output_format"] = "mp4"
            if com_capa:
                pps.append({"key": "FFmpegMetadata", "add_metadata": True})
        elif it["fmt"] == "mp3":
            if com_capa:
                opts["writethumbnail"] = True
                pps.append({"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"})
            pps.append({"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": str(it["qual"])})
            if com_capa:
                pps.append({"key": "FFmpegMetadata", "add_metadata": True})
                pps.append({"key": "EmbedThumbnail"})
        elif com_capa:
            pps.append({"key": "FFmpegMetadata", "add_metadata": True})
            if ext_orig in ("m4a", "mp4", "mp3", "opus", "ogg", "mka", "flac"):
                opts["writethumbnail"] = True
                pps.insert(0, {"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"})
                pps.append({"key": "EmbedThumbnail"})
        if pps:
            opts["postprocessors"] = pps
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.process_ie_result(copy.deepcopy(info), download=True)

    def limpar_capas():
        for e in (".jpg", ".jpeg", ".png", ".webp"):
            try:
                os.remove(os.path.join(destino, nome + e))
            except OSError:
                pass

    try:
        tentar(True)
    except Exception as ex:
        m = str(ex).lower()
        if not it["cancel"] and "cancelado_pelo_usuario" not in m and any(
                x in m for x in ("thumbnail", "embed", "mutagen", "convert", "cover", "image", "picture", "metadata", "atom", "postprocess")):
            limpar_capas()
            tentar(False)
        else:
            raise
    limpar_capas()


def rel_do_arquivo(destino, nome, exts):
    r = os.path.realpath(raiz())
    for e in exts:
        p = os.path.realpath(os.path.join(destino, nome + e))
        if os.path.isfile(p) and p.startswith(r + os.sep):
            return os.path.relpath(p, r)
    return ""


# --------------------------------------------------------------------------- pausa / modo rápido / registro
PAUSA = {"on": False}
DEV = {"rapido": False, "freio": False, "log": [], "medidas": [], "gap": 1.5, "ult_rede": 0.0, "ok": 0, "falha": 0}
DEV_LOCK = threading.Lock()
REDE = threading.Semaphore(1)   # só um download de rede por vez (o YouTube vê o mesmo ritmo de pedidos)
CONV = threading.Semaphore(1)   # só uma conversão por vez


def dev_log(tipo, msg):
    with DEV_LOCK:
        DEV["log"].append({"t": time.strftime("%H:%M:%S"), "tipo": tipo, "msg": str(msg)[:400]})
        del DEV["log"][:-200]


def rapido_ligado():
    return bool(DEV["rapido"] and not DEV["freio"])


def definir_pausa(v):
    PAUSA["on"] = bool(v)
    dev_log("pausa", "Downloads pausados" if PAUSA["on"] else "Downloads retomados")
    aviso("⏸️ Downloads pausados. A música em andamento termina antes de parar." if PAUSA["on"] else "")


def definir_rapido(v):
    DEV["rapido"] = bool(v)
    if v:
        DEV["freio"] = False
    dev_log("modo", "Download mais rápido " + ("ligado" if v else "desligado"))


def acionar_freio(motivo):
    if DEV["rapido"] and not DEV["freio"]:
        DEV["freio"] = True
        dev_log("freio", "Voltando ao ritmo normal: " + motivo)


def _pegar(sem, it, chave):
    while not sem.acquire(timeout=0.5):
        if it["cancel"]:
            raise RuntimeError("cancelado_pelo_usuario")
    it[chave] = True


def rede_pegar(it):
    _pegar(REDE, it, "_rede")
    espera = DEV["gap"] - (time.time() - DEV["ult_rede"])
    if espera > 0:
        esperar(espera, lambda: it["cancel"])
    if it["cancel"]:
        rede_soltar(it)
        raise RuntimeError("cancelado_pelo_usuario")


def rede_soltar(it):
    if it.pop("_rede", False):
        DEV["ult_rede"] = time.time()
        REDE.release()


def conv_pegar(it):
    _pegar(CONV, it, "_conv")


def conv_soltar(it):
    if it.pop("_conv", False):
        CONV.release()


def dev_estado():
    with DEV_LOCK:
        med = list(DEV["medidas"][-20:])
        log = list(DEV["log"][-80:])
    n = len(med)
    media = {k: (round(sum(m[k] for m in med) / n, 1) if n else 0) for k in ("info", "dl", "conv", "espera", "total")}
    with LOCK:
        c = {}
        for i in ITENS:
            c[i["status"]] = c.get(i["status"], 0) + 1
    return {"rapido": DEV["rapido"], "freio": DEV["freio"], "pausado": PAUSA["on"], "medias": media, "n": n,
            "por_hora": round(3600 / media["total"]) if media["total"] else 0,
            "ok": DEV["ok"], "falha": DEV["falha"], "cont": c, "log": log}


def processar(it):
    if it["cancel"]:
        raise RuntimeError("cancelado_pelo_usuario")
    it.pop("_td", None)
    it.pop("_tf", None)
    it["_rap"] = bool(rapido_ligado() and it.get("fmt") == "mp3")
    it["_t"] = {"ini": time.monotonic(), "espera": 0.0}
    try:
        _processar(it)
    finally:
        rede_soltar(it)
        conv_soltar(it)


def _processar(it):
    t_ini = it["_t"]["ini"]
    if it["_rap"]:
        rede_pegar(it)
        it["_t"]["espera"] = time.monotonic() - t_ini
    titulo_preview = it.get("titulo") or ""
    it["vel"] = "Preparando…" if titulo_preview else "Lendo título…"
    try:
        info, titulo, base = obter_info(it["url"])
    except Exception:
        info, titulo, base = {}, titulo_preview, ""
    # se o titulo novo vier vazio / generico, mantém o do preview
    if not titulo or titulo.strip() in ("", "sem título"):
        titulo = titulo_preview
    if titulo:
        it["titulo"] = titulo
    if not base:
        # base a partir do titulo se obter_info falhou
        base = re.sub(r'[\\/:*?"<>|]', "", titulo_preview).strip()[:80] or "video"
    else:
        # se já tinha titulo do preview, usa ele como base do arquivo pra não ficar com nome do link
        pass
    if info.get("is_live") or info.get("live_status") in ("is_live", "is_upcoming"):
        raise RuntimeError("AO_VIVO")
    it["vel"] = "Baixando…"
    if info.get("duration"):
        it["dur"] = info["duration"]
        DURS[chave(it["url"])] = info["duration"]
    if it["cancel"]:
        raise RuntimeError("cancelado_pelo_usuario")
    r = it["pasta"]
    dest = os.path.join(r, it["sub"]) if it.get("sub") else r
    try: os.makedirs(dest, exist_ok=True)
    except OSError: pass
    exts = VIDEO_EXTS if it["fmt"] == "video" else AUDIO_EXTS
    ja = existe(dest, base, exts) or (bool(_norm(base)) and _norm(base) in nomes_pasta("v" if it["fmt"] == "video" else "a", dest))
    if ja and not it["forcar"]:
        marcar(it, "duplicada", "Já está na pasta")
        return
    nome = proximo_livre(dest, base, exts) if ja else base
    it["nome"] = nome
    it["destino"] = os.path.join(r, it["sub"]) if it["sub"] else r
    it["pct"] = 0
    t0 = time.monotonic()
    it["_t"]["info"] = t0 - t_ini - it["_t"]["espera"]
    baixar(it, info, nome, it["destino"])
    if it["cancel"]:
        raise RuntimeError("cancelado_pelo_usuario")
    t1 = time.monotonic()
    SESS["tempo_dl"] += t1 - t0
    tf = it.get("_tf") or t1
    it["_t"]["dl"] = tf - (it.get("_td") or t0)
    it["_t"]["conv"] = t1 - tf
    it["arq"] = rel_do_arquivo(it["destino"], nome, exts)
    for e in exts:
        pp = os.path.join(it["destino"], nome + e)
        if os.path.isfile(pp):
            registrar(chave(it["url"]), os.path.realpath(pp), "v" if it["fmt"] == "video" else "a")
            break
    marcar(it, "ok")
    tt = it["_t"]
    with DEV_LOCK:
        DEV["ok"] += 1
        DEV["medidas"].append({"info": max(0, tt.get("info", 0)), "dl": max(0, tt.get("dl", 0)), "conv": max(0, tt.get("conv", 0)),
                               "espera": max(0, tt.get("espera", 0)), "total": time.monotonic() - t_ini})
        del DEV["medidas"][:-60]
    for k in ("_tf", "_td"):
        it.pop(k, None)


def restantes():
    return sum(1 for i in ITENS if i["status"] == "fila")


def esperar(seg, parar=None):
    fim = time.time() + seg
    while time.time() < fim:
        if parar and parar():
            return False
        time.sleep(1)
    return True


def pegar():
    with LOCK:
        for i in ITENS:
            if i["status"] == "fila":
                i.update(status="baixando", pct=0, vel="Lendo título…", erro="", cancel=False)
                if SESS["inicio"] is None:
                    SESS["inicio"] = time.time()
                SESS["fim"] = None
                return i
    return None


def ocioso():
    with LOCK:
        if SESS["inicio"] and SESS["fim"] is None and not any(i["status"] == "baixando" for i in ITENS):
            SESS["fim"] = time.time()
    if not any(i["status"] == "baixando" for i in ITENS) and not PAUSA["on"]:
        aviso("")
    time.sleep(1)


def trabalhador(idx=0):
    feitos = 0
    while True:
        try:
            if idx == 1 and not rapido_ligado():
                time.sleep(1)
                continue
            if PAUSA["on"]:
                if restantes():
                    aviso("⏸️ Downloads pausados. Toque em Continuar para seguir.")
                time.sleep(1)
                continue
            it = pegar()
            if not it:
                feitos = 0
                ocioso()
                continue
            bloqueado = False
            for tent in (1, 2, 3):
                try:
                    processar(it)
                    break
                except Exception as ex:
                    erro = limpar_erro(ex)
                    if "AO_VIVO" in erro or "code 183" in erro or "code -183" in erro:
                        try:
                            limpar_cancelado(it)
                        except Exception:
                            pass
                        marcar(it, "falha", "Transmissão ao vivo: não dá para baixar")
                        break
                    if it["cancel"] or "cancelado_pelo_usuario" in erro:
                        limpar_cancelado(it)
                        marcar(it, "cancelada")
                        break
                    if passageiro(erro) and tent < 3:
                        if bloqueio_youtube(erro):
                            acionar_freio("YouTube pediu confirmação (bloqueio)")
                        dev_log("tentativa", "%s (%d/3): %s" % ((it.get("titulo") or it.get("url") or "")[:60], tent, erro[:160]))
                        esp = 60 * tent if bloqueio_youtube(erro) else 20 * tent
                        aviso(f"⏳ Falhou (tentativa {tent}/3). Tentando novamente em {esp} s.")
                        esperar(esp, lambda: it["cancel"])
                        aviso("")
                        continue
                    bloqueado = bloqueio_youtube(erro)
                    try:
                        limpar_cancelado(it)
                    except Exception:
                        pass
                    if bloqueado:
                        acionar_freio("YouTube bloqueou temporariamente")
                    dev_log("erro", "%s: %s" % ((it.get("titulo") or it.get("url") or "")[:60], erro[:200]))
                    DEV["falha"] += 1
                    marcar(it, "falha", "YouTube bloqueou temporariamente (confirmação necessária)" if bloqueado else erro[:150])
                    break
            feitos += 1
            resta = restantes()
            if resta == 0:
                feitos = 0
            elif bloqueado:
                feitos = 0
                dev_log("pausa", "Pausa de 5 minutos para o YouTube esfriar")
                aviso("⏸️ Pausando 5 minutos para o YouTube esfriar. A fila continuará em seguida.")
                esperar(300, lambda: restantes() == 0)
            elif it.get("_rap") and rapido_ligado():
                pass    # no modo rápido o intervalo entre downloads é controlado pela rede (rede_pegar)
            elif feitos >= CFG["lote"]:
                feitos = 0
                aviso(f"☕ Pausa de {CFG['pausa_lote']} s para estabilidade. Faltam {resta} itens.")
                esperar(CFG["pausa_lote"], lambda: restantes() == 0)
            else:
                time.sleep(calcular_pausa(resta + feitos))
            aviso("")
        except Exception as ex:
            aviso(f"Erro interno: {limpar_erro(ex)[:100]}")
            time.sleep(2)


def acao(d):
    a, iid = d.get("acao"), d.get("id")
    with LOCK:
        it = next((i for i in ITENS if i["id"] == iid), None)
        if a == "cancelar_tudo":
            GEN[0] += 1
            n = 0
            for i in ITENS:
                if i["status"] in ("fila", "baixando"):
                    n += 1
                    if i["status"] == "baixando":
                        i["cancel"] = True
                        i["vel"] = "Cancelando…"
            ITENS[:] = [i for i in ITENS if i["status"] not in ("fila",)]
            if n:
                matar_ffmpeg()
        elif a == "limpar":
            ITENS[:] = [i for i in ITENS if i["status"] in ("fila", "baixando", "falha")]
        elif it and a == "remover":
            if it["status"] == "baixando":
                it["cancel"] = True
                it["vel"] = "Cancelando…"
                matar_ffmpeg()
            else:
                ITENS.remove(it)
        elif it and a == "forcar" and it["status"] in ("duplicada", "cancelada", "falha"):
            it.update(status="fila", forcar=True, auto=True, cancel=False)
        elif it and a == "retentar" and it["status"] == "falha":
            it.update(status="fila", auto=True, cancel=False)
    salvar_fila()
    return {"ok": True}


def estado():
    with LOCK:
        c = Counter(i["status"] for i in ITENS)
        ini, fim = SESS["inicio"], SESS["fim"]
        at = next((i for i in ITENS if i["status"] == "baixando"), None)
        out = {"itens": [{k: i[k] for k in ("id", "url", "titulo", "status", "erro", "sub", "pct", "vel", "arq")} for i in ITENS],
               "total": len(ITENS), "dec": ((fim or time.time()) - ini) if ini else 0, "aviso": SESS["aviso"],
               "agora": (at["titulo"] or at["url"]) if at else "",
               "pasta": CFG["atual"], "qualidade": CFG["qualidade"]}
        for k in ("fila", "baixando", "ok", "falha", "duplicada", "cancelada"):
            out[k] = c.get(k, 0)
        alvo = [i for i in ITENS if i["status"] in ("fila", "baixando", "ok")]
        out["est"] = sum(est_bytes(i["dur"], i["fmt"], i["qual"], i["res"]) for i in alvo)
        out["est_sem"] = sum(1 for i in alvo if not i["dur"])
        return out


def lista_biblioteca():
    r = raiz()
    out = {"musicas": [], "playlists": [], "videos": []}
    playlists_map = {}

    for c in listar_mp3(r, EXTS):
        rel = os.path.relpath(c, r)
        p = os.path.dirname(rel)
        try:
            tam = os.path.getsize(c)
        except OSError:
            continue
        ext = os.path.splitext(c)[1].lower()
        nome_arq = os.path.splitext(os.path.basename(c))[0]
        
        item = {"rel": rel, "nome": nome_arq, "pasta": "" if p == "." else p, "tam": tam}
        
        if ext in VIDEO_EXTS:
            if p and p != ".":
                playlists_map.setdefault(p, []).append(item)
            else:
                out["videos"].append(item)
        else:
            if p and p != ".":
                playlists_map.setdefault(p, []).append(item)
            else:
                out["musicas"].append(item)

    pl_formatadas = []
    for pl_nome, itens in playlists_map.items():
        tem_mp4 = any(i["rel"].lower().endswith(VIDEO_EXTS) for i in itens)
        pl_formatadas.append({
            "nome": pl_nome,
            "total": len(itens),
            "primeira_musica": itens[0]["nome"],
            "primeira_rel": itens[0]["rel"],
            "tem_mp4": tem_mp4,
            "itens": itens
        })
    out["playlists"] = pl_formatadas
    out["pasta"] = CFG["atual"]
    out["caminho"] = r
    return out


def apagar(rels):
    n = 0
    NOMES["k"] = None
    for rel in rels:
        p = caminho_seguro(rel)
        if p and p.lower().endswith(EXTS) and os.path.isfile(p):
            try:
                os.remove(p)
                limpar_pasta_vazia(p)
                n += 1
            except OSError:
                pass
    return {"apagadas": n}


def _sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not 0x300 <= ord(c) <= 0x36F)


def chave_repetida(nome):
    t = _sem_acento(os.path.splitext(nome)[0]).lower()
    t = re.sub(r"(\s*\(\d+\))+\s*$", "", t)
    return re.sub(r"\s+", " ", t).strip()


def chave_parecida(nome):
    t = _sem_acento(os.path.splitext(nome)[0]).lower()
    t = re.sub(r"[\(\[][^\)\]]*[\)\]]", " ", t)
    return re.sub(r"[\W_]+", " ", t).strip()


def _mtime(c):
    try:
        return os.path.getmtime(c)
    except OSError:
        return 0


def duracao_seg(c):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", c],
                           capture_output=True, text=True, timeout=20)
        return float(r.stdout.strip())
    except Exception:
        return None


def varrer_repetidas():
    r = raiz()
    por = {}
    for c in listar_mp3(r, (".mp3",)):
        por.setdefault((os.path.dirname(c), c.lower().endswith(VIDEO_EXTS), chave_repetida(os.path.basename(c)) or c), []).append(c)
    certas, reps = [], []
    for k in sorted(por):
        l = sorted(por[k])
        if len(l) > 1:
            pool = [c for c in l if not re.search(r"\(\d+\)\.\w+$", c, re.I)] or l
            manter = min(pool, key=lambda c: (_mtime(c), len(os.path.basename(c))))
            certas.append({"tipo": "certa", "arq": l, "manter": manter})
            reps.append(manter)
        else:
            reps.append(l[0])
    par = {}
    for c in reps:
        k = chave_parecida(os.path.basename(c))
        if len(k) >= 3:
            par.setdefault((os.path.dirname(c), c.lower().endswith(VIDEO_EXTS), k), []).append(c)
    talvez = [{"tipo": "talvez", "arq": sorted(l), "manter": None} for _, l in sorted(par.items()) if len(l) > 1]
    brutos = certas + talvez
    todos = list(dict.fromkeys(c for g in brutos for c in g["arq"]))
    with ThreadPoolExecutor(max_workers=4) as ex:
        dur = dict(zip(todos, ex.map(duracao_seg, todos)))
    grupos = []
    for g in brutos:
        ds = [dur[c] for c in g["arq"] if dur[c] is not None]
        dif = len(ds) > 1 and max(ds) - min(ds) > 2
        auto = g["tipo"] == "certa" and not dif
        grupos.append({"tipo": g["tipo"], "dif": dif, "sem_dur": len(ds) < 2, "arquivos": [
            {"rel": os.path.relpath(c, r), "nome": os.path.splitext(os.path.basename(c))[0], "dur": dur[c],
             "tam": os.path.getsize(c) if os.path.exists(c) else 0,
             "pasta": "" if os.path.dirname(os.path.relpath(c, r)) in ("", ".") else os.path.dirname(os.path.relpath(c, r)),
             "marcada": bool(auto and c != g["manter"])} for c in g["arq"]]})
    return {"grupos": grupos}


def criar_zip(rels):
    arqs = []
    for rel in list(rels)[:3000]:
        p = caminho_seguro(rel)
        if p and p.lower().endswith(EXTS) and os.path.isfile(p):
            arqs.append((p, rel))
    if not arqs:
        raise ValueError("Nenhum arquivo para colocar no ZIP")
    os.makedirs(ZIP_DIR, exist_ok=True)
    agora = time.time()
    for n in os.listdir(ZIP_DIR):
        try:
            f = os.path.join(ZIP_DIR, n)
            if agora - os.path.getmtime(f) > 1800:
                os.remove(f)
        except OSError:
            pass
    tok = uuid.uuid4().hex
    nome = "WaveFly-" + time.strftime("%Y%m%d-%H%M") + ".zip"
    with zipfile.ZipFile(os.path.join(ZIP_DIR, tok + ".zip"), "w", zipfile.ZIP_STORED) as z:
        for p, rel in arqs:
            z.write(p, rel.replace(os.sep, "/"))
    return {"url": "/api/zipdl?t=" + tok + "&n=" + quote_plus(nome), "nome": nome, "qtd": len(arqs)}


def faxina():
    while True:
        time.sleep(600)
        agora = time.time()
        try:
            for c in listar_mp3(raiz()):
                if agora - _mtime(c) > HORAS_SERVIDOR * 3600:
                    try:
                        os.remove(c)
                        limpar_pasta_vazia(c)
                    except OSError:
                        pass
        except Exception:
            pass


def navegar(p):
    p = os.path.abspath(os.path.expanduser(p or raiz()))
    while not os.path.isdir(p) and os.path.dirname(p) != p:
        p = os.path.dirname(p)
    dirs, erro = [], ""
    try:
        for n in sorted(os.listdir(p), key=str.lower):
            c = os.path.join(p, n)
            if not n.startswith(".") and os.path.isdir(c):
                dirs.append({"nome": n, "caminho": c})
    except OSError:
        erro = "Sem permissão para abrir esta pasta." + (" Permita o acesso aos arquivos nas configurações do Android e tente de novo." if ANDROID else "")
    base = "/storage/emulated/0" if ANDROID else os.path.expanduser("~")
    cand = [("📱 Armazenamento" if ANDROID else "🏠 Início", base), ("🎵 Music", os.path.join(base, "Music")),
            ("⬇️ Download" if ANDROID else "⬇️ Downloads", os.path.join(base, "Download" if ANDROID else "Downloads"))]
    pai = os.path.dirname(p)
    return {"caminho": p, "pai": pai if pai != p else None, "dirs": dirs, "erro": erro,
            "atalhos": [{"nome": n, "caminho": c} for n, c in cand if os.path.isdir(c)]}


def nova_pasta(pai, nome):
    nome = (nome or "").strip()
    if not nome or nome in (".", "..") or any(c in nome for c in '/\\:*?"<>|'):
        raise ValueError("Nome de pasta inválido")
    novo = os.path.join(pai, nome)
    os.makedirs(novo, exist_ok=True)
    return navegar(novo)


def aplicar_cfg(d):
    if SERVIDOR and any(k in d for k in ("atual", "usar_caminho", "add_pasta", "del_pasta")):
        raise ValueError("No modo servidor a pasta é fixa")
    with LOCK:
        if "atual" in d:
            if d["atual"] not in CFG["pastas"]:
                raise ValueError("Essa pasta não existe")
            CFG["atual"] = d["atual"]
            os.makedirs(raiz(), exist_ok=True)
        if d.get("formato") in ("mp3", "original", "video"):
            CFG["formato"] = d["formato"]
        if d.get("qualidade") in (128, 192, 320):
            CFG["qualidade"] = int(d["qualidade"])
        if d.get("res") in (360, 720, 1080):
            CFG["res"] = d["res"]
        if d.get("modo_playlist") in ("pasta", "junto"):
            CFG["modo_playlist"] = d["modo_playlist"]
        if d.get("usar_caminho"):
            cam = os.path.abspath(os.path.expanduser(d["usar_caminho"]))
            os.makedirs(cam, exist_ok=True)
            nome = next((n for n, p in CFG["pastas"].items() if os.path.abspath(p) == cam), None)
            if not nome:
                base = os.path.basename(cam.rstrip(os.sep)) or "Pasta"
                nome, k = base, 2
                while nome in CFG["pastas"]:
                    nome, k = f"{base} ({k})", k + 1
                CFG["pastas"][nome] = cam
            CFG["atual"] = nome
        if d.get("add_pasta"):
            nome = (d["add_pasta"].get("nome") or "").strip()
            cam = os.path.expanduser((d["add_pasta"].get("caminho") or "").strip())
            if not nome or not cam:
                raise ValueError("Preencha o nome e o caminho da pasta")
            os.makedirs(cam, exist_ok=True)
            CFG["pastas"][nome] = cam
        if d.get("del_pasta"):
            n = d["del_pasta"]
            if n == CFG["atual"]:
                raise ValueError("Troque para outra pasta antes de remover esta")
            if len(CFG["pastas"]) <= 1:
                raise ValueError("Precisa sobrar pelo menos uma pasta")
            CFG["pastas"].pop(n, None)
        salvar_cfg()
        return cfg_publica()


def pasta_ok():
    r = raiz()
    return os.path.isdir(r) and os.access(r, os.W_OK)


def cfg_publica():
    return {"servidor": SERVIDOR, "res": CFG["res"], "primeira": PRIMEIRA, "pasta_ok": pasta_ok(), "android": ANDROID, "pastas": CFG["pastas"], "atual": CFG["atual"], "caminho": raiz(), "qualidade": CFG["qualidade"],
            "formato": CFG["formato"], "modo_playlist": CFG["modo_playlist"],
            "max_links": MAX_LINKS, "app": APP_NOME}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _bytes(self, b, ctype, code=200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _json(self, obj, code=200):
        self._bytes(json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8", code)

    def _host_ok(self):
        h = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        return LIBERADO or h in ("localhost", "127.0.0.1", "[::1]")

    def do_GET(self):
        try:
            if not self._host_ok():
                return self._json({"erro": "host inválido"}, 403)
            u = urlparse(self.path)
            q, p = parse_qs(u.query), u.path
            if p == "/":
                return self._bytes(HTML.replace("{{APP}}", APP_NOME).encode(), "text/html; charset=utf-8")
            if p == "/manifest.json":
                return self._json({"name": APP_NOME, "short_name": APP_NOME, "start_url": "/", "display": "standalone",
                                   "background_color": "#f3e6cc", "theme_color": "#f3e6cc",
                                   "icons": [{"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"}]})
            if p == "/icon.svg":
                return self._bytes(ICON.encode(), "image/svg+xml")
            if p == "/api/estado":
                return self._json(estado())
            if p == "/api/config":
                return self._json(cfg_publica())
            if p == "/api/arquivos":
                return self._json(lista_biblioteca())
            if p == "/api/buscar":
                termo = (q.get("q") or [""])[0].strip()[:100]
                if len(termo) < 3:
                    return self._json({"erro": "Digite pelo menos 3 letras"}, 400)
                try:
                    ini = max(0, int((q.get("inicio") or ["0"])[0]))
                except ValueError:
                    ini = 0
                try:
                    n = min(30, max(1, int((q.get("n") or ["10"])[0])))
                except ValueError:
                    n = 10
                tp = (q.get("tipo") or ["musica"])[0]
                r = busca_paginada(tp, termo, ini, n)
                if tp != "playlist":
                    r = dict(r, itens=[dict(x, ja=ja_existe(x["id"])) for x in r["itens"]])
                return self._json(r)
            if p == "/api/playlist":
                d = listar_playlist((q.get("id") or [""])[0])
                return self._json(dict(d, itens=[dict(x, ja=ja_existe(x["id"])) for x in d["itens"]]))
            if p == "/api/navegar":
                return self._json(navegar((q.get("p") or [""])[0]))
            if p == "/api/audio":
                return self._audio((q.get("f") or [""])[0])
            if p == "/api/baixar":
                return self._audio((q.get("f") or [""])[0], anexo=True)
            if p == "/api/zipdl":
                t = (q.get("t") or [""])[0]
                if not re.fullmatch(r"[0-9a-f]{32}", t):
                    return self._json({"erro": "arquivo não encontrado"}, 404)
                nome = re.sub(r"[^\w .-]", "", (q.get("n") or ["WaveFly.zip"])[0])[:60] or "WaveFly.zip"
                return self._audio("", anexo=True, abs_path=os.path.join(ZIP_DIR, t + ".zip"), nome=nome)
            if p == "/api/titulo":
                return self._json(titulo_rapido((q.get("id") or [""])[0], bool((q.get("live") or [""])[0])))
            if p == "/api/existe":
                ids = [v for v in (q.get("ids") or [""])[0].split(",") if re.fullmatch(r"[\w-]{11}", v)][:400]
                import urllib.parse as _up; _q=_up.parse_qs(_up.urlparse(self.path).query); _sub=_q.get("sub",[""])[0]; return self._json({"ja": [v for v in ids if ja_existe(v, pasta=raiz(), sub=_sub)]})
            if p == "/api/capa":
                return self._capa((q.get("f") or [""])[0])
            self._json({"erro": "não encontrado"}, 404)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as ex:
            try:
                self._json({"erro": limpar_erro(ex)[:200]}, 500)
            except Exception:
                pass

    def do_POST(self):
        try:
            if not self._host_ok() or self.headers.get("X-Requested-With") != "wavefly":
                return self._json({"erro": "requisição bloqueada"}, 403)
            n = int(self.headers.get("Content-Length") or 0)
            d = json.loads(self.rfile.read(n) or b"{}")
            p = urlparse(self.path).path
            if p == "/api/add":
                return self._json(adicionar(d.get("texto", ""), d.get("modo") or CFG["modo_playlist"], _pos(d.get("de")), _pos(d.get("ate")), d.get("listas")))
            if p == "/api/zip":
                return self._json(criar_zip(d.get("rels") or []))
            if p == "/api/acao":
                return self._json(acao(d))
            if p == "/api/config":
                return self._json(aplicar_cfg(d))
            if p == "/api/apagar":
                return self._json(apagar(d.get("rels") or []))
            if p == "/api/novapasta":
                return self._json(nova_pasta(d.get("pai", ""), d.get("nome", "")))
            if p == "/api/repetidas":
                return self._json(varrer_repetidas())
            if p == "/api/limparbusca":
                with BUSCA_LOCK:
                    BUSCA.clear()
                PL_CACHE.clear()
                return self._json({"ok": True})
            self._json({"erro": "não encontrado"}, 404)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as ex:
            try:
                self._json({"erro": limpar_erro(ex)[:200]}, 400)
            except Exception:
                pass

    def _capa(self, rel):
        pth = caminho_seguro(rel)
        img = capa_de(pth) if pth and os.path.isfile(pth) else None
        if not img:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.send_header("Cache-Control", "private, max-age=300")
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", img[0])
        self.send_header("Content-Length", str(len(img[1])))
        self.send_header("Cache-Control", "private, max-age=86400")
        self.end_headers()
        self.wfile.write(img[1])

    def _audio(self, rel, anexo=False, abs_path=None, nome=None):
        p = abs_path or caminho_seguro(rel)
        if not p or not os.path.isfile(p):
            return self._json({"erro": "arquivo não encontrado"}, 404)
        tam = os.path.getsize(p)
        ini, fim, code = 0, tam - 1, 200
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range") or "")
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                ini = int(m.group(1))
                fim = int(m.group(2)) if m.group(2) else tam - 1
            else:
                ini = max(0, tam - int(m.group(2)))
            fim = min(fim, tam - 1)
            code = 206
        self.send_response(code)
        self.send_header("Content-Type", MIME.get(os.path.splitext(p)[1].lower(), "audio/mpeg"))
        self.send_header("Accept-Ranges", "bytes")
        if anexo:
            self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + quote(nome or os.path.basename(p)))
        self.send_header("Content-Length", str(max(0, fim - ini + 1)))
        if code == 206:
            self.send_header("Content-Range", f"bytes {ini}-{fim}/{tam}")
        self.end_headers()
        with open(p, "rb") as f:
            f.seek(ini)
            resto = fim - ini + 1
            while resto > 0:
                ch = f.read(min(65536, resto))
                if not ch:
                    break
                self.wfile.write(ch)
                resto -= len(ch)


ICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="110" fill="#f3e3c3"/>'
        '<rect x="56" y="136" width="400" height="240" rx="28" fill="#f1dfb8" stroke="#4a2a17" stroke-width="16"/>'
        '<rect x="92" y="170" width="328" height="96" rx="12" fill="#e8873a" stroke="#4a2a17" stroke-width="8"/>'
        '<rect x="136" y="288" width="240" height="64" rx="32" fill="#3b2314"/>'
        '<circle cx="196" cy="320" r="22" fill="#f1dfb8"/><circle cx="316" cy="320" r="22" fill="#f1dfb8"/></svg>')

HTML = r'''<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="color-scheme" content="dark light"><meta name="theme-color" content="#f3e6cc" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#1f1510" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="/manifest.json"><link rel="icon" href="/icon.svg">
<title>{{APP}}</title>
<style>
:root{color-scheme:light;--bg:#f3e6cc;--cd:#fbf3e1;--sf:#ead9b6;--sf2:#d8c299;--on:#fbf3e1;--ln:#dcc9a0;--fg:#3b2314;--mut:#8a6f55;--ac:#d9692a;--ac2:#e8a15f;--at:#b4501a;--acs:#f7e1c0;--err:#b5402a;--yt:#d9692a;--ink:#2f1a0e;--bd:#6b4a33;--ol:#9aa571;--yl:#e0b25c;--sh:0 6px 16px rgb(80 45 15 / .14),0 1px 2px rgb(80 45 15 / .12)}
@media(prefers-color-scheme:dark){:root{color-scheme:dark;--bg:#1f1510;--cd:#2b1d15;--sf:#38271c;--sf2:#4a352a;--on:#38271c;--ln:#4a3528;--fg:#f3e6cc;--mut:#b39b82;--ac:#e07a35;--ac2:#eaa45f;--at:#f0b27a;--acs:#3d2a1c;--err:#e58a72;--yt:#e07a35;--ink:#120b07;--bd:#8a6a52;--ol:#b0ba84;--yl:#e3bd72;--sh:0 6px 16px rgb(0 0 0 / .4)}}
*{box-sizing:border-box;margin:0;-webkit-tap-highlight-color:transparent}
[hidden]{display:none!important}
html{overflow-x:hidden}
button{transition:opacity .15s,transform .15s}
body{position:relative;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased;padding:0 16px calc(140px + env(safe-area-inset-bottom));overflow-x:hidden}

svg.i{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;display:block}
.w{max-width:560px;margin:0 auto;position:relative;z-index:1}
header{display:flex;align-items:center;gap:12px;padding:calc(16px + env(safe-area-inset-top)) 0 12px}
.mk{width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,var(--ac),var(--ac2));color:#fff;display:grid;place-items:center;box-shadow:0 4px 12px color-mix(in srgb,var(--ac) 30%,transparent)}.mk svg{width:22px;height:22px}
.wm{font-size:20px;font-weight:700;letter-spacing:-.5px}.wm i{font-style:normal;color:var(--ac)}
.sp1{flex:1}
.ib{width:38px;height:38px;padding:0;border-radius:12px;display:grid;place-items:center;background:var(--cd);border:1px solid var(--ln);color:var(--fg)}
.tabs{display:flex;gap:4px;background:var(--sf);border-radius:14px;padding:3px;margin-bottom:4px;border:1px solid var(--ln)}
.tabs a{flex:1;display:flex;align-items:center;justify-content:center;gap:6px;padding:9px 4px;border-radius:11px;color:var(--mut);font-size:14px;font-weight:600;cursor:pointer}
.tabs a svg.i{width:16px;height:16px}
.tabs a.on{background:var(--cd);color:var(--at);box-shadow:var(--sh)}
.cb{display:inline-block;font-size:11px;background:var(--ac);color:#fff;padding:0 6px;border-radius:99px;font-weight:700}
.v{animation:fd .2s ease}
@keyframes fd{from{opacity:0;transform:translateY(6px)}}
h1{font-size:24px;font-weight:700;letter-spacing:-.5px;line-height:1.2;margin:18px 0 4px}h2{font-size:18px;letter-spacing:-.3px;margin:4px 0 2px}
.sub{color:var(--mut);font-size:14px;margin-bottom:14px}
button{font:inherit;color:var(--fg);background:var(--sf);border:0;border-radius:12px;padding:10px 14px;cursor:pointer}
button:active{opacity:.7;transform:scale(0.98)}button:disabled{opacity:.4}
button.p{background:linear-gradient(135deg,var(--ac),var(--ac2));color:#fff;font-weight:600;padding:14px;width:100%;border-radius:14px;margin-top:12px;font-size:15px;box-shadow:0 4px 12px color-mix(in srgb,var(--ac) 25%,transparent)}
button.s2{display:inline-flex;align-items:center;gap:8px;background:var(--cd);border:1px solid var(--ln);font-weight:600}
button.t{background:none;padding:4px 6px;color:var(--mut);font-size:13.5px;white-space:nowrap}
button.more{display:block;width:100%;margin:12px 0 4px;padding:12px;font-weight:600;color:var(--at);background:var(--cd);border:1px solid var(--ln);border-radius:12px}
textarea,input[type=text],input[type=number]{width:100%;background:var(--cd);border:1px solid var(--ln);border-radius:14px;color:var(--fg);padding:12px 14px;font:inherit;font-size:14.5px;outline:none}
textarea:focus,input[type=text]:focus{border-color:var(--ac);box-shadow:0 0 0 3px color-mix(in srgb,var(--ac) 15%,transparent)}
textarea{min-height:120px;resize:vertical}
input[type=checkbox]{width:18px;height:18px;accent-color:var(--ac);flex:none;border-radius:4px}
.mut{color:var(--mut)}.sm{font-size:13px}.er{color:var(--err)}
.row{display:flex;gap:8px;align-items:center;justify-content:space-between}
.chip{display:flex;justify-content:space-between;align-items:center;width:100%;background:var(--cd);border:1px solid var(--ln);box-shadow:var(--sh);border-radius:14px;padding:12px 14px;margin-top:10px;text-align:left}.chip b{font-weight:600;font-size:14.5px}.chip span{color:var(--at);font-size:13.5px;font-weight:600;white-space:nowrap}
.hello,.warn{border-radius:14px;padding:12px 14px;margin:12px 0 0;font-size:13.5px}
.hello{background:var(--acs)}.warn{background:color-mix(in srgb,var(--err) 12%,transparent);color:var(--err)}
.hello .row{justify-content:flex-end;margin-top:4px}
code{font:12.5px ui-monospace,Menlo,monospace;background:var(--sf2);padding:1px 5px;border-radius:5px;color:var(--fg)}
.pvl{margin-top:8px}.pr{display:flex;gap:10px;align-items:center;padding:6px 0}
.ft{width:44px;height:44px;border-radius:10px;object-fit:cover;background:var(--sf);flex:none}.ft.s{width:52px;height:30px;border-radius:6px}
.plc{background:var(--cd);border:1px solid var(--ln);box-shadow:var(--sh);border-radius:14px;padding:10px 12px;margin-top:8px}
.plh{display:flex;gap:10px;align-items:center}
.bar{height:5px;background:var(--sf2);border-radius:5px;overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--ac),var(--ac2));width:0;transition:width .3s;border-radius:5px}
.sec{margin-top:24px}.aviso{margin:6px 0;padding:10px 12px;background:var(--acs);border-radius:10px;font-size:13px}
.deliver{background:var(--cd);border:1px solid var(--ln);border-radius:14px;padding:12px 14px;margin:10px 0}.deliver .row{margin-top:8px;justify-content:stretch}.deliver button{flex:1}.deliver button.a{background:var(--ac);color:#fff;font-weight:600}



.it{display:flex;gap:10px;align-items:center;padding:8px 0}.it .bd{flex:1;min-width:0}.tt{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:14px}.tt.d{color:var(--mut)}
.lh{display:flex;justify-content:space-between;align-items:center;margin:16px 0 4px;color:var(--mut);font-size:12.5px;font-weight:700}
.lr{display:flex;align-items:center;gap:10px;padding:8px 0}.lr label{flex:1;min-width:0;display:flex;align-items:center;gap:10px;cursor:pointer}.nm{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:14px}
.srch{display:flex;gap:8px;margin-top:10px}.srch .ip{flex:1;position:relative}.srch input{padding-left:40px;padding-right:40px}
.srch .ip>span{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--mut);pointer-events:none}.srch .ip>span svg.i{width:16px;height:16px}
#qx{position:absolute;right:6px;top:50%;transform:translateY(-50%);width:30px;height:30px;padding:0;display:grid;place-items:center;border-radius:50%;background:var(--sf);color:var(--mut)}#qx svg.i{width:14px;height:14px}
.srch>button{flex:none;padding:0 18px;background:linear-gradient(135deg,var(--ac),var(--ac2));color:#fff;font-weight:600;border-radius:14px}
.rs,.pc,.tr{display:flex;gap:10px;align-items:center;padding:8px 0}.rs{cursor:pointer}.bd2{flex:1;min-width:0}
.th{position:relative;width:68px;height:38px;border-radius:8px;overflow:hidden;background:var(--sf);flex:none}.th img{width:100%;height:100%;object-fit:cover;display:block}
.tr img{width:52px;height:30px;object-fit:cover;border-radius:6px;flex:none}
.pp{position:absolute;inset:0;width:100%;height:100%;padding:0;border-radius:0;background:#00000040;color:#fff;display:grid;place-items:center;opacity:0}.pp svg.i{width:16px;height:16px}
.rs:hover .pp,.pp.on{opacity:1}@media(hover:none){.pp{opacity:1}}
.pv{margin:2px 0 8px}.pv iframe{width:100%;aspect-ratio:16/9;border:0;border-radius:14px;background:#000;display:block}
.sbar{position:sticky;top:calc(8px + env(safe-area-inset-top));z-index:8;background:linear-gradient(135deg,var(--ac),var(--ac2));color:#fff;border-radius:14px;padding:6px 6px 6px 14px;display:flex;justify-content:space-between;align-items:center;margin:12px 0 4px;font-weight:600;font-size:14px;box-shadow:0 4px 12px color-mix(in srgb,var(--ac) 25%,transparent)}
.sbar small{display:block;font-size:11.5px;font-weight:400;opacity:.9}
.sbar button,.sel button{background:none;color:#fff;font-weight:600}.sbar .pb{background:#fff;color:#0369a1;font-weight:700}
#tray{background:var(--cd);border:1px solid var(--ln);border-radius:14px;padding:4px 12px;margin:4px 0 6px;max-height:240px;overflow:auto}
.sel{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(12px + env(safe-area-inset-bottom));width:min(540px,calc(100% - 32px));background:linear-gradient(135deg,var(--ac),var(--ac2));color:#fff;border-radius:14px;padding:6px 6px 6px 14px;display:flex;justify-content:space-between;align-items:center;z-index:10;font-weight:600;font-size:14px}
.empty{text-align:center;color:var(--mut);padding:32px 10px}.empty svg{width:48px;height:48px;color:var(--ac);margin:0 auto 8px;display:block}
.sg{display:inline-flex;background:var(--sf);border-radius:12px;padding:2px;border:1px solid var(--ln)}
.sg button{background:none;padding:8px 12px;font-size:13.5px;color:var(--mut);border-radius:10px}.sg button.on{background:var(--cd);color:var(--at);font-weight:600;box-shadow:var(--sh)}
.sg.full{display:flex;width:100%}.sg.full button{flex:1;padding:10px 4px}
.sheet{position:fixed;inset:0;background:rgba(0,0,0,.4);display:flex;align-items:flex-end;justify-content:center;z-index:45;opacity:0;pointer-events:none;transition:opacity .2s}.sheet.on{opacity:1;pointer-events:auto}
.spn{background:var(--bg);width:min(560px,100%);max-height:85vh;overflow:auto;border-radius:24px 24px 0 0;padding:10px 18px calc(20px + env(safe-area-inset-bottom));transform:translateY(30px);transition:transform .25s ease}.sheet.on .spn{transform:none}
.grip{width:36px;height:4px;border-radius:4px;background:var(--sf2);margin:0 auto 12px}
.g{margin-top:18px}.g .l{display:block;color:var(--mut);font-size:12.5px;margin-bottom:6px;font-weight:700}
.note{font-size:12px;color:var(--mut);margin-top:6px}
.rb{display:flex;justify-content:space-between;align-items:center;width:100%;background:var(--cd);border:1px solid var(--ln);border-radius:14px;padding:12px 14px;text-align:left}
.rb .r{text-align:right;min-width:0}.rb b{display:block;font-size:14.5px}.rb small{display:block;color:var(--mut);font-size:11.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:200px}
.md{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;align-items:center;justify-content:center;padding:20px;z-index:55}.md.on{display:flex}
.mb{background:var(--bg);border-radius:20px;padding:20px;max-width:360px;width:100%;box-shadow:var(--sh)}.mb p{margin-bottom:14px;font-size:14.5px}.mb input{margin-bottom:14px}.mb .row{justify-content:flex-end}
.fb{position:fixed;inset:0;background:var(--bg);display:none;z-index:50;padding:calc(14px + env(safe-area-inset-top)) 18px calc(14px + env(safe-area-inset-bottom))}.fb.on{display:block}
.fb .w{display:flex;flex-direction:column;height:100%}#fbl{flex:1;overflow:auto;margin:8px 0}
#fbl button{display:flex;align-items:center;gap:10px;width:100%;text-align:left;background:none;border-radius:0;padding:12px 0;border-bottom:1px solid var(--ln)}#fbl button svg.i{color:var(--at);flex:none}
#fbat{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0}
.fbf{display:flex;gap:8px;margin-top:6px}.fbf button{flex:1;margin-top:0}.fbf button.p{flex:1.4}
#toast{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) scale(.96);background:rgba(15,23,42,0.9);color:#fff;padding: 6px 10px;border-radius:14px;font-size:13px;text-align:center;line-height:1.4;opacity:0;pointer-events:none;transition:opacity .3s ease,transform .3s ease;z-index:70;width:max-content;max-width:min(86%,320px);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
#toast.on{opacity:1;transform:translate(-50%,-50%) scale(1)}
.cv{position:relative;width:40px;height:40px;border-radius:10px;overflow:hidden;background:var(--sf);color:var(--at);display:grid;place-items:center;flex:none}
.cv svg.i{width:18px;height:18px}.cv img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ja{color:var(--at);font-size:12px;font-weight:600}
.rs.off{cursor:default}.rs.off .th,.rs.off .bd2>.tt:first-child{opacity:.5}
.pl-card{background:var(--cd);border:1px solid var(--ln);border-radius:14px;padding:12px 14px;margin-top:10px;display:flex;align-items:center;gap:12px;box-shadow:var(--sh)}
.pl-card .th{width:56px;height:56px;border-radius:10px;overflow:hidden;background:var(--sf);flex:none}.pl-card .th img{width:100%;height:100%;object-fit:cover}
.cv{width:46px;height:46px}.cv.lg{width:56px;height:56px;border-radius:12px}
.lr{border-radius:12px;padding:6px 8px;margin:0 -8px;transition:background .15s}.lr.now{background:var(--acs)}
.lr .cv{box-shadow:0 1px 2px rgb(0 0 0 / .12)}
/*skin-organico*/
*{scrollbar-width:thin;scrollbar-color:var(--sf2) transparent}
:root{--serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;--paper:#fbf8ef}
body{font-family:ui-rounded,"Segoe UI",system-ui,-apple-system,Roboto,sans-serif}
body::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.55;mix-blend-mode:multiply;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .3 0 0 0 0 .27 0 0 0 0 .2 0 0 0 .6 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}
@media(prefers-color-scheme:dark){body::before{opacity:.3}}
body::after{content:"";position:absolute;top:0;left:0;right:0;height:6px;z-index:5;background:linear-gradient(90deg,var(--ac) 0 33.3%,var(--ac2) 33.3% 66.6%,var(--yl) 66.6%)}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes rise{from{opacity:0;transform:translateY(12px)}}
@keyframes pop{50%{transform:scale(1.28) rotate(-8deg)}}
@keyframes bob{50%{transform:translateY(-3px) rotate(2deg)}}
@keyframes barber{to{background-position:22.63px 0}}
@keyframes up{from{opacity:0;transform:translate(-50%,40px)}to{opacity:1;transform:translate(-50%,0)}}
.wm{font-family:var(--serif);font-size:27px;font-weight:800;letter-spacing:-.5px}
.wm i{font-style:italic;color:var(--ac)}
h1,h2{font-family:var(--serif);color:var(--fg)}
h1{font-size:34px;font-weight:800;letter-spacing:-.5px;margin-top:22px}
.sub{font-family:var(--serif);font-style:italic;font-size:15px}
.ib{background:var(--cd);border:1px solid var(--ln);border-radius:14px;box-shadow:var(--sh)}
.tabs{background:var(--sf);border:1px solid var(--ln);border-radius:18px;padding:4px;gap:3px;box-shadow:inset 0 2px 4px rgb(0 0 0 / .08)}
.tabs a{border-radius:14px;padding:10px 4px;font-weight:700;transition:background .25s,color .25s,transform .2s}
.tabs a.on{background:var(--ac);color:var(--paper);box-shadow:0 3px 8px rgb(190 80 20 / .35)}
.tabs a.on svg{animation:pop .4s ease}
.cb{background:var(--ac2);color:var(--ink)}.tabs a.on .cb{background:var(--paper);color:var(--ac)}
.chip,.plc,.pl-card,.deliver,#tray,.rb{background:var(--cd);border:1px solid var(--ln);border-radius:16px;box-shadow:var(--sh)}
.chip span{color:var(--at)}
textarea,input[type=text],input[type=number]{background:var(--cd);border:1px solid var(--ln);border-radius:14px;box-shadow:inset 0 2px 4px rgb(0 0 0 / .06)}
textarea:focus,input[type=text]:focus{border-color:var(--ac);box-shadow:0 0 0 3px color-mix(in srgb,var(--ac) 25%,transparent)}
button{transition:transform .15s,box-shadow .2s,opacity .15s,background .2s}
button.p{background:var(--ac);color:var(--paper);border:0;border-radius:16px;padding:15px;font-family:var(--serif);font-size:19px;font-weight:700;letter-spacing:.3px;box-shadow:0 6px 14px rgb(190 80 20 / .3),inset 0 -3px 0 rgb(0 0 0 / .14)}
button.p:active{transform:scale(.97) translateY(1px);opacity:1}
button.s2,button.more{border:1px solid var(--ln);border-radius:14px;box-shadow:var(--sh);font-weight:700}
button.more{color:var(--at)}
@media(hover:hover){button.p:hover{transform:translateY(-2px);box-shadow:0 10px 20px rgb(190 80 20 / .35),inset 0 -3px 0 rgb(0 0 0 / .14)}.lr:hover,.pl-card:hover{background-color:color-mix(in srgb,var(--acs) 55%,transparent)}}
.sg{background:var(--sf);border:1px solid var(--ln);border-radius:14px;padding:3px;box-shadow:inset 0 2px 4px rgb(0 0 0 / .08)}
.sg button.on{background:var(--ac);color:var(--paper);box-shadow:0 2px 6px rgb(190 80 20 / .35)}
.sbar,.sel{background:var(--ink);color:#f1ecdd;border-radius:16px;box-shadow:0 10px 26px rgb(0 0 0 / .3)}
.sbar .pb{background:var(--ac2);color:var(--ink)}
.hello,.aviso{background:var(--acs);border:1px dashed var(--ln);border-radius:14px}
.cv,.th,.ft{border:3px solid var(--paper);border-radius:6px;box-shadow:0 3px 8px rgb(40 35 25 / .3)}
.cv img,.th img,img.ft{filter:sepia(.2) saturate(.92)}
.lr:nth-child(odd) .cv{transform:rotate(-2.5deg)}.lr:nth-child(even) .cv{transform:rotate(2deg)}
.lr,.pl-card,.pc{animation:rise .45s cubic-bezier(.2,.8,.3,1) both}
:is(.lr,.pl-card,.pc):nth-child(2){animation-delay:0.04s}
:is(.lr,.pl-card,.pc):nth-child(3){animation-delay:0.08s}
:is(.lr,.pl-card,.pc):nth-child(4){animation-delay:0.12s}
:is(.lr,.pl-card,.pc):nth-child(5){animation-delay:0.16s}
:is(.lr,.pl-card,.pc):nth-child(6){animation-delay:0.20s}
:is(.lr,.pl-card,.pc):nth-child(7){animation-delay:0.24s}
:is(.lr,.pl-card,.pc):nth-child(8){animation-delay:0.28s}
:is(.lr,.pl-card,.pc):nth-child(9){animation-delay:0.32s}
:is(.lr,.pl-card,.pc):nth-child(10){animation-delay:0.36s}
.lh,.g .l{text-transform:uppercase;letter-spacing:.12em;font-size:11px}
.lr.now{background:var(--acs);box-shadow:inset 4px 0 0 var(--ac)}
.lr.now .nm{color:var(--at);font-weight:700}
.lr.now .cv{animation:bob 1.3s ease-in-out infinite}
.bar{height:10px;background:var(--sf2);border-radius:99px;box-shadow:inset 0 1px 3px rgb(0 0 0 / .2)}
.bar i{background:repeating-linear-gradient(-45deg,var(--ac) 0 8px,var(--ac2) 8px 16px);background-size:22.63px 22.63px;border-radius:99px;animation:barber 1s linear infinite}
.spn{background:var(--bg);border-top:1px solid var(--ln);border-radius:26px 26px 0 0}
.mb{background:var(--cd);border:1px solid var(--ln);border-radius:20px;box-shadow:0 20px 50px rgb(0 0 0 / .3)}
#toast{background:var(--ink);color:#f1ecdd;border-radius:14px}
/*retro-cassete*/
.mk{background:none;box-shadow:none;width:54px;height:36px;border-radius:0}
.mk svg{width:54px;height:36px;display:block;filter:drop-shadow(0 2px 3px rgb(60 30 10 / .35))}
.mkr{animation:spin 4s linear infinite}
body.baixando .mkr{animation-duration:.9s}
.wm i{color:#d9692a}
.empty svg{width:76px;height:48px}
.cv.vd{width:70px;height:42px;border:0;border-radius:4px;background:linear-gradient(#332a24,#1c1612);box-shadow:0 3px 8px rgb(40 35 25 / .35),inset 0 0 0 1.5px #4a3d33}
.cv.vd svg.i{display:none}
.cv.vd::before{content:"";position:absolute;left:5px;top:4px;width:60px;height:23px;border-radius:2px;background:#efe4cc}
.cv.vd img{inset:auto;left:5px;top:4px;width:60px;height:23px;border-radius:2px}
.cv.vd::after{content:"T-120";position:absolute;left:0;right:0;bottom:3px;text-align:center;font:800 8px/1 ui-monospace,Menlo,monospace;letter-spacing:.14em;color:#e8873a}
body.pon{padding-bottom:calc(var(--plh,150px) + 40px + env(safe-area-inset-bottom))}
.pon .sel{bottom:calc(var(--plh,150px) + 24px + env(safe-area-inset-bottom))}
#pl{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(12px + env(safe-area-inset-bottom));width:min(420px,calc(100% - 32px));max-height:calc(100vh - 24px);overflow:auto;background:#eaa45f;background-image:radial-gradient(rgb(120 60 20 / .12) 1px,transparent 1.5px);background-size:7px 7px;border:4px solid #3b1f10;border-radius:22px;padding:10px 14px 12px;z-index:9;box-shadow:0 10px 28px rgb(0 0 0 / .3);animation:up .5s cubic-bezier(.2,1.2,.4,1);color:#3b1f10}
.pt{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.ptx{flex:1;min-width:0}
.rb4{width:28px;height:28px;flex:none;border-radius:50%;border:2px solid #3b1f10;background:transparent;color:#3b1f10;display:grid;place-items:center;padding:0}
.rb4 svg.i{width:14px;height:14px}
#pl.aud .vwrap,#pl.aud #bfs{display:none}
.vwrap{margin-bottom:8px}
.vm{aspect-ratio:16/9;max-height:34vh;margin:0 auto;background:#000;border-radius:12px;overflow:hidden;border:3px solid #3b1f10;cursor:pointer}
.vm video{width:100%;height:100%;object-fit:contain;display:block;background:#000}
.tl{display:flex;align-items:center;gap:10px}
.tl b{font:800 15px/1 ui-rounded,system-ui,sans-serif;font-variant-numeric:tabular-nums;min-width:2.9em}
.tl b:last-child{text-align:right}
.ptrack{position:relative;flex:1;height:24px;cursor:pointer;touch-action:none}
.ptrack::before{content:"";position:absolute;left:0;right:0;top:50%;height:2px;background:#3b1f10;transform:translateY(-50%)}
.ptrack i{position:absolute;left:0;top:50%;height:14px;width:0;transform:translateY(-50%);background:#5a2c12;border-radius:9px}
#pl hr{border:0;height:3px;background:#3b1f10;border-radius:2px;margin:4px 0 10px}
.btns{display:flex;justify-content:space-between;align-items:center;gap:5px}
.rb2{flex:1;min-width:0;max-width:46px;aspect-ratio:1;border-radius:50%;border:2.5px solid #3b1f10;background:transparent;color:#3b1f10;display:grid;place-items:center;padding:0}
.rb2 svg.i{width:46%;height:46%}
.rb2.big{flex:1.25;max-width:58px;background:#c8581f;color:#f6e7c8;border-width:3px;box-shadow:0 3px 8px rgb(80 30 5 / .4)}
.rb2.sp{border-color:transparent}
.rb2:active,.rb4:active{transform:scale(.93)}
.vrow{margin-top:10px}
#vol{display:block;width:100%;height:22px;padding:0;border:0;background:transparent;-webkit-appearance:none;appearance:none}
#vol::-webkit-slider-runnable-track{height:4px;background:#3b1f10;border-radius:3px}
#vol::-webkit-slider-thumb{-webkit-appearance:none;width:18px;height:18px;margin-top:-7px;border-radius:50%;background:#c8581f;border:3px solid #3b1f10}
#vol::-moz-range-track{height:4px;background:#3b1f10;border-radius:3px}
#vol::-moz-range-thumb{width:12px;height:12px;border-radius:50%;background:#c8581f;border:3px solid #3b1f10}
/*retro-skin*/
:root{--rk:#3b1f10}
@media(prefers-color-scheme:dark){:root{--rk:#8a6646}}
.mk{width:66px;height:43px}
.mk svg{width:66px;height:43px}
.rb2{max-width:56px}
.rb2.big{max-width:68px}
.btns{gap:8px;padding:0 2px}
body{background-image:radial-gradient(color-mix(in srgb,var(--rk) 13%,transparent) 1px,transparent 1.6px);background-size:9px 9px}
header{border-bottom:3px double var(--rk);margin-bottom:8px;padding-bottom:10px}
.ib{border:2.5px solid var(--rk);box-shadow:2px 2px 0 var(--rk);border-radius:12px}
.tabs{border:2.5px solid var(--rk);box-shadow:3px 3px 0 var(--rk)}
.tabs a.on{background:var(--ac);color:#fbf3e1;box-shadow:inset 0 0 0 2px var(--rk)}
h1::after{content:"";display:block;width:72px;height:7px;margin-top:8px;border-radius:4px;border:2px solid var(--rk);background:repeating-linear-gradient(90deg,var(--ac) 0 12px,var(--ac2) 12px 24px)}
.chip,.plc,.pl-card,.deliver,#tray,.rb{border:2.5px solid var(--rk);border-radius:14px;box-shadow:3px 3px 0 var(--rk)}
.hello,.aviso{border:2px dashed var(--rk);border-radius:14px;box-shadow:none}
.mb{border:3px solid var(--rk);box-shadow:5px 5px 0 var(--rk);border-radius:18px}
.spn{border-top:3px solid var(--rk)}
textarea,input[type=text],input[type=number]{border:2.5px solid var(--rk);border-radius:12px;box-shadow:inset 2px 2px 0 rgb(0 0 0 / .08)}
button.p{border:3px solid var(--rk);color:#fbf3e1;box-shadow:0 4px 0 var(--rk);border-radius:14px}
button.p:active{transform:translateY(3px);box-shadow:0 1px 0 var(--rk)}
@media(hover:hover){button.p:hover{transform:translateY(-1px);box-shadow:0 5px 0 var(--rk)}}
button.s2,button.more{border:2.5px solid var(--rk);box-shadow:2px 2px 0 var(--rk);border-radius:12px}
.sg{border:2.5px solid var(--rk);box-shadow:2px 2px 0 var(--rk)}
.sg button.on{background:var(--ac);color:#fbf3e1;box-shadow:inset 0 0 0 2px var(--rk)}
.lr,.rs,.pc,.tr,.it{border-bottom:2px dotted color-mix(in srgb,var(--rk) 35%,transparent)}
.cv,.th,.ft{border:2.5px solid var(--rk);border-radius:6px;box-shadow:2px 2px 0 var(--rk)}
.cv.vd{border:0;border-radius:4px}
.sbar,.sel{background:#eaa45f;background-image:radial-gradient(rgb(120 60 20 / .12) 1px,transparent 1.5px);background-size:7px 7px;color:#3b1f10;border:3px solid #3b1f10;border-radius:16px;box-shadow:3px 3px 0 #3b1f10}
.sbar button,.sel button{color:#3b1f10;font-weight:700}
.sbar .pb{background:#c8581f;color:#f6e7c8;border-radius:10px}
.bar{border:2px solid var(--rk);height:12px}
#toast{background:#3b1f10;color:#f6e7c8;border:2px solid #e8a15f;border-radius:12px}
.lh{border-bottom:2px dotted color-mix(in srgb,var(--rk) 35%,transparent);padding-bottom:4px}
.cb{border:1.5px solid var(--rk)}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
.mkr{animation:spin 4s linear infinite!important}
body.baixando .mkr{animation-duration:.9s!important}


/* AUTO-3D-FINAL - claro e escuro separados, sem briga */
@media (prefers-color-scheme: light){
  body{background:#f3e6cc!important;color:#3b2314!important}
  body .tabs{background:linear-gradient(180deg,#e8ddc2,#cbbd98)!important;border:3px solid #6b5a35!important;border-radius:18px!important;box-shadow:0 6px 0 #6b5a35,0 10px 18px rgba(0,0,0,.35),inset 0 2px 0 #fff!important;padding:5px!important}
  body .tabs a{background:linear-gradient(180deg,#fff8e6,#d9cda9)!important;color:#5a4a2c!important;border:2px solid #a8936a!important;border-radius:14px!important;box-shadow:0 4px 0 #a8936a,0 6px 10px rgba(0,0,0,.3),inset 0 2px 0 #fff,inset 0 -3px 5px rgba(0,0,0,.15)!important}
  body .tabs a.on{background:linear-gradient(180deg,#3a2a12,#0d0803)!important;color:#ffb840!important;border:2px solid #a8936a!important;box-shadow:0 4px 0 #000,0 8px 14px rgba(0,0,0,.5),inset 0 2px 0 rgba(255,255,255,.35),0 0 14px rgba(255,180,60,.5)!important}
  body .tabs a.on .cb{background:#ffb840!important;color:#241a0e!important}
  textarea{background:#d8cfae!important;border:3px solid #6b4d1a!important;box-shadow:inset 0 5px 12px rgba(0,0,0,.4),0 3px 0 #f0e6c0,0 8px 14px rgba(0,0,0,.3)!important;color:#221806!important}
  .chip{background:linear-gradient(180deg,#f0e2b8,#b8a05a)!important;border:2px solid #6b4d1a!important;box-shadow:0 5px 0 #6b4d1a,0 8px 14px rgba(0,0,0,.3),inset 0 2px 0 #fff!important}
  button.p{background:linear-gradient(180deg,#4a4438,#000)!important;color:#f0a830!important;border:3px solid #000!important;box-shadow:0 8px 0 #000,0 14px 22px rgba(0,0,0,.5),inset 0 2px 0 rgba(255,255,255,.25)!important}
  button.t,#bpaste,#bclr{background:linear-gradient(180deg,#f0e6c0,#c8b888)!important;color:#221806!important;border:2px solid #6b4d1a!important;box-shadow:0 3px 0 #6b4d1a,0 5px 8px rgba(0,0,0,.3),inset 0 1px 0 #fff!important}
  body #pl,body .spn,body #player{background:linear-gradient(180deg,#fff8e6,#d9cda9)!important;border:3px solid #6b5a35!important;box-shadow:0 6px 0 #6b5a35,0 12px 20px rgba(0,0,0,.4),inset 0 2px 0 #fff!important;color:#241a0e!important}
  body #pl *,body .spn *{color:#241a0e!important}
  body #pl #bplay{background:#241a0e!important;color:#ffb840!important;border:2px solid #a8936a!important;box-shadow:0 4px 0 #000,0 6px 10px rgba(0,0,0,.4)!important}
}

body h1::after,body h1::before{display:none!important;content:none!important}

@media (prefers-color-scheme: dark){
  body{background:#2e2620!important;color:#fff7e0!important}
  /* LOGO - pra aparecer no escuro */
  .mk, header .mk, .logo{background:#f3e6cc!important;border:3px solid #ffb840!important;border-radius:14px!important;padding:4px 6px!important;box-shadow:0 4px 0 #000,0 8px 14px rgba(0,0,0,.6)!important}
  .mk svg{filter:drop-shadow(0 2px 2px rgba(0,0,0,.4))!important}
  body .tabs{background:linear-gradient(180deg,#4a3a28,#2e2318)!important;border:3px solid #d4a94e!important;border-radius:18px!important;box-shadow:0 6px 0 #000,0 10px 18px rgba(0,0,0,.6),inset 0 2px 0 rgba(255,255,255,.25)!important;padding:5px!important}
  body .tabs a{background:linear-gradient(180deg,#6b5636,#3a2c1e)!important;color:#fff2cc!important;border:2px solid #d4a94e!important;border-radius:14px!important;box-shadow:0 4px 0 #000,0 6px 10px rgba(0,0,0,.6),inset 0 2px 0 rgba(255,255,255,.28)!important;text-shadow:0 1px 2px #000!important}
  body .tabs a.on{background:linear-gradient(180deg,#1a1005,#000)!important;color:#ffd860!important;border:2px solid #ffd860!important;box-shadow:0 4px 0 #000,0 8px 14px rgba(0,0,0,.7),0 0 16px rgba(255,200,80,.6)!important}
  body .tabs a.on .cb{background:#ffd860!important;color:#241a0e!important}
  textarea{background:#3a2e22!important;color:#fff7e0!important;border:3px solid #d4a94e!important;box-shadow:inset 0 5px 12px rgba(0,0,0,.6),0 3px 0 rgba(255,255,255,.12)!important}
  textarea::placeholder{color:#d8c9a0!important}
  .chip{background:linear-gradient(180deg,#5a4630,#2e2318)!important;border:2px solid #d4a94e!important;color:#fff7e0!important;box-shadow:0 5px 0 #000,0 8px 14px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.22)!important}
  .chip b,.chip span,.chip small{color:#fff7e0!important}
  button.p{background:linear-gradient(180deg,#4a4438,#000)!important;color:#ffd860!important;border:3px solid #000!important;box-shadow:0 8px 0 #000,0 14px 22px rgba(0,0,0,.7),inset 0 2px 0 rgba(255,255,255,.25)!important}
  button.t,#bpaste,#bclr{background:linear-gradient(180deg,#5a4630,#2e2318)!important;color:#fff7e0!important;border:2px solid #d4a94e!important;box-shadow:0 3px 0 #000,0 5px 8px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.2)!important}
  body #pl,body .spn,body #player{background:linear-gradient(180deg,#5a4630,#2e2318)!important;border:3px solid #d4a94e!important;box-shadow:0 6px 0 #000,0 12px 20px rgba(0,0,0,.65),inset 0 2px 0 rgba(255,255,255,.22)!important;color:#fff7e0!important}
  body #pl *,body .spn *{color:#fff7e0!important;text-shadow:0 1px 2px #000!important}
  body #pl #bplay{background:#000!important;color:#ffd860!important;border:2px solid #ffd860!important;box-shadow:0 4px 0 #000,0 6px 10px rgba(0,0,0,.6)!important}
  h1,.wm{color:#fff7e0!important;text-shadow:0 2px 0 #000!important}
  .sub{color:#e8d9b0!important}
  .lr,.pl-card,.it{background:linear-gradient(180deg,#4a3a28,#2e2318)!important;border:2px solid #8a6a3a!important;color:#fff7e0!important}
  .lr b,.lr span,.pl-card b{color:#fff7e0!important}
  .lr small,.pl-card small{color:#e8d9b0!important}
}

/* TUDO-3D-FINAL - tudo saltado, logo no centro, player visivel */
header{display:flex!important;flex-direction:row!important;align-items:center!important;justify-content:flex-start!important;text-align:left!important;overflow:hidden!important}
.mk{margin:0!important;flex:none!important;flex-shrink:0!important;max-width:100%!important;box-sizing:border-box!important}
h1,.wm{text-align:left!important}
.sub{text-align:left!important}
/* TUDO 3D - cards, listas, caixas */
.lr,.pl-card,.it,.plc,.deliver,#tray,.rb,.mb,.hello,.aviso,.sg,.chip{box-shadow:0 5px 0 rgba(0,0,0,.35),0 10px 16px rgba(0,0,0,.3),inset 0 2px 0 rgba(255,255,255,.6)!important}
.lr:active,.pl-card:active{transform:translateY(2px)!important;box-shadow:0 2px 0 rgba(0,0,0,.35),0 4px 8px rgba(0,0,0,.3)!important}
/* PLAYER - estrutura */
body #pl{padding:14px!important}
body #pl .pt{display:flex!important;align-items:center!important;gap:10px!important}
body #pl .ptx{flex:1!important;min-width:0!important}
/* LINHA DO PLAYER - clara nos 2 modos, pra enxergar */
@media (prefers-color-scheme: light){
  body #pl .ptrack,body #pl #pfill-track,body #pl input[type=range],body #pl .bar,body #pl .pb{background:#c8b88f!important;border:2px solid #6b5a35!important;border-radius:99px!important;height:10px!important;box-shadow:inset 0 2px 4px rgba(0,0,0,.35),0 1px 0 #fff!important}
  body #pl #pfill,body #pl .pfill,body #pl .fill{background:#c99a3a!important;border-radius:99px!important;height:10px!important;box-shadow:none!important}
  body #pl input[type=range]{-webkit-appearance:none!important;appearance:none!important}
  body #pl input[type=range]::-webkit-slider-thumb{-webkit-appearance:none!important;width:22px!important;height:22px!important;border-radius:50%!important;background:#241a0e!important;border:3px solid #ffb840!important;box-shadow:0 3px 0 #000,0 4px 8px rgba(0,0,0,.4)!important;cursor:pointer!important}
  body #pl input[type=range]::-moz-range-thumb{width:22px!important;height:22px!important;border-radius:50%!important;background:#241a0e!important;border:3px solid #ffb840!important;box-shadow:0 3px 0 #000!important}
  body #pl .rb2,body #pl button{box-shadow:0 4px 0 #6b5a35,0 6px 10px rgba(0,0,0,.3),inset 0 2px 0 #fff!important}
  body #pl .tm,body #pl .time,body #pl small{color:#241a0e!important;font-weight:800!important;background:#f5eedb!important;padding:2px 8px!important;border-radius:99px!important;border:1px solid #6b5a35!important}
}
@media (prefers-color-scheme: dark){
  .lr,.pl-card,.it,.plc,.deliver,#tray,.rb,.mb{box-shadow:0 5px 0 #000,0 10px 16px rgba(0,0,0,.6),inset 0 2px 0 rgba(255,255,255,.22)!important}
  /* PLAYER DARK - linha clara, bolinha dourada */
  body #pl .ptrack,body #pl #pfill-track,body #pl input[type=range],body #pl .bar,body #pl .pb{background:#d8c9a0!important;border:2px solid #a8936a!important;border-radius:99px!important;height:10px!important;box-shadow:inset 0 2px 4px rgba(0,0,0,.5)!important}
  body #pl #pfill,body #pl .pfill,body #pl .fill{background:#c99a3a!important;border-radius:99px!important;height:10px!important;box-shadow:none!important}
  body #pl input[type=range]{-webkit-appearance:none!important;appearance:none!important;background:#d8c9a0!important}
  body #pl input[type=range]::-webkit-slider-thumb{-webkit-appearance:none!important;width:24px!important;height:24px!important;border-radius:50%!important;background:#c99a3a!important;border:3px solid #000!important;box-shadow:0 3px 0 #000!important;cursor:pointer!important}
  body #pl input[type=range]::-moz-range-thumb{width:24px!important;height:24px!important;border-radius:50%!important;background:#ffd860!important;border:3px solid #000!important}
  body #pl input[type=range]::-moz-range-track{height:10px!important;background:#d8c9a0!important;border:2px solid #a8936a!important;border-radius:99px!important}
  body #pl .rb2,body #pl button{background:linear-gradient(180deg,#5a4630,#2e2318)!important;color:#fff7e0!important;border:2px solid #d4a94e!important;box-shadow:0 4px 0 #000,0 6px 10px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.25)!important}
  body #pl .tm,body #pl .time,body #pl small{color:#e8d9b0!important;font-weight:800!important;background:#241a0e!important;padding:2px 8px!important;border-radius:99px!important;border:1px solid #ffb840!important}
  body #pl .ptx b,body #pl .ptx{color:#fff7e0!important}
  body #pl #vol,body #vol{background:#d8c9a0!important}
}

/* LOGO-NAO-VAZA - volta pra onde tava, so nao vaza */
header{overflow:hidden!important;max-width:100%!important;box-sizing:border-box!important}
header > *{min-width:0!important;max-width:100%!important}
.mk{width:auto!important;max-width:72px!important;overflow:hidden!important}
.mk svg{width:100%!important;height:auto!important;max-width:66px!important;display:block!important}

/* AJUSTE-FINAL-5 - abas com profundidade, botoes 3D, barra marcada, logo sem quadrado */
/* 1. ABAS ABERTAS COM PROFUNDIDADE - Baixar / Buscar */
body .tabs a.on{color:#ffb840!important;text-shadow:0 2px 0 #000,0 3px 4px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.2)!important;box-shadow:inset 0 4px 8px rgba(0,0,0,.6),inset 0 -1px 0 rgba(255,255,255,.2),0 4px 0 #000,0 8px 14px rgba(0,0,0,.5)!important;transform:translateY(1px)!important}
body .tabs a{ text-shadow:0 1px 0 #fff,0 2px 2px rgba(0,0,0,.15)!important; }
/* 2. BOTOES MUSICA / PLAYLIST / BUSCAR - 3D */
.sg{display:flex!important;gap:6px!important;padding:5px!important;border-radius:18px!important;box-shadow:0 4px 0 rgba(0,0,0,.3),0 8px 12px rgba(0,0,0,.25),inset 0 1px 0 rgba(255,255,255,.6)!important}
.sg button,.sg a,button.s2,button.more,#bbuscar,#bBuscar,#buscar{box-shadow:0 4px 0 rgba(0,0,0,.3),0 6px 10px rgba(0,0,0,.25),inset 0 2px 0 #fff,inset 0 -3px 5px rgba(0,0,0,.15)!important;border:2px solid #6b5a35!important}
.sg button.on,.sg button:active,#bbuscar:active{transform:translateY(2px)!important;box-shadow:inset 0 3px 6px rgba(0,0,0,.4),0 1px 0 rgba(0,0,0,.3)!important}
.sg button.on{background:linear-gradient(180deg,#3a2a12,#1a1005)!important;color:#ffb840!important;border:2px solid #ffb840!important;text-shadow:0 2px 0 #000!important}
/* 3. PROCURAR REPETIDAS - nao preto, bege 3D */
#fbar button,#brep,button[onclick*="repet"],.fbf button:not(.p),#bclr,#bpaste{background:linear-gradient(180deg,#fff8e6,#d9cda9)!important;color:#3b2314!important;border:2px solid #6b5a35!important;border-radius:14px!important;box-shadow:0 4px 0 #6b5a35,0 6px 10px rgba(0,0,0,.3),inset 0 2px 0 #fff!important;text-shadow:0 1px 0 #fff!important}
#fbar button:active,#brep:active{transform:translateY(2px)!important;box-shadow:0 1px 0 #6b5a35!important}
/* 4. BARRA MARCADA - 1 marcada / apagar marcadas - 3D bege, nao preta */
.sel,.sbar,#selbar,.bar-sel{position:fixed!important;background:linear-gradient(180deg,#fff8e6,#e8ddc2)!important;color:#3b2314!important;border:3px solid #6b5a35!important;border-radius:18px!important;box-shadow:0 6px 0 #6b5a35,0 12px 20px rgba(0,0,0,.4),inset 0 2px 0 #fff!important;padding:10px 14px!important}
.sel *, .sbar *, #selbar *{color:#3b2314!important;text-shadow:0 1px 0 #fff!important}
.sel button,.sbar button,.sbar .pb,#selbar button{background:linear-gradient(180deg,#3a2a12,#1a1005)!important;color:#ffb840!important;border:2px solid #ffb840!important;border-radius:12px!important;box-shadow:0 3px 0 #000,0 5px 8px rgba(0,0,0,.4)!important}
.sel .cb,.sbar .cb{background:#ffb840!important;color:#241a0e!important;border-radius:99px!important;padding:2px 8px!important;font-weight:800!important}
/* 5. LOGO - sem quadrado, sem fundo, cores quentes */
.mk, header .mk, .logo, .mk svg{ background:none!important;background-color:transparent!important;border:none!important;box-shadow:none!important;padding:0!important;border-radius:0!important}
.mk{width:auto!important;max-width:72px!important;filter:drop-shadow(0 4px 4px rgba(0,0,0,.35))!important}
.mk svg{width:66px!important;height:auto!important;filter:sepia(.15) saturate(1.15) contrast(1.05)!important}
@media (prefers-color-scheme: dark){
  .sg{box-shadow:0 4px 0 #000,0 8px 12px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.2)!important}
  .sg button,.sg a,button.s2,button.more{box-shadow:0 4px 0 #000,0 6px 10px rgba(0,0,0,.6),inset 0 2px 0 rgba(255,255,255,.2)!important;border:2px solid #d4a94e!important}
  .sg button.on{color:#ffd860!important;border-color:#ffd860!important}
  #fbar button,#brep,.fbf button:not(.p){background:linear-gradient(180deg,#5a4630,#2e2318)!important;color:#fff7e0!important;border:2px solid #d4a94e!important;box-shadow:0 4px 0 #000,0 6px 10px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.2)!important;text-shadow:0 1px 2px #000!important}
  .sel,.sbar,#selbar{background:linear-gradient(180deg,#5a4630,#2e2318)!important;color:#fff7e0!important;border:3px solid #d4a94e!important;box-shadow:0 6px 0 #000,0 12px 20px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.2)!important}
  .sel *, .sbar *, #selbar *{color:#fff7e0!important;text-shadow:0 1px 2px #000!important}
  .sel button,.sbar button{background:#000!important;color:#ffd860!important;border:2px solid #ffd860!important}
  .mk{filter:drop-shadow(0 4px 4px rgba(0,0,0,.6))!important}
}
</style></head><body>
<div class="w">
<header><span class="mk"><svg viewBox="0 0 80 52" aria-hidden="true"><rect x="1.5" y="1.5" width="77" height="49" rx="6" fill="#f1dfb8" stroke="#4a2a17" stroke-width="2.6"/><circle cx="6.5" cy="6.5" r="1.8" fill="#d9bf8c" stroke="#4a2a17" stroke-width=".8"/><circle cx="73.5" cy="6.5" r="1.8" fill="#d9bf8c" stroke="#4a2a17" stroke-width=".8"/><circle cx="6.5" cy="45.5" r="1.8" fill="#d9bf8c" stroke="#4a2a17" stroke-width=".8"/><circle cx="73.5" cy="45.5" r="1.8" fill="#d9bf8c" stroke="#4a2a17" stroke-width=".8"/><rect x="11" y="5.5" width="58" height="21" rx="2.5" fill="#e8873a" stroke="#4a2a17" stroke-width="1.4"/><path d="M11 8a2.5 2.5 0 0 1 2.5-2.5h53A2.5 2.5 0 0 1 69 8v2.5H11z" fill="#c8581f"/><rect x="14" y="13" width="52" height="10" rx="1.5" fill="#f3e3c3" stroke="#4a2a17" stroke-width=".6"/><path d="M16.5 16.5h27M16.5 20h17" stroke="#4a2a17" stroke-width="1" stroke-linecap="round" opacity=".7"/><circle cx="58" cy="18" r="3.6" fill="#e8873a" stroke="#4a2a17" stroke-width=".9"/><circle cx="58" cy="18" r="1.2" fill="#4a2a17"/><rect x="17" y="29" width="46" height="14" rx="7" fill="#2a1a10" stroke="#4a2a17" stroke-width="1.4"/><path d="M29 42.4H51" stroke="#6b4228" stroke-width="1.2"/><circle cx="29" cy="36" r="6.4" fill="#6b4228"/><circle cx="51" cy="36" r="5" fill="#6b4228"/><g class="mkr" style="transform-origin:29px 36px"><circle cx="29" cy="36" r="4.6" fill="#f1dfb8" stroke="#4a2a17" stroke-width=".9"/><path d="M29 31.9v8.2M25.5 34l7 4M32.5 34l-7 4" stroke="#4a2a17" stroke-width="1.2" stroke-linecap="round"/></g><g class="mkr" style="transform-origin:51px 36px"><circle cx="51" cy="36" r="4.6" fill="#f1dfb8" stroke="#4a2a17" stroke-width=".9"/><path d="M51 31.9v8.2M47.5 34l7 4M54.5 34l-7 4" stroke="#4a2a17" stroke-width="1.2" stroke-linecap="round"/></g><path d="M22 45.5 25 49.2H55L58 45.5z" fill="#d9bf8c" stroke="#4a2a17" stroke-width="1.1" stroke-linejoin="round"/><circle cx="32" cy="47.3" r="1.1" fill="#2a1a10"/><circle cx="48" cy="47.3" r="1.1" fill="#2a1a10"/><path d="M5 12v26" stroke="#fff" stroke-width="1.2" stroke-linecap="round" opacity=".35"/></svg></span><b class="wm">Wave<i>Fly</i></b><span class="sp1"></span>
<button class="ib" id="bset" aria-label="Ajustes" data-i="gear"></button></header>
<nav class="tabs"><a data-go="baixar" class="on"><span data-i="down"></span>Baixar</a><a data-go="nome"><span data-i="search"></span>Buscar<span class="cb" id="nb" hidden></span></a><a data-go="musicas"><span data-i="folder"></span>Biblioteca</a></nav>

<section class="v" id="v-baixar">
  <h1>Baixar</h1>
  <p class="sub">Cole links do YouTube para gerenciar seus downloads.</p>
  <div class="warn" id="warn" hidden>Para organizar suas músicas, precisamos de acesso à pasta de destino. <button class="t" style="color:inherit;font-weight:700;text-decoration:underline" onclick="fbabrir()">[Escolher Pasta]</button><span id="warnand"> Permita o acesso aos arquivos quando o Android pedir.</span></div>
  <div class="hello" id="hello" hidden>Bem-vindo ao WaveFly! As músicas serão salvas em <b class="js-pcam"></b>.<div class="row"><button class="t" id="hchg">Alterar pasta</button><button class="t" id="hok">Entendi</button></div></div>
  <textarea id="ta" placeholder="Cole os links aqui..." spellcheck="false"></textarea>
  <div class="row" style="margin-top:6px"><span class="sm mut" id="cnt">Nenhum link</span><span><button class="t" id="bpaste">Colar</button><button class="t" id="bclr">Limpar</button></span></div>
  <div class="pvl" id="pv" hidden></div>
  <button class="chip js-chip"><b class="js-resumo">…</b><span>Alterar ›</span></button>
  <button class="p" id="bgo">Baixar</button>

  <div class="sec" id="fila" hidden>
    <div class="row"><b><span id="eq" class="onda-sonora"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span><span id="fh">Fila</span></b><span class="mut sm" id="fc"></span></div>
    <div class="bar" style="margin:8px 0"><i id="fbar"></i></div>
    <div class="sm mut" id="fs"></div>
    <div class="aviso" id="fav" hidden></div>
    <div class="deliver" id="entrega" hidden><b><span id="en">0</span> arquivo(s) pronto(s) para receber</b><div class="row"><button id="bsolto">Avulsos</button><button class="a" id="bzipq">Em ZIP</button></div></div>
    <div style="margin:4px -6px"><button class="t" id="bcanc">Cancelar tudo</button><button class="t" id="blimpa">Limpar concluídos</button></div>
    <div class="row" id="abasFila" style="margin:6px 0"><button class="t" data-aba="fila" id="abaFila">Fila</button><button class="t" data-aba="ok" id="abaOk">Concluídas</button></div><div id="lista"></div>
  </div>
</section>

<section class="v" id="v-nome" hidden>
  <h1>Buscar</h1>
  <p class="sub">Pesquise faixas, confira visualizações e o tamanho estimado.</p>
  <div class="sg full" id="segs"><button data-v="musica" class="on">Músicas</button><button data-v="playlist">Playlists</button></div>
  <div class="srch"><div class="ip"><span data-i="search"></span><input type="text" id="q" placeholder="Nome da música ou artista" autocomplete="off"><button id="qx" aria-label="Limpar busca" hidden data-i="x"></button></div><button id="bq">Buscar</button></div>
  <button class="chip js-chip"><b class="js-resumo">…</b><span>Alterar ›</span></button>
  <div class="sbar" id="sbar" hidden><span><span id="sc"></span><small id="se"></small></span><span><button id="stray">Ver lista</button><button id="scl">Limpar</button><button class="pb" id="sgo">Baixar</button></span></div>
  <div id="tray" hidden></div>
  <div id="res" style="margin-top:10px"></div>
</section>

<section class="v" id="v-musicas" hidden>
  <div class="row" style="margin-top:14px">
    <div class="sg" id="segm"><button data-v="todas" class="on">Músicas</button><button data-v="videos">Vídeos</button><button data-v="rep">Repetidas</button></div>
    <span class="sm mut" id="libinfo"></span>
  </div>
  <div id="m-todas" style="margin-top:12px"><input type="text" id="lf" placeholder="Filtrar músicas..."><label id="wrapvid" hidden style="display:flex;gap:8px;align-items:center;margin:6px 0 10px;cursor:pointer;font-size:14px"><input type="checkbox" id="chkvid" style="width:18px;height:18px"> Mostrar vídeos <span class="sm mut">(prioriza músicas)</span></label><div id="lib"></div></div>
  <div id="m-videos" style="margin-top:12px" hidden><input type="text" id="lfv" placeholder="Filtrar vídeos..."><div id="libv"></div></div>
  <div id="m-rep" style="margin-top:12px" hidden>
    <p class="sm mut">Procura cópias exatas e faixas parecidas na pasta atual para otimizar espaço.</p>
    <button class="p" id="bvar" style="margin-top:8px">Procurar repetidas</button><div id="rep"></div>
  </div>
</section>
</div>

<div class="sel" id="libbar" hidden><span id="selc"></span><span><button id="bsl">Limpar</button><button id="bdl" hidden>Avulsos</button><button id="bzip" hidden>ZIP</button><button id="bdel">Apagar</button></span></div>
<div class="sel" id="repbar" hidden><span id="repc"></span><button id="brdel">Apagar marcadas</button></div>

<div id="pl" class="aud" data-st="stop" hidden>
  <div class="pt"><div class="ptx"><div class="tt" id="plt" style="font-weight:700"></div><div class="sm tt" id="pls"></div></div><button class="rb4" id="bvol" aria-label="Volume" data-i="vol"></button><button class="rb4" id="bfs" aria-label="Tela cheia" data-i="full"></button><button class="rb4" id="plx" aria-label="Fechar" data-i="x"></button></div>
  <div class="vwrap"><div class="vm" id="tv-screen"></div></div>
  <div class="tl"><b id="tcur">00:00</b><div class="ptrack" id="ptrack"><i id="pfill"></i></div><b id="tdur">--:--</b></div>
  <hr>
  <div class="btns">
    <button class="rb2" id="plprev" aria-label="Anterior" data-i="prev"></button>
    <button class="rb2" id="brew" aria-label="Voltar 10 segundos" data-i="rew"></button>
    <button class="rb2 big" id="bplay" aria-label="Tocar" data-i="play"></button>
    <button class="rb2" id="bff" aria-label="Avançar 10 segundos" data-i="ff"></button>
    <button class="rb2" id="plnext" aria-label="Próxima" data-i="next"></button>
  </div>
  <div class="vrow" id="vrow" hidden><input type="range" id="vol" min="0" max="100" step="1" aria-label="Volume"></div>
  <div id="pl-audio" hidden></div>
</div>

<div class="sheet" id="sheet"><div class="spn">
  <div class="grip"></div>
  <div class="row"><b style="font-size:17px">Ajustes e Qualidade</b><button class="t" id="shx" style="color:var(--at);font-weight:600">Concluir</button></div>
  <div class="g"><span class="l">Formato e Qualidade</span><div class="sg full" data-k="formato"><button data-v="mp3">MP3</button><button data-v="original">M4A / Opus (Original Bruto)</button><button data-v="video">Vídeo MP4</button></div><p class="note js-fnote"></p></div>
  <div class="g" id="g-r"><span class="l">Resolução do Vídeo</span><div class="sg full" data-k="res"><button data-v="360">360p</button><button data-v="720">720p</button><button data-v="1080">1080p</button></div></div>
  <div class="g" id="g-p"><span class="l">Salvar na Pasta</span><button class="rb js-pasta"><span>Pasta</span><span class="r"><b class="js-pnome">…</b><small class="js-pcam"></small></span></button></div>
  <div class="g"><span class="l">Organização de Playlists</span><div class="sg full" data-k="modo_playlist"><button data-v="pasta">Subpasta própria</button><button data-v="junto">Tudo na pasta principal</button></div></div>
  <p class="note" id="srvnote" hidden>Modo servidor ativado: os arquivos expiram após algumas horas.</p>
</div></div>

<div class="fb" id="fb"><div class="w">
  <div class="row"><b>Escolher pasta de destino</b><button class="t" id="fbx">Fechar</button></div>
  <div id="fbat"></div><div class="sm mut" id="fbp" style="word-break:break-all"></div>
  <div id="fbl"></div>
  <div class="fbf"><button class="s2" id="fbn"><span data-i="folderplus"></span>Criar pasta</button><button class="p" id="fbok">Usar esta pasta</button></div>
</div></div>
<div class="md" id="md"><div class="mb"><p id="mt"></p><input type="text" id="mi" hidden autocomplete="off"><div class="row"><button class="t" id="mn">Cancelar</button><button id="my">Confirmar</button></div></div></div>
<div id="toast"></div>

<script>
const APPN='{{APP}}';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const I={
 down:'<path d="M12 4v11m0 0 4-4m-4 4-4-4M5 20h14"/>',
 search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
 note:'<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
 video:'<rect x="2" y="6" width="14" height="12" rx="2"/><path d="m16 10 4-3v10l-4-3z"/>',
 x:'<path d="M18 6 6 18M6 6l12 12"/>',
 gear:'<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
 folder:'<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
 folderplus:'<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M12 10.5v5M9.5 13h5"/>',
 play:'<path d="M8 5.5v13l11-6.5z" fill="currentColor" stroke="none"/>',
 stop:'<rect x="7" y="7" width="10" height="10" rx="1.5" fill="currentColor" stroke="none"/>',
 back:'<path d="m15 6-6 6 6 6"/>',
 prev:'<path d="M19 5v14L8 12z" fill="currentColor" stroke="none"/><path d="M5 5v14"/>',
 next:'<path d="M5 5v14l11-7z" fill="currentColor" stroke="none"/><path d="M19 5v14"/>',
 rew:'<path d="M11 6v12L2.5 12z" fill="currentColor" stroke="none"/><path d="M21 6v12l-8.5-6z" fill="currentColor" stroke="none"/>',
 ff:'<path d="M13 6v12l8.5-6z" fill="currentColor" stroke="none"/><path d="M3 6v12l8.5-6z" fill="currentColor" stroke="none"/>',
 pause:'<rect x="6" y="5" width="4" height="14" rx="1" fill="currentColor" stroke="none"/><rect x="14" y="5" width="4" height="14" rx="1" fill="currentColor" stroke="none"/>',
 vol:'<path d="M4 9v6h4l5 4V5L8 9z" fill="currentColor" stroke="none"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/>',
 full:'<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>'
};
const ic=(n,s)=>`<svg class="i" viewBox="0 0 24 24"${s?` style="width:${s}px;height:${s}px"`:''}>${I[n]}</svg>`;
$$('[data-i]').forEach(e=>e.innerHTML=ic(e.dataset.i));
const WAVE='<svg viewBox="0 0 76 48" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="70" height="42" rx="6"/><rect x="11" y="9" width="54" height="14" rx="2"/><rect x="20" y="28" width="36" height="11" rx="5.5"/><circle cx="29" cy="33.5" r="2.6"/><circle cx="47" cy="33.5" r="2.6"/></svg>';
const cov=(rel,isVid,cls,icn)=>`<span class="cv ${cls||''}${isVid?' vd':''}">${ic(icn||(isVid?'video':'note'))}<img loading="lazy" decoding="async" src="/api/capa?f=${encodeURIComponent(rel)}" alt="" onerror="this.style.display='none'"></span>`;
let C={},LAST='',LIB={musicas:[],playlists:[],videos:[]},SEL=new Set(),RG=[],FB='',TM,TT,READY=[],LST=[],LR={dup:0,fora:0},PVN=3,PVT,QVN=5,ABAF='fila';
async function api(p,b){const r=await fetch(p,b===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Requested-With':'wavefly'},body:JSON.stringify(b)});const j=await r.json();if(!r.ok||j.erro)throw new Error(j.erro||('Erro '+r.status));return j}
function toast(m){const t=$('#toast');t.textContent=m;t.classList.add('on');clearTimeout(TT);TT=setTimeout(()=>t.classList.remove('on'),Math.min(4500,1700+m.length*28))}
function conf(msg,ok){return new Promise(r=>{$('#mi').hidden=true;$('#mt').innerHTML=msg;$('#my').textContent=ok||'Confirmar';$('#md').classList.add('on');const f=v=>{$('#md').classList.remove('on');r(v)};$('#my').onclick=()=>f(true);$('#mn').onclick=()=>f(false)})}
function ask(msg,ok){return new Promise(r=>{const i=$('#mi');$('#mt').textContent=msg;i.hidden=false;i.value='';$('#my').textContent=ok||'Criar';$('#md').classList.add('on');setTimeout(()=>i.focus(),60);
 const f=v=>{$('#md').classList.remove('on');i.hidden=true;i.onkeydown=null;r(v)};$('#my').onclick=()=>f(i.value.trim());$('#mn').onclick=()=>f(null);i.onkeydown=e=>{if(e.key==='Enter')f(i.value.trim())}})}
const p2=n=>String(n).padStart(2,'0');
const fmt=s=>{s=Math.round(s);const h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;return h?h+' h '+m+' min':m?m+' min '+x+' s':x+' s'};
const tamf=b=>b<1048576?Math.max(1,Math.round(b/1024))+' KB':b<1073741824?(b/1048576).toFixed(b<10485760?1:0)+' MB':(b/1073741824).toFixed(2)+' GB';
const durf=s=>{if(!s)return'?:??';s=Math.round(s);const h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;return h?h+':'+p2(m)+':'+p2(x):m+':'+p2(x)};
const short=u=>u.replace(/^https?:\/\/(www\.)?/,'').slice(0,60);
const vidOf=u=>{const m=(u||'').match(/(?:v=|youtu\.be\/|shorts\/|embed\/|live\/)([\w-]{11})/);return m?m[1]:''};
const plId=u=>{const m=(u||'').match(/[?&]list=([\w-]+)/);return m?m[1]:''};
function segset(g,v){g=typeof g==='string'?$('#'+g):g;[...g.children].forEach(b=>b.classList.toggle('on',b.dataset.v==String(v)))}
const estB=d=>{if(!d)return 0;const f=C.formato,k=f==='mp3'?192:f==='video'?(({360:700,720:1800,1080:3500})[C.res]||1800)+128:128;return d*k*125};

function go(t){$$('.v').forEach(e=>e.hidden=e.id!=='v-'+t);$$('.tabs a').forEach(a=>a.classList.toggle('on',a.dataset.go===t));window.scrollTo(0,0);if(t==='musicas')loadLib();updbars()}
$$('.tabs a').forEach(a=>a.onclick=()=>go(a.dataset.go));

const abrirAj=()=>$('#sheet').classList.add('on'),fecharAj=()=>$('#sheet').classList.remove('on');
$('#bset').onclick=abrirAj;$('#shx').onclick=fecharAj;$('#sheet').onclick=e=>{if(e.target.id==='sheet')fecharAj()};
document.addEventListener('click',e=>{if(e.target.closest('.js-chip'))abrirAj()});
const FN={
 mp3:'MP3 Universal. Ótima qualidade com compatibilidade garantida em qualquer aparelho, som automotivo ou pendrive.',
 original:'M4A ou Opus (Original Bruto). Download rápido e leve direto do YouTube sem conversão.',
 video:'Vídeo completo em formato MP4 com excelente qualidade de som e imagem.'};
async function loadCfg(){try{C=await api('/api/config');rcfg()}catch(e){toast(e.message)}}
function rcfg(){const f=C.formato;
 $$('.js-pnome').forEach(e=>e.textContent=C.atual);$$('.js-pcam').forEach(e=>e.textContent=C.caminho);
 $$('.sg[data-k]').forEach(g=>segset(g,C[g.dataset.k]));
 $$('.js-fnote').forEach(e=>e.textContent=FN[f]||'');
 $('#g-r').hidden=f!=='video';
 let rs=f==='mp3'?`MP3`:f==='video'?`MP4 · ${C.res}p`:'Original';rs+=C.servidor?' · web':' · '+C.atual;
 $$('.js-resumo').forEach(e=>e.textContent=rs);
 $('#g-p').hidden=!!C.servidor;$('#srvnote').hidden=!C.servidor;
 $('#bdel').hidden=!!C.servidor;$('#bdl').hidden=$('#bzip').hidden=!C.servidor;$('#segm [data-v=rep]').hidden=!!C.servidor;
 $('#warn').hidden=C.pasta_ok!==false;$('#warnand').hidden=!C.android;
 let seen='';try{seen=localStorage.getItem('wf_hello')}catch(e){}$('#hello').hidden=!(C.primeira&&!seen);const jk=C.atual+'|'+C.formato+'|'+C.caminho;if(jk!==JKEY){JKEY=jk;JA.clear();JAK.clear();Object.keys(PLP).forEach(k=>delete PLP[k]);if(LST.length)cnt()}ccount();updsel()}
async function cfg(d){try{C=await api('/api/config',d);rcfg()}catch(e){toast(e.message)}}
document.addEventListener('click',e=>{const b=e.target.closest('.sg[data-k] button');if(!b)return;const k=b.parentElement.dataset.k;let v=b.dataset.v;if(k==='res')v=+v;cfg({[k]:v})});
$('#hok').onclick=()=>{try{localStorage.setItem('wf_hello','1')}catch(e){}$('#hello').hidden=true};
$('#hchg').onclick=()=>{$('#hok').click();fbabrir()};

async function fbgo(p){try{const d=await api('/api/navegar?p='+encodeURIComponent(p||''));FB=d.caminho;$('#fbp').textContent=d.caminho;
 $('#fbat').innerHTML=d.atalhos.map(a=>`<button class="t" data-p="${esc(a.caminho)}">${esc(a.nome.replace(/^\S+\s/,''))}</button>`).join('');
 $('#fbl').innerHTML=(d.pai?`<button data-p="${esc(d.pai)}">${ic('back')}Voltar</button>`:'')+d.dirs.map(x=>`<button data-p="${esc(x.caminho)}">${ic('folder')}${esc(x.nome)}</button>`).join('')+(d.dirs.length?'':`<p class="mut sm" style="padding:14px 0">${esc(d.erro||'Nenhuma subpasta aqui. Use esta pasta ou crie uma nova.')}</p>`)}catch(e){toast(e.message)}}
const fbabrir=()=>{fecharAj();$('#fb').classList.add('on');fbgo(C.caminho||'')};
document.addEventListener('click',e=>{if(e.target.closest('.js-pasta'))fbabrir()});
$('#fbx').onclick=()=>$('#fb').classList.remove('on');
$('#fb').onclick=e=>{const b=e.target.closest('[data-p]');if(b)fbgo(b.dataset.p)};
$('#fbok').onclick=async()=>{await cfg({usar_caminho:FB});$('#fb').classList.remove('on');toast('Salvando em: '+C.atual)};
$('#fbn').onclick=async()=>{const n=await ask('Nome da nova pasta');if(!n)return;try{const d=await api('/api/novapasta',{pai:FB,nome:n});await fbgo(d.caminho);toast('Pasta criada')}catch(e){toast(e.message)}};

const LRE=/https?:\/\/.+?(?=https?:\/\/|\s|$)/gi;
const YTRE=/^https?:\/\/([\w-]+\.)*(youtube\.com|youtu\.be|youtube-nocookie\.com)(\/|$|\?)/i;
const normLinks=t=>(t||'').replace(/(^|[\s(<])((?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be)\/)/gi,'$1https://$2');
function parse(t){t=normLinks(t);const seen=new Set(),lst=[];let dup=0,fora=0;for(let l of t.match(LRE)||[]){l=l.replace(/[.,;)>\]'"]+$/,'');if(!YTRE.test(l)){fora++;continue}const id=vidOf(l),isp=/\/playlist|[?&]list=(?!RD|UL)/.test(l),pid=isp?plId(l):'',k=isp&&pid?'pl:'+pid:(id||l);if(seen.has(k)){dup++;continue}seen.add(k);lst.push({url:l,id,pl:isp&&!!pid,pid})}return{n:lst.length,dup,fora,lst}}
const PLP={};
const JA=new Set(),JAK=new Set();let JKEY='',LASTOK=-1;
function jaIds(ids){ids=ids.filter(i=>i&&!JAK.has(i));if(!ids.length)return;ids.forEach(i=>JAK.add(i));
 for(let k=0;k<ids.length;k+=100){const lote=ids.slice(k,k+100);
  api('/api/existe?ids='+lote.join(',')).then(d=>{let n=0;d.ja.forEach(i=>{if(!JA.has(i)){JA.add(i);n++}});if(n){rpv();ccount()}}).catch(()=>lote.forEach(i=>JAK.delete(i)))}}
const plSelDur=p=>p.itens.reduce((a,x)=>a+(p.sel.has(x.id)?(x.dur||0):0),0);
const plHead=p=>{const e=estB(plSelDur(p));return `${p.sel.size} de ${p.itens.length-p.nja} selecionados`+(p.nja?` · ${p.nja} já existe${p.nja>1?'m':''} na subpasta`:'')+(e?` · ~${tamf(e)}`:'')};
function carregaPL(x){if(PLP[x.pid])return;const p=PLP[x.pid]={pid:x.pid,titulo:'Playlist',canal:'',itens:[],sel:new Set(),nja:0,vis:30,open:false,loading:true,erro:''};
 api('/api/playlist?id='+encodeURIComponent(x.pid)).then(d=>{p.titulo=d.titulo||'Playlist';p.canal=d.canal||'';p.itens=d.itens;p.nja=d.itens.filter(i=>i.ja).length;p.sel=new Set(d.itens.filter(i=>!i.ja).map(i=>i.id));if(!d.itens.length)p.erro='Playlist vazia ou privada'}).catch(e=>{p.erro=e.message||'Não foi possível abrir a playlist'}).finally(()=>{p.loading=false;rpv();ccount()})}
function plRow(p,x){const j=!!x.ja;return `<label class="rs${j?' off':''}"><input type="checkbox" data-pc="${esc(p.pid)}" data-vid="${esc(x.id)}" ${p.sel.has(x.id)?'checked':''} ${j?'disabled':''}><span class="th"><img loading="lazy" src="https://i.ytimg.com/vi/${esc(x.id)}/mqdefault.jpg" alt=""><button type="button" class="pp" data-pv="${esc(x.id)}" aria-label="Ouvir prévia">${ic('play',18)}</button></span><div class="bd2"><div class="tt">${esc(x.titulo)}</div>${j?'<div class="ja tt">Já existe na subpasta · duplicada ignorada</div>':`<div class="sm mut tt">${esc(x.canal||'')}${x.canal&&x.dur?' · ':''}${x.dur?durf(x.dur):''} ${x.views?' · '+x.views+' views':''} ${x.tamanho?'· '+x.tamanho:''}</div>`}</div></label>`}
function plHTML(p){const pid=esc(p.pid);
 if(p.loading)return `<div class="plc"><div class="tt">Playlist</div><div class="sm mut">Carregando itens...</div></div>`;
 if(p.erro)return `<div class="plc"><div class="tt">Playlist</div><div class="sm er">${esc(p.erro)}</div></div>`;
 let h=`<div class="plc"><div class="plh"><img class="ft s" loading="lazy" src="https://i.ytimg.com/vi/${esc(p.itens[0].id)}/mqdefault.jpg" alt=""><div class="bd2"><div class="tt">${esc(p.titulo)}</div><div class="sm mut tt" data-ph="${pid}">${plHead(p)}</div></div><button class="t" data-pa="open" data-pid="${pid}" style="color:var(--at);font-weight:600">${p.open?'Ocultar':'Entrar'}</button></div>`;
 if(p.open)h+=`<div class="row" style="margin:6px 0 2px"><span class="sm mut">${p.itens.length} itens</span><span><button class="t" data-pa="all" data-pid="${pid}">Selecionar todos</button><button class="t" data-pa="none" data-pid="${pid}">Desmarcar todos</button></span></div>`+p.itens.slice(0,p.vis).map(x=>plRow(p,x)).join('')+(p.vis<p.itens.length?`<button class="more" data-pa="more" data-pid="${pid}">Mostrar mais</button>`:'');
 return h+'</div>'}
const TITS=new Map(),TQ=[];let TA=0;
function fetchTit(id){if(TITS.has(id)||TQ.includes(id))return;TQ.push(id);pumpT()}
let RPVT=0;function refazer(){clearTimeout(RPVT);RPVT=setTimeout(()=>{rpv();ccount()},120)}
function pumpT(){while(TA<3&&TQ.length){const id=TQ.shift();TA++;api('/api/titulo?id='+encodeURIComponent(id)+(LST.length<=5?'&live=1':'')).then(d=>TITS.set(id,(d.titulo||d.live)?d:{titulo:'',canal:'',erro:true})).catch(()=>TITS.set(id,{titulo:'',canal:'',erro:true})).finally(()=>{TA--;updTit(id);if(!JA.has(id)){JAK.delete(id);jaIds([id])}const dd=TITS.get(id);if(dd&&(dd.erro||dd.live))refazer();pumpT()})}}
const titTxt=(id,d)=>d.titulo||(d.erro?'Vídeo '+id:'Carregando...');
function updTit(id){const d=TITS.get(id)||{};$$(`[data-tid="${id}"]`).forEach(e=>e.textContent=titTxt(id,d));$$(`[data-cid="${id}"]`).forEach(e=>e.textContent=d.canal||(d.erro?'Título indisponível':''))}
const indisp=x=>!!(x.id&&TITS.get(x.id)&&TITS.get(x.id).erro&&!TITS.get(x.id).titulo);
const aoVivo=x=>!!(x.id&&TITS.get(x.id)&&TITS.get(x.id).live);
function tirarLink(url){const ta=$('#ta');ta.value=ta.value.split('\n').filter(l=>!l.includes(url)&&!(url.match(/[\w-]{11}$/)&&l.includes(url.match(/[\w-]{11}$/)[0]))).join('\n');PVN=3;cnt()}
function rpv(){const b=$('#pv');if(!LST.length){b.hidden=true;b.innerHTML='';return}
 const pls=LST.filter(x=>x.pl),sing=LST.filter(x=>!x.pl&&!indisp(x));pls.forEach(carregaPL);
 const vis=sing.slice(0,PVN),rest=sing.length-vis.length;b.hidden=false;
 b.innerHTML=pls.map(x=>plHTML(PLP[x.pid])).join('')+vis.map(x=>{const d=x.id?(TITS.get(x.id)||{}):{},j=!!(x.id&&JA.has(x.id));
  const th=x.id?`<img class="ft s" loading="lazy" src="https://i.ytimg.com/vi/${esc(x.id)}/mqdefault.jpg" alt="">`:'<span class="ft s"></span>';
  const lv=aoVivo(x);
  const l2=lv?'<div class="ja tt">Transmissão ao vivo: não dá para baixar</div>':j?'<div class="ja tt">Já existe na pasta · marcada como duplicada</div>':`<div class="sm mut tt" data-cid="${esc(x.id)}">${esc(d.canal||(d.erro?'Título indisponível':'Carregando...'))}</div>`;
  const tt=x.id?`<div class="tt" data-tid="${esc(x.id)}">${esc(titTxt(x.id,d))}</div>${l2}`:`<div class="tt">Link do YouTube</div><div class="sm mut tt">${esc(short(x.url))}</div>`;
  return `<div class="pr${j||lv?' off':''}" ${j||lv?'style="opacity:.7"':''}>${th}<div class="bd2">${tt}</div><button class="pvx" data-rm="${esc(x.url)}" aria-label="Remover" data-i="x">×</button></div>`}).join('')+
  (rest>0?`<button class="t" id="pvmais">Ver mais (${Math.min(7,rest)})</button>`:'')+(PVN>3&&sing.length>3?'<button class="t" id="pvmenos">Recolher</button>':'');
 vis.forEach(x=>{if(x.id)fetchTit(x.id)})}
$('#pv').onclick=e=>{const t=e.target;
 const rm=t.closest('[data-rm]');if(rm){return tirarLink(rm.dataset.rm)}
 if(t.id==='pvmais'){PVN=(PVN===3)?10:(PVN+10);return rpv()}
 if(t.id==='pvmenos'){PVN=3;return rpv()}
 const a=t.closest('[data-pa]');if(!a)return;const p=PLP[a.dataset.pid];if(!p)return;const k=a.dataset.pa;
 if(k==='open')p.open=!p.open;else if(k==='all')p.sel=new Set(p.itens.filter(i=>!i.ja).map(i=>i.id));else if(k==='none')p.sel.clear();else if(k==='more')p.vis+=10;
 rpv();ccount()};
$('#pv').onchange=e=>{const c=e.target.closest('input[data-pc]');if(!c)return;const p=PLP[c.dataset.pc];if(!p)return;c.checked?p.sel.add(c.dataset.vid):p.sel.delete(c.dataset.vid);const h=$(`[data-ph="${c.dataset.pc}"]`);if(h)h.textContent=plHead(p);ccount()};
function ccount(){const MX=C.max_links||1000;let pls=0,sing=0,sel=0,est=0,pend=0,jaN=0;
 LST.forEach(x=>{const p=x.pl?PLP[x.pid]:null;if(p&&p.loading)pend++;else if(p&&!p.erro&&p.itens.length){pls++;sel+=p.sel.size;jaN+=p.nja;est+=estB(plSelDur(p))}else if(x.id&&JA.has(x.id))jaN++;else if(indisp(x)||aoVivo(x)){}else sing++});
 const tot=sing+sel;let s=LST.length?`${tot} ${tot===1?'item':'itens'}`+(pls?` · ${pls} playlist${pls>1?'s':''}`:'')+(pend?' · carregando...':''):(LR.dup?` · ${LR.dup} repetidos`:'');
 if(jaN)s+=` · ${jaN} duplicados marcados`;
 if(est)s+=` · ~${tamf(est)}`;
 $('#cnt').textContent=s;$('#bgo').textContent=tot>1?`Baixar ${Math.min(tot,MX)}`:'Baixar';$('#bgo').hidden=!(tot>0)}
let LASTDUP=0;
function cnt(){
 const raw=$('#ta').value;
 const r=parse(raw);
 LST=r.lst;
 LR={dup:r.dup,fora:r.fora};
 
 // Aviso dinâmico instantâneo se houver links repetidos detectados na caixa de texto
 if(r.dup > LASTDUP){
  const novos=r.dup-LASTDUP;toast(`${novos} repetido${novos>1?'s':''} ignorado${novos>1?'s':''}`);
 }
 LASTDUP=r.dup;
 
 jaIds(LST.filter(x=>!x.pl).map(x=>x.id));ccount();clearTimeout(PVT);PVT=setTimeout(rpv,250)}
$('#ta').oninput=()=>{PVN=3;cnt()};
$('#bclr').onclick=()=>{$('#ta').value='';PVN=3;cnt()};
$('#bpaste').onclick=async()=>{let t='';try{t=(window.WF&&WF.paste)?WF.paste():await navigator.clipboard.readText()}catch(e){}t=(t||'').trim();if(t){$('#ta').value+=($('#ta').value?'\n':'')+t;cnt()}else toast('Nenhum link copiado.')};
let WFLAST='';window.wfClip=()=>{try{if(!window.WF||!WF.paste)return;const ta=$('#ta');if(!ta||ta.value.trim())return;const t=(WF.paste()||'').trim();if(/^https?:\/\/\S+$/i.test(t)&&t!==WFLAST){WFLAST=t;ta.value=t;cnt();toast('Link copiado colado')}}catch(e){}};
$('#bgo').onclick=async()=>{const t=$('#ta').value,r=parse(t);try{
  // TITS é onde o preview guarda o nome de verdade
  if(typeof TITS!=='undefined') TITS.forEach((v,k)=>{ if(v&&v.titulo){window.__TIT['https://www.youtube.com/watch?v='+k]=v.titulo; window.__TIT[k]=v.titulo} });
  r.lst.forEach(x=>{if(x.titulo&&x.url)window.__TIT[x.url]=x.titulo;if(x.titulo&&x.id)window.__TIT[x.id]=x.titulo});
  // playlist: titulo vem de PLP
  try{Object.values(PLP||{}).forEach(pl=>{(pl.itens||[]).forEach(it2=>{if(it2.titulo)window.__TIT['https://www.youtube.com/watch?v='+it2.id]=it2.titulo; window.__TIT[it2.id]=it2.titulo})})}catch(_){}
  try{localStorage.setItem('wf_tit', JSON.stringify(window.__TIT))}catch(_){}
}catch(_){}if(!r.n)return toast('Cole pelo menos um link do YouTube');
 if(r.lst.some(x=>x.pl&&PLP[x.pid]&&PLP[x.pid].loading))return toast('Aguarde o carregamento da playlist.');
 const keep=[],listas=[];r.lst.forEach(x=>{const p=x.pl?PLP[x.pid]:null;if(p&&!p.erro&&p.itens.length){if(p.sel.size)listas.push({pid:p.pid,titulo:p.titulo,ids:p.itens.filter(i=>p.sel.has(i.id)).map(i=>i.id)})}else if(!(x.id&&JA.has(x.id))&&!indisp(x)&&!aoVivo(x))keep.push(x.url)});
 
 const b=$('#bgo');b.disabled=true;b.textContent='Processando links...';
 try{const d=await api('/api/add',{texto:keep.join('\n'),listas,titulos:window.__TIT||{}});$('#ta').value='';PVN=3;let m=d.add?`${d.add} adicionado${d.add>1?'s':''}`:`Nada novo`;
  const ign=(d.rep||0)+(d.ja||0);
  if(ign)m+=` · ${ign} ignorado${ign>1?'s':''}`;
  else if(d.ja)m+=` · ${d.ja} já existente${d.ja>1?'s':''}`;
  toast(m);tick()}
 catch(e){toast(e.message)}b.disabled=false;cnt()};

function rowHTML(i){let sub='',cls='';
 if(i.status==='baixando')sub=(i.vel&&/Lendo|Convertendo|Juntando|Baixando/.test(i.vel)?i.vel:(i.pct||0)+'%'+(i.vel?' · '+i.vel:''));
 else if(i.status==='falha'){sub='Falhou: '+(i.erro||'erro');cls=' er'}
 else if(i.status==='duplicada')sub='Já existe na pasta (será ignorado)';
 else if(i.status==='ok')sub='Concluído';
 else if(i.status==='cancelada')sub='Cancelada';
 else sub=(i.sub&&!/lendo nome/i.test(i.sub))?'Na fila · '+i.sub:'Na fila';
 let a='';
 if(i.status==='duplicada'||i.status==='cancelada'||i.status==='falha')a+=`<button class="t" data-a="forcar" data-id="${i.id}" style="color:var(--at);font-weight:600">Forçar</button>`;
 if(i.status==='falha')a+=`<button class="t" data-a="retentar" data-id="${i.id}">Tentar de novo</button>`;
 if(i.status==='ok'&&i.arq&&C.servidor)a+=`<a class="t" style="color:var(--at);font-size:13.5px;padding:4px 6px" href="/api/baixar?f=${encodeURIComponent(i.arq)}" download>Receber</a>`;
 a+=`<button class="t" data-a="remover" data-id="${i.id}">${i.status==='baixando'?'Cancelar':'Remover'}</button>`;
 const v=vidOf(i.url),th=v?`<img class="ft" loading="lazy" src="https://i.ytimg.com/vi/${v}/mqdefault.jpg" alt="">`:'<span class="ft"></span>';
 return `<div class="it" data-id="${i.id}">${th}<div class="bd"><div class="tt${i.status==='ok'?' d':''}">${esc((i.titulo&&!i.titulo.includes('http')?i.titulo:null)||(window.__TIT||{})[i.url]||(window.__TIT||{})[i.id]||((typeof TITS!=='undefined'&&TITS.get(vidOf(i.url))||{}).titulo)||(i.titulo||short(i.url)))}</div><div class="sm mut${cls}">${esc(sub)}</div>${i.status==='baixando'?`<div class="bar" style="margin-top:4px"><i style="width:${i.pct||0}%"></i></div>`:''}</div><div style="flex:none;display:flex;align-items:center">${a}</div></div>`}
const ORD={baixando:0,fila:1,falha:2,duplicada:3,cancelada:4,ok:5};
function draw(s){const c=s.ok+s.duplicada+s.falha+s.cancelada,at=s.fila+s.baixando>0;
 if(s.ok!==LASTOK){const first=LASTOK<0;LASTOK=s.ok;if(!first){JA.clear();JAK.clear();if(LST.length)cnt()}}
 document.title=(at?`${c}/${s.total} · `:'')+APPN;$('#fila').hidden=!s.total;if(!s.total){LAST='';READY=[];return}
 READY=s.itens.filter(i=>i.status==='ok'&&i.arq).map(i=>i.arq);$('#entrega').hidden=!(C.servidor&&READY.length);$('#en').textContent=READY.length;
 $('#eq').classList.toggle('on',at);document.body.classList.toggle('baixando',at);$('#fh').textContent=at?'Baixando Fila':'Concluído';$('#fc').textContent=`${c} de ${s.total}`;$('#fbar').style.width=Math.round(c/s.total*100)+'%';
 const p=[];if(s.ok)p.push(s.ok+' concluídas');if(s.duplicada)p.push(s.duplicada+' duplicadas');if(s.falha)p.push(s.falha+' falhas');
 p.push(fmt(s.dec));if(at&&c>0)p.push('faltam ~'+fmt(s.dec/c*(s.fila+s.baixando)));
 if(s.est)p.push('~'+tamf(s.est)+' est.');$('#fs').textContent=p.join(' · ');
 $('#fav').hidden=!s.aviso;$('#fav').textContent=s.aviso||'';
 $('#bcanc').hidden=!at;$('#blimpa').hidden=!(s.ok+s.duplicada);
 const k=JSON.stringify(s.itens)+'|'+QVN+'|'+ABAF;if(k===LAST)return;LAST=k;
 const it=s.itens.slice().sort((a,b)=>ORD[a.status]-ORD[b.status]||a.id-b.id);
 const nOk=it.filter(x=>x.status==='ok').length, nFila=it.length-nOk;
 const abaF=$('#abaFila'),abaO=$('#abaOk');if(abaF){abaF.textContent=`Fila (${nFila})`;abaO.textContent=`Concluídas (${nOk})`;abaF.style.background=ABAF==='fila'?'var(--at)':'';abaF.style.color=ABAF==='fila'?'#fff':'';abaO.style.background=ABAF==='ok'?'var(--at)':'';abaO.style.color=ABAF==='ok'?'#fff':'';}
 const it2=ABAF==='ok'?it.filter(x=>x.status==='ok'):it.filter(x=>x.status!=='ok');
 $('#lista').innerHTML=it2.slice(0,QVN).map(rowHTML).join('')+(it2.length>QVN?`<button class="t" data-q="mais" style="margin:8px 0">Ver mais 5 (${it2.length-QVN} restantes)</button>`:'')+(QVN>5?`<button class="t" data-q="menos" style="margin:8px 0 8px 6px">Recolher</button>`:'')}
$('#abasFila').onclick=e=>{const b=e.target.closest('button[data-aba]');if(!b)return;ABAF=b.dataset.aba;QVN=5;LAST='';tick()};
$('#lista').onclick=async e=>{const q=e.target.closest('button[data-q]');if(q){if(q.dataset.q==='mais')QVN+=5;else QVN=5;LAST='';return tick()}const b=e.target.closest('button[data-a]');if(!b)return;try{await api('/api/acao',{acao:b.dataset.a,id:+b.dataset.id});tick()}catch(x){toast(x.message)}};
$('#blimpa').onclick=async()=>{await api('/api/acao',{acao:'limpar'});tick()};
$('#bcanc').onclick=async()=>{if(await conf('Cancelar <b>tudo</b> e interromper os downloads?','Cancelar tudo')){await api('/api/acao',{acao:'cancelar_tudo'});tick()}};
async function tick(){clearTimeout(TM);try{draw(await api('/api/estado'))}catch(e){}TM=setTimeout(tick,document.hidden?4000:1000)}

function receberSoltos(rels){if(!rels.length)return;toast(rels.length>1?`Baixando ${rels.length} arquivos...`:'Baixando...');
 rels.forEach((r,i)=>setTimeout(()=>{const a=document.createElement('a');a.href='/api/baixar?f='+encodeURIComponent(r);a.download='';document.body.appendChild(a);a.click();a.remove()},i*700))}
async function receberZip(rels){if(!rels.length)return;try{toast('Compactando arquivos em ZIP...');const d=await api('/api/zip',{rels});const a=document.createElement('a');a.href=d.url;a.download=d.nome;document.body.appendChild(a);a.click();a.remove();toast(`ZIP pronto com ${d.qtd} arquivos`)}catch(e){toast(e.message)}}
$('#bsolto').onclick=()=>receberSoltos(READY);$('#bzipq').onclick=()=>receberZip(READY);
$('#bdl').onclick=()=>receberSoltos([...SEL]);$('#bzip').onclick=()=>receberZip([...SEL]);

async function loadLib(){try{const d=await api('/api/arquivos');LIB=d;let sv=ACTIVE_PL?ACTIVE_PL.nome:'';if(!sv){try{sv=localStorage.getItem('wf_pl_aberta')||''}catch(e){}}ACTIVE_PL=sv?(d.playlists||[]).find(p=>p.nome===sv)||null:null;dlib()}catch(e){toast(e.message)}}
function updbars(){
 const off=$('#v-musicas').hidden,rep=!$('#m-rep').hidden,n=nrep();
 $('#libbar').hidden=off||rep||!SEL.size;
 $('#selc').textContent=SEL.size?(SEL.size+(SEL.size>1?' selecionados':' selecionado')):'';
 $('#repbar').hidden=off||!rep||!n;$('#repc').textContent=n+(n>1?' marcadas':' marcada')
}
function nrep(){return RG.reduce((a,g)=>a+g.arquivos.filter(x=>x.marcada).length,0)}

let ACTIVE_PL = null;
let PL_FILTRO_VID = false;try{PL_FILTRO_VID=localStorage.getItem('wf_vid_filtro')==='1'}catch(e){}
const svPL=()=>{try{ACTIVE_PL?localStorage.setItem('wf_pl_aberta',ACTIVE_PL.nome):localStorage.removeItem('wf_pl_aberta');localStorage.setItem('wf_vid_filtro',PL_FILTRO_VID?'1':'0')}catch(e){}};

let LIBN=60,LIBNV=60,LIBQ=[],LIBQV=[],LIBIO=null;
function dlib(){
 $('#wrapvid').hidden=!(ACTIVE_PL&&ACTIVE_PL.tem_mp4);$('#chkvid').checked=PL_FILTRO_VID;
 const f=$('#lf').value.trim().toLowerCase();
 const fv=$('#lfv').value.trim().toLowerCase();
 
 let mus = LIB.musicas || [];
 if(f) mus = mus.filter(x=>(x.nome+' '+x.pasta).toLowerCase().includes(f));
 
 let pls = LIB.playlists || [];
 let hPls = '';
 if(ACTIVE_PL){
  hPls = `<button class="t" id="bvoltapl" style="margin:2px 0 8px">‹ Voltar às pastas</button><h2>${esc(ACTIVE_PL.nome)}</h2><div class="sm mut" style="margin-bottom:8px">${ACTIVE_PL.total} arquivos${ACTIVE_PL.tem_mp4?' · <span style="color:#ffb74d;font-weight:600">Contém vídeo</span>':''}</div>` +
   (LIBQ=(PL_FILTRO_VID ? [...ACTIVE_PL.itens].sort((a,b)=>((/\.(mp4|mkv)$/i.test(a.rel)) - (/\.(mp4|mkv)$/i.test(b.rel)))) : ACTIVE_PL.itens.filter(x=>!/\.(mp4|mkv)$/i.test(x.rel))).map(x=>x.rel),
    (PL_FILTRO_VID ? [...ACTIVE_PL.itens].sort((a,b)=>((/\.(mp4|mkv)$/i.test(a.rel)) - (/\.(mp4|mkv)$/i.test(b.rel)))) : ACTIVE_PL.itens.filter(x=>!/\.(mp4|mkv)$/i.test(x.rel))).slice(0,LIBN)).map(x=>{
    const isVid = x.rel.toLowerCase().endsWith('.mp4') || x.rel.toLowerCase().endsWith('.mkv');
    return `<div class="lr"><label><input type="checkbox" data-rel="${esc(x.rel)}" ${SEL.has(x.rel)?'checked':''}>${cov(x.rel, isVid)}<span class="nm">${esc(x.nome)}</span></label><span class="sm mut">${tamf(x.tam)}</span><button class="t" data-playrel="${esc(x.rel)}">${isVid?'Assistir':'Ouvir'}</button></div>`;
   }).join('');
 } else {
  hPls = pls.map(p=>`<div class="pl-card">${cov(p.primeira_rel,false,'lg','folder')}<div class="bd2"><div class="tt"><b>${esc(p.nome)}</b></div><div class="sm mut">${p.total} itens · Início: ${esc(p.primeira_musica)}${p.tem_mp4?' <span class="er" style="font-weight:600">· Contém vídeo</span>':''}</div></div><button class="t" data-oppl="${esc(p.nome)}" style="color:var(--at);font-weight:600">Entrar</button></div>`).join('');
  if(pls.length && mus.length) hPls += `<div class="lh"><span>Arquivos Soltos na Raiz</span></div>`;
  LIBQ=mus.map(x=>x.rel);
  hPls += mus.slice(0,LIBN).map(x=>`<div class="lr"><label><input type="checkbox" data-rel="${esc(x.rel)}" ${SEL.has(x.rel)?'checked':''}>${cov(x.rel, false)}<span class="nm">${esc(x.nome)}</span></label><span class="sm mut">${tamf(x.tam)}</span><button class="t" data-playrel="${esc(x.rel)}">Ouvir</button></div>`).join('');
 }
 const totalLib = ACTIVE_PL ? LIBQ.length : mus.length;
 if(totalLib>LIBN) hPls += `<div id="libmais" class="sm mut" style="text-align:center;padding:14px">Mostrando ${LIBN} de ${totalLib} · role para ver mais</div>`;
 $('#lib').innerHTML = hPls || `<div class="empty">${WAVE}<p>Nenhum arquivo encontrado.</p></div>`;

 let vids = LIB.videos || [];
 if(fv) vids = vids.filter(x=>(x.nome+' '+x.pasta).toLowerCase().includes(fv));
 LIBQV=vids.map(x=>x.rel);
 $('#libv').innerHTML = vids.length ? vids.slice(0,LIBNV).map(x=>`<div class="lr"><label><input type="checkbox" data-rel="${esc(x.rel)}" ${SEL.has(x.rel)?'checked':''}>${cov(x.rel, true)}<span class="nm">${esc(x.nome)}</span></label><span class="sm mut">${tamf(x.tam)}</span><button class="t" data-playrel="${esc(x.rel)}">Assistir</button></div>`).join('') : `<div class="empty">${WAVE}<p>Nenhum vídeo MP4 encontrado nesta pasta.</p></div>`;
 if(vids.length>LIBNV) $('#libv').insertAdjacentHTML('beforeend',`<div id="libvmais" class="sm mut" style="text-align:center;padding:14px">Mostrando ${LIBNV} de ${vids.length} · role para ver mais</div>`);
 try{if(LIBIO)LIBIO.disconnect();LIBIO=new IntersectionObserver(es=>{es.forEach(en=>{if(!en.isIntersecting)return;if(en.target.id==='libmais'){LIBN+=60}else{LIBNV+=60}dlib()})},{rootMargin:'600px'});['libmais','libvmais'].forEach(i=>{const el=document.getElementById(i);if(el)LIBIO.observe(el)})}catch(e){}

 const totalItens = (LIB.musicas?.length||0) + (LIB.videos?.length||0) + (LIB.playlists?.reduce((a,b)=>a+b.total,0)||0);
 $('#libinfo').textContent = `${totalItens} arquivos`;
 updbars();marcarNow();
}

$('#lf').oninput=()=>{LIBN=60;dlib()};$('#lfv').oninput=()=>{LIBNV=60;dlib()};

document.addEventListener('click',e=>{
 if(e.target.id==='chkvid'){PL_FILTRO_VID=e.target.checked;svPL();return dlib()}
  const opp=e.target.closest('[data-oppl]');
 if(opp){const nome=opp.dataset.oppl;ACTIVE_PL=LIB.playlists.find(p=>p.nome===nome)||null;PL_FILTRO_VID=false;LIBN=60;svPL();return dlib()}
 if(e.target.id==='bvoltapl'){ACTIVE_PL=null;PL_FILTRO_VID=false;LIBN=60;svPL();return dlib()}
 const pr=e.target.closest('[data-playrel]');
 if(pr){tocar(pr.dataset.playrel,pr.closest('#lib,#libv'));return}
 const cb=e.target.closest('input[data-rel]');
 if(cb){const rel=cb.dataset.rel;cb.checked?SEL.add(rel):SEL.delete(rel);updbars()}
});

$$('#segm button').forEach(b=>b.onclick=()=>{
 segset('segm',b.dataset.v);
 $('#m-todas').hidden=b.dataset.v!=='todas';
 $('#m-videos').hidden=b.dataset.v!=='videos';
 $('#m-rep').hidden=b.dataset.v!=='rep';
 updbars();
});

let CUR='';
let QUEUE=[];
let ST_STOP=false;
let VOL=0.9;try{const v=parseFloat(localStorage.getItem('wf_vol'));if(v>=0&&v<=1)VOL=v}catch(e){}
const MA=()=>$('#au');
const tf=s=>{s=Math.max(0,Math.floor(s||0));const h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;return h?h+':'+p2(m)+':'+p2(x):p2(m)+':'+p2(x)};
function marcarNow(){$$('#lib .lr,#libv .lr').forEach(r=>{const b=r.querySelector('[data-playrel]');r.classList.toggle('now',!!b&&!!CUR&&b.dataset.playrel===CUR)})}
function proxima(d){const i=QUEUE.indexOf(CUR),n=i<0?null:QUEUE[i+d];if(n)tocar(n);else if(d>0)stopPlayer()}
function plState(st){const p=$('#pl');p.dataset.st=st;p.classList.toggle('rodando',st==='play');const b=$('#bplay');b.innerHTML=ic(st==='play'?'pause':'play');b.setAttribute('aria-label',st==='play'?'Pausar':'Tocar')}
function plTime(){const a=MA();if(!a)return;const d=isFinite(a.duration)?a.duration:0,c=a.currentTime||0,pc=d?Math.min(1,c/d):0;
 $('#tcur').textContent=tf(c);$('#tdur').textContent=d?tf(d):'--:--';$('#pfill').style.width=(pc*100)+'%'}
function tocar(rel,box){
 const all=[...(LIB.musicas||[]),...(LIB.videos||[]),...(LIB.playlists||[]).flatMap(p=>p.itens)];
 const x=all.find(i=>i.rel===rel);if(!x)return;
 if(box)QUEUE=(box.id==='libv'?LIBQV:LIBQ).length?[...(box.id==='libv'?LIBQV:LIBQ)]:[...box.querySelectorAll('[data-playrel]')].map(b=>b.dataset.playrel);
 const vid=/\.(mp4|mkv)$/i.test(rel),url='/api/audio?f='+encodeURIComponent(rel),capa='/api/capa?f='+encodeURIComponent(rel);
 CUR=rel;
 $('#plt').textContent=x.nome;$('#pls').textContent=x.pasta||(vid?'Vídeo':'Música');
 $('#pl').hidden=false;$('#pl').classList.toggle('aud',!vid);document.body.classList.add('pon');
 $('#tv-screen').innerHTML='';$('#pl-audio').innerHTML='';ST_STOP=false;
 (vid?$('#tv-screen'):$('#pl-audio')).innerHTML=vid?`<video id="au" autoplay playsinline src="${url}"></video>`:`<audio id="au" autoplay src="${url}"></audio>`;
 const a=MA();a.volume=VOL;
 a.onended=()=>proxima(1);a.onerror=()=>toast('Não consegui reproduzir este arquivo');
 a.onplay=()=>{ST_STOP=false;plState('play')};a.onpause=()=>plState(ST_STOP?'stop':'pause');
 a.ontimeupdate=plTime;a.onloadedmetadata=plTime;a.ondurationchange=plTime;
 plState('pause');plTime();
 if('mediaSession' in navigator){try{navigator.mediaSession.metadata=new MediaMetadata({title:x.nome,artist:APPN,artwork:[{src:capa}]});
  navigator.mediaSession.setActionHandler('nexttrack',()=>proxima(1));navigator.mediaSession.setActionHandler('previoustrack',()=>proxima(-1))}catch(e){}}
 marcarNow()}
const togglePlay=()=>{const a=MA();if(!a)return;if(a.paused){ST_STOP=false;const r=a.play();if(r&&r.catch)r.catch(()=>{})}else a.pause()};
$('#plprev').onclick=()=>proxima(-1);$('#plnext').onclick=()=>proxima(1);
$('#bplay').onclick=togglePlay;
$('#brew').onclick=()=>{const a=MA();if(a)a.currentTime=Math.max(0,a.currentTime-10)};
$('#bff').onclick=()=>{const a=MA();if(a&&isFinite(a.duration))a.currentTime=Math.min(a.duration-0.2,a.currentTime+10)};
$('#bfs').onclick=()=>{const a=MA();if(!a)return;const f=a.requestFullscreen||a.webkitRequestFullscreen||a.webkitEnterFullscreen;if(f)try{f.call(a)}catch(e){}};
$('#bvol').onclick=()=>{$('#vrow').hidden=!$('#vrow').hidden};
$('#tv-screen').onclick=togglePlay;
const TRK=$('#ptrack');let DRAG=false;
function seekAt(e){const a=MA();if(!a||!isFinite(a.duration))return;const r=TRK.getBoundingClientRect();a.currentTime=Math.min(1,Math.max(0,(e.clientX-r.left)/r.width))*a.duration;plTime()}
TRK.onpointerdown=e=>{DRAG=true;try{TRK.setPointerCapture(e.pointerId)}catch(x){}seekAt(e)};
TRK.onpointermove=e=>{if(DRAG)seekAt(e)};
TRK.onpointerup=TRK.onpointercancel=()=>{DRAG=false};
const VOLI=$('#vol');VOLI.value=Math.round(VOL*100);
VOLI.oninput=()=>{VOL=VOLI.value/100;const a=MA();if(a)a.volume=VOL;try{localStorage.setItem('wf_vol',String(VOL))}catch(e){}};
try{new ResizeObserver(()=>document.documentElement.style.setProperty('--plh',($('#pl').offsetHeight||0)+'px')).observe($('#pl'))}catch(e){}
function stopPlayer(){
 const a=MA();if(a){ST_STOP=true;a.pause();a.removeAttribute('src');a.load()}
 $('#pl').hidden=true;$('#tv-screen').innerHTML='';$('#pl-audio').innerHTML='';
 $('#pl').classList.remove('rodando');document.body.classList.remove('pon');CUR='';marcarNow()
}
function stopIf(r){if(CUR&&r.includes(CUR))stopPlayer()}
$('#plx').onclick=stopPlayer;
$('#bsl').onclick=()=>{SEL.clear();dlib()};
$('#bdel').onclick=async()=>{const n=SEL.size;if(!n)return;if(await conf(`Apagar <b>${n}</b> arquivo${n>1?'s':''} do aparelho?`,'Apagar')){try{stopIf([...SEL]);const r=await api('/api/apagar',{rels:[...SEL]});SEL.clear();toast(r.apagadas+' apagados');loadLib()}catch(e){toast(e.message)}}};

$('#bvar').onclick=async()=>{const b=$('#bvar');b.disabled=true;b.textContent='Procurando...';
 try{RG=(await api('/api/repetidas',{})).grupos;drep();if(!RG.length)$('#rep').innerHTML=`<div class="empty">${WAVE}<p>Nenhuma repetida encontrada.</p></div>`}catch(e){toast(e.message)}b.disabled=false;b.textContent='Procurar repetidas'};
function drep(){$('#rep').innerHTML=RG.map((g,gi)=>`<div class="lh"><span>${g.tipo==='certa'?'Cópias Exatas':'Parecidas'}</span></div>`+g.arquivos.map((x,j)=>`<div class="lr"><label><input type="checkbox" data-g="${gi}" data-j="${j}" ${x.marcada?'checked':''}>${cov(x.rel, x.rel.toLowerCase().endsWith('.mp4'))}<span class="nm">${esc(x.nome)}</span></label><span class="sm mut">${durf(x.dur)} · ${tamf(x.tam)}</span></div>`).join('')).join('');updbars()}
$('#rep').onchange=e=>{const c=e.target.closest('input[data-g]');if(!c)return;RG[+c.dataset.g].arquivos[+c.dataset.j].marcada=c.checked;updbars()};
$('#brdel').onclick=async()=>{const rels=[];RG.forEach(g=>g.arquivos.filter(x=>x.marcada).forEach(x=>rels.push(x.rel)));if(!rels.length)return;
 if(await conf(`Apagar <b>${rels.length}</b> arquivos marcados?`,'Apagar')){try{stopIf(rels);const r=await api('/api/apagar',{rels});RG=[];$('#rep').innerHTML='';updbars();toast(r.apagadas+' apagados')}catch(e){toast(e.message)}}};

const mkS=()=>({q:'',itens:[],vis:10,mais:false,erro:'',busy:false});
const ST={musica:mkS(),playlist:mkS()};
let MB='musica',PLV=null,SELM=new Map(),TRAY=false,BL=false;const INFO=new Map();
try{SELM=new Map(JSON.parse(localStorage.getItem('wf_sel')||'[]'))}catch(e){}
const meta=x=>({id:x.id,titulo:x.titulo,canal:x.canal||'',dur:x.dur||0});
function selSave(){try{localStorage.setItem('wf_sel',JSON.stringify([...SELM]))}catch(e){}}
function buscaSave(){if(!BL)return;try{if(!SELM.size){localStorage.removeItem('wf_busca');return}
 const pk=s=>({q:s.q,itens:s.itens,vis:s.vis,mais:s.mais});
 localStorage.setItem('wf_busca',JSON.stringify({mb:MB,musica:pk(ST.musica),playlist:pk(ST.playlist),plv:PLV}))}catch(e){}}
function buscaLoad(){try{if(SELM.size){const d=JSON.parse(localStorage.getItem('wf_busca')||'null');
  if(d){['musica','playlist'].forEach(k=>{if(d[k])Object.assign(ST[k],mkS(),d[k])});MB=d.mb==='playlist'?'playlist':'musica';PLV=d.plv||null;segset('segs',MB);$('#q').value=ST[MB].q;$('#q').placeholder=MB==='musica'?'Nome da música ou artista':'Nome da playlist'}}
 else localStorage.removeItem('wf_busca')}catch(e){}BL=true}
function syncChecks(){$$('#res input[data-id]').forEach(c=>{if(!c.disabled)c.checked=SELM.has(c.dataset.id)});if(PLV&&$('#pn'))$('#pn').textContent=PLV.itens.filter(y=>SELM.has(y.id)).length}
function rtray(){const t=$('#tray');t.hidden=!SELM.size||!TRAY;if(t.hidden)return;
 t.innerHTML=[...SELM.values()].map(x=>`<div class="tr"><span class="th"><img loading="lazy" src="https://i.ytimg.com/vi/${esc(x.id)}/mqdefault.jpg" alt=""><button type="button" class="pp" data-pv="${esc(x.id)}" aria-label="Ouvir prévia">${ic('play',18)}</button></span><div class="bd2"><div class="tt">${esc(x.titulo)}</div><div class="sm mut tt">${esc(x.canal||'')}</div></div><button class="t" data-rm="${esc(x.id)}">${ic('x',14)}</button></div>`).join('')}
function qxv(){$('#qx').hidden=!($('#q').value||ST.musica.q||ST.playlist.q||SELM.size)}
function updsel(){const n=SELM.size;$('#sbar').hidden=!n;let d=0;SELM.forEach(x=>d+=x.dur||0);const e=estB(d);
 $('#sc').textContent=n+(n>1?' selecionadas':' selecionada');$('#se').textContent=e?`Estimativa: ~${tamf(e)}`:'';$('#se').hidden=!e;
 const b=$('#nb');b.hidden=!n;b.textContent=n;$('#stray').textContent=TRAY?'Ocultar':'Ver lista';if(!n)TRAY=false;rtray();qxv();buscaSave()}
function songRow(x){INFO.set(x.id,x);const j=!!x.ja;return `<label class="rs${j?' off':''}"><input type="checkbox" data-id="${esc(x.id)}" ${SELM.has(x.id)&&!j?'checked':''} ${j?'disabled':''}><span class="th"><img loading="lazy" src="https://i.ytimg.com/vi/${esc(x.id)}/mqdefault.jpg" alt=""><button type="button" class="pp" data-pv="${esc(x.id)}" aria-label="Ouvir prévia">${ic('play',18)}</button></span><div class="bd2"><div class="tt">${esc(x.titulo)}</div>${j?'<div class="ja tt">Já existe na pasta</div>':`<div class="sm mut tt">${esc(x.canal||'')}${x.canal&&x.dur?' · ':''}${x.dur?durf(x.dur):''} ${x.views?' · '+x.views+' views':''} ${x.tamanho?'· '+x.tamanho:''}</div>`}</div></label>`}
function plCard(x){return `<div class="pc"><div class="th">${x.thumb?`<img loading="lazy" src="${esc(x.thumb)}" alt="">`:''}</div><div class="bd2"><div class="tt">${esc(x.titulo)}</div><div class="sm mut tt">${esc(x.canal||'')}${x.n?(x.canal?' · ':'')+x.n+' itens':''}</div></div><button class="t" data-open="${esc(x.id)}">Abrir</button><button class="t" data-dl="${esc(x.id)}">Baixar</button></div>`}
function rdet(){const v=PLV,n=v.itens.filter(x=>SELM.has(x.id)).length;
 $('#res').innerHTML=`<button class="t" id="bvolta" style="margin:2px -6px 6px">‹ Voltar</button><h2>${esc(v.titulo)}</h2><div class="sm mut">${esc(v.canal||'')}${v.canal?' · ':''}${v.itens.length} itens · <span id="pn">${n}</span> selecionadas</div>`+
 (v.itens.length?`<div class="row" style="margin:8px 0 2px"><span></span><span><button class="t" id="pall">Selecionar todas</button><button class="t" id="pnone">Desmarcar todas</button></span></div>`+v.itens.slice(0,v.vis).map(songRow).join('')+(v.vis<v.itens.length?'<button class="more" id="pmore">Mostrar mais</button>':''):'<p class="mut" style="margin-top:14px">Playlist vazia.</p>')}
function _rres(){const box=$('#res');if(PLV&&MB==='playlist')return rdet();const s=ST[MB];
 if(!s.q){box.innerHTML=`<div class="empty">${WAVE}<p>${MB==='musica'?'Pesquise por música ou artista.':'Pesquise por playlist.'}</p></div>`;return}
 if(s.busy&&!s.itens.length){box.innerHTML='<p class="mut">Pesquisando...</p>';return}
 if(s.erro&&!s.itens.length){box.innerHTML=`<p class="er">${esc(s.erro)}</p>`;return}
 if(!s.itens.length){box.innerHTML='<p class="mut">Nenhum resultado.</p>';return}
 const vis=s.itens.slice(0,s.vis);
 let h=MB==='musica'?`<div class="row" style="margin:2px 0"><span class="sm mut">${vis.length} resultados</span><span><button class="t" id="bsall">Selecionar visíveis</button><button class="t" id="bdall">Baixar visíveis</button></span></div>`+vis.map(songRow).join(''):vis.map(plCard).join('');
 if(s.erro)h+=`<p class="er sm">${esc(s.erro)}</p>`;
 const espera=s.vis>s.itens.length&&s.busy;
 if(s.vis<s.itens.length||s.mais)h+=`<button class="more" id="bmore" ${espera?'disabled':''}>${espera?'Carregando...':'Mostrar mais'}</button>`;
 box.innerHTML=h}
function rres(){_rres();buscaSave()}
async function pedir(tipo,s,n){const q=s.q;const d=await api(`/api/buscar?tipo=${tipo}&q=${encodeURIComponent(q)}&inicio=${s.itens.length}&n=${n}`);if(s.q!==q)return;
 const ids=new Set(s.itens.map(x=>x.id));d.itens.forEach(x=>{if(!ids.has(x.id)){ids.add(x.id);s.itens.push(x)}});s.mais=!!d.mais&&d.itens.length>0;s.erro=''}
async function prefetch(tipo){const s=ST[tipo];while(!s.busy&&s.mais&&s.itens.length<s.vis+10){s.busy=true;let falhou=false;try{await pedir(tipo,s,10)}catch(e){s.erro=e.message;falhou=true}s.busy=false;if(MB===tipo)rres();if(falhou)break}}
async function buscar(){const q=$('#q').value.trim();if(q.length<3)return toast('Digite pelo menos 3 letras');const tipo=MB,s=ST[tipo];PLV=null;Object.assign(s,mkS(),{q,busy:true});qxv();rres();
 try{await pedir(tipo,s,30)}catch(e){s.erro=e.message}s.busy=false;if(MB===tipo)rres();prefetch(tipo)}
function limparBusca(){$('#q').value='';Object.assign(ST.musica,mkS());Object.assign(ST.playlist,mkS());PLV=null;SELM.clear();selSave();TRAY=false;api('/api/limparbusca',{}).catch(()=>{});const o=$('.pv');if(o)o.remove();updsel();rres();$('#q').focus()}
async function abrir(id){const p=ST.playlist.itens.find(x=>x.id===id);$('#res').innerHTML='<p class="mut">Abrindo playlist...</p>';
 try{const d=await api('/api/playlist?id='+encodeURIComponent(id));PLV={id,titulo:d.titulo||(p&&p.titulo)||'Playlist',canal:d.canal||(p&&p.canal)||'',itens:d.itens,vis:30}}catch(e){toast(e.message);PLV=null}rres()}
function msgAdd(r){let m=r.add?`${r.add} adicionado${r.add>1?'s':''} à fila`:'Nada novo para baixar';if(r.rep)m+=` · ${r.rep} já ${r.rep>1?'estão':'está'} na fila`;if(r.ja)m+=` · ${r.ja} já ${r.ja>1?'existem':'existe'} na pasta`;return m}
async function baixarIds(ids,limpa){if(!ids.length)return toast('Itens já existentes foram ignorados.');
 try{const r=await api('/api/add',{texto:ids.map(i=>'https://www.youtube.com/watch?v='+i).join('\n')});toast(msgAdd(r));
  if(limpa){SELM.clear();selSave()}updsel();rres();tick()}catch(e){toast(e.message)}}
$('#bq').onclick=buscar;$('#q').onkeydown=e=>{if(e.key==='Enter')buscar()};$('#q').oninput=qxv;$('#qx').onclick=limparBusca;
$$('#segs button').forEach(b=>b.onclick=()=>{MB=b.dataset.v;segset('segs',MB);$('#q').value=ST[MB].q;$('#q').placeholder=MB==='musica'?'Nome da música ou artista':'Nome da playlist';qxv();rres()});
$('#res').onchange=e=>{const c=e.target.closest('input[data-id]');if(!c||c.disabled)return;const x=INFO.get(c.dataset.id);if(!x)return;c.checked?SELM.set(x.id,meta(x)):SELM.delete(x.id);selSave();updsel();syncChecks()};
$('#res').onclick=async e=>{const t=e.target,id=t.id;
 if(id==='bmore'){const s=ST[MB];s.vis+=10;rres();prefetch(MB);return}
 if(id==='pmore'){PLV.vis+=10;return rdet()}
 if(id==='bvolta'){PLV=null;return rres()}
 if(id==='pall'){PLV.itens.forEach(x=>{if(x.ja)return;INFO.set(x.id,x);SELM.set(x.id,meta(x))});selSave();updsel();return rdet()}
 if(id==='pnone'){PLV.itens.forEach(x=>SELM.delete(x.id));selSave();updsel();return rdet()}
 if(id==='bsall'){const s=ST.musica;s.itens.slice(0,s.vis).forEach(x=>{if(x.ja)return;INFO.set(x.id,x);SELM.set(x.id,meta(x))});selSave();updsel();return rres()}
 if(id==='bdall'){const s=ST.musica;return baixarIds(s.itens.slice(0,s.vis).filter(x=>!x.ja).map(x=>x.id),false)}
 const o=t.closest('[data-open]');if(o)return abrir(o.dataset.open);
 const d=t.closest('[data-dl]');if(d){try{const r=await api('/api/add',{texto:'https://www.youtube.com/playlist?list='+d.dataset.dl});toast(msgAdd(r));tick()}catch(x){toast(x.message)}}};
$('#scl').onclick=async()=>{if(SELM.size>3&&!await conf(`Remover as <b>${SELM.size}</b> músicas da seleção?`,'Limpar'))return;SELM.clear();selSave();updsel();syncChecks()};
$('#sgo').onclick=()=>baixarIds([...SELM.keys()],true);
$('#stray').onclick=()=>{TRAY=!TRAY;updsel()};
$('#tray').onclick=e=>{const r=e.target.closest('[data-rm]');if(!r)return;SELM.delete(r.dataset.rm);selSave();updsel();syncChecks()};

document.addEventListener('click',e=>{const b=e.target.closest('[data-pv]');if(!b)return;e.preventDefault();e.stopPropagation();
 const id=b.dataset.pv,old=$('.pv'),same=old&&old.dataset.id===id;if(old)old.remove();$$('.pp').forEach(x=>x.innerHTML=ic('play',18));if(same)return;
 const row=b.closest('.rs,.tr');
 row.insertAdjacentHTML('afterend',`<div class="pv" data-id="${esc(id)}"><iframe src="https://www.youtube-nocookie.com/embed/${esc(id)}?autoplay=1&playsinline=1&rel=0" allow="autoplay; encrypted-media; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>`);b.innerHTML=ic('stop',18)},true);

if(SELM.size){TRAY=true;setTimeout(()=>toast(`${SELM.size} músicas mantidas na seleção.`),500)}
buscaLoad();updsel();rres();loadCfg();tick();




</script>
<style>/* FORCA-FINAL - vai por ultimo, ganha de tudo */
body .tabs a.on{color:#ffb840!important;text-shadow:0 2px 0 #000,0 3px 4px #000!important;box-shadow:inset 0 4px 8px rgba(0,0,0,.6),0 4px 0 #000!important}
.sg button,.sg a{box-shadow:0 4px 0 #000,0 6px 10px rgba(0,0,0,.35),inset 0 2px 0 #fff!important;border:2px solid #6b5a35!important}
.sg button.on{background:#1a1005!important;color:#ffb840!important}
/* COLAR E LIMPAR - nao brancos, bege 3D */
#bpaste,#bclr,button#bpaste,button#bclr{background:linear-gradient(180deg,#e8ddc2,#c8b888)!important;color:#3b2314!important;border:2px solid #6b5a35!important;border-radius:14px!important;box-shadow:0 4px 0 #6b5a35,0 6px 10px rgba(0,0,0,.3),inset 0 2px 0 #fff!important;text-shadow:0 1px 0 #fff!important}
#fbar button,#brep{background:linear-gradient(180deg,#e8ddc2,#c8b888)!important;color:#3b2314!important;border:2px solid #6b5a35!important;box-shadow:0 4px 0 #6b5a35,0 6px 10px rgba(0,0,0,.3),inset 0 2px 0 #fff!important}
/* BARRA MARCADA - forca bege */
.sel,.sbar,#selbar,div[class*="sel"]{background:linear-gradient(180deg,#fff8e6,#e8ddc2)!important;color:#3b2314!important;border:3px solid #6b5a35!important;box-shadow:0 6px 0 #6b5a35,0 12px 20px rgba(0,0,0,.4)!important}
.sel *, .sbar *, #selbar *{color:#3b2314!important}
/* LOGO - sem quadrado */
.mk,header .mk{background:none!important;border:none!important;box-shadow:none!important;padding:0!important}
.mk svg{filter:drop-shadow(0 3px 3px rgba(0,0,0,.35))!important}
@media (prefers-color-scheme: dark){
  #bpaste,#bclr,#fbar button,#brep{background:linear-gradient(180deg,#5a4630,#2e2318)!important;color:#fff7e0!important;border:2px solid #d4a94e!important;box-shadow:0 4px 0 #000,0 6px 10px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.2)!important;text-shadow:0 1px 2px #000!important}
  .sel,.sbar,#selbar{background:linear-gradient(180deg,#5a4630,#2e2318)!important;color:#fff7e0!important;border:3px solid #d4a94e!important}
  .sel *, .sbar *, #selbar *{color:#fff7e0!important}
}
</style>

<style>/* FORCA-2-BUSCAR - barra marcada bonita + Buscar 3D de verdade */
/* BARRA 1 MARCADA - marrom escuro + dourado, nos 2 modos */
.sel,.sbar,#selbar,div[class*="sel"],div[id*="sel"]{background:linear-gradient(180deg,#3a2a12,#1a1005)!important;color:#ffb840!important;border:3px solid #ffb840!important;border-radius:18px!important;box-shadow:0 6px 0 #000,0 12px 20px rgba(0,0,0,.5),inset 0 2px 0 rgba(255,255,255,.25)!important;padding:10px 14px!important}
.sel *, .sbar *, #selbar *{color:#f3e6cc!important;text-shadow:0 1px 2px #000!important}
.sel b,.sbar b,#selbar b,.sel .cb,.sbar .cb{color:#ffb840!important;font-weight:900!important}
.sel button,.sbar button,#selbar button{background:linear-gradient(180deg,#ffb840,#c99a3a)!important;color:#241a0e!important;border:2px solid #ffb840!important;border-radius:12px!important;box-shadow:0 3px 0 #6b4d1a,0 5px 8px rgba(0,0,0,.4),inset 0 1px 0 #fff!important;font-weight:900!important;text-shadow:0 1px 0 #fff!important}
.sel button:active,.sbar button:active{transform:translateY(2px)!important;box-shadow:0 1px 0 #6b4d1a!important}
/* BUSCAR - aba + botao, 3D forte */
body .tabs a[href*="buscar"],body .tabs a[data-tab="buscar"],body .tabs a[data-t="buscar"],body .tabs a:nth-child(2){box-shadow:0 4px 0 #6b5a35,0 6px 10px rgba(0,0,0,.35),inset 0 2px 0 #fff,inset 0 -3px 5px rgba(0,0,0,.15)!important;border:2px solid #6b5a35!important}
body .tabs a[href*="buscar"].on,body .tabs a[data-tab="buscar"].on,body .tabs a:nth-child(2).on{background:linear-gradient(180deg,#3a2a12,#0d0803)!important;color:#ffb840!important;border:2px solid #ffb840!important;box-shadow:inset 0 4px 8px rgba(0,0,0,.6),0 4px 0 #000,0 8px 14px rgba(0,0,0,.5)!important;text-shadow:0 2px 0 #000!important}
#bbuscar,#bBuscar,button[id*="buscar"],button[id*="Buscar"],#buscar,.fbf button.p{background:linear-gradient(180deg,#3a2a12,#1a1005)!important;color:#ffb840!important;border:3px solid #000!important;border-radius:16px!important;box-shadow:0 6px 0 #000,0 10px 16px rgba(0,0,0,.45),inset 0 2px 0 rgba(255,255,255,.25)!important;text-shadow:0 2px 0 #000!important}
@media (prefers-color-scheme: dark){
  .sel,.sbar,#selbar{background:linear-gradient(180deg,#3a2a12,#000)!important;border-color:#ffd860!important}
  .sel button,.sbar button{background:linear-gradient(180deg,#ffd860,#c99a3a)!important;color:#241a0e!important}
  body .tabs a[href*="buscar"],body .tabs a:nth-child(2){box-shadow:0 4px 0 #000,0 6px 10px rgba(0,0,0,.6),inset 0 2px 0 rgba(255,255,255,.25)!important;border:2px solid #d4a94e!important}
}
</style>

<style>/* FORCA-3-BUSCAR-EXATO - nome real: data-go=nome e #bq, mesma cor, so 3D */
.tabs a[data-go="nome"]{box-shadow:0 4px 0 #6b5a35,0 6px 10px rgba(0,0,0,.35),inset 0 2px 0 #fff,inset 0 -3px 5px rgba(0,0,0,.15)!important;border:2px solid #6b5a35!important}
.tabs a[data-go="nome"].on{box-shadow:inset 0 4px 8px rgba(0,0,0,.6),inset 0 -1px 0 rgba(255,255,255,.2),0 4px 0 #000,0 8px 14px rgba(0,0,0,.5)!important;transform:translateY(1px)!important}
.srch{box-shadow:0 4px 0 rgba(0,0,0,.25),0 8px 12px rgba(0,0,0,.25),inset 0 1px 0 rgba(255,255,255,.6)!important;border-radius:16px!important}
#bq{box-shadow:0 5px 0 #000,0 8px 12px rgba(0,0,0,.4),inset 0 2px 0 rgba(255,255,255,.3),inset 0 -3px 5px rgba(0,0,0,.3)!important;border:2px solid #000!important}
#bq:active{transform:translateY(3px)!important;box-shadow:0 1px 0 #000,0 2px 4px rgba(0,0,0,.4),inset 0 3px 6px rgba(0,0,0,.4)!important}
@media (prefers-color-scheme: dark){
  .tabs a[data-go="nome"]{box-shadow:0 4px 0 #000,0 6px 10px rgba(0,0,0,.6),inset 0 2px 0 rgba(255,255,255,.25)!important;border:2px solid #d4a94e!important}
  #bq{box-shadow:0 5px 0 #000,0 8px 12px rgba(0,0,0,.6),inset 0 2px 0 rgba(255,255,255,.25)!important}
}
</style>

<style>/* CORRIGE-SOMBRA-BAIXO - sombra so embaixo, sem espalhar pros lados */
.tabs a[data-go="nome"]{box-shadow:0 4px 0 #6b5a35,inset 0 2px 0 #fff!important}
.tabs a[data-go="nome"].on{box-shadow:inset 0 3px 6px rgba(0,0,0,.55),0 3px 0 #000!important;transform:translateY(1px)!important}
.srch{box-shadow:0 4px 0 rgba(0,0,0,.25),inset 0 1px 0 rgba(255,255,255,.6)!important}
#bq{box-shadow:0 5px 0 #000,inset 0 2px 0 rgba(255,255,255,.3)!important}
#bq:active{transform:translateY(3px)!important;box-shadow:0 1px 0 #000,inset 0 3px 6px rgba(0,0,0,.4)!important}
@media (prefers-color-scheme: dark){
  .tabs a[data-go="nome"]{box-shadow:0 4px 0 #000,inset 0 2px 0 rgba(255,255,255,.25)!important}
  #bq{box-shadow:0 5px 0 #000,inset 0 2px 0 rgba(255,255,255,.25)!important}
}
</style>

<style>/* TIRA-3D-BUSCAR - volta como tava antes, sem 3D no Buscar */
.tabs a[data-go="nome"]{box-shadow:none!important;transform:none!important;border:none!important}
.tabs a[data-go="nome"].on{box-shadow:none!important;transform:none!important}
#bq{box-shadow:none!important;transform:none!important;border:none!important}
#bq:active{transform:none!important;box-shadow:none!important}
.srch{box-shadow:none!important}
</style>

<style>/* APAGAR-IGUAL-CANCELAR - Apagar igual ao Cancelar, mesma cor */
#mn,#my,#bdel,#brdel,#bdel2{box-shadow:0 4px 0 #a8936a,0 6px 10px rgba(0,0,0,.2),inset 0 2px 0 #fff!important;background:linear-gradient(180deg,#fff8e6,#d9cda9)!important;color:#5a4a2c!important;border:2px solid #a8936a!important;border-radius:14px!important;text-shadow:0 1px 0 #fff!important}
#mn:active,#my:active,#bdel:active,#brdel:active{transform:translateY(2px)!important;box-shadow:0 1px 0 #a8936a!important}
@media (prefers-color-scheme: dark){
  #mn,#my,#bdel,#brdel{background:linear-gradient(180deg,#6b5636,#3a2c1e)!important;color:#fff2cc!important;border:2px solid #d4a94e!important;box-shadow:0 4px 0 #000,inset 0 2px 0 rgba(255,255,255,.25)!important;text-shadow:0 1px 2px #000!important}
}
</style>

<style>/* APAGAR-MESMO-TAMANHO - Cancelar e Apagar mesmo tamanho */
#md .row{display:flex!important;gap:8px!important}
#md .row button,#mn,#my{flex:1!important;min-width:0!important;width:auto!important;min-height:44px!important;padding:10px 12px!important;font-size:14px!important;font-weight:700!important;line-height:1.2!important;border-radius:14px!important;box-sizing:border-box!important}
</style>

<style>/* SBAR-BONITA - barra de cima da pesquisa bonita */
#sbar{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:8px!important;background:linear-gradient(180deg,#fff8e6,#e8ddc2)!important;color:#3b2314!important;border:2px solid #6b5a35!important;border-radius:18px!important;padding:8px 10px!important;box-shadow:0 4px 0 #6b5a35,0 8px 14px rgba(0,0,0,.25),inset 0 2px 0 #fff!important}
#sbar>span:first-child{display:flex!important;flex-direction:column!important;line-height:1.2!important;color:#3b2314!important;font-weight:700!important}
#sbar>span:last-child{display:flex!important;gap:6px!important;align-items:center!important}
#sbar button,#stray,#scl,#sgo{flex:0 0 auto!important;min-height:38px!important;padding:8px 12px!important;font-size:13px!important;font-weight:700!important;border-radius:12px!important;line-height:1.2!important;box-sizing:border-box!important}
#stray,#scl{background:linear-gradient(180deg,#fff8e6,#d9cda9)!important;color:#5a4a2c!important;border:2px solid #a8936a!important;box-shadow:0 3px 0 #a8936a,inset 0 2px 0 #fff!important;text-shadow:0 1px 0 #fff!important}
#sgo{background:linear-gradient(180deg,#3a2a12,#1a1005)!important;color:#ffb840!important;border:2px solid #000!important;box-shadow:0 3px 0 #000,inset 0 2px 0 rgba(255,255,255,.25)!important;text-shadow:0 1px 2px #000!important}
#sbar button:active{transform:translateY(2px)!important;box-shadow:0 1px 0 #a8936a!important}
@media (prefers-color-scheme: dark){
  #sbar{background:linear-gradient(180deg,#4a3a28,#2e2318)!important;color:#fff2cc!important;border:2px solid #d4a94e!important;box-shadow:0 4px 0 #000,inset 0 1px 0 rgba(255,255,255,.2)!important}
  #sbar>span:first-child{color:#fff2cc!important}
  #stray,#scl{background:linear-gradient(180deg,#6b5636,#3a2c1e)!important;color:#fff2cc!important;border:2px solid #d4a94e!important;box-shadow:0 3px 0 #000!important;text-shadow:0 1px 2px #000!important}
}
</style>

<style>/* SBAR-ESCONDE-0 - esconde barra quando 0 selecionada */
#sbar[hidden]{display:none!important}
#sbar:not([hidden]){display:flex!important}
</style>

<style>/* ABAS-LETRAS-VISIVEIS - letras das abas bem visiveis */
.tabs a{color:#3b2314!important;opacity:1!important}
.tabs a span,.tabs a small,.tabs a b{color:#3b2314!important;opacity:1!important;font-size:13px!important;font-weight:800!important;letter-spacing:.2px!important;text-shadow:0 1px 0 rgba(255,255,255,.9)!important}
.tabs a svg{color:#3b2314!important;opacity:1!important}
.tabs a.on{color:#fff!important;background:#3a2a12!important}
.tabs a.on span,.tabs a.on small,.tabs a.on b{color:#ffb840!important;text-shadow:0 1px 2px #000!important}
.tabs a.on svg{color:#ffb840!important}
@media (prefers-color-scheme: dark){
  .tabs a{color:#fff2cc!important}
  .tabs a span,.tabs a small,.tabs a b{color:#fff2cc!important;text-shadow:0 1px 2px #000!important}
  .tabs a svg{color:#fff2cc!important}
  .tabs a.on span,.tabs a.on small,.tabs a.on b{color:#ffb840!important}
}
</style>

<style>/* ABAS-MEIO-TERMO - nem branca forte, nem apagada */
.tabs a{color:#d9cba8!important;opacity:1!important}
.tabs a span,.tabs a small,.tabs a b{color:#d9cba8!important;opacity:1!important;font-size:13px!important;font-weight:700!important;letter-spacing:.2px!important;text-shadow:none!important}
.tabs a svg{color:#d9cba8!important;opacity:.9!important}
.tabs a.on{color:#ffe9b0!important;background:#3a2a12!important}
.tabs a.on span,.tabs a.on small,.tabs a.on b{color:#ffe9b0!important;font-weight:800!important;text-shadow:none!important}
.tabs a.on svg{color:#ffe9b0!important;opacity:1!important}
@media (prefers-color-scheme: dark){
  .tabs a,.tabs a span,.tabs a small,.tabs a b,.tabs a svg{color:#d9cba8!important}
  .tabs a.on,.tabs a.on span,.tabs a.on small,.tabs a.on b,.tabs a.on svg{color:#ffe9b0!important}
}
</style>

<style>/* ABAS-NAO-SEL-CERTO - texto da aba nao selecionada, meio termo */
body .tabs a:not(.on){color:#6b5a35!important;text-shadow:none!important;opacity:1!important}
body .tabs a:not(.on) svg, body .tabs a:not(.on) span{color:#6b5a35!important;opacity:.85!important;text-shadow:none!important}
body .tabs a.on{color:#ffb840!important;text-shadow:none!important}
@media (prefers-color-scheme: dark){
  body .tabs a:not(.on){color:#c8b88a!important;text-shadow:none!important}
  body .tabs a:not(.on) svg, body .tabs a:not(.on) span{color:#c8b88a!important;opacity:.9!important}
  body .tabs a.on{color:#ffb840!important}
}
</style>


<style>#moldura{display:none!important}#bvol,#vrow{display:none!important}
html,body{touch-action:pan-x pan-y}/* MOLDURA-CIRCULA - barra laranja/amarela circulando por toda periferia */
#moldura{position:fixed!important;inset:0!important;z-index:9999!important;pointer-events:none!important;padding:3px!important;background:linear-gradient(90deg,#ff7a00,#ffd860,#ff8c00,#ffe9b0,#ff7a00)!important;background-size:300% 100%!important;animation:circula-moldura 4s linear infinite!important;-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0)!important;-webkit-mask-composite:xor!important;mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0)!important;mask-composite:exclude!important}
@keyframes circula-moldura{0%{background-position:0% 0}100%{background-position:300% 0}}
body::before,body::after{border-top:none!important}
</style>












<style>/* ONDA-SONORA-LARGA */
#eq{display:none;align-items:flex-end;gap:2px;height:22px;margin-right:8px;vertical-align:0}
#eq.on{display:inline-flex}
#eq i{display:block;width:3px;background:#d8b96a;border-radius:2px;height:6px;opacity:.9}
#eq.on i{animation:onda-larga 2.8s ease-in-out infinite}
#eq.on i:nth-child(1){animation-delay:0s}
#eq.on i:nth-child(2){animation-delay:.2s}
#eq.on i:nth-child(3){animation-delay:.4s}
#eq.on i:nth-child(4){animation-delay:.6s}
#eq.on i:nth-child(5){animation-delay:.8s}
#eq.on i:nth-child(6){animation-delay:1s}
#eq.on i:nth-child(7){animation-delay:1.2s}
#eq.on i:nth-child(8){animation-delay:1s}
#eq.on i:nth-child(9){animation-delay:.8s}
#eq.on i:nth-child(10){animation-delay:.6s}
#eq.on i:nth-child(11){animation-delay:.4s}
#eq.on i:nth-child(12){animation-delay:.2s}
#eq.on i:nth-child(13){animation-delay:0s}
#eq.on i:nth-child(14){animation-delay:.2s}
@keyframes onda-larga{0%,100%{height:5px}50%{height:20px}}
</style>

<style>/* SEM LISTRA - BARRA SOLIDA */
.bar i{animation:none!important;background:linear-gradient(90deg,var(--ac),var(--ac2))!important;background-size:auto!important}
#fbar.done{animation:none!important;background:linear-gradient(90deg,#d8b96a,#a8936a)!important;box-shadow:0 0 8px rgba(216,185,106,.5)}
</style>



<script>/* TRAVA NOME DO PREVIEW */
window.__TIT=window.__TIT||{};
try{Object.assign(window.__TIT, JSON.parse(localStorage.getItem('wf_tit')||'{}'))}catch(e){}
function salvaTit(){
  // procura no preview qualquer linha que tenha link + titulo
  document.querySelectorAll('a[href*="youtube"],a[href*="youtu.be"]').forEach(a=>{
    const url=a.href;
    const box=a.closest('div,li,p')||a.parentElement;
    const t=(box?box.textContent:'').trim();
    // titulo é o texto da linha sem o link
    const titulo=t.replace(url,'').replace(a.textContent,'').trim() || a.textContent.trim();
    if(url && titulo && titulo.length>2 && !titulo.includes('http')){window.__TIT[url]=titulo}
  });
  // tambem pega do LST se ele ja tiver titulo
  try{(window.LST||[]).forEach(x=>{if(x.url&&x.titulo)window.__TIT[x.url]=x.titulo; if(x.url&&x.nome)window.__TIT[x.url]=x.nome})}catch(e){}
  try{localStorage.setItem('wf_tit', JSON.stringify(window.__TIT))}catch(e){}
}
setInterval(salvaTit, 800);
document.addEventListener('input', ()=>setTimeout(salvaTit, 600));
</script>
<style>/* TEMA-WAVEFLY-FINAL - visual novo: cores unificadas e botões 3D médios (só aparência) */
:root{--t-bg:#f4e9d3;--t-s1:#fffaf0;--t-s2:#f0e2c6;--t-ln:#dcc9a3;--t-tx:#34200f;--t-mu:#8b7155;
--t-ac1:#ff9d45;--t-ac2:#e46f22;--t-acd:#a84a12;--t-on:#2b1304;--t-bt1:#fffdf6;--t-bt2:#eadbbb;--t-btd:#bfa57a;--t-bg-ink:#34200f}
@media(prefers-color-scheme:dark){:root{--t-bg:#17110d;--t-s1:#241b14;--t-s2:#2f231a;--t-ln:#43332a;--t-tx:#f6ead3;--t-mu:#b9a58b;
--t-ac1:#ffa94f;--t-ac2:#e9742a;--t-acd:#8f3d0d;--t-on:#2b1304;--t-bt1:#4a392c;--t-bt2:#33271d;--t-btd:#120c08;--t-bg-ink:#f6ead3}}
html body{background:var(--t-bg)!important;color:var(--t-tx)!important}
html body h1,html body h2,html body h3,html body .wm,html body .wm i{text-shadow:none!important}
html body .wm i{color:var(--t-ac2)!important}
html body .mut,html body .sm,html body .sub,html body p.mut{color:var(--t-mu)!important}

/* cartões e listas: borda fina e sombra suave */
html body .lr,html body .pc,html body .pl-card,html body .rs,html body .tr,html body .chip,html body .plc,html body .deliver,html body #tray,html body .rb,html body .hello,html body .card,html body .cd{
 background:linear-gradient(180deg,var(--t-s1),var(--t-s2))!important;border:1px solid var(--t-ln)!important;
 box-shadow:0 1px 0 rgba(255,255,255,.06) inset,0 3px 10px rgba(0,0,0,.22)!important;color:var(--t-tx)!important}
html body .hello{border-style:dashed!important}

/* campos */
html body textarea,html body input[type=text],html body input[type=number],html body input[type=search],html body select{
 background:var(--t-s1)!important;color:var(--t-tx)!important;border:1px solid var(--t-ln)!important;border-radius:14px!important;
 box-shadow:inset 0 2px 5px rgba(0,0,0,.25)!important}
html body textarea:focus,html body input[type=text]:focus,html body input[type=number]:focus,html body input[type=search]:focus{
 border-color:var(--t-ac1)!important;box-shadow:inset 0 2px 5px rgba(0,0,0,.25),0 0 0 3px rgba(255,157,69,.22)!important;outline:none!important}

/* botões 3D médios: gradiente, brilho no topo e borda inferior em relevo */
html body button,html body .sg button,html body .sg a,html body #bpaste,html body #bclr,html body #fbar button,html body #brep,html body .sbar button,html body .sel button,html body #fbl button,html body .srch>button{
 background:linear-gradient(180deg,var(--t-bt1),var(--t-bt2))!important;color:var(--t-tx)!important;
 border:1px solid rgba(255,255,255,.10)!important;text-shadow:none!important;
 box-shadow:inset 0 1px 0 rgba(255,255,255,.22),0 3px 0 var(--t-btd),0 6px 9px rgba(0,0,0,.28)!important;
 transition:transform .08s ease,box-shadow .08s ease!important}
html body button:active,html body .sg button:active,html body .sg a:active,html body .tabs a:active{
 transform:translateY(2px)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 1px 0 var(--t-btd),0 2px 4px rgba(0,0,0,.25)!important}
html body button.t,html body button.more{background:transparent!important;box-shadow:none!important;border-color:transparent!important;color:var(--t-ac2)!important}
html body button.t:active{transform:none!important}

/* botão principal e item selecionado: laranja */
html body button.p,html body #bgo,html body .sg button.on,html body .sg a.on,html body .tabs a.on{
 background:linear-gradient(180deg,var(--t-ac1),var(--t-ac2))!important;color:var(--t-on)!important;
 border:1px solid rgba(255,255,255,.28)!important;text-shadow:0 1px 0 rgba(255,255,255,.25)!important;
 box-shadow:inset 0 1px 0 rgba(255,255,255,.45),0 3px 0 var(--t-acd),0 7px 12px rgba(228,111,34,.35)!important}
html body .tabs a.on svg,html body .tabs a.on span{color:var(--t-on)!important}

/* abas */
html body .tabs{background:var(--t-s2)!important;border:1px solid var(--t-ln)!important;box-shadow:inset 0 2px 6px rgba(0,0,0,.28)!important}
html body .tabs a{background:linear-gradient(180deg,var(--t-bt1),var(--t-bt2))!important;color:var(--t-mu)!important;border:1px solid rgba(255,255,255,.08)!important;
 box-shadow:inset 0 1px 0 rgba(255,255,255,.2),0 3px 0 var(--t-btd)!important;text-shadow:none!important}

/* barras de progresso */
html body .bar{background:var(--t-s2)!important;box-shadow:inset 0 1px 3px rgba(0,0,0,.4)!important}
html body .bar i{background:linear-gradient(90deg,var(--t-ac1),var(--t-ac2))!important}

/* player */
html body #pl{background:linear-gradient(180deg,var(--t-s1),var(--t-s2))!important;background-image:linear-gradient(180deg,var(--t-s1),var(--t-s2))!important;border:1px solid var(--t-ln)!important;
 box-shadow:0 10px 28px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.08)!important;color:var(--t-tx)!important}
html body #pl *{color:var(--t-tx)}
html body #bvol,html body #vrow{display:none!important}
html body #moldura{display:none!important}
html,body{-webkit-tap-highlight-color:transparent}
html body::after{display:none!important}
html body .tabs a,html body .tabs a:nth-child(2),html body .tabs a[data-go],html body .tabs a[href*="buscar"]{
 border:1px solid rgba(255,255,255,.10)!important;background:linear-gradient(180deg,var(--t-bt1),var(--t-bt2))!important;color:var(--t-mu)!important;
 box-shadow:inset 0 1px 0 rgba(255,255,255,.2),0 3px 0 var(--t-btd),0 5px 8px rgba(0,0,0,.22)!important;transform:none!important}
html body .tabs a.on,html body .tabs a:nth-child(2).on,html body .tabs a[data-go].on,html body .tabs a[href*="buscar"].on{
 background:linear-gradient(180deg,var(--t-ac1),var(--t-ac2))!important;color:var(--t-on)!important;border:1px solid rgba(255,255,255,.28)!important;
 box-shadow:inset 0 1px 0 rgba(255,255,255,.45),0 3px 0 var(--t-acd),0 7px 12px rgba(228,111,34,.35)!important}
html body .tabs{padding:6px!important}
html body .sg{background:var(--t-s2)!important;border:1px solid var(--t-ln)!important;box-shadow:inset 0 2px 6px rgba(0,0,0,.28)!important}
</style>
</body></html>
'''


def main():
    global LIBERADO, SERVIDOR
    ap = argparse.ArgumentParser(description="WaveFly YT - baixador de músicas do YouTube")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8773)
    ap.add_argument("--servidor", action="store_true")
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    SERVIDOR = a.servidor
    if SERVIDOR and a.host == "127.0.0.1":
        a.host = "0.0.0.0"
    LIBERADO = a.host not in ("127.0.0.1", "localhost")
    carregar_cfg()
    carregar_index()
    restaurar_fila()
    threading.Thread(target=trabalhador, daemon=True).start()
    threading.Thread(target=trabalhador, args=(1,), daemon=True).start()
    if SERVIDOR:
        threading.Thread(target=faxina, daemon=True).start()
    try:
        srv = ThreadingHTTPServer((a.host, a.port), H)
    except OSError as ex:
        sys.exit(f"Não consegui abrir a porta {a.port} ({ex}). Tente: python wavefly_yt.py --port 8800")
    url = f"http://localhost:{a.port}"
    print(f"\n🎵 {APP_NOME} rodando em {url}\n   Pasta atual: {raiz()}\n   (Ctrl+C para parar)\n")
    if not ANDROID and not a.no_browser and not SERVIDOR:
        threading.Timer(1, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        salvar_fila()


if __name__ == "__main__":
    main()
