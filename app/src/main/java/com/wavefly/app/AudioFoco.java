package com.wavefly.app;

import android.content.Context;
import android.media.AudioAttributes;
import android.media.AudioFocusRequest;
import android.media.AudioManager;
import android.os.SystemClock;
import android.util.Log;

import java.text.SimpleDateFormat;
import java.util.ArrayDeque;
import java.util.Date;
import java.util.Locale;

/**
 * Foco de áudio (modo de teste, ligado no Painel do desenvolvedor): abaixa a música quando outro app
 * fala por cima, pausa em chamadas e áudios longos e volta depois. Registra tudo para diagnóstico.
 */
final class AudioFoco {
    private static final String TAG = "WaveFlyFoco";
    private static AudioFocusRequest pedido;
    private static AudioManager am;
    private static boolean temFoco = false;
    private static boolean pausadoPorFoco = false;
    private static boolean abaixado = false;
    private static final ArrayDeque<String> LOG = new ArrayDeque<>();
    private static final SimpleDateFormat HORA = new SimpleDateFormat("HH:mm:ss.SSS", Locale.US);

    private AudioFoco() {
    }

    static boolean ligado(Context c) {
        return "1".equals(Idioma.prefs(c).getString("p_foco", ""));
    }

    static synchronized void reg(String s) {
        String l = HORA.format(new Date()) + " " + s;
        Log.i(TAG, l);
        LOG.addLast(l);
        while (LOG.size() > 150) LOG.removeFirst();
    }

    static synchronized String log() {
        StringBuilder b = new StringBuilder();
        for (String l : LOG) b.append(l).append('\n');
        return b.toString();
    }

    static String nome(int m) {
        switch (m) {
            case AudioManager.AUDIOFOCUS_GAIN: return "GAIN (voltou)";
            case AudioManager.AUDIOFOCUS_GAIN_TRANSIENT: return "GAIN_TRANSIENT";
            case AudioManager.AUDIOFOCUS_LOSS: return "LOSS (perdeu de vez)";
            case AudioManager.AUDIOFOCUS_LOSS_TRANSIENT: return "LOSS_TRANSIENT (pausa curta)";
            case AudioManager.AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK: return "LOSS_TRANSIENT_CAN_DUCK (pode abaixar)";
            default: return "código " + m;
        }
    }

    private static final AudioManager.OnAudioFocusChangeListener OUVINTE = new AudioManager.OnAudioFocusChangeListener() {
        @Override
        public void onAudioFocusChange(int mudanca) {
            reg("foco: " + nome(mudanca) + " · tocando=" + PythonService.pTocando);
            switch (mudanca) {
                case AudioManager.AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK:
                    abaixado = true;
                    reg("ação: abaixar a música");
                    MainActivity.comandoPlayer("duck");
                    break;
                case AudioManager.AUDIOFOCUS_LOSS_TRANSIENT:
                    if (PythonService.pTocando) {
                        pausadoPorFoco = true;
                        reg("ação: pausar (volta sozinha depois)");
                        MainActivity.comandoPlayer("pause");
                    }
                    break;
                case AudioManager.AUDIOFOCUS_LOSS:
                    pausadoPorFoco = false;
                    temFoco = false;
                    if (PythonService.pTocando) {
                        reg("ação: pausar (outro app assumiu)");
                        MainActivity.comandoPlayer("pause");
                    }
                    break;
                case AudioManager.AUDIOFOCUS_GAIN:
                    if (abaixado) {
                        abaixado = false;
                        reg("ação: voltar o volume");
                        MainActivity.comandoPlayer("unduck");
                    }
                    if (pausadoPorFoco) {
                        pausadoPorFoco = false;
                        reg("ação: continuar a música");
                        MainActivity.comandoPlayer("play");
                    }
                    break;
                default:
                    break;
            }
        }
    };

    /** A página avisou que o player começou ou parou de tocar. */
    static synchronized void estado(Context ctx, boolean tocando) {
        try {
            if (!ligado(ctx)) return;
            reg("player: " + (tocando ? "tocando" : "parado") + " · foco=" + temFoco + " · pausadoPorFoco=" + pausadoPorFoco);
            if (am == null) am = (AudioManager) ctx.getApplicationContext().getSystemService(Context.AUDIO_SERVICE);
            if (am == null) return;
            if (tocando) {
                pausadoPorFoco = false;
                if (temFoco) return;
                if (pedido == null) {
                    pedido = new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN)
                            .setAudioAttributes(new AudioAttributes.Builder()
                                    .setUsage(AudioAttributes.USAGE_MEDIA)
                                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
                            .setOnAudioFocusChangeListener(OUVINTE)
                            .build();
                }
                int r = am.requestAudioFocus(pedido);
                temFoco = r == AudioManager.AUDIOFOCUS_REQUEST_GRANTED;
                reg("pediu o foco: " + (temFoco ? "concedido" : "negado (" + r + ")"));
            } else if (!pausadoPorFoco && temFoco && pedido != null) {
                am.abandonAudioFocusRequest(pedido);
                temFoco = false;
                reg("devolveu o foco");
                if (abaixado) {
                    abaixado = false;
                    MainActivity.comandoPlayer("unduck");
                }
            }
        } catch (Throwable t) {
            reg("erro: " + t);
        }
    }

    /** O interruptor do Painel do desenvolvedor mudou. */
    static synchronized void mudou(Context ctx) {
        try {
            boolean on = ligado(ctx);
            reg("modo de teste " + (on ? "LIGADO" : "desligado") + " · Android " + android.os.Build.VERSION.RELEASE);
            try {
                android.content.pm.PackageInfo wv = android.webkit.WebView.getCurrentWebViewPackage();
                if (wv != null) reg("WebView " + wv.packageName + " " + wv.versionName);
            } catch (Throwable ignored) {
            }
            if (!on && temFoco && am != null && pedido != null) {
                am.abandonAudioFocusRequest(pedido);
                temFoco = false;
                pausadoPorFoco = false;
                if (abaixado) {
                    abaixado = false;
                    MainActivity.comandoPlayer("unduck");
                }
            }
        } catch (Throwable t) {
            reg("erro: " + t);
        }
    }

    static synchronized void limpar() {
        LOG.clear();
    }
}
