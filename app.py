from flask import Flask, render_template, request
import os
import pyclamd
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if not allowed_file(file.filename):
        return "File type not allowed!"

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Connect to ClamAV
    cd = pyclamd.ClamdNetworkSocket(host='clamav', port=3310)

    try:
        scan_result = cd.scan_file(f"/app/uploads/{filename}")
        print("SCAN RESULT:", scan_result)
    except Exception as e:
        return f"ClamAV connection error: {e}"

    # If malware detected
    if scan_result:
        os.remove(file_path)
        return "Malware detected! File blocked."

    return f"File '{filename}' uploaded and scanned successfully!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # nosec B104