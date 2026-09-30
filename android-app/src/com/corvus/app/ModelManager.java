package com.corvus.app;

import android.content.Context;
import android.net.Uri;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.security.MessageDigest;

public final class ModelManager {

    public static final String MODEL_NAME =
        "qwen2.5-1.5b-instruct-q4_k_m.gguf";

    public static final String EXPECTED_SHA256 =
        "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e";

    private ModelManager() {}

    public static File modelFile(Context context) {
        File dir = new File(context.getFilesDir(), "models");

        if (!dir.exists()) {
            dir.mkdirs();
        }

        return new File(dir, MODEL_NAME);
    }

    public static boolean isReady(Context context) {
        File f = modelFile(context);

        if (!f.isFile() || f.length() < 100000000L) {
            return false;
        }

        try {
            return EXPECTED_SHA256.equalsIgnoreCase(
                sha256(f)
            );
        } catch (Exception e) {
            return false;
        }
    }

    public static void importModel(
        Context context,
        Uri uri
    ) throws Exception {

        File target = modelFile(context);
        File temp = new File(
            target.getParentFile(),
            MODEL_NAME + ".importing"
        );

        if (temp.exists()) {
            temp.delete();
        }

        try (
            InputStream in =
                context.getContentResolver()
                       .openInputStream(uri);

            FileOutputStream out =
                new FileOutputStream(temp)
        ) {
            if (in == null) {
                throw new Exception(
                    "Unable to open selected model."
                );
            }

            byte[] buffer = new byte[1024 * 1024];
            int n;

            while ((n = in.read(buffer)) > 0) {
                out.write(buffer, 0, n);
            }

            out.getFD().sync();
        }

        String hash = sha256(temp);

        if (!EXPECTED_SHA256.equalsIgnoreCase(hash)) {
            temp.delete();
            throw new Exception(
                "Selected model failed SHA-256 verification."
            );
        }

        if (target.exists() && !target.delete()) {
            temp.delete();
            throw new Exception(
                "Unable to replace existing model."
            );
        }

        if (!temp.renameTo(target)) {
            temp.delete();
            throw new Exception(
                "Unable to activate imported model."
            );
        }
    }

    private static String sha256(File file)
        throws Exception {

        MessageDigest digest =
            MessageDigest.getInstance("SHA-256");

        try (InputStream in =
                 new java.io.FileInputStream(file)) {

            byte[] buffer = new byte[1024 * 1024];
            int n;

            while ((n = in.read(buffer)) > 0) {
                digest.update(buffer, 0, n);
            }
        }

        StringBuilder out = new StringBuilder();

        for (byte b : digest.digest()) {
            out.append(
                String.format("%02x", b & 0xff)
            );
        }

        return out.toString();
    }
}
