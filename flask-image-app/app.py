from flask import Flask, render_template, request, redirect, url_for
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2
import os

app = Flask(__name__)

# Gunakan path absolut
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder uploads ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        # Simpan file asli
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Proses gambar
        img = Image.open(filepath)
        filenames = improve_image_quality(img, file.filename)

        return render_template('index.html',
                               original_filename='uploads/' + file.filename,
                               step_images=filenames)


def improve_image_quality(original_img, base_filename):
    steps = {}

    # Grayscale — tetap
    img = original_img.convert('L')
    steps['grayscale'] = img.copy()

    # Kontras — lebih ekstrim
    img = original_img.convert('L')
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(3.0)  # sebelumnya 1.5 → sekarang 3.0
    steps['contrast'] = img.copy()

    # Gaussian Blur — lebih kuat
    img = original_img.convert('L')
    img = cv2.cvtColor(np.array(img), cv2.COLOR_GRAY2BGR)
    img = cv2.GaussianBlur(img, (25, 25), 10)  # kernel lebih besar & sigma lebih tinggi
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    steps['blur'] = img.copy()

    # Crop — tetap
    img = original_img.convert('L')
    width, height = img.size
    crop_box = (
        (width - 200) // 2,
        (height - 300) // 2,
        (width + 200) // 2,
        (height + 300) // 2
    )
    img = img.crop(crop_box)
    steps['crop'] = img.copy()

    # Portrait — tetap
    img = original_img.convert('L')
    portrait_width = 150
    center_x = img.size[0] // 2
    portrait_box = (
        center_x - portrait_width // 2,
        0,
        center_x + portrait_width // 2,
        img.size[1]
    )
    img = img.crop(portrait_box)
    steps['portrait'] = img.copy()

    # Simpan hasil-hasilnya
    filenames = {}
    for step, image in steps.items():
        filename = f'{step}_{base_filename}'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        filenames[step] = 'uploads/' + filename

    return filenames





if __name__ == '__main__':
    print("Menjalankan Flask...")
    app.run(debug=True, port=8000)
