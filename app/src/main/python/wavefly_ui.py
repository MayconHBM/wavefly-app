# -*- coding: utf-8 -*-
"""Idiomas (pt/en/es), ajustes do botão flutuante, atualizações e 'Combina com você'.
Injetado na página por wavefly_android.ajustar_html."""
import json

# (português, inglês, espanhol) - textos exatos da interface
DICT = [
    ("Baixar", "Download", "Descargar"), ("Buscar", "Search", "Buscar"), ("Biblioteca", "Library", "Biblioteca"),
    ("Cole links do YouTube para gerenciar seus downloads.", "Paste YouTube links to manage your downloads.", "Pega enlaces de YouTube para gestionar tus descargas."),
    ("Para organizar suas músicas, precisamos de acesso à pasta de destino.", "To organize your music, we need access to the destination folder.", "Para organizar tu música, necesitamos acceso a la carpeta de destino."),
    ("[Escolher Pasta]", "[Choose folder]", "[Elegir carpeta]"),
    ("Permita o acesso aos arquivos quando o Android pedir.", "Allow file access when Android asks.", "Permite el acceso a los archivos cuando Android lo pida."),
    ("Bem-vindo ao WaveFly! As músicas serão salvas em", "Welcome to WaveFly! Music will be saved to", "¡Bienvenido a WaveFly! La música se guardará en"),
    ("Alterar pasta", "Change folder", "Cambiar carpeta"), ("Entendi", "Got it", "Entendido"),
    ("Cole os links aqui...", "Paste links here...", "Pega los enlaces aquí..."),
    ("Nenhum link", "No links", "Ningún enlace"), ("Colar", "Paste", "Pegar"), ("Limpar", "Clear", "Limpiar"),
    ("Alterar ›", "Change ›", "Cambiar ›"), ("Fila", "Queue", "Cola"), ("Baixando Fila", "Downloading queue", "Descargando cola"),
    ("Baixando", "Downloading", "Descargando"), ("Concluído", "Done", "Completado"),
    ("Cancelar tudo", "Cancel all", "Cancelar todo"), ("Limpar concluídos", "Clear completed", "Limpiar completados"),
    ("Concluídas", "Completed", "Completadas"), ("Avulsos", "Separate files", "Archivos sueltos"), ("Em ZIP", "As ZIP", "En ZIP"),
    ("arquivo(s) pronto(s) para receber", "file(s) ready to receive", "archivo(s) listo(s) para recibir"),
    ("Pesquise faixas, confira visualizações e o tamanho estimado.", "Search tracks, check views and the estimated size.", "Busca canciones, mira las visualizaciones y el tamaño estimado."),
    ("Músicas", "Music", "Música"), ("Playlists", "Playlists", "Listas"), ("Vídeos", "Videos", "Vídeos"), ("Repetidas", "Duplicates", "Repetidas"),
    ("Nome da música ou artista", "Song or artist name", "Nombre de la canción o artista"),
    ("Ver lista", "View list", "Ver lista"), ("Filtrar músicas...", "Filter music...", "Filtrar música..."),
    ("Filtrar vídeos...", "Filter videos...", "Filtrar vídeos..."), ("Mostrar vídeos", "Show videos", "Mostrar vídeos"),
    ("(prioriza músicas)", "(music first)", "(prioriza música)"),
    ("Procura cópias exatas e faixas parecidas na pasta atual para otimizar espaço.", "Finds exact copies and similar tracks in the current folder to save space.", "Busca copias exactas y canciones parecidas en la carpeta actual para ahorrar espacio."),
    ("Procurar repetidas", "Find duplicates", "Buscar repetidas"), ("Apagar", "Delete", "Borrar"), ("Apagar marcadas", "Delete selected", "Borrar marcadas"),
    ("Anterior", "Previous", "Anterior"), ("Próxima", "Next", "Siguiente"), ("Tocar", "Play", "Reproducir"),
    ("Voltar 10 segundos", "Back 10 seconds", "Retroceder 10 segundos"), ("Avançar 10 segundos", "Forward 10 seconds", "Avanzar 10 segundos"),
    ("Fechar", "Close", "Cerrar"), ("Tela cheia", "Full screen", "Pantalla completa"), ("Volume", "Volume", "Volumen"),
    ("Limpar busca", "Clear search", "Borrar búsqueda"), ("Ajustes", "Settings", "Ajustes"),
    ("Ajustes e Qualidade", "Settings and Quality", "Ajustes y calidad"), ("Concluir", "Done", "Listo"),
    ("Formato e Qualidade", "Format and Quality", "Formato y calidad"),
    ("M4A / Opus (Original Bruto)", "M4A / Opus (Raw original)", "M4A / Opus (Original sin procesar)"),
    ("Vídeo MP4", "MP4 Video", "Vídeo MP4"), ("Resolução do Vídeo", "Video resolution", "Resolución del vídeo"),
    ("Salvar na Pasta", "Save to folder", "Guardar en carpeta"), ("Pasta", "Folder", "Carpeta"),
    ("Organização de Playlists", "Playlist organization", "Organización de listas"),
    ("Subpasta própria", "Own subfolder", "Subcarpeta propia"), ("Tudo na pasta principal", "All in main folder", "Todo en la carpeta principal"),
    ("MP3 Universal. Ótima qualidade com compatibilidade garantida em qualquer aparelho, som automotivo ou pendrive.", "Universal MP3. Great quality that works on any device, car stereo or flash drive.", "MP3 universal. Gran calidad compatible con cualquier dispositivo, coche o memoria USB."),
    ("M4A ou Opus (Original Bruto). Download rápido e leve direto do YouTube sem conversão.", "M4A or Opus (raw original). Fast, light download straight from YouTube with no conversion.", "M4A u Opus (original sin procesar). Descarga rápida y ligera directo de YouTube sin conversión."),
    ("Vídeo completo em formato MP4 com excelente qualidade de som e imagem.", "Full video in MP4 with excellent sound and picture quality.", "Vídeo completo en MP4 con excelente calidad de sonido e imagen."),
    ("Modo servidor ativado: os arquivos expiram após algumas horas.", "Server mode on: files expire after a few hours.", "Modo servidor activado: los archivos caducan tras unas horas."),
    ("Escolher pasta de destino", "Choose destination folder", "Elegir carpeta de destino"), ("Criar pasta", "New folder", "Crear carpeta"),
    ("Usar esta pasta", "Use this folder", "Usar esta carpeta"), ("‹ Voltar", "‹ Back", "‹ Volver"), ("Voltar", "Back", "Volver"),
    ("‹ Voltar às pastas", "‹ Back to folders", "‹ Volver a las carpetas"),
    ("Nome da nova pasta", "New folder name", "Nombre de la nueva carpeta"), ("Nome da playlist", "Playlist name", "Nombre de la lista"),
    ("Cancelar", "Cancel", "Cancelar"), ("Confirmar", "Confirm", "Confirmar"), ("Remover", "Remove", "Quitar"),
    ("Forçar", "Force", "Forzar"), ("Tentar de novo", "Try again", "Reintentar"), ("Receber", "Receive", "Recibir"),
    ("Cancelada", "Cancelled", "Cancelada"), ("Na fila", "Queued", "En cola"),
    ("Já existe na pasta (será ignorado)", "Already in the folder (will be skipped)", "Ya está en la carpeta (se omitirá)"),
    ("Já existe na pasta", "Already in the folder", "Ya está en la carpeta"),
    ("Já existe na subpasta · duplicada ignorada", "Already in the subfolder · duplicate skipped", "Ya está en la subcarpeta · duplicada omitida"),
    ("Já existe na pasta · marcada como duplicada", "Already in the folder · marked as duplicate", "Ya está en la carpeta · marcada como duplicada"),
    ("Já está na pasta", "Already in the folder", "Ya está en la carpeta"),
    ("Link do YouTube", "YouTube link", "Enlace de YouTube"), ("Mostrar mais", "Show more", "Mostrar más"), ("Recolher", "Collapse", "Contraer"),
    ("Ouvir prévia", "Preview", "Escuchar vista previa"), ("Título indisponível", "Title unavailable", "Título no disponible"),
    ("Carregando...", "Loading...", "Cargando..."), ("Carregando itens...", "Loading items...", "Cargando elementos..."),
    ("Pesquisando...", "Searching...", "Buscando..."), ("Abrindo playlist...", "Opening playlist...", "Abriendo lista..."),
    ("Processando links...", "Processing links...", "Procesando enlaces..."),
    ("Nenhum resultado.", "No results.", "Sin resultados."), ("Playlist vazia.", "Empty playlist.", "Lista vacía."),
    ("Nenhum arquivo encontrado.", "No files found.", "No se encontraron archivos."),
    ("Nenhuma repetida encontrada.", "No duplicates found.", "No se encontraron repetidas."),
    ("Nenhum vídeo MP4 encontrado nesta pasta.", "No MP4 video found in this folder.", "No se encontró ningún vídeo MP4 en esta carpeta."),
    ("Pesquise por música ou artista.", "Search for a song or artist.", "Busca una canción o artista."), ("Pesquise por playlist.", "Search for a playlist.", "Busca una lista."),
    ("Arquivos Soltos na Raiz", "Loose files in the root", "Archivos sueltos en la raíz"),
    ("Cópias Exatas", "Exact copies", "Copias exactas"), ("Parecidas", "Similar", "Parecidas"),
    ("Nada novo", "Nothing new", "Nada nuevo"), ("Nada novo para baixar", "Nothing new to download", "Nada nuevo que descargar"),
    ("Pasta criada", "Folder created", "Carpeta creada"), ("Nenhum link copiado.", "No link copied.", "Ningún enlace copiado."),
    ("Link copiado colado", "Copied link pasted", "Enlace copiado pegado"),
    ("Cole pelo menos um link do YouTube", "Paste at least one YouTube link", "Pega al menos un enlace de YouTube"),
    ("Aguarde o carregamento da playlist.", "Wait for the playlist to load.", "Espera a que cargue la lista."),
    ("Compactando arquivos em ZIP...", "Packing files into a ZIP...", "Comprimiendo archivos en ZIP..."),
    ("Não consegui reproduzir este arquivo", "I couldn't play this file", "No pude reproducir este archivo"),
    ("Digite pelo menos 3 letras", "Type at least 3 letters", "Escribe al menos 3 letras"),
    ("Itens já existentes foram ignorados.", "Items that already exist were skipped.", "Se omitieron los elementos que ya existen."),
    ("Não foi possível abrir a playlist", "Could not open the playlist", "No se pudo abrir la lista"),
    ("Playlist vazia ou privada", "Empty or private playlist", "Lista vacía o privada"),
    ("Vídeo", "Video", "Vídeo"), ("Música", "Music", "Música"), ("Contém vídeo", "Contains video", "Contiene vídeo"),
    ("Selecionar todos", "Select all", "Seleccionar todos"), ("Selecionar todas", "Select all", "Seleccionar todas"),
    ("Desmarcar todos", "Deselect all", "Deseleccionar todos"), ("Desmarcar todas", "Deselect all", "Deseleccionar todas"),
    ("Selecionar visíveis", "Select visible", "Seleccionar visibles"), ("Baixar visíveis", "Download visible", "Descargar visibles"),
    ("Assistir", "Watch", "Ver"), ("Ouvir", "Listen", "Escuchar"), ("Abrir", "Open", "Abrir"),
    ("tudo", "all", "todo"), ("e interromper os downloads?", "and stop the downloads?", "e interrumpir las descargas?"),
    ("arquivos marcados?", "marked files?", "archivos marcados?"), ("arquivo do aparelho?", "file from the device?", "archivo del dispositivo?"),
    ("arquivos do aparelho?", "files from the device?", "archivos del dispositivo?"),
    ("Remover as", "Remove the", "Quitar las"), ("músicas da seleção?", "songs from the selection?", "canciones de la selección?"),
    ("Preparando…", "Preparing…", "Preparando…"), ("Lendo título…", "Reading title…", "Leyendo título…"),
    ("Baixando…", "Downloading…", "Descargando…"), ("Cancelando…", "Cancelling…", "Cancelando…"),
    ("convertendo…", "converting…", "convirtiendo…"), ("juntando…", "merging…", "uniendo…"),
    ("YouTube bloqueou temporariamente (confirmação necessária)", "YouTube temporarily blocked this (confirmation required)", "YouTube lo bloqueó temporalmente (se requiere confirmación)"),
    # novos
    ("Idioma", "Language", "Idioma"), ("Botão flutuante", "Floating button", "Botón flotante"),
    ("Ativar botão flutuante", "Enable floating button", "Activar botón flotante"),
    ("Fica sobre os outros apps: copie o link do vídeo e toque nele para baixar.", "Stays on top of other apps: copy the video link and tap it to download.", "Se queda sobre otras apps: copia el enlace del vídeo y tócalo para descargar."),
    ("Atualizações", "Updates", "Actualizaciones"), ("Procurar atualizações", "Check for updates", "Buscar actualizaciones"),
    ("Combina com você", "Made for you", "Combina contigo"),
    ("Sugestões a partir das suas músicas. Tudo fica neste aparelho.", "Suggestions based on your music. Everything stays on this device.", "Sugerencias según tu música. Todo se queda en este dispositivo."),
    ("Procurando sugestões…", "Finding suggestions…", "Buscando sugerencias…"), ("Adicionada", "Added", "Añadida"),
    ("Não foi possível carregar as sugestões agora.", "Could not load suggestions right now.", "No se pudieron cargar las sugerencias ahora."),
    ("Não mostrar este aviso novamente", "Don't show this notice again", "No mostrar este aviso de nuevo"),
    ("Como usar", "How to use", "Cómo usar"),
]

