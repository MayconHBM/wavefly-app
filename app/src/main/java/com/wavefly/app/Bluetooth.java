package com.wavefly.app;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothClass;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothProfile;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.media.AudioManager;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

/**
 * Bluetooth: toca ao conectar um aparelho marcado e pausa quando o som deixa de sair pelo aparelho
 * (Bluetooth desconectado ou fone com fio tirado). Só funciona com o app aberto ou em segundo plano.
 */
final class Bluetooth {
    private static final String TAG = "WaveFlyBT";
    private static final long ESPERA_MS = 2500;
    private static BroadcastReceiver receptor;
    private static long ultimoGatilho = 0;
    private static final Handler H = new Handler(Looper.getMainLooper());

    private Bluetooth() {
    }

    static boolean ligado(Context c) {
        return "1".equals(Idioma.prefs(c).getString("p_bt_on", ""));
    }

    static Set<String> marcados(Context c) {
        String s = Idioma.prefs(c).getString("p_bt_devs", "");
        Set<String> r = new HashSet<>();
        if (!s.isEmpty()) r.addAll(Arrays.asList(s.split(",")));
        return r;
    }

    /** Aparelhos já pareados que tocam áudio, como JSON [{"n":nome,"a":endereço}]. */
    static String listaPareados() {
        JSONArray arr = new JSONArray();
        try {
            BluetoothAdapter ad = BluetoothAdapter.getDefaultAdapter();
            if (ad != null) {
                Set<BluetoothDevice> bs = ad.getBondedDevices();
                if (bs != null) {
                    for (BluetoothDevice d : bs) {
                        BluetoothClass bc = d.getBluetoothClass();
                        if (bc != null && bc.getMajorDeviceClass() != BluetoothClass.Device.Major.AUDIO_VIDEO) continue;
                        String nome = d.getName();
                        JSONObject o = new JSONObject();
                        o.put("n", nome == null || nome.isEmpty() ? d.getAddress() : nome);
                        o.put("a", d.getAddress());
                        arr.put(o);
                    }
                }
            }
        } catch (Throwable t) {
            Log.w(TAG, "lista de pareados", t);
        }
        return arr.toString();
    }

    static synchronized void registrar(final Context ctx) {
        if (receptor != null) return;
        final Context app = ctx.getApplicationContext();
        receptor = new BroadcastReceiver() {
            @Override
            public void onReceive(Context c, Intent it) {
                try {
                    String act = it.getAction();
                    if (act == null) return;
                    if (AudioManager.ACTION_AUDIO_BECOMING_NOISY.equals(act)) {
                        // o som ia sair pelo alto-falante: Bluetooth caiu ou o fone foi tirado
                        MainActivity.comandoPlayer("pause");
                        return;
                    }
                    BluetoothDevice d = it.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                    if (d == null || !ligado(app)) return;
                    boolean conectou = BluetoothDevice.ACTION_ACL_CONNECTED.equals(act)
                            || (act.equals("android.bluetooth.a2dp.profile.action.CONNECTION_STATE_CHANGED")
                            && it.getIntExtra(BluetoothProfile.EXTRA_STATE, -1) == BluetoothProfile.STATE_CONNECTED);
                    if (!conectou || !marcados(app).contains(d.getAddress())) return;
                    long agora = SystemClock.elapsedRealtime();
                    if (agora - ultimoGatilho < 8000) return;
                    ultimoGatilho = agora;
                    Log.i(TAG, "conectou " + d.getAddress());
                    // espera o áudio do aparelho ficar pronto antes de começar
                    H.postDelayed(() -> MainActivity.comandoPlayer("btplay"), ESPERA_MS);
                } catch (Throwable t) {
                    Log.w(TAG, "receptor", t);
                }
            }
        };
        IntentFilter f = new IntentFilter();
        f.addAction(BluetoothDevice.ACTION_ACL_CONNECTED);
        f.addAction("android.bluetooth.a2dp.profile.action.CONNECTION_STATE_CHANGED");
        f.addAction(AudioManager.ACTION_AUDIO_BECOMING_NOISY);
        try {
            app.registerReceiver(receptor, f);
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
