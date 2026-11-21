#!/usr/bin/env python3
"""Conferência rápida antes de gerar o APK: sintaxe (Python e JavaScript), traduções e a lógica principal.
Roda no CI; se falhar, nenhuma release é criada."""
import ast, os, re, subprocess, sys, tempfile, types

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(RAIZ, "app", "src", "main", "python")
erros = []


def falha(msg):
    erros.append(msg)
    print("FALHOU:", msg)


def ok(msg):
    print("ok:", msg)


# 1) sintaxe Python
fontes = {}
for f in sorted(os.listdir(PY)):
    if f.endswith(".py"):
        fontes[f] = open(os.path.join(PY, f), encoding="utf-8").read()
        try:
            ast.parse(fontes[f])
        except SyntaxError as e:
            falha("sintaxe %s: %s" % (f, e))
ok("sintaxe Python (%d arquivos)" % len(fontes))

# 2) sintaxe JavaScript (tela principal e script de interface)
def checa_js(nome, js):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as t:
        t.write(js)
    r = subprocess.run(["node", "--check", t.name], capture_output=True, text=True)
    os.unlink(t.name)
    if r.returncode:
        falha("JavaScript %s: %s" % (nome, r.stderr.strip()[:300]))
    else:
        ok("JavaScript " + nome)

m = re.search(r"HTML = r'''(.*?)'''", fontes["waveflysite.py"], re.S)
if not m:
    falha("HTML da tela não encontrado")
else:
    scripts = re.findall(r"<script>(.*?)</script>", m.group(1), re.S)
    checa_js("tela principal", max(scripts, key=len))
    # a função de tradução T() só existe na camada de interface; chamá-la na tela principal quebra o botão em silêncio
    if re.search(r"(?<![\w.$])T\(", max(scripts, key=len)):
        falha("a tela principal chama T(), que não existe lá (use texto em português puro)")
for n in ast.parse(fontes["wavefly_ui.py"]).body:
    v = getattr(getattr(n, "value", None), "value", None)
    if isinstance(n, ast.Assign) and isinstance(v, str) and "<script" in v and "</script>" in v:
        corpo = v.split(">", 1)[1].rsplit("</script>", 1)[0]
        checa_js("interface (%s)" % n.targets[0].id, corpo)

# 3) lógica (com o yt_dlp trocado por um de mentira)
stub = types.ModuleType("yt_dlp")
class _Y:
    def __init__(s, *a, **k): pass
    def __enter__(s): return s
    def __exit__(s, *a): pass
    def extract_info(s, *a, **k):
        return {"entries": [
            {"id": "AAAAAAAAAAA", "title": "Hello (Live)", "duration": 300, "channel": "Adele"},
            {"id": "BBBBBBBBBBB", "title": "Lionel Richie - Hello", "duration": 250, "channel": "LionelRichieVEVO"},
            {"id": "DDDDDDDDDDD", "title": "Adele - Hello", "duration": 361, "channel": "Adele - Topic"}]}
stub.YoutubeDL = _Y
utils = types.ModuleType("yt_dlp.utils"); utils.DownloadError = Exception
stub.utils = utils
sys.modules.setdefault("yt_dlp", stub); sys.modules.setdefault("yt_dlp.utils", utils)
import shutil
_COPIA = os.path.join(tempfile.mkdtemp(), "py")      # roda numa cópia: o teste grava arquivos e não pode sujar o repositório
shutil.copytree(PY, _COPIA)
sys.path.insert(0, _COPIA)
os.environ.setdefault("WAVEFLY_DATA", tempfile.mkdtemp())
try:
    import waveflysite as w
    import wavefly_ui as ui
    w.yt_dlp.YoutubeDL = _Y
    t = tempfile.mkdtemp()
    w.CFG["pastas"] = {"T": t}; w.CFG["atual"] = "T"
    os.makedirs(t + "/Rock"); open(t + "/Rock/a.mp3", "wb").write(b"x" * 3000); open(t + "/solta.mp3", "wb").write(b"y" * 3000)
    assert w.nova_playlist("Vazia")["ok"]
    pls = {p["nome"]: p["total"] for p in w.lista_biblioteca()["playlists"]}
    assert pls == {"Rock": 1, "Vazia": 0}, pls
    assert w.renomear_playlist("Rock", "Rock 2")["ok"] and os.path.exists(t + "/Rock 2/a.mp3")
    assert w.mover_copiar(["solta.mp3"], "Vazia")["ok"] == 1
    w.TIT_CACHE["BwLs22Hxi6Q"] = {"titulo": "Hello", "canal": "Adele - Topic"}
    it = {"titulo": "Hello", "url": "https://www.youtube.com/watch?v=BwLs22Hxi6Q", "dur": 365}
    assert w.buscar_alternativa(it).endswith("DDDDDDDDDDD")
    it["dur"] = 100
    assert w.buscar_alternativa(it) is None
    ok("lógica: biblioteca, playlists, mover e alternativa")
    # 4) traduções: toda entrada tem 3 textos; padrões compilam
    for e in ui.DICT:
        if not (len(e) == 3 and all(isinstance(x, str) and x for x in e)):
            falha("tradução incompleta: %r" % (e[:1],))
    for e in ui.PADROES:
        re.compile(e[0])
    ok("traduções (%d textos, %d padrões)" % (len(ui.DICT), len(ui.PADROES)))
except Exception as ex:
    import traceback; traceback.print_exc()
    falha("lógica: %r" % ex)

if erros:
    print("\n%d problema(s). Nada será publicado." % len(erros))
    sys.exit(1)
print("\nTudo certo.")
