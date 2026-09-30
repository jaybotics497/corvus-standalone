package com.corvus.app;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.IBinder;

import java.io.File;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class CorvusEngineService extends Service {

    public interface Callback {
        void onAnswer(String answer);
        void onError(String error);
    }

    private static final ExecutorService EXECUTOR =
        Executors.newSingleThreadExecutor();

    static {
        System.loadLibrary("c++_shared");
        System.loadLibrary("ggml-base");
        System.loadLibrary("ggml");
        System.loadLibrary("ggml-cpu");
        System.loadLibrary("llama");
        System.loadLibrary("corvus");
    }

    private static native String nativeAsk(
        String modelPath,
        String prompt
    );

    public static void submit(
        Context context,
        String prompt,
        Callback callback
    ) {

        if (prompt == null ||
            prompt.trim().isEmpty()) {

            callback.onError(
                "Prompt required."
            );

            return;
        }

        File model =
            ModelManager.modelFile(context);

        if (!ModelManager.isReady(context)) {
            callback.onError(
                "Verified local model unavailable."
            );
            return;
        }

        EXECUTOR.execute(() -> {
            try {
                String answer =
                    nativeAsk(
                        model.getAbsolutePath(),
                        prompt.trim()
                    );

                if (answer == null ||
                    answer.trim().isEmpty()) {

                    callback.onError(
                        "Native CORVUS returned no response."
                    );

                    return;
                }

                callback.onAnswer(
                    answer.trim()
                );

            } catch (Throwable e) {
                callback.onError(
                    "CORVUS native engine: " +
                    e.getClass()
                     .getSimpleName()
                );
            }
        });
    }

    @Override
    public void onCreate() {
        super.onCreate();

        android.util.Log.i(
            "CORVUS_ENGINE",
            "Native CORVUS service started"
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
    public IBinder onBind(
        Intent intent
    ) {
        return null;
    }
}
