from flask import Flask, render_template, request
import os
import moviepy.editor as mp
import speech_recognition as sr

app = Flask(__name__)

class VideoTranscriber:
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'wmv', 'avi', 'mkv', 'mp3', 'wav', 'aac', 'flac', 'ogg'}

    def __init__(self, video_path):
        self.video_path = video_path
        self.audio_path = "extracted_audio.wav"  # Path to save extracted audio

    def allowed_file(self, filename):
        """Check if the file has a valid extension."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def extract_audio(self):
        """Extract audio from the video and save it as a WAV file."""
        video = mp.VideoFileClip(self.video_path)
        audio = video.audio
        audio.write_audiofile(self.audio_path, codec='pcm_s16le')
        video.close()

    def transcribe_audio(self):
        """Transcribe the extracted audio using Google's Speech Recognition API."""
        recognizer = sr.Recognizer()
        with sr.AudioFile(self.audio_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)

    def process_video(self):
        """Extract audio from video and transcribe the audio."""
        self.extract_audio()
        transcription = self.transcribe_audio()
        return transcription

    def cleanup(self):
        """Delete the audio file after transcription."""
        if os.path.exists(self.audio_path):
            os.remove(self.audio_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    transcription = None
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return "No file uploaded", 400

        file = request.files['file']

        if file.filename == '':
            return "No selected file", 400

        # Save the uploaded file
        file_path = os.path.join('uploads', file.filename)
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        file.save(file_path)

        # Transcribe the uploaded video
        try:
            transcriber = VideoTranscriber(file_path)
            transcription = transcriber.process_video()
        except Exception as e:
            transcription = f"Error occurred: {str(e)}"
        finally:
            transcriber.cleanup()
            if os.path.exists(file_path):
                os.remove(file_path)

    return render_template('index.html', transcription=transcription)

if __name__ == '__main__':
    app.run(debug=True)
