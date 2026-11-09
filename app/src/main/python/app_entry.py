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

        sys.argv = ["wavefly", "--no-browser", "--port", str(port)]
        import waveflysite

        _thread = threading.Thread(target=waveflysite.main, name="wavefly-server", daemon=True)
        _thread.start()

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
        atual = baixando[0] if baixando else None
        total = len(baixando) + len(fila) + len(feitos)
        return "%d|%d|%d|%d|%s|%s" % (
            len(baixando), len(fila), total,
            int(atual.get("pct") or 0) if atual else 0,
            (atual.get("vel") or "") if atual else "",
            (atual.get("titulo") or "").replace("|", " ") if atual else "")
    except Exception:
        return "0|0|0|0||"


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
