# modules/audio_processing.py
"""
OPTIMIZED Audio processing with FREE transcription options
- Google Speech Recognition (FREE, no API key needed)
- OpenAI Whisper (requires API key)
- Manual transcript fallback
"""

import os
import tempfile
from pydub import AudioSegment
import subprocess
from functools import lru_cache

# Try both import methods for MoviePy
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy.video.io.VideoFileClip import VideoFileClip

# Import speech recognition library
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("speech_recognition not available. Install with: pip install SpeechRecognition")

# OpenAI support
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    NEW_OPENAI_API = True
except ImportError:
    try:
        import openai
        OPENAI_AVAILABLE = True
        NEW_OPENAI_API = False
    except ImportError:
        OPENAI_AVAILABLE = False
        NEW_OPENAI_API = False


def extract_audio_from_video(video_path, output_audio_path=None, fast_mode=True):
    """
    Extract audio from video file
    Optimized for faster processing
    """
    if output_audio_path is None:
        output_audio_path = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=".wav"
        ).name
    
    sample_rate = 16000 if fast_mode else 44100
    
    try:
        video = VideoFileClip(video_path)
        
        if video.audio is None:
            video.close()
            raise RuntimeError("Video file contains no audio track!")
        
        video.audio.write_audiofile(
            output_audio_path,
            codec='pcm_s16le',
            fps=sample_rate,
            nbytes=2,
            bitrate='32k' if fast_mode else '128k',
            logger=None
        )
        video.close()
        
        print(f"Audio extracted successfully to: {output_audio_path}")
        return output_audio_path
        
    except Exception as e:
        print(f"MoviePy extraction failed: {e}")
        
        try:
            print("Trying ffmpeg fallback...")
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', str(sample_rate),
                '-ac', '1' if fast_mode else '2',
                '-threads', '0',
                output_audio_path,
                '-y'
            ]
            
            subprocess.run(
                cmd, 
                check=True, 
                capture_output=True, 
                text=True,
                timeout=120
            )
            
            print(f"FFmpeg extraction successful: {output_audio_path}")
            return output_audio_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Audio extraction timed out (>2 minutes).")
        except subprocess.CalledProcessError as e2:
            raise RuntimeError(f"Audio extraction failed: {e2.stderr}")
        except FileNotFoundError:
            raise RuntimeError(f"FFmpeg not found. Please install FFmpeg.")


def transcribe_with_google_free(audio_path, chunk_duration=30):
    """
    FREE transcription using Google Speech Recognition API
    No API key needed! Works out of the box.
    
    Args:
        audio_path: Path to audio file (WAV format)
        chunk_duration: Process audio in chunks (seconds)
        
    Returns:
        Transcribed text as string
    """
    if not SR_AVAILABLE:
        raise RuntimeError(
            "speech_recognition library not installed.\n"
            "Install with: pip install SpeechRecognition"
        )
    
    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_path)
        
        # Convert to mono and 16kHz (required for speech recognition)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        
        # Export as WAV
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio.export(temp_wav.name, format="wav")
        temp_wav.close()
        
        recognizer = sr.Recognizer()
        
        # Load audio file
        with sr.AudioFile(temp_wav.name) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Calculate chunks
            duration = len(audio) / 1000.0  # Duration in seconds
            chunks = []
            
            print(f"Transcribing audio ({duration:.1f}s) in chunks...")
            
            # Process in chunks to avoid timeout
            for i in range(0, int(duration), chunk_duration):
                try:
                    # Record chunk
                    audio_chunk = recognizer.record(source, duration=min(chunk_duration, duration - i))
                    
                    # Recognize using Google (FREE)
                    text = recognizer.recognize_google(audio_chunk)
                    chunks.append(text)
                    print(f"Chunk {len(chunks)}: {len(text)} characters")
                    
                except sr.UnknownValueError:
                    print(f"Chunk {len(chunks)+1}: Could not understand audio")
                    chunks.append("")
                except sr.RequestError as e:
                    print(f"Chunk {len(chunks)+1}: API error: {e}")
                    chunks.append("")
        
        # Cleanup
        try:
            os.unlink(temp_wav.name)
        except:
            pass
        
        # Combine all chunks
        full_transcript = " ".join(chunks).strip()
        
        if not full_transcript:
            raise RuntimeError("Could not transcribe any audio. Audio may be unclear or too quiet.")
        
        print(f"Transcription complete: {len(full_transcript)} characters")
        return full_transcript
        
    except Exception as e:
        raise RuntimeError(f"Free transcription failed: {e}")


