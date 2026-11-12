# -*- coding: utf-8 -*-
"""Idiomas (pt/en/es), ajustes do botão flutuante, atualizações e 'Combina com você'.
Injetado na página por wavefly_android.ajustar_html."""
import json

# (português, inglês, espanhol) - textos exatos da interface
DICT = [
    ("Ícone do app (teste)", "App icon (test)", "Icono de la app (prueba)"),
    ("Escolha um. O ícone na tela inicial pode levar alguns segundos para trocar.", "Pick one. The home screen icon may take a few seconds to change.", "Elige uno. El icono de la pantalla de inicio puede tardar unos segundos."),
    ("Ícone trocado. Pode levar alguns segundos.", "Icon changed. It may take a few seconds.", "Icono cambiado. Puede tardar unos segundos."),
    ("Padrão", "Default", "Predeterminado"), ("Fita", "Tape", "Cinta"), ("Fone", "Headphones", "Auriculares"), ("Nota", "Note", "Nota"),
    ("Tempo médio por música", "Average time per song", "Tiempo medio por canción"),
    ("Contagem", "Count", "Recuento"),
    ("Aparelho", "Device", "Dispositivo"),
    ("Registro", "Log", "Registro"),
    ("Vale para downloads em MP3: baixa e converte várias músicas ao mesmo tempo (até 3), com esperas curtas, e grava título e capa direto no arquivo. Se o YouTube bloquear, volta sozinho ao ritmo normal.", "Applies to MP3 downloads: downloads and converts several songs at once (up to 3), with short waits, and writes title and cover straight into the file. If YouTube blocks, it returns to the normal pace by itself.", "Vale para descargas en MP3: descarga y convierte varias canciones a la vez (hasta 3), con esperas cortas, y escribe título y portada en el archivo. Si YouTube bloquea, vuelve solo al ritmo normal."),
    ("Explorar", "Explore", "Explorar"),
    ("Descubra músicas e estilos novos. Toque para ouvir, sem baixar nada.", "Discover new music and styles. Tap to listen, nothing is downloaded.", "Descubre música y estilos nuevos. Toca para escuchar, sin descargar nada."),
    ("Descobrir", "Discover", "Descubrir"),
    ("Favoritas", "Favorites", "Favoritas"),
    ("Favorita", "Favorite", "Favorita"),
    ("Favoritar", "Favorite", "Favorita"),
    ("Carregar mais", "Load more", "Cargar más"),
    ("Carregando…", "Loading…", "Cargando…"),
    ("Só áudio", "Audio only", "Solo audio"),
    ("Ver vídeo", "Show video", "Ver vídeo"),
    ("Baixar todas", "Download all", "Descargar todas"),
    ("Selecionar", "Select", "Seleccionar"),
    ("Cancelar seleção", "Cancel selection", "Cancelar selección"),
    ("Selecionar tudo", "Select all", "Seleccionar todo"),
    ("Remover", "Remove", "Quitar"),
    ("Nenhuma favorita ainda. Toque no coração de uma música.", "No favorites yet. Tap the heart on a song.", "Aún no hay favoritas. Toca el corazón de una canción."),
    ("Nada encontrado agora. Tente de novo.", "Nothing found right now. Try again.", "No se encontró nada ahora. Inténtalo de nuevo."),
    ("Não foi possível reproduzir. Tente outra.", "Could not play. Try another one.", "No se pudo reproducir. Prueba otra."),
    ("Adicionada às favoritas", "Added to favorites", "Añadida a favoritas"),
    ("Removida das favoritas", "Removed from favorites", "Quitada de favoritas"),
    ("Removidas das favoritas", "Removed from favorites", "Quitadas de favoritas"),
    ("Adicionada à fila", "Added to queue", "Añadida a la cola"),
    ("Este vídeo ao vivo não pode ser transmitido.", "This live video cannot be streamed.", "Este vídeo en vivo no se puede transmitir."),
    ("Surpreenda-me", "Surprise me", "Sorpréndeme"),
    ("Rap e Hip-hop", "Rap & Hip-hop", "Rap y Hip-hop"),
    ("Eletrônica", "Electronic", "Electrónica"),
    ("Lo-fi e Chill", "Lo-fi & Chill", "Lo-fi y Chill"),
    ("Jazz e Blues", "Jazz & Blues", "Jazz y Blues"),
    ("Latina", "Latin", "Latina"),
    ("K-pop e J-pop", "K-pop & J-pop", "K-pop y J-pop"),
    ("Forró e Pagode", "Forró & Pagode", "Forró y Pagode"),
    ("Clássica", "Classical", "Clásica"),
    ("Do mundo", "World", "Del mundo"),
    ("MPB", "Brazilian music (MPB)", "MPB"),
    ("Sertanejo", "Sertanejo", "Sertanejo"),
    ("Reggae", "Reggae", "Reggae"),
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
    ("Ouvir prévia", "Preview", "Escuchar vista previa"), ("Link não reconhecido. Confira se ele está correto.", "Link not recognized. Check that it is correct.", "Enlace no reconocido. Comprueba que sea correcto."),
    ("Vídeo indisponível (privado, removido ou bloqueado).", "Video unavailable (private, removed or blocked).", "Vídeo no disponible (privado, eliminado o bloqueado)."),
    ("Vídeo com restrição de idade: não dá para baixar.", "Age-restricted video: cannot be downloaded.", "Vídeo con restricción de edad: no se puede descargar."),
    ("Título indisponível", "Title unavailable", "Título no disponible"),
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
#wfx{padding:12px 0 24px}
#wfx .wfxs{font-size:12.5px;opacity:.72;margin:2px 0 10px}
#wfx .wfxseg{display:flex;gap:6px;margin-bottom:10px}
#wfx .wfxseg button{flex:1;padding:10px 6px;border-radius:14px;font-weight:800;font-size:14px}
#wfx .wfxseg button.on{background:#c8581f!important;color:#fff!important}
#wfx .wfxch{display:flex;gap:6px;overflow-x:auto;padding:2px 0 10px;-webkit-overflow-scrolling:touch;scrollbar-width:none}
#wfx .wfxch::-webkit-scrollbar{display:none}
#wfx .wfxch button{flex:none;padding:8px 13px;border-radius:999px;font-size:13px;font-weight:700;white-space:nowrap;background:rgba(127,110,90,.16);color:inherit;border:0}
#wfx .wfxch button.on{background:#c8581f;color:#fff}
#wfx .wfxp{position:sticky;top:0;z-index:5;background:var(--t-bg,#efe4c9);border-radius:18px;padding:10px;margin-bottom:12px;box-shadow:0 6px 18px rgba(0,0,0,.28);border:2px solid rgba(127,110,90,.35)}
#wfx .wfxvw{position:relative;border-radius:12px;overflow:hidden;background:#000;aspect-ratio:16/9}
#wfx .wfxvw video{width:100%;height:100%;display:block;background:#000}
#wfx .wfxvw.so video{opacity:0}
#wfx .wfxvw .po{position:absolute;inset:0;background-size:cover;background-position:center;display:none}
#wfx .wfxvw.so .po{display:block}
#wfx .wfxld{position:absolute;inset:0;display:none;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:14px;background:rgba(0,0,0,.45)}
#wfx .wfxld.on{display:flex}
#wfx .wfxx{position:absolute;top:6px;right:6px;width:30px;height:30px;border-radius:50%;border:0;background:rgba(0,0,0,.55);color:#fff;font-size:15px;line-height:1;padding:0}
#wfx .wfxti{margin:8px 2px 2px}
#wfx .wfxti b{display:block;font-size:14.5px;line-height:1.25;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
#wfx .wfxti span{font-size:12px;opacity:.7}
#wfx .wfxbar{display:flex;align-items:center;gap:8px;font-size:11.5px;opacity:.85;margin:4px 2px}
#wfx .wfxbar input{flex:1;min-width:0}
#wfx .wfxct{display:flex;align-items:center;justify-content:center;gap:8px;margin:2px 0 6px}
#wfx .wfxct button{border:0;background:rgba(127,110,90,.2);color:inherit;border-radius:50%;width:42px;height:42px;padding:0;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800}
#wfx .wfxct button.big{width:56px;height:56px;background:#c8581f;color:#fff}
#wfx .wfxct svg{width:22px;height:22px;fill:currentColor}
#wfx .wfxac{display:flex;gap:6px;flex-wrap:wrap}
#wfx .wfxac button{flex:1 1 auto;padding:9px 10px;font-size:13px;border-radius:12px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:6px}
#wfx .wfxac svg,#wfx .wfxr svg{width:18px;height:18px}
#wfx .wfxr{display:flex;gap:10px;align-items:center;padding:7px;border-radius:14px;background:rgba(127,110,90,.12);margin-bottom:8px}
#wfx .wfxr.on{outline:2px solid #c8581f}
#wfx .wfxr .th{position:relative;flex:none;width:104px;aspect-ratio:16/9;border-radius:9px;overflow:hidden;background:rgba(0,0,0,.25)}
#wfx .wfxr .th img{width:100%;height:100%;object-fit:cover;display:block}
#wfx .wfxr .th i{position:absolute;right:3px;bottom:3px;background:rgba(0,0,0,.72);color:#fff;font:700 10.5px/1 sans-serif;padding:2px 4px;border-radius:4px}
#wfx .wfxr .tx{flex:1;min-width:0;cursor:pointer}
#wfx .wfxr .tx b{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:13.5px;line-height:1.25}
#wfx .wfxr .tx span{display:block;font-size:11.5px;opacity:.7;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}
#wfx .wfxr .bt{flex:none;display:flex;flex-direction:column;gap:6px}
#wfx .wfxr .bt button{width:36px;height:36px;padding:0;border-radius:50%;border:0;background:rgba(127,110,90,.2);color:inherit;display:flex;align-items:center;justify-content:center}
#wfx .wfxr .bt button.f{color:#d23b3b}
#wfx .wfxr .bt button[disabled]{opacity:.4}
#wfx .wfxr input[type=checkbox]{flex:none;width:22px;height:22px}
#wfx .wfxm{display:block;width:100%;padding:11px;border-radius:14px;font-weight:700;margin:6px 0}
#wfx .wfxe{text-align:center;opacity:.75;font-size:13.5px;padding:24px 8px}
#wfx .wfxfb{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
#wfx .wfxfb button{flex:1 1 auto;padding:9px 8px;border-radius:12px;font-weight:700;font-size:13px}
#wfdev{position:fixed;inset:0;z-index:99998;background:var(--t-bg,#e8dcc2);color:#3b2314;overflow-y:auto;padding:16px 16px 40px;-webkit-overflow-scrolling:touch}
#wfdev h2{margin:0 0 4px;font-size:20px}
#wfdev .wfbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
#wfdev .wfcx{background:rgba(127,110,90,.16);border-radius:14px;padding:12px 14px;margin:10px 0}
#wfdev .wfcx h3{margin:0 0 8px;font-size:14px;text-transform:uppercase;letter-spacing:.04em;color:#4a2a14;opacity:.9}
#wfdev .wfbar .t,#wfdev .t{color:#8f3407!important;font-weight:800;font-size:15px}
#wfdev .note,#wfdev .wfcx p{color:#4a3424!important;opacity:1!important}
#wfdev .wfbtns button{color:#6b2a05!important;font-weight:800}
#wfdev table{width:100%;border-collapse:collapse;font-size:14px}
#wfdev td{padding:3px 0}#wfdev td:last-child{text-align:right;font-weight:700}
#wfdev .wflog{font:11.5px/1.35 monospace;max-height:320px;overflow-y:auto;background:rgba(0,0,0,.08);border-radius:10px;padding:8px;white-space:pre-wrap;overflow-wrap:anywhere;-webkit-user-select:text;user-select:text}
#wfdev .wficons{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
#wfdev .wfic{display:flex;flex-direction:column;align-items:center;gap:4px;padding:6px 2px;border-radius:14px;border:2px solid transparent;background:rgba(127,110,90,.12);color:#3b2314;font-size:12px;font-weight:700}
#wfdev .wfic.on{border-color:#c8581f}
#wfdev .wfic span{display:block;width:54px;height:54px;border-radius:50%;overflow:hidden}
#wfdev .wfic svg{width:100%;height:100%;display:block}
#wfdev .wfic em{font-style:normal}
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
  if(window.exRefaz)window.exRefaz();if(window.wfPausaRender)window.wfPausaRender()}

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
    '<p class="note" id="wfmodo"></p><p class="note">Vale para downloads em MP3: baixa e converte várias músicas ao mesmo tempo (até 3), com esperas curtas, e grava título e capa direto no arquivo. Se o YouTube bloquear, volta sozinho ao ritmo normal.</p></div>'+
    '<div class="wfcx"><h3>Ícone do app (teste)</h3><div class="wficons" id="wficons"></div><p class="note">Escolha um. O ícone na tela inicial pode levar alguns segundos para trocar.</p></div>'+
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
  (function(){var ic=[{"n": "Padrão", "s": "<svg viewBox=\"18 18 72 72\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"108\" height=\"108\" fill=\"#D9692A\"/><path d=\"M30,46 L30,62\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\"/><path d=\"M42,38 L42,70\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\"/><path d=\"M54,30 L54,78\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\"/><path d=\"M66,38 L66,70\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\"/><path d=\"M78,46 L78,62\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\"/></svg>"}, {"n": "Fita", "s": "<svg viewBox=\"18 18 72 72\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"108\" height=\"108\" fill=\"#F3E3C3\"/><path d=\"M32,38 h44 a4,4 0 0 1 4,4 v26 a4,4 0 0 1 -4,4 h-44 a4,4 0 0 1 -4,-4 v-26 a4,4 0 0 1 4,-4z\" fill=\"#E8873A\" stroke=\"#4A2A17\" stroke-width=\"3\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M38,47 h32 a6,6 0 0 1 0,12 h-32 a6,6 0 0 1 0,-12z\" fill=\"#2A1A10\"/><circle cx=\"46\" cy=\"53\" r=\"4.2\" fill=\"#F3E3C3\"/><circle cx=\"62\" cy=\"53\" r=\"4.2\" fill=\"#F3E3C3\"/><path d=\"M44,68 h20 l3,5 h-26z\" fill=\"#4A2A17\"/></svg>"}, {"n": "Fone", "s": "<svg viewBox=\"18 18 72 72\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"108\" height=\"108\" fill=\"#1F6F78\"/><path d=\"M32,60 C32,34 76,34 76,60\" fill=\"none\" stroke=\"#FBF3E1\" stroke-width=\"6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M29,56 h8 a2,2 0 0 1 2,2 v14 a2,2 0 0 1 -2,2 h-6 a4,4 0 0 1 -4,-4 v-10 a4,4 0 0 1 4,-4z\" fill=\"#FBF3E1\"/><path d=\"M79,56 h-8 a2,2 0 0 0 -2,2 v14 a2,2 0 0 0 2,2 h6 a4,4 0 0 0 4,-4 v-10 a4,4 0 0 0 -4,-4z\" fill=\"#FBF3E1\"/></svg>"}, {"n": "Nota", "s": "<svg viewBox=\"18 18 72 72\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"108\" height=\"108\" fill=\"#16283F\"/><path d=\"M44,40 L66,35 L66,64\" fill=\"none\" stroke=\"#F5C14B\" stroke-width=\"5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M44,40 L44,68\" fill=\"none\" stroke=\"#F5C14B\" stroke-width=\"5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M44,70 a7,5.5 -20 1 1 -0.1,0z\" fill=\"#F5C14B\"/><path d=\"M66,66 a7,5.5 -20 1 1 -0.1,0z\" fill=\"#F5C14B\"/></svg>"}, {"n": "Play", "s": "<svg viewBox=\"18 18 72 72\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"108\" height=\"108\" fill=\"#3B2314\"/><path d=\"M54,32 a22,22 0 1 1 -0.1,0z\" fill=\"none\" stroke=\"#F2A154\" stroke-width=\"4.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M48,43 L48,65 L66,54z\" fill=\"#F2A154\" stroke=\"#F2A154\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg>"}, {"n": "Onda", "s": "<svg viewBox=\"18 18 72 72\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"108\" height=\"108\" fill=\"#C8581F\"/><path d=\"M26,56 C36,34 46,34 54,52 S72,72 82,48\" fill=\"none\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M30,70 C38,58 46,58 54,68 S68,78 78,64\" fill=\"none\" stroke=\"#FBF3E1\" stroke-width=\"3.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg>"}],box=d.querySelector('#wficons'),at=0;try{if(W&&W.icone)at=W.icone()}catch(e){}
    box.innerHTML=ic.map(function(x,i){return '<button type="button" class="wfic'+(i===at?' on':'')+'" data-i="'+i+'"><span>'+x.s+'</span><em>'+x.n+'</em></button>'}).join('');
    box.onclick=function(ev){var b=ev.target.closest('button');if(!b)return;try{if(W&&W.setIcone)W.setIcone(+b.dataset.i)}catch(e){}
      [].forEach.call(box.children,function(c){c.classList.toggle('on',c===b)});toast(T('Ícone trocado. Pode levar alguns segundos.'))}})();
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

