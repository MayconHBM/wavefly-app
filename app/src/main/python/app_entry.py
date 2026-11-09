# -*- coding: utf-8 -*-
"""Ponte entre o app Android (Java) e o servidor WaveFly (Python)."""
import os
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
