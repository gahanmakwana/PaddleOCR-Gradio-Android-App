package com.example.myocrapplication // This matches your existing package name

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private var filePathCallback: ValueCallback<Array<Uri>>? = null
    private lateinit var fileChooserLauncher: ActivityResultLauncher<Intent>

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)

        // --- Configure WebView settings ---
        val webSettings: WebSettings = webView.settings
        webSettings.javaScriptEnabled = true
        webSettings.domStorageEnabled = true
        webSettings.loadWithOverviewMode = true
        webSettings.useWideViewPort = true
        webSettings.allowFileAccess = true // Allow file access within WebView
        webSettings.allowContentAccess = true // Allow content access within WebView

        webSettings.builtInZoomControls = false
        webSettings.displayZoomControls = false
        webSettings.setSupportZoom(false)

        // --- Set WebViewClient ---
        webView.webViewClient = object : WebViewClient() {
            @Deprecated("Deprecated in Java. This override is for older Android versions.")
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                if (url != null) {
                    view?.loadUrl(url)
                }
                return true
            }
        }

        // --- Setup File Chooser Launcher (Modern way to handle Activity Results) ---
        fileChooserLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (result.resultCode == Activity.RESULT_OK) {
                val uris = result.data?.let { intent ->
                    WebChromeClient.FileChooserParams.parseResult(result.resultCode, intent)
                }
                filePathCallback?.onReceiveValue(uris ?: arrayOf())
            } else {
                filePathCallback?.onReceiveValue(null)
            }
            filePathCallback = null
        }

        // --- Set WebChromeClient for file chooser ---
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                this@MainActivity.filePathCallback = filePathCallback
                val intent = fileChooserParams?.createIntent()
                try {
                    // Try to launch the intent using the modern ActivityResultLauncher
                    if (intent != null) {
                        fileChooserLauncher.launch(intent)
                    } else {
                        // Fallback or error handling if intent is null
                        this@MainActivity.filePathCallback?.onReceiveValue(null)
                        this@MainActivity.filePathCallback = null
                        return false
                    }
                } catch (e: Exception) {
                    // Handle exception, e.g., if no activity can handle the intent
                    this@MainActivity.filePathCallback?.onReceiveValue(null)
                    this@MainActivity.filePathCallback = null
                    return false
                }
                return true // Indicate that we've handled the file chooser
            }
        }

        // --- Load your Hugging Face Space URL ---
        val huggingFaceSpaceUrl = "https://huggingface.co/spaces/gahanmakwana/my-ocr-demo"
        webView.loadUrl(huggingFaceSpaceUrl)
    }

    @Deprecated("Deprecated in Java.")
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
