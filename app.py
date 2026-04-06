import pandas as pd
import streamlit as st

from detector.features import extract_features
from detector.scoring import compute_ai_score


def classify_score(score: int) -> tuple[str, str]:
    if score <= 40:
        return "Seperti Manusia", "success"
    if score <= 70:
        return "Manusia dan Ai", "warning"
    return "Seperti buatan AI", "error"


st.set_page_config(page_title="Pendeteksi Code Buatan AI", page_icon="AI")

st.title("Pendeteksi Code Buatan AI")
st.markdown(
    """
Hey.....
Kalian yang ada disana.... Iyaaa KALIAN, Siapin ya... PBL Kalian, ini aku punya teman untuk bantu cek
karya kalian, apakah karya kalian itu buatan AI atau buatan manusia. Tapi ingat ya, perjanjian kita dibawah 10%, HARUS!!!

**Disclaimer:** It use as supporting evidence only.
"""
)

uploaded_file = st.file_uploader("Upload a Python, PHP, or Dart file", type=["py", "php", "dart"])

if uploaded_file is not None:
    code = uploaded_file.read().decode("utf-8", errors="ignore")
    features = extract_features(code, uploaded_file.name)
    score, details = compute_ai_score(features)
    classification, color = classify_score(score)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("AI Likelihood Score", f"{score}%")
        st.progress(score / 100)

    with col2:
        st.metric("Detected Language", features["language"].upper())
        if color == "success":
            st.success(classification)
        elif color == "warning":
            st.warning(classification)
        else:
            st.error(classification)

    st.subheader("Feature Breakdown")
    df = pd.DataFrame(list(details.items()), columns=["Feature", "Contribution"])
    st.table(df)

    st.subheader("Raw Extracted Features")
    st.json(features)

    st.markdown("---")
    if features["language"] == "php":
        st.caption(
            "PHP analysis emphasizes AI-style explanatory comments, placeholder/demo text, "
            "single-file full-stack patterns, and overly generic naming."
        )
    elif features["language"] == "dart":
        st.caption(
            "Dart/Flutter analysis emphasizes AI-style explanatory comments, placeholder UI text, "
            "large monolithic widget trees, and boilerplate-heavy widget structure."
        )
    else:
        st.caption(
            "Python analysis emphasizes comment behavior, AST structure, docstrings, "
            "exception density, and formatting compactness."
        )
