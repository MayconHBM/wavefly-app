package com.wavefly.app

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.LruCache
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import java.util.concurrent.Semaphore

/** Música da biblioteca. */
data class Musica(val rel: String, val nome: String, val pasta: String, val tam: Long, val mt: Long)

/** Pasta (playlist) da biblioteca. */
data class Pasta(val nome: String, val itens: List<Musica>)

data class Biblioteca(val raiz: String, val soltas: List<Musica>, val pastas: List<Pasta>)

/** Item da fila de downloads. */
data class ItemFila(val id: String, val titulo: String, val status: String, val pct: Double, val vel: String, val erro: String)

data class Fila(
    val itens: List<ItemFila>,
    val fila: Int, val baixando: Int, val ok: Int, val falha: Int, val puladas: Int,
    val agora: String, val aviso: String,
)

/** Fala com o servidor Python local (o mesmo motor da versão web). */
object Api {
    private val BASE = "http://127.0.0.1:" + PythonService.PORT

    fun enc(s: String): String = URLEncoder.encode(s, "UTF-8")

    fun get(path: String): JSONObject {
        val c = URL(BASE + path).openConnection() as HttpURLConnection
        c.connectTimeout = 5000
        c.readTimeout = 60000
        try {
            val st = if (c.responseCode in 200..299) c.inputStream else c.errorStream
            return JSONObject(st.bufferedReader().readText())
        } finally {
            c.disconnect()
        }
    }

    fun post(path: String, body: JSONObject): JSONObject {
        val c = URL(BASE + path).openConnection() as HttpURLConnection
        c.requestMethod = "POST"
        c.doOutput = true
        c.connectTimeout = 5000
        c.readTimeout = 120000
        c.setRequestProperty("X-Requested-With", "wavefly")
        c.setRequestProperty("Content-Type", "application/json")
        try {
            c.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
            val st = if (c.responseCode in 200..299) c.inputStream else c.errorStream
            return JSONObject(st.bufferedReader().readText())
        } finally {
            c.disconnect()
        }
    }

    private fun musica(o: JSONObject) = Musica(
        o.optString("rel"), o.optString("nome"), o.optString("pasta"), o.optLong("tam"), o.optLong("mt"),
    )

    fun biblioteca(): Biblioteca {
        val j = get("/api/arquivos")
        val soltas = ArrayList<Musica>()
        for (k in listOf("musicas", "videos")) {
            val a = j.optJSONArray(k) ?: continue
            for (i in 0 until a.length()) soltas.add(musica(a.getJSONObject(i)))
        }
        val pastas = ArrayList<Pasta>()
        val pl = j.optJSONArray("playlists")
        if (pl != null) {
            for (i in 0 until pl.length()) {
                val p = pl.getJSONObject(i)
                val ia = p.optJSONArray("itens")
                val itens = ArrayList<Musica>()
                if (ia != null) for (n in 0 until ia.length()) itens.add(musica(ia.getJSONObject(n)))
                pastas.add(Pasta(p.optString("nome"), itens))
            }
        }
        soltas.sortByDescending { it.mt }
        pastas.sortBy { it.nome.lowercase() }
        return Biblioteca(j.optString("caminho"), soltas, pastas)
    }

    fun estado(): Fila {
        val j = get("/api/estado")
        val a = j.optJSONArray("itens")
        val itens = ArrayList<ItemFila>()
        if (a != null) for (i in 0 until a.length()) {
            val o = a.getJSONObject(i)
            itens.add(ItemFila(o.optString("id"), o.optString("titulo").ifEmpty { o.optString("url") },
                o.optString("status"), o.optDouble("pct", 0.0), o.optString("vel"), o.optString("erro")))
        }
        return Fila(itens, j.optInt("fila"), j.optInt("baixando"), j.optInt("ok"), j.optInt("falha"),
            j.optInt("pulada"), j.optString("agora"), j.optString("aviso"))
    }

    fun adicionar(texto: String): JSONObject = post("/api/add", JSONObject().put("texto", texto))

    fun acao(acao: String, id: String = ""): JSONObject =
        post("/api/acao", JSONObject().put("acao", acao).put("id", id))

    fun apagar(rels: List<String>): JSONObject =
        post("/api/apagar", JSONObject().put("rels", org.json.JSONArray(rels)))

    // ---- capas (com cache em memória e no máximo 3 pedidos ao mesmo tempo)
    private val cache = LruCache<String, Bitmap>(60)
    private val semaforo = Semaphore(3)
    private val semCapa = HashSet<String>()

    fun capa(rel: String, lado: Int): Bitmap? {
        val chave = "$rel@$lado"
        cache.get(chave)?.let { return it }
        synchronized(semCapa) { if (semCapa.contains(rel)) return null }
        semaforo.acquire()
        try {
            val c = URL(BASE + "/api/capa?f=" + enc(rel)).openConnection() as HttpURLConnection
            c.connectTimeout = 5000
            c.readTimeout = 20000
            try {
                if (c.responseCode != 200) {
                    if (c.responseCode == 404) synchronized(semCapa) { semCapa.add(rel) }
                    return null
                }
                val bytes = c.inputStream.readBytes()
                val o = BitmapFactory.Options().apply { inJustDecodeBounds = true }
                BitmapFactory.decodeByteArray(bytes, 0, bytes.size, o)
                var s = 1
                while (o.outWidth / (s * 2) >= lado && o.outHeight / (s * 2) >= lado) s *= 2
                val o2 = BitmapFactory.Options().apply { inSampleSize = s }
                val b = BitmapFactory.decodeByteArray(bytes, 0, bytes.size, o2) ?: return null
                cache.put(chave, b)
                return b
            } finally {
                c.disconnect()
            }
        } catch (t: Throwable) {
            return null
        } finally {
            semaforo.release()
        }
    }

    fun limparCapa(rel: String) {
        synchronized(semCapa) { semCapa.remove(rel) }
    }
}
