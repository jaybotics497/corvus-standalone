#include <jni.h>
#include <llama.h>

#include <algorithm>
#include <mutex>
#include <string>
#include <vector>

static std::mutex g_mutex;

static std::string token_piece(
    const llama_vocab * vocab,
    llama_token token
) {
    std::vector<char> buf(256);

    int n = llama_token_to_piece(
        vocab,
        token,
        buf.data(),
        (int) buf.size(),
        0,
        true
    );

    if (n < 0) {
        buf.resize(-n);

        n = llama_token_to_piece(
            vocab,
            token,
            buf.data(),
            (int) buf.size(),
            0,
            true
        );
    }

    if (n <= 0) {
        return {};
    }

    return std::string(
        buf.data(),
        (size_t) n
    );
}

static std::string run_inference(
    const std::string & model_path,
    const std::string & user_prompt
) {
    llama_backend_init();

    llama_model_params mp =
        llama_model_default_params();

    // CPU-only. The phone has limited physical RAM.
    mp.n_gpu_layers = 0;

    llama_model * model =
        llama_model_load_from_file(
            model_path.c_str(),
            mp
        );

    if (!model) {
        return "ERROR: unable to load local model.";
    }

    const llama_vocab * vocab =
        llama_model_get_vocab(model);

    llama_context_params cp =
        llama_context_default_params();

    cp.n_ctx = 2048;
    cp.n_batch = 512;
    cp.no_perf = true;

    llama_context * ctx =
        llama_init_from_model(
            model,
            cp
        );

    if (!ctx) {
        llama_model_free(model);
        return "ERROR: unable to create model context.";
    }

    const char * tmpl =
        llama_model_chat_template(
            model,
            nullptr
        );

    llama_chat_message messages[1] = {
        {
            "user",
            user_prompt.c_str()
        }
    };

    int formatted_size =
        llama_chat_apply_template(
            tmpl,
            messages,
            1,
            true,
            nullptr,
            0
        );

    if (formatted_size <= 0) {
        llama_free(ctx);
        llama_model_free(model);
        return "ERROR: chat template failed.";
    }

    std::vector<char> formatted(
        (size_t) formatted_size + 1
    );

    formatted_size =
        llama_chat_apply_template(
            tmpl,
            messages,
            1,
            true,
            formatted.data(),
            formatted.size()
        );

    if (formatted_size <= 0) {
        llama_free(ctx);
        llama_model_free(model);
        return "ERROR: chat formatting failed.";
    }

    std::string prompt(
        formatted.data(),
        (size_t) formatted_size
    );

    int n_tokens =
        -llama_tokenize(
            vocab,
            prompt.c_str(),
            prompt.size(),
            nullptr,
            0,
            true,
            true
        );

    if (n_tokens <= 0 ||
        n_tokens > 1536) {

        llama_free(ctx);
        llama_model_free(model);

        return "ERROR: prompt is too large.";
    }

    std::vector<llama_token> tokens(
        (size_t) n_tokens
    );

    int tokenized =
        llama_tokenize(
            vocab,
            prompt.c_str(),
            prompt.size(),
            tokens.data(),
            tokens.size(),
            true,
            true
        );

    if (tokenized < 0) {
        llama_free(ctx);
        llama_model_free(model);
        return "ERROR: tokenization failed.";
    }

    llama_batch batch =
        llama_batch_get_one(
            tokens.data(),
            tokenized
        );

    if (llama_decode(ctx, batch) != 0) {
        llama_free(ctx);
        llama_model_free(model);
        return "ERROR: prompt decode failed.";
    }

    llama_sampler * sampler =
        llama_sampler_chain_init(
            llama_sampler_chain_default_params()
        );

    llama_sampler_chain_add(
        sampler,
        llama_sampler_init_min_p(
            0.05f,
            1
        )
    );

    llama_sampler_chain_add(
        sampler,
        llama_sampler_init_temp(
            0.7f
        )
    );

    llama_sampler_chain_add(
        sampler,
        llama_sampler_init_dist(
            LLAMA_DEFAULT_SEED
        )
    );

    std::string response;

    const int max_output = 384;

    for (int i = 0; i < max_output; ++i) {

        llama_token token =
            llama_sampler_sample(
                sampler,
                ctx,
                -1
            );

        if (llama_vocab_is_eog(
                vocab,
                token
            )) {
            break;
        }

        response += token_piece(
            vocab,
            token
        );

        batch =
            llama_batch_get_one(
                &token,
                1
            );

        if (llama_decode(
                ctx,
                batch
            ) != 0) {
            break;
        }
    }

    llama_sampler_free(sampler);
    llama_free(ctx);
    llama_model_free(model);

    return response;
}

extern "C"
JNIEXPORT jstring JNICALL
Java_com_corvus_app_CorvusEngineService_nativeAsk(
    JNIEnv * env,
    jclass,
    jstring model_path,
    jstring prompt
) {
    std::lock_guard<std::mutex> lock(
        g_mutex
    );

    if (!model_path || !prompt) {
        return env->NewStringUTF(
            "ERROR: invalid native request."
        );
    }

    const char * mp =
        env->GetStringUTFChars(
            model_path,
            nullptr
        );

    const char * pp =
        env->GetStringUTFChars(
            prompt,
            nullptr
        );

    std::string result;

    try {
        result =
            run_inference(mp, pp);
    } catch (...) {
        result =
            "ERROR: native inference failure.";
    }

    env->ReleaseStringUTFChars(
        model_path,
        mp
    );

    env->ReleaseStringUTFChars(
        prompt,
        pp
    );

    return env->NewStringUTF(
        result.c_str()
    );
}
