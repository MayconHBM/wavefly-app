package com.wavefly.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

/** Depois de ligar o celular, volta o botão flutuante se ele estava ativado. */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context c, Intent i) {
        try {
            if (Idioma.prefs(c).getBoolean("bolha", false) && Bolha.permitido(c)) {
                Intent s = new Intent(c, PythonService.class);
                if (Build.VERSION.SDK_INT >= 26) c.startForegroundService(s);
                else c.startService(s);
            }
        } catch (Throwable ignored) {
        }
    }
}