/* ---------- Explorar: descobrir músicas novas, transmitir sem baixar, favoritas ---------- */
var EX={g:'surpresa',pag:0,seed:String(Date.now()%100000),lista:[],busy:false,mais:true,modo:'d',favs:[],sel:{},selOn:false,
  cur:null,fila:[],idx:-1,vid:(function(){try{return wfget('exvid')!=='0'}catch(e){return true}})(),au:null,bg:false,gens:null,tentou:0,quer:false,montado:false,ini:false};
var EXI={
  play:'<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>',
  pause:'<svg viewBox="0 0 24 24"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>',
  prev:'<svg viewBox="0 0 24 24"><path d="M6 6h2v12H6zM9.5 12L18 18V6z"/></svg>',
  next:'<svg viewBox="0 0 24 24"><path d="M16 6h2v12h-2zM6 18l8.5-6L6 6z"/></svg>',
  heart:'<svg viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M12 20.3l-1.1-1C6 15 3 12.2 3 8.8 3 6.1 5.1 4 7.8 4c1.5 0 3 .7 4.2 1.9C13.2 4.7 14.7 4 16.2 4 18.9 4 21 6.1 21 8.8c0 3.4-3 6.2-7.9 10.5z"/></svg>',
  heartf:'<svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 20.3l-1.1-1C6 15 3 12.2 3 8.8 3 6.1 5.1 4 7.8 4c1.5 0 3 .7 4.2 1.9C13.2 4.7 14.7 4 16.2 4 18.9 4 21 6.1 21 8.8c0 3.4-3 6.2-7.9 10.5z"/></svg>',
  down:'<svg viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M12 4v11m0 0l-4.5-4.5M12 15l4.5-4.5M5 20h14"/></svg>'};
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function exFmt(s){s=Math.max(0,Math.round(s||0));var m=Math.floor(s/60),x=s%60;return m+':'+(x<10?'0':'')+x}
function exQ(id){return document.getElementById(id)}
function exEhFav(id){return EX.favs.some(function(f){return f.id===id})}
function exView(){return EX.modo==='f'?EX.favs:EX.lista}
function exMedia(){return EX.bg&&EX.au?EX.au:EX.v}
function exMonta(){
  if(EX.montado)return true;
  var sec=exQ('v-explorar');if(!sec)return false;
  sec.innerHTML='<div id="wfx"><div class="wfxs">Descubra músicas e estilos novos. Toque para ouvir, sem baixar nada.</div>'+
   '<div class="wfxp" id="wfxp" hidden><div class="wfxvw" id="wfxvw"><video id="wfxv" playsinline webkit-playsinline preload="auto"></video><div class="po" id="wfxpo"></div><div class="wfxld" id="wfxld"></div><button class="wfxx" id="wfxx" aria-label="Fechar">✕</button></div>'+
   '<div class="wfxti"><b id="wfxt"></b><span id="wfxc"></span></div>'+
   '<div class="wfxbar"><span id="wfxa">0:00</span><input type="range" id="wfxsk" min="0" max="1000" value="0"><span id="wfxb">0:00</span></div>'+
   '<div class="wfxct"><button id="wfxpv" aria-label="Anterior">'+EXI.prev+'</button><button id="wfxb10">−10</button><button class="big" id="wfxpp" aria-label="Tocar">'+EXI.play+'</button><button id="wfxf10">+10</button><button id="wfxnx" aria-label="Próxima">'+EXI.next+'</button></div>'+
   '<div class="wfxac"><button id="wfxfv"></button><button id="wfxdl">'+EXI.down+'<span>Baixar</span></button><button id="wfxmd"></button></div></div>'+
   '<div class="wfxseg"><button id="wfxm1" class="on">Descobrir</button><button id="wfxm2">Favoritas</button></div>'+
   '<div id="wfxd"><div class="wfxch" id="wfxch"></div></div><div id="wfxf" hidden></div><div id="wfxl"></div><button class="wfxm" id="wfxmais" hidden>Carregar mais</button></div>';
  EX.v=exQ('wfxv');
  var v=EX.v;
  v.addEventListener('playing',function(){exLd('');exUI()});
  v.addEventListener('waiting',function(){if(!EX.bg)exLd(T('Carregando…'))});
  v.addEventListener('pause',function(){exUI();if(document.hidden&&EX.quer&&!v.ended)exParaFundo()});
  v.addEventListener('play',function(){EX.quer=true;exUI()});
  v.addEventListener('ended',function(){exProx(1,true)});
  v.addEventListener('error',function(){exErro()});
  v.addEventListener('timeupdate',exProg);
  v.addEventListener('loadedmetadata',exProg);
  exQ('wfxx').onclick=exFecha;
  exQ('wfxpp').onclick=function(){exCmd('toggle')};
  exQ('wfxpv').onclick=function(){exProx(-1)};
  exQ('wfxnx').onclick=function(){exProx(1)};
  exQ('wfxb10').onclick=function(){exPula(-10)};
  exQ('wfxf10').onclick=function(){exPula(10)};
  exQ('wfxsk').onchange=function(){var m=exMedia(),d=m&&m.duration;if(d&&isFinite(d))m.currentTime=d*this.value/1000};
  exQ('wfxfv').onclick=function(){if(EX.cur)exFav(EX.cur)};
  exQ('wfxdl').onclick=function(){if(EX.cur)exBaixar([EX.cur])};
  exQ('wfxmd').onclick=function(){EX.vid=!EX.vid;try{wfset('exvid',EX.vid?'1':'0')}catch(e){}exModoUI();if(EX.cur){var m=exMedia(),t=m?m.currentTime:0;EX.retomar=t;exCarrega(false)}};
  exQ('wfxm1').onclick=function(){exModo('d')};
  exQ('wfxm2').onclick=function(){exModo('f')};
  exQ('wfxmais').onclick=function(){exMais()};
  exQ('wfxl').addEventListener('click',exCliqueLista);
  exQ('wfxf').addEventListener('click',exCliqueFav);
  EX.montado=true;exModoUI();return true}
