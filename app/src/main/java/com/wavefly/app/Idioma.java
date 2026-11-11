package com.wavefly.app;

import android.content.Context;
import android.content.SharedPreferences;

import java.util.Locale;

/** Idioma do app (pt, en, es) e preferências simples, usadas também fora da página. */
final class Idioma {
    private Idioma() {
    }

    static SharedPreferences prefs(Context c) {
        return c.getApplicationContext().getSharedPreferences("wavefly", Context.MODE_PRIVATE);
    }

    static String lang(Context c) {
        String l = prefs(c).getString("lang", "");
        if (l.equals("pt") || l.equals("en") || l.equals("es")) return l;
        String s = Locale.getDefault().getLanguage();
        return s.equals("es") ? "es" : s.equals("en") ? "en" : "pt";
    }

    static String t(Context c, String pt, String en, String es) {
        String l = lang(c);
        return l.equals("en") ? en : l.equals("es") ? es : pt;
    }
}
