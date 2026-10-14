import streamlit as st
from google import genai
from pypdf import PdfReader
from PIL import Image
from youtube_transcript_api import YouTubeTranscriptApi
import re

st.set_page_config(page_title="NEET & JEE AI Tutor", page_icon="🎯", layout="centered")
st.title("🎯 NEET & JEE Smart AI App")
st.caption("AI Bot • VVI Notes • Flashcards • PYQs • YouTube Notes")

api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key dalein:", type="password")

def ask_ai(prompt, image=None):
    if not api_key:
        st.warning("⚠️ Kripya Streamlit Secrets ya Sidebar mein apni Gemini API Key dalein!")
        return None
    try:
        client = genai.Client(api_key=api_key)
        contents = [image, prompt] if image else prompt
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )
        return response.text
    except Exception as e:
        st.error(f"Error: {e}")
        return None

mode = st.selectbox(
    "👇 Apna Study Tool Chunein:",
    [
        "🤖 1. AI Study & Doubt Bot",
        "📄 2. Notes/Photo se VVI, Short Notes & Formulas",
        "🎥 3. YouTube Video se High-Concept Notes",
        "🗂️ 4. Smart Flashcards Maker",
        "📝 5. NEET & JEE PYQ Practice"
    ]
)

st.divider()

if mode == "🤖 1. AI Study & Doubt Bot":
    st.subheader("🤖 Personal NEET/JEE AI Tutor")
    doubt_img = st.file_uploader("Sawal ki photo upload karein (Optional):", type=["jpg", "jpeg", "png"])
    user_q = st.text_area("Apna sawal ya topic likhein (Hinglish/English/Hindi):")
    
    if st.button("🚀 Samjhao"):
        if user_q or doubt_img:
            with st.spinner("AI Tutor soch raha hai..."):
                img = Image.open(doubt_img) if doubt_img else None
                prompt = f"""
                Tum ek expert NEET aur JEE coach ho. Student ke is sawal ko step-by-step aasan Hinglish mein samjhao. 
                Agar numerical hai toh formula, trick aur pura calculation dikhao:
                Sawal: {user_q}
                """
                ans = ask_ai(prompt, img)
                if ans:
                    st.markdown(ans)

elif mode == "📄 2. Notes/Photo se VVI, Short Notes & Formulas":
    st.subheader("📄 Notes Analyzer (PDF ya Photo)")
    upload_type = st.radio("Kya upload karna hai?", ["Notes ki Photo", "PDF File"], horizontal=True)
    
    extracted_text = ""
    img_data = None
    
    if upload_type == "PDF File":
        pdf_file = st.file_uploader("PDF upload karein", type=["pdf"])
        if pdf_file:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                if page.extract_text():
                    extracted_text += page.extract_text()
            st.success("✅ PDF Load Ho Gayi!")
    else:
        photo_file = st.file_uploader("Handwritten Notes ya Book ke page ki photo lein", type=["jpg", "jpeg", "png"])
        if photo_file:
            img_data = Image.open(photo_file)
            st.image(img_data, caption="Uploaded Notes", use_container_width=True)

    task = st.selectbox("In notes se kya banana hai?", [
        "🔥 VVI Questions (NEET/JEE Level) with Solutions",
        "⚡ Short Revision Notes + All Formulas Sheet",
        "🧠 High-Concept Deep Explanation",
        "🎬 Visual Video Script (3D Animation Concept Breakdown)"
    ])

    if st.button("✨ Generate Karein"):
        if extracted_text or img_data:
            with st.spinner("Notes scan ho rahe hain..."):
                prompt = f"""
                Tum ek top NEET/JEE faculty ho. Diye gaye study notes ke aadhar par '{task}' taiyar karo.
                Bhasha simple Hinglish rakho, saare important formulas highlight karo aur exam tricks batao.
                Notes Text: {extracted_text[:15000]}
                """
                res = ask_ai(prompt, img_data)
                if res:
                    st.markdown(res)
        else:
            st.warning("Pehle PDF ya Photo upload karein!")