function exLd(t){var e=exQ('wfxld');if(!e)return;e.textContent=t||'';e.classList.toggle('on',!!t)}
function exModoUI(){var b=exQ('wfxmd');if(b)b.textContent=EX.vid?T('Só áudio'):T('Ver vídeo');var w=exQ('wfxvw');if(w)w.classList.toggle('so',!EX.vid)}
function exUI(){
  var m=exMedia(),tocando=!!(m&&!m.paused&&!m.ended);
  var pp=exQ('wfxpp');if(pp)pp.innerHTML=tocando?EXI.pause:EXI.play;
  var f=exQ('wfxfv');if(f&&EX.cur){var on=exEhFav(EX.cur.id);f.innerHTML=(on?EXI.heartf:EXI.heart)+'<span>'+T(on?'Favorita':'Favoritar')+'</span>';f.style.color=on?'#d23b3b':''}
  [].forEach.call(document.querySelectorAll('#wfxl .wfxr,#wfxf .wfxr'),function(r){r.classList.toggle('on',!!EX.cur&&r.dataset.id===EX.cur.id)})}
function exProg(){
  var m=exMedia();if(!m)return;var d=m.duration,t=m.currentTime;
  if(exQ('wfxa'))exQ('wfxa').textContent=exFmt(t);
  if(d&&isFinite(d)){if(exQ('wfxb'))exQ('wfxb').textContent=exFmt(d);var sk=exQ('wfxsk');if(sk&&document.activeElement!==sk)sk.value=Math.round(t/d*1000)}}
