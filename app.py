from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
from paddleocr import PaddleOCR
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allow only certain image file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize PaddleOCR once (loads models)
ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = ''
    filename = None

    if request.method == 'POST':
        # Check if an image file was submitted
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file and allowed_file(file.filename):
            # Secure the filename and save to upload folder
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Run OCR on the uploaded image
            result = ocr_engine.ocr(filepath, cls=True)
            # Un-nest result if PaddleOCR returns a nested list
            if result and isinstance(result[0], list) and len(result) == 1:
                result = result[0]
            # Extract recognized text lines
            extracted_text_lines = [line[1][0] for line in result]
            extracted_text = '\n'.join(extracted_text_lines)

    # Render the template, passing in filename and extracted text
    return render_template('index.html', filename=filename, extracted_text=extracted_text)

if __name__ == '__main__':
    # Bind to PORT for Render (default 10000) on all interfaces
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