# padrões com números: (regex em português, inglês, espanhol)
PADROES = [
    (r"^(\d+) adicionados? à fila$", "$1 added to the queue", "$1 añadido(s) a la cola"),
    (r"^(\d+) adicionados?$", "$1 added", "$1 añadido(s)"),
    (r"^(\d+) já (?:estão|está) na fila$", "$1 already in the queue", "$1 ya en la cola"),
    (r"^(\d+) já (?:existem|existe) na pasta$", "$1 already in the folder", "$1 ya en la carpeta"),
    (r"^(\d+) já existem? na subpasta$", "$1 already in the subfolder", "$1 ya en la subcarpeta"),
    (r"^(\d+) duplicados marcados$", "$1 duplicates marked", "$1 duplicados marcados"),
    (r"^(\d+) repetidos? ignorados?$", "$1 duplicate(s) skipped", "$1 repetido(s) omitido(s)"),
    (r"^(\d+) ignorados?$", "$1 skipped", "$1 omitido(s)"),
    (r"^(\d+) playlists?$", "$1 playlist(s)", "$1 lista(s)"),
    (r"^(\d+) apagados$", "$1 deleted", "$1 borrados"),
    (r"^(\d+) selecionad[oa]s?$", "$1 selected", "$1 seleccionado(s)"),
    (r"^(\d+) de (\d+) selecionados$", "$1 of $2 selected", "$1 de $2 seleccionados"),
    (r"^(\d+) itens?$", "$1 item(s)", "$1 elemento(s)"),
    (r"^(\d+) arquivos?$", "$1 file(s)", "$1 archivo(s)"),
    (r"^(\d+) músicas mantidas na seleção\.$", "$1 songs kept in the selection.", "$1 canciones mantenidas en la selección."),
    (r"^Fila \((\d+)\)$", "Queue ($1)", "Cola ($1)"),
    (r"^Concluídas \((\d+)\)$", "Completed ($1)", "Completadas ($1)"),
    (r"^Baixar (\d+)(.*)$", "Download $1$2", "Descargar $1$2"),
    (r"^Baixando (\d+) arquivos\.\.\.$", "Downloading $1 files...", "Descargando $1 archivos..."),
    (r"^ZIP pronto com (\d+) arquivos$", "ZIP ready with $1 files", "ZIP listo con $1 archivos"),
    (r"^Ver mais \((\d+)\)$", "See more ($1)", "Ver más ($1)"),
    (r"^Falhou: (.*)$", "Failed: $1", "Falló: $1"),
    (r"^faltam ~(.*)$", "~$1 left", "faltan ~$1"),
    (r"^~(.*) est\.$", "~$1 est.", "~$1 est."),
    (r"^([\d.]+) views$", "$1 views", "$1 visualizaciones"),
    (r"^Estimativa: ~(.*)$", "Estimate: ~$1", "Estimación: ~$1"),
    (r"^Salvando em: (.*)$", "Saving to: $1", "Guardando en: $1"),
    (r"^(\d+) de (\d+)$", "$1 of $2", "$1 de $2"),
    (r"^(.*) selecionados? \((.*)\)$", "$1 selected ($2)", "$1 seleccionado(s) ($2)"),
    (r"^Lendo(.*)$", "Reading$1", "Leyendo$1"),
]

