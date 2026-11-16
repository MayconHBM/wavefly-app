package com.wavefly.app;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.util.HashSet;
import java.util.Set;

/** Login opcional no YouTube: o usuário entra na própria conta e o app guarda os cookies só neste aparelho. */
public class LoginActivity extends Activity {
    private WebView web;
    private boolean fechou = false;

    static File arquivo(android.content.Context c) {
        return new File(c.getFilesDir(), "cookies.txt");
    }

    static void sair(android.content.Context c) {
        try { arquivo(c).delete(); } catch (Exception ignore) { }
        try { CookieManager.getInstance().removeAllCookies(null); CookieManager.getInstance().flush(); } catch (Exception ignore) { }
    }

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        LinearLayout raiz = new LinearLayout(this);
        raiz.setOrientation(LinearLayout.VERTICAL);
        raiz.setBackgroundColor(Color.WHITE);

        LinearLayout barra = new LinearLayout(this);
        barra.setOrientation(LinearLayout.HORIZONTAL);
        barra.setGravity(Gravity.CENTER_VERTICAL);
        barra.setPadding(24, 16, 24, 16);
        TextView t = new TextView(this);
        t.setText(Idioma.t(this, "Entre na sua conta do YouTube. O login fecha sozinho quando terminar.",
                "Sign in to your YouTube account. It closes by itself when done.",
                "Inicia sesión en tu cuenta de YouTube. Se cierra solo al terminar."));
        t.setTextColor(Color.BLACK);
        t.setTextSize(13);
        barra.addView(t, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        Button cancelar = new Button(this);
        cancelar.setText(Idioma.t(this, "Cancelar", "Cancel", "Cancelar"));
        cancelar.setOnClickListener(v -> finish());
        barra.addView(cancelar);
        Button ok = new Button(this);
        ok.setText(Idioma.t(this, "Concluir", "Done", "Listo"));
        ok.setOnClickListener(v -> concluir(true));
        barra.addView(ok);
        raiz.addView(barra);

        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        // O Google recusa login em "WebView"; com a identificação de navegador comum ele aceita.
        String ua = s.getUserAgentString().replace("; wv", "").replaceAll("Version/\\d+\\.\\d+ ", "");
        s.setUserAgentString(ua);
        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);
        cm.setAcceptThirdPartyCookies(web, true);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView v, String url) {
                if (url != null && url.contains("youtube.com") && logado()) concluir(false);
            }
        });
        raiz.addView(web, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));
        setContentView(raiz);
        web.loadUrl("https://accounts.google.com/ServiceLogin?service=youtube&hl=" + Idioma.lang(this)
                + "&continue=" + android.net.Uri.encode("https://www.youtube.com/"));
    }

    private boolean logado() {
        String c = CookieManager.getInstance().getCookie("https://www.youtube.com");
        return c != null && (c.contains("SAPISID=") || c.contains("__Secure-3PAPISID="));
    }

    private void linhas(StringBuilder sb, Set<String> vistos, String url, String dominio) {
        String c = CookieManager.getInstance().getCookie(url);
        if (c == null) return;
        long exp = System.currentTimeMillis() / 1000 + 180L * 86400;
        for (String par : c.split(";")) {
            int i = par.indexOf('=');
            if (i <= 0) continue;
            String nome = par.substring(0, i).trim(), valor = par.substring(i + 1).trim();
            if (nome.isEmpty() || !vistos.add(dominio + "|" + nome)) continue;
            boolean host = nome.startsWith("__Host-");
            sb.append(host ? url.replace("https://", "") : dominio).append('\t')
              .append(host ? "FALSE" : "TRUE").append("\t/\tTRUE\t").append(exp).append('\t')
              .append(nome).append('\t').append(valor).append('\n');
        }
    }

    private void concluir(boolean manual) {
        if (fechou) return;
        try {
            CookieManager.getInstance().flush();
            if (!logado()) {
                if (manual) Toast.makeText(this, Idioma.t(this, "Login ainda não concluído.", "Sign-in not finished yet.",
                        "El inicio de sesión aún no terminó."), Toast.LENGTH_LONG).show();
                return;
            }
            StringBuilder sb = new StringBuilder("# Netscape HTTP Cookie File\n");
            Set<String> vistos = new HashSet<>();
            linhas(sb, vistos, "https://www.youtube.com", ".youtube.com");
            linhas(sb, vistos, "https://accounts.youtube.com", ".youtube.com");
            linhas(sb, vistos, "https://accounts.google.com", ".google.com");
            linhas(sb, vistos, "https://www.google.com", ".google.com");
            try (FileOutputStream o = new FileOutputStream(arquivo(this))) {
                o.write(sb.toString().getBytes("UTF-8"));
            }
            fechou = true;
            Toast.makeText(this, Idioma.t(this, "Login salvo.", "Sign-in saved.", "Inicio de sesión guardado."), Toast.LENGTH_SHORT).show();
            finish();
        } catch (Exception e) {
            Toast.makeText(this, "Erro: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    @Override
    protected void onDestroy() {
        if (web != null) { web.destroy(); web = null; }
        super.onDestroy();
    }
}