elif mode == "🎥 3. YouTube Video se High-Concept Notes":
    st.subheader("🎥 YouTube Lecture Summarizer")
    yt_url = st.text_input("YouTube Video ka Link paste karein:")
    topic_backup = st.text_input("Chapter/Topic ka naam likhein:")
    
    if st.button("📝 Video Notes & Formulas Banayein"):
        with st.spinner("Video se High-Concept aur Short Notes ban rahe hain..."):
            transcript_text = ""
            if yt_url:
                match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", yt_url)
                if match:
                    vid_id = match.group(1)
                    try:
                        t_list = YouTubeTranscriptApi.get_transcript(vid_id, languages=['hi', 'en'])
                        transcript_text = " ".join([t['text'] for t in t_list])
                    except Exception:
                        st.info("Topic ke naam se High-Concept notes banaye ja rahe hain.")
            
            prompt = f"""
            Ek expert NEET/JEE teacher ki tarah niche diye gaye lecture data/topic se:
            1. High-Concept Detailed Notes (with deep logic)
            2. Ultra-Short 1-Page Revision Notes
            3. Complete Formula & Reaction Sheet
            4. 5 VVI Exam Questions with answers
            taiyar karo.
            Topic: {topic_backup}
            Lecture Content: {transcript_text[:15000]}
            """
            res = ask_ai(prompt)
            if res:
                st.markdown(res)

elif mode == "🗂️ 4. Smart Flashcards Maker":
    st.subheader("🗂️ Quick Revision Flashcards")
    fc_topic = st.text_input("Chapter ya Topic ka naam likhein (jaise: Thermodynamics, Plant Kingdom):")
    
    if st.button("🃏 5 Smart Flashcards Banayein"):
        if fc_topic:
            with st.spinner("Flashcards taiyar ho rahe hain..."):
                prompt = f"""
                Topic '{fc_topic}' par NEET/JEE revision ke liye 5 sabse important Flashcards banao.
                Har flashcard ko bilkul is format mein likho:
                Q: [Sawal ya Concept]
                A: [Chhota, crisp jawab ya Formula/Trick]
                ---
                """
                res = ask_ai(prompt)
                if res:
                    cards = res.split("---")
                    for i, card in enumerate(cards, 1):
                        if "Q:" in card and "A:" in card:
                            parts = card.split("A:")
                            q_part = parts[0].replace("Q:", "").strip()
                            a_part = parts[1].strip()
                            with st.expander(f"📌 Card {i}: {q_part}"):
                                st.success(f"**Jawab:** {a_part}")

elif mode == "📝 5. NEET & JEE PYQ Practice":
    st.subheader("📝 Previous Year Questions (PYQs)")
    col1, col2 = st.columns(2)
    with col1:
        exam = st.selectbox("Exam:", ["NEET UG", "JEE Main", "JEE Advanced"])
    with col2:
        subject = st.selectbox("Subject:", ["Physics", "Chemistry", "Biology", "Mathematics"])
    
    chapter = st.text_input("Chapter ka naam likhein (jaise: Rotational Motion, Equilibrium):")
    
    if st.button("🎯 5 Important PYQs Dein"):
        if chapter:
            with st.spinner(f"{exam} ke PYQs nikaale ja rahe hain..."):
                prompt = f"""
                {exam} ke {subject} ke chapter '{chapter}' se 5 sabse important Previous Year Questions (PYQs) year tag ke saath do.
                Pehle saare 5 sawal unke 4 options (A, B, C, D) ke saath likho.
                Uske baad niche '===SOLUTIONS===' likhkar har sawal ka sahi option aur step-by-step trick/solution do.
                """
                res = ask_ai(prompt)
                if res:
                    if "===SOLUTIONS===" in res:
                        q_sec, sol_sec = res.split("===SOLUTIONS===")
                        st.markdown(q_sec)
                        with st.expander("👀 Answer Key & Step-by-Step Solutions Dekhein"):
                            st.markdown(sol_sec)
                    else:
                        st.markdown(res)
