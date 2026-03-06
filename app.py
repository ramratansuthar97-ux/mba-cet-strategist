import streamlit as st
import json
import time
from datetime import datetime

# --- SET PAGE CONFIG ---
st.set_page_config(page_title="MBA CET Strategist", page_icon="🎯", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; font-weight: bold; }
    .stSelectbox { font-size: 12px; }
    .main-header { font-size: 2.5rem; font-weight: 800; color: #1E293B; margin-bottom: 0.5rem; }
    .strategy-box { background-color: #0F172A; color: white; padding: 20px; border-radius: 15px; border-left: 5px solid #3B82F6; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- SAMPLE DATA (This will grow once you run your extraction script) ---
SAMPLE_DATA = [
    {
        "id": 1,
        "slot": "2025 Slot 1",
        "section": "Quantitative Aptitude",
        "topic": "Mensuration",
        "difficulty": "Level 2 (Moderate)",
        "question": "The length of a room exceeds its breadth by 2 meters. If the length be increased by 4 meters and the breadth decreased by 2 meters, the area remains the same. Find the surface area of its walls if the height is 3 meters?",
        "options": ["248 m²", "48 m²", "84 m²", "56 m²", "260 m²"],
        "correctAnswer": 2,
        "proTrick": "Multiples of 6: Formula is 2H(L+B) = 6(L+B). Only 84 and 48 are divisible by 6. Testing confirms 84.",
        "idealTime": 40,
        "skipLogic": "SOLVE. Use divisibility to save time.",
        "recurrence": "High"
    },
    {
        "id": 2,
        "slot": "2025 Slot 6",
        "section: ": "Logical Reasoning",
        "topic": "Blood Relations",
        "difficulty": "Level 1 (Easy)",
        "question": "Puja is the mother-in-law of Sunita who is the wife of Rohit. Rohit whose father is Gajanan, is the father of Rupali. Dhanashree is the daughter of Puja. How is Puja related to Rupali?",
        "options": ["Grandson", "Grandmother", "Granddaughter", "Aunt", "Mother-in-law"],
        "correctAnswer": 1,
        "proTrick": "Direct Mapping: Rohit's Mom = Rupali's Grandma. Ignore others.",
        "idealTime": 30,
        "skipLogic": "SOLVE.",
        "recurrence": "Standard"
    }
]

# --- INITIALIZE SESSION STATE (Persistence) ---
if 'answers' not in st.session_state: st.session_state.answers = {}
if 'doubts' not in st.session_state: st.session_state.doubts = []
if 'q_index' not in st.session_state: st.session_state.q_index = 0
if 'start_time' not in st.session_state: st.session_state.start_time = time.time()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.title("🎯 CET Strategist")
    
    # Filter Logic
    sections = ["All"] + list(set(q["section"] for q in SAMPLE_DATA))
    selected_section = st.selectbox("Select Subject", sections)
    
    if selected_section == "All":
        filtered_questions = SAMPLE_DATA
    else:
        filtered_questions = [q for q in SAMPLE_DATA if q["section"] == selected_section]
        
    st.divider()
    
    # Progress Metric
    done = len(st.session_state.answers)
    total = len(SAMPLE_DATA)
    st.progress(done/total if total > 0 else 0)
    st.write(f"Progress: {done}/{total}")
    
    # Reset Button
    if st.button("🗑️ Reset All Progress"):
        st.session_state.answers = {}
        st.session_state.doubts = []
        st.session_state.q_index = 0
        st.rerun()

# --- MAIN DASHBOARD ---
if filtered_questions:
    # Ensure index doesn't go out of bounds after filtering
    if st.session_state.q_index >= len(filtered_questions):
        st.session_state.q_index = 0
        
    q = filtered_questions[st.session_state.q_index]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### Q{st.session_state.q_index + 1}: {q['topic']}")
        st.caption(f"📍 {q['slot']} | {q['difficulty']}")
        
        # Question Display
        st.info(q['question'])
        
        # Options
        options_labels = [f"{chr(65+i)}) {opt}" for i, opt in enumerate(q['options'])]
        
        # Persistence check
        already_answered = q['id'] in st.session_state.answers
        saved_answer = st.session_state.answers.get(q['id'])
        
        user_choice = st.radio(
            "Select your answer:", 
            options_labels, 
            index=options_labels.index(saved_answer) if already_answered else None,
            key=f"q_{q['id']}",
            disabled=already_answered
        )
        
        # Check Answer
        if st.button("Submit Answer") and not already_answered:
            choice_idx = options_labels.index(user_choice)
            st.session_state.answers[q['id']] = user_choice
            st.rerun()

    with col2:
        # Timer Display
        current_duration = int(time.time() - st.session_state.start_time)
        st.markdown(f"""
            <div class='metric-card'>
                <p style='margin:0; font-size:12px; font-weight:bold; color:#64748B;'>ELAPSED TIME</p>
                <h2 style='margin:0; color:#EF4444;'>{current_duration}s</h2>
                <p style='margin:0; font-size:10px;'>Target: {q['idealTime']}s</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("🔖 Mark Doubt"):
            if q['id'] not in st.session_state.doubts:
                st.session_state.doubts.append(q['id'])
                st.success("Added to Review")
        
        if q['id'] in st.session_state.doubts:
            st.warning("⚠️ Flagged for Doubt")

    # --- STRATEGY REVEAL ---
    if already_answered:
        st.divider()
        is_correct = options_labels.index(st.session_state.answers[q['id']]) == q['correctAnswer']
        
        if is_correct:
            st.success("✅ Correct! Brilliant work.")
        else:
            st.error(f"❌ Incorrect. The right answer is {chr(65+q['correctAnswer'])})")
            
        st.markdown(f"""
            <div class='strategy-box'>
                <h4 style='color:#60A5FA; margin-top:0;'>⚡ THE PRO-TRICK</h4>
                <p style='font-size:15px;'>{q['proTrick']}</p>
                <div style='display:flex; gap:20px; margin-top:15px;'>
                    <div><small style='color:#94A3B8;'>SKIP LOGIC</small><br><b>{q['skipLogic']}</b></div>
                    <div><small style='color:#94A3B8;'>RECURRENCE</small><br><b>{q['recurrence']}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- FOOTER NAV ---
    st.divider()
    fcol1, fcol2, fcol3 = st.columns([1, 2, 1])
    with fcol1:
        if st.button("⬅️ Previous") and st.session_state.q_index > 0:
            st.session_state.q_index -= 1
            st.session_state.start_time = time.time()
            st.rerun()
    with fcol3:
        if st.button("Next ➡️") and st.session_state.q_index < len(filtered_questions) - 1:
            st.session_state.q_index += 1
            st.session_state.start_time = time.time()
            st.rerun()

else:
    st.warning("No questions match your filter. Please select another subject.")
