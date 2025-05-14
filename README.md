---
title: My OCR Demo
emoji: 📸
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "4.20.0" # Check your requirements.txt for the exact Gradio version you are using
app_file: app.py
pinned: false
# Add this line if your paddleocr_models directory is large and you want to ensure LFS is used for it.
# It's good practice even if individual files inside are already LFS tracked.
# You might need to adjust if your models are not LFS tracked at the folder level.
# For now, since individual model files are LFS tracked, this might not be strictly necessary
# but can be a good general practice for model directories.
# hf_storage_lfs:
#  - "paddleocr_models/**"
---

# My PaddleOCR Demo Application

This is a web application that uses PaddleOCR to perform Optical Character Recognition (OCR) on uploaded images.
It's built with Gradio and deployed on Hugging Face Spaces.

The application uses bundled PaddleOCR models for English, managed with Git LFS to ensure fast startup and avoid re-downloads.

## How to Use
1. Upload an image using the interface.
2. The extracted text and the image with bounding boxes will be displayed.