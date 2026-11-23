"""Palavrões em inglês, português e espanhol, para a busca de versões alternativas.

O YouTube esconde resultados quando a busca tem palavrão ("fuck forever" volta quase nada, "fck forever" volta tudo), e muitos
títulos aparecem censurados ("F**k", "f*ck", "fck"). Aqui ficam:
  - a lista de palavras (sem acento, minúsculas);
  - desmascarar(): volta "f**k"/"fck" para "fuck", para comparar títulos de forma justa;
  - variantes(): as consultas de busca com a palavra abreviada, com asterisco, e sem ela.
Obs.: ofensas discriminatórias ficam de fora de propósito; a lista é só de palavrões comuns em títulos de música."""
import re, unicodedata

EN = """fuck fucks fucked fucking fucker fuckers motherfucker motherfuckers motherfucking fuckin
shit shits shitty bullshit shite bitch bitches bitchin cunt cunts dick dicks dickhead cock cocks pussy pussies
asshole assholes ass bastard bastards whore whores slut sluts sluttish damn goddamn goddamned piss pissed pissing
tits twat wanker prick douche douchebag cum cumming jackass dumbass horseshit crap""".split()
PT = """porra porras caralho caralhos merda merdas puta putas puto putos putaria foda fodas foder fodido fodida fodidos
fodendo cacete cacetes buceta bucetas boceta cu cus cuzao cuzoes viado viados bicha bichas arrombado arrombada
desgraca desgracado desgracada bosta bostas escroto escrota babaca vagabunda vagabundo vadia vadias piranha piranhas
punheta safado safada filhodaputa fdp pqp krl""".split()
ES = """mierda mierdas puta putas puto putos joder jodido jodida jodidos jodete cono conos cabron cabrones cabrona pendejo
pendeja pendejos culo culos verga vergas chingar chingada chingado chingue mamada mamon hostia hostias carajo pinche
marica maricon maricones zorra zorras follar follando cojones polla pollas gilipollas boludo boluda pelotudo concha
conchudo hijodeputa""".split()

PALAVROES = set(EN) | set(PT) | set(ES)
SIMBOLOS = "*#@$%"


def _sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not 0x300 <= ord(c) <= 0x36F)


def abrevia(p):
    """fuck -> fck, shit -> sht (sem as vogais, como se digita para fugir do filtro)."""
    return p[0] + re.sub(r"[aeiou]", "", p[1:]) if len(p) > 3 else p


# abreviações de 3+ letras que valem como a palavra inteira ("fck" = fuck). Palavras curtas não entram (evita "pt" = puta).
ABREV = {}
for _p in sorted(PALAVROES):
    _a = abrevia(_p)
    if len(_p) >= 4 and len(_a) >= 3 and _a != _p:
        ABREV.setdefault(_a, _p)

_TOKEN = re.compile(r"[a-z0-9]*[\*#@\$%][a-z0-9\*#@\$%]*|[a-z0-9]+")


def desmascarar(texto):
    """'F**k Forever' -> 'fuck forever'; 'fck' -> 'fuck'. Devolve o texto em minúsculas, sem acento."""
    t = _sem_acento(texto or "").lower()

    def troca(m):
        tok = m.group(0)
        if any(c in SIMBOLOS for c in tok):
            rx = re.compile("^" + "".join("." if c in SIMBOLOS else re.escape(c) for c in tok) + "$")
            ach = [p for p in sorted(PALAVROES) if len(p) == len(tok) and rx.match(p)]
            return ach[0] if ach else re.sub(r"[\*#@\$%]", "", tok)
        return ABREV.get(tok, tok)

    return _TOKEN.sub(troca, t)


def tem_palavrao(texto):
    return any(w in PALAVROES for w in re.findall(r"[a-z0-9]+", desmascarar(texto)))


def _mascaras(p):
    """Formas de escrever o palavrão, da mais comum para a menos: fck, f*ck, f**k."""
    out = []
    a = abrevia(p)
    if a != p:
        out.append(a)
    m = re.search(r"[aeiou]", p[1:])
    if m:
        i = m.start() + 1
        out.append(p[:i] + "*" + p[i + 1:])
    if len(p) >= 4:
        out.append(p[0] + "*" * (len(p) - 2) + p[-1])
    return out


def variantes(consulta, maximo=4):
    """Consultas alternativas para uma busca com palavrão: abreviada, com asterisco, e sem a palavra."""
    base = " ".join(re.findall(r"[a-z0-9]+", desmascarar(consulta)))
    toks = base.split()
    if not any(t in PALAVROES for t in toks):
        return []
    qs = []
    for k in range(3):
        novo = []
        for t in toks:
            if t in PALAVROES:
                ms = _mascaras(t)
                novo.append(ms[min(k, len(ms) - 1)] if ms else t)
            else:
                novo.append(t)
        qs.append(" ".join(novo))
    qs.append(" ".join(t for t in toks if t not in PALAVROES))
    vistos, out = {base}, []
    for q in qs:
        if q.strip() and q not in vistos:
            vistos.add(q)
            out.append(q)
    return out[:maximo]
