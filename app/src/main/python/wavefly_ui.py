# -*- coding: utf-8 -*-
"""Idiomas (pt/en/es), ajustes do botão flutuante, atualizações e 'Combina com você'.
Injetado na página por wavefly_android.ajustar_html."""
import json

# (português, inglês, espanhol) - textos exatos da interface
DICT = [
    ("Transmissão ao vivo não dá para baixar", "Live streams cannot be downloaded", "Las transmisiones en vivo no se pueden descargar"),
    ("Falhou depois de várias tentativas. Use “Tentar de novo”.", "Failed after several attempts. Use “Retry”.", "Falló tras varios intentos. Usa “Reintentar”."),
    ("Tentar de novo as falhas", "Retry failed ones", "Reintentar las fallidas"),
    ("Comparação do lote", "Batch comparison", "Comparación del lote"),
    ("Rápido", "Fast", "Rápido"),
    ("Normal", "Normal", "Normal"),
    ("músicas", "songs", "canciones"),
    ("Cassete", "Cassette", "Casete"), ("Onda W", "W wave", "Onda W"), ("Vinil", "Vinyl", "Vinilo"), ("Avião", "Paper plane", "Avión de papel"),
    ("Ajustes do modo rápido", "Fast mode settings", "Ajustes del modo rápido"),
    ("Downloads ao mesmo tempo", "Simultaneous downloads", "Descargas simultáneas"),
    ("Conversões ao mesmo tempo", "Simultaneous conversions", "Conversiones simultáneas"),
    ("Leitura leve de informações", "Light info reading", "Lectura ligera de información"),
    ("Mais simultâneas = mais rápido, mas esquenta mais o celular e aumenta o risco de bloqueio do YouTube. Se bloquear, o freio automático volta ao ritmo normal.", "More at once = faster, but the phone gets hotter and YouTube may block more easily. If it blocks, the automatic brake returns to normal pace.", "Más a la vez = más rápido, pero el teléfono se calienta más y YouTube puede bloquear. Si bloquea, el freno automático vuelve al ritmo normal."),
    ("Ícone do app (teste)", "App icon (test)", "Icono de la app (prueba)"),
    ("Escolha um. O ícone na tela inicial pode levar alguns segundos para trocar.", "Pick one. The home screen icon may take a few seconds to change.", "Elige uno. El icono de la pantalla de inicio puede tardar unos segundos."),
    ("Ícone trocado. Pode levar alguns segundos.", "Icon changed. It may take a few seconds.", "Icono cambiado. Puede tardar unos segundos."),
    ("Padrão", "Default", "Predeterminado"), ("Fita", "Tape", "Cinta"), ("Fone", "Headphones", "Auriculares"), ("Nota", "Note", "Nota"),
    ("Tempo médio por música", "Average time per song", "Tiempo medio por canción"),
    ("Contagem", "Count", "Recuento"),
    ("Aparelho", "Device", "Dispositivo"),
    ("Registro", "Log", "Registro"),
    ("Vale para downloads em MP3: baixa e converte várias músicas ao mesmo tempo (você escolhe quantas), com esperas curtas, e grava título e capa direto no arquivo. Se o YouTube bloquear, volta sozinho ao ritmo normal.", "Applies to MP3 downloads: downloads and converts several songs at once (you choose how many), with short waits, and writes title and cover straight into the file. If YouTube blocks, it returns to the normal pace by itself.", "Vale para descargas en MP3: descarga y convierte varias canciones a la vez (tú eliges cuántas), con esperas cortas, y escribe título y portada en el archivo. Si YouTube bloquea, vuelve solo al ritmo normal."),
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
    ("Músicas por hora", "Songs per hour", "Canciones por hora"), ("Link inválido · não dá para baixar", "Invalid link · can't be downloaded", "Enlace no válido · no se puede descargar"), ("Vídeo inexistente ou indisponível · não dá para baixar", "Video doesn't exist or is unavailable · can't be downloaded", "El video no existe o no está disponible · no se puede descargar"), ("Relatório copiado", "Report copied", "Informe copiado"), ("Limpar o registro? Isso não pode ser desfeito.", "Clear the log? This can't be undone.", "¿Borrar el registro? No se puede deshacer."), ("Escreva uma mensagem antes de enviar", "Write a message before sending", "Escribe un mensaje antes de enviar"), ("Não achei um app de e-mail. Texto copiado: envie para contato.wavefly@gmail.com", "No email app found. Text copied: send it to contato.wavefly@gmail.com", "No encontré una app de correo. Texto copiado: envíalo a contato.wavefly@gmail.com"), ("Problemas ou sugestões?", "Problems or suggestions?", "¿Problemas o sugerencias?"), ("Escreva aqui o que aconteceu ou o que você gostaria de ver. Vamos olhar.", "Write here what happened or what you would like to see. We will take a look.", "Escribe aquí lo que pasó o lo que te gustaría ver. Lo revisaremos."), ("Incluir informações técnicas (versão, aparelho e últimos eventos)", "Include technical info (version, device and latest events)", "Incluir información técnica (versión, dispositivo y últimos eventos)"), ("Escreva aqui…", "Write here…", "Escribe aquí…"), ("Copiar tudo", "Copy all", "Copiar todo"), ("Enviar", "Send", "Enviar"), ("Mediana (total)", "Median (total)", "Mediana (total)"), ("Mediana (conversão)", "Median (conversion)", "Mediana (conversión)"), ("Amostra", "Sample", "Muestra"),
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
#md{z-index:100000!important}
#wfdev{position:fixed;inset:0;z-index:99998;background:var(--bg);color:var(--fg);overflow-y:auto;padding:16px 16px 40px;-webkit-overflow-scrolling:touch}
#wfdev h2{margin:0 0 4px;font-size:20px}
#wfdev .wfbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
#wfdev .wfcx{background:var(--cd);border:1px solid var(--ln);border-radius:14px;padding:12px 14px;margin:10px 0}
#wfdev .wfcx h3{margin:0 0 8px;font-size:14px;text-transform:uppercase;letter-spacing:.04em;color:var(--fg);opacity:1}
#wfdev .wfbar .t,#wfdev .t{color:var(--at)!important;font-weight:800;font-size:15px}
#wfdev .note,#wfdev .wfcx p{color:var(--fg)!important;opacity:.9!important}
#wfdev .wfbtns button{color:var(--fg)!important;background:var(--sf)!important;font-weight:800;border-radius:12px;padding:10px}
#wfdev table{width:100%;border-collapse:collapse;font-size:14px}
#wfdev td{padding:3px 0}#wfdev td:last-child{text-align:right;font-weight:700}
#wfdev .wflog{font:11.5px/1.35 monospace;max-height:320px;overflow-y:auto;background:var(--sf);color:var(--fg);border-radius:10px;padding:8px;white-space:pre-wrap;overflow-wrap:anywhere;-webkit-user-select:text;user-select:text}
#wfdev .wfrow{display:flex;flex-direction:column;align-items:flex-start;gap:6px;margin:10px 0}
#wfdev .wfrow .wfsw{align-self:flex-start}
#wfdev .wfseg{display:flex;gap:6px;width:100%}
#wfdev .wfseg button{flex:1;height:38px;border-radius:10px;border:2px solid var(--ln)!important;background:var(--sf)!important;color:var(--fg)!important;font-weight:800;box-shadow:none!important}
#wfdev .wfseg button.on{background:#d9692a!important;border-color:#d9692a!important;color:#fff!important}
#wfdev .wfcmp{margin-top:10px;padding-top:8px;border-top:1px solid var(--ln);font-size:13px}
#wfdev .wfcmpt{font-weight:800;margin-bottom:4px}
#wfdev .wficons{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
#wfdev .wfic{box-shadow:none!important;display:flex;flex-direction:column;align-items:center;gap:4px;padding:6px 2px;border-radius:14px;border:2px solid transparent;background:var(--sf);color:var(--fg);font-size:12px;font-weight:700}
#wfdev .wfic.on{border-color:#d9692a!important;background:rgba(217,105,42,.22)!important}
#wfdev .wfic span{display:block;width:54px;height:54px;border-radius:50%;overflow:hidden}
#wfdev .wfic svg{width:100%;height:100%;display:block}
#wfdev .wfic em{font-style:normal}
#wfdev textarea.wffb{width:100%;min-height:110px;box-sizing:border-box;background:var(--sf);color:var(--fg);border:1px solid var(--ln);border-radius:12px;padding:10px;font:inherit;resize:none}
#wfdev .wfchk{display:flex;gap:8px;align-items:center;margin:8px 0;color:var(--fg)}
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
  if(window.wfPausaRender)window.wfPausaRender()}

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
  var bf=mk('<button class="t wfpb" id="btfal" hidden>Tentar de novo as falhas</button>');bc.parentNode.insertBefore(bf,bc);
  var ATIVOS=0,FALHAS=0;
  function pinta(){bp.textContent=PAUSADO?T('Continuar'):T('Pausar tudo');bp.hidden=!(PAUSADO||ATIVOS>0);bf.hidden=!FALHAS;bf.textContent=T('Tentar de novo as falhas')+' ('+FALHAS+')'}
  function aplica(j){PAUSADO=!!j.pausado;ATIVOS=j.ativos||0;FALHAS=j.falhas||0;pinta()}
  bp.onclick=function(){fetch('/api/pausa?v='+(PAUSADO?0:1)).then(function(r){return r.json()}).then(function(j){aplica(j);try{tick()}catch(e){}}).catch(function(){})};
  bf.onclick=function(){fetch('/api/pausa?falhas=1').then(function(r){return r.json()}).then(function(j){aplica(j);try{tick()}catch(e){}}).catch(function(){})};
  function ler(){if(document.hidden)return;fetch('/api/pausa').then(function(r){return r.json()}).then(aplica).catch(function(){})}
  setInterval(ler,2000);ler();
  window.wfPausaRender=pinta;
})();

