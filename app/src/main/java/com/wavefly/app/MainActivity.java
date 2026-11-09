package com.wavefly.app;

import android.Manifest;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.DownloadListener;
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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
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
        iniciarServico();
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
        Intent i = new Intent(this, PythonService.class);
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(i);
        else startService(i);
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

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.onResume();
    }

    @Override
    protected void onPause() {
        if (web != null) web.onPause();
        super.onPause();
    }

    @Override
    protected void onDestroy() {
        destruida = true;
        ui.removeCallbacksAndMessages(null);
        if (web != null) {
            ((ViewGroup) web.getParent()).removeView(web);
            web.destroy();
        }
        super.onDestroy();
    }
}
