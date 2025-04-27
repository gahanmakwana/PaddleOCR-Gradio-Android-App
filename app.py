# from flask import Flask, render_template, request, send_from_directory
# from paddleocr import PaddleOCR
# import os

# app = Flask(__name__)

# # Upload folder
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# # Initialize OCR
# ocr = PaddleOCR(use_angle_cls=True, lang='en')

# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     text = None
#     filename = None
#     if request.method == 'POST':
#         file = request.files.get('file')
#         if not file or file.filename == '':
#             return render_template('index.html', error="No file selected")

#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(filepath)

#         # Run OCR
#         result = ocr.ocr(filepath, cls=True)
#         extracted_text = ""
#         for line in result:
#             for word_info in line:
#                 extracted_text += word_info[1][0] + " "

#         text = extracted_text
#         filename = file.filename

#     return render_template('index.html', text=text, filename=filename)

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))  # <-- IMPORTANT
#     app.run(host='0.0.0.0', port=port)

from flask import Flask, render_template, request, send_from_directory
from paddleocr import PaddleOCR
import os
import time
import logging

app = Flask(__name__)

# Configure minimal logging
logging.basicConfig(level=logging.WARNING)

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Lightweight OCR initialization
def get_ocr():
    return PaddleOCR(
        lang='en',
        use_angle_cls=False,  # Disable angle classifier to save memory
        use_gpu=False,
        enable_mkldnn=True,  # CPU optimization
        rec_batch_num=1,     # Process one line at a time
        det_limit_side_len=480,  # Smaller image size
        thread_num=1         # Critical for free tier
    )

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return render_template('index.html', error="No file selected")

        try:
            # Verify file size (<500KB)
            file.seek(0, os.SEEK_END)
            if file.tell() > 500000:
                return render_template('index.html', error="File too large (max 500KB)")
            file.seek(0)

            # Save with timestamp
            filename = f"{int(time.time())}_{file.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Initialize OCR per-request (avoids memory buildup)
            ocr = get_ocr()
            
            # Fast OCR with small image
            result = ocr.ocr(filepath, cls=False)[0]  # [0] gets first batch
            text = ' '.join([word[1][0] for word in result if len(word) >= 2])

            return render_template('index.html', text=text, filename=filename)

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return render_template('index.html', error=f"Error: {str(e)}")

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=False)