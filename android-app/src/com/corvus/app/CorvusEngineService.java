package com.corvus.app;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

public class CorvusEngineService extends Service {

    @Override
    public void onCreate() {
        super.onCreate();
        android.util.Log.i("CORVUS_ENGINE", "Native engine service started");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
