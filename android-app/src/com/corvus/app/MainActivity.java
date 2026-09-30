package com.corvus.app;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;

import org.json.JSONObject;

public class MainActivity extends Activity {
    private WebView webView;


    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);

        startService(new android.content.Intent(this, CorvusEngineService.class));

        webView = new WebView(this);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);

        webView.addJavascriptInterface(
            new CorvusBridge(this),
            "CorvusBridge"
        );

        webView.setBackgroundColor(0xFF000000);

        setContentView(webView);
        webView.loadUrl("file:///android_asset/index.html");

        setStatus("READY");
    }

    void performAsk(String prompt) {
        setStatus("THINKING");

        CorvusEngineService.submit(
            this,
            prompt,
            new CorvusEngineService.Callback() {
                @Override
                public void onAnswer(String answer) {
                    deliverAnswer(answer);
                    setStatus("READY");
                }

                @Override
                public void onError(String error) {
                    deliverError(error);
                    setStatus("DEGRADED");
                }
            }
        );
    }

    private void deliverAnswer(String answer) {
        runOnUiThread(() -> {
            String js =
                "window.corvusReceive(" +
                JSONObject.quote(answer) +
                ");";

            webView.evaluateJavascript(js, null);
        });
    }

    private void deliverError(String error) {
        runOnUiThread(() -> {
            String js =
                "window.corvusError(" +
                JSONObject.quote(error) +
                ");";

            webView.evaluateJavascript(js, null);
        });
    }

    private void setStatus(String status) {
        runOnUiThread(() -> {
            String js =
                "window.corvusSetStatus && " +
                "window.corvusSetStatus(" +
                JSONObject.quote(status) +
                ");";

            webView.evaluateJavascript(js, null);
        });
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
