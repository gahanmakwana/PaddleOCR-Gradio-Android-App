from flask import Flask, render_template, request, redirect, flash, url_for
import os
from werkzeug.utils import secure_filename
from paddleocr import PaddleOCR
from PIL import Image
import gc

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this')  # Replace in production
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize PaddleOCR once at the start (use CPU mode)
ocr = PaddleOCR(
    use_angle_cls=False,
    use_gpu=False,
    lang='en',
    det_model_dir='/tmp/ocr_models/det',
    rec_model_dir='/tmp/ocr_models/rec',
    cls_model_dir='/tmp/ocr_models/cls'
)

# Resize image before processing to reduce memory usage
def resize_image(image_path):
    with Image.open(image_path) as img:
        img.thumbnail((1024, 1024))  # Resize to max dimension of 1024x1024
        img.save(image_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = None
    image_file = None

    if request.method == 'POST':
        # Check file in request
        if 'image' not in request.files:
            flash('No file part in the request.')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No image selected.')
            return redirect(request.url)

        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Resize the image to optimize memory usage
        resize_image(file_path)

        # Run PaddleOCR on the resized image (CPU mode)
        result = ocr.ocr(file_path, cls=False)
        # Collect recognized text lines
        lines = []
        for res_line in result:
            for box, (txt, prob) in res_line:
                lines.append(txt)
        extracted_text = "\n".join(lines)
        image_file = filename

        # Clear memory after processing
        del result
        gc.collect()

    return render_template('index.html', extracted_text=extracted_text, image_file=image_file)

if __name__ == '__main__':
    app.run(debug=True)
