package com.wavefly.app;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.view.animation.LinearInterpolator;

/** Tela de abertura: equalizador animado, nome do app e barra de carregamento. */
class SplashView extends android.view.View {
    private final boolean escuro;
    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF r = new RectF();
    private final ValueAnimator anim;
    private float t = 0f;
    private long inicio = System.currentTimeMillis();
    String texto = "";

    SplashView(Context c, boolean escuro) {
        super(c);
        this.escuro = escuro;
        anim = ValueAnimator.ofFloat(0f, 1f);
        anim.setDuration(2400);
        anim.setRepeatCount(ValueAnimator.INFINITE);
        anim.setInterpolator(new LinearInterpolator());
        anim.addUpdateListener(a -> {
            t = (float) a.getAnimatedValue();
            invalidate();
        });
    }

    @Override
    protected void onAttachedToWindow() {
        super.onAttachedToWindow();
        anim.start();
    }

    @Override
    protected void onDetachedFromWindow() {
        anim.cancel();
        super.onDetachedFromWindow();
    }

    long ativoHa() {
        return System.currentTimeMillis() - inicio;
    }

    @Override
    protected void onDraw(Canvas c) {
        float w = getWidth(), h = getHeight();
        float cw = Math.min(w * 0.72f, 520f * getResources().getDisplayMetrics().density / 2.4f);
        float u = cw / 80f;
        double T = t * 2 * Math.PI;

        // equalizador com degradê
        float by = h * 0.46f - 20.8f * u;   // sem a fita: o conjunto fica centralizado na tela
        float bw = 5f * u * 0.6f;
        for (int i = 0; i < 13; i++) {
            float a = (float) Math.abs(Math.sin(T + i * 0.55) * Math.cos(T * 0.5 + i * 0.3));
            float alt = (2.5f + 12f * a) * u * 0.8f;
            float bx = w / 2f + (i - 6) * bw * 1.8f;
            float base0 = by + 14 * u * 0.8f;
            p.setShader(new LinearGradient(0, base0 - alt, 0, base0, 0xFFF2A154, 0xFFC8581F, Shader.TileMode.CLAMP));
            r.set(bx - bw / 2f, base0 - alt, bx + bw / 2f, base0);
            c.drawRoundRect(r, bw / 2f, bw / 2f, p);
            p.setShader(null);
        }
        // título
        p.setStyle(Paint.Style.FILL);
        p.setTextAlign(Paint.Align.CENTER);
        p.setTypeface(Typeface.create(Typeface.SERIF, Typeface.BOLD));
        p.setTextSize(10f * u);
        p.setColor(0xFFD9692A);
        c.drawText("WaveFly", w / 2f, by + 36 * u * 0.8f, p);
        // barra de carregamento indeterminada
        float bwid = cw * 0.5f, bxx = (w - bwid) / 2f, byy = by + 42 * u * 0.8f;
        p.setColor(escuro ? 0x33FFFFFF : 0x2A4A2A17);
        r.set(bxx, byy, bxx + bwid, byy + 1.6f * u);
        c.drawRoundRect(r, u, u, p);
        float seg = bwid * 0.3f, pos = (t * (bwid + seg)) - seg;
        float l = Math.max(0, pos), rr2 = Math.min(bwid, pos + seg);
        if (rr2 > l) {
            p.setColor(0xFFD9692A);
            r.set(bxx + l, byy, bxx + rr2, byy + 1.6f * u);
            c.drawRoundRect(r, u, u, p);
        }
        // texto de status
        p.setTypeface(Typeface.SANS_SERIF);
        p.setTextSize(4.2f * u);
        p.setColor(escuro ? 0xFFF3E6CC : 0xFF3B2314);
        c.drawText(texto, w / 2f, byy + 8 * u, p);
    }
}
