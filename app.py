# app.py - AI Mock Interview Evaluator with Screenshot-Optimized UI
import streamlit as st
import json
import os
import tempfile
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy.video.io.VideoFileClip import VideoFileClip

from modules import audio_processing, text_analysis, video_analysis, scoring

# Page config
st.set_page_config(
    page_title="AI Mock Interview Evaluator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Custom CSS - Optimized for Screenshots
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1600px;
    }
    
    /* Hero Header - Compact */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.95;
        font-weight: 400;
    }
    
    /* Card styling - Compact */
    .custom-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8;
        margin-bottom: 1rem;
        height: 100%;
    }
    
    .card-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    /* Question box - Compact */
    .question-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border-left: 4px solid #667eea;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.15);
    }
    
    .question-text {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        line-height: 1.5;
        margin: 0;
    }
    
    /* Score display - Compact */
    .score-mega {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin: 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .score-number {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .score-label {
        font-size: 1.1rem;
        opacity: 0.95;
        margin-top: 0.3rem;
    }
    
    /* Status badges - Compact */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.3rem;
    }
    
    .badge-excellent {
        background: #4caf50;
        color: white;
    }
    
    .badge-good {
        background: #ff9800;
        color: white;
    }
    
    .badge-improve {
        background: #f44336;
        color: white;
    }
    
    /* Metric cards - Compact */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #e8e8e8;
        height: 100%;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.3rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        font-weight: 500;
    }
    
    /* Buttons - Compact */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Tabs styling - Compact */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 0.4rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.2);
        color: white;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #667eea;
    }
    
    /* Info boxes - Compact */
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%);
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    .error-box {
        background: linear-gradient(135deg, #ffebee 0%, #fce4ec 100%);
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    /* Transcript area - Compact */
    .transcript-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        max-height: 180px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        line-height: 1.5;
        font-size: 0.85rem;
    }
    
    /* Two-column layout helper */
    .split-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Compact headings */
    .compact-heading {
        font-size: 1rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: #f5f7fa;
        border-radius: 5px;
    }
    
    /* Video container */
    .video-container {
        max-height: 300px;
        overflow: hidden;
        border-radius: 10px;
    }
    
    /* Feedback section - Compact */
    .feedback-section {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 2px solid #e8e8e8;
        margin: 0.5rem 0;
    }
    
    .feedback-section h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
    }
    
    .feedback-section p {
        margin: 0.3rem 0;
        font-size: 0.85rem;
    }
    
    .feedback-section ul {
        margin: 0.5rem 0;
        padding-left: 1.2rem;
    }
    
    .feedback-section li {
        margin: 0.2rem 0;
        font-size: 0.85rem;
    }
    
    /* Hide scrollbar but keep functionality */
    .element-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .element-container::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    .element-container::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 3px;
    }
    
    /* Plotly chart height control */
    .js-plotly-plot {
        height: 250px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.question = None
    st.session_state.last_result = None
    st.session_state.analysis_done = False
    st.session_state.selected_role = "Software Developer"
    st.session_state.use_free_transcription = True
    st.session_state.enable_video = True
    st.session_state.fast_mode = True

# Load role keywords
@st.cache_data
def load_role_keywords():
    try:
        with open("role_keywords.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "Software Developer": ["programming", "code", "algorithm", "database", "api", "testing", "debugging", "software", "development"],
            "Data Analyst": ["data", "analysis", "visualization", "sql", "dashboard", "metrics", "insights", "statistics", "reporting"],
            "HR Executive": ["recruitment", "onboarding", "employee", "performance", "retention", "conflict", "hiring", "training"]
        }

role_keywords = load_role_keywords()
roles = list(role_keywords.keys())

questions = {
    "Software Developer": [
        "Explain object-oriented programming and give an example.",
        "Describe how you would design a REST API.",
        "Explain a situation where you optimized code for performance.",
        "What is the difference between SQL and NoSQL databases?",
        "Describe your experience with version control systems like Git."
    ],
    "Data Analyst": [
        "Explain how you would clean a messy dataset.",
        "Describe a dashboard you built and the metrics you tracked.",
        "How do you write SQL to find the top 10 customers by revenue?",
        "What is your approach to data visualization?",
        "Explain the difference between correlation and causation."
    ],
    "HR Executive": [
        "How do you handle a conflict between two employees?",
        "Describe your process for onboarding a new hire.",
        "How do you measure employee satisfaction?",
        "What strategies do you use for talent retention?",
        "Explain your approach to performance reviews."
    ]
}

# HERO HEADER - Compact
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🎯 AI Mock Interview Evaluator</div>
    <div class="hero-subtitle">🆓 FREE Transcription • Multi-Modal Analysis • Real-Time Feedback</div>
</div>
""", unsafe_allow_html=True)

# MAIN TABS
tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Setup", "🎬 Interview", "📊 Results", "💡 Insights"])

# TAB 1: SETUP - Compact Single Screen
with tab1:
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🎯 Interview Role</div>', unsafe_allow_html=True)
        role = st.selectbox("Select Role", roles, index=0, key="role_select", label_visibility="collapsed")
        st.session_state.selected_role = role
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🔊 Transcription</div>', unsafe_allow_html=True)
        trans_method = st.radio(
            "Method:",
            ["🆓 FREE Auto", "📝 Manual"],
            key="trans_method",
            label_visibility="collapsed",
            horizontal=True
        )
        st.session_state.use_free_transcription = (trans_method == "🆓 FREE Auto")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🎥 Analysis Options</div>', unsafe_allow_html=True)
        st.session_state.enable_video = st.checkbox("Video Analysis", value=True, key="video_enable")
        st.session_state.fast_mode = st.checkbox("Fast Mode", value=True, key="fast_enable")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">⏱️ Est. Time</div>', unsafe_allow_html=True)
        estimated_time = 30 if st.session_state.use_free_transcription else 5
        estimated_time += 5
        if st.session_state.enable_video:
            estimated_time += 20 if st.session_state.fast_mode else 40
        estimated_time += 5
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">~{estimated_time}s</div>
            <div class="metric-label">Processing Time</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📊 Score Weights</div>', unsafe_allow_html=True)
        
        weights = [("📚 Content", "45%"), ("💬 Clarity", "15%"), ("🎤 Audio", "20%"), ("📹 Video", "20%")]
        for label, weight in weights:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #eee;">
                <span style="font-size: 0.9rem;">{label}</span>
                <span style="font-weight: 700; color: #667eea;">{weight}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: INTERVIEW - Single Screen Layout
with tab2:
    # Top row - Question and Controls
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🎬 Interview Question</div>', unsafe_allow_html=True)
        
        if st.session_state.question:
            st.markdown(f"""
            <div class="question-box">
                <div style="font-size: 0.8rem; color: #666; margin-bottom: 0.3rem;">
                    📌 {st.session_state.selected_role}
                </div>
                <div class="question-text">{st.session_state.question}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">Click "Generate Question" to start</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🎮 Controls</div>', unsafe_allow_html=True)
        
        if st.button("🚀 Generate Question", use_container_width=True, key="gen_question"):
            import random
            st.session_state.question = random.choice(questions[st.session_state.selected_role])
            st.session_state.analysis_done = False
            st.session_state.last_result = None
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Bottom row - Video Upload and Manual Transcript (if needed)
    if not st.session_state.use_free_transcription:
        col1, col2 = st.columns([1, 1])
    else:
        col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📹 Video Input</div>', unsafe_allow_html=True)
        
        video_source = st.radio("Source:", ["📁 Upload", "📸 Webcam"], horizontal=True, key="video_source", label_visibility="collapsed")
        
        video_file = None
        cam_video = None
        
        if video_source == "📁 Upload":
            video_file = st.file_uploader(
                "Drop video here",
                type=["mp4", "mov", "avi", "mkv", "webm"],
                key="video_upload",
                label_visibility="collapsed"
            )
            if video_file:
                st.success(f"✅ {video_file.name}")
                st.video(video_file)
        else:
            cam_video = st.camera_input("Record", key="camera", label_visibility="collapsed")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if not st.session_state.use_free_transcription:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📝 Manual Transcript</div>', unsafe_allow_html=True)
            manual_transcript = st.text_area(
                "Type your answer:",
                height=200,
                placeholder="Enter transcript...",
                key="manual_trans",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            manual_transcript = ""
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">ℹ️ Info</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="info-box">
                <strong>Using FREE Auto Transcription</strong><br>
                Upload your video and click Analyze.<br>
                Speech will be transcribed automatically.
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Analyze Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 ANALYZE INTERVIEW", use_container_width=True, type="primary", key="analyze")

# ANALYSIS LOGIC
if analyze_button:
    if not st.session_state.question:
        st.error("❌ Generate a question first!")
    elif not video_file and not cam_video:
        st.error("❌ Upload or record video!")
    elif not st.session_state.use_free_transcription and not manual_transcript:
        st.error("❌ Enter transcript!")
    else:
        with st.spinner("🔄 Processing..."):
            try:
                chosen_video = cam_video if cam_video else video_file
                
                tmp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                tmp_video.write(chosen_video.getvalue())
                tmp_video.close()
                tmp_video_path = tmp_video.name
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🎵 Extracting audio...")
                progress_bar.progress(10)
                
                tmp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
                audio_processing.extract_audio_from_video(tmp_video_path, tmp_audio_path, fast_mode=st.session_state.fast_mode)
                progress_bar.progress(20)
                
                transcript = ""
                if st.session_state.use_free_transcription:
                    status_text.text("🎙️ Transcribing...")
                    progress_bar.progress(25)
                    transcript = audio_processing.transcribe_with_google_free(tmp_audio_path)
                    progress_bar.progress(50)
                else:
                    transcript = manual_transcript
                    progress_bar.progress(50)
                
                if not transcript or len(transcript.strip()) < 10:
                    st.error("❌ Transcript too short!")
                    st.stop()
                
                status_text.text("📊 Analyzing audio...")
                progress_bar.progress(55)
                
                audio_dur = audio_processing.get_audio_duration_seconds(tmp_audio_path)
                audio_metrics = audio_processing.simple_speech_metrics(transcript, audio_dur)
                progress_bar.progress(60)
                
                if st.session_state.enable_video:
                    status_text.text("🎥 Analyzing video...")
                    progress_bar.progress(65)
                    video_metrics = video_analysis.analyze_video_emotions(
                        tmp_video_path,
                        sample_every_n_frames=60 if st.session_state.fast_mode else 30,
                        max_frames=8 if st.session_state.fast_mode else 15
                    )
                    progress_bar.progress(85)
                else:
                    video_metrics = {
                        'sampled_frames': 0,
                        'face_present_ratio': 0,
                        'emotion_confidence_score': 0.5,
                        'emotion_counts': {}
                    }
                    progress_bar.progress(85)
                
                status_text.text("🧠 NLP analysis...")
                progress_bar.progress(90)
                
                keywords = role_keywords.get(st.session_state.selected_role, [])
                nlp_kw_score = text_analysis.keyword_score(transcript, keywords)
                clarity = text_analysis.clarity_score(transcript)
                
                status_text.text("✅ Final scoring...")
                progress_bar.progress(95)
                
                final_score, breakdown = scoring.aggregate_scores(
                    nlp_kw_score, clarity, audio_metrics, video_metrics
                )
                
                result = {
                    "final_score": final_score,
                    "breakdown": breakdown,
                    "transcript": transcript,
                    "audio_metrics": audio_metrics,
                    "video_metrics": video_metrics,
                    "role": st.session_state.selected_role,
                    "question": st.session_state.question,
                    "nlp_kw_score": nlp_kw_score,
                    "clarity": clarity,
                    "audio_duration": audio_dur
                }
                
                st.session_state.last_result = result
                st.session_state.analysis_done = True
                
                progress_bar.progress(100)
                status_text.text("🎉 Complete!")
                
                for path in [tmp_video_path, tmp_audio_path]:
                    if os.path.exists(path):
                        try:
                            os.unlink(path)
                        except:
                            pass
                
                progress_bar.empty()
                status_text.empty()
                st.success("🎉 Check Results tab!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Failed: {str(e)}")

# TAB 3: RESULTS - Single Screen with Side-by-Side Layout
with tab3:
    if st.session_state.last_result:
        result = st.session_state.last_result
        
        # Row 1: Overall Score + Performance Breakdown (Side by Side)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div class="score-mega">
                <div class="score-number">{result["final_score"]:.1f}</div>
                <div class="score-label">Overall Score</div>
            </div>
            """, unsafe_allow_html=True)
            
            if result["final_score"] >= 80:
                st.markdown('<div style="text-align: center; margin-top: 0.5rem;"><span class="status-badge badge-excellent">🌟 OUTSTANDING</span></div>', unsafe_allow_html=True)
            elif result["final_score"] >= 60:
                st.markdown('<div style="text-align: center; margin-top: 0.5rem;"><span class="status-badge badge-good">👍 GOOD JOB</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align: center; margin-top: 0.5rem;"><span class="status-badge badge-improve">💪 PRACTICE</span></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📈 Performance Breakdown</div>', unsafe_allow_html=True)
            
            breakdown_df = pd.DataFrame([
                {"Category": "Content", "Score": result['breakdown']['content'], "Weight": "45%"},
                {"Category": "Clarity", "Score": result['breakdown']['clarity'], "Weight": "15%"},
                {"Category": "Audio", "Score": result['breakdown']['audio_confidence'], "Weight": "20%"},
                {"Category": "Video", "Score": result['breakdown']['video_confidence'], "Weight": "20%"}
            ])
            
            fig_bar = px.bar(
                breakdown_df, x="Category", y="Score",
                color="Score",
                color_continuous_scale=["#f44336", "#ff9800", "#4caf50"],
                text="Score"
            )
            fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_bar.update_layout(height=220, showlegend=False, yaxis_range=[0, 105], margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Row 2: Audio and Video Analysis (Side by Side)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🎤 Audio Analysis</div>', unsafe_allow_html=True)
            
            audio_cols = st.columns(2)
            with audio_cols[0]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Speaking Rate</div>
                    <div class="metric-value" style="font-size: 1.5rem;">{result['audio_metrics']['words_per_second']:.2f}</div>
                    <div class="metric-label" style="font-size: 0.8rem;">words/sec</div>
                </div>
                """, unsafe_allow_html=True)
            with audio_cols[1]:
                pause_pct = result['audio_metrics']['pause_ratio'] * 100
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Pause Ratio</div>
                    <div class="metric-value" style="font-size: 1.5rem;">{pause_pct:.1f}%</div>
                    <div class="metric-label" style="font-size: 0.8rem;">of duration</div>
                </div>
                """, unsafe_allow_html=True)
            
            audio_cols2 = st.columns(2)
            with audio_cols2[0]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Words</div>
                    <div class="metric-value" style="font-size: 1.5rem;">{result['audio_metrics']['word_count']}</div>
                </div>
                """, unsafe_allow_html=True)
            with audio_cols2[1]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Duration</div>
                    <div class="metric-value" style="font-size: 1.5rem;">{result['audio_duration']:.1f}s</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📹 Video Analysis</div>', unsafe_allow_html=True)
            
            if result['video_metrics']['sampled_frames'] > 0:
                video_cols = st.columns(2)
                with video_cols[0]:
                    face_pct = result['video_metrics']['face_present_ratio'] * 100
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Face Detection</div>
                        <div class="metric-value" style="font-size: 1.5rem;">{face_pct:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                with video_cols[1]:
                    emotion_score = result['video_metrics']['emotion_confidence_score'] * 100
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Emotion Score</div>
                        <div class="metric-value" style="font-size: 1.5rem;">{emotion_score:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if result['video_metrics']['emotion_counts']:
                    emotion_df = pd.DataFrame(
                        list(result['video_metrics']['emotion_counts'].items()),
                        columns=['Emotion', 'Count']
                    )
                    fig_pie = px.pie(
                        emotion_df, values='Count', names='Emotion',
                        hole=0.4
                    )
                    fig_pie.update_layout(height=180, margin=dict(t=10, b=10, l=10, r=10))
                    st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.markdown('<div class="info-box">Video analysis was disabled</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Row 3: Transcript
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📝 Your Transcript</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="transcript-box">{result["transcript"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div class="custom-card">
            <div class="info-box">
                <h3>📊 Complete your interview to see results!</h3>
                <p>You'll get comprehensive analysis with scores, breakdowns, and detailed metrics.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# TAB 4: INSIGHTS - Single Screen, No Scrolling
with tab4:
    if st.session_state.last_result:
        result = st.session_state.last_result
        
        # Row 1: Content + Clarity Feedback (Side by Side)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">💡 Performance Feedback</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Content feedback
            if result['breakdown']['content'] < 50:
                st.markdown("""
                <div class="feedback-section" style="border-left: 4px solid #f44336;">
                    <h4>🔴 Content - Needs Improvement</h4>
                    <p><strong>Score:</strong> {:.1f}/100</p>
                    <ul>
                        <li>Use more role-specific keywords</li>
                        <li>Include concrete examples</li>
                        <li>Show deeper technical knowledge</li>
                    </ul>
                </div>
                """.format(result['breakdown']['content']), unsafe_allow_html=True)
            elif result['breakdown']['content'] < 75:
                st.markdown("""
                <div class="feedback-section" style="border-left: 4px solid #ff9800;">
                    <h4>🟡 Content - Good Foundation</h4>
                    <p><strong>Score:</strong> {:.1f}/100</p>
                    <ul>
                        <li>Add more technical depth</li>
                        <li>Include specific metrics</li>
                        <li>Expand examples with detail</li>
                    </ul>
                </div>
                """.format(result['breakdown']['content']), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="feedback-section" style="border-left: 4px solid #4caf50;">
                    <h4>🟢 Content - Excellent!</h4>
                    <p><strong>Score:</strong> {:.1f}/100</p>
                    <ul>
                        <li>Strong terminology use</li>
                        <li>Clear understanding shown</li>
                        <li>Keep up the great work!</li>
                    </ul>
                </div>
                """.format(result['breakdown']['content']), unsafe_allow_html=True)
            
            # Audio feedback
            if result['breakdown']['audio_confidence'] < 50:
                st.markdown("""
                <div class="feedback-section" style="border-left: 4px solid #f44336;">
                    <h4>🔴 Audio - Practice Needed</h4>
                    <p><strong>Score:</strong> {:.1f}/100</p>
                    <ul>
                        <li>Speak more fluently</li>
                        <li>Reduce pauses and fillers</li>
                        <li>Maintain steady pace</li>
                    </ul>
                </div>
                """.format(result['breakdown']['audio_confidence']), unsafe_allow_html=True)
            elif result['breakdown']['audio_confidence'] < 75:
                st.markdown("""
                <div class="feedback-section" style="border-left: 4px solid #ff9800;">
                    <h4>🟡 Audio - Good Delivery</h4>
                    <p><strong>Score:</strong> {:.1f}/100</p>
                    <ul>
                        <li>Eliminate filler words</li>
                        <li>Vary tone for emphasis</li>
                        <li>Reduce minor pauses</li>
                    </ul>
                </div>
                """.format(result['breakdown']['audio_confidence']), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="feedback-section" style="border-left: 4px solid #4caf50;">
                    <h4>🟢 Audio - Excellent!</h4>
                    <p><strong>Score:</strong> {:.1f}/100</p>
                    <ul>
                        <li>Excellent vocal delivery</li>
                        <li>Well-paced rhythm</li>
                        <li>Professional quality</li>
                    </ul>
                </div>
                """.format(result['breakdown']['audio_confidence']), unsafe_allow_html=True)
        
        with col2:
            # Clarity feedback
            clarity_score = result['clarity'] * 100
            if clarity_score < 50:
                st.markdown("""
                <div class="feedback-section" style="border-left: 4px solid #f44336;">
                    <h4>🔴 Clarity - Needs Work</h4>
                    <p><strong>Score:</strong> {:.1f}/100</p>
                    <ul>
                        <li>Use STAR method structure</li>
                        <li>Keep sentences concise</li>
                        <li>Avoid rambling</li>
                    </ul>
                </div>
                """.format(clarity_score), unsafe_allow_html=True)
            elif clarity_score < 75:
                st.markdown("""
                <div class="feedback-section" style="border-left: 4px solid #ff9800;">
                    <h4>🟡 Clarity - Well-Structured</h4>
                    <p><strong>Score:</strong> {:.1f}/100</p>
                    <ul>
                        <li>Add concrete examples</li>
                        <li>Use better transitions</li>
                        <li>Reduce filler words</li>
                    </ul>
                </div>
                """.format(clarity_score), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="feedback-section" style="border-left: 4px solid #4caf50;">
                    <h4>🟢 Clarity - Crystal Clear!</h4>
                    <p><strong>Score:</strong> {:.1f}/100</p>
                    <ul>
                        <li>Very clear responses</li>
                        <li>Excellent organization</li>
                        <li>Professional delivery</li>
                    </ul>
                </div>
                """.format(clarity_score), unsafe_allow_html=True)
            
            # Video feedback
            if result['video_metrics']['sampled_frames'] > 0:
                if result['breakdown']['video_confidence'] < 50:
                    st.markdown("""
                    <div class="feedback-section" style="border-left: 4px solid #f44336;">
                        <h4>🔴 Video - Work on Body Language</h4>
                        <p><strong>Score:</strong> {:.1f}/100</p>
                        <ul>
                            <li>Maintain eye contact</li>
                            <li>Practice positive expressions</li>
                            <li>Check lighting/camera</li>
                        </ul>
                    </div>
                    """.format(result['breakdown']['video_confidence']), unsafe_allow_html=True)
                elif result['breakdown']['video_confidence'] < 75:
                    st.markdown("""
                    <div class="feedback-section" style="border-left: 4px solid #ff9800;">
                        <h4>🟡 Video - Good Presence</h4>
                        <p><strong>Score:</strong> {:.1f}/100</p>
                        <ul>
                            <li>More positive expressions</li>
                            <li>Smile when appropriate</li>
                            <li>Stay engaged</li>
                        </ul>
                    </div>
                    """.format(result['breakdown']['video_confidence']), unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="feedback-section" style="border-left: 4px solid #4caf50;">
                        <h4>🟢 Video - Excellent!</h4>
                        <p><strong>Score:</strong> {:.1f}/100</p>
                        <ul>
                            <li>Excellent camera presence</li>
                            <li>Good eye contact</li>
                            <li>Professional quality</li>
                        </ul>
                    </div>
                    """.format(result['breakdown']['video_confidence']), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Row 2: Action Items + Download Options
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🎯 Top Action Items</div>', unsafe_allow_html=True)
            
            action_items = []
            if result['breakdown']['content'] < 70:
                action_items.append("📚 Study role-specific topics for " + result['role'])
            if result['clarity'] * 100 < 70:
                action_items.append("📝 Practice STAR method structure")
            if result['audio_metrics']['pause_ratio'] > 0.3:
                action_items.append("🎤 Reduce pauses - practice fluency")
            if result['video_metrics']['sampled_frames'] > 0 and result['breakdown']['video_confidence'] < 70:
                action_items.append("📹 Improve body language and expressions")
            
            if not action_items:
                action_items.append("🌟 Great job! Keep practicing")
            
            for item in action_items[:4]:  # Limit to 4 items
                st.markdown(f"<div style='padding: 0.4rem 0; border-bottom: 1px solid #eee;'>• {item}</div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📥 Export</div>', unsafe_allow_html=True)
            
            result_json = json.dumps(result, indent=2, default=str)
            st.download_button(
                "📄 JSON",
                result_json,
                f"results_{result['role'].replace(' ', '_')}.json",
                "application/json",
                use_container_width=True
            )
            
            breakdown_df = pd.DataFrame([
                {"Category": "Content", "Score": result['breakdown']['content']},
                {"Category": "Clarity", "Score": result['breakdown']['clarity']},
                {"Category": "Audio", "Score": result['breakdown']['audio_confidence']},
                {"Category": "Video", "Score": result['breakdown']['video_confidence']}
            ])
            csv_data = breakdown_df.to_csv(index=False)
            st.download_button(
                "📊 CSV",
                csv_data,
                f"breakdown_{result['role'].replace(' ', '_')}.csv",
                "text/csv",
                use_container_width=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div class="custom-card">
            <div class="info-box">
                <h3>💡 Complete your interview to see insights!</h3>
                <p>You'll receive personalized feedback on content, clarity, audio, and video performance.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer - Compact
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 0.5rem 0;'>
    <p style='font-size: 1rem; font-weight: 600; color: #667eea; margin: 0;'>🎯 AI Mock Interview Evaluator</p>
    <p style='font-size: 0.8rem; color: #999; margin: 0.3rem 0;'>
        Powered by Google Speech API • spaCy • DeepFace • OpenCV
    </p>
</div>
""", unsafe_allow_html=True)