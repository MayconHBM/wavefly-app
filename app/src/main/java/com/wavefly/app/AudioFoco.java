package com.wavefly.app;

import android.content.Context;
import android.media.AudioAttributes;
import android.media.AudioFocusRequest;
import android.media.AudioManager;
import android.util.Log;

/**
 * Foco de áudio: o WebView não cuida disso sozinho. Aqui a música abaixa quando outro app fala
 * por cima (aviso curto), pausa em chamadas ou áudios mais longos e volta depois.
 */
final class AudioFoco {
    private static final String TAG = "WaveFlyFoco";
    private static AudioFocusRequest pedido;
    private static AudioManager am;
    private static boolean temFoco = false;
    private static boolean pausadoPorFoco = false;
    private static boolean abaixado = false;

    private AudioFoco() {
    }

    private static final AudioManager.OnAudioFocusChangeListener OUVINTE = new AudioManager.OnAudioFocusChangeListener() {
        @Override
        public void onAudioFocusChange(int mudanca) {
            Log.i(TAG, "foco " + mudanca);
            switch (mudanca) {
                case AudioManager.AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK:
                    abaixado = true;
                    MainActivity.comandoPlayer("duck");
                    break;
                case AudioManager.AUDIOFOCUS_LOSS_TRANSIENT:
                    if (PythonService.pTocando) {
                        pausadoPorFoco = true;
                        MainActivity.comandoPlayer("pause");
                    }
                    break;
                case AudioManager.AUDIOFOCUS_LOSS:
                    // outro app de música assumiu: pausa e não volta sozinha
                    pausadoPorFoco = false;
                    temFoco = false;
                    if (PythonService.pTocando) MainActivity.comandoPlayer("pause");
                    break;
                case AudioManager.AUDIOFOCUS_GAIN:
                    if (abaixado) {
                        abaixado = false;
                        MainActivity.comandoPlayer("unduck");
                    }
                    if (pausadoPorFoco) {
                        pausadoPorFoco = false;
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
                temFoco = am.requestAudioFocus(pedido) == AudioManager.AUDIOFOCUS_REQUEST_GRANTED;
                Log.i(TAG, "pediu foco: " + temFoco);
            } else if (!pausadoPorFoco && temFoco && pedido != null) {
                // parou por vontade do usuário: devolve o foco (se foi o sistema que pausou, espera o GAIN)
                am.abandonAudioFocusRequest(pedido);
                temFoco = false;
                if (abaixado) {
                    abaixado = false;
                    MainActivity.comandoPlayer("unduck");
                }
            }
        } catch (Throwable t) {
            Log.w(TAG, "foco", t);
        }
    }
}
