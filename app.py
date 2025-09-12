import streamlit as st
import pandas as pd
import io
from typing import Dict

# ------------------ Helper Functions ------------------
def safe_set_session_state(key, value):
    if key not in st.session_state or st.session_state[key] != value:
        st.session_state[key] = value

def safe_get_session_state(key, default=None):
    return st.session_state.get(key, default)

def init_session_state():
    defaults = {
        "users": {},
        "current_user": None,
        "user_data": {},
        "df": None,
        "cleaned_df": None,
        "show_settings": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ------------------ User Manager ------------------
class UserManager:
    def __init__(self):
        if "users" not in st.session_state:
            st.session_state["users"] = {}

    def register_user(self, username, password, plan="free"):
        if username in st.session_state["users"]:
            return False
        st.session_state["users"][username] = {
            "password": password,
            "plan": plan,
            "usage": {"files": 0, "operations": 0},
        }
        return True

    def authenticate_user(self, username, password):
        user = st.session_state["users"].get(username)
        if user and user["password"] == password:
            st.session_state["current_user"] = username
            return True
        return False

    def get_current_user(self):
        return st.session_state.get("current_user")

    def get_user_data(self, username):
        return st.session_state["users"].get(username)

    def update_usage(self, username, files=0, operations=0):
        if username in st.session_state["users"]:
            st.session_state["users"][username]["usage"]["files"] += files
            st.session_state["users"][username]["usage"]["operations"] += operations

    def get_plan_limits(self, plan):
        plans = {
            "free": {"files": 3, "operations": 10, "export_formats": ["csv"]},
            "pro": {"files": 100, "operations": 1000, "export_formats": ["csv", "excel", "json"]},
            "enterprise": {"files": 1000, "operations": 10000, "export_formats": ["csv", "excel", "json", "parquet"]},
        }
        return plans.get(plan, plans["free"])

# ------------------ Data Cleaner ------------------
class DataCleaner:
    def __init__(self, df):
        self.df = df.copy()

    def clean_missing(self, method="drop", fill_value=None):
        if method == "drop":
            self.df.dropna(inplace=True)
        elif method == "fill":
            self.df.fillna(fill_value, inplace=True)
        return self.df

    def remove_duplicates(self):
        self.df.drop_duplicates(inplace=True)
        return self.df

    def standardize_text(self, cols):
        for col in cols:
            if self.df[col].dtype == "object":
                self.df[col] = self.df[col].str.strip().str.lower()
        return self.df

    def fix_dates(self, cols, format=None):
        for col in cols:
            self.df[col] = pd.to_datetime(self.df[col], errors="coerce", format=format)
        return self.df

# ------------------ Render Tabs ------------------
def render_upload_tab(user_manager, user_data):
    st.markdown("### 📤 Upload Data")
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            if uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            safe_set_session_state("df", df)
            safe_set_session_state("cleaned_df", None)
            user_manager.update_usage(st.session_state["current_user"], files=1)

            st.success("✅ File uploaded successfully")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"❌ Error: {e}")

def render_clean_tab(cleaner, user_manager, user_data):
    st.markdown("### 🧹 Clean Data")
    df = safe_get_session_state("df", None)

    if df is None:
        st.info("Upload a file first")
        return

    cleaning_ops = []

    if st.checkbox("Remove Duplicates"):
        cleaning_ops.append("duplicates")

    if st.checkbox("Handle Missing Values"):
        method = st.radio("Method", ["drop", "fill"])
        fill_value = None
        if method == "fill":
            fill_value = st.text_input("Fill value")
        cleaning_ops.append(("missing", method, fill_value))

    if st.checkbox("Standardize Text Columns"):
        cols = st.multiselect("Columns", df.select_dtypes(include="object").columns.tolist())
        if cols:
            cleaning_ops.append(("text", cols))

    if st.checkbox("Fix Date Columns"):
        cols = st.multiselect("Date Columns", df.columns.tolist())
        if cols:
            cleaning_ops.append(("dates", cols))

    if st.button("Apply Cleaning"):
        cleaned_df = df.copy()
        cleaner = DataCleaner(cleaned_df)

        for op in cleaning_ops:
            if op == "duplicates":
                cleaned_df = cleaner.remove_duplicates()
            elif isinstance(op, tuple) and op[0] == "missing":
                _, method, fill_value = op
                cleaned_df = cleaner.clean_missing(method, fill_value)
            elif isinstance(op, tuple) and op[0] == "text":
                _, cols = op
                cleaned_df = cleaner.standardize_text(cols)
            elif isinstance(op, tuple) and op[0] == "dates":
                _, cols = op
                cleaned_df = cleaner.fix_dates(cols)

        safe_set_session_state("cleaned_df", cleaned_df)
        user_manager.update_usage(st.session_state["current_user"], operations=len(cleaning_ops))

        st.success("✅ Cleaning applied successfully")
        st.dataframe(cleaned_df.head())

