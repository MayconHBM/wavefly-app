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
            try {
                String[] p = Python.getInstance().getModule("app_entry").callAttr("resumo").toString().split("\\|", -1);
                baixando = Integer.parseInt(p[0]);
                fila = Integer.parseInt(p[1]);
                total = Integer.parseInt(p[2]);
            } catch (Throwable ignored) {
            }
            boolean baixandoAlgo = baixando + fila > 0;
            boolean musica = pAtivo;                     // música e vídeo (no vídeo, só o áudio)
            boolean tocandoAlgo = pAtivo && pTocando;    // música ou vídeo: mantém o app acordado
            boolean ativo = baixandoAlgo || tocandoAlgo;

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
        boolean precisa = baixando || musicaTocando;
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
        String chave = (musica ? "m|" + pTitulo + "|" + pSub + "|" + pTocando + "|" + pEm + "|" + (capaBmp != null && capaDe.equals(pCapa)) : "d")
                + "|" + baixando + "|" + feitos + "/" + total + "|" + fixa;
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
            b.setColor(0xFF3B2314).setColorized(true).setShowWhen(false);
            Bitmap cb = capaBmp;
            if (cb != null && capaDe.equals(pCapa)) b.setLargeIcon(cb);
            b.setContentTitle(pTitulo.isEmpty() ? "WaveFly" : pTitulo);
            if (baixando) {
                b.setContentText("Baixando " + contagem);
                b.setProgress(total, Math.min(feitos, total), false);
            } else {
                b.setContentText(pSub);
            }
            b.addAction(acao(ACTION_PREV, R.drawable.ic_n_prev, "Anterior", 5));
            b.addAction(acao(ACTION_PLAY_PAUSE,
                    pTocando ? R.drawable.ic_n_pause : R.drawable.ic_n_play,
                    pTocando ? "Pausar" : "Tocar", 3));
            b.addAction(acao(ACTION_NEXT, R.drawable.ic_n_next, "Próxima", 4));
            if (baixando) b.addAction(acao(ACTION_CANCEL, 0, "Cancelar download", 2));
            Notification.MediaStyle estilo = new Notification.MediaStyle();
            synchronized (this) {
                if (sessao != null) estilo.setMediaSession(sessao.getSessionToken());
            }
            estilo.setShowActionsInCompactView(0, 1, 2);
            b.setStyle(estilo);
        } else {
            b.setContentTitle("Baixando");
            b.setContentText(contagem);
            b.setProgress(total, Math.min(feitos, total), false);
            b.addAction(acao(ACTION_CANCEL, 0, "Cancelar", 2));
        }
        return b.build();
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
                    public void onSeekTo(long pos) {
                        Log.i(TAG, "onSeekTo " + pos);
                        pPosMs = pos;
                        pEm = SystemClock.elapsedRealtime();
                        atualizarSessao();
                        MainActivity.comandoPlayer("seek:" + pos);
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
            if (pDurMs > 0) md.putLong(MediaMetadata.METADATA_KEY_DURATION, pDurMs);
            Bitmap cb = capaBmp;
            if (cb != null && capaDe.equals(pCapa)) md.putBitmap(MediaMetadata.METADATA_KEY_ALBUM_ART, cb);
            sessao.setMetadata(md.build());
            long em = pEm == 0 ? SystemClock.elapsedRealtime() : pEm;
            PlaybackState ps = new PlaybackState.Builder()
                    .setActions(PlaybackState.ACTION_PLAY | PlaybackState.ACTION_PAUSE
                            | PlaybackState.ACTION_PLAY_PAUSE | PlaybackState.ACTION_SKIP_TO_NEXT
                            | PlaybackState.ACTION_SKIP_TO_PREVIOUS | PlaybackState.ACTION_SEEK_TO)
                    .setState(pTocando ? PlaybackState.STATE_PLAYING : PlaybackState.STATE_PAUSED,
                            pPosMs, pTocando ? 1f : 0f, em)
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
