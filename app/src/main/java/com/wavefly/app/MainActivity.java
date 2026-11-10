package com.wavefly.app;

import android.Manifest;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.DownloadListener;
import android.webkit.JavascriptInterface;
import android.webkit.JsPromptResult;
import android.webkit.JsResult;
import android.webkit.URLUtil;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

/** Tela do app: mostra a interface do WaveFly em tela cheia (sem barra de navegador). */
public class MainActivity extends AppCompatActivity {
    private static final String HOME = "http://127.0.0.1:" + PythonService.PORT + "/";

    private WebView web;
    private LinearLayout loading;
    private TextView loadingText;
    private ProgressBar spinner;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private boolean paginaCarregada = false;
    private boolean destruida = false;
    private boolean avisouFfmpeg = false;
    private static MainActivity atual;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        atual = this;
        boolean escuro = (getResources().getConfiguration().uiMode
                & android.content.res.Configuration.UI_MODE_NIGHT_MASK)
                == android.content.res.Configuration.UI_MODE_NIGHT_YES;
        int fundo = escuro ? 0xFF1F1510 : 0xFFF3E6CC;
        int texto = escuro ? 0xFFF3E6CC : 0xFF3B2314;

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(fundo);

        web = new WebView(this);
        web.setBackgroundColor(fundo);
        web.setVisibility(View.INVISIBLE);
        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        loading = new LinearLayout(this);
        loading.setOrientation(LinearLayout.VERTICAL);
        loading.setGravity(Gravity.CENTER);
        loading.setBackgroundColor(fundo);
        TextView nome = new TextView(this);
        nome.setText("WaveFly");
        nome.setTextSize(34);
        nome.setTextColor(0xFFD9692A);
        nome.setGravity(Gravity.CENTER);
        spinner = new ProgressBar(this);
        loadingText = new TextView(this);
        loadingText.setTextColor(texto);
        loadingText.setTextSize(15);
        loadingText.setGravity(Gravity.CENTER);
        loadingText.setPadding(48, 32, 48, 0);
        loadingText.setTextIsSelectable(true);
        loading.addView(nome);
        loading.addView(spinner, new LinearLayout.LayoutParams(120, 120));
        loading.addView(loadingText);
        root.addView(loading, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);

