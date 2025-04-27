import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from paddleocr import PaddleOCR

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize PaddleOCR (CPU mode)
ocr = PaddleOCR(use_angle_cls=True, lang='en')

@app.route('/', methods=['GET', 'POST'])
def index():
    filename = None
    extracted_text = None
    error = None

    if request.method == 'POST':
        file = request.files.get('image')
        if not file or file.filename == '' or not allowed_file(file.filename):
            error = "Please upload a valid image file (png/jpg/jpeg/gif)."
        else:
            # Save the uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Run OCR on the saved image
            result = ocr.ocr(filepath, cls=True)
            # Flatten nested results if needed
            if isinstance(result, list) and len(result) == 1 and isinstance(result[0], list):
                result = result[0]
            # Extract text lines
            lines = [line[1][0] for line in result]
            extracted_text = "\n".join(lines) if lines else "No text detected."

    return render_template('index.html', filename=filename,
                           extracted_text=extracted_text, error=error)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Use the PORT environment variable if provided by Render, else 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
