# My OCR Application Project

This project demonstrates an Optical Character Recognition (OCR) system. It consists of a core web application and an Android application that provides mobile access to the OCR functionality.

**Project Submitted By:** Gahan Makwana
**College/Course:** Sardar Vallabhbhai National Institute of Technology

## Components

### 1. OCR Web Application (Python/Gradio/PaddleOCR)

* **Description:** A web application built using Python with the Gradio framework for the user interface and PaddleOCR for the OCR engine. This application allows users to upload images and extract text.
* **Technology Stack:** Python, Gradio, PaddleOCR, Pillow, NumPy.
* **Deployment:** The web application is deployed on Hugging Face Spaces and can be accessed here: [https://huggingface.co/spaces/gahanmakwana/my-ocr-demo](https://huggingface.co/spaces/gahanmakwana/my-ocr-demo)
* **Source Code:** The source code for the web application (e.g., `app.py`, `requirements.txt`, bundled models in `paddleocr_models/`) is located in the root of this repository. The models are handled using Git LFS.

### 2. Android Application

* **Description:** An Android application that provides a mobile interface to the OCR system. This app uses a WebView component to load and display the deployed OCR web application, allowing users to interact with it seamlessly on their Android devices.
* **Technology Stack:** Android (Kotlin/Java), Android Studio, WebView.
* **Source Code:** The Android Studio project is located in the `MyOCRApplication/` folder (or whatever you named your Android project folder) within this repository.
* **Installable APK:** The installable Android application package (`.apk`) can be found [Link to your GitHub Release where APK is attached - OR - mention it will be submitted separately].

## How it Works

The Android application embeds the live web application hosted on Hugging Face Spaces. When an image is uploaded through the Android app, it is processed by the PaddleOCR engine running on the Hugging Face Space server, and the results are displayed back within the Android app's WebView.

## Video Demonstration

[Link to your video demonstration on GitHub or elsewhere, once you've made it]

## Setup (Optional - for developers)

### Web Application (Local)
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure PaddleOCR models are present in `paddleocr_models/` (or allow download).
4. Run: `python app.py`

### Android Application
1. Open the `MyOCRApplication/` folder (or your Android project folder name) in Android Studio.
2. Let Gradle sync the project.
3. Build and run on an emulator or a connected Android device.