function exParaBib(){try{var a=document.getElementById('au');if(a&&!a.paused)a.pause()}catch(e){}try{if(typeof pvStop==='function')pvStop()}catch(e){}}
function exMostra(){
  var e=EX.cur;exQ('wfxp').hidden=false;exQ('wfxt').textContent=e.titulo||'';exQ('wfxc').textContent=e.canal||'';
  exQ('wfxpo').style.backgroundImage='url(https://i.ytimg.com/vi/'+e.id+'/hqdefault.jpg)';
  exQ('wfxsk').value=0;exQ('wfxa').textContent='0:00';exQ('wfxb').textContent=e.dur?exFmt(e.dur):'0:00';exUI();
  try{window.scrollTo(0,0)}catch(x){}}
function exPlay(i,lista){
  var L=lista||exView(),e=L[i];if(!e)return;
  EX.fila=L;EX.idx=i;EX.cur=e;EX.tentou=0;EX.retomar=0;EX.quer=true;exFim();exMostra();exCarrega(false)}
function exFim(){if(EX.au){try{EX.au.pause()}catch(e){}EX.au=null}EX.bg=false}
function exCarrega(fresh){
  var e=EX.cur;exFim();exLd(T('Carregando…'));exParaBib();
  fetch('/api/exstream?id='+encodeURIComponent(e.id)+'&v='+(EX.vid?1:0)+(fresh?'&f=1':'')).then(function(r){return r.json()}).then(function(j){
    if(EX.cur!==e)return;
    if(j.erro||!j.url){exLd('');toast(T(j.erro||'Não foi possível reproduzir. Tente outra.'));exUI();return}
    if(j.dur&&!e.dur){e.dur=j.dur;exQ('wfxb').textContent=exFmt(j.dur)}
    var v=EX.v,r0=EX.retomar||0;EX.retomar=0;
    v.src=j.url;v.load();
    if(r0)v.addEventListener('loadedmetadata',function(){try{v.currentTime=r0}catch(x){}},{once:true});
    var p=v.play();if(p&&p.catch)p.catch(function(){exLd('');exUI()})
  }).catch(function(){if(EX.cur!==e)return;exLd('');toast(T('Não foi possível reproduzir. Tente outra.'))})}
