# -*- coding: utf-8 -*-
"""Ponte entre o app Android (Java) e o servidor WaveFly (Python)."""
import os
import re
import shutil
import stat
import sys
import threading
import time
import traceback
import urllib.request

_thread = None


def start(data_dir, ffmpeg_bin, ffmpeg_lib, port):
    """Sobe o servidor do WaveFly. Devolve "" se deu certo, ou o texto do erro."""
    global _thread
    try:
        if _thread is not None and _thread.is_alive():
            return ""
        os.makedirs(data_dir, exist_ok=True)
        tmp = os.path.join(data_dir, "tmp")
        os.makedirs(tmp, exist_ok=True)
        os.environ["WAVEFLY_DATA"] = data_dir
        os.environ["HOME"] = data_dir
        os.environ["TMPDIR"] = tmp
        if ffmpeg_bin:
            os.environ["WAVEFLY_FFMPEG"] = ffmpeg_bin
            os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ.get("PATH", "")
        if ffmpeg_lib:
            antigo = os.environ.get("LD_LIBRARY_PATH", "")
            os.environ["LD_LIBRARY_PATH"] = ffmpeg_lib + ((os.pathsep + antigo) if antigo else "")
        try:
            import certifi
            os.environ.setdefault("SSL_CERT_FILE", certifi.where())
        except Exception:
            pass

        usar_ytdlp_novo(data_dir)
        sys.argv = ["wavefly", "--no-browser", "--port", str(port)]
        import waveflysite
        try:
            import wavefly_android
            wavefly_android.aplicar(waveflysite)
        except Exception:
            traceback.print_exc()

        _thread = threading.Thread(target=waveflysite.main, name="wavefly-server", daemon=True)
        _thread.start()
        threading.Thread(target=atualizar_ytdlp, args=(data_dir, False), name="wavefly-ytdlp", daemon=True).start()

        url = "http://127.0.0.1:%d/" % port
        for _ in range(120):
            try:
                urllib.request.urlopen(url, timeout=1).read(1)
                return ""
            except Exception:
                if not _thread.is_alive():
                    return "O servidor do WaveFly parou logo ao iniciar."
                time.sleep(0.25)
        return "O servidor do WaveFly demorou demais para responder."
    except BaseException:
        return traceback.format_exc()


def resumo():
    """Texto curto com o estado da fila: 'baixando|na_fila|total|pct|vel|titulo'."""
    try:
        import waveflysite as w
        with w.LOCK:
            itens = list(w.ITENS)
        baixando = [i for i in itens if i.get("status") == "baixando"]
        fila = [i for i in itens if i.get("status") == "fila"]
        feitos = [i for i in itens if i.get("status") in ("ok", "duplicada", "falha", "cancelada")]
        atual = next((i for i in baixando if "convert" not in (i.get("vel") or "")), baixando[0] if baixando else None)
        total = len(baixando) + len(fila) + len(feitos)
        return "%d|%d|%d|%d|%s|%s|%d" % (
            len(baixando), len(fila), total,
            int(atual.get("pct") or 0) if atual else 0,
            (atual.get("vel") or "") if atual else "",
            (atual.get("titulo") or "").replace("|", " ") if atual else "",
            1 if w.PAUSA["on"] else 0)
    except Exception:
        return "0|0|0|0|||0"


def pausar(v):
    """Pausa (ou retoma) a fila de downloads: o que já está baixando termina e o resto espera."""
    try:
        import waveflysite as w
        w.definir_pausa(bool(v))
    except Exception:
        traceback.print_exc()


def cancelar_tudo():
    try:
        import waveflysite as w
        w.acao({"acao": "cancelar_tudo"})
    except Exception:
        pass


def extrair(zip_path, dest, so_somente, nao_sobrescrever):
    """Descompacta um zip respeitando links simbólicos. Devolve um resumo."""
    import zipfile
    dest = os.path.abspath(dest)
    os.makedirs(dest, exist_ok=True)
    arqs = links = pulados = 0
    with zipfile.ZipFile(zip_path) as z:
        for zi in z.infolist():
            nome = zi.filename[2:] if zi.filename.startswith("./") else zi.filename
            if so_somente and not re.fullmatch(r"usr/lib/[^/]+\.so[^/]*", nome):
                continue
            alvo = os.path.abspath(os.path.join(dest, nome))
            if not alvo.startswith(dest + os.sep):
                continue
            if zi.is_dir():
                os.makedirs(alvo, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(alvo), exist_ok=True)
            if nao_sobrescrever and os.path.lexists(alvo):
                pulados += 1
                continue
            modo = (zi.external_attr >> 16) & 0xFFFF
            if os.path.lexists(alvo):
                os.remove(alvo)
            if stat.S_ISLNK(modo):
                destino = z.read(zi).decode("utf-8", "ignore").strip()
                if not destino or os.path.basename(destino) == os.path.basename(alvo):
                    pulados += 1
                    continue
                os.symlink(destino, alvo)
                links += 1
            else:
                with z.open(zi) as src, open(alvo, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                os.chmod(alvo, 0o755)
                arqs += 1
    return "%d arquivos, %d links, %d pulados" % (arqs, links, pulados)


def verificar(raiz):
    """Lista bibliotecas suspeitas: arquivos minúsculos ou links quebrados."""
    ruins = []
    for pasta, _, nomes in os.walk(raiz):
        for n in nomes:
            if ".so" not in n:
                continue
            c = os.path.join(pasta, n)
            if os.path.islink(c) and not os.path.exists(c):
                ruins.append(n + "(link quebrado)")
            elif os.path.isfile(c) and os.path.getsize(c) < 1000:
                ruins.append("%s(%d bytes)" % (n, os.path.getsize(c)))
    return ", ".join(ruins[:12])


def stream_url(vid):
    """Endereço direto do áudio de um vídeo, para a prévia da busca."""
    try:
        import yt_dlp
        import waveflysite as w
        opts = {k: v for k, v in w.OPTS.items() if k not in ("outtmpl", "windowsfilenames")}
        opts.update({
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "skip_download": True, "noplaylist": True, "quiet": True, "no_warnings": True,
        })
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info("https://www.youtube.com/watch?v=" + vid, download=False)
        url = info.get("url") or ""
        if not url:
            for f in reversed(info.get("formats") or []):
                if f.get("url") and f.get("acodec") not in (None, "none"):
                    url = f["url"]
                    break
        return url or "ERRO:Não achei o áudio deste vídeo para a prévia."
    except BaseException as e:
        return "ERRO:" + str(e)[:200]


# --------------------------------------------------------------------------- yt-dlp sempre em dia
def _ver(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "")[:4])


