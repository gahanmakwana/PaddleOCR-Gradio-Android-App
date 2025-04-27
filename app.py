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

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize OCR with error handling and optimized settings
try:
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang='en',
        use_gpu=False,  # Disable GPU on Render
        rec_model_dir='paddle_models/rec',  # Cache models
        det_model_dir='paddle_models/det',
        cls_model_dir='paddle_models/cls',
        enable_mkldnn=True,  # CPU optimization
        thread_num=2  # Limit threads to prevent OOM
    )
except Exception as e:
    print(f"OCR initialization failed: {str(e)}")
    ocr = None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    text = None
    filename = None
    error = None
    
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return render_template('index.html', error="No file selected")

        try:
            # Save file with timestamp to prevent overwrites
            timestamp = str(int(time.time()))
            safe_filename = f"{timestamp}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            file.save(filepath)

            # Check OCR initialization
            if not ocr:
                raise Exception("OCR engine not available")

            # Run OCR with timeout safeguard
            start_time = time.time()
            result = ocr.ocr(filepath, cls=True)
            
            # Process results
            extracted_text = ""
            if result and len(result) > 0:
                for line in result[0]:  # Note: result[0] contains the actual OCR data
                    if line and len(line) >= 2:  # Check if line has text information
                        extracted_text += line[1][0] + " "

            text = extracted_text.strip()
            filename = safe_filename

        except Exception as e:
            error = f"Error processing file: {str(e)}"
            print(error)

    return render_template('index.html', text=text, filename=filename, error=error)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)