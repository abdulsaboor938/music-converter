from flask import Flask, render_template, request, send_file
import os
from midi2audio import FluidSynth
from pydub import AudioSegment
import uuid

app = Flask(__name__)

def midi_to_audio(midi_file, output_file, soundfont_path=None):
    # Default soundfont path
    if soundfont_path is None:
        soundfont_path = '/usr/share/sounds/sf2/FluidR3_GM.sf2'  # Adjust this path as needed

    # Check if the soundfont file exists
    if not os.path.exists(soundfont_path):
        raise FileNotFoundError(f"Soundfont file not found: {soundfont_path}")

    # Create a FluidSynth instance
    fs = FluidSynth(sound_font=soundfont_path)

    # Convert MIDI to WAV
    temp_wav = 'temp_output.wav'
    fs.midi_to_audio(midi_file, temp_wav)

    # Load the WAV file
    audio = AudioSegment.from_wav(temp_wav)

    # Export to the desired format
    output_format = output_file.split('.')[-1].lower()
    if output_format in ['mp3', 'wav']:
        audio.export(output_file, format=output_format)
    else:
        raise ValueError("Unsupported output format. Use 'mp3' or 'wav'.")

    # Remove the temporary WAV file
    os.remove(temp_wav)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded MIDI file and the selected format
        midi_file = request.files['midi_file']
        output_format = request.form['format']

        # Save the uploaded MIDI file
        original_filename = os.path.splitext(midi_file.filename)[0]
        midi_filename = f"{uuid.uuid4()}.mid"
        midi_file.save(midi_filename)

        # Set the output filename
        output_filename = f"{original_filename}.{output_format}"

        # Convert the MIDI file to the selected format
        try:
            midi_to_audio(midi_filename, output_filename)
        except Exception as e:
            return str(e)

        # Send the converted file to the user
        return send_file(output_filename, as_attachment=True, download_name=output_filename)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
