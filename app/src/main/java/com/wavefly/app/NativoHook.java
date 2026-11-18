package com.wavefly.app;

/** Ponte entre a notificação (Java) e o player nativo (Kotlin): comandos play, pause, next, prev, stop, rel:N, seek:ms. */
public final class NativoHook {
    private NativoHook() {
    }

    public static volatile java.util.function.Consumer<String> cmd;
}
