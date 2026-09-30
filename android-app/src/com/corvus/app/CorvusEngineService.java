package com.corvus.app;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.IBinder;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class CorvusEngineService extends Service {

    public interface Callback {
        void onAnswer(String answer);
        void onError(String error);
    }

    private static final ExecutorService executor =
        Executors.newSingleThreadExecutor();

    static {
        try {
            System.loadLibrary("corvus");
        } catch (UnsatisfiedLinkError ignored) {
        }
    }

    private static native String nativeAsk(
        String filesDir,
        String prompt
    );

    public static void submit(
        Context context,
        String prompt,
        Callback callback
    ) {
        if (prompt == null || prompt.trim().isEmpty()) {
            callback.onError("Prompt required.");
            return;
        }

        final String filesDir =
            context.getApplicationContext()
                   .getFilesDir()
                   .getAbsolutePath();

        executor.execute(() -> {
            try {
                String answer = nativeAsk(filesDir, prompt);

                if (answer == null || answer.trim().isEmpty()) {
                    callback.onError(
                        "Native CORVUS returned no response."
                    );
                    return;
                }

                callback.onAnswer(answer.trim());

            } catch (UnsatisfiedLinkError e) {
                callback.onError(
                    "Native CORVUS runtime is not installed yet."
                );

            } catch (Throwable e) {
                callback.onError(
                    "CORVUS engine error: " +
                    e.getClass().getSimpleName()
                );
            }
        });
    }

    @Override
    public void onCreate() {
        super.onCreate();
        android.util.Log.i(
            "CORVUS_ENGINE",
            "App-owned engine service started"
        );
    }

    @Override
    public int onStartCommand(
        Intent intent,
        int flags,
        int startId
    ) {
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
