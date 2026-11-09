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

    /** Devolve {pastaBin, caminhoLibs} ou null se não achou o ffmpeg. */
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

            boolean pronto = marker.exists() && versao.equals(readText(marker)) && new File(bin, "ffmpeg").canExecute();
            if (!pronto) {
                deleteRecursive(root);
                deleteRecursive(bin);
                root.mkdirs();
                bin.mkdirs();
                File[] libs = nativeDir.listFiles();
                if (libs != null) {
                    for (File f : libs) {
                        String n = f.getName();
                        if (n.contains("ffmpeg") && n.endsWith(".zip.so")) {
                            unzip(f, root);
                        }
                    }
                }
                File exe = find(root, "libffmpeg.so");
                if (exe == null) {
                    File direto = new File(nativeDir, "libffmpeg.so");
                    if (direto.exists()) exe = direto;
                }
                if (exe == null) {
                    Log.e(TAG, "ffmpeg não encontrado no APK");
                    return null;
                }
                copy(exe, new File(bin, "ffmpeg"));
                File probe = find(root, "libffprobe.so");
                if (probe != null) copy(probe, new File(bin, "ffprobe"));
                writeText(marker, versao);
            }

            Set<String> dirs = new LinkedHashSet<>();
            collectLibDirs(root, dirs);
            dirs.add(nativeDir.getAbsolutePath());
            StringBuilder ld = new StringBuilder();
            for (String d : dirs) {
                if (ld.length() > 0) ld.append(':');
                ld.append(d);
            }
            return new String[]{bin.getAbsolutePath(), ld.toString()};
        } catch (Throwable t) {
            Log.e(TAG, "Falha preparando ffmpeg", t);
            return null;
        }
    }

    private static void unzip(File zip, File dest) throws IOException {
        String destPath = dest.getCanonicalPath() + File.separator;
        try (ZipInputStream in = new ZipInputStream(new FileInputStream(zip))) {
            ZipEntry e;
            byte[] buf = new byte[65536];
            while ((e = in.getNextEntry()) != null) {
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