def render_results_tab(user_manager, user_data):
    cleaned_df = safe_get_session_state("cleaned_df", None)
    if cleaned_df is None:
        st.info("🧹 Clean your data first")
        return

    st.markdown("### 📊 Results")
    st.dataframe(cleaned_df, use_container_width=True, height=400)

    st.markdown("### 📥 Download")
    plan_limits = user_manager.get_plan_limits(user_data["plan"])
    file_format = st.selectbox("Format", plan_limits["export_formats"])

    if file_format == "csv":
        csv_data = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ CSV", csv_data, "cleaned.csv", "text/csv")

    elif file_format == "excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            cleaned_df.to_excel(writer, index=False)
        st.download_button("⬇️ Excel", buffer.getvalue(), "cleaned.xlsx")

    elif file_format == "json":
        json_data = cleaned_df.to_json(orient="records")
        st.download_button("⬇️ JSON", json_data, "cleaned.json", "application/json")

    elif file_format == "parquet":
        buffer = io.BytesIO()
        cleaned_df.to_parquet(buffer, index=False)
        st.download_button("⬇️ Parquet", buffer.getvalue(), "cleaned.parquet")

def render_analytics_tab():
    st.markdown("### 📈 Analytics")
    cleaned_df = safe_get_session_state("cleaned_df", None)
    if cleaned_df is None:
        st.info("Upload and clean data first")
        return

    st.write("#### Data Types")
    st.write(cleaned_df.dtypes)

    st.write("#### Summary Stats")
    st.write(cleaned_df.describe(include='all'))

# ------------------ Auth Screens ------------------
def render_auth_screen(user_manager):
    st.markdown("## 🔐 No-Code Data Cleaner Pro")
    st.markdown("Your no-code SaaS for smarter data cleaning ✨")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if user_manager.authenticate_user(username, password):
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab_register:
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")
        plan = st.selectbox("Plan", ["free", "pro", "enterprise"])
        if st.button("Register"):
            if user_manager.register_user(username, password, plan):
                st.success("Registered successfully! Please login.")
            else:
                st.error("Username already exists")

# ------------------ Dashboard ------------------
def render_dashboard(user_manager):
    user = user_manager.get_current_user()
    if not user:
        return

    user_data = user_manager.get_user_data(user)
    st.sidebar.success(f"👋 Welcome {user} ({user_data['plan']})")
    if st.sidebar.button("Logout"):
        st.session_state["current_user"] = None
        st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📤 Upload", "🧹 Clean", "📊 Results", "💾 Templates", "📈 Analytics"])

    with tab1:
        render_upload_tab(user_manager, user_data)
    with tab2:
        render_clean_tab(DataCleaner, user_manager, user_data)
    with tab3:
        render_results_tab(user_manager, user_data)
    with tab4:
        st.info("Templates feature coming soon 🚀")
    with tab5:
        render_analytics_tab()

# ------------------ Main ------------------
def main():
    st.set_page_config(page_title="No-Code Data Cleaner Pro", layout="wide")
    init_session_state()
    user_manager = UserManager()

    if st.session_state.get("current_user"):
        render_dashboard(user_manager)
    else:
        render_auth_screen(user_manager)

if __name__ == "__main__":
    main()
