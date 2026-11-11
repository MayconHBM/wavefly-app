package com.wavefly.app;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.graphics.RectF;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewConfiguration;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import com.chaquo.python.Python;

/**
 * Botão flutuante (só Android). Fica por cima dos outros apps.
 * - toque: pega o link copiado e começa o download em segundo plano;
 * - engrenagem pequena: escolhe o formato (MP3, M4A/Opus, MP4);
 * - segurar: pergunta se quer desativar.
 */
final class Bolha {
    private static final int BRANCO = 0xFFF3E6CC, MARROM = 0xFF3B2314, LARANJA = 0xFFD9692A;

    private final Context ctx;
    private final WindowManager wm;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private Cx raiz;
    private WindowManager.LayoutParams lp;
    private FrameLayout painel;
    private boolean pendente = false;

    static boolean permitido(Context c) {
        return Build.VERSION.SDK_INT < 23 || Settings.canDrawOverlays(c);
    }

    static boolean ligada(Context c) {
        return Idioma.prefs(c).getBoolean("bolha", false);
    }

    static String formato(Context c) {
        String f = Idioma.prefs(c).getString("bolha_fmt", "mp3");
        return f.equals("original") || f.equals("video") ? f : "mp3";
    }

    Bolha(Context c) {
        ctx = c;
        wm = (WindowManager) c.getSystemService(Context.WINDOW_SERVICE);
    }

    private int dp(float v) {
        return Math.round(v * ctx.getResources().getDisplayMetrics().density);
    }

    private static int tipo() {
        return Build.VERSION.SDK_INT >= 26 ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                : WindowManager.LayoutParams.TYPE_PHONE;
    }

    private void toast(String m) {
        ui.post(() -> Toast.makeText(ctx, m, Toast.LENGTH_LONG).show());
    }

    // ----------------------------------------------------------------- o botão
    private class Desenho extends View {
        final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        final RectF r = new RectF();

        Desenho(Context c) {
            super(c);
        }

        @Override
        protected void onDraw(Canvas c) {
            float s = Math.min(getWidth(), getHeight()), cx = getWidth() / 2f, cy = getHeight() / 2f, rad = s / 2f - dp(3);
            p.setStyle(Paint.Style.FILL);
            p.setColor(0x55000000);
            c.drawCircle(cx, cy + dp(2), rad, p);
            p.setColor(LARANJA);
            c.drawCircle(cx, cy, rad, p);
            p.setStyle(Paint.Style.STROKE);
            p.setStrokeWidth(dp(2));
            p.setColor(0xFF8A3E12);
            c.drawCircle(cx, cy, rad, p);
            p.setStyle(Paint.Style.FILL);
            p.setColor(0xFFF3E3C3);
            float bw = rad * 0.18f;
            float[] alt = {0.35f, 0.65f, 0.95f, 0.55f, 0.8f};
            for (int i = 0; i < 5; i++) {
                float h = rad * alt[i] * 0.9f, x = cx + (i - 2) * bw * 1.7f;
                r.set(x - bw / 2f, cy + rad * 0.45f - h, x + bw / 2f, cy + rad * 0.45f);
                c.drawRoundRect(r, bw / 2f, bw / 2f, p);
            }
        }
    }

    private class Engrenagem extends View {
        final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);

        Engrenagem(Context c) {
            super(c);
        }

