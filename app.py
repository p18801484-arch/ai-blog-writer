import streamlit as st
from google import genai
from google.genai import types

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------
st.set_page_config(
    page_title="AI Blog Writer",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------
# CUSTOM LIGHT THEME CSS
# -----------------------------------
st.markdown("""
<style>
.stApp { background-color: #F4F7FB; color: #1F2937; }
.main .block-container { max-width: 1100px; padding-top: 2rem; padding-bottom: 3rem; }
h1, h2, h3 { color: #172554 !important; }
p, label, .stMarkdown { color: #1F2937; }
.stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important; color: #111827 !important; border-radius: 8px;
}
.stTextInput input::placeholder { color: #6B7280 !important; }
.stButton > button, .stFormSubmitButton > button {
    background-color: #2563EB; color: #FFFFFF !important; border: none;
    border-radius: 10px; padding: 0.65rem 1rem; font-weight: 600; transition: 0.2s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: #1D4ED8; color: #FFFFFF !important; border: none;
}
.stDownloadButton > button {
    background-color: #059669; color: #FFFFFF !important; border: none;
    border-radius: 10px; font-weight: 600;
}
.stDownloadButton > button:hover { background-color: #047857; color: #FFFFFF !important; }
.blog-card {
    background-color: #FFFFFF; color: #1F2937; padding: 28px; border-radius: 14px;
    border: 1px solid #E5E7EB; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    line-height: 1.8; overflow-wrap: anywhere;
}
.blog-card h1, .blog-card h2, .blog-card h3 { color: #1D4ED8 !important; }
hr { border-color: #D1D5DB !important; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# APPLICATION HEADER
# -----------------------------------
st.title("✍️ AI Blog Writer")
st.markdown("""
Create high-quality blogs using Artificial Intelligence.

Enter your topic, choose a language and word length,
and generate your blog with Google Gemini AI.
""")
st.divider()

# -----------------------------------
# GEMINI CONFIGURATION
# Set GEMINI_API_KEY in Streamlit Cloud > App settings > Secrets
# -----------------------------------
def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "Gemini API key is missing. Add GEMINI_API_KEY in "
            "Streamlit Cloud > your app > Settings > Secrets."
        )
    return genai.Client(api_key=api_key)

# -----------------------------------
# BLOG GENERATION FUNCTION
# -----------------------------------
def generate_blog(topic, language, length, keywords):
    prompt = f"""
You are a professional blog writer and SEO expert.

Write a complete, useful, original and well-organized blog.

Topic: {topic}
Language: {language}
Requested length: {length}
SEO keywords: {keywords if keywords else "Choose relevant keywords"}

Requirements:
1. Start with an attractive title.
2. Write an engaging introduction.
3. Use clear headings and subheadings.
4. Explain the topic accurately and clearly.
5. Include practical examples when appropriate.
6. Add a conclusion.
7. Use SEO keywords naturally.
8. Avoid repetition and unnecessary content.
9. Do not invent statistics, facts or references.
10. Write the entire blog in the requested language.
11. Return the result in Markdown format.
12. Aim for the requested word count.

Write the complete blog now.
"""
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        blog = (response.text or "").strip()
        if not blog:
            return None, "Gemini returned an empty response. Please try again."
        return blog, None

    except RuntimeError as error:
        return None, str(error)
    except Exception as error:
        error_text = str(error)
        if "API_KEY_INVALID" in error_text or "invalid api key" in error_text.lower():
            return None, "Gemini API key is invalid. Check GEMINI_API_KEY in Streamlit Secrets."
        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            return None, "Gemini API quota/rate limit reached. Wait and try again, or check your API usage limits."
        return None, f"Could not generate the blog with Gemini: {error_text[:700]}"

# -----------------------------------
# BLOG INPUT FORM
# -----------------------------------
st.subheader("📝 Enter Blog Details")
with st.form("blog_form"):
    topic = st.text_input("Blog Topic", placeholder="Example: Artificial Intelligence")
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("Select Language", ["English", "Gujarati", "Hindi"])
    with col2:
        length = st.selectbox("Blog Length", ["Short (300 words)", "Medium (600 words)", "Long (1000 words)"])
    keywords = st.text_input("SEO Keywords (Optional)", placeholder="AI, technology, machine learning")
    submitted = st.form_submit_button("🚀 Generate Blog", use_container_width=True)

# -----------------------------------
# GENERATE BLOG
# -----------------------------------
if submitted:
    if not topic.strip():
        st.warning("Please enter a blog topic.")
    else:
        with st.spinner("✍️ Gemini AI is writing your blog. Please wait..."):
            blog_content, error_message = generate_blog(
                topic=topic.strip(),
                language=language,
                length=length,
                keywords=keywords.strip()
            )
        if error_message:
            st.error(error_message)
        else:
            st.session_state["generated_blog"] = blog_content
            st.session_state["blog_topic"] = topic.strip()

# -----------------------------------
# DISPLAY GENERATED BLOG
# -----------------------------------
if st.session_state.get("generated_blog"):
    st.divider()
    st.subheader("📄 Your Generated Blog")
    blog_content = st.session_state["generated_blog"]
    st.markdown('<div class="blog-card">', unsafe_allow_html=True)
    st.markdown(blog_content)
    st.markdown('</div>', unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Download Blog as TXT",
        data=blog_content,
        file_name="AI_Blog.txt",
        mime="text/plain",
        use_container_width=True
    )
    st.success("Your blog is ready!")

# -----------------------------------
# FOOTER
# -----------------------------------
st.divider()
st.caption("AI Blog Writer | Python + Streamlit + Google Gemini")
