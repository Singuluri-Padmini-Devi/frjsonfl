from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # For consistent results
import pytesseract
from PIL import Image
import os
import io
import csv
import json

app = Flask(__name__, template_folder=r"C:\Users\DELL\Downloads\frjsonfl")

# Configuration
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'jfif', 'webp', 'bmp'}  # Added 'jfif' and other common formats
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Open the image file
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        # Generate JSON and CSV output
        json_output = json.dumps({'text': text}, indent=4)
        csv_output = 'text\n' + text.replace('\n', '\n')

        return jsonify({
            'text': text,
            'json': json_output,
            'csv': csv_output
        })
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)
