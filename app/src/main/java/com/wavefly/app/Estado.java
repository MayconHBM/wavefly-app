package com.wavefly.app;

import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Build;
import android.os.PowerManager;

/** Estado do aparelho (bateria, temperatura, rede), lido pelo Python para as condições de download e o relatório do lote. */
public final class Estado {
    private Estado() {
    }

    public static String json(Context c) {
        try {
            Intent b = c.registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
            int nivel = b == null ? -1 : b.getIntExtra("level", -1);
            int esc = b == null ? 100 : b.getIntExtra("scale", 100);
            int st = b == null ? 0 : b.getIntExtra("status", 0);
            int temp = b == null ? 0 : b.getIntExtra("temperature", 0);      // décimos de °C
            boolean carregando = st == 2 || st == 5;
            int termico = 0;
            if (Build.VERSION.SDK_INT >= 29) {
                PowerManager pm = (PowerManager) c.getSystemService(Context.POWER_SERVICE);
                if (pm != null) termico = pm.getCurrentThermalStatus();
            }
            String rede = "offline";
            ConnectivityManager cm = (ConnectivityManager) c.getSystemService(Context.CONNECTIVITY_SERVICE);
            NetworkInfo ni = cm == null ? null : cm.getActiveNetworkInfo();
            if (ni != null && ni.isConnected())
                rede = ni.getType() == ConnectivityManager.TYPE_WIFI ? "Wi-Fi" : "móvel";
            return "{\"bat\":" + (nivel < 0 ? 0 : nivel * 100 / Math.max(1, esc)) + ",\"carregando\":" + carregando
                    + ",\"temp\":" + (temp / 10.0) + ",\"termico\":" + termico + ",\"rede\":\"" + rede + "\"}";
        } catch (Throwable t) {
            return "{}";
        }
    }
}