/* ---------- Painel do desenvolvedor ---------- */
var DEVT=null;
function aplicaRapido(){try{var q='/api/dev?rede='+Math.min(5,wfget('dev_rede4')||4)+'&conv='+Math.min(5,wfget('dev_conv4')||4);fetch(q).then(function(){if(wfget('dev_rapido')==='1')fetch('/api/dev?rapido=1')})}catch(e){}}
aplicaRapido();
function devAbrir(){
  if(document.getElementById('wfdev'))return;
  var d=mk('<div id="wfdev"><div class="wfbar"><h2>Desenvolvedor</h2><button class="t" id="wfdx">Fechar</button></div>'+
    '<div class="wfcx"><div class="wfrow"><span class="wft">Download mais rápido</span><label class="wfsw"><input type="checkbox" id="wfrap"><i></i></label></div>'+
    '<p class="note" id="wfmodo"></p><p class="note">Vale para downloads em MP3: baixa e converte várias músicas ao mesmo tempo (você escolhe quantas), com esperas curtas, e grava título e capa direto no arquivo. Se o YouTube bloquear, volta sozinho ao ritmo normal.</p></div>'+
    '<div class="wfcx"><h3>Ajustes do modo rápido</h3>'+
    '<div class="wfrow"><span class="wft">Downloads ao mesmo tempo</span><span class="wfseg" id="wfsr"></span></div>'+
    '<div class="wfrow"><span class="wft">Conversões ao mesmo tempo</span><span class="wfseg" id="wfsc"></span></div>'+
    '<p class="note">Mais simultâneas = mais rápido, mas esquenta mais o celular e aumenta o risco de bloqueio do YouTube. Se bloquear, o freio automático volta ao ritmo normal.</p><div class="note" id="wfdica"></div></div>'+
    '<div class="wfcx"><h3>Ícone do app (teste)</h3><div class="wficons" id="wficons"></div><p class="note">Escolha um. O ícone na tela inicial pode levar alguns segundos para trocar.</p></div>'+
    '<div class="wfcx"><h3>Tempo médio por música</h3><table id="wftb"></table></div>'+
    '<div class="wfcx"><h3>Contagem</h3><table id="wfct"></table></div>'+
    '<div class="wfcx"><h3>Aparelho</h3><table id="wfap"></table></div>'+
    '<div class="wfcx"><h3>Problemas ou sugestões?</h3><p class="note">Escreva aqui o que aconteceu ou o que você gostaria de ver. Vamos olhar.</p><textarea class="wffb" id="wffb" placeholder="Escreva aqui…"></textarea><label class="wfchk"><input type="checkbox" id="wffi" checked> <span>Incluir informações técnicas (versão, aparelho e últimos eventos)</span></label><div class="wfbtns"><button id="wffc">Cancelar</button><button id="wffe">Enviar</button></div></div>'+
    '<div class="wfcx"><h3>Registro</h3><div class="wflog" id="wflg"></div><div class="wfbtns"><button id="wfca">Copiar tudo</button><button id="wfcp">Copiar registro</button><button id="wflp">Limpar</button></div></div></div>');
  document.body.appendChild(d);
  var sw=d.querySelector('#wfrap');
  sw.onchange=function(){wfset('dev_rapido',sw.checked?'1':'');fetch('/api/dev?rapido='+(sw.checked?1:0)).then(function(){devAtualiza()})};
  function seg(id,chave,pad){var el=d.querySelector(id),at=Math.min(5,+(wfget(chave)||pad));
    el.innerHTML=[2,3,4,5].map(function(n){return '<button type="button" data-n="'+n+'" class="'+(n===at?'on':'')+'">'+n+'</button>'}).join('');
    el.onclick=function(ev){var b=ev.target.closest('button');if(!b)return;wfset(chave,b.dataset.n);
      [].forEach.call(el.children,function(c){c.classList.toggle('on',c===b)});fetch('/api/dev?'+(chave==='dev_rede4'?'rede':'conv')+'='+b.dataset.n).then(devAtualiza)}}
  seg('#wfsr','dev_rede4',4);seg('#wfsc','dev_conv4',4);
  (function(){var DC={pt:[['2','Leve: menos calor e bateria, cerca de metade da velocidade. Bom com bateria baixa.'],['3','Equilibrado: bom ganho sem esquentar muito.'],['4','Recomendado: melhor equilíbrio. Nos testes, 30 músicas (inclusive faixas longas) em cerca de 13 min.'],['5','Máximo: só compensa com músicas curtas. Com faixas longas a conversão é limitada pelo processador, esquenta mais e o YouTube pode bloquear mais fácil.']],
    en:[['2','Light: less heat and battery use, about half the speed. Good on low battery.'],['3','Balanced: good gain without much heat.'],['4','Recommended: best balance. In tests, 30 songs (including long tracks) in about 13 min.'],['5','Maximum: only worth it with short songs. With long tracks conversion is limited by the processor, it runs hotter and YouTube may block more easily.']],
    es:[['2','Ligero: menos calor y batería, cerca de la mitad de velocidad. Bueno con batería baja.'],['3','Equilibrado: buena mejora sin calentar mucho.'],['4','Recomendado: mejor equilibrio. En pruebas, 30 canciones (con pistas largas) en unos 13 min.'],['5','Máximo: solo vale con canciones cortas. Con pistas largas la conversión la limita el procesador, calienta más y YouTube puede bloquear más fácil.']]};
    var el=d.querySelector('#wfdica');el.innerHTML=(DC[LANG]||DC.pt).map(function(x){return '<div><b>'+x[0]+'</b> — '+x[1]+'</div>'}).join('')+'<div style="margin-top:6px">'+({pt:'Downloads: o limite é o YouTube (bloqueio). Conversões: o limite é o processador do celular.',en:'Downloads: the limit is YouTube (blocking). Conversions: the limit is the phone processor.',es:'Descargas: el límite es YouTube (bloqueo). Conversiones: el límite es el procesador del teléfono.'}[LANG]||'')+'</div>'})();
  d.querySelector('#wfdx').onclick=function(){clearInterval(DEVT);DEVT=null;d.remove()};
  d.querySelector('#wflp').onclick=function(){conf(T('Limpar o registro? Isso não pode ser desfeito.'),T('Limpar')).then(function(ok){if(ok)fetch('/api/dev?limpar=1').then(function(){devAtualiza()})})};
  function copia(t,msg){try{if(W&&W.copiar){W.copiar(t);toast(T(msg));return}}catch(e){}
    try{var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();toast(T(msg))}catch(e){}}
  function relatorio(comLog){return fetch('/api/dev').then(function(r){return r.json()}).then(function(j){
    var v='',ap='';try{if(W&&W.versaoApp)v=W.versaoApp()}catch(e){}
    try{if(W&&W.info){var i=JSON.parse(W.info());ap='Bateria '+i.bat+'%'+(i.carregando?' (carregando)':'')+' · Memória do app '+i.memMb+' MB · Rede '+i.rede}}catch(e){}
    var m=j.medias||{},md=j.medianas||{};
    var L=['WaveFly '+v,'Aparelho: '+(navigator.userAgent||''),ap,'Idioma: '+LANG,'',
      'Modo: '+(j.freio?'freio ativo':j.rapido?'rápido':'normal')+' · downloads '+j.rede_n+' · conversões '+j.conv_n,
      'Concluídas '+j.ok+' · Falhas '+j.falha+' · Na fila '+((j.cont||{}).fila||0)+' · Baixando '+((j.cont||{}).baixando||0),
      'Médias ('+j.n+' músicas): info '+m.info+'s · download '+m.dl+'s · conversão '+m.conv+'s · espera '+m.espera+'s · total '+m.total+'s · '+j.por_hora+'/h',
      'Medianas: total '+md.total+'s · conversão '+md.conv+'s'];
    [['Normal',j.normal],['Rápido',j.veloz]].forEach(function(x){var r=x[1];if(r&&r.n)L.push('Lote '+x[0]+': '+r.n+' músicas · '+r.medias.total+'s · '+r.por_hora+'/h')});
    if(comLog!==false){L.push('','Registro:');L=L.concat((j.log||[]).slice(-40).map(function(x){return x.t+' ['+x.tipo+'] '+x.msg}))}
    return L.join('\n')})}
  d.querySelector('#wfca').onclick=function(){relatorio(true).then(function(t){copia(t,'Relatório copiado')})};
  d.querySelector('#wffc').onclick=function(){d.querySelector('#wffb').value=''};
  d.querySelector('#wffe').onclick=function(){var txt=(d.querySelector('#wffb').value||'').trim();if(!txt){toast(T('Escreva uma mensagem antes de enviar'));return}
    var com=d.querySelector('#wffi').checked;
    (com?relatorio(true):Promise.resolve('')).then(function(info){
      var corpo=txt+(info?'\n\n--- Informações técnicas ---\n'+info:'');
      var para='contato.wavefly@gmail.com',ass='WaveFly - Feedback',ok=false;
      try{if(W&&W.email)ok=W.email(para,ass,corpo)}catch(e){}
      if(!ok){copia('Para: '+para+'\nAssunto: '+ass+'\n\n'+corpo,'Não achei um app de e-mail. Texto copiado: envie para contato.wavefly@gmail.com')}})};
  d.querySelector('#wfcp').onclick=function(){var t=d.querySelector('#wflg').dataset.txt||'';
    try{if(W&&W.copiar){W.copiar(t);toast(T('Registro copiado'));return}}catch(e){}
    try{var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();toast(T('Registro copiado'))}catch(e){}};
  (function(){var ic=[{"n": "Padrão", "s": "<svg viewBox=\"0 0 108 108\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"108\" height=\"108\" fill=\"#D9692A\"/><path d=\"M30,46 L30,62\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\"/><path d=\"M42,38 L42,70\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\"/><path d=\"M54,30 L54,78\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\"/><path d=\"M66,38 L66,70\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\"/><path d=\"M78,46 L78,62\" stroke=\"#FBF3E1\" stroke-width=\"7\" stroke-linecap=\"round\"/></svg>"}, {"n": "Cassete", "s": "<svg viewBox=\"0 0 108 108\" xmlns=\"http://www.w3.org/2000/svg\"><defs><linearGradient id=\"g1\" x1=\"0.18\" y1=\"0\" x2=\"0.82\" y2=\"1\"><stop offset=\"0\" stop-color=\"#3B2314\"/><stop offset=\"1\" stop-color=\"#1A100A\"/></linearGradient></defs><rect width=\"108\" height=\"108\" fill=\"url(#g1)\"/><path d=\"M30,38 h48 a5,5 0 0 1 5,5 v26 a5,5 0 0 1 -5,5 h-48 a5,5 0 0 1 -5,-5 v-26 a5,5 0 0 1 5,-5z\" fill=\"#F6E7C8\" fill-opacity=\"1\"/><path d=\"M30,38 h48 a5,5 0 0 1 5,5 v6 h-58 v-6 a5,5 0 0 1 5,-5z\" fill=\"#E8873A\" fill-opacity=\"1\"/><path d=\"M35,42 h24 v3 h-24z\" fill=\"#FBF3E1\" fill-opacity=\"0.85\"/><path d=\"M36,57 h36 a7,7 0 0 1 0,14 h-36 a7,7 0 0 1 0,-14z\" fill=\"#2A1A10\" fill-opacity=\"1\"/><path d=\"M41.6,64 a4.4,4.4 0 1 0 8.8,0 a4.4,4.4 0 1 0 -8.8,0z\" fill=\"#F6E7C8\" fill-opacity=\"1\"/><path d=\"M57.6,64 a4.4,4.4 0 1 0 8.8,0 a4.4,4.4 0 1 0 -8.8,0z\" fill=\"#F6E7C8\" fill-opacity=\"1\"/><path d=\"M44.5,64 a1.5,1.5 0 1 0 3,0 a1.5,1.5 0 1 0 -3,0z\" fill=\"#2A1A10\" fill-opacity=\"1\"/><path d=\"M60.5,64 a1.5,1.5 0 1 0 3,0 a1.5,1.5 0 1 0 -3,0z\" fill=\"#2A1A10\" fill-opacity=\"1\"/><path d=\"M50,64 h8\" fill=\"none\" stroke=\"#F6E7C8\" stroke-opacity=\"0.7\" stroke-width=\"1.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M27.8,42 a1.2,1.2 0 1 0 2.4,0 a1.2,1.2 0 1 0 -2.4,0z\" fill=\"#8A6F55\" fill-opacity=\"1\"/><path d=\"M77.8,42 a1.2,1.2 0 1 0 2.4,0 a1.2,1.2 0 1 0 -2.4,0z\" fill=\"#8A6F55\" fill-opacity=\"1\"/><path d=\"M40,80 l3,-4 h22 l3,4z\" fill=\"#C9B48A\" fill-opacity=\"1\"/></svg>"}, {"n": "Onda W", "s": "<svg viewBox=\"0 0 108 108\" xmlns=\"http://www.w3.org/2000/svg\"><defs><linearGradient id=\"g2\" x1=\"0.18\" y1=\"0\" x2=\"0.82\" y2=\"1\"><stop offset=\"0\" stop-color=\"#F2A154\"/><stop offset=\"1\" stop-color=\"#B82E1F\"/></linearGradient></defs><rect width=\"108\" height=\"108\" fill=\"url(#g2)\"/><path d=\"M25,40 C31,40 36,66 41,66 C46,66 50,46 54,46 C58,46 62,66 67,66 C72,66 77,40 83,40\" fill=\"none\" stroke=\"#FFF6E4\" stroke-opacity=\"1\" stroke-width=\"8.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M25,52 C31,52 36,74 41,74 C46,74 50,58 54,58 C58,58 62,74 67,74 C72,74 77,52 83,52\" fill=\"none\" stroke=\"#FFF6E4\" stroke-opacity=\"0.45\" stroke-width=\"3.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg>"}, {"n": "Vinil", "s": "<svg viewBox=\"0 0 108 108\" xmlns=\"http://www.w3.org/2000/svg\"><defs><linearGradient id=\"g3\" x1=\"0.18\" y1=\"0\" x2=\"0.82\" y2=\"1\"><stop offset=\"0\" stop-color=\"#27355A\"/><stop offset=\"1\" stop-color=\"#0F1628\"/></linearGradient></defs><rect width=\"108\" height=\"108\" fill=\"url(#g3)\"/><path d=\"M25,54 a29,29 0 1 0 58,0 a29,29 0 1 0 -58,0z\" fill=\"#0E0E12\" fill-opacity=\"1\"/><path d=\"M29,54 a25,25 0 1 0 50,0 a25,25 0 1 0 -50,0z\" fill=\"none\" stroke=\"#2A2A33\" stroke-opacity=\"1\" stroke-width=\"1\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M33,54 a21,21 0 1 0 42,0 a21,21 0 1 0 -42,0z\" fill=\"none\" stroke=\"#22222A\" stroke-opacity=\"1\" stroke-width=\"1\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M37,54 a17,17 0 1 0 34,0 a17,17 0 1 0 -34,0z\" fill=\"none\" stroke=\"#2A2A33\" stroke-opacity=\"1\" stroke-width=\"1\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M54,54 L72,30 A30,30 0 0 1 80,48z\" fill=\"#FFFFFF\" fill-opacity=\"0.09\"/><path d=\"M54,54 L36,78 A30,30 0 0 1 28,60z\" fill=\"#FFFFFF\" fill-opacity=\"0.09\"/><path d=\"M44,54 a10,10 0 1 0 20,0 a10,10 0 1 0 -20,0z\" fill=\"#E8873A\" fill-opacity=\"1\"/><path d=\"M44,54 a10,10 0 1 0 20,0 a10,10 0 1 0 -20,0z\" fill=\"none\" stroke=\"#F6B26B\" stroke-opacity=\"1\" stroke-width=\"1.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M51.8,54 a2.2,2.2 0 1 0 4.4,0 a2.2,2.2 0 1 0 -4.4,0z\" fill=\"#0E0E12\" fill-opacity=\"1\"/></svg>"}, {"n": "Avião", "s": "<svg viewBox=\"0 0 108 108\" xmlns=\"http://www.w3.org/2000/svg\"><defs><linearGradient id=\"g4\" x1=\"0.18\" y1=\"0\" x2=\"0.82\" y2=\"1\"><stop offset=\"0\" stop-color=\"#1FA3A3\"/><stop offset=\"1\" stop-color=\"#0B4F63\"/></linearGradient></defs><rect width=\"108\" height=\"108\" fill=\"url(#g4)\"/><path d=\"M84,28 L26,50 L49,59z\" fill=\"#FFF6E4\" fill-opacity=\"1\"/><path d=\"M84,28 L49,59 L58,82z\" fill=\"#D9E7E0\" fill-opacity=\"1\"/><path d=\"M49,59 L58,82 L61,67z\" fill=\"#A9C9C4\" fill-opacity=\"1\"/><path d=\"M22,84 C32,76 40,92 50,84 S68,76 80,84\" fill=\"none\" stroke=\"#FFF6E4\" stroke-opacity=\"0.65\" stroke-width=\"3.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg>"}, {"n": "Ripple", "s": "<svg viewBox=\"0 0 108 108\" xmlns=\"http://www.w3.org/2000/svg\"><defs><linearGradient id=\"g5\" x1=\"0.18\" y1=\"0\" x2=\"0.82\" y2=\"1\"><stop offset=\"0\" stop-color=\"#D1306A\"/><stop offset=\"1\" stop-color=\"#6B1B57\"/></linearGradient></defs><rect width=\"108\" height=\"108\" fill=\"url(#g5)\"/><path d=\"M20,54 a34,34 0 1 0 68,0 a34,34 0 1 0 -68,0z\" fill=\"none\" stroke=\"#FFE3EE\" stroke-opacity=\"0.35\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M29,54 a25,25 0 1 0 50,0 a25,25 0 1 0 -50,0z\" fill=\"none\" stroke=\"#FFF1F6\" stroke-opacity=\"1\" stroke-width=\"4.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><path d=\"M48,43 L48,65 L66,54z\" fill=\"#FFF1F6\" fill-opacity=\"1\" stroke=\"#FFF1F6\" stroke-opacity=\"1\" stroke-width=\"3\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg>"}],box=d.querySelector('#wficons'),at=0;try{if(W&&W.icone)at=W.icone()}catch(e){}
    box.innerHTML=ic.map(function(x,i){return '<button type="button" class="wfic'+(i===at?' on':'')+'" data-i="'+i+'"><span>'+x.s+'</span><em>'+x.n+'</em></button>'}).join('');
    box.onclick=function(ev){var b=ev.target.closest('button');if(!b)return;try{if(W&&W.setIcone)W.setIcone(+b.dataset.i)}catch(e){}
      [].forEach.call(box.children,function(c){c.classList.toggle('on',c===b)});toast(T('Ícone trocado. Pode levar alguns segundos.'))}})();
  devAtualiza();DEVT=setInterval(devAtualiza,2000);
}
function lin(a,b){return '<tr><td>'+a+'</td><td>'+b+'</td></tr>'}
function cmp(j){
  function l(nome,r){return r&&r.n?'<div class="wfcmpl"><b>'+nome+'</b> · '+r.n+' '+T('músicas')+' · '+r.medias.total+' s · '+r.por_hora+'/h</div>':''}
  var t=l(T('Normal'),j.normal)+l(T('Rápido'),j.veloz);
  return t?'<div class="wfcmp"><div class="wfcmpt">'+T('Comparação do lote')+'</div>'+t+'</div>':''}
