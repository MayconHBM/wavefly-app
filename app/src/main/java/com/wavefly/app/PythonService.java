package com.wavefly.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.media.AudioManager;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;
import android.util.Log;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

/**
 * Mantém o servidor Python do WaveFly vivo enquanto há download ou música tocando.
 * - Deslizar o app nos recentes encerra tudo.
 * - Fora da tela e sem fazer nada por 10 minutos, encerra sozinho.
 */
public class PythonService extends Service {
    static final int PORT = 8773;
    static final String ACTION_STOP = "com.wavefly.app.STOP";
    static final String ACTION_CANCEL = "com.wavefly.app.CANCEL";
    private static final String CHANNEL = "wavefly";
    private static final long OCIOSO_MS = 10 * 60 * 1000L;
    private static final String TAG = "WaveFly";

    static volatile String status = "Iniciando…";
    static volatile boolean ready = false;
    static volatile String error = null;
    static volatile String ffmpegInfo = "";
    static volatile boolean visivel = false;
    private static boolean started = false;

    private PowerManager.WakeLock wakeLock;
    private volatile boolean rodando = true;
    private String ultimoTexto = "";

    @Override
    public void onCreate() {
        super.onCreate();
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= 26 && nm != null) {
            NotificationChannel ch = new NotificationChannel(CHANNEL, "WaveFly", NotificationManager.IMPORTANCE_LOW);
            ch.setDescription("Mostra o andamento dos downloads");
            ch.setShowBadge(false);
            nm.createNotificationChannel(ch);
        }
        startForeground(1, buildNotification("WaveFly", "Aberto", -1));
        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        if (pm != null) {
            wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "WaveFly:downloads");
            wakeLock.setReferenceCounted(false);
        }
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
        synchronized (PythonService.class) {
            if (!started) {
                started = true;
                new Thread(this::boot, "wavefly-boot").start();
                new Thread(this::vigiar, "wavefly-watch").start();
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
        stopForeground(true);
        stopSelf();
        android.os.Process.killProcess(android.os.Process.myPid());
    }

    private void boot() {
        try {
            status = "Preparando o conversor de áudio…";
            String[] ff = FfmpegSetup.prepare(this);
            if (ff != null && ff.length > 2) ffmpegInfo = ff[2];
            status = "Iniciando o WaveFly…";
            if (!Python.isStarted()) {
                Python.start(new AndroidPlatform(this));
            }
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

    /** A cada poucos segundos: atualiza a notificação e controla o encerramento por inatividade. */
    private void vigiar() {
        long ociosoDesde = 0;
        while (rodando) {
            try {
                Thread.sleep(3000);
            } catch (InterruptedException e) {
                return;
            }
            if (!ready) continue;
            int baixando = 0, fila = 0, total = 0, pct = 0;
            String vel = "", titulo = "";
            try {
                String[] p = Python.getInstance().getModule("app_entry").callAttr("resumo").toString().split("\\|", -1);
                baixando = Integer.parseInt(p[0]);
                fila = Integer.parseInt(p[1]);
                total = Integer.parseInt(p[2]);
                pct = Integer.parseInt(p[3]);
                vel = p[4];
                titulo = p[5];
            } catch (Throwable ignored) {
            }
            AudioManager am = (AudioManager) getSystemService(Context.AUDIO_SERVICE);
            boolean tocando = am != null && am.isMusicActive();
            boolean ativo = baixando > 0 || fila > 0 || tocando;

            if (ativo) {
                if (wakeLock != null && !wakeLock.isHeld()) wakeLock.acquire(60 * 60 * 1000L);
            } else if (wakeLock != null && wakeLock.isHeld()) {
                wakeLock.release();
            }

            String t1, t2;
            int prog = -1;
            if (baixando > 0 || fila > 0) {
                t1 = "Baixando " + (baixando + fila) + (baixando + fila == 1 ? " item" : " itens");
                t2 = (titulo.isEmpty() ? "" : titulo + " · ") + pct + "%" + (vel.isEmpty() ? "" : " · " + vel);
                prog = pct;
            } else if (tocando) {
                t1 = "WaveFly";
                t2 = "Tocando música";
            } else {
                t1 = "WaveFly";
                t2 = visivel ? "Aberto" : "Em espera";
            }
            String chave = t1 + "|" + t2 + "|" + prog;
            if (!chave.equals(ultimoTexto)) {
                ultimoTexto = chave;
                NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
                if (nm != null) nm.notify(1, buildNotification(t1, t2, prog, baixando + fila > 0));
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

    private Notification buildNotification(String titulo, String texto, int progresso) {
        return buildNotification(titulo, texto, progresso, false);
    }

    private Notification buildNotification(String titulo, String texto, int progresso, boolean comCancelar) {
        Intent open = new Intent(this, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(this, 0, open, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        Intent cancel = new Intent(this, PythonService.class).setAction(ACTION_CANCEL);
        PendingIntent pc = PendingIntent.getService(this, 2, cancel, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        Intent stop = new Intent(this, PythonService.class).setAction(ACTION_STOP);
        PendingIntent ps = PendingIntent.getService(this, 1, stop, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);

        Notification.Builder b = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(this, CHANNEL)
                : new Notification.Builder(this);
        b.setSmallIcon(R.drawable.ic_notification)
                .setContentTitle(titulo)
                .setContentText(texto)
                .setContentIntent(pi)
                .setOnlyAlertOnce(true)
                .setOngoing(true);
        if (progresso >= 0) b.setProgress(100, progresso, false);
        if (comCancelar) {
            b.addAction(new Notification.Action.Builder(null, "Cancelar", pc).build());
        }
        b.addAction(new Notification.Action.Builder(null, "Encerrar", ps).build());
        return b.build();
    }

    @Override
    public void onDestroy() {
        rodando = false;
        if (wakeLock != null && wakeLock.isHeld()) wakeLock.release();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
