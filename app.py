from flask import Flask, render_template, request, send_file, jsonify, url_for
from werkzeug.utils import secure_filename
import tempfile
import os
import fx

app = Flask(__name__)

UPLOAD_FOLDER = '/uploads/'
ALLOWED_EXTENSIONS = {'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        audio_file = request.files['audio_file']
        input_text = request.form['input_text']

        # Save the uploaded file as a temporary file
        temp_dir = tempfile.mkdtemp()
        secure_filename_audio = secure_filename(audio_file.filename)
        temp_file_path = os.path.join(temp_dir, secure_filename_audio)
        audio_file.save(temp_file_path)

        # Process the audio file and input_text here
        processed_audio_path, processed_text = process_audio(temp_file_path, input_text)

        # Cleanup: Remove the temporary directory and its contents
        os.remove(temp_file_path)
        os.rmdir(temp_dir)

        # Generate a download URL for the processed audio file
        download_url = url_for('download_file', filename=processed_audio_path)

        return jsonify({"processed_text": processed_text, "download_url": download_url})

    return render_template('index.html')


"""
# Old Version of process_audio
def process_audio(input_file_path, input_text):
    iteration = fx.ranger.__next__()
    f_name = "current_output" + str(iteration) + ".wav"
    input_audio = fx.set_input(input_file_path)
    board = fx.board
    board = fx.modify_board(board, option = int(input_text))
    effected = fx.write_output(input_audio, f_name, board, samplerate= 44100)
    return f_name
"""


def process_audio(input_file_path, input_text):
    iteration = fx.ranger.__next__()
    f_name = "output.wav"
    input_audio = fx.set_input(input_file_path)
    p_board = fx.BoardGenerator(input_text)
    effected = fx.write_output(input_audio, f_name, p_board.board, samplerate= 44100)
    return f_name, p_board.gpt_response

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)