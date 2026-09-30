package com.corvus.app;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class MainActivity extends Activity {
    private WebView webView;

    private static final String API_BASE =
        "http://127.0.0.1:8765";

    private static final String API_TOKEN =
        "ez7bsetraDt5QRgd6auS8WsUPFFhTu1oUwTut3Ip8GY";

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

        checkCorvusHealth();
    }

    private void checkCorvusHealth() {
        new Thread(() -> {
            HttpURLConnection connection = null;

            try {
                URL url = new URL(API_BASE + "/status");
                connection =
                    (HttpURLConnection) url.openConnection();

                connection.setRequestMethod("GET");
                connection.setConnectTimeout(3000);
                connection.setReadTimeout(10000);
                connection.setRequestProperty(
                    "Authorization",
                    "Bearer " + API_TOKEN
                );
                connection.setRequestProperty(
                    "Connection",
                    "close"
                );

                int code = connection.getResponseCode();

                if (code == 200) {
                    setStatus("NORMAL");
                } else {
                    setStatus("DEGRADED");
                }

            } catch (Exception e) {
                setStatus("OFFLINE");

            } finally {
                if (connection != null) {
                    connection.disconnect();
                }
            }
        }).start();
    }

    void performAsk(String prompt) {
        HttpURLConnection connection = null;

        try {
            setStatus("THINKING");

            URL url = new URL(API_BASE + "/ask");
            connection =
                (HttpURLConnection) url.openConnection();

            connection.setRequestMethod("POST");
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(610000);
            connection.setDoOutput(true);

            connection.setRequestProperty(
                "Authorization",
                "Bearer " + API_TOKEN
            );

            connection.setRequestProperty(
                "Content-Type",
                "application/json; charset=utf-8"
            );

            connection.setRequestProperty(
                "Connection",
                "close"
            );

            JSONObject request = new JSONObject();
            request.put("prompt", prompt);

            byte[] payload =
                request.toString().getBytes(StandardCharsets.UTF_8);

            connection.setFixedLengthStreamingMode(payload.length);

            try (OutputStream out = connection.getOutputStream()) {
                out.write(payload);
            }

            int code = connection.getResponseCode();

            InputStream stream =
                code >= 200 && code < 300
                    ? connection.getInputStream()
                    : connection.getErrorStream();

            String body = readStream(stream);
            JSONObject response = new JSONObject(body);

            if (code == 200) {
                String answer =
                    response.optString("output", "").trim();

                deliverAnswer(answer);
                setStatus("NORMAL");
            } else {
                String error =
                    response.optString(
                        "error",
                        "CORVUS request failed"
                    );

                deliverError(error);
                setStatus("DEGRADED");
            }

        } catch (Exception e) {
            deliverError(
                "CORVUS ERROR: " +
                e.getClass().getSimpleName() +
                ": " +
                String.valueOf(e.getMessage())
            );
            setStatus("OFFLINE");

        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    private String readStream(InputStream stream)
            throws Exception {
        if (stream == null) {
            return "{}";
        }

        BufferedReader reader =
            new BufferedReader(
                new InputStreamReader(
                    stream,
                    StandardCharsets.UTF_8
                )
            );

        StringBuilder body = new StringBuilder();
        String line;

        while ((line = reader.readLine()) != null) {
            body.append(line);
        }

        reader.close();
        return body.toString();
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
