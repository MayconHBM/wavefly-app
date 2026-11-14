# -*- coding: utf-8 -*-
"""Ponto de entrada do WaveFly para Windows (.exe). Usa o mesmo motor e a mesma tela do app do celular."""
import os
import socket
import sys
import threading
import traceback


def _base():
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def _ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "IP-DO-PC"


def main():
    celular = "--celular" in sys.argv
    porta = 8773
    for i, a in enumerate(sys.argv):
        if a == "--port" and i + 1 < len(sys.argv):
            porta = int(sys.argv[i + 1])
    dados = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "WaveFly")
    os.makedirs(os.path.join(dados, "tmp"), exist_ok=True)
    os.environ["WAVEFLY_PC"] = "1"
    os.environ["WAVEFLY_DATA"] = dados
    b = os.path.join(_base(), "bin")
    if os.path.isdir(b):
        os.environ["WAVEFLY_FFMPEG"] = b
        os.environ["PATH"] = b + os.pathsep + os.environ.get("PATH", "")
    try:
        import certifi
        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    except Exception:
        pass
    sys.argv = ["wavefly", "--port", str(porta)] + (["--host", "0.0.0.0", "--no-browser"] if celular else [])
    import waveflysite
    try:
        import wavefly_android
        wavefly_android.aplicar(waveflysite)
    except Exception:
        traceback.print_exc()
    try:
        import app_entry
        app_entry.atualizar_ytdlp = lambda d, f: "pc:baixe um .exe mais novo na página de downloads"
    except Exception:
        pass
    if celular:
        print("\n📱 MODO CELULAR: no navegador do celular (na MESMA rede Wi-Fi) abra:\n   http://%s:%d\n" % (_ip_local(), porta))
        print("   Se o Windows perguntar sobre o Firewall, permita em 'Redes privadas'.")
        print("   Feche esta janela para encerrar.\n")
    waveflysite.main()


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        # teste de fumaça do build: confere ffmpeg, deno e a importação do motor
        import subprocess
        b = os.path.join(_base(), "bin")
        ok = True
        for exe in ("ffmpeg.exe", "deno.exe"):
            try:
                r = subprocess.run([os.path.join(b, exe), "-version" if "ffmpeg" in exe else "--version"], capture_output=True, timeout=60)
                print(exe, "ok" if r.returncode == 0 else "FALHOU")
                ok = ok and r.returncode == 0
            except Exception as e:
                print(exe, "FALHOU", e)
                ok = False
        try:
            import yt_dlp, mutagen, waveflysite, wavefly_android, wavefly_ui, app_entry  # noqa: F401
            print("imports ok · yt-dlp", yt_dlp.version.__version__)
        except Exception:
            traceback.print_exc()
            ok = False
        sys.exit(0 if ok else 1)
    main()
