package com.wavefly.app;

import android.content.Context;
import android.content.pm.PackageInfo;
import android.util.Log;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Prepara o ffmpeg que vem dentro do APK (biblioteca nativa empacotada em zip),
 * descompactando para a pasta privada do app e deixando executável.
 */
final class FfmpegSetup {
    private static final String TAG = "WaveFly";

    private FfmpegSetup() {}

    /** Devolve {pastaBin, caminhoLibs, resultadoDoTeste} ou null se não achou o ffmpeg. */
    static String[] prepare(Context ctx) {
        try {
            File nativeDir = new File(ctx.getApplicationInfo().nativeLibraryDir);
            File root = new File(ctx.getFilesDir(), "ffmpeg");
            File bin = new File(ctx.getFilesDir(), "bin");
            File marker = new File(root, ".versao");
            String versao = "0";
            try {
                PackageInfo pi = ctx.getPackageManager().getPackageInfo(ctx.getPackageName(), 0);
                versao = String.valueOf(pi.lastUpdateTime);
            } catch (Exception ignored) {
            }

            // As bibliotecas do ffmpeg vêm num zip dentro do APK: descompacta uma vez por versão.
            if (!(marker.exists() && versao.equals(readText(marker)))) {
                deleteRecursive(root);
                root.mkdirs();
                File[] libs = nativeDir.listFiles();
                if (libs != null) {
                    for (File f : libs) {
                        String n = f.getName();
                        if (n.endsWith(".zip.so") && (n.contains("ffmpeg") || n.contains("python"))) {
                            unzip(f, root, !n.contains("ffmpeg"));
                        }
                    }
                }
                writeText(marker, versao);
            }

            // Os executáveis ficam na pasta nativa (único lugar onde o Android deixa executar).
            File exe = new File(nativeDir, "libffmpeg.so");
            File probe = new File(nativeDir, "libffprobe.so");
            if (!exe.exists()) {
                Log.e(TAG, "libffmpeg.so não está em " + nativeDir);
                return null;
            }
            deleteRecursive(bin);
            bin.mkdirs();
            android.system.Os.symlink(exe.getAbsolutePath(), new File(bin, "ffmpeg").getAbsolutePath());
            if (probe.exists()) {
                android.system.Os.symlink(probe.getAbsolutePath(), new File(bin, "ffprobe").getAbsolutePath());
            }

            Set<String> dirs = new LinkedHashSet<>();
            collectLibDirs(root, dirs);
            dirs.add(nativeDir.getAbsolutePath());
            StringBuilder ld = new StringBuilder();
            for (String d : dirs) {
                if (ld.length() > 0) ld.append(':');
                ld.append(d);
            }
            String teste = selfTest(new File(bin, "ffmpeg"), ld.toString());
            Log.i(TAG, "teste ffmpeg: " + teste);
            return new String[]{bin.getAbsolutePath(), ld.toString(), teste};
        } catch (Throwable t) {
            Log.e(TAG, "Falha preparando ffmpeg", t);
            return new String[]{"", "", "ERRO: " + t};
        }
    }

    /** Roda "ffmpeg -version" e devolve a primeira linha (ou o erro). */
    private static String selfTest(File ffmpeg, String ld) {
        try {
            ProcessBuilder pb = new ProcessBuilder(ffmpeg.getAbsolutePath(), "-version");
            pb.environment().put("LD_LIBRARY_PATH", ld);
            pb.redirectErrorStream(true);
            Process p = pb.start();
            StringBuilder sb = new StringBuilder();
            try (InputStream in = p.getInputStream()) {
                byte[] buf = new byte[1500];
                int n;
                while (sb.length() < 1500 && (n = in.read(buf)) > 0) sb.append(new String(buf, 0, n, "UTF-8"));
            }
            p.waitFor(5, java.util.concurrent.TimeUnit.SECONDS);
            String t = sb.toString().trim();
            if (t.toLowerCase().startsWith("ffmpeg version")) {
                int nl = t.indexOf('\n');
                return nl > 0 ? t.substring(0, nl) : t;
            }
            return t.replace("\n", " | ") + " [LD=" + ld + "]";
        } catch (Throwable t) {
            return "ERRO: " + t;
        }
    }

    private static void unzip(File zip, File dest, boolean soSomente) throws IOException {
        String destPath = dest.getCanonicalPath() + File.separator;
        try (ZipInputStream in = new ZipInputStream(new FileInputStream(zip))) {
            ZipEntry e;
            byte[] buf = new byte[65536];
            while ((e = in.getNextEntry()) != null) {
                if (soSomente && !e.getName().matches("(?:\\./)?usr/lib/[^/]+\\.so[^/]*")) continue;
                File out = new File(dest, e.getName());
                if (!out.getCanonicalPath().startsWith(destPath)) continue; // protege contra zip-slip
                if (e.isDirectory()) {
                    out.mkdirs();
                    continue;
                }
                File parent = out.getParentFile();
                if (parent != null) parent.mkdirs();
                try (OutputStream os = new FileOutputStream(out)) {
                    int n;
                    while ((n = in.read(buf)) > 0) os.write(buf, 0, n);
                }
                out.setReadable(true, false);
                out.setExecutable(true, false);
                // No zip, "libX.so.61" é um atalho (link). Aqui ele sai como um arquivo pequeno
                // com o nome do alvo dentro; recria como link de verdade.
                if (out.length() < 200 && out.getName().contains(".so")) {
                    String alvo = readText(out);
                    if (alvo.matches("[A-Za-z0-9._+\\-/]+") && !alvo.equals(out.getName())) {
                        out.delete();
                        try {
                            android.system.Os.symlink(alvo, out.getAbsolutePath());
                        } catch (Exception ex) {
                            Log.e(TAG, "symlink " + out + " -> " + alvo, ex);
                        }
                    }
                }
            }
        }
    }

    private static File find(File dir, String name) {
        File[] fs = dir.listFiles();
        if (fs == null) return null;
        for (File f : fs) {
            if (f.isDirectory()) {
                File r = find(f, name);
                if (r != null) return r;
            } else if (f.getName().equals(name)) {
                return f;
            }
        }
        return null;
    }

    private static void collectLibDirs(File dir, Set<String> out) {
        File[] fs = dir.listFiles();
        if (fs == null) return;
        for (File f : fs) {
            if (f.isDirectory()) collectLibDirs(f, out);
            else if (f.getName().endsWith(".so")) out.add(dir.getAbsolutePath());
        }
    }

    private static void copy(File src, File dst) throws IOException {
        try (InputStream in = new FileInputStream(src); OutputStream out = new FileOutputStream(dst)) {
            byte[] buf = new byte[65536];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
        }
        dst.setReadable(true, false);
        dst.setExecutable(true, false);
    }

    private static String readText(File f) {
        try (InputStream in = new FileInputStream(f)) {
            byte[] b = new byte[(int) f.length()];
            int n = in.read(b);
            return new String(b, 0, Math.max(n, 0), "UTF-8").trim();
        } catch (IOException e) {
            return "";
        }
    }

    private static void writeText(File f, String s) throws IOException {
        try (OutputStream out = new FileOutputStream(f)) {
            out.write(s.getBytes("UTF-8"));
        }
    }

    private static void deleteRecursive(File f) {
        if (f == null || !f.exists()) return;
        File[] fs = f.listFiles();
        if (fs != null) for (File c : fs) deleteRecursive(c);
        f.delete();
    }
}
