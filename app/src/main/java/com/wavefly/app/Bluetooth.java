package com.wavefly.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.media.AudioManager;
import android.util.Log;

/**
 * Pausa a música quando o som deixaria de sair pelo aparelho atual
 * (Bluetooth desconectado ou fone com fio tirado), em vez de voltar para o alto-falante.
 */
final class Bluetooth {
    private static final String TAG = "WaveFlyBT";
    private static BroadcastReceiver receptor;

    private Bluetooth() {
    }

    static synchronized void registrar(final Context ctx) {
        if (receptor != null) return;
        final Context app = ctx.getApplicationContext();
        receptor = new BroadcastReceiver() {
            @Override
            public void onReceive(Context c, Intent it) {
                if (AudioManager.ACTION_AUDIO_BECOMING_NOISY.equals(it.getAction())) {
                    MainActivity.comandoPlayer("pause");
                }
            }
        };
        try {
            app.registerReceiver(receptor, new IntentFilter(AudioManager.ACTION_AUDIO_BECOMING_NOISY));
        } catch (Throwable t) {
            Log.w(TAG, "registrar", t);
            receptor = null;
        }
    }

    static synchronized void soltar(Context ctx) {
        if (receptor == null) return;
        try {
            ctx.getApplicationContext().unregisterReceiver(receptor);
        } catch (Throwable ignored) {
        }
        receptor = null;
    }
}
