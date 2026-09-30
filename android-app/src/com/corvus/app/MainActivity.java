package com.corvus.app;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;

import org.json.JSONObject;

public class MainActivity extends Activity {

    private static final int PICK_MODEL = 6001;

    private WebView webView;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);

        startService(
            new Intent(
                this,
                CorvusEngineService.class
            )
        );

        webView = new WebView(this);

        WebSettings settings =
            webView.getSettings();

        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);

        webView.addJavascriptInterface(
            new CorvusBridge(this),
            "CorvusBridge"
        );

        webView.setBackgroundColor(0xFF000000);

        setContentView(webView);

        webView.loadUrl(
            "file:///android_asset/index.html"
        );

        webView.postDelayed(() -> {
            if (ModelManager.isReady(this)) {
                setStatus("READY");
            } else {
                setStatus("MODEL REQUIRED");
                requestModel();
            }
        }, 500);
    }

    private void requestModel() {
        Intent intent =
            new Intent(Intent.ACTION_OPEN_DOCUMENT);

        intent.addCategory(
            Intent.CATEGORY_OPENABLE
        );

        intent.setType(
            "application/octet-stream"
        );

        startActivityForResult(
            intent,
            PICK_MODEL
        );
    }

    @Override
    protected void onActivityResult(
        int requestCode,
        int resultCode,
        Intent data
    ) {
        super.onActivityResult(
            requestCode,
            resultCode,
            data
        );

        if (requestCode != PICK_MODEL ||
            resultCode != RESULT_OK ||
            data == null ||
            data.getData() == null) {

            return;
        }

        Uri uri = data.getData();

        setStatus("IMPORTING MODEL");

        new Thread(() -> {
            try {
                ModelManager.importModel(
                    this,
                    uri
                );

                setStatus("READY");
                deliverAnswer(
                    "Local model imported and verified."
                );

            } catch (Exception e) {
                setStatus("MODEL ERROR");
                deliverError(e.getMessage());
            }
        }).start();
    }

    void performAsk(String prompt) {

        if (!ModelManager.isReady(this)) {
            deliverError(
                "Local model is not installed."
            );
            requestModel();
            return;
        }

        setStatus("THINKING");

        CorvusEngineService.submit(
            this,
            prompt,
            new CorvusEngineService.Callback() {

                @Override
                public void onAnswer(
                    String answer
                ) {
                    deliverAnswer(answer);
                    setStatus("READY");
                }

                @Override
                public void onError(
                    String error
                ) {
                    deliverError(error);
                    setStatus("DEGRADED");
                }
            }
        );
    }

    private void deliverAnswer(String answer) {
        runOnUiThread(() -> {
            webView.evaluateJavascript(
                "window.corvusReceive(" +
                JSONObject.quote(answer) +
                ");",
                null
            );
        });
    }

    private void deliverError(String error) {
        runOnUiThread(() -> {
            webView.evaluateJavascript(
                "window.corvusError(" +
                JSONObject.quote(error) +
                ");",
                null
            );
        });
    }

    private void setStatus(String status) {
        runOnUiThread(() -> {
            webView.evaluateJavascript(
                "window.corvusSetStatus && " +
                "window.corvusSetStatus(" +
                JSONObject.quote(status) +
                ");",
                null
            );
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
