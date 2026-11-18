package com.wavefly.app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Slider
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

private val Fundo = Color(0xFF1F1510)
private val Cartao = Color(0xFF2B1D15)
private val Superficie = Color(0xFF38271C)
private val Creme = Color(0xFFF3E6CC)
private val Suave = Color(0xFFB39B82)
private val Laranja = Color(0xFFE07A35)

/** Versão de teste com a interface 100% nativa (Jetpack Compose). O motor (Python) é o mesmo do app oficial. */
class NativoActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 23 &&
            checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(
                arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE), 1,
            )
        }
        Tocador.iniciar()
        setContent {
            MaterialTheme(
                colorScheme = darkColorScheme(
                    primary = Laranja, onPrimary = Fundo, background = Fundo, onBackground = Creme,
                    surface = Cartao, onSurface = Creme, surfaceVariant = Superficie, onSurfaceVariant = Suave,
                    secondaryContainer = Superficie, onSecondaryContainer = Creme,
                ),
            ) {
                Surface(Modifier.fillMaxSize(), color = Fundo) { Raiz() }
            }
        }
        tratarIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        tratarIntent(intent)
    }

    /** Link compartilhado de outro app (Compartilhar > WaveFly): entra na fila. */
    private fun tratarIntent(it: Intent?) {
        if (it == null || Intent.ACTION_SEND != it.action) return
        val txt = it.getStringExtra(Intent.EXTRA_TEXT) ?: return
        it.action = null
        Thread {
            var n = 0
            while (!PythonService.ready && n++ < 200) Thread.sleep(300)
            val r = try {
                com.chaquo.python.Python.getInstance().getModule("app_entry").callAttr("baixar_link", txt, "").toString()
            } catch (t: Throwable) {
                "erro"
            }
            runOnUiThread {
                val m = if (r.startsWith("ok")) "Adicionado à fila de download"
                else if (r.startsWith("ja")) "Já está na fila ou na pasta" else "Esse link não é do YouTube"
                android.widget.Toast.makeText(this, m, android.widget.Toast.LENGTH_LONG).show()
            }
        }.start()
    }

    override fun onStart() {
        super.onStart()
        PythonService.visivel = true
        startService(Intent(this, PythonService::class.java))
    }

    override fun onStop() {
        PythonService.visivel = false
        super.onStop()
    }
}

private fun mmss(ms: Int): String {
    val s = maxOf(0, ms) / 1000
    return "%d:%02d".format(s / 60, s % 60)
}

// ====================================================================== raiz
@Composable
private fun Raiz() {
    var pronto by remember { mutableStateOf(PythonService.ready) }
    var erro by remember { mutableStateOf<String?>(null) }
    var status by remember { mutableStateOf(PythonService.status) }
    LaunchedEffect(Unit) {
        while (!pronto && erro == null) {
            erro = PythonService.error
            status = PythonService.status
            pronto = PythonService.ready
            delay(300)
        }
    }
    Crossfade(targetState = pronto, animationSpec = tween(450), label = "inicio") { ok ->
        if (!ok) Abertura(erro ?: status) else Principal()
    }
}

@Composable
private fun Abertura(texto: String) {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Row {
                Text("Wave", fontSize = 40.sp, fontWeight = FontWeight.Bold, color = Creme)
                Text("Fly", fontSize = 40.sp, fontWeight = FontWeight.Bold, fontStyle = FontStyle.Italic, color = Laranja)
            }
            Spacer(Modifier.height(20.dp))
            CircularProgressIndicator(color = Laranja)
            Spacer(Modifier.height(16.dp))
            Text(texto, color = Suave, fontSize = 14.sp)
        }
    }
}

