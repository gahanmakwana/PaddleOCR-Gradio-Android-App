from flask import Flask, render_template, request, send_from_directory
from paddleocr import PaddleOCR
import os

app = Flask(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Set the uploads folder in app config
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize the OCR model
ocr = PaddleOCR(lang='en')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file selected')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No file selected')

        if file:
            # Save the file to uploads directory
            img_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(img_path)
            
            # Perform OCR
            result = ocr.ocr(img_path)
            
            # Extract text from OCR result
            text = ""
            for line in result[0]:
                text += line[1][0] + "\n"
            
            # Return the rendered template with the extracted text and image
            return render_template('index.html', text=text, filename=file.filename)
    
    return render_template('index.html')

# Serve the uploaded file (from the uploads directory)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
