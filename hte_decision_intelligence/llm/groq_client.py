import os
import json
import streamlit as st

try:
    from groq import Groq
    GROQ_SDK_AVAILABLE = True
except ImportError:
    GROQ_SDK_AVAILABLE = False

@st.cache_resource
def get_groq_client():
    """
    Initializes Groq client if API key is present in environment variables.
    """
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if GROQ_SDK_AVAILABLE and api_key:
        try:
            return Groq(api_key=api_key)
        except Exception as e:
            return None
    return None

def query_groq_llm(prompt, system_message="You are an expert HTE (Higher & Technical Education) AI Decision Analyst.", model="llama-3.3-70b-versatile", max_tokens=600):
    """
    Executes an LLM request via Groq API.
    Falls back gracefully if key or network is unavailable.
    """
    client = get_groq_client()
    if client is not None:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.sidebar.warning(f"Groq API call fallback: {str(e)[:60]}")
            return None
    return None
