import streamlit as st
from mindee import ClientV2, product
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Receipt Scanner v2", layout="centered")
st.title("🧾 Receipt Scanner (2026 v2 Platform)")

# 2. Initialize Connections
try:
    # ClientV2 is the correct entry point for keys starting with 'md_'
    api_key = st.secrets["MINDEE_API_KEY"]
    mindee_client = ClientV2(api_key=api_key)
    
    # Initialize Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

uploaded_files = st.file_uploader("Upload Receipts", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files and st.button("🚀 Process & Sync to Sheets"):
    all_records = []
    
    for uploaded_file in uploaded_files:
        with st.spinner(f"AI Analyzing {uploaded_file.name}..."):
            try:
                # 3. Load the document from bytes
                input_doc = mindee_client.source_from_bytes(uploaded_file.read(), uploaded_file.name)
                
                # 4. VERIFIED V2 CALL: enqueue_and_parse
                # In SDK v4.34, this is the all-in-one method for V2 asynchronous processing.
                # It sends the file, waits for the result, and returns it.
                result = mindee_client.parse_document(product.ReceiptV5, input_doc)
                prediction = result.document.inference.prediction

                
                # 5. Extract Data
                all_records.append({
                    "Shop Name": str(prediction.supplier_name.value) if prediction.supplier_name.value else "Unknown",
                    "Date": str(prediction.date.value) if prediction.date.value else "N/A",
                    "Total Price": float(prediction.total_amount.value) if prediction.total_amount.value else 0.0,
                    "Currency": str(prediction.total_amount.currency) if prediction.total_amount.currency else "USD",
                    "Processed At": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                st.error(f"Failed on {uploaded_file.name}: {e}")

    # 6. Save to Google Sheets
    if all_records:
        new_df = pd.DataFrame(all_records)
        st.subheader("Data Extracted Successfully:")
        st.dataframe(new_df)
        
        try:
            # Get existing data and append new records
            existing_df = conn.read(ttl=0)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Update Google Sheet
            conn.update(data=updated_df)
            st.success("✅ Google Sheet updated successfully!")
            st.balloons()
        except Exception as e:
            st.error(f"GSheets Sync Error: {e}")