package com.wavefly.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.drawable.Icon;
import android.media.MediaMetadata;
import android.media.session.MediaSession;
import android.media.session.PlaybackState;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;
import android.os.SystemClock;
import android.util.Log;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

/**
 * Mantém o servidor Python do WaveFly vivo enquanto há download ou música tocando.
 *
 * Notificação (só aparece quando faz sentido):
 * - baixando: "Baixando" com a contagem (ex.: 3/10);
 * - tocando música (vídeo não): player com anterior / tocar-pausar / próxima;
 * - os dois ao mesmo tempo: uma notificação só, com o player e a contagem do download.
 * Sem download e sem música, não há notificação nenhuma.
 *
 * - Deslizar o app nos recentes encerra tudo.
 * - Fora da tela e sem fazer nada por 10 minutos, encerra sozinho.
 */
public class PythonService extends Service {
    static final int PORT = 8773;
    static final String ACTION_STOP = "com.wavefly.app.STOP";
    static final String ACTION_CANCEL = "com.wavefly.app.CANCEL";
    static final String ACTION_PLAY_PAUSE = "com.wavefly.app.PLAY_PAUSE";
    static final String ACTION_NEXT = "com.wavefly.app.NEXT";
    static final String ACTION_PREV = "com.wavefly.app.PREV";
    static final String ACTION_BACK10 = "com.wavefly.app.BACK10";
    static final String ACTION_FWD10 = "com.wavefly.app.FWD10";
    static final String ACTION_PAUSA_DL = "com.wavefly.app.PAUSA_DL";
    static final String ACTION_DISPENSADA = "com.wavefly.app.DISPENSADA";

    private static final String CHANNEL = "wavefly";
    private static final int NOTIF_ID = 1;
    private static final long OCIOSO_MS = 10 * 60 * 1000L;
    /** Depois que não há mais o que manter em primeiro plano, espera um pouco antes de soltar. */
    private static final long GRACA_MS = 8000L;
    private static final String TAG = "WaveFly";

    static volatile String status = "Iniciando…";
    static volatile boolean ready = false;
    static volatile String error = null;
    static volatile String ffmpegInfo = "";
    static volatile boolean visivel = false;
    private static boolean started = false;

    // Estado do player, enviado pela página (MainActivity.Ponte.player)
    static volatile boolean pAtivo = false;     // existe uma faixa carregada no player
    static volatile boolean pTocando = false;
    static volatile boolean pVideo = false;
    static volatile String pTitulo = "";
    static volatile String pSub = "";
    static volatile long pPosMs = 0;
    static volatile long pDurMs = 0;
    static volatile long pEm = 0;               // SystemClock.elapsedRealtime() do último aviso
    static volatile String pCapa = "";          // caminho relativo do arquivo (para buscar a capa)
    private volatile Bitmap capaBmp = null;
    private volatile String capaDe = "";
    private volatile String capaBuscando = "";

    private PowerManager.WakeLock wakeLock;
    private volatile boolean rodando = true;
    private Thread vigia;
    private MediaSession sessao;
    private boolean emPrimeiroPlano = false;
    private long semUsoDesde = 0;
    private String ultimaChave = "";
    static volatile boolean dlPausado = false;

