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
    ("Pausar tudo", "Pause all", "Pausar todo"), ("Continuar", "Resume", "Continuar"),
    ("Downloads pausados.", "Downloads paused.", "Descargas en pausa."), ("Registro copiado", "Log copied", "Registro copiado"),
    ("Informações", "Info", "Información"), ("Conversão", "Conversion", "Conversión"), ("Espera", "Wait", "Espera"),
    ("Músicas por hora", "Songs per hour", "Canciones por hora"), ("Amostra", "Sample", "Muestra"),
    ("Sem medidas ainda. Baixe algumas músicas.", "No measurements yet. Download a few songs.", "Aún sin mediciones. Descarga algunas canciones."),
    ("Falhas", "Failures", "Fallos"), ("Bateria", "Battery", "Batería"), ("Memória do app", "App memory", "Memoria de la app"),
    ("Rede", "Network", "Red"), ("Sem eventos.", "No events.", "Sin eventos."), ("Desenvolvedor", "Developer", "Desarrollador"),
    ("Esconder", "Hide", "Ocultar"), ("Painel do desenvolvedor", "Developer panel", "Panel de desarrollador"),
    ("Download mais rápido", "Faster download", "Descarga más rápida"), ("Copiar registro", "Copy log", "Copiar registro"),
    ("Anterior", "Previous", "Anterior"), ("Ouvir", "Listen", "Escuchar"),
    ("Transmissão ao vivo: não dá para baixar", "Live stream: it can't be downloaded", "Transmisión en vivo: no se puede descargar"),
    ("Remover", "Remove", "Quitar"),
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
#wfcomb .wfbox{display:flex;align-items:stretch;gap:6px}
#wfcomb .wfnav{flex:none;width:30px;align-self:center;height:56px;padding:0;border-radius:14px;font-size:24px;line-height:1;display:flex;align-items:center;justify-content:center}
#wfcomb .wfnav[disabled]{opacity:.3}
#wfcomb .wfgrid{flex:1;min-width:0;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto auto;gap:8px;min-height:150px}
#wfcomb .wfc{min-width:0;border-radius:14px;background:rgba(127,110,90,.14);overflow:hidden;display:flex;flex-direction:column}
#wfcomb .wfth{position:relative;width:100%;aspect-ratio:16/9;background:rgba(0,0,0,.2);overflow:hidden}
#wfcomb .wfth img{width:100%;height:100%;object-fit:cover;display:block}
#wfcomb .wfb{padding:6px 7px 8px;display:flex;flex-direction:column;gap:2px;flex:1;min-width:0}
#wfcomb .wfn{font-weight:700;font-size:12px;line-height:1.2;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.4em}
#wfcomb .wfa{font-size:11px;opacity:.7;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#wfcomb .wfc .wfd{margin-top:5px;width:100%;padding:7px 4px;font-size:12.5px}
#wfcomb .wfm{grid-column:1/3;font-size:13px;opacity:.75;padding:20px 4px;text-align:center}
.wfver{font-size:12.5px;opacity:.75;margin:6px 0 0}
#wfdev{position:fixed;inset:0;z-index:99998;background:var(--t-bg,#e8dcc2);color:#3b2314;overflow-y:auto;padding:16px 16px 40px;-webkit-overflow-scrolling:touch}
#wfdev h2{margin:0 0 4px;font-size:20px}
#wfdev .wfbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
#wfdev .wfcx{background:rgba(127,110,90,.16);border-radius:14px;padding:12px 14px;margin:10px 0}
#wfdev .wfcx h3{margin:0 0 8px;font-size:14px;text-transform:uppercase;letter-spacing:.04em;opacity:.7}
#wfdev table{width:100%;border-collapse:collapse;font-size:14px}
#wfdev td{padding:3px 0}#wfdev td:last-child{text-align:right;font-weight:700}
#wfdev .wflog{font:11.5px/1.35 monospace;max-height:320px;overflow-y:auto;background:rgba(0,0,0,.08);border-radius:10px;padding:8px;white-space:pre-wrap;overflow-wrap:anywhere;-webkit-user-select:text;user-select:text}
#wfdev .wfbtns{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
#wfdev .wfbtns button{flex:1 1 auto}
.wfpb{margin:0 2px}
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
  var v=n.nodeValue,base;
  if(n.__wft!==undefined&&v===n.__wft)base=n.__wfo;
  else{base=v;n.__wfo=v}
  var o=trans(base,LANG);
  n.__wft=(o!==base)?o:undefined;
  if(o!==v)n.nodeValue=o}
