import streamlit as st
import pandas as pd
from openai import OpenAI
from streamlit_gsheets import GSheetsConnection
import base64

st.set_page_config(page_title="Receipt Scanner", layout="centered")
st.title("🧾 Smart Receipt Scanner")

# Initialize OpenAI & GSheets
# You need an OPENAI_API_KEY in your secrets.toml
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
conn = st.connection("gsheets", type=GSheetsConnection)

def encode_image(file):
    return base64.b64encode(file.read()).decode('utf-8')

uploaded_files = st.file_uploader("Upload Receipts", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if uploaded_files and st.button("🚀 Process & Save"):
    all_records = []
    for uploaded_file in uploaded_files:
        with st.spinner(f"AI reading {uploaded_file.name}..."):
            base64_image = encode_image(uploaded_file)
            
            # Send to GPT-4o-mini
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract: Shop Name, Date, Total Price (number only), and Currency. Format as: Shop|Date|Total|Currency"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }]
            )
            
            # Simple text parsing of the AI's response
            data = response.choices[0].message.content.split("|")
            all_records.append({
                "Shop Name": data[0],
                "Date": data[1],
                "Total Price": float(data[2]) if data[2] else 0.0,
                "Currency": data[3]
            })

    if all_records:
        new_df = pd.DataFrame(all_records)
        st.dataframe(new_df)
        # Update GSheets
        existing_df = conn.read(ttl=0)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        conn.update(data=updated_df)
        st.success("✅ Saved to Google Sheets!")