@Composable
private fun Principal() {
    val escopo = rememberCoroutineScope()
    var aba by rememberSaveable { mutableStateOf(1) }
    var bib by remember { mutableStateOf<Biblioteca?>(null) }
    var fila by remember { mutableStateOf<Fila?>(null) }
    var expandido by remember { mutableStateOf(false) }

    fun recarregar() {
        escopo.launch {
            val b = withContext(Dispatchers.IO) { try { Api.biblioteca() } catch (t: Throwable) { null } }
            if (b != null) {
                bib = b
                Tocador.raiz = b.raiz
            }
        }
    }

    // Estado dos downloads: consulta a cada 1 s com fila ativa e a cada 4 s em repouso.
    LaunchedEffect(Unit) {
        recarregar()
        var ultimoOk = -1
        while (true) {
            val f = withContext(Dispatchers.IO) { try { Api.estado() } catch (t: Throwable) { null } }
            if (f != null) {
                fila = f
                if (f.ok != ultimoOk) {
                    ultimoOk = f.ok
                    recarregar()
                }
            }
            delay(if (f != null && (f.baixando > 0 || f.fila > 0)) 1000L else 4000L)
        }
    }

    Box(Modifier.fillMaxSize()) {
        Column(Modifier.fillMaxSize()) {
            Cabecalho()
            Box(Modifier.weight(1f)) {
                Crossfade(targetState = aba, animationSpec = tween(220), label = "aba") { a ->
                    if (a == 0) BaixarTela(fila, onFeito = { recarregar() }) else BibliotecaTela(bib, ::recarregar)
                }
            }
            if (Tocador.atual != null) MiniPlayer(onAbrir = { expandido = true })
            NavigationBar(containerColor = Cartao) {
                NavigationBarItem(selected = aba == 0, onClick = { aba = 0 },
                    icon = { Text("⬇", fontSize = 18.sp) }, label = { Text("Baixar") })
                NavigationBarItem(selected = aba == 1, onClick = { aba = 1 },
                    icon = { Text("♫", fontSize = 18.sp) }, label = { Text("Biblioteca") })
            }
        }
        AnimatedVisibility(
            visible = expandido && Tocador.atual != null,
            enter = slideInVertically(tween(300)) { it } + fadeIn(tween(300)),
            exit = slideOutVertically(tween(250)) { it } + fadeOut(tween(250)),
        ) {
            TocandoAgora(onFechar = { expandido = false })
        }
    }
}

@Composable
private fun Cabecalho() {
    Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
        Text("Wave", fontSize = 26.sp, fontWeight = FontWeight.Bold, color = Creme)
        Text("Fly", fontSize = 26.sp, fontWeight = FontWeight.Bold, fontStyle = FontStyle.Italic, color = Laranja)
        Spacer(Modifier.width(8.dp))
        Text("NATIVO", fontSize = 11.sp, color = Laranja, fontWeight = FontWeight.Bold,
            modifier = Modifier.clip(RoundedCornerShape(6.dp)).background(Superficie).padding(horizontal = 6.dp, vertical = 2.dp))
    }
}

