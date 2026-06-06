# modules/video_analysis.py
import cv2
from deepface import DeepFace
import tempfile
import os
import numpy as np

def analyze_video_emotions(video_file, sample_every_n_frames=30, max_frames=40):
    """
    Analyzes video by sampling frames.
    Returns:
      - face_present_ratio: fraction of sampled frames where a face is detected
      - dominant_emotion_counts: dict of emotion -> count
      - emotion_confidence_score: normalized score 0..1 where higher means more 'positive/confident'
    """
    # write upload to temp file if needed
    if hasattr(video_file, "read"):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.write(video_file.read())
        tmp.close()
        path = tmp.name
    else:
        path = video_file

    cap = cv2.VideoCapture(path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    sampled = 0
    face_detected = 0
    emotion_counts = {}
    frames_processed = 0

    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % sample_every_n_frames == 0:
            frames_processed += 1
            try:
                # DeepFace analyze returns emotion dict
                analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                # analysis may be dict or list
                if isinstance(analysis, list):
                    analysis = analysis[0]
                if analysis and analysis.get("emotion"):
                    face_detected += 1
                    dom = analysis["dominant_emotion"]
                    emotion_counts[dom] = emotion_counts.get(dom, 0) + 1
            except Exception as e:
                # treat exceptions as no face detected for this frame
                pass
            sampled += 1
        idx += 1
        if sampled >= max_frames:
            break

    cap.release()
    if sampled == 0:
        face_present_ratio = 0.0
    else:
        face_present_ratio = face_detected / sampled

    # Compute emotion confidence: reward 'neutral' and 'happy' as confident/positive
    positive_emotions = ["happy", "neutral", "surprise"]  # surprise can be positive-ish
    total_emotion_hits = sum(emotion_counts.values()) or 1
    positive_hits = sum(c for e,c in emotion_counts.items() if e in positive_emotions)
    emotion_confidence_score = positive_hits / total_emotion_hits

    # cleanup temp file
    if hasattr(video_file, "read"):
        try:
            os.remove(path)
        except:
            pass

    return {
        "sampled_frames": sampled,
        "face_present_ratio": face_present_ratio,
        "emotion_counts": emotion_counts,
        "emotion_confidence_score": emotion_confidence_score
    }
