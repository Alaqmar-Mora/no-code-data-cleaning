import streamlit as st
import pandas as pd

# --- Branding ---
st.set_page_config(page_title="No-Code Data Cleaner", page_icon="🧹", layout="wide")
st.title("🧹 No-Code Data Cleaning Platform")
st.markdown("Easily clean your datasets without writing a single line of code.")

# --- File Upload ---
uploaded_file = st.file_uploader("📂 Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Show raw preview
    st.subheader("📊 Raw Data Preview")
    st.dataframe(df.head(20), use_container_width=True)

    # Sidebar Cleaning Options
    st.sidebar.header("⚙️ Cleaning Options")

    if st.sidebar.button("Remove Duplicates"):
        df = df.drop_duplicates()
        st.sidebar.success("✅ Duplicates removed!")

    if st.sidebar.button("Drop Missing Values"):
        df = df.dropna()
        st.sidebar.success("✅ Missing values dropped!")

    if st.sidebar.button("Fill Missing with 0"):
        df = df.fillna(0)
        st.sidebar.success("✅ Missing values filled with 0!")

    if st.sidebar.button("Standardize Text (lowercase)"):
        df = df.applymap(lambda s: s.lower().strip() if type(s) == str else s)
        st.sidebar.success("✅ Text standardized!")

    if st.sidebar.button("Convert Dates (YYYY-MM-DD)"):
        for col in df.select_dtypes(include=['object']):
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore').dt.strftime('%Y-%m-%d')
            except:
                pass
        st.sidebar.success("✅ Dates standardized!")

    # Show cleaned preview
    st.subheader("🔍 Cleaned Data Preview")
    st.dataframe(df.head(20), use_container_width=True)

    # Download option
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Cleaned Data (CSV)",
        data=csv,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Upload a CSV or Excel file to get started.")