function exErro(){
  if(!EX.cur||!EX.v.src||EX.bg)return;
  if(EX.tentou<1){EX.tentou++;EX.retomar=EX.v.currentTime||0;exCarrega(true);return}
  exLd('');toast(T('Não foi possível reproduzir. Tente outra.'));exUI()}
function exProx(d,auto){
  var L=EX.fila||[],i=EX.idx+d;
  if(i<0||i>=L.length){
    if(d>0&&L===EX.lista&&EX.mais&&!EX.busy){exMais(function(){if(EX.idx+1<EX.lista.length)exPlay(EX.idx+1,EX.lista)});return}
    if(auto)exUI();return}
  exPlay(i,L)}
function exPula(s){var m=exMedia();if(!m)return;var d=m.duration;var t=(m.currentTime||0)+s;if(t<0)t=0;if(d&&isFinite(d)&&t>d)t=d;m.currentTime=t}
function exFecha(){
  if(EX.v){try{EX.v.pause()}catch(e){}EX.v.removeAttribute('src');try{EX.v.load()}catch(e){}}
  exFim();EX.cur=null;EX.quer=false;var p=exQ('wfxp');if(p)p.hidden=true;exUI();exRep()}
function exParaFundo(){
  /* o sistema pausou o vídeo ao sair do app: segue só com o áudio */
  try{
    var v=EX.v,t=v.currentTime||0,src=v.currentSrc||v.src;if(!src)return;
    var a=new Audio();a.src=src;EX.au=a;EX.bg=true;
    a.addEventListener('loadedmetadata',function(){try{a.currentTime=t}catch(x){}var p=a.play();if(p&&p.catch)p.catch(function(){})},{once:true});
    a.addEventListener('ended',function(){EX.bg=false;exProx(1,true)});
    a.addEventListener('timeupdate',exProg);
    a.addEventListener('error',function(){});
    a.load()}catch(e){}}
