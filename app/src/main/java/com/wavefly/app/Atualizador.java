package com.wavefly.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.Uri;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/** Procura uma versão nova do app no GitHub e instala com um toque. */
final class Atualizador {
    private static final String API = "https://api.github.com/repos/MayconHBM/wavefly-app/releases?per_page=15";
    private static long ultima = 0;

    private Atualizador() {
    }

    static void verificar(final Activity a, final boolean manual) {
        if (!manual && System.currentTimeMillis() - ultima < 6 * 3600_000L) return;
        ultima = System.currentTimeMillis();
        new Thread(() -> {
            try {
                HttpURLConnection c = (HttpURLConnection) new URL(API).openConnection();
                c.setConnectTimeout(8000);
                c.setReadTimeout(8000);
                c.setRequestProperty("Accept", "application/vnd.github+json");
                if (c.getResponseCode() != 200) throw new RuntimeException("http " + c.getResponseCode());
                InputStream in = c.getInputStream();
                java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
                byte[] b = new byte[8192];
                int n;
                while ((n = in.read(b)) > 0) bo.write(b, 0, n);
                JSONArray lista = new JSONArray(bo.toString("UTF-8"));
                int local = a.getPackageManager().getPackageInfo(a.getPackageName(), 0).versionCode;
                String vn = a.getPackageManager().getPackageInfo(a.getPackageName(), 0).versionName;
                boolean teste = vn != null && vn.contains("teste");   // quem usa versão de teste também recebe as de teste
                JSONObject j = new JSONObject();
                int remoto = 0;
                java.util.regex.Pattern pv = java.util.regex.Pattern.compile("versionCode:\\s*(\\d+)");
                for (int k = 0; k < lista.length(); k++) {
                    JSONObject r = lista.getJSONObject(k);
                    if (r.optBoolean("draft") || (r.optBoolean("prerelease") && !teste)) continue;
                    java.util.regex.Matcher mm = pv.matcher(r.optString("body", ""));
                    int v = mm.find() ? Integer.parseInt(mm.group(1)) : 0;
                    if (v > remoto) {
                        remoto = v;
                        j = r;
                    }
                }
                String url = "";
                JSONArray as = j.optJSONArray("assets");
                for (int i = 0; as != null && i < as.length(); i++) {
                    String u = as.getJSONObject(i).optString("browser_download_url", "");
                    if (u.endsWith(".apk")) url = u;
                }
                final String nome = j.optString("name", j.optString("tag_name", ""));
                final String apk = url;
                final boolean nova = remoto > local && !apk.isEmpty();
                a.runOnUiThread(() -> {
                    if (a.isFinishing()) return;
                    if (nova) perguntar(a, nome, apk);
                    else if (manual) Toast.makeText(a, Idioma.t(a, "O WaveFly já está atualizado.",
                            "WaveFly is up to date.", "WaveFly ya está actualizado."), Toast.LENGTH_LONG).show();
                });
            } catch (Throwable t) {
                if (manual) a.runOnUiThread(() -> Toast.makeText(a, Idioma.t(a,
                        "Não consegui verificar atualizações agora.", "Could not check for updates right now.",
                        "No pude comprobar actualizaciones ahora."), Toast.LENGTH_LONG).show());
            }
        }, "wavefly-update").start();
    }

    private static void perguntar(final Activity a, String nome, final String apk) {
        new AlertDialog.Builder(a)
                .setTitle(Idioma.t(a, "Nova versão disponível", "New version available", "Nueva versión disponible"))
                .setMessage(nome + "\n\n" + Idioma.t(a,
                        "Quer baixar e instalar agora? Suas configurações e downloads são mantidos.",
                        "Download and install now? Your settings and downloads are kept.",
                        "¿Descargar e instalar ahora? Se mantienen tus ajustes y descargas."))
                .setPositiveButton(Idioma.t(a, "Atualizar", "Update", "Actualizar"), (d, w) -> baixar(a, apk))
                .setNegativeButton(Idioma.t(a, "Depois", "Later", "Más tarde"), null)
                .show();
    }

    private static void baixar(final Context c, String url) {
        try {
            File dir = c.getExternalFilesDir(null);
            final File arq = new File(dir, "WaveFly-novo.apk");
            if (arq.exists()) arq.delete();
            DownloadManager.Request rq = new DownloadManager.Request(Uri.parse(url));
            rq.setDestinationUri(Uri.fromFile(arq));
            rq.setTitle("WaveFly");
            rq.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            final DownloadManager dm = (DownloadManager) c.getSystemService(Context.DOWNLOAD_SERVICE);
            final long id = dm.enqueue(rq);
            Toast.makeText(c, Idioma.t(c, "Baixando a atualização…", "Downloading the update…",
                    "Descargando la actualización…"), Toast.LENGTH_LONG).show();
            c.getApplicationContext().registerReceiver(new BroadcastReceiver() {
                @Override
                public void onReceive(Context ctx, Intent i) {
                    if (i.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1) != id) return;
                    try {
                        ctx.getApplicationContext().unregisterReceiver(this);
                    } catch (Throwable ignored) {
                    }
                    instalar(ctx, arq);
                }
            }, new IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE));
        } catch (Throwable t) {
            try {
                c.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            } catch (Throwable ignored) {
            }
        }
    }

    private static void instalar(Context c, File arq) {
        try {
            Uri u = androidx.core.content.FileProvider.getUriForFile(c, c.getPackageName() + ".arquivos", arq);
            Intent i = new Intent(Intent.ACTION_VIEW);
            i.setDataAndType(u, "application/vnd.android.package-archive");
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
            c.startActivity(i);
        } catch (Throwable t) {
            Toast.makeText(c, "APK: " + t.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

}
