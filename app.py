
import streamlit as st
import requests

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

/* Main application background */
.stApp {
    background-color: #F4F7FB;
    color: #1F2937;
}

/* Main content area */
.main .block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Headings */
h1, h2, h3 {
    color: #172554 !important;
}

/* Normal text */
p, label, .stMarkdown {
    color: #1F2937;
}

/* Input fields and select boxes */
.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border-radius: 8px;
}

/* Text input placeholder */
.stTextInput input::placeholder {
    color: #6B7280 !important;
}

/* Main buttons */
.stButton > button {
    background-color: #2563EB;
    color: #FFFFFF !important;
    border: none;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background-color: #1D4ED8;
    color: #FFFFFF !important;
    border: none;
}

/* Download button */
.stDownloadButton > button {
    background-color: #059669;
    color: #FFFFFF !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
}

.stDownloadButton > button:hover {
    background-color: #047857;
    color: #FFFFFF !important;
}

/* Blog output card */
.blog-card {
    background-color: #FFFFFF;
    color: #1F2937;
    padding: 28px;
    border-radius: 14px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    line-height: 1.8;
    overflow-wrap: anywhere;
}

/* Blog headings */
.blog-card h1,
.blog-card h2,
.blog-card h3 {
    color: #1D4ED8 !important;
}

/* Divider */
hr {
    border-color: #D1D5DB !important;
}

/* Footer */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------------
# APPLICATION HEADER
# -----------------------------------

st.title("✍️ AI Blog Writer")

st.markdown("""
Create high-quality blogs using Artificial Intelligence.

Enter your topic, choose a language and word length,
and generate your blog with a local AI model.
""")

st.divider()


# -----------------------------------
# OLLAMA CONFIGURATION
# -----------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:1b"


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

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=600
        )

        response.raise_for_status()

        result = response.json()
        blog = result.get("response", "").strip()

        if not blog:
            return None, (
                "The AI returned an empty response. "
                "Please try again."
            )

        return blog, None

    except requests.exceptions.ConnectionError:
        return None, (
            "Cannot connect to Ollama.\n\n"
            "1. Make sure Ollama is installed.\n"
            "2. Open Command Prompt or terminal.\n"
            "3. Run: ollama serve\n"
            "4. Check the model using: ollama list"
        )

    except requests.exceptions.Timeout:
        return None, (
            "The AI model took too long to respond. "
            "Try again or check whether your computer "
            "has enough available memory."
        )

    except requests.exceptions.HTTPError as error:
        details = ""

        if error.response is not None:
            details = error.response.text[:1000]

        return None, (
            f"Ollama HTTP error: {error}\n\n{details}"
        )

    except (requests.exceptions.RequestException, ValueError) as error:
        return None, f"Could not generate the blog: {error}"


# -----------------------------------
# BLOG INPUT FORM
# -----------------------------------

st.subheader("📝 Enter Blog Details")

with st.form("blog_form"):

    topic = st.text_input(
        "Blog Topic",
        placeholder="Example: Artificial Intelligence"
    )

    col1, col2 = st.columns(2)

    with col1:
        language = st.selectbox(
            "Select Language",
            ["English", "Gujarati", "Hindi"]
        )

    with col2:
        length = st.selectbox(
            "Blog Length",
            [
                "Short (300 words)",
                "Medium (600 words)",
                "Long (1000 words)"
            ]
        )

    keywords = st.text_input(
        "SEO Keywords (Optional)",
        placeholder="AI, technology, machine learning"
    )

    submitted = st.form_submit_button(
        "🚀 Generate Blog",
        use_container_width=True
    )


# -----------------------------------
# GENERATE BLOG
# -----------------------------------

if submitted:

    if not topic.strip():
        st.warning("Please enter a blog topic.")

    else:
        with st.spinner(
            "✍️ AI is writing your blog. Please wait..."
        ):
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

    st.markdown(
        '<div class="blog-card">',
        unsafe_allow_html=True
    )

    st.markdown(blog_content)

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

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

st.caption(
    "AI Blog Writer | Python + Streamlit + Ollama"
)
