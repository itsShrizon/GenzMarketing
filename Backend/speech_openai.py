import os
import logging
import openai
from io import BytesIO
from pydub import AudioSegment
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# Check if OpenAI API key is available
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY is missing. Speech-to-text functionality will not work!")

# Set up OpenAI client
openai.api_key = OPENAI_API_KEY

# Set up audio directory
audio_dir = os.path.join(os.getcwd(), "audio_files")
os.makedirs(audio_dir, exist_ok=True)
audio_file_path = os.path.join(audio_dir, "user.wav")

def record_audio_from_file(audio_data_bytes):
    """Process audio data from uploaded file"""
    try:
        # Convert and save audio as WAV
        audio_segment = AudioSegment.from_file(BytesIO(audio_data_bytes))
        audio_segment = audio_segment.set_channels(1)
        audio_segment.export(audio_file_path, format="wav")
        file_size = os.path.getsize(audio_file_path)
        logging.info(f"Audio saved to {audio_file_path}, size: {file_size} bytes")
        return audio_file_path
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return None

def transcribe_audio_with_openai():
    """
    Transcribe audio using OpenAI's Whisper API
    """
    logging.info(f"Transcribing audio from: {audio_file_path}")
    
    if not OPENAI_API_KEY:
        logging.error("OpenAI API key is missing! Cannot transcribe audio.")
        return "Error: OpenAI API key is missing!"
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            # Call OpenAI's Whisper API
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
            transcript = response.text
            logging.info(f"Transcription successful: {transcript}")
            return transcript
            
    except Exception as e:
        logging.error(f"Error transcribing audio: {str(e)}")
        return "Transcription failed."
