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
import os
import time

app = Flask(__name__)

# Configure minimal setup
UPLOAD_FOLDER = 'tmp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Lazy-load OCR only when needed
def get_ocr():
    from paddleocr import PaddleOCR
    return PaddleOCR(
        lang='en',
        use_angle_cls=False,
        use_gpu=False,
        det_model_dir='en_PP-OCRv3_det_infer',
        rec_model_dir='en_PP-OCRv3_rec_infer',
        cls_model_dir='ch_ppocr_mobile_v2.0_cls_infer',
        enable_mkldnn=True,
        rec_batch_num=1,
        det_limit_side_len=320,
        thread_num=1
    )

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return render_template('index.html', error="Please select a file")

        try:
            # 300KB file size limit
            if len(file.read()) > 300000:
                return render_template('index.html', error="Max 300KB file size")
            file.seek(0)

            # Save file
            filename = f"{int(time.time())}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Process with OCR
            ocr = get_ocr()
            result = ocr.ocr(filepath, cls=False)
            text = ' '.join([word[1][0] for line in result[0] for word in line if len(word) >= 2])

            # Cleanup
            os.remove(filepath)
            return render_template('index.html', text=text)

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return render_template('index.html', error="OCR processing failed")

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=False)