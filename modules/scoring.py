# modules/scoring.py

def aggregate_scores(nlp_keyword_score, clarity_score, audio_metrics, video_metrics):
    """
    Combine different metrics into a final score 0..100 using weighted sum.
    Weights can be tuned.
    """
    # Example weights
    W = {
        "content": 0.45,   # keyword relevance
        "clarity": 0.15,   # clarity
        "audio_conf": 0.20,# audio-based confidence (we use pause_ratio and words_per_second)
        "video_conf": 0.20 # video-based confidence (face & emotion)
    }

    # content score (0..1)
    content = nlp_keyword_score

    # clarity already 0..1
    clarity = clarity_score

    # audio confidence: combine speaking rate & pause ratio
    # words_per_second typical speaking 2.5 - 4.5 w/s
    wps = audio_metrics.get("words_per_second", 0)
    # normalize wps to 0..1 roughly between 1 and 5
    audio_rate_score = max(0.0, min(1.0, (wps - 1.0) / (5.0 - 1.0)))
    pause_ratio = audio_metrics.get("pause_ratio", 1.0)  # 0..1 where 1 means lots of pause (bad)
    audio_conf = 0.7 * audio_rate_score + 0.3 * (1 - pause_ratio)

    # video confidence from video_metrics
    face_ratio = video_metrics.get("face_present_ratio", 0.0)
    emotion_conf = video_metrics.get("emotion_confidence_score", 0.5)
    # combine
    video_conf = 0.6 * face_ratio + 0.4 * emotion_conf

    # weighted sum
    final_norm = (W["content"] * content +
                  W["clarity"] * clarity +
                  W["audio_conf"] * audio_conf +
                  W["video_conf"] * video_conf)

    final_score = round(final_norm * 100, 2)
    breakdown = {
        "content": round(content * 100, 2),
        "clarity": round(clarity * 100, 2),
        "audio_confidence": round(audio_conf * 100, 2),
        "video_confidence": round(video_conf * 100, 2)
    }
    return final_score, breakdown