function exVolta(){
  if(!EX.bg||!EX.au)return;
  var a=EX.au,t=a.currentTime||0,tocando=!a.paused&&!a.ended;
  EX.au=null;EX.bg=false;try{a.pause()}catch(e){}
  var v=EX.v;v.src=a.src;v.load();
  v.addEventListener('loadedmetadata',function(){try{v.currentTime=t}catch(x){}if(tocando){var p=v.play();if(p&&p.catch)p.catch(function(){})}},{once:true})}
document.addEventListener('visibilitychange',function(){
  if(!EX.cur||!EX.montado)return;
  if(document.hidden){if(EX.v&&!EX.v.paused&&!EX.bg)exParaFundo()}else exVolta()});
/* comandos vindos da notificação */
(function(){var o=window.wfCmd;window.wfCmd=function(c){
  if(EX.cur){exCmd(c);return}
  if(o)o(c)}})();
function exCmd(c){
  var m=exMedia();
  if(c==='play'){if(m&&m.paused)m.play()}
  else if(c==='pause'){if(m&&!m.paused)m.pause()}
  else if(c==='toggle'){if(m){if(m.paused)m.play();else m.pause()}}
  else if(c==='next')exProx(1);
  else if(c==='prev')exProx(-1);
  else if(c==='stop')exFecha();
  else if(c==='fav'){if(EX.cur)exFav(EX.cur)}
  else if(c.indexOf('seek:')===0){var ms=parseInt(c.slice(5),10);if(m&&isFinite(ms))m.currentTime=ms/1000}
  setTimeout(exRep,200)}