function devAtualiza(){
  var d=document.getElementById('wfdev');if(!d)return;
  fetch('/api/dev').then(function(r){return r.json()}).then(function(j){
    var sw=d.querySelector('#wfrap');sw.checked=!!j.rapido;
    var modo=j.freio?{pt:'Freio ativo: voltou ao ritmo normal por causa de um bloqueio.',en:'Brake on: back to normal speed because of a block.',es:'Freno activo: volvió al ritmo normal por un bloqueo.'}[LANG]:j.rapido?{pt:'Modo rápido em uso.',en:'Fast mode in use.',es:'Modo rápido en uso.'}[LANG]:{pt:'Modo normal.',en:'Normal mode.',es:'Modo normal.'}[LANG];
    var mm=d.querySelector('#wfmodo');mm.textContent=modo+(j.pausado?(' '+T('Downloads pausados.')):'');
    var m=j.medias||{};
    d.querySelector('#wftb').innerHTML=j.n?lin(T('Informações'),m.info+' s')+lin('Download',m.dl+' s')+lin(T('Conversão'),m.conv+' s')+lin(T('Espera'),m.espera+' s')+lin('Total',m.total+' s')+lin(T('Mediana (total)'),(j.medianas||{}).total+' s')+lin(T('Mediana (conversão)'),(j.medianas||{}).conv+' s')+lin(T('Músicas por hora'),j.por_hora)+lin(T('Amostra'),j.n)+cmp(j):'<tr><td>'+T('Sem medidas ainda. Baixe algumas músicas.')+'</td></tr>';
    var c=j.cont||{};
    d.querySelector('#wfct').innerHTML=lin(T('Concluídas'),j.ok)+lin(T('Falhas'),j.falha)+lin(T('Na fila'),c.fila||0)+lin('Baixando',c.baixando||0)+lin(T('Repetidas'),c.duplicada||0);
    var lg=(j.log||[]).map(function(x){return x.t+' ['+x.tipo+'] '+x.msg}).join('\n');
    var el=d.querySelector('#wflg');el.textContent=lg||T('Sem eventos.');el.dataset.txt=lg;
    var ap='';try{if(W&&W.info){var i=JSON.parse(W.info());ap=lin(T('Bateria'),i.bat+'%'+(i.carregando?' ⚡':''))+lin(T('Memória do app'),i.memMb+' MB')+lin(T('Rede'),i.rede)}}catch(e){}
    d.querySelector('#wfap').innerHTML=ap||lin('—','—')}).catch(function(){})}

setLang(LANG);
})();
</script>
"""


def bloco():
    js = JS_TPL.replace("__DICT__", json.dumps(DICT, ensure_ascii=False)).replace("__PAD__", json.dumps(PADROES, ensure_ascii=False))
    return CSS + js
