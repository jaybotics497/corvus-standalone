package com.corvus.app;

import android.webkit.JavascriptInterface;

public class CorvusBridge {
    private final MainActivity activity;

    public CorvusBridge(MainActivity activity) {
        this.activity = activity;
    }

    @JavascriptInterface
    public void ask(String prompt) {
        if (prompt == null || prompt.trim().isEmpty()) {
            return;
        }

        new Thread(() -> activity.performAsk(prompt)).start();
    }
}
