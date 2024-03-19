from flask import Flask, render_template, request, jsonify, send_from_directory
import cv2 
import os  

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CARTOON_FOLDER'] = 'static'

def cartoonify_image(image_path):
    # Read the original image
    original_image = cv2.imread(image_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    # Check if the image is valid
    if original_image is None:
        print("Can't find any image. Choose appropriate file")
        return None

    # Convert the image to grayscale
    grayscale_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    # Apply median blur to smoothen the grayscale image
    smooth_grayscale_image = cv2.medianBlur(grayscale_image, 5)

    # Retrieve the edges for cartoon effect by using thresholding technique
    get_edge = cv2.adaptiveThreshold(smooth_grayscale_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

    # Apply bilateral filter to remove noise and keep edge sharp
    color_image = cv2.bilateralFilter(original_image, 9, 300, 300)

    # Mask the edged image with the color image
    cartoon_image = cv2.bitwise_and(color_image, color_image, mask=get_edge)

    # Save the cartoonified image with a modified filename
    cartoon_image_path = save_cartoonified_image(cartoon_image, image_path)

    return cartoon_image_path

def save_cartoonified_image(cartoon_image, image_path):
    filename = os.path.basename(image_path)
    cartoon_filename = f"cartoon_{filename}"  # Modify the filename as desired
    save_path = os.path.join(app.config['CARTOON_FOLDER'], cartoon_filename)
    cv2.imwrite(save_path, cv2.cvtColor(cartoon_image, cv2.COLOR_RGB2BGR))
    return save_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename != '':
            # Save the uploaded file to the upload folder
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(image_path)
            # Cartoonify the uploaded image
            cartoon_image_path = cartoonify_image(image_path)
            if cartoon_image_path:
                return jsonify({'cartoon_image_path': cartoon_image_path})
            else:
                return jsonify({'error': 'Failed to cartoonify the image'})
    return jsonify({'error': 'No file uploaded'})

@app.route('/cartoon/<path:filename>')
def cartoon_image(filename):
    cartoon_image_path = os.path.join(app.config['CARTOON_FOLDER'], filename)
    return send_from_directory(app.config['CARTOON_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