def _pasta_ytdlp(data_dir):
    return os.path.join(data_dir, "ytdlp")


def _versao_embutida():
    try:
        from importlib.metadata import version
        return version("yt-dlp")
    except Exception:
        return ""


def usar_ytdlp_novo(data_dir):
    """Se já baixamos um yt-dlp mais novo que o do app, usa ele (precisa rodar antes de importar o motor)."""
    try:
        pasta = _pasta_ytdlp(data_dir)
        whls = sorted(f for f in os.listdir(pasta) if f.endswith(".whl")) if os.path.isdir(pasta) else []
        if not whls:
            return
        whl = os.path.join(pasta, whls[-1])
        v = re.search(r"yt_dlp-([\d.]+)-", whls[-1])
        emb = _versao_embutida()
        if v and emb and _ver(v.group(1)) <= _ver(emb):
            return
        sys.path.insert(0, whl)
        try:
            import yt_dlp.version  # noqa: F401
        except Exception:
            sys.path.remove(whl)
            for k in [k for k in sys.modules if k == "yt_dlp" or k.startswith("yt_dlp.")]:
                del sys.modules[k]
    except Exception:
        traceback.print_exc()


def versao_ytdlp():
    try:
        import yt_dlp.version as v
        return v.__version__
    except Exception:
        return ""


def atualizar_ytdlp(data_dir, forcar):
    """Confere o PyPI; se houver yt-dlp novo, baixa para ser usado na próxima abertura. Devolve um texto curto."""
    import hashlib
    import json
    try:
        marca = os.path.join(_pasta_ytdlp(data_dir), "ultima.txt")
        if not forcar:
            try:
                if time.time() - float(open(marca).read()) < 20 * 3600:
                    return "recente"
            except Exception:
                pass
        req = urllib.request.Request("https://pypi.org/pypi/yt-dlp/json", headers={"User-Agent": "WaveFly"})
        info = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
        nova = info["info"]["version"]
        atual = max(versao_ytdlp(), _versao_embutida(), key=_ver)
        os.makedirs(_pasta_ytdlp(data_dir), exist_ok=True)
        open(marca, "w").write(str(time.time()))
        if _ver(nova) <= _ver(atual):
            return "em_dia:" + atual
        arq = next(u for u in info["urls"] if u["packagetype"] == "bdist_wheel")
        destino = os.path.join(_pasta_ytdlp(data_dir), arq["filename"])
        tmp = destino + ".baixando"
        dados = urllib.request.urlopen(urllib.request.Request(arq["url"], headers={"User-Agent": "WaveFly"}), timeout=60).read()
        if hashlib.sha256(dados).hexdigest() != arq["digests"]["sha256"]:
            return "erro:checksum"
        with open(tmp, "wb") as f:
            f.write(dados)
        os.replace(tmp, destino)
        for f in os.listdir(_pasta_ytdlp(data_dir)):
            if f.endswith(".whl") and f != arq["filename"]:
                try:
                    os.remove(os.path.join(_pasta_ytdlp(data_dir), f))
                except OSError:
                    pass
        return "baixada:" + nova
    except BaseException as e:
        return "erro:" + str(e)[:100]


# --------------------------------------------------------------------------- botão flutuante / compartilhar
def baixar_link(texto, fmt):
    """Põe um link na fila. fmt: 'mp3', 'original', 'video' (vazio = o formato das configurações).
    Devolve 'ok', 'ja', 'nenhum' ou 'erro'."""
    try:
        import waveflysite as w
        links, _rep, _fora = w.extrair_links(texto or "")
        if not links:
            return "nenhum"
        url = links[0]
        m = w.ID_RE.search(url)
        if m and not re.search(r"/playlist", url):
            url = "https://www.youtube.com/watch?v=" + m.group(1)
        with w.LOCK:
            antigo = w.CFG["formato"]
            if fmt in ("mp3", "original", "video"):
                w.CFG["formato"] = fmt
            try:
                r = w.adicionar(url, w.CFG["modo_playlist"])
            finally:
                w.CFG["formato"] = antigo
        return "ok" if r.get("add") else "ja"
    except BaseException:
        traceback.print_exc()
        return "erro"