        @Override
        protected void onDraw(Canvas c) {
            float cx = getWidth() / 2f, cy = getHeight() / 2f, rad = Math.min(cx, cy) - dp(1);
            p.setStyle(Paint.Style.FILL);
            p.setColor(MARROM);
            c.drawCircle(cx, cy, rad, p);
            p.setColor(BRANCO);
            p.setStyle(Paint.Style.STROKE);
            p.setStrokeWidth(rad * 0.28f);
            p.setStrokeCap(Paint.Cap.ROUND);
            c.drawCircle(cx, cy, rad * 0.42f, p);
            p.setStrokeWidth(rad * 0.2f);
            for (int i = 0; i < 8; i++) {
                c.save();
                c.rotate(i * 45f, cx, cy);
                c.drawLine(cx, cy - rad * 0.62f, cx, cy - rad * 0.8f, p);
                c.restore();
            }
        }
    }

    private class Cx extends FrameLayout {
        Cx(Context c) {
            super(c);
        }

        @Override
        public void onWindowFocusChanged(boolean hasWindowFocus) {
            super.onWindowFocusChanged(hasWindowFocus);
            if (hasWindowFocus && pendente) ui.postDelayed(Bolha.this::lerAreaDeTransferencia, 60);
        }
    }

    void mostrar() {
        ui.post(() -> {
            if (raiz != null || !permitido(ctx)) return;
            try {
                raiz = new Cx(ctx);
                Desenho d = new Desenho(ctx);
                raiz.addView(d, new FrameLayout.LayoutParams(dp(58), dp(58), Gravity.START | Gravity.TOP));
                Engrenagem g = new Engrenagem(ctx);
                raiz.addView(g, new FrameLayout.LayoutParams(dp(22), dp(22), Gravity.END | Gravity.BOTTOM));
                lp = new WindowManager.LayoutParams(dp(74), dp(74), tipo(),
                        WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
                                | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
                        PixelFormat.TRANSLUCENT);
                lp.gravity = Gravity.TOP | Gravity.START;
                lp.x = Idioma.prefs(ctx).getInt("bolha_x", dp(8));
                lp.y = Idioma.prefs(ctx).getInt("bolha_y", dp(240));
                raiz.setOnTouchListener(new Toque());
                wm.addView(raiz, lp);
            } catch (Throwable t) {
                raiz = null;
            }
        });
    }

    void esconder() {
        ui.post(() -> {
            fecharPainel();
            if (raiz != null) {
                try {
                    wm.removeView(raiz);
                } catch (Throwable ignored) {
                }
                raiz = null;
            }
        });
    }

    private class Toque implements View.OnTouchListener {
        float dx, dy, x0, y0;
        boolean moveu, longo, naEngrenagem;
        final int slop = ViewConfiguration.get(ctx).getScaledTouchSlop();
        final Runnable seg = () -> {
            if (!moveu) {
                longo = true;
                raiz.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS);
                confirmarDesativar();
            }
        };

        @Override
        public boolean onTouch(View v, MotionEvent e) {
            switch (e.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    x0 = e.getRawX();
                    y0 = e.getRawY();
                    dx = lp.x - x0;
                    dy = lp.y - y0;
                    moveu = false;
                    longo = false;
                    naEngrenagem = e.getX() > dp(48) && e.getY() > dp(48);
                    if (!naEngrenagem) ui.postDelayed(seg, 650);
                    return true;
                case MotionEvent.ACTION_MOVE:
                    if (!moveu && (Math.abs(e.getRawX() - x0) > slop || Math.abs(e.getRawY() - y0) > slop)) {
                        moveu = true;
                        ui.removeCallbacks(seg);
                    }
                    if (moveu) {
                        lp.x = (int) (e.getRawX() + dx);
                        lp.y = (int) (e.getRawY() + dy);
                        try {
                            wm.updateViewLayout(raiz, lp);
                        } catch (Throwable ignored) {
                        }
                    }
                    return true;
                case MotionEvent.ACTION_UP:
                    ui.removeCallbacks(seg);
                    if (moveu) {
                        Idioma.prefs(ctx).edit().putInt("bolha_x", lp.x).putInt("bolha_y", lp.y).apply();
                    } else if (!longo) {
                        if (naEngrenagem) abrirConfig();
                        else capturar();
                    }
                    return true;
                case MotionEvent.ACTION_CANCEL:
                    ui.removeCallbacks(seg);
                    return true;
            }
            return false;
        }
    }

    // ----------------------------------------------------------------- captura do link
    private void capturar() {
        if (raiz == null) return;
        pendente = true;
        // O Android só deixa ler a área de transferência quem está com foco: dá foco por um instante.
        lp.flags &= ~WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE;
        try {
            wm.updateViewLayout(raiz, lp);
        } catch (Throwable ignored) {
        }
        ui.postDelayed(this::lerAreaDeTransferencia, 700);
    }

    private void lerAreaDeTransferencia() {
        if (!pendente) return;
        pendente = false;
        String texto = "";
        try {
            ClipboardManager cm = (ClipboardManager) ctx.getSystemService(Context.CLIPBOARD_SERVICE);
            if (cm != null && cm.hasPrimaryClip()) {
                ClipData d = cm.getPrimaryClip();
                if (d != null && d.getItemCount() > 0) {
                    CharSequence t = d.getItemAt(0).coerceToText(ctx);
                    if (t != null) texto = t.toString();
                }
            }
        } catch (Throwable ignored) {
        }
        if (raiz != null) {
            lp.flags |= WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE;
            try {
                wm.updateViewLayout(raiz, lp);
            } catch (Throwable ignored) {
            }
        }
        enviar(texto);
    }

    private void enviar(final String texto) {
        if (!PythonService.ready) {
            toast(Idioma.t(ctx, "O WaveFly ainda está iniciando. Tente de novo em instantes.",
                    "WaveFly is still starting. Try again in a moment.",
                    "WaveFly aún se está iniciando. Inténtalo de nuevo en un momento."));
            return;
        }
        new Thread(() -> {
            String r;
            try {
                r = Python.getInstance().getModule("app_entry").callAttr("baixar_link", texto, formato(ctx)).toString();
            } catch (Throwable t) {
                r = "erro";
            }
            String m;
            if (r.startsWith("ok")) {
                m = Idioma.t(ctx, "Download iniciado em segundo plano", "Download started in the background",
                        "Descarga iniciada en segundo plano");
            } else if (r.startsWith("ja")) {
                m = Idioma.t(ctx, "Esse vídeo já está na fila ou na pasta", "This video is already queued or saved",
                        "Este vídeo ya está en la cola o en la carpeta");
            } else if (r.startsWith("nenhum")) {
                m = Idioma.t(ctx,
                        "Nenhum link do YouTube copiado. No vídeo, toque em Compartilhar › Copiar link e depois toque no botão.",
                        "No YouTube link copied. On the video, tap Share › Copy link, then tap the button.",
                        "No hay ningún enlace de YouTube copiado. En el vídeo, toca Compartir › Copiar enlace y luego toca el botón.");
            } else {
                m = Idioma.t(ctx, "Não foi possível iniciar o download", "Could not start the download",
                        "No se pudo iniciar la descarga");
            }
            toast(m);
        }, "wavefly-bolha").start();
    }

    // ----------------------------------------------------------------- painéis
    private GradientDrawable fundo(int cor, float raio) {
        GradientDrawable g = new GradientDrawable();
        g.setColor(cor);
        g.setCornerRadius(dp(raio));
        return g;
    }

    private TextView botao(String t, boolean forte, View.OnClickListener ck) {
        TextView b = new TextView(ctx);
        b.setText(t);
        b.setGravity(Gravity.CENTER);
        b.setTextSize(15);
        b.setSingleLine(false);
        b.setPadding(dp(14), dp(11), dp(14), dp(11));
        b.setTextColor(forte ? 0xFFFFFFFF : MARROM);
        b.setTypeface(null, android.graphics.Typeface.BOLD);
        b.setBackground(fundo(forte ? LARANJA : 0xFFE4D2AE, 12));
        b.setOnClickListener(ck);
        return b;
    }

    private void mostrarPainel(View cartao) {
        fecharPainel();
        painel = new FrameLayout(ctx);
        painel.setBackgroundColor(0x99000000);
        painel.setOnClickListener(v -> fecharPainel());
        FrameLayout.LayoutParams cl = new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.CENTER);
        cl.leftMargin = cl.rightMargin = dp(28);
        cartao.setClickable(true);
        painel.addView(cartao, cl);
        WindowManager.LayoutParams pl = new WindowManager.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT, tipo(),
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                PixelFormat.TRANSLUCENT);
        try {
            wm.addView(painel, pl);
        } catch (Throwable t) {
            painel = null;
        }
    }

    private void fecharPainel() {
        if (painel != null) {
            try {
                wm.removeView(painel);
            } catch (Throwable ignored) {
            }
            painel = null;
        }
    }

    private LinearLayout cartao() {
        LinearLayout l = new LinearLayout(ctx);
        l.setOrientation(LinearLayout.VERTICAL);
        l.setPadding(dp(20), dp(18), dp(20), dp(16));
        l.setBackground(fundo(BRANCO, 20));
        return l;
    }

    private TextView titulo(String t) {
        TextView v = new TextView(ctx);
        v.setText(t);
        v.setTextSize(18);
        v.setTextColor(MARROM);
        v.setTypeface(null, android.graphics.Typeface.BOLD);
        return v;
    }

    private LinearLayout linhaBotoes(TextView a, TextView b) {
        LinearLayout l = new LinearLayout(ctx);
        l.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        p.setMargins(dp(4), dp(16), dp(4), 0);
        l.addView(a, p);
        l.addView(b, p);
        return l;
    }

    private void abrirConfig() {
        final String[] escolhido = {formato(ctx)};
        LinearLayout c = cartao();
        c.addView(titulo(Idioma.t(ctx, "Formato do botão flutuante", "Floating button format",
                "Formato del botón flotante")));
        TextView n = new TextView(ctx);
        n.setText(Idioma.t(ctx, "Vale para os downloads feitos pelo botão.", "Applies to downloads started by the button.",
                "Vale para las descargas hechas con el botón."));
        n.setTextColor(0xFF7A5A40);
        n.setTextSize(13);
        n.setPadding(0, dp(4), 0, dp(6));
        c.addView(n);
        RadioGroup g = new RadioGroup(ctx);
        String[][] op = {{"mp3", "MP3"}, {"original", "M4A / Opus"}, {"video", "MP4"}};
        for (String[] o : op) {
            RadioButton rb = new RadioButton(ctx);
            rb.setText(o[1]);
            rb.setTextSize(16);
            rb.setTextColor(MARROM);
            rb.setPadding(dp(8), dp(10), dp(8), dp(10));
            rb.setId(View.generateViewId());
            rb.setTag(o[0]);
            rb.setChecked(o[0].equals(escolhido[0]));
            g.addView(rb);
        }
        g.setOnCheckedChangeListener((grp, id) -> {
            View v = grp.findViewById(id);
            if (v != null) escolhido[0] = (String) v.getTag();
        });
        c.addView(g);
        c.addView(linhaBotoes(
                botao(Idioma.t(ctx, "Cancelar", "Cancel", "Cancelar"), false, v -> fecharPainel()),
                botao(Idioma.t(ctx, "Aplicar", "Apply", "Aplicar"), true, v -> {
                    Idioma.prefs(ctx).edit().putString("bolha_fmt", escolhido[0]).apply();
                    fecharPainel();
                    toast(Idioma.t(ctx, "Formato aplicado", "Format applied", "Formato aplicado"));
                })));
        mostrarPainel(c);
    }

    private void confirmarDesativar() {
        LinearLayout c = cartao();
        c.addView(titulo(Idioma.t(ctx, "Desativar o botão flutuante?", "Turn off the floating button?",
                "¿Desactivar el botón flotante?")));
        TextView n = new TextView(ctx);
        n.setText(Idioma.t(ctx,
                "O WaveFly continua aberto até terminar os downloads e depois por mais 10 minutos.",
                "WaveFly stays open until downloads finish and then for 10 more minutes.",
                "WaveFly sigue abierto hasta terminar las descargas y después 10 minutos más."));
        n.setTextColor(0xFF7A5A40);
        n.setTextSize(14);
        n.setPadding(0, dp(8), 0, 0);
        c.addView(n);
        c.addView(linhaBotoes(
                botao(Idioma.t(ctx, "Cancelar", "Cancel", "Cancelar"), false, v -> fecharPainel()),
                botao(Idioma.t(ctx, "Desativar", "Turn off", "Desactivar"), true, v -> {
                    Idioma.prefs(ctx).edit().putBoolean("bolha", false).apply();
                    fecharPainel();
                    esconder();
                    MainActivity.avisarBolha(false);
                })));
        mostrarPainel(c);
    }
}