function exRep(){
  try{
    if(!window.WF||!WF.player)return false;
    if(!EX.cur){return false}
    var m=exMedia(),toc=!!(m&&!m.paused&&!m.ended);
    var pos=m&&isFinite(m.currentTime)?Math.round(m.currentTime*1000):0,dur=m&&isFinite(m.duration)?Math.round(m.duration*1000):0;
    if(WF.playerX)WF.playerX(1,exEhFav(EX.cur.id)?1:0);
    WF.player(1,toc?1:0,0,EX.cur.titulo||'',EX.cur.canal||'',pos,dur,'yt:'+EX.cur.id);
    return true}catch(e){return false}}
(function(){var o=window.wfRep;window.wfRep=function(){
  if(EX.cur){exRep();return}
  try{if(window.WF&&WF.playerX)WF.playerX(0,0)}catch(e){}
  if(o)o()}})();
/* ---------- lista ---------- */
function exRow(e,i,sel){
  var fav=exEhFav(e.id);
  return '<div class="wfxr" data-id="'+esc(e.id)+'" data-i="'+i+'">'+
   (sel?'<input type="checkbox" data-act="sel" '+(EX.sel[e.id]?'checked':'')+'>':'')+
   '<div class="th" data-act="play"><img loading="lazy" decoding="async" src="https://i.ytimg.com/vi/'+esc(e.id)+'/mqdefault.jpg" alt="">'+(e.dur?'<i>'+exFmt(e.dur)+'</i>':'')+'</div>'+
   '<div class="tx" data-act="play"><b>'+esc(e.titulo)+'</b><span>'+esc(e.canal||'')+'</span></div>'+
   (sel?'':'<div class="bt"><button class="'+(fav?'f':'')+'" data-act="fav" aria-label="Favoritar">'+(fav?EXI.heartf:EXI.heart)+'</button><button data-act="dl" aria-label="Baixar">'+EXI.down+'</button></div>')+'</div>'}
function exDesenha(){
  var L=exQ('wfxl');if(!L)return;
  var arr=exView(),sel=EX.modo==='f'&&EX.selOn;
  if(!arr.length){
    L.innerHTML='<div class="wfxe">'+esc(EX.modo==='f'?T('Nenhuma favorita ainda. Toque no coração de uma música.'):(EX.busy?T('Carregando…'):T('Nada encontrado agora. Tente de novo.')))+'</div>'}
  else L.innerHTML=arr.map(function(e,i){return exRow(e,i,sel)}).join('');
  var mb=exQ('wfxmais');mb.hidden=EX.modo!=='d'||!EX.mais||!EX.lista.length;mb.textContent=EX.busy?T('Carregando…'):T('Carregar mais');
  exUI()}
function exCliqueLista(ev){
  var el=ev.target.closest('[data-act]');if(!el)return;
  var r=el.closest('.wfxr');if(!r)return;var i=+r.dataset.i,arr=exView(),e=arr[i];if(!e)return;
  var a=el.dataset.act;
  if(a==='play')exPlay(i,arr);
  else if(a==='fav')exFav(e);
  else if(a==='dl')exBaixar([e]);
  else if(a==='sel'){if(el.checked)EX.sel[e.id]=1;else delete EX.sel[e.id];exFavBarra()}}
function exCliqueFav(ev){
  var b=ev.target.closest('button');if(!b)return;var a=b.dataset.a,ids=Object.keys(EX.sel);
  if(a==='sel'){EX.selOn=!EX.selOn;EX.sel={};exFavDesenha();exDesenha()}
  else if(a==='all'){EX.favs.forEach(function(f){EX.sel[f.id]=1});exFavDesenha();exDesenha()}
  else if(a==='dlall'){exBaixar(EX.favs)}
  else if(a==='dlsel'){exBaixar(EX.favs.filter(function(f){return EX.sel[f.id]}))}
  else if(a==='del'){if(!ids.length)return;
    fetch('/api/fav?del='+encodeURIComponent(ids.join(','))).then(function(r){return r.json()}).then(function(j){EX.favs=j.itens||[];EX.sel={};toast(T('Removidas das favoritas'));exFavDesenha();exDesenha();exRep()})}}