CSS = """<style id="wf-ui-css">
/* textos mais longos (inglês/espanhol): os botões quebram a linha em vez de estourar */
html body button,html body .tabs a,html body .chip{overflow-wrap:anywhere;min-width:0}
html body .sg button{min-width:0;white-space:normal;line-height:1.15}
html body .tabs a{min-width:0;padding-left:4px;padding-right:4px;white-space:normal;overflow-wrap:normal;word-break:normal;line-height:1.1;text-align:center}
html[lang="es"] body .tabs a{font-size:13px;letter-spacing:-.2px}
.wfrow{display:flex;align-items:center;justify-content:space-between;gap:12px}
.wfrow .wft{min-width:0;font-weight:600}
.wfsw{position:relative;flex:none;width:52px;height:30px}
.wfsw input{opacity:0;position:absolute;inset:0;width:100%;height:100%;margin:0;z-index:2}
.wfsw i{position:absolute;inset:0;border-radius:30px;background:rgba(127,110,90,.45);transition:.2s;box-shadow:inset 0 2px 4px rgba(0,0,0,.25)}
.wfsw i:after{content:"";position:absolute;left:3px;top:3px;width:24px;height:24px;border-radius:50%;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.35);transition:.2s}
.wfsw input:checked+i{background:#d9692a}
.wfsw input:checked+i:after{transform:translateX(22px)}
.wfmodal{position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;padding:24px}
.wfmodal .wfcard{background:#f3e6cc;color:#3b2314;border-radius:20px;padding:20px 20px 18px;max-width:420px;width:100%;box-shadow:0 12px 40px rgba(0,0,0,.45)}
.wfmodal h3{margin:0 0 8px;font-size:19px}
.wfmodal p{margin:8px 0;font-size:14.5px;line-height:1.4}
.wfmodal label{display:flex;gap:10px;align-items:center;margin:14px 0 4px;font-size:14px}
.wfmodal label input{width:20px;height:20px;flex:none}
.wfmodal .wfok{display:block;margin:12px auto 0;min-width:60%}
#wfcomb{margin:16px 0 4px}
#wfcomb .wfh{display:flex;align-items:center;justify-content:space-between;gap:8px}
#wfcomb h2{margin:0;font-size:18px}
#wfcomb .wfs{font-size:12.5px;opacity:.7;margin:2px 0 8px}
#wfcomb .wfar{display:flex;gap:6px}
#wfcomb .wfar button{width:34px;height:34px;padding:0;border-radius:50%;font-size:20px;line-height:1}
#wfcomb .wftr{display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding:2px 2px 8px;-webkit-overflow-scrolling:touch}
#wfcomb .wftr::-webkit-scrollbar{display:none}
#wfcomb .wfc{flex:none;width:min(64%,230px);scroll-snap-align:start;border-radius:14px;background:rgba(127,110,90,.14);overflow:hidden;display:flex;flex-direction:column}
#wfcomb .wfc img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;background:rgba(0,0,0,.2)}
#wfcomb .wfc .wfb{padding:8px 10px 10px;display:flex;flex-direction:column;gap:3px;flex:1}
#wfcomb .wfc .wfn{font-weight:700;font-size:13.5px;line-height:1.25;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
#wfcomb .wfc .wfa{font-size:12px;opacity:.7;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#wfcomb .wfc button{margin-top:auto;width:100%}
#wfcomb .wfm{font-size:13px;opacity:.75;padding:10px 2px}
.wfver{font-size:12.5px;opacity:.75;margin:6px 0 0}
</style>
"""