        configurarWeb();
        pedirPermissoes();
        aguardarServidor();
    }

    private void configurarWeb() {
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setTextZoom(100);
        web.addJavascriptInterface(new Ponte(), "WF");
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, android.webkit.WebResourceRequest r) {
                Uri u = r.getUrl();
                String host = u.getHost();
                if ("127.0.0.1".equals(host) || "localhost".equals(host)) return false;
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, u));
                } catch (Exception ignored) {
                }
                return true;
            }

            @Override
            public void onPageFinished(WebView v, String url) {
                paginaCarregada = true;
                loading.setVisibility(View.GONE);
                web.setVisibility(View.VISIBLE);
                avisarFfmpeg();
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onJsAlert(WebView v, String url, String msg, final JsResult r) {
                new AlertDialog.Builder(MainActivity.this).setMessage(msg)
                        .setPositiveButton("OK", (d, w) -> r.confirm())
                        .setOnCancelListener(d -> r.cancel()).show();
                return true;
            }

            @Override
            public boolean onJsConfirm(WebView v, String url, String msg, final JsResult r) {
                new AlertDialog.Builder(MainActivity.this).setMessage(msg)
                        .setPositiveButton("OK", (d, w) -> r.confirm())
                        .setNegativeButton("Cancelar", (d, w) -> r.cancel())
                        .setOnCancelListener(d -> r.cancel()).show();
                return true;
            }

            @Override
            public boolean onJsPrompt(WebView v, String url, String msg, String def, final JsPromptResult r) {
                final android.widget.EditText et = new android.widget.EditText(MainActivity.this);
                et.setText(def);
                new AlertDialog.Builder(MainActivity.this).setMessage(msg).setView(et)
                        .setPositiveButton("OK", (d, w) -> r.confirm(et.getText().toString()))
                        .setNegativeButton("Cancelar", (d, w) -> r.cancel())
                        .setOnCancelListener(d -> r.cancel()).show();
                return true;
            }
        });
        web.setDownloadListener(new DownloadListener() {
            @Override
            public void onDownloadStart(String url, String ua, String cd, String mime, long len) {
                try {
                    DownloadManager.Request rq = new DownloadManager.Request(Uri.parse(url));
                    String nome = URLUtil.guessFileName(url, cd, mime);
                    rq.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, nome);
                    rq.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                    ((DownloadManager) getSystemService(DOWNLOAD_SERVICE)).enqueue(rq);
                } catch (Exception ignored) {
                }
            }
        });
    }

    private void pedirPermissoes() {
        if (Build.VERSION.SDK_INT >= 23
                && checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{
                    Manifest.permission.READ_EXTERNAL_STORAGE,
                    Manifest.permission.WRITE_EXTERNAL_STORAGE}, 1);
        }
    }

    private void iniciarServico() {
        // Serviço comum: só vira "primeiro plano" (com notificação) quando há download ou música tocando.
        startService(new Intent(this, PythonService.class));
    }

    /** Espera o servidor Python ficar pronto e então abre a página. */
    private void aguardarServidor() {
        ui.post(new Runnable() {
            @Override
            public void run() {
                if (destruida) return;
                if (PythonService.error != null) {
                    spinner.setVisibility(View.GONE);
                    loadingText.setText("Não foi possível iniciar o WaveFly.\n\n" + PythonService.error);
                    return;
                }
                if (PythonService.ready) {
                    if (!paginaCarregada) web.loadUrl(HOME);
                    return;
                }
                loadingText.setText(PythonService.status);
                ui.postDelayed(this, 300);
            }
        });
    }

    @Override
    public void onBackPressed() {
        if (web != null && paginaCarregada && web.canGoBack()) web.goBack();
        else moveTaskToBack(true);
    }

    /** Manda um comando (play, pause, next, prev) para o player da página. Usado pela notificação. */
    static void comandoPlayer(final String cmd) {
        final MainActivity a = atual;
        if (a == null) return;
        a.runOnUiThread(() -> {
            if (a.web != null && !a.destruida && a.paginaCarregada) {
                a.web.evaluateJavascript("window.wfCmd&&wfCmd('" + cmd + "')", null);
            }
        });
    }

    /** Funções do Android que a página pode chamar. */
    private class Ponte {
        /** A página avisa o estado do player para a notificação. */
        @JavascriptInterface
        public void player(int ativo, int tocando, int video, String titulo, String sub, int posMs, int durMs, String capa) {
            PythonService.pCapa = capa == null ? "" : capa;
            PythonService.pTitulo = titulo == null ? "" : titulo;
            PythonService.pSub = sub == null ? "" : sub;
            PythonService.pVideo = video == 1;
            PythonService.pTocando = tocando == 1;
            PythonService.pPosMs = posMs;
            PythonService.pDurMs = durMs;
            PythonService.pEm = SystemClock.elapsedRealtime();
            PythonService.pAtivo = ativo == 1;
        }

        /** Prévia de vídeo da busca: abre numa janela própria com origem https (o YouTube recusa localhost). */
        @JavascriptInterface
        public void preview(final String id) {
            runOnUiThread(() -> mostrarPrevia(id));
        }

        @JavascriptInterface
        public String paste() {
            final String[] out = {""};
            final java.util.concurrent.CountDownLatch l = new java.util.concurrent.CountDownLatch(1);
            runOnUiThread(() -> {
                try {
                    ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                    if (cm != null && cm.hasPrimaryClip()) {
                        ClipData d = cm.getPrimaryClip();
                        if (d != null && d.getItemCount() > 0) {
                            CharSequence t = d.getItemAt(0).coerceToText(MainActivity.this);
                            if (t != null) out[0] = t.toString();
                        }
                    }
                } catch (Exception ignored) {
                }
                l.countDown();
            });
            try {
                l.await(1, java.util.concurrent.TimeUnit.SECONDS);
            } catch (InterruptedException ignored) {
            }
            return out[0];
        }
    }

    private android.app.Dialog previa;

    private void mostrarPrevia(String id) {
        if (id == null || !id.matches("[A-Za-z0-9_-]{6,20}")) return;
        if (previa != null) previa.dismiss();
        final WebView w = new WebView(this);
        WebSettings st = w.getSettings();
        st.setJavaScriptEnabled(true);
        st.setDomStorageEnabled(true);
        st.setMediaPlaybackRequiresUserGesture(false);
        w.setBackgroundColor(Color.BLACK);
        w.setWebChromeClient(new WebChromeClient());
        w.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, android.webkit.WebResourceRequest r) {
                String h = r.getUrl().getHost();
                return h == null || !(h.endsWith("youtube.com") || h.endsWith("youtube-nocookie.com")
                        || h.endsWith("google.com") || h.endsWith("gstatic.com") || h.endsWith("ytimg.com")
                        || h.endsWith("googlevideo.com"));
            }
        });
        String html = "<html><body style='margin:0;background:#000'><iframe style='position:fixed;inset:0;width:100%;height:100%;border:0' "
                + "src='https://www.youtube.com/embed/" + id + "?autoplay=1&playsinline=1&rel=0&modestbranding=1' "
                + "allow='autoplay; encrypted-media; picture-in-picture; fullscreen' allowfullscreen "
                + "referrerpolicy='strict-origin-when-cross-origin'></iframe></body></html>";
        w.loadDataWithBaseURL("https://www.youtube.com/", html, "text/html", "utf-8", null);

        FrameLayout box = new FrameLayout(this);
        box.setBackgroundColor(Color.BLACK);
        int largura = getResources().getDisplayMetrics().widthPixels;
        box.addView(w, new FrameLayout.LayoutParams(largura, largura * 9 / 16));
        TextView fechar = new TextView(this);
        fechar.setText("✕  Fechar");
        fechar.setTextColor(Color.WHITE);
        fechar.setTextSize(16);
        fechar.setPadding(40, 28, 40, 28);
        fechar.setBackgroundColor(0xFF3B2314);
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.BOTTOM | Gravity.END);
        box.addView(fechar, lp);
        box.setMinimumHeight(largura * 9 / 16 + 120);

        final android.app.Dialog d = new android.app.Dialog(this, android.R.style.Theme_DeviceDefault_NoActionBar);
        d.setContentView(box);
        d.setOnDismissListener(x -> {
            w.loadUrl("about:blank");
            w.destroy();
            if (previa == d) previa = null;
        });
        fechar.setOnClickListener(x -> d.dismiss());
        previa = d;
        d.show();
        if (d.getWindow() != null) {
            d.getWindow().setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            d.getWindow().setGravity(Gravity.TOP);
        }
    }

    /** Se o conversor (ffmpeg) não iniciou, mostra o motivo uma vez. */
    private void avisarFfmpeg() {
        if (avisouFfmpeg) return;
        String info = PythonService.ffmpegInfo;
        if (info == null || info.isEmpty() || info.toLowerCase().startsWith("ffmpeg version")) return;
        avisouFfmpeg = true;
        new AlertDialog.Builder(this)
                .setTitle("Conversor de áudio com problema")
                .setMessage("O ffmpeg não iniciou. Mande esta mensagem para o suporte:\n\n" + info)
                .setPositiveButton("OK", null).show();
    }

    @Override
    protected void onStart() {
        super.onStart();
        PythonService.visivel = true;
        iniciarServico();
    }

    @Override
    protected void onStop() {
        PythonService.visivel = false;
        super.onStop();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.resumeTimers();
    }

    @Override
    protected void onDestroy() {
        destruida = true;
        if (atual == this) atual = null;
        ui.removeCallbacksAndMessages(null);
        if (web != null) {
            ((ViewGroup) web.getParent()).removeView(web);
            web.destroy();
        }
        super.onDestroy();
    }
}
