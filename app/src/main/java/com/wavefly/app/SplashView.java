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

/** Tela de abertura: uma fita cassete com os carretéis girando e a fita passando de um lado para o outro. */
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

    private void reel(Canvas c, float cx, float cy, float raio, float graus) {
        p.setStyle(Paint.Style.FILL);
        p.setColor(0xFF6B4228);
        c.drawCircle(cx, cy, raio, p);
        c.save();
        c.rotate(graus, cx, cy);
        p.setColor(0xFFF1DFB8);
        c.drawCircle(cx, cy, raio * 0.62f, p);
        p.setColor(0xFF4A2A17);
        p.setStrokeWidth(raio * 0.12f);
        p.setStrokeCap(Paint.Cap.ROUND);
        for (int i = 0; i < 3; i++) {
            c.save();
            c.rotate(i * 60f, cx, cy);
            c.drawLine(cx, cy - raio * 0.5f, cx, cy + raio * 0.5f, p);
            c.restore();
        }
        c.restore();
    }

    @Override
    protected void onDraw(Canvas c) {
        float w = getWidth(), h = getHeight();
        float cw = Math.min(w * 0.72f, 520f * getResources().getDisplayMetrics().density / 2.4f);
        float ch = cw * 0.64f;
        float x0 = (w - cw) / 2f, y0 = h * 0.36f - ch / 2f;
        float u = cw / 80f;
        // sombra
        p.setStyle(Paint.Style.FILL);
        p.setColor(0x33000000);
        r.set(x0 + u, y0 + 3 * u, x0 + cw + u, y0 + ch + 3 * u);
        c.drawRoundRect(r, 6 * u, 6 * u, p);
        // corpo
        p.setColor(0xFFF1DFB8);
        r.set(x0, y0, x0 + cw, y0 + ch);
        c.drawRoundRect(r, 6 * u, 6 * u, p);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(2.4f * u);
        p.setColor(0xFF4A2A17);
        c.drawRoundRect(r, 6 * u, 6 * u, p);
        // etiqueta laranja
        p.setStyle(Paint.Style.FILL);
        p.setShader(new LinearGradient(0, y0 + 5 * u, 0, y0 + 26 * u, 0xFFE8873A, 0xFFC8581F, Shader.TileMode.CLAMP));
        r.set(x0 + 10 * u, y0 + 5 * u, x0 + 70 * u, y0 + 26 * u);
        c.drawRoundRect(r, 2.5f * u, 2.5f * u, p);
        p.setShader(null);
        p.setColor(0xFFF3E3C3);
        r.set(x0 + 13 * u, y0 + 12 * u, x0 + 67 * u, y0 + 23 * u);
        c.drawRoundRect(r, 1.5f * u, 1.5f * u, p);
        p.setColor(0xFF4A2A17);
        p.setTextSize(7.2f * u);
        p.setTypeface(Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD));
        p.setTextAlign(Paint.Align.LEFT);
        c.drawText("WaveFly", x0 + 16 * u, y0 + 20.6f * u, p);
        // janela da fita
        p.setColor(0xFF2A1A10);
        r.set(x0 + 15 * u, y0 + 30 * u, x0 + 65 * u, y0 + 46 * u);
        c.drawRoundRect(r, 8 * u, 8 * u, p);
        // fita: quanto passou de um carretel para o outro
        float vai = 0.5f + 0.5f * (float) Math.sin(t * 2 * Math.PI);
        float rE = (6.2f - 1.6f * vai) * u, rD = (4.6f + 1.6f * vai) * u;
        p.setColor(0xFF6B4228);
        c.drawCircle(x0 + 28 * u, y0 + 38 * u, rE, p);
        c.drawCircle(x0 + 52 * u, y0 + 38 * u, rD, p);
        reel(c, x0 + 28 * u, y0 + 38 * u, 4.4f * u, t * 720f);
        reel(c, x0 + 52 * u, y0 + 38 * u, 4.4f * u, t * 720f);
        // base trapezoidal
        p.setColor(0xFFD9BF8C);
        android.graphics.Path base = new android.graphics.Path();
        base.moveTo(x0 + 22 * u, y0 + ch - 4 * u);
        base.lineTo(x0 + 26 * u, y0 + ch - 0.5f * u);
        base.lineTo(x0 + 54 * u, y0 + ch - 0.5f * u);
        base.lineTo(x0 + 58 * u, y0 + ch - 4 * u);
        base.close();
        c.drawPath(base, p);
        // equalizador embaixo
        float by = h * 0.36f + ch / 2f + 40 * u / 2f;
        float bw = 5f * u * 0.6f;
        p.setStyle(Paint.Style.FILL);
        p.setColor(0xFFD9692A);
        for (int i = 0; i < 9; i++) {
            float a = (float) Math.abs(Math.sin(t * 2 * Math.PI * 1.0 + i * 0.7));
            float alt = (3f + 11f * a) * u * 0.8f;
            float bx = w / 2f + (i - 4) * bw * 1.9f;
            r.set(bx - bw / 2f, by + 14 * u * 0.8f - alt, bx + bw / 2f, by + 14 * u * 0.8f);
            c.drawRoundRect(r, bw / 2f, bw / 2f, p);
        }
        // texto
        p.setTextAlign(Paint.Align.CENTER);
        p.setTypeface(Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD));
        p.setTextSize(9f * u);
        p.setColor(0xFFD9692A);
        c.drawText("WaveFly", w / 2f, by + 36 * u * 0.8f, p);
        p.setTypeface(Typeface.SANS_SERIF);
        p.setTextSize(4.2f * u);
        p.setColor(escuro ? 0xFFF3E6CC : 0xFF3B2314);
        c.drawText(texto, w / 2f, by + 50 * u * 0.8f, p);
    }
}
