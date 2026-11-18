package com.wavefly.app

import android.media.MediaPlayer
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import java.io.File
import java.util.function.Consumer

/** Player nativo (MediaPlayer). Conversa com a notificação pelos campos de PythonService e por NativoHook. */
object Tocador {
    private val ui = Handler(Looper.getMainLooper())
    private var mp: MediaPlayer? = null
    private var pronto = false
    var raiz: String = ""

    var fila: List<Musica> = emptyList()
    var idx by mutableIntStateOf(-1)
    var tocando by mutableStateOf(false)
    var pos by mutableIntStateOf(0)
    var dur by mutableIntStateOf(0)

    val atual: Musica? get() = fila.getOrNull(idx)

    private val tique = object : Runnable {
        override fun run() {
            val m = mp
            if (m != null && pronto) {
                try {
                    pos = m.currentPosition
                } catch (_: Throwable) {
                }
                publicar(false)
            }
            if (tocando) ui.postDelayed(this, 500)
        }
    }

    fun iniciar() {
        NativoHook.cmd = Consumer { c -> comando(c) }
    }

    fun tocar(lista: List<Musica>, i: Int) {
        fila = lista
        idx = i
        carregar()
    }

    private fun carregar() {
        val m0 = mp
        mp = null
        pronto = false
        try {
            m0?.release()
        } catch (_: Throwable) {
        }
        val musica = atual ?: return
        pos = 0
        dur = 0
        try {
            val m = MediaPlayer()
            mp = m
            m.setDataSource(File(raiz, musica.rel).path)
            m.setOnPreparedListener {
                if (mp !== m) return@setOnPreparedListener
                pronto = true
                dur = m.duration
                m.start()
                tocando = true
                ui.removeCallbacks(tique)
                ui.post(tique)
                publicar(true)
            }
            m.setOnCompletionListener { if (mp === m) proximo() }
            m.setOnErrorListener { _, _, _ ->
                if (mp === m) proximo()
                true
            }
            m.prepareAsync()
            tocando = true
            publicar(true)
        } catch (_: Throwable) {
            proximo()
        }
    }

    fun alternar() {
        val m = mp ?: return
        if (!pronto) return
        if (tocando) {
            m.pause()
            tocando = false
        } else {
            m.start()
            tocando = true
            ui.removeCallbacks(tique)
            ui.post(tique)
        }
        publicar(true)
    }

    fun proximo() {
        if (fila.isEmpty()) return
        if (idx + 1 < fila.size) {
            idx += 1
            carregar()
        } else {
            parar()
        }
    }

    fun anterior() {
        val m = mp
        if (m != null && pronto && pos > 3000) {
            m.seekTo(0)
            pos = 0
            publicar(true)
            return
        }
        if (idx > 0) {
            idx -= 1
            carregar()
        }
    }

    fun buscar(ms: Int) {
        val m = mp ?: return
        if (!pronto) return
        val t = ms.coerceIn(0, maxOf(0, dur))
        m.seekTo(t)
        pos = t
        publicar(true)
    }

    fun parar() {
        ui.removeCallbacks(tique)
        try {
            mp?.release()
        } catch (_: Throwable) {
        }
        mp = null
        pronto = false
        tocando = false
        idx = -1
        fila = emptyList()
        pos = 0
        dur = 0
        PythonService.pAtivo = false
        PythonService.pTocando = false
        PythonService.acordar()
    }

    /** Comandos vindos da notificação. */
    fun comando(c: String) {
        when {
            c == "play" -> if (!tocando) alternar()
            c == "pause" -> if (tocando) alternar()
            c == "next" -> proximo()
            c == "prev" -> anterior()
            c == "stop" -> parar()
            c.startsWith("rel:") -> c.substring(4).toIntOrNull()?.let { buscar(pos + it * 1000) }
            c.startsWith("seek:") -> c.substring(5).toIntOrNull()?.let { buscar(it) }
        }
    }

    /** Conta o estado para a notificação (título, capa, posição). */
    private fun publicar(mudou: Boolean) {
        val m = atual
        PythonService.pCapa = m?.rel ?: ""
        PythonService.pTitulo = m?.nome ?: ""
        PythonService.pSub = if (m == null || m.pasta.isEmpty()) "WaveFly" else m.pasta
        PythonService.pVideo = false
        PythonService.pPosMs = pos.toLong()
        PythonService.pDurMs = dur.toLong()
        PythonService.pEm = SystemClock.elapsedRealtime()
        val antesAtivo = PythonService.pAtivo
        val antesToc = PythonService.pTocando
        PythonService.pTocando = tocando
        PythonService.pAtivo = m != null
        if (mudou || antesAtivo != PythonService.pAtivo || antesToc != PythonService.pTocando) PythonService.acordar()
    }
}