function exFavBarra(){var n=Object.keys(EX.sel).length;var a=exQ('wfxf').querySelector('[data-a=dlsel]'),d=exQ('wfxf').querySelector('[data-a=del]');if(a)a.textContent=T('Baixar')+' ('+n+')';if(d)d.textContent=T('Remover')+' ('+n+')'}
function exFavDesenha(){
  var f=exQ('wfxf');if(!f)return;
  if(!EX.favs.length){f.innerHTML='';return}
  f.innerHTML='<div class="wfxfb"><button data-a="dlall">'+esc(T('Baixar todas'))+'</button><button data-a="sel">'+esc(T(EX.selOn?'Cancelar seleção':'Selecionar'))+'</button>'+
    (EX.selOn?'<button data-a="all">'+esc(T('Selecionar tudo'))+'</button><button data-a="dlsel"></button><button data-a="del"></button>':'')+'</div>';
  exFavBarra()}
function exModo(m){
  EX.modo=m;exQ('wfxm1').classList.toggle('on',m==='d');exQ('wfxm2').classList.toggle('on',m==='f');
  exQ('wfxd').hidden=m!=='d';exQ('wfxf').hidden=m!=='f';
  if(m==='f'){EX.selOn=false;EX.sel={};exFavDesenha()}
  exDesenha()}
function exFav(e){
  var on=exEhFav(e.id),u=on?'/api/fav?del='+encodeURIComponent(e.id):'/api/fav?add='+encodeURIComponent(e.id)+'&t='+encodeURIComponent(e.titulo||'')+'&c='+encodeURIComponent(e.canal||'')+'&d='+(e.dur||0);
  if(on)EX.favs=EX.favs.filter(function(f){return f.id!==e.id});else EX.favs.unshift({id:e.id,titulo:e.titulo,canal:e.canal,dur:e.dur||0});
  toast(T(on?'Removida das favoritas':'Adicionada às favoritas'));
  exFavDesenha();exDesenha();exRep();
  fetch(u).then(function(r){return r.json()}).then(function(j){if(j.itens)EX.favs=j.itens;exFavDesenha();exDesenha()}).catch(function(){})}
function exBaixar(arr){
  if(!arr||!arr.length)return;
  var t={};arr.forEach(function(e){t[e.id]=e.titulo||''});
  var txt=arr.map(function(e){return 'https://www.youtube.com/watch?v='+e.id}).join('\n');
  api('/api/add',{texto:txt,titulos:t}).then(function(r){try{toast(msgAdd(r))}catch(x){toast(T('Adicionada à fila'))}try{tick()}catch(x){}}).catch(function(err){toast(err.message)})}
function exCarregaLista(reset,cb){
  if(EX.busy)return;
  if(reset){EX.lista=[];EX.pag=0;EX.mais=true;EX.seed=String(Date.now()%100000)}
  EX.busy=true;exDesenha();
  fetch('/api/ex?g='+encodeURIComponent(EX.g)+'&p='+EX.pag+'&s='+EX.seed).then(function(r){return r.json()}).then(function(j){
    EX.busy=false;
    var vistos={};EX.lista.forEach(function(x){vistos[x.id]=1});
    (j.itens||[]).forEach(function(x){if(!vistos[x.id]){vistos[x.id]=1;EX.lista.push(x)}});
    EX.mais=!!j.mais&&!!(j.itens||[]).length;
    if(j.erro&&!EX.lista.length)toast(j.erro);
    EX.pag++;exDesenha();if(cb)cb()}).catch(function(){EX.busy=false;EX.mais=false;exDesenha();toast(T('Nada encontrado agora. Tente de novo.'))})}
function exMais(cb){if(EX.g==='surpresa'||EX.pag>0)exCarregaLista(false,cb);else exCarregaLista(false,cb)}
window.exRefaz=function(){try{if(EX.montado){exModoUI();exChips();exFavDesenha();exDesenha()}}catch(e){}};
function exChips(){
  var c=exQ('wfxch');if(!c||!EX.gens)return;
  c.innerHTML=EX.gens.map(function(g){return '<button data-g="'+esc(g.k)+'" class="'+(g.k===EX.g?'on':'')+'">'+esc(T(g.t))+'</button>'}).join('');
  c.onclick=function(ev){var b=ev.target.closest('button');if(!b)return;EX.g=b.dataset.g;exChips();exCarregaLista(true)}}
function exAbrir(){
  if(!exMonta())return;
  fetch('/api/fav').then(function(r){return r.json()}).then(function(j){EX.favs=j.itens||[];exFavDesenha();exDesenha()}).catch(function(){});
  if(!EX.ini){EX.ini=true;
    fetch('/api/ex?generos=1').then(function(r){return r.json()}).then(function(j){EX.gens=j.generos||[];exChips()}).catch(function(){});
    exCarregaLista(true)}}
(function(){var o=window.go;if(typeof go==='function'){var og=go;go=function(t){og(t);if(t==='explorar')exAbrir()}}})();
document.addEventListener('click',function(ev){var a=ev.target.closest&&ev.target.closest('.tabs a[data-go=explorar]');if(a)setTimeout(exAbrir,0)},true);

setLang(LANG);
})();
</script>
"""


def bloco():
    js = JS_TPL.replace("__DICT__", json.dumps(DICT, ensure_ascii=False)).replace("__PAD__", json.dumps(PADROES, ensure_ascii=False))
    return CSS + js
