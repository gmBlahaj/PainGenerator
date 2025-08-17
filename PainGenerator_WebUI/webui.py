from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import generator

app = Flask(__name__)


c_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app.config['RESULTS_FOLDER'] = os.path.join(c_path, 'results')
app.config['RESOURCES_FOLDER'] = os.path.join(c_path, 'resources')

@app.route('/', methods=['GET', 'POST'])
def index():
    image_path = None
    form_data = request.form.to_dict()

    if request.method == 'POST':
        try:
            values = {
                '-CHECKBOX-': 'is_user_generated' in request.form,
                '-WORD-': request.form.get('word'),
                '-HEX1-': request.form.get('hex1'),
                '-HEX2-': request.form.get('hex2'),
                '-SPIN-': request.form.get('spin'),
                '-FOLDER-': app.config['RESULTS_FOLDER'],
                '-WORDLIST-': request.form.get('wordlist'),
                '-SIZE-': request.form.get('size')
            }

            times_to_run = 1
            if not values['-CHECKBOX-']:
                 try:
                    times_to_run = int(values['-SPIN-'])
                    if not 1 <= times_to_run <= 100:
                        raise ValueError("Number of images must be between 1 and 100.")
                 except (ValueError, TypeError):
                    raise ValueError("Invalid number of images.")

            
            for _ in range(times_to_run):
                saved_image_path = generator.generate_image(values)

            
            relative_image_path = os.path.relpath(saved_image_path, c_path)
            image_path = url_for('serve_results', filename=os.path.basename(relative_image_path))

        except ValueError as e:
            
            print(f"Error: {e}")
            
            return redirect(url_for('index'))

    
    colors = [
        
        '#000000', '#1b4418', '#5e5441', '#416e38', '#8a755d', '#659d4a',
        '#c0ad8b', '#81c75f', '#f2e4b9', '#b1e783', '#ffffff', '#d6f89f',
        
        '#333333', '#4F4F4F', '#828282', '#BDBDBD', '#E0E0E0', '#F2F2F2',
        '#564D4D', '#6A5F5F', '#7F7272', '#948585', '#A99898', '#BEACAC',
        
        '#58181F', '#8C1C27', '#B82735', '#E5394A', '#FF576B', '#FF8A9A',
        '#4A251D', '#7B4032', '#A55A48', '#D27C65', '#FFAD8F', '#FFE4D6',
        
        '#A1B43B', '#CADB50', '#EFFF6B', '#FFFF9E', '#FFFFD1', '#F0F5BE',
        '#5E6E25', '#7D9033', '#A0B842', '#C7E351', '#EFFF6B', '#F8FFB0',
        
        '#0D1B2A', '#1B263B', '#415A77', '#778DA9', '#A9BCD0', '#E0E1DD',
        '#003049', '#00507A', '#0077B6', '#0096C7', '#48CAE4', '#90E0EF',
        
        '#FF00FF', '#FF00BF', '#FF0080', '#FF0040', '#FF4000', '#FF8000',
        '#FFBF00', '#FFFF00', '#BFFF00', '#80FF00', '#40FF00', '#00FF00',
        '#00FF40', '#00FF80', '#00FFBF', '#00FFFF', '#00BFFF', '#0080FF',
        '#0040FF', '#0000FF', '#4000FF', '#8000FF', '#BF00FF', '#FF00FF',
    ]
    return render_template('index.html', image_path=image_path, form_data=form_data, colors=colors)

@app.route('/results/<filename>')
def serve_results(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)


@app.route('/static/<filename>')
def serve_static_from_resources(filename):
    if filename in ['PAIN.ico', 'PAIN.png']:
        return send_from_directory(app.config['RESOURCES_FOLDER'], filename)
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), filename)


if __name__ == '__main__':
    if not os.path.exists(app.config['RESULTS_FOLDER']):
        os.makedirs(app.config['RESULTS_FOLDER'])
    app.run(debug=False)
