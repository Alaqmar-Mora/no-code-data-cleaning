import streamlit as st
import pandas as pd

st.title("🧹 No-Code Data Cleaning Prototype")

# Upload file
uploaded_file = st.file_uploader("Upload your CSV/Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📊 Preview of Data")
    st.dataframe(df.head())

    # Cleaning Options
    st.subheader("⚙️ Data Cleaning Options")

    if st.button("Remove Duplicates"):
        df = df.drop_duplicates()
        st.success("✅ Duplicates removed!")

    if st.button("Drop Missing Values"):
        df = df.dropna()
        st.success("✅ Missing values dropped!")

    if st.button("Fill Missing with 0"):
        df = df.fillna(0)
        st.success("✅ Missing values filled with 0!")

    if st.button("Lowercase Text"):
        df = df.applymap(lambda s: s.lower().strip() if type(s) == str else s)
        st.success("✅ Text standardized to lowercase!")

    st.subheader("🔍 Cleaned Data Preview")
    st.dataframe(df.head())

    # Download cleaned file
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Cleaned CSV", data=csv, file_name="cleaned_data.csv", mime="text/csv")
