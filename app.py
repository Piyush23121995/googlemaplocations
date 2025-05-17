import streamlit as st
import pandas as pd
import requests
import urllib.parse
from io import BytesIO

# --- CONFIG ---
st.set_page_config(page_title="Google Maps Link Generator", layout="centered")
st.title("📍 Google Maps URL Generator from Excel")
st.markdown("Upload an Excel file with a column of location names to get Google Maps URLs.")

# --- SIDEBAR API KEY INPUT ---
api_key = st.sidebar.text_input("🔑 Enter your Google Maps API Key", type="password")

# --- UPLOAD EXCEL FILE ---
uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file and api_key:
    df = pd.read_excel(uploaded_file)

    # Try to detect the column with location names
    st.subheader("📋 Preview of Uploaded File")
    st.write(df.head())

    location_column = st.selectbox("Select the column with location names:", df.columns)

    if st.button("Generate Google Maps URLs"):
        with st.spinner("🔍 Searching Google Maps..."):
            def get_maps_url(place_name):
                endpoint = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
                params = {
                    "input": place_name,
                    "inputtype": "textquery",
                    "fields": "place_id",
                    "key": api_key
                }
                response = requests.get(endpoint, params=params)
                data = response.json()
                if data.get("candidates"):
                    place_id = data["candidates"][0]["place_id"]
                    return f"https://www.google.com/maps/place/?q=place_id:{place_id}"
                else:
                    return "Not Found"

            df["Google Maps URL"] = df[location_column].apply(get_maps_url)

        st.success("✅ URLs Generated!")

        # Display result
        st.subheader("📍 Results")
        st.write(df)

        # Download Excel
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button(
            label="📥 Download Updated Excel",
            data=output.getvalue(),
            file_name="locations_with_google_maps.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif uploaded_file and not api_key:
    st.warning("🔐 Please enter your Google Maps API key in the sidebar to continue.")
