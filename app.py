import os
from flask import Flask, render_template, request, send_from_directory
from paddleocr import PaddleOCR

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ocr = PaddleOCR(use_angle_cls=True, lang='en')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    text = None
    filename = None
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(img_path)

            # Run OCR
            result = ocr.ocr(img_path, cls=True)
            extracted_text = ""
            for line in result:
                for word_info in line:
                    extracted_text += word_info[1][0] + " "

            text = extracted_text

    return render_template('index.html', text=text, filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Corrected indentation here
    # Run the app, binding to all IP addresses and the correct port
    app.run(host="0.0.0.0", port=port)