JS_TPL = r"""<script id="wf-ui-js">
(function(){
var DICT=__DICT__, PAD=__PAD__;
var IDX={en:{},es:{}};DICT.forEach(function(d){IDX.en[d[0]]=d[1];IDX.es[d[0]]=d[2]});
var PADR=PAD.map(function(p){return [new RegExp(p[0]),p[1],p[2]]});
var NAT=[['pt','Português'],['en','English'],['es','Español']];
var W=(typeof WF!=='undefined')?WF:null;
function wfget(k){try{return W&&W.pref?W.pref(k):localStorage.getItem('wf_'+k)||''}catch(e){return ''}}
function wfset(k,v){try{if(W&&W.setPref)W.setPref(k,v);else localStorage.setItem('wf_'+k,v)}catch(e){}}
var LANG='pt';
try{LANG=(W&&W.lang&&W.lang())||localStorage.getItem('wf_lang')||''}catch(e){}
if(LANG!=='pt'&&LANG!=='en'&&LANG!=='es'){var n=(navigator.language||'pt').slice(0,2);LANG=n==='es'?'es':n==='en'?'en':'pt'}
function T(pt){if(LANG==='pt')return pt;var m=IDX[LANG];return m[pt]||pt}
function tseg(s,lang){
  var m=IDX[lang];if(m[s]!==undefined)return m[s];
  for(var i=0;i<PADR.length;i++){var r=PADR[i][0].exec(s);if(r){var t=PADR[i][lang==='en'?1:2];return t.replace(/\$(\d)/g,function(_,k){return r[k]===undefined?'':r[k]})}}
  return null}
function trans(raw,lang){
  if(lang==='pt'||!raw)return raw;
  var lead=raw.match(/^\s*/)[0],trail=raw.match(/\s*$/)[0],core=raw.trim();
  if(!core||core.length>400)return raw;
  var out=tseg(core,lang);
  if(out===null&&core.indexOf(' · ')>0){
    var ps=core.split(' · '),ch=false;
    ps=ps.map(function(p){var o=tseg(p.trim(),lang);if(o===null)return p;ch=true;return o});
    if(ch)out=ps.join(' · ')}
  return out===null?raw:lead+out+trail}
var BUSY=false;
function doText(n){
  var v=n.nodeValue;
  if(n.__wft!==undefined&&v===n.__wft)return;
  n.__wfo=v;
  var o=trans(v,LANG);
  if(o!==v){n.__wft=o;n.nodeValue=o}else n.__wft=undefined}
function restoreText(n){if(n.__wft!==undefined&&n.__wfo!==undefined){n.nodeValue=n.__wfo;n.__wft=undefined}}
var ATTRS=['placeholder','aria-label','title'];
function doAttr(e){
  ATTRS.forEach(function(a){
    if(!e.hasAttribute||!e.hasAttribute(a))return;
    var k='wfo_'+a,cur=e.getAttribute(a);
    if(e[k+'_t']!==undefined&&cur===e[k+'_t'])return;
    e[k]=cur;var o=trans(cur,LANG);
    if(o!==cur){e[k+'_t']=o;e.setAttribute(a,o)}else e[k+'_t']=undefined})}
function walk(root,fn,afn){
  if(root.nodeType===3){fn(root);return}
  if(root.nodeType!==1&&root.nodeType!==9&&root.nodeType!==11)return;
  if(root.nodeType===1){var tg=root.tagName;if(tg==='SCRIPT'||tg==='STYLE')return;afn(root)}
  var c=root.firstChild;while(c){walk(c,fn,afn);c=c.nextSibling}}
function applyAll(){
  BUSY=true;
  try{walk(document.body,LANG==='pt'?restoreText:doText,LANG==='pt'?function(e){ATTRS.forEach(function(a){var k='wfo_'+a;if(e[k+'_t']!==undefined&&e.getAttribute(a)===e[k+'_t']){e.setAttribute(a,e[k]);e[k+'_t']=undefined}})}:doAttr)}catch(e){}
  BUSY=false;
  document.documentElement.lang=LANG==='pt'?'pt-BR':LANG}
var MO=new MutationObserver(function(ms){
  if(BUSY||LANG==='pt'){return}
  BUSY=true;
  try{ms.forEach(function(m){
    if(m.type==='characterData'){doText(m.target)}
    else if(m.type==='attributes'){doAttr(m.target)}
    else m.addedNodes.forEach(function(n){walk(n,doText,doAttr)})})}catch(e){}
  BUSY=false});
MO.observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:ATTRS});

function setLang(l){
  LANG=l;try{localStorage.setItem('wf_lang',l);if(W&&W.setLang)W.setLang(l)}catch(e){}
  applyAll();
  document.querySelectorAll('[data-wflang]').forEach(function(b){b.classList.toggle('on',b.dataset.wflang===l)});
  try{if(typeof tick==='function')tick()}catch(e){}
  if(comb.pronto)combRender(true)}

/* ---------- Ajustes: idioma, botão flutuante, atualizações ---------- */
function mk(h){var d=document.createElement('div');d.innerHTML=h;return d.firstChild}
var pn=document.querySelector('#sheet .spn'),ref=document.getElementById('srvnote');
if(pn){
  var g1=mk('<div class="g" id="wf-g-lang"><span class="l">Idioma / Language</span><div class="sg full">'+
    NAT.map(function(n){return '<button data-wflang="'+n[0]+'">'+n[1]+'</button>'}).join('')+'</div></div>');
  pn.insertBefore(g1,ref);
  g1.querySelectorAll('button').forEach(function(b){b.onclick=function(){setLang(b.dataset.wflang)};b.classList.toggle('on',b.dataset.wflang===LANG)});
  if(W&&typeof W.bolhaEstado==='function'){
    var g2=mk('<div class="g" id="wf-g-bolha"><span class="l">Botão flutuante</span><div class="wfrow"><span class="wft">Ativar botão flutuante</span><label class="wfsw"><input type="checkbox" id="wfbolha"><i></i></label></div><p class="note">Fica sobre os outros apps: copie o link do vídeo e toque nele para baixar.</p></div>');
    pn.insertBefore(g2,ref);
    var sw=g2.querySelector('input');sw.checked=W.bolhaEstado()==='1';
    sw.onchange=function(){
      if(!sw.checked){W.bolha(0);return}
      sw.checked=false;
      var ativar=function(){var r=W.bolha(1);if(r==='perm'){toast(T('Libere "Aparecer sobre outros apps" para o WaveFly e volte.'))}else sw.checked=true};
      if(wfget('bolha_aviso')==='1')ativar();else aviso(ativar)};
    window.wfBolha=function(on){sw.checked=!!on};
  }
  var g3=mk('<div class="g" id="wf-g-up"><span class="l">Atualizações</span><button class="rb" id="wfup"><span>Procurar atualizações</span><span class="r"><b id="wfv1"></b></span></button><p class="wfver" id="wfv2"></p></div>');
  pn.insertBefore(g3,ref);
  g3.querySelector('#wfup').onclick=function(){
    if(W&&W.verificarAtualizacao)W.verificarAtualizacao();
    fetch('/api/ytdlp?forcar=1').then(function(r){return r.json()}).then(function(j){
      var m=j.resultado||'';
      if(m.indexOf('baixada')===0)toast(LANG==='en'?'yt-dlp updated. Restart the app to use it.':LANG==='es'?'yt-dlp actualizado. Reinicia la app para usarlo.':'yt-dlp atualizado. Reabra o app para usar.');
      else if(m.indexOf('erro')===0)toast(LANG==='en'?'Could not check yt-dlp now.':LANG==='es'?'No se pudo comprobar yt-dlp ahora.':'Não consegui verificar o yt-dlp agora.');
      else toast(LANG==='en'?'yt-dlp is up to date.':LANG==='es'?'yt-dlp está al día.':'yt-dlp está em dia.');
      info()}).catch(function(){})};
  function info(){fetch('/api/ytdlp').then(function(r){return r.json()}).then(function(j){
    var a=W&&W.versaoApp?W.versaoApp():'';
    document.getElementById('wfv1').textContent=a?('v'+a):'';
    document.getElementById('wfv2').textContent='yt-dlp '+(j.versao||'?')}).catch(function(){})}
  info();
}
function aviso(depois){
  var m=mk('<div class="wfmodal"><div class="wfcard"><h3>'+T('Botão flutuante')+'</h3>'+
   '<p>'+({pt:'O botão flutuante fica na tela para capturar links do YouTube com um toque e fazer downloads em segundo plano.',en:'The floating button stays on screen to capture YouTube links with one tap and download in the background.',es:'El botón flotante se queda en pantalla para capturar enlaces de YouTube con un toque y descargar en segundo plano.'})[LANG]+'</p>'+
   '<p><b>'+T('Como usar')+':</b> '+({pt:'abra um vídeo no YouTube, toque em Compartilhar › Copiar link e toque no botão flutuante para iniciar o download. Para desativar, mantenha o botão pressionado e confirme no menu de encerramento.',en:'open a video on YouTube, tap Share › Copy link, then tap the floating button to start the download. To turn it off, press and hold the button and confirm in the menu.',es:'abre un vídeo en YouTube, toca Compartir › Copiar enlace y toca el botón flotante para iniciar la descarga. Para desactivarlo, mantén pulsado el botón y confirma en el menú.'})[LANG]+'</p>'+
   '<label><input type="checkbox" id="wfnm"> <span>'+T('Não mostrar este aviso novamente')+'</span></label>'+
   '<button class="p wfok">'+T('Entendi')+'</button></div></div>');
  document.body.appendChild(m);
  m.querySelector('.wfok').onclick=function(){if(m.querySelector('#wfnm').checked)wfset('bolha_aviso','1');m.remove();depois()}}

/* ---------- Combina com você ---------- */
var comb={pg:0,itens:[],mais:true,busy:false,pronto:false,box:null};
function combBox(){
  if(comb.box)return comb.box;
  var bgo=document.getElementById('bgo');if(!bgo)return null;
  var b=mk('<div id="wfcomb" hidden><div class="wfh"><h2>Combina com você</h2><div class="wfar"><button class="s2" id="wfcl" aria-label="Anterior">‹</button><button class="s2" id="wfcr" aria-label="Próxima">›</button></div></div><div class="wfs">Sugestões a partir das suas músicas. Tudo fica neste aparelho.</div><div class="wftr" id="wftr"></div></div>');
  bgo.parentNode.insertBefore(b,bgo.nextSibling);
  b.querySelector('#wfcl').onclick=function(){b.querySelector('#wftr').scrollBy({left:-(b.querySelector('.wfc')||{offsetWidth:220}).offsetWidth-10,behavior:'smooth'})};
  b.querySelector('#wfcr').onclick=function(){var tr=b.querySelector('#wftr'),w=(b.querySelector('.wfc')||{offsetWidth:220}).offsetWidth+10;
    if(tr.scrollLeft+tr.clientWidth>=tr.scrollWidth-w*1.2&&comb.mais)combMais();tr.scrollBy({left:w,behavior:'smooth'})};
  b.querySelector('#wftr').addEventListener('scroll',function(){var tr=this;if(tr.scrollLeft+tr.clientWidth>=tr.scrollWidth-40&&comb.mais)combMais()},{passive:true});
  comb.box=b;return b}
function combRender(){
  var b=combBox();if(!b)return;
  var tr=b.querySelector('#wftr');
  if(!comb.itens.length){tr.innerHTML=comb.busy?'<div class="wfm">'+T('Procurando sugestões…')+'</div>':'';b.hidden=!comb.busy;return}
  b.hidden=false;
  tr.innerHTML=comb.itens.map(function(e){return '<div class="wfc" data-id="'+e.id+'"><img loading="lazy" src="https://i.ytimg.com/vi/'+e.id+'/mqdefault.jpg" alt=""><div class="wfb"><div class="wfn"></div><div class="wfa"></div><button class="a" data-wfd="'+e.id+'">'+T('Baixar')+'</button></div></div>'}).join('');
  [].forEach.call(tr.querySelectorAll('.wfc'),function(c,i){c.querySelector('.wfn').textContent=comb.itens[i].titulo;c.querySelector('.wfa').textContent=comb.itens[i].canal||''});
  [].forEach.call(tr.querySelectorAll('button[data-wfd]'),function(bt){bt.onclick=function(){
    var id=bt.dataset.wfd,e=comb.itens.filter(function(x){return x.id===id})[0],t={};t[id]=e?e.titulo:'';
    bt.disabled=true;
    api('/api/add',{texto:'https://www.youtube.com/watch?v='+id,titulos:t}).then(function(r){
      try{toast(msgAdd(r))}catch(x){}
      bt.textContent=T('Adicionada');
      comb.itens=comb.itens.filter(function(x){return x.id!==id});
      setTimeout(function(){combRender()},700);
      try{tick()}catch(x){}}).catch(function(err){bt.disabled=false;toast(err.message)})}})}
function combMais(){if(comb.busy||!comb.mais)return;comb.busy=true;
  fetch('/api/combina?pg='+comb.pg).then(function(r){return r.json()}).then(function(j){
    comb.busy=false;comb.pronto=true;
    if(j.itens&&j.itens.length){comb.itens=comb.itens.concat(j.itens);comb.pg++}
    comb.mais=!!j.mais&&j.itens&&j.itens.length>0;
    combRender()}).catch(function(){comb.busy=false;comb.mais=false;combRender()})}
setTimeout(function(){combBox();combMais()},2500);

setLang(LANG);
})();
</script>
"""


def bloco():
    js = JS_TPL.replace("__DICT__", json.dumps(DICT, ensure_ascii=False)).replace("__PAD__", json.dumps(PADROES, ensure_ascii=False))
    return CSS + js