// ====================================================================== capa
@Composable
private fun Capa(rel: String, tamanho: Dp, modifier: Modifier = Modifier) {
    val px = with(LocalDensity.current) { tamanho.roundToPx() }
    val img by produceState<androidx.compose.ui.graphics.ImageBitmap?>(null, rel) {
        value = withContext(Dispatchers.IO) { Api.capa(rel, px)?.asImageBitmap() }
    }
    Box(modifier.size(tamanho).clip(RoundedCornerShape(8.dp)).background(Superficie), contentAlignment = Alignment.Center) {
        Text("♪", color = Suave, fontSize = (tamanho.value / 2.5f).sp)
        val b = img
        AnimatedVisibility(visible = b != null, enter = fadeIn(tween(300))) {
            if (b != null) Image(b, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
        }
    }
}

// ====================================================================== biblioteca
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun BibliotecaTela(bib: Biblioteca?, recarregar: () -> Unit) {
    val escopo = rememberCoroutineScope()
    var aberta by rememberSaveable { mutableStateOf<String?>(null) }
    val sel = remember { mutableStateListOf<String>() }
    var confirmar by remember { mutableStateOf(false) }

    if (bib == null) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Laranja) }
        return
    }
    val pasta = bib.pastas.firstOrNull { it.nome == aberta }
    val musicas = if (pasta != null) pasta.itens else bib.soltas
    val modoSel = sel.isNotEmpty()

    BackHandler(enabled = modoSel || aberta != null) {
        if (modoSel) sel.clear() else aberta = null
    }

    fun chaveMusica(m: Musica) = m.rel
    fun chavePasta(p: Pasta) = "pasta:" + p.nome

    Column(Modifier.fillMaxSize()) {
        // barra superior: título ou ações de seleção
        Row(Modifier.fillMaxWidth().height(52.dp).padding(horizontal = 12.dp), verticalAlignment = Alignment.CenterVertically) {
            if (modoSel) {
                TextButton(onClick = { sel.clear() }) { Text("✕", color = Creme, fontSize = 18.sp) }
                Text("${sel.size} selecionados", color = Creme, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
                TextButton(onClick = {
                    sel.clear()
                    if (pasta == null) {
                        bib.pastas.forEach { sel.add(chavePasta(it)) }
                    } else {
                        musicas.forEach { sel.add(chaveMusica(it)) }
                    }
                }) { Text("Tudo", color = Laranja) }
                TextButton(onClick = { confirmar = true }) { Text("Apagar", color = Color(0xFFE58A72)) }
            } else if (pasta != null) {
                TextButton(onClick = { aberta = null }) { Text("←", color = Creme, fontSize = 20.sp) }
                Text(pasta.nome, color = Creme, fontWeight = FontWeight.SemiBold, maxLines = 1,
                    overflow = TextOverflow.Ellipsis, modifier = Modifier.weight(1f))
                Text("${pasta.itens.size}", color = Suave)
            } else {
                Text("Biblioteca", color = Creme, fontSize = 22.sp, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                Text("${bib.soltas.size + bib.pastas.sumOf { it.itens.size }} músicas", color = Suave, fontSize = 13.sp)
            }
        }

        if (bib.pastas.isEmpty() && bib.soltas.isEmpty()) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("Nada por aqui ainda. Baixe algo na aba Baixar.", color = Suave)
            }
        } else {
            LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(bottom = 8.dp)) {
                if (pasta == null) {
                    items(bib.pastas, key = { "p:" + it.nome }) { p ->
                        val ch = chavePasta(p)
                        Linha(
                            modifier = Modifier.animateItemPlacement(),
                            titulo = p.nome, sub = "${p.itens.size} músicas",
                            capa = p.itens.firstOrNull()?.rel, pasta = true,
                            tocando = false, selecionado = sel.contains(ch), modoSel = modoSel,
                            onClick = {
                                if (modoSel) { if (sel.contains(ch)) sel.remove(ch) else sel.add(ch) } else aberta = p.nome
                            },
                            onLong = { if (sel.contains(ch)) sel.remove(ch) else sel.add(ch) },
                        )
                    }
                }
                items(musicas, key = { "m:" + it.rel }) { m ->
                    val ch = chaveMusica(m)
                    Linha(
                        modifier = Modifier.animateItemPlacement(),
                        titulo = m.nome, sub = if (pasta == null) "" else pasta.nome,
                        capa = m.rel, pasta = false,
                        tocando = Tocador.atual?.rel == m.rel, selecionado = sel.contains(ch), modoSel = modoSel,
                        onClick = {
                            if (modoSel) { if (sel.contains(ch)) sel.remove(ch) else sel.add(ch) }
                            else Tocador.tocar(musicas, musicas.indexOf(m))
                        },
                        onLong = { if (sel.contains(ch)) sel.remove(ch) else sel.add(ch) },
                    )
                }
            }
        }
    }

    if (confirmar) {
        val nPastas = sel.count { it.startsWith("pasta:") }
        val msg = if (nPastas > 0) "Apagar ${sel.size} itens? As playlists selecionadas serão apagadas com todas as músicas dentro."
        else "Apagar ${sel.size} músicas do aparelho?"
        AlertDialog(
            onDismissRequest = { confirmar = false },
            containerColor = Cartao,
            text = { Text(msg, color = Creme) },
            confirmButton = {
                TextButton(onClick = {
                    confirmar = false
                    val lista = sel.toList()
                    if (Tocador.atual != null && (lista.contains(Tocador.atual!!.rel) || lista.any { it.startsWith("pasta:") && Tocador.atual!!.pasta == it.substring(6) })) Tocador.parar()
                    sel.clear()
                    if (aberta != null && lista.contains("pasta:$aberta")) aberta = null
                    escopo.launch {
                        withContext(Dispatchers.IO) { try { Api.apagar(lista) } catch (t: Throwable) { null } }
                        recarregar()
                    }
                }) { Text("Apagar", color = Color(0xFFE58A72)) }
            },
            dismissButton = { TextButton(onClick = { confirmar = false }) { Text("Cancelar", color = Creme) } },
        )
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun Linha(
    modifier: Modifier, titulo: String, sub: String, capa: String?, pasta: Boolean, tocando: Boolean,
    selecionado: Boolean, modoSel: Boolean, onClick: () -> Unit, onLong: () -> Unit,
) {
    Row(
        modifier.fillMaxWidth()
            .background(if (selecionado) Superficie else Color.Transparent)
            .combinedClickable(onClick = onClick, onLongClick = onLong)
            .padding(horizontal = 16.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (capa != null) Capa(capa, 52.dp) else Box(Modifier.size(52.dp))
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(titulo, color = if (tocando) Laranja else Creme, maxLines = 1, overflow = TextOverflow.Ellipsis,
                fontWeight = if (pasta || tocando) FontWeight.SemiBold else FontWeight.Normal)
            if (sub.isNotEmpty()) Text(sub, color = Suave, fontSize = 12.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
        if (modoSel) Checkbox(checked = selecionado, onCheckedChange = { onClick() })
        else if (pasta) Text("›", color = Suave, fontSize = 22.sp)
        else if (tocando) Text("▶", color = Laranja, fontSize = 14.sp)
    }
}

// ====================================================================== baixar
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun BaixarTela(fila: Fila?, onFeito: () -> Unit) {
    val escopo = rememberCoroutineScope()
    val clip = LocalClipboardManager.current
    var texto by rememberSaveable { mutableStateOf("") }
    var msg by remember { mutableStateOf("") }
    var enviando by remember { mutableStateOf(false) }

    Column(Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
        Text("Baixar", color = Creme, fontSize = 30.sp, fontWeight = FontWeight.Bold)
        Text("Cole links do YouTube para gerenciar seus downloads.", color = Suave, fontSize = 14.sp, fontStyle = FontStyle.Italic)
        Spacer(Modifier.height(10.dp))
        OutlinedTextField(
            value = texto, onValueChange = { texto = it },
            modifier = Modifier.fillMaxWidth().height(110.dp),
            placeholder = { Text("Cole os links aqui…", color = Suave) },
        )
        Row(Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Button(
                enabled = texto.isNotBlank() && !enviando,
                onClick = {
                    enviando = true
                    escopo.launch {
                        val r = withContext(Dispatchers.IO) { try { Api.adicionar(texto) } catch (t: Throwable) { null } }
                        enviando = false
                        if (r == null || r.has("erro")) msg = r?.optString("erro") ?: "Não deu para adicionar"
                        else {
                            msg = "${r.optInt("add")} adicionadas · ${r.optInt("ja")} já existiam"
                            texto = ""
                        }
                        onFeito()
                    }
                },
            ) { Text("Baixar") }
            OutlinedButton(onClick = { clip.getText()?.let { texto = if (texto.isEmpty()) it.text else texto + "\n" + it.text } }) { Text("Colar") }
            OutlinedButton(onClick = { texto = "" }) { Text("Limpar") }
            Text(msg, color = Suave, fontSize = 12.sp, modifier = Modifier.weight(1f))
        }
        Spacer(Modifier.height(12.dp))
        if (fila != null && fila.itens.isNotEmpty()) {
            Text(
                "Baixando ${fila.baixando} · Na fila ${fila.fila} · Prontas ${fila.ok} · Falhas ${fila.falha}" +
                    if (fila.puladas > 0) " · Puladas ${fila.puladas}" else "",
                color = Suave, fontSize = 12.sp,
            )
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(vertical = 6.dp)) {
                TextButton(onClick = { escopo.launch(Dispatchers.IO) { try { Api.acao("cancelar_tudo") } catch (_: Throwable) {} } }) { Text("Cancelar tudo", color = Color(0xFFE58A72)) }
                TextButton(onClick = { escopo.launch(Dispatchers.IO) { try { Api.acao("limpar") } catch (_: Throwable) {} } }) { Text("Limpar", color = Laranja) }
                if (fila.falha > 0) TextButton(onClick = { escopo.launch(Dispatchers.IO) { try { Api.acao("tentar_falhas") } catch (_: Throwable) {} } }) { Text("Tentar falhas", color = Laranja) }
            }
            LazyColumn(Modifier.fillMaxSize()) {
                items(fila.itens, key = { it.id }) { i ->
                    Column(Modifier.fillMaxWidth().animateItemPlacement().padding(vertical = 6.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(i.titulo, color = Creme, maxLines = 1, overflow = TextOverflow.Ellipsis, modifier = Modifier.weight(1f))
                            Spacer(Modifier.width(8.dp))
                            val (rot, cor) = when (i.status) {
                                "ok" -> "✓" to Color(0xFFB0BA84)
                                "falha" -> "falhou" to Color(0xFFE58A72)
                                "baixando" -> "${i.pct.toInt()}%" to Laranja
                                "fila" -> "na fila" to Suave
                                "pulada" -> "pulada" to Suave
                                "duplicada" -> "já existe" to Suave
                                else -> i.status to Suave
                            }
                            Text(rot, color = cor, fontSize = 13.sp)
                        }
                        if (i.status == "baixando") {
                            Spacer(Modifier.height(4.dp))
                            LinearProgressIndicator(
                                progress = (i.pct / 100.0).coerceIn(0.0, 1.0).toFloat(),
                                modifier = Modifier.fillMaxWidth().height(4.dp).clip(CircleShape),
                                color = Laranja, trackColor = Superficie,
                            )
                            if (i.vel.isNotEmpty()) Text(i.vel, color = Suave, fontSize = 11.sp)
                        } else if (i.status == "falha" && i.erro.isNotEmpty()) {
                            Text(i.erro, color = Suave, fontSize = 11.sp, maxLines = 2, overflow = TextOverflow.Ellipsis)
                        }
                    }
                }
            }
        } else {
            Box(Modifier.fillMaxSize().padding(top = 40.dp), contentAlignment = Alignment.TopCenter) {
                Text("Nenhum download por enquanto.", color = Suave)
            }
        }
    }
}

// ====================================================================== player
@Composable
private fun MiniPlayer(onAbrir: () -> Unit) {
    val m = Tocador.atual ?: return
    Column(Modifier.fillMaxWidth().background(Superficie).clickable { onAbrir() }) {
        val frac = if (Tocador.dur > 0) Tocador.pos.toFloat() / Tocador.dur else 0f
        LinearProgressIndicator(progress = frac.coerceIn(0f, 1f), modifier = Modifier.fillMaxWidth().height(2.dp),
            color = Laranja, trackColor = Cartao)
        Row(Modifier.padding(horizontal = 12.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            Capa(m.rel, 44.dp)
            Spacer(Modifier.width(10.dp))
            Column(Modifier.weight(1f)) {
                Text(m.nome, color = Creme, maxLines = 1, overflow = TextOverflow.Ellipsis, fontWeight = FontWeight.SemiBold)
                Text(if (m.pasta.isEmpty()) "WaveFly" else m.pasta, color = Suave, fontSize = 12.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
            }
            TextButton(onClick = { Tocador.alternar() }) { Text(if (Tocador.tocando) "⏸" else "▶", color = Creme, fontSize = 22.sp) }
            TextButton(onClick = { Tocador.proximo() }) { Text("⏭", color = Creme, fontSize = 20.sp) }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun TocandoAgora(onFechar: () -> Unit) {
    val m = Tocador.atual ?: return
    BackHandler { onFechar() }
    var arrastando by remember { mutableStateOf<Float?>(null) }
    Column(
        Modifier.fillMaxSize().background(Fundo).padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = onFechar) { Text("⌄", color = Creme, fontSize = 26.sp) }
            Text("Tocando agora", color = Suave, modifier = Modifier.weight(1f).padding(start = 8.dp))
        }
        Spacer(Modifier.height(16.dp))
        Capa(m.rel, 300.dp)
        Spacer(Modifier.height(24.dp))
        Text(m.nome, color = Creme, fontSize = 20.sp, fontWeight = FontWeight.Bold, maxLines = 2, overflow = TextOverflow.Ellipsis)
        Text(if (m.pasta.isEmpty()) "WaveFly" else m.pasta, color = Suave, fontSize = 14.sp)
        Spacer(Modifier.height(16.dp))
        val valor = arrastando ?: (if (Tocador.dur > 0) Tocador.pos.toFloat() / Tocador.dur else 0f)
        Slider(
            value = valor.coerceIn(0f, 1f),
            onValueChange = { arrastando = it },
            onValueChangeFinished = {
                arrastando?.let { Tocador.buscar((it * Tocador.dur).toInt()) }
                arrastando = null
            },
        )
        Row(Modifier.fillMaxWidth()) {
            Text(mmss(if (arrastando != null) (arrastando!! * Tocador.dur).toInt() else Tocador.pos), color = Suave, fontSize = 12.sp, modifier = Modifier.weight(1f))
            Text(mmss(Tocador.dur), color = Suave, fontSize = 12.sp)
        }
        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(20.dp), verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = { Tocador.anterior() }) { Text("⏮", color = Creme, fontSize = 30.sp) }
            Button(
                onClick = { Tocador.alternar() },
                shape = CircleShape,
                modifier = Modifier.size(72.dp),
                contentPadding = PaddingValues(0.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Laranja, contentColor = Fundo),
            ) { Text(if (Tocador.tocando) "⏸" else "▶", fontSize = 30.sp) }
            TextButton(onClick = { Tocador.proximo() }) { Text("⏭", color = Creme, fontSize = 30.sp) }
        }
    }
}
