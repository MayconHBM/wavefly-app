package com.wavefly.app;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.RadialGradient;
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

    private void nota(Canvas c, float x, float y, float u, int cor) {
        p.setStyle(Paint.Style.FILL);
        p.setColor(cor);
        c.drawOval(x - 2.2f * u, y - 1.6f * u, x + 2.2f * u, y + 1.6f * u, p);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(0.9f * u);
        p.setStrokeCap(Paint.Cap.ROUND);
        c.drawLine(x + 2f * u, y, x + 2f * u, y - 7f * u, p);
        c.drawLine(x + 2f * u, y - 7f * u, x + 5f * u, y - 5.5f * u, p);
        p.setStyle(Paint.Style.FILL);
    }

    private void parafuso(Canvas c, float x, float y, float u, float ang) {
        p.setStyle(Paint.Style.FILL);
        p.setColor(0xFFB89A66);
        c.drawCircle(x, y, 1.7f * u, p);
        p.setColor(0xFF4A2A17);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(0.5f * u);
        c.save();
        c.rotate(ang, x, y);
        c.drawLine(x - 1.1f * u, y, x + 1.1f * u, y, p);
        c.restore();
        p.setStyle(Paint.Style.FILL);
    }

    @Override
    protected void onDraw(Canvas c) {
        float w = getWidth(), h = getHeight();
        float cw = Math.min(w * 0.72f, 520f * getResources().getDisplayMetrics().density / 2.4f);
        float ch = cw * 0.64f;
        float cy0 = h * 0.36f;
        float x0 = (w - cw) / 2f, y0 = cy0 - ch / 2f;
        float u = cw / 80f;
        double T = t * 2 * Math.PI;

        // brilho de fundo
        p.setStyle(Paint.Style.FILL);
        p.setShader(new RadialGradient(w / 2f, cy0, cw * 0.95f,
                escuro ? 0x55D9692A : 0x44E8873A, 0x00000000, Shader.TileMode.CLAMP));
        c.drawCircle(w / 2f, cy0, cw * 0.95f, p);
        p.setShader(null);
        // ondas sonoras saindo da fita
        p.setStyle(Paint.Style.STROKE);
        for (int k = 0; k < 3; k++) {
            float f = (t + k / 3f) % 1f;
            float rr = cw * (0.62f + 0.55f * f);
            p.setStrokeWidth(1.6f * u);
            p.setColor(((int) (70 * (1f - f)) << 24) | 0xD9692A);
            c.drawCircle(w / 2f, cy0, rr, p);
        }
        // notas subindo
        for (int k = 0; k < 5; k++) {
            float f = (t * 1f + k * 0.2f) % 1f;
            float nx = w / 2f + (k - 2) * cw * 0.3f + (float) Math.sin(T + k * 1.7) * 3f * u;
            float ny = y0 - 2 * u - f * cw * 0.45f;
            nota(c, nx, ny, u * 0.9f, ((int) (200 * Math.sin(Math.PI * f)) << 24) | 0xD9692A);
        }

        // sombra
        p.setStyle(Paint.Style.FILL);
        p.setColor(0x33000000);
        r.set(x0 + u, y0 + 3 * u, x0 + cw + u, y0 + ch + 3 * u);
        c.drawRoundRect(r, 6 * u, 6 * u, p);
        // corpo com leve degradê
        p.setShader(new LinearGradient(0, y0, 0, y0 + ch, 0xFFF7E8C6, 0xFFE6CF9C, Shader.TileMode.CLAMP));
        r.set(x0, y0, x0 + cw, y0 + ch);
        c.drawRoundRect(r, 6 * u, 6 * u, p);
        p.setShader(null);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(2.4f * u);
        p.setColor(0xFF4A2A17);
        c.drawRoundRect(r, 6 * u, 6 * u, p);
        // parafusos
        parafuso(c, x0 + 5 * u, y0 + 5 * u, u, 30);
        parafuso(c, x0 + cw - 5 * u, y0 + 5 * u, u, 100);
        parafuso(c, x0 + 5 * u, y0 + ch - 5 * u, u, 70);
        parafuso(c, x0 + cw - 5 * u, y0 + ch - 5 * u, u, 150);
        // etiqueta laranja
        p.setStyle(Paint.Style.FILL);
        p.setShader(new LinearGradient(0, y0 + 5 * u, 0, y0 + 26 * u, 0xFFE8873A, 0xFFC8581F, Shader.TileMode.CLAMP));
        r.set(x0 + 10 * u, y0 + 5 * u, x0 + 70 * u, y0 + 26 * u);
        c.drawRoundRect(r, 2.5f * u, 2.5f * u, p);
        p.setShader(null);
        // listras da etiqueta
        p.setColor(0x55FFFFFF);
        c.drawRect(x0 + 10 * u, y0 + 7.5f * u, x0 + 70 * u, y0 + 8.7f * u, p);
        c.drawRect(x0 + 10 * u, y0 + 9.6f * u, x0 + 70 * u, y0 + 10.3f * u, p);
        p.setColor(0xFFF3E3C3);
        r.set(x0 + 13 * u, y0 + 12 * u, x0 + 67 * u, y0 + 23 * u);
        c.drawRoundRect(r, 1.5f * u, 1.5f * u, p);
        p.setColor(0xFF4A2A17);
        p.setTextSize(7.2f * u);
        p.setTypeface(Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD));
        p.setTextAlign(Paint.Align.LEFT);
        c.drawText("WaveFly", x0 + 16 * u, y0 + 20.6f * u, p);
        // mini onda na etiqueta
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(0.9f * u);
        p.setColor(0xFFD9692A);
        android.graphics.Path onda = new android.graphics.Path();
        for (int i = 0; i <= 20; i++) {
            float ox = x0 + 49 * u + i * 0.85f * u;
            float oy = y0 + 17.5f * u + (float) Math.sin(T * 2 + i * 0.55) * 2.4f * u * (1f - Math.abs(i - 10) / 11f);
            if (i == 0) onda.moveTo(ox, oy); else onda.lineTo(ox, oy);
        }
        c.drawPath(onda, p);
        p.setStyle(Paint.Style.FILL);
        // janela da fita
        p.setColor(0xFF2A1A10);
        r.set(x0 + 15 * u, y0 + 30 * u, x0 + 65 * u, y0 + 46 * u);
        c.drawRoundRect(r, 8 * u, 8 * u, p);
        // fita esticada entre os carretéis (parte de baixo)
        float vai = 0.5f + 0.5f * (float) Math.sin(T);
        float rE = (6.2f - 1.6f * vai) * u, rD = (4.6f + 1.6f * vai) * u;
        p.setColor(0xFF6B4228);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(0.8f * u);
        c.drawLine(x0 + 28 * u, y0 + 38 * u + rE, x0 + 52 * u, y0 + 38 * u + rD, p);
        p.setStyle(Paint.Style.FILL);
        c.drawCircle(x0 + 28 * u, y0 + 38 * u, rE, p);
        c.drawCircle(x0 + 52 * u, y0 + 38 * u, rD, p);
        // anéis da fita enrolada
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(0.3f * u);
        p.setColor(0x55000000);
        for (float q = 5.2f; q < 6.2f; q += 0.5f) { c.drawCircle(x0 + 28 * u, y0 + 38 * u, Math.min(rE, q * u), p); }
        for (float q = 4.9f; q < 6.2f; q += 0.5f) { c.drawCircle(x0 + 52 * u, y0 + 38 * u, Math.min(rD, q * u), p); }
        p.setStyle(Paint.Style.FILL);
        reel(c, x0 + 28 * u, y0 + 38 * u, 4.4f * u, t * 720f);
        reel(c, x0 + 52 * u, y0 + 38 * u, 4.4f * u, t * 720f);
        // reflexo no vidro da janela
        p.setColor(0x22FFFFFF);
        android.graphics.Path vid = new android.graphics.Path();
        vid.moveTo(x0 + 20 * u, y0 + 31 * u);
        vid.lineTo(x0 + 34 * u, y0 + 31 * u);
        vid.lineTo(x0 + 26 * u, y0 + 45 * u);
        vid.lineTo(x0 + 17 * u, y0 + 45 * u);
        vid.close();
        c.drawPath(vid, p);
        // base trapezoidal com furos
        p.setColor(0xFFD9BF8C);
        android.graphics.Path base = new android.graphics.Path();
        base.moveTo(x0 + 22 * u, y0 + ch - 4 * u);
        base.lineTo(x0 + 26 * u, y0 + ch - 0.5f * u);
        base.lineTo(x0 + 54 * u, y0 + ch - 0.5f * u);
        base.lineTo(x0 + 58 * u, y0 + ch - 4 * u);
        base.close();
        c.drawPath(base, p);
        p.setColor(0xFF4A2A17);
        for (int i = 0; i < 4; i++) c.drawCircle(x0 + (31 + i * 6) * u, y0 + ch - 2.2f * u, 0.8f * u, p);

        // equalizador com degradê
        float by = cy0 + ch / 2f + 20 * u;
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
