package com.wavefly.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;
import android.util.Log;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

/** Mantém o servidor Python do WaveFly vivo mesmo com o app em segundo plano. */
public class PythonService extends Service {
    static final int PORT = 8773;
    static final String ACTION_STOP = "com.wavefly.app.STOP";
    private static final String CHANNEL = "wavefly";
    private static final String TAG = "WaveFly";

    static volatile String status = "Iniciando…";
    static volatile boolean ready = false;
    static volatile String error = null;
    private static boolean started = false;

    private PowerManager.WakeLock wakeLock;

    @Override
    public void onCreate() {
        super.onCreate();
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= 26 && nm != null) {
            NotificationChannel ch = new NotificationChannel(CHANNEL, "WaveFly", NotificationManager.IMPORTANCE_LOW);
            ch.setDescription("Mantém os downloads funcionando em segundo plano");
            nm.createNotificationChannel(ch);
        }
        startForeground(1, buildNotification());
        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        if (pm != null) {
            wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "WaveFly:downloads");
            wakeLock.setReferenceCounted(false);
            wakeLock.acquire();
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            stopForeground(true);
            stopSelf();
            // encerra o processo inteiro (servidor Python incluso)
            android.os.Process.killProcess(android.os.Process.myPid());
            return START_NOT_STICKY;
        }
        synchronized (PythonService.class) {
            if (!started) {
                started = true;
                new Thread(this::boot, "wavefly-boot").start();
            }
        }
        return START_STICKY;
    }

    private void boot() {
        try {
            status = "Preparando o conversor de áudio…";
            String[] ff = FfmpegSetup.prepare(this);
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

    private Notification buildNotification() {
        Intent open = new Intent(this, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(this, 0, open, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        Intent stop = new Intent(this, PythonService.class).setAction(ACTION_STOP);
        PendingIntent ps = PendingIntent.getService(this, 1, stop, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);

        Notification.Builder b = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(this, CHANNEL)
                : new Notification.Builder(this);
        b.setSmallIcon(R.drawable.ic_notification)
                .setContentTitle("WaveFly")
                .setContentText("Rodando em segundo plano")
                .setContentIntent(pi)
                .setOngoing(true)
                .addAction(new Notification.Action.Builder(null, "Encerrar", ps).build());
        return b.build();
    }

    @Override
    public void onDestroy() {
        if (wakeLock != null && wakeLock.isHeld()) wakeLock.release();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