var ATTRS=['placeholder','aria-label','title'];
function doAttr(e){
  ATTRS.forEach(function(a){
    if(!e.hasAttribute||!e.hasAttribute(a))return;
    var k='wfo_'+a,t=k+'_t',cur=e.getAttribute(a),base;
    if(e[t]!==undefined&&cur===e[t])base=e[k];
    else{base=cur;e[k]=cur}
    var o=trans(base,LANG);
    e[t]=(o!==base)?o:undefined;
    if(o!==cur)e.setAttribute(a,o)})}
function walk(root,fn,afn){
  if(root.nodeType===3){fn(root);return}
  if(root.nodeType!==1&&root.nodeType!==9&&root.nodeType!==11)return;
  if(root.nodeType===1){var tg=root.tagName;if(tg==='SCRIPT'||tg==='STYLE')return;afn(root)}
  var c=root.firstChild;while(c){walk(c,fn,afn);c=c.nextSibling}}
function applyAll(){
  BUSY=true;
  try{walk(document.body,doText,doAttr)}catch(e){}
  BUSY=false;
  document.documentElement.lang=LANG==='pt'?'pt-BR':LANG}
var MO=new MutationObserver(function(ms){
  if(BUSY){return}
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
  if(comb.paginas.length)combRender();if(window.wfPausaRender)window.wfPausaRender()}

/* ---------- Ajustes: idioma e atualizações ---------- */
function mk(h){var d=document.createElement('div');d.innerHTML=h;return d.firstChild}
var pn=document.querySelector('#sheet .spn'),ref=document.getElementById('srvnote');
var DEVON=false;try{DEVON=wfget('dev')==='1'}catch(e){}
function info(){fetch('/api/ytdlp').then(function(r){return r.json()}).then(function(j){
  var a=W&&W.versaoApp?W.versaoApp():'';
  var el=document.getElementById('wfv2');if(el)el.textContent='WaveFly '+(a?('v'+a):'')+' · yt-dlp '+(j.versao||'?')}).catch(function(){})}
if(pn){
  var g1=mk('<div class="g" id="wf-g-lang"><span class="l">Idioma / Language</span><div class="sg full">'+
    NAT.map(function(n){return '<button data-wflang="'+n[0]+'">'+n[1]+'</button>'}).join('')+'</div></div>');
  pn.insertBefore(g1,ref);
  g1.querySelectorAll('button').forEach(function(b){b.onclick=function(){setLang(b.dataset.wflang)};b.classList.toggle('on',b.dataset.wflang===LANG)});
  var g3=mk('<div class="g" id="wf-g-up"><span class="l">Atualizações</span><button class="rb" id="wfup"><span>Procurar atualizações</span></button><p class="wfver" id="wfv2"></p><div id="wfdevg" hidden><span class="l" style="margin-top:12px;display:block">Desenvolvedor</span><button class="rb" id="wfdevopen"><span>Painel do desenvolvedor</span></button><button class="t" id="wfdevoff" style="margin-top:4px">Esconder</button></div></div>');
  pn.insertBefore(g3,ref);
  g3.querySelector('#wfup').onclick=function(){
    if(W&&W.verificarAtualizacao)W.verificarAtualizacao();
    fetch('/api/ytdlp?forcar=1').then(function(r){return r.json()}).then(function(j){
      var m=j.resultado||'';
      if(m.indexOf('baixada')===0)toast(LANG==='en'?'yt-dlp updated. Restart the app to use it.':LANG==='es'?'yt-dlp actualizado. Reinicia la app para usarlo.':'yt-dlp atualizado. Reabra o app para usar.');
      else if(m.indexOf('erro')===0)toast(LANG==='en'?'Could not check yt-dlp now.':LANG==='es'?'No se pudo comprobar yt-dlp ahora.':'Não consegui verificar o yt-dlp agora.');
      else toast(LANG==='en'?'yt-dlp is up to date.':LANG==='es'?'yt-dlp está al día.':'yt-dlp está em dia.');
      info()}).catch(function(){})};
  info();
  /* 7 toques na linha de versão abrem o modo desenvolvedor */
  var tq=0,tt=0,vl=g3.querySelector('#wfv2'),dg=g3.querySelector('#wfdevg');
  dg.hidden=!DEVON;
  vl.addEventListener('click',function(){var n=Date.now();if(n-tt>1500)tq=0;tt=n;tq++;
    if(tq>=7){tq=0;DEVON=true;wfset('dev','1');dg.hidden=false;toast(LANG==='en'?'Developer mode on':LANG==='es'?'Modo desarrollador activado':'Modo desenvolvedor ativado')}});
  g3.querySelector('#wfdevoff').onclick=function(){DEVON=false;wfset('dev','');dg.hidden=true};
  g3.querySelector('#wfdevopen').onclick=function(){devAbrir()};
}

/* ---------- Pausar tudo (fila de downloads) ---------- */
var PAUSADO=false;
(function(){
  var bc=document.getElementById('bcanc');if(!bc)return;
  var bp=mk('<button class="t wfpb" id="bpausa">Pausar tudo</button>');bc.parentNode.insertBefore(bp,bc);
  function pinta(){bp.textContent=PAUSADO?T('Continuar'):T('Pausar tudo')}
  bp.onclick=function(){fetch('/api/pausa?v='+(PAUSADO?0:1)).then(function(r){return r.json()}).then(function(j){PAUSADO=!!j.pausado;pinta();try{tick()}catch(e){}}).catch(function(){})};
  function ler(){if(document.hidden)return;var f=document.getElementById('fila');if(f&&f.hidden&&!PAUSADO)return;
    fetch('/api/pausa').then(function(r){return r.json()}).then(function(j){if(!!j.pausado!==PAUSADO){PAUSADO=!!j.pausado}pinta()}).catch(function(){})}
  setInterval(ler,2500);ler();
  window.wfPausaRender=pinta;
})();

/* ---------- Painel do desenvolvedor ---------- */
var DEVT=null;
function aplicaRapido(){try{if(wfget('dev_rapido')==='1')fetch('/api/dev?rapido=1')}catch(e){}}
aplicaRapido();
function devAbrir(){
  if(document.getElementById('wfdev'))return;
  var d=mk('<div id="wfdev"><div class="wfbar"><h2>Desenvolvedor</h2><button class="t" id="wfdx">Fechar</button></div>'+
    '<div class="wfcx"><div class="wfrow"><span class="wft">Download mais rápido</span><label class="wfsw"><input type="checkbox" id="wfrap"><i></i></label></div>'+
    '<p class="note" id="wfmodo"></p><p class="note">Vale para downloads em MP3: converte uma música enquanto baixa a próxima e usa esperas curtas. Se o YouTube bloquear, volta sozinho ao ritmo normal.</p></div>'+
    '<div class="wfcx"><h3>Tempo médio por música</h3><table id="wftb"></table></div>'+
    '<div class="wfcx"><h3>Contagem</h3><table id="wfct"></table></div>'+
    '<div class="wfcx"><h3>Aparelho</h3><table id="wfap"></table></div>'+
    '<div class="wfcx"><h3>Registro</h3><div class="wflog" id="wflg"></div><div class="wfbtns"><button id="wfcp">Copiar registro</button><button id="wflp">Limpar</button></div></div></div>');
  document.body.appendChild(d);
  var sw=d.querySelector('#wfrap');
  sw.onchange=function(){wfset('dev_rapido',sw.checked?'1':'');fetch('/api/dev?rapido='+(sw.checked?1:0)).then(function(){devAtualiza()})};
  d.querySelector('#wfdx').onclick=function(){clearInterval(DEVT);DEVT=null;d.remove()};
  d.querySelector('#wflp').onclick=function(){fetch('/api/dev?limpar=1').then(function(){devAtualiza()})};
  d.querySelector('#wfcp').onclick=function(){var t=d.querySelector('#wflg').dataset.txt||'';
    try{if(W&&W.copiar){W.copiar(t);toast(T('Registro copiado'));return}}catch(e){}
    try{var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();toast(T('Registro copiado'))}catch(e){}};
  devAtualiza();DEVT=setInterval(devAtualiza,2000);
}
function lin(a,b){return '<tr><td>'+a+'</td><td>'+b+'</td></tr>'}
function devAtualiza(){
  var d=document.getElementById('wfdev');if(!d)return;
  fetch('/api/dev').then(function(r){return r.json()}).then(function(j){
    var sw=d.querySelector('#wfrap');sw.checked=!!j.rapido;
    var modo=j.freio?{pt:'Freio ativo: voltou ao ritmo normal por causa de um bloqueio.',en:'Brake on: back to normal speed because of a block.',es:'Freno activo: volvió al ritmo normal por un bloqueo.'}[LANG]:j.rapido?{pt:'Modo rápido em uso.',en:'Fast mode in use.',es:'Modo rápido en uso.'}[LANG]:{pt:'Modo normal.',en:'Normal mode.',es:'Modo normal.'}[LANG];
    var mm=d.querySelector('#wfmodo');mm.textContent=modo+(j.pausado?(' '+T('Downloads pausados.')):'');
    var m=j.medias||{};
    d.querySelector('#wftb').innerHTML=j.n?lin(T('Informações'),m.info+' s')+lin('Download',m.dl+' s')+lin(T('Conversão'),m.conv+' s')+lin(T('Espera'),m.espera+' s')+lin('Total',m.total+' s')+lin(T('Músicas por hora'),j.por_hora)+lin(T('Amostra'),j.n):'<tr><td>'+T('Sem medidas ainda. Baixe algumas músicas.')+'</td></tr>';
    var c=j.cont||{};
    d.querySelector('#wfct').innerHTML=lin(T('Concluídas'),j.ok)+lin(T('Falhas'),j.falha)+lin(T('Na fila'),c.fila||0)+lin('Baixando',c.baixando||0)+lin(T('Repetidas'),c.duplicada||0);
    var lg=(j.log||[]).map(function(x){return x.t+' ['+x.tipo+'] '+x.msg}).join('\n');
    var el=d.querySelector('#wflg');el.textContent=lg||T('Sem eventos.');el.dataset.txt=lg;
    var ap='';try{if(W&&W.info){var i=JSON.parse(W.info());ap=lin(T('Bateria'),i.bat+'%'+(i.carregando?' ⚡':''))+lin(T('Memória do app'),i.memMb+' MB')+lin(T('Rede'),i.rede)}}catch(e){}
    d.querySelector('#wfap').innerHTML=ap||lin('—','—')}).catch(function(){})}

/* ---------- Combina com você: quadrado de 4 sugestões ---------- */
var comb={paginas:[],idx:-1,busy:false,fim:false,box:null};
function combBox(){
  if(comb.box)return comb.box;
  var bgo=document.getElementById('bgo');if(!bgo)return null;
  var b=mk('<div id="wfcomb" hidden><div class="wfh"><h2>Combina com você</h2></div><div class="wfs">Sugestões a partir das suas músicas. Tudo fica neste aparelho.</div>'+
    '<div class="wfbox"><button class="wfnav" id="wfcl" aria-label="Anterior">‹</button><div class="wfgrid" id="wfgrid"></div><button class="wfnav" id="wfcr" aria-label="Próxima">›</button></div></div>');
  bgo.parentNode.insertBefore(b,bgo.nextSibling);
  b.querySelector('#wfcl').onclick=function(){if(comb.idx>0){comb.idx--;combRender()}};
  b.querySelector('#wfcr').onclick=function(){
    if(comb.idx+1<comb.paginas.length){comb.idx++;combRender();return}
    combMais()};
  comb.box=b;return b}
function combRender(){
  var b=combBox();if(!b)return;
  var g=b.querySelector('#wfgrid'),pg=comb.paginas[comb.idx];
  b.querySelector('#wfcl').disabled=comb.idx<=0;
  b.querySelector('#wfcr').disabled=comb.busy||(comb.fim&&comb.idx>=comb.paginas.length-1);
  if(!pg){g.innerHTML=comb.busy?'<div class="wfm">'+T('Procurando sugestões…')+'</div>':'';b.hidden=!comb.busy;return}
  b.hidden=false;
  g.innerHTML=pg.map(function(e){return '<div class="wfc" data-id="'+e.id+'"><div class="wfth"><img loading="lazy" src="https://i.ytimg.com/vi/'+e.id+'/mqdefault.jpg" alt=""><button type="button" class="pp" data-pv="'+e.id+'" aria-label="Ouvir">'+(typeof ic==='function'?ic('play',18):'▶')+'</button></div><div class="wfb"><div class="wfn"></div><div class="wfa"></div><button class="a wfd" data-wfd="'+e.id+'">'+T(e.baixada?'Adicionada':'Baixar')+'</button></div></div>'}).join('');
  [].forEach.call(g.querySelectorAll('.wfc'),function(c,i){c.querySelector('.wfn').textContent=pg[i].titulo;c.querySelector('.wfa').textContent=pg[i].canal||'';
    var bt=c.querySelector('.wfd');if(pg[i].baixada)bt.disabled=true});
  [].forEach.call(g.querySelectorAll('button[data-wfd]'),function(bt){bt.onclick=function(){
    var id=bt.dataset.wfd,e=pg.filter(function(x){return x.id===id})[0],t={};t[id]=e?e.titulo:'';
    bt.disabled=true;
    api('/api/add',{texto:'https://www.youtube.com/watch?v='+id,titulos:t}).then(function(r){
      try{toast(msgAdd(r))}catch(x){}
      if(e)e.baixada=true;bt.textContent=T('Adicionada');
      try{tick()}catch(x){}}).catch(function(err){bt.disabled=false;toast(err.message)})}})}
function combMais(){if(comb.busy)return;comb.busy=true;combRender();
  fetch('/api/combina').then(function(r){return r.json()}).then(function(j){
    comb.busy=false;
    if(j.itens&&j.itens.length){comb.paginas.push(j.itens);comb.idx=comb.paginas.length-1}
    else comb.fim=true;
    combRender()}).catch(function(){comb.busy=false;comb.fim=true;combRender()})}
setTimeout(function(){combBox();combMais()},2500);

setLang(LANG);
})();
</script>
"""


def bloco():
    js = JS_TPL.replace("__DICT__", json.dumps(DICT, ensure_ascii=False)).replace("__PAD__", json.dumps(PADROES, ensure_ascii=False))
    return CSS + js
