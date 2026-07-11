from google import genai
import streamlit as st

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

prompt = "Hello, how are you?"

interaction = client.interactions.create(
    model="gemini-3.5-flash",
    messages=[{"role": "user", "content": prompt}]
)
print(interaction.output_text)