    @Override
    public void onCreate() {
        super.onCreate();
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= 26 && nm != null) {
            NotificationChannel ch = new NotificationChannel(CHANNEL, "WaveFly", NotificationManager.IMPORTANCE_LOW);
            ch.setDescription("Downloads e player");
            ch.setShowBadge(false);
            nm.createNotificationChannel(ch);
        }
        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        if (pm != null) {
            wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "WaveFly:downloads");
            wakeLock.setReferenceCounted(false);
        }
        vigia = new Thread(this::vigiar, "wavefly-watch");
        vigia.start();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String act = intent == null ? null : intent.getAction();
        if (ACTION_STOP.equals(act)) {
            encerrar();
            return START_NOT_STICKY;
        }
        if (ACTION_CANCEL.equals(act)) {
            new Thread(() -> {
                try {
                    Python.getInstance().getModule("app_entry").callAttr("cancelar_tudo");
                } catch (Throwable ignored) {
                }
            }).start();
            return START_STICKY;
        }
        if (ACTION_PAUSA_DL.equals(act)) {
            final boolean novo = !dlPausado;
            dlPausado = novo;
            new Thread(() -> {
                try {
                    Python.getInstance().getModule("app_entry").callAttr("pausar", novo);
                } catch (Throwable ignored) {
                }
            }).start();
            return START_STICKY;
        }
        if (ACTION_BACK10.equals(act) || ACTION_FWD10.equals(act)) {
            // A página faz a conta com a posição real do áudio (a nossa pode estar atrasada).
            int passo = passoSeg();
            long novo = posAgora() + (ACTION_FWD10.equals(act) ? passo * 1000L : -passo * 1000L);
            pPosMs = Math.max(0, pDurMs > 0 ? Math.min(novo, pDurMs) : novo);
            pEm = SystemClock.elapsedRealtime();
            MainActivity.comandoPlayer(ACTION_FWD10.equals(act) ? "rel:" + passo : "rel:-" + passo);
            ultimaChave = "";
            return START_STICKY;
        }
        if (ACTION_DISPENSADA.equals(act)) {
            // O usuário arrastou a notificação (só dá com a música pausada): para o player de vez.
            MainActivity.comandoPlayer("stop");
            pAtivo = false;
            pTocando = false;
            ultimaChave = "";
            return START_STICKY;
        }
        if (ACTION_PLAY_PAUSE.equals(act)) {
            MainActivity.comandoPlayer(pTocando ? "pause" : "play");
            return START_STICKY;
        }
        if (ACTION_NEXT.equals(act)) {
            MainActivity.comandoPlayer("next");
            return START_STICKY;
        }
        if (ACTION_PREV.equals(act)) {
            MainActivity.comandoPlayer("prev");
            return START_STICKY;
        }
        synchronized (PythonService.class) {
            if (!started) {
                started = true;
                new Thread(this::boot, "wavefly-boot").start();
            }
        }
        return START_STICKY;
    }

    /** O usuário deslizou o app nos recentes: encerra tudo. */
    @Override
    public void onTaskRemoved(Intent rootIntent) {
        encerrar();
    }

    private void encerrar() {
        rodando = false;
        try {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (nm != null) nm.cancel(NOTIF_ID);
        } catch (Throwable ignored) {
        }
        fecharSessao();
        pararPrimeiroPlano(true);
        stopSelf();
        android.os.Process.killProcess(android.os.Process.myPid());
    }

    private void boot() {
        try {
            status = "Iniciando o Python…";
            if (!Python.isStarted()) {
                Python.start(new AndroidPlatform(this));
            }
            status = "Preparando o conversor de áudio…";
            String[] ff = FfmpegSetup.prepare(this);
            if (ff != null && ff.length > 2) ffmpegInfo = ff[2];
            status = "Iniciando o WaveFly…";
            PyObject mod = Python.getInstance().getModule("app_entry");
            PyObject r = mod.callAttr("start",
                    getFilesDir().getAbsolutePath(),
                    ff == null ? "" : ff[0],
                    ff == null ? "" : ff[1],
                    PORT);
            String err = r == null ? "" : r.toString();
            if (err.isEmpty()) {
                ready = true;
                status = "Pronto";
            } else {
                error = err;
                started = false;
                Log.e(TAG, err);
            }
        } catch (Throwable t) {
            error = t.toString();
            started = false;
            Log.e(TAG, "Falha ao iniciar", t);
        }
    }

    /** A cada segundo: atualiza a notificação e controla o encerramento por inatividade. */
    private void vigiar() {
        long ociosoDesde = 0;
        while (rodando) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                return;
            }
            if (!ready) continue;
            int baixando = 0, fila = 0, total = 0;
            boolean pausado = false;
            try {
                String[] p = Python.getInstance().getModule("app_entry").callAttr("resumo").toString().split("\\|", -1);
                baixando = Integer.parseInt(p[0]);
                fila = Integer.parseInt(p[1]);
                total = Integer.parseInt(p[2]);
                pausado = p.length > 6 && p[6].equals("1");
                dlPausado = pausado;
            } catch (Throwable ignored) {
            }
            boolean baixandoAlgo = baixando + fila > 0;
            boolean musica = pAtivo;                     // música e vídeo (no vídeo, só o áudio)
            boolean tocandoAlgo = pAtivo && pTocando;    // música ou vídeo: mantém o app acordado
            boolean ativo = baixando > 0 || (fila > 0 && !pausado) || tocandoAlgo;

            if (ativo) {
                if (wakeLock != null && !wakeLock.isHeld()) wakeLock.acquire(60 * 60 * 1000L);
            } else if (wakeLock != null && wakeLock.isHeld()) {
                wakeLock.release();
            }

            try {
                atualizarNotificacao(baixandoAlgo, musica, musica && pTocando, Math.max(0, total - baixando - fila), total);
            } catch (Throwable t) {
                Log.w(TAG, "notificação", t);
            }

            if (visivel || ativo) {
                ociosoDesde = 0;
            } else {
                if (ociosoDesde == 0) ociosoDesde = System.currentTimeMillis();
                if (System.currentTimeMillis() - ociosoDesde > OCIOSO_MS) {
                    encerrar();
                    return;
                }
            }
        }
    }

    private void atualizarNotificacao(boolean baixando, boolean musica, boolean musicaTocando, int feitos, int total) {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (nm == null) return;

        // Nada para mostrar: tira a notificação.
        if (!baixando && !musica) {
            semUsoDesde = 0;
            if (emPrimeiroPlano) pararPrimeiroPlano(true);
            else if (!ultimaChave.isEmpty()) nm.cancel(NOTIF_ID);
            ultimaChave = "";
            fecharSessao();
            return;
        }

        // Em primeiro plano enquanto baixa ou toca música; ao parar, espera um pouco antes de soltar
        // (evita sobe-e-desce na troca de faixa/download).
        long agora = System.currentTimeMillis();
        boolean precisa = (baixando && !dlPausado) || musicaTocando;
        boolean fixa;
        if (precisa) {
            semUsoDesde = 0;
            fixa = true;
        } else if (emPrimeiroPlano) {
            if (semUsoDesde == 0) semUsoDesde = agora;
            fixa = agora - semUsoDesde < GRACA_MS;
        } else {
            fixa = false;
        }

        if (musica) buscarCapa(pCapa);
        // A posição entra na chave só em segundos: no máximo uma atualização por segundo (o Android descarta o excesso).
        String chave = (dlPausado ? "P|" : "") + (musica ? "m|" + pTitulo + "|" + pSub + "|" + pTocando + "|" + (posAgora() / 1000) + "|" + (capaBmp != null && capaDe.equals(pCapa)) : "d")
                + "|" + baixando + "|" + feitos + "/" + total + "|" + fixa + "|" + estiloCapa() + "|" + passoSeg();
        if (chave.equals(ultimaChave) && fixa == emPrimeiroPlano) return;

        Notification n = montar(baixando, musica, feitos, total, fixa);
        try {
            if (fixa && !emPrimeiroPlano) {
                startForeground(NOTIF_ID, n);
                emPrimeiroPlano = true;
            } else if (!fixa && emPrimeiroPlano) {
                pararPrimeiroPlano(false);
                nm.notify(NOTIF_ID, n);
            } else {
                nm.notify(NOTIF_ID, n);
            }
        } catch (Throwable t) {
            // Se o Android não deixar subir para primeiro plano (app em segundo plano), mostra mesmo assim.
            Log.w(TAG, "primeiro plano", t);
            try {
                nm.notify(NOTIF_ID, n);
            } catch (Throwable ignored) {
            }
        }
        ultimaChave = chave;
    }

    /** Posição atual da faixa (a última informada pela página + o tempo que passou, se estiver tocando). */
    private long posAgora() {
        long cur = pPosMs;
        if (pTocando && pEm != 0) cur += SystemClock.elapsedRealtime() - pEm;
        if (pDurMs > 0 && cur > pDurMs) cur = pDurMs;
        return Math.max(0, cur);
    }

    private static String fmt(long ms) {
        long s = ms / 1000;
        return (s / 60) + ":" + (s % 60 < 10 ? "0" : "") + (s % 60);
    }

    private Notification montar(boolean baixando, boolean musica, int feitos, int total, boolean fixa) {
        Intent open = new Intent(this, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(this, 0, open,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);

        Notification.Builder b = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(this, CHANNEL)
                : new Notification.Builder(this);
        b.setSmallIcon(R.drawable.ic_notification)
                .setContentIntent(pi)
                .setOnlyAlertOnce(true)
                .setOngoing(fixa)
                .setVisibility(Notification.VISIBILITY_PUBLIC);

        String contagem = feitos + "/" + total;
        if (musica) {
            atualizarSessao();
            if (estiloCapa().equals("fundo") && capaBmp != null && capaDe.equals(pCapa)) prepararFundo(capaBmp);
            b.setColor(estiloCapa().equals("fundo") && fundoCor != 0 && fundoDe.equals(capaDe) ? fundoCor : 0xFF3B2314).setColorized(true).setShowWhen(false);
            b.setContentTitle(pTitulo.isEmpty() ? "WaveFly" : pTitulo);
            b.setContentText(pSub);
            b.setDeleteIntent(PendingIntent.getService(this, 9,
                    new Intent(this, PythonService.class).setAction(ACTION_DISPENSADA),
                    PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT));
            String est = estiloCapa();
            int lg = est.equals("dir") ? R.layout.notif_player_dir : est.equals("fundo") ? R.layout.notif_player_fundo : R.layout.notif_player;
            int lp = est.equals("dir") ? R.layout.notif_player_small_dir : est.equals("fundo") ? R.layout.notif_player_small_fundo : R.layout.notif_player_small;
            android.widget.RemoteViews rv = visaoMusica(lg, baixando, feitos, total, contagem, true, est);
            android.widget.RemoteViews rvp = visaoMusica(lp, baixando, feitos, total, contagem, false, est);
            b.setStyle(new Notification.DecoratedCustomViewStyle());
            b.setCustomContentView(rvp);
            b.setCustomBigContentView(rv);
        } else {
            b.setContentTitle(dlPausado ? Idioma.t(this, "Downloads pausados", "Downloads paused", "Descargas en pausa")
                    : Idioma.t(this, "Baixando", "Downloading", "Descargando"));
            b.setContentText(contagem);
            if (!dlPausado) b.setProgress(total, Math.min(feitos, total), false);
            b.addAction(acao(ACTION_PAUSA_DL, 0, dlPausado ? Idioma.t(this, "Continuar", "Resume", "Continuar")
                    : Idioma.t(this, "Pausar", "Pause", "Pausar"), 8));
            b.addAction(acao(ACTION_CANCEL, 0, Idioma.t(this, "Cancelar", "Cancel", "Cancelar"), 2));
        }
        return b.build();
    }

    private volatile Bitmap fundoBmp = null;
    private volatile String fundoDe = "";
    private volatile int fundoCor = 0;

    /** "esq", "dir" ou "fundo": onde fica a capa na notificação (escolhido no painel do desenvolvedor). */
    private String estiloCapa() {
        String v = Idioma.prefs(this).getString("p_capa", "esq");
        return "dir".equals(v) || "fundo".equals(v) ? v : "esq";
    }

    /** Tamanho do pulo dos botões (10, 15 ou 30 segundos). */
    private int passoSeg() {
        try {
            int n = Integer.parseInt(Idioma.prefs(this).getString("p_passo", "10"));
            if (n == 15 || n == 30) return n;
        } catch (Throwable ignored) {
        }
        return 10;
    }

    /** Fundo estilo YouTube Music: cor escura tirada da capa, com a capa nítida à direita esmaecendo para a esquerda. */
    private void prepararFundo(Bitmap src) {
        if (src == null || fundoDe.equals(capaDe)) return;
        try {
            int w = 720, h = 264, cw = 330;          // área total e largura da capa à direita
            float sa = (float) src.getWidth() / src.getHeight(), da = (float) cw / h;
            int sx, sy, sw, sh;
            if (sa > da) { sh = src.getHeight(); sw = (int) (sh * da); sx = (src.getWidth() - sw) / 2; sy = 0; }
            else { sw = src.getWidth(); sh = (int) (sw / da); sx = 0; sy = (src.getHeight() - sh) / 2; }
            Bitmap corte = Bitmap.createBitmap(src, sx, sy, Math.max(1, sw), Math.max(1, sh));
            int px = Bitmap.createScaledBitmap(src, 1, 1, true).getPixel(0, 0);
            int cor = 0xFF000000 | (((px >> 16 & 0xFF) * 32 / 100) << 16) | (((px >> 8 & 0xFF) * 32 / 100) << 8) | ((px & 0xFF) * 32 / 100);
            Bitmap out = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
            android.graphics.Canvas c = new android.graphics.Canvas(out);
            c.drawColor(cor);
            android.graphics.Paint p = new android.graphics.Paint(android.graphics.Paint.FILTER_BITMAP_FLAG | android.graphics.Paint.ANTI_ALIAS_FLAG);
            c.drawBitmap(corte, null, new android.graphics.Rect(w - cw, 0, w, h), p);
            p.setShader(new android.graphics.LinearGradient(w - cw, 0, w - cw * 0.35f, 0, cor, cor & 0x00FFFFFF, android.graphics.Shader.TileMode.CLAMP));
            c.drawRect(w - cw, 0, w, h, p);
            fundoCor = cor;
            fundoBmp = out;
            fundoDe = capaDe;
        } catch (Throwable t) {
            fundoBmp = null;
            fundoDe = capaDe;
            fundoCor = 0;
        }
    }

    private PendingIntent pend(String action, int codigo) {
        return PendingIntent.getService(this, codigo, new Intent(this, PythonService.class).setAction(action),
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
    }

    /** Layout próprio da notificação do player (sem a barra do sistema): capa, título, barra laranja e botões. */
    private android.widget.RemoteViews visaoMusica(int layout, boolean baixando, int feitos, int total, String contagem, boolean grande, String est) {
        android.widget.RemoteViews rv = new android.widget.RemoteViews(getPackageName(), layout);
        rv.setTextViewText(R.id.n_titulo, pTitulo.isEmpty() ? "WaveFly" : pTitulo);
        long pos = posAgora();
        Bitmap cb = capaBmp;
        boolean temCapa = cb != null && capaDe.equals(pCapa);
        if (est.equals("fundo")) {
            if (temCapa) {
                prepararFundo(cb);
                if (fundoBmp != null && fundoDe.equals(capaDe)) rv.setImageViewBitmap(R.id.n_fundo, fundoBmp);
            } else {
                rv.setImageViewResource(R.id.n_fundo, R.drawable.ic_notification);
            }
        } else if (temCapa) {
            rv.setImageViewBitmap(R.id.n_capa, cb);
        } else {
            rv.setImageViewResource(R.id.n_capa, R.drawable.ic_notification);
        }
        if (grande) {
            rv.setTextViewText(R.id.n_sub, pSub);
            rv.setTextViewText(R.id.n_t1, fmt(pos));
            rv.setTextViewText(R.id.n_t2, pDurMs > 0 ? fmt(pDurMs) : "");
            rv.setViewVisibility(R.id.n_linha_prog, pDurMs > 0 ? android.view.View.VISIBLE : android.view.View.GONE);
            rv.setTextViewText(R.id.n_b10t, String.valueOf(passoSeg()));
            rv.setTextViewText(R.id.n_f10t, String.valueOf(passoSeg()));
            rv.setOnClickPendingIntent(R.id.n_b10, pend(ACTION_BACK10, 6));
            rv.setOnClickPendingIntent(R.id.n_f10, pend(ACTION_FWD10, 7));
            rv.setOnClickPendingIntent(R.id.n_x, pend(ACTION_DISPENSADA, 10));
            if (baixando && total > 0) {
                rv.setViewVisibility(R.id.n_dl, android.view.View.VISIBLE);
                rv.setProgressBar(R.id.n_dl, total, Math.min(feitos, total), false);
                rv.setTextViewText(R.id.n_dltxt, Idioma.t(this, "Baixando ", "Downloading ", "Descargando ") + contagem);
                rv.setViewVisibility(R.id.n_dltxt, android.view.View.VISIBLE);
            } else {
                rv.setViewVisibility(R.id.n_dl, android.view.View.GONE);
                rv.setViewVisibility(R.id.n_dltxt, android.view.View.GONE);
            }
        } else {
            String sub = pSub;
            if (baixando && total > 0) sub = (sub.isEmpty() ? "" : sub + " · ") + contagem;
            rv.setTextViewText(R.id.n_sub, sub);
        }
        if (pDurMs > 0) {
            rv.setViewVisibility(R.id.n_prog, android.view.View.VISIBLE);
            rv.setProgressBar(R.id.n_prog, (int) (pDurMs / 1000), (int) (pos / 1000), false);
        } else {
            rv.setViewVisibility(R.id.n_prog, android.view.View.GONE);
        }
        rv.setOnClickPendingIntent(R.id.n_prev, pend(ACTION_PREV, 5));
        rv.setOnClickPendingIntent(R.id.n_next, pend(ACTION_NEXT, 4));
        rv.setOnClickPendingIntent(R.id.n_play, pend(ACTION_PLAY_PAUSE, 3));
        rv.setImageViewResource(R.id.n_play, pTocando ? R.drawable.ic_n_pause : R.drawable.ic_n_play);
        return rv;
    }

    private Notification.Action acao(String action, int iconeRes, String titulo, int codigo) {
        Intent i = new Intent(this, PythonService.class).setAction(action);
        PendingIntent p = PendingIntent.getService(this, codigo, i,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        Icon icone = iconeRes == 0 ? null : Icon.createWithResource(this, iconeRes);
        return new Notification.Action.Builder(icone, titulo, p).build();
    }

    /** Sessão de mídia: dá os botões na tela de bloqueio / fone Bluetooth e o visual de player. */
    private synchronized void atualizarSessao() {
        try {
            if (sessao == null) {
                sessao = new MediaSession(this, "WaveFly");
                sessao.setCallback(new MediaSession.Callback() {
                    @Override
                    public void onPlay() {
                        MainActivity.comandoPlayer("play");
                    }

                    @Override
                    public void onPause() {
                        MainActivity.comandoPlayer("pause");
                    }

                    @Override
                    public void onSkipToNext() {
                        MainActivity.comandoPlayer("next");
                    }

                    @Override
                    public void onSkipToPrevious() {
                        MainActivity.comandoPlayer("prev");
                    }
                });
            }
            sessao.setActive(true);
            MediaMetadata.Builder md = new MediaMetadata.Builder()
                    .putString(MediaMetadata.METADATA_KEY_TITLE, pTitulo)
                    .putString(MediaMetadata.METADATA_KEY_ARTIST, pSub);
            Bitmap cb = capaBmp;
            if (cb != null && capaDe.equals(pCapa)) md.putBitmap(MediaMetadata.METADATA_KEY_ALBUM_ART, cb);
            sessao.setMetadata(md.build());
                        long em = pEm == 0 ? SystemClock.elapsedRealtime() : pEm;
            long posAtual = pPosMs;
            if (pTocando && pEm != 0) {
                posAtual = pPosMs + (SystemClock.elapsedRealtime() - pEm);
                if (pDurMs > 0 && posAtual > pDurMs) posAtual = pDurMs;
            }
            PlaybackState ps = new PlaybackState.Builder()
                    .setActions(PlaybackState.ACTION_PLAY | PlaybackState.ACTION_PAUSE
                            | PlaybackState.ACTION_PLAY_PAUSE | PlaybackState.ACTION_SKIP_TO_NEXT
                            | PlaybackState.ACTION_SKIP_TO_PREVIOUS)
                    .setState(pTocando ? PlaybackState.STATE_PLAYING : PlaybackState.STATE_PAUSED,
                            posAtual, pTocando ? 1f : 0f, em)
                    .build();
            sessao.setPlaybackState(ps);
        } catch (Throwable t) {
            Log.w(TAG, "sessão de mídia", t);
        }
    }

    private synchronized void fecharSessao() {
        if (sessao == null) return;
        try {
            sessao.setActive(false);
            sessao.release();
        } catch (Throwable ignored) {
        }
        sessao = null;
    }

    /** Baixa a capa da faixa atual do servidor local (em segundo plano) e guarda para a notificação. */
    private void buscarCapa(final String rel) {
        if (rel == null || rel.isEmpty() || rel.equals(capaDe) || rel.equals(capaBuscando)) return;
        capaBuscando = rel;
        new Thread(() -> {
            Bitmap bmp = null;
            try {
                java.net.URL u = new java.net.URL("http://127.0.0.1:" + PORT + "/api/capa?f="
                        + java.net.URLEncoder.encode(rel, "UTF-8"));
                java.net.HttpURLConnection c = (java.net.HttpURLConnection) u.openConnection();
                c.setConnectTimeout(3000);
                c.setReadTimeout(8000);
                java.io.InputStream in = c.getInputStream();
                java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
                byte[] buf = new byte[16384];
                int n;
                while ((n = in.read(buf)) > 0 && bo.size() < 6_000_000) bo.write(buf, 0, n);
                in.close();
                byte[] dados = bo.toByteArray();
                BitmapFactory.Options o = new BitmapFactory.Options();
                o.inJustDecodeBounds = true;
                BitmapFactory.decodeByteArray(dados, 0, dados.length, o);
                int lado = Math.max(o.outWidth, o.outHeight), amostra = 1;
                while (lado / amostra > 600) amostra *= 2;
                o = new BitmapFactory.Options();
                o.inSampleSize = amostra;
                bmp = BitmapFactory.decodeByteArray(dados, 0, dados.length, o);
            } catch (Throwable t) {
                Log.w(TAG, "capa da notificação", t);
            }
            capaBmp = bmp;
            capaDe = rel;
            capaBuscando = "";
        }, "wavefly-capa").start();
    }

    private void pararPrimeiroPlano(boolean removerNotificacao) {
        try {
            stopForeground(removerNotificacao ? Service.STOP_FOREGROUND_REMOVE : Service.STOP_FOREGROUND_DETACH);
        } catch (Throwable ignored) {
        }
        emPrimeiroPlano = false;
    }

    @Override
    public void onDestroy() {
        rodando = false;
        if (vigia != null) vigia.interrupt();
        fecharSessao();
        if (wakeLock != null && wakeLock.isHeld()) wakeLock.release();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