def transcribe_with_openai_whisper(filepath, openai_api_key=None, timeout=60):
    """
    Transcribe audio using OpenAI Whisper API (requires paid API key)
    """
    if not OPENAI_AVAILABLE:
        raise RuntimeError(
            "OpenAI library not installed. Install with: pip install openai"
        )
    
    api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise RuntimeError(
            "No OpenAI API key provided. Set OPENAI_API_KEY environment "
            "variable or pass openai_api_key parameter."
        )
    
    try:
        with open(filepath, "rb") as audio_file:
            if NEW_OPENAI_API:
                client = OpenAI(api_key=api_key, timeout=timeout)
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
                return response.text
            else:
                import openai
                openai.api_key = api_key
                openai.request_timeout = timeout
                response = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
                return response["text"]
            
    except Exception as e:
        raise RuntimeError(f"Whisper transcription failed: {e}")


def transcribe_audio(audio_path, method="google_free", api_key=None):
    """
    Universal transcription function supporting multiple methods
    
    Args:
        audio_path: Path to audio file
        method: "google_free" (default, no API key) or "openai_whisper" (paid)
        api_key: OpenAI API key (only needed for whisper)
        
    Returns:
        Transcribed text
    """
    if method == "google_free":
        return transcribe_with_google_free(audio_path)
    elif method == "openai_whisper":
        return transcribe_with_openai_whisper(audio_path, api_key)
    else:
        raise ValueError(f"Unknown transcription method: {method}")


@lru_cache(maxsize=10)
def get_audio_duration_seconds(filepath):
    """Get duration of audio file in seconds"""
    try:
        audio = AudioSegment.from_file(filepath)
        return audio.duration_seconds
    except Exception as e:
        raise RuntimeError(f"Failed to get audio duration: {e}")


def simple_speech_metrics(transcript_text, duration_seconds):
    """
    Compute simple speech metrics from transcript and duration
    """
    words = transcript_text.split()
    word_count = len(words)
    
    if duration_seconds <= 0:
        words_per_second = 0.0
        pause_ratio = 1.0
    else:
        words_per_second = word_count / duration_seconds
        
        IDEAL_WPS = 3.5
        
        if words_per_second == 0:
            pause_ratio = 1.0
        else:
            estimated_speaking_time = word_count / IDEAL_WPS
            pause_ratio = max(
                0.0, 
                1.0 - min(1.0, estimated_speaking_time / duration_seconds)
            )
    
    return {
        "word_count": word_count,
        "words_per_second": round(words_per_second, 2),
        "pause_ratio": round(pause_ratio, 3),
        "duration_seconds": round(duration_seconds, 2)
    }


def analyze_audio_from_video(video_path, transcription_method="google_free", 
                            api_key=None, fast_mode=True):
    """
    Complete audio analysis pipeline
    
    Args:
        video_path: Path to video file
        transcription_method: "google_free" or "openai_whisper"
        api_key: OpenAI API key (if using whisper)
        fast_mode: Use optimized settings
        
    Returns:
        Dictionary with transcript and metrics
    """
    audio_path = extract_audio_from_video(video_path, fast_mode=fast_mode)
    
    try:
        duration = get_audio_duration_seconds(audio_path)
        
        # Transcribe using selected method
        if transcription_method != "manual":
            transcript = transcribe_audio(audio_path, transcription_method, api_key)
        else:
            transcript = None
        
        # Compute metrics
        if transcript:
            metrics = simple_speech_metrics(transcript, duration)
        else:
            metrics = {
                "word_count": 0,
                "words_per_second": 0.0,
                "pause_ratio": 1.0,
                "duration_seconds": round(duration, 2)
            }
        
        return {
            "transcript": transcript,
            "audio_metrics": metrics,
            "audio_path": audio_path,
            "success": True
        }
        
    except Exception as e:
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        raise e


# Example usage
if __name__ == "__main__":
    video_file = "test_interview.mp4"
    
    if os.path.exists(video_file):
        print("Testing FREE transcription...")
        
        # Extract audio
        audio_path = extract_audio_from_video(video_file, fast_mode=True)
        
        # Test free transcription
        try:
            transcript = transcribe_with_google_free(audio_path)
            print(f"Transcript: {transcript}")
            
            duration = get_audio_duration_seconds(audio_path)
            metrics = simple_speech_metrics(transcript, duration)
            print(f"Metrics: {metrics}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Cleanup
        os.unlink(audio_path)
    else:
        print(f"Test video not found: {video_file}")