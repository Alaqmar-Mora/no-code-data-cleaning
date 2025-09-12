import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
import io
import json
import hashlib
from typing import List, Dict, Any, Optional
import uuid

# Page configuration
st.set_page_config(
    page_title="No-Code Data Cleaner Pro",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional SaaS design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .success-banner {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
    }
    .pricing-card {
        background: white;
        border: 2px solid #e1e5e9;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem;
        text-align: center;
        position: relative;
        transition: all 0.3s;
    }
    .pricing-card:hover {
        border-color: #667eea;
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2);
    }
    .pricing-card.popular {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .pricing-card.popular::before {
        content: "MOST POPULAR";
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        background: #f5576c;
        color: white;
        padding: 5px 20px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .auth-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .usage-bar {
        background: #e1e5e9;
        height: 10px;
        border-radius: 5px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .usage-fill {
        height: 100%;
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        transition: width 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# User Management System
class UserManager:
    def __init__(self):
        if 'users' not in st.session_state:
            st.session_state.users = {}
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {}
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, plan: str = 'free') -> bool:
        if username in st.session_state.users:
            return False
        
        user_id = str(uuid.uuid4())
        st.session_state.users[username] = {
            'user_id': user_id,
            'email': email,
            'password_hash': self.hash_password(password),
            'plan': plan,
            'created_at': datetime.now().isoformat(),
            'usage': {
                'operations_this_month': 0,
                'file_size_used_mb': 0,
                'last_reset': datetime.now().replace(day=1).isoformat()
            },
            'cleaning_history': [],
            'saved_templates': {}
        }
        return True
    
    def authenticate(self, username: str, password: str) -> bool:
        if username in st.session_state.users:
            user = st.session_state.users[username]
            if user['password_hash'] == self.hash_password(password):
                st.session_state.current_user = username
                st.session_state.user_data = user
                return True
        return False
    
    def logout(self):
        st.session_state.current_user = None
        st.session_state.user_data = {}
    
    def get_plan_limits(self, plan: str) -> Dict[str, Any]:
        limits = {
            'free': {
                'max_file_size_mb': 5,
                'max_operations_per_month': 10,
                'export_formats': ['csv'],
                'features': ['Basic cleaning', 'CSV export only']
            },
            'pro': {
                'max_file_size_mb': 100,
                'max_operations_per_month': 1000,
                'export_formats': ['csv', 'excel', 'json'],
                'features': ['All cleaning operations', 'Multi-format export', 'Cleaning templates', 'Email support']
            },
            'enterprise': {
                'max_file_size_mb': float('inf'),
                'max_operations_per_month': float('inf'),
                'export_formats': ['csv', 'excel', 'json', 'parquet'],
                'features': ['Unlimited everything', 'Batch processing', 'API access', 'Priority support', 'Team collaboration']
            }
        }
        return limits.get(plan, limits['free'])
    
    def can_perform_operation(self, user_data: Dict, file_size_mb: float) -> tuple[bool, str]:
        plan_limits = self.get_plan_limits(user_data['plan'])
        
        # Check file size limit
        if file_size_mb > plan_limits['max_file_size_mb']:
            return False, f"File too large. {user_data['plan'].title()} plan limit: {plan_limits['max_file_size_mb']}MB"
        
        # Check monthly operations limit
        if user_data['usage']['operations_this_month'] >= plan_limits['max_operations_per_month']:
            return False, f"Monthly operations limit reached. {user_data['plan'].title()} plan limit: {plan_limits['max_operations_per_month']} operations"
        
        return True, ""
    
    def increment_usage(self, username: str, file_size_mb: float):
        if username in st.session_state.users:
            user = st.session_state.users[username]
            user['usage']['operations_this_month'] += 1
            user['usage']['file_size_used_mb'] += file_size_mb
            st.session_state.user_data = user

# Enhanced Data Cleaner with SaaS features
class DataCleanerPro:
    """Professional Data Cleaning Engine with SaaS Features"""
    
    def __init__(self):
        self.cleaning_operations = {
            'Remove Duplicates': self.remove_duplicates,
            'Handle Missing Values': self.handle_missing_values,
            'Standardize Text': self.standardize_text,
            'Fix Date Formats': self.fix_dates,
            'Remove Outliers': self.remove_outliers,
            'Trim Whitespace': self.trim_whitespace,
            'Convert Data Types': self.convert_data_types,
            'Remove Empty Rows': self.remove_empty_rows
        }
    
    # [Previous cleaning methods remain the same - keeping them for space]
    def remove_duplicates(self, df: pd.DataFrame, columns: List[str] = None, rows: List[int] = None) -> pd.DataFrame:
        if rows is not None:
            selected_df = df.iloc[rows]
            other_df = df.drop(df.index[rows])
            cleaned_selected = selected_df.drop_duplicates(subset=columns)
            return pd.concat([other_df, cleaned_selected]).sort_index()
        else:
            return df.drop_duplicates(subset=columns)
    
    def handle_missing_values(self, df: pd.DataFrame, columns: List[str] = None, 
                            rows: List[int] = None, method: str = 'drop') -> pd.DataFrame:
        working_df = df.copy()
        if columns is None:
            columns = df.columns.tolist()
        
        if rows is not None:
            mask = working_df.index.isin(rows)
            for col in columns:
                if col in working_df.columns:
                    if method == 'drop':
                        working_df = working_df.dropna(subset=[col])
                    elif method == 'forward_fill':
                        working_df.loc[mask, col] = working_df.loc[mask, col].fillna(method='ffill')
                    elif method == 'mean' and working_df[col].dtype in ['int64', 'float64']:
                        mean_val = working_df.loc[mask, col].mean()
                        working_df.loc[mask, col] = working_df.loc[mask, col].fillna(mean_val)
        else:
            for col in columns:
                if col in working_df.columns:
                    if method == 'drop':
                        working_df = working_df.dropna(subset=[col])
                    elif method == 'forward_fill':
                        working_df[col] = working_df[col].fillna(method='ffill')
                    elif method == 'mean' and working_df[col].dtype in ['int64', 'float64']:
                        working_df[col] = working_df[col].fillna(working_df[col].mean())
        
        return working_df
    
    def standardize_text(self, df: pd.DataFrame, columns: List[str] = None, 
                        rows: List[int] = None, operations: List[str] = None) -> pd.DataFrame:
        working_df = df.copy()
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns.tolist()
        if operations is None:
            operations = ['lowercase', 'trim']
        
        for col in columns:
            if col in working_df.columns and working_df[col].dtype == 'object':
                if rows is not None:
                    mask = working_df.index.isin(rows)
                    if 'lowercase' in operations:
                        working_df.loc[mask, col] = working_df.loc[mask, col].str.lower()
                    if 'trim' in operations:
                        working_df.loc[mask, col] = working_df.loc[mask, col].str.strip()
                else:
                    if 'lowercase' in operations:
                        working_df[col] = working_df[col].str.lower()
                    if 'trim' in operations:
                        working_df[col] = working_df[col].str.strip()
        return working_df
    
    def fix_dates(self, df: pd.DataFrame, columns: List[str] = None, 
                  rows: List[int] = None, target_format: str = '%Y-%m-%d') -> pd.DataFrame:
        working_df = df.copy()
        if columns is None:
            columns = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    sample = df[col].dropna().head(10)
                    if any(self._is_date_like(str(val)) for val in sample):
                        columns.append(col)
        
        for col in columns:
            if col in working_df.columns:
                if rows is not None:
                    mask = working_df.index.isin(rows)
                    working_df.loc[mask, col] = pd.to_datetime(
                        working_df.loc[mask, col], errors='coerce'
                    ).dt.strftime(target_format)
                else:
                    working_df[col] = pd.to_datetime(
                        working_df[col], errors='coerce'
                    ).dt.strftime(target_format)
        return working_df
    
    def _is_date_like(self, text: str) -> bool:
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
        ]
        return any(re.match(pattern, str(text)) for pattern in date_patterns)
    
    def remove_outliers(self, df: pd.DataFrame, columns: List[str] = None, 
                       rows: List[int] = None, method: str = 'iqr') -> pd.DataFrame:
        working_df = df.copy()
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            if col in working_df.columns and working_df[col].dtype in ['int64', 'float64']:
                if rows is not None:
                    data = working_df.loc[working_df.index.isin(rows), col]
                else:
                    data = working_df[col]
                
                if method == 'iqr':
                    Q1 = data.quantile(0.25)
                    Q3 = data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outlier_mask = (data < lower_bound) | (data > upper_bound)
                
                if rows is not None:
                    row_indices = working_df.index[working_df.index.isin(rows)]
                    outlier_indices = row_indices[outlier_mask]
                else:
                    outlier_indices = working_df.index[outlier_mask]
                
                working_df = working_df.drop(outlier_indices)
        return working_df
    
    def trim_whitespace(self, df: pd.DataFrame, columns: List[str] = None, 
                       rows: List[int] = None) -> pd.DataFrame:
        working_df = df.copy()
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns.tolist()
        
        for col in columns:
            if col in working_df.columns and working_df[col].dtype == 'object':
                if rows is not None:
                    mask = working_df.index.isin(rows)
                    working_df.loc[mask, col] = working_df.loc[mask, col].str.strip()
                else:
                    working_df[col] = working_df[col].str.strip()
        return working_df
    
    def convert_data_types(self, df: pd.DataFrame, conversions: Dict[str, str], 
                          rows: List[int] = None) -> pd.DataFrame:
        working_df = df.copy()
        for col, target_type in conversions.items():
            if col in working_df.columns:
                try:
                    if rows is not None:
                        mask = working_df.index.isin(rows)
                        if target_type == 'numeric':
                            working_df.loc[mask, col] = pd.to_numeric(working_df.loc[mask, col], errors='coerce')
                    else:
                        if target_type == 'numeric':
                            working_df[col] = pd.to_numeric(working_df[col], errors='coerce')
                except Exception as e:
                    st.warning(f"Could not convert {col} to {target_type}: {str(e)}")
        return working_df
    
    def remove_empty_rows(self, df: pd.DataFrame, rows: List[int] = None) -> pd.DataFrame:
        if rows is not None:
            selected_rows = df.iloc[rows]
            other_rows = df.drop(df.index[rows])
            cleaned_selected = selected_rows.dropna(how='all')
            return pd.concat([other_rows, cleaned_selected]).sort_index()
        else:
            return df.dropna(how='all')
    
    def save_cleaning_template(self, template_name: str, operations: Dict, user_data: Dict) -> bool:
        """Save cleaning operations as a reusable template"""
        if 'saved_templates' not in user_data:
            user_data['saved_templates'] = {}
        
        user_data['saved_templates'][template_name] = {
            'operations': operations,
            'created_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        return True

def render_authentication():
    """Render login/signup interface"""
    user_manager = UserManager()
    
    st.markdown("""
    <div class="auth-container">
        <h2 style="text-align: center; color: #667eea;">Welcome to Data Cleaner Pro</h2>
        <p style="text-align: center; color: #666;">Sign in to unlock powerful data cleaning features</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            st.markdown("### Sign In")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                if user_manager.authenticate(username, password):
                    st.success("✅ Welcome back!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
    
    with tab2:
        with st.form("signup_form"):
            st.markdown("### Create Account")
            new_username = st.text_input("Choose Username")
            email = st.text_input("Email Address")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            plan = st.selectbox("Choose Plan", ["free", "pro", "enterprise"])
            
            # Show plan details
            user_manager_temp = UserManager()
            plan_details = user_manager_temp.get_plan_limits(plan)
            st.info(f"**{plan.title()} Plan**: {plan_details['max_file_size_mb']}MB files, {plan_details['max_operations_per_month']} operations/month")
            
            submit = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit:
                if new_password != confirm_password:
                    st.error("❌ Passwords don't match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif user_manager.create_user(new_username, email, new_password, plan):
                    st.success("✅ Account created! Please sign in.")
                else:
                    st.error("❌ Username already exists")

def render_dashboard():
    """Render user dashboard with usage stats"""
    # Ensure session state is initialized
    init_session_state()
    
    # Safety check for user data
    if not st.session_state.current_user or not st.session_state.user_data:
        st.error("❌ Session expired. Please sign in again.")
        st.session_state.current_user = None
        st.session_state.user_data = {}
        st.rerun()
        return
    
    user_data = st.session_state.user_data
    user_manager = UserManager()
    
    # Additional safety check for plan limits
    try:
        plan_limits = user_manager.get_plan_limits(user_data.get('plan', 'free'))
    except Exception as e:
        st.error(f"Error loading plan data: {e}")
        return
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### Welcome back, **{st.session_state.current_user}**! 👋")
        st.markdown(f"**Plan:** {user_data['plan'].title()} | **Member since:** {user_data['created_at'][:10]}")
    
    with col2:
        if st.button("⚙️ Account Settings", use_container_width=True):
            st.session_state.show_settings = True
    
    with col3:
        if st.button("🚪 Sign Out", use_container_width=True):
            user_manager.logout()
            st.rerun()
    
    # Usage statistics
    st.markdown("### 📊 Your Usage This Month")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        operations_used = user_data['usage']['operations_this_month']
        operations_limit = plan_limits['max_operations_per_month']
        operations_pct = (operations_used / operations_limit * 100) if operations_limit != float('inf') else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>{operations_used:,}</h3>
            <p>Operations Used</p>
            <div class="usage-bar">
                <div class="usage-fill" style="width: {min(operations_pct, 100)}%"></div>
            </div>
            <small>{operations_limit if operations_limit != float('inf') else '∞'} limit</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        file_size_used = user_data['usage']['file_size_used_mb']
        st.markdown(f"""
        <div class="metric-card">
            <h3>{file_size_used:.1f} MB</h3>
            <p>Data Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        templates_count = len(user_data.get('saved_templates', {}))
        st.markdown(f"""
        <div class="metric-card">
            <h3>{templates_count}</h3>
            <p>Saved Templates</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Upgrade prompt for free users
    if user_data['plan'] == 'free' and operations_used >= operations_limit * 0.8:
        st.markdown("""
        <div class="feature-card" style="border-left-color: #f5576c;">
            <h4>🚀 You're almost at your limit!</h4>
            <p>Upgrade to Pro for unlimited operations and advanced features.</p>
        </div>
        """, unsafe_allow_html=True)

def render_pricing():
    """Render pricing plans"""
    st.markdown("### 💎 Choose Your Plan")
    
    current_user = safe_get_session_state('current_user', None)
    user_data = safe_get_session_state('user_data', {})
    users = safe_get_session_state('users', {})
    
    col1, col2, col3 = st.columns(3)
    
    # Free Plan
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3>🆓 Free</h3>
            <h2>$0<small>/month</small></h2>
            <ul style="text-align: left;">
                <li>5 MB file limit</li>
                <li>10 operations/month</li>
                <li>CSV export only</li>
                <li>Basic cleaning tools</li>
                <li>Community support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Current Plan" if user_data.get('plan') == 'free' else "Downgrade", key="free_plan", disabled=True):
            pass
    
    # Pro Plan
    with col2:
        st.markdown("""
        <div class="pricing-card popular">
            <h3>💼 Pro</h3>
            <h2>$19<small>/month</small></h2>
            <ul style="text-align: left;">
                <li>100 MB file limit</li>
                <li>1,000 operations/month</li>
                <li>Multi-format export</li>
                <li>All cleaning tools</li>
                <li>Cleaning templates</li>
                <li>Email support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upgrade to Pro" if user_data.get('plan') != 'pro' else "Current Plan", key="pro_plan"):
            if user_data.get('plan') != 'pro' and current_user and current_user in users:
                users[current_user]['plan'] = 'pro'
                user_data['plan'] = 'pro'
                safe_set_session_state('users', users)
                safe_set_session_state('user_data', user_data)
                st.success("🎉 Upgraded to Pro! (Demo mode)")
                st.rerun()
    
    # Enterprise Plan
    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3>🏢 Enterprise</h3>
            <h2>$99<small>/month</small></h2>
            <ul style="text-align: left;">
                <li>Unlimited file size</li>
                <li>Unlimited operations</li>
                <li>All export formats</li>
                <li>Batch processing</li>
                <li>API access</li>
                <li>Priority support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upgrade to Enterprise" if user_data.get('plan') != 'enterprise' else "Current Plan", key="enterprise_plan"):
            if user_data.get('plan') != 'enterprise' and current_user and current_user in users:
                users[current_user]['plan'] = 'enterprise'
                user_data['plan'] = 'enterprise'
                safe_set_session_state('users', users)
                safe_set_session_state('user_data', user_data)
                st.success("🎉 Upgraded to Enterprise! (Demo mode)")
                st.rerun()

def main():
    """Main application with authentication"""
    
    # Initialize session state
    if 'show_settings' not in st.session_state:
        st.session_state.show_settings = False
    
    # Check if user is logged in
    if safe_get_session_state('current_user', None) is None:
        # Show landing page with authentication
        st.markdown("""
        <div class="main-header">
            <h1>🧹 No-Code Data Cleaner Pro</h1>
            <p>Professional data cleaning platform with selective column and row processing</p>
            <p><strong>Join 1000+ data professionals cleaning their data efficiently</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        render_authentication()
        
        # Show features preview
        st.markdown("### 🚀 What You Get")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>🎯 Selective Cleaning</h4>
                <p>Choose exactly which columns and rows to process</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>📊 Multi-Format Support</h4>
                <p>CSV, Excel, JSON exports with professional formatting</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4>⚡ 8+ Cleaning Operations</h4>
                <p>From duplicates to outliers, standardization to type conversion</p>
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # User is logged in - show main app
    user_data = st.session_state.user_data
    user_manager = UserManager()
    cleaner = DataCleanerPro()
    
    # Initialize data storage
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'cleaned_df' not in st.session_state:
        st.session_state.cleaned_df = None
    
    # Main navigation
    if st.session_state.show_settings:
        st.markdown("### ⚙️ Account Settings")
        render_pricing()
        if st.button("← Back to Data Cleaner"):
            st.session_state.show_settings = False
            st.rerun()
        return
    
    # Dashboard
    render_dashboard()
    
    # Main application tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 Upload Data", "🧹 Clean Data", "📊 Results", "📋 Templates", "📈 Analytics"])
    
    with tab1:
        render_upload_tab(user_manager, user_data)
def render_upload_tab(user_manager, user_data):
    """Render the upload data tab"""
    st.markdown("### 📁 Upload Your Data")
    
    # Plan-based file upload
    plan_limits = user_manager.get_plan_limits(user_data.get('plan', 'free'))
    st.info(f"**{user_data.get('plan', 'free').title()} Plan**: Max file size {plan_limits['max_file_size_mb']}MB")
    
    uploaded_file = st.file_uploader(
        "Choose your data file",
        type=['csv', 'xlsx', 'xls'],
        help=f"Upload files up to {plan_limits['max_file_size_mb']}MB"
    )
    
    if uploaded_file is not None:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        # Check if user can upload this file
        can_upload, message = user_manager.can_perform_operation(user_data, file_size_mb)
        
        if not can_upload:
            st.error(f"❌ {message}")
            if user_data.get('plan') == 'free':
                st.markdown("**🚀 Upgrade to Pro** for 100MB files and 1000 operations per month!")
                if st.button("Upgrade Now", type="primary"):
                    safe_set_session_state('show_settings', True)
                    st.rerun()
            return
        
        try:
            # Load file based on type
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
            
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                try:
                    excel_file = pd.ExcelFile(uploaded_file)
                    if len(excel_file.sheet_names) > 1:
                        selected_sheet = st.selectbox("Choose sheet:", excel_file.sheet_names)
                        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    # Clean Excel artifacts
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                    
                except ImportError:
                    st.error("❌ Excel support not available. Install: pip install openpyxl xlrd")
                    st.info("💡 Convert to CSV and upload instead!")
                    return
            
            # Store in session state safely
            safe_set_session_state('df', df)
            
            # Success - show file info
            st.success("✅ File loaded successfully!")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", f"{len(df):,}")
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Size", f"{file_size_mb:.1f} MB")
            
            st.dataframe(df.head(10), use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")

def render_clean_tab(cleaner, user_manager, user_data):
    """Render the data cleaning tab"""
    df = safe_get_session_state('df', None)
    if df is None:
        st.info("👆 Please upload a file first in the Upload Data tab")
        return
    
    st.markdown("### 🧹 Selective Data Cleaning")
    
    # Column selection
    st.markdown("#### 📊 Choose Columns")
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to clean (leave empty for all):",
        options=all_columns
    )
    
    # Basic cleaning operations
    st.markdown("#### 🛠️ Select Operations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Basic Operations:**")
        remove_duplicates = st.checkbox("Remove Duplicates")
        handle_missing = st.checkbox("Handle Missing Values")
        trim_whitespace = st.checkbox("Trim Whitespace")
    
    with col2:
        st.markdown("**Advanced Operations:**")
        standardize_text = st.checkbox("Standardize Text")
        fix_dates = st.checkbox("Fix Dates")
        remove_outliers = st.checkbox("Remove Outliers")
    
    # Apply cleaning
    if st.button("🧹 Clean Data", type="primary"):
        # Check operation limits
        can_clean, message = user_manager.can_perform_operation(user_data, 0)
        if not can_clean:
            st.error(f"❌ {message}")
            return
        
        try:
            working_df = df.copy()
            operations_applied = []
            
            with st.spinner("Cleaning your data..."):
                if remove_duplicates:
                    working_df = cleaner.remove_duplicates(working_df, selected_columns)
                    operations_applied.append("Removed duplicates")
                
                if handle_missing:
                    working_df = cleaner.handle_missing_values(working_df, selected_columns)
                    operations_applied.append("Handled missing values")
                
                if trim_whitespace:
                    working_df = cleaner.trim_whitespace(working_df, selected_columns)
                    operations_applied.append("Trimmed whitespace")
            
            # Store cleaned data
            safe_set_session_state('cleaned_df', working_df)
            
            # Update usage
            current_user = safe_get_session_state('current_user')
            if current_user:
                user_manager.increment_usage(current_user, 1.0)  # Simplified usage tracking
            
            st.success(f"✅ Data cleaned! Applied {len(operations_applied)} operations.")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Cleaning error: {str(e)}")

def render_results_tab(user_manager, user_data):
    """Render the results tab"""
    cleaned_df = safe_get_session_state('cleaned_df', None)
    if cleaned_df is None:
        st.info("🧹 Clean your data first to see results here")
        return
    
    st.markdown("### 📊 Cleaning Results")
    st.dataframe(cleaned_df, use_container_width=True, height=400)
    
    # Download options
    st.markdown("### 📥 Download Cleaned Data")
    csv_data = cleaned_df.to_csv(index=False)
    st.download_button(
        "📥 Download CSV",
        csv_data,
        f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        use_container_width=True,
        type="primary"
    )

def render_templates_tab(user_data):
    """Render the templates tab"""
    st.markdown("### 📋 Cleaning Templates")
    
    if user_data.get('plan') == 'free':
        st.info("🚀 Upgrade to Pro to save and reuse cleaning templates!")
        return
    
    st.info("💾 Template features coming soon in next update!")

def render_analytics_tab(user_data):
    """Render the analytics tab"""
    st.markdown("### 📈 Analytics & History")
    
    # Show basic usage stats
    usage = user_data.get('usage', {})
    operations_count = usage.get('operations_this_month', 0)
    
    if operations_count > 0:
        st.metric("Operations This Month", operations_count)
        st.info("📊 Detailed analytics coming in next update!")
    else:
        st.info("📊 No operations performed yet. Start cleaning data to see analytics!")
        if st.session_state.df is None:
            st.info("👆 Please upload a file first in the Upload Data tab")
            return
        
        st.markdown("### 🧹 Selective Data Cleaning")
        
        # Column selection
        st.markdown("#### 📊 Choose Columns")
        all_columns = st.session_state.df.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to clean (leave empty for all):",
            options=all_columns
        )
        
        # Row selection
        st.markdown("#### 📄 Choose Rows")
        row_selection = st.radio(
            "Row selection method:",
            ["All Rows", "Row Range", "Specific Rows", "Conditional"]
        )
        
        selected_rows = None
        if row_selection == "Row Range":
            col1, col2 = st.columns(2)
            with col1:
                start_row = st.number_input("Start row", 0, len(st.session_state.df)-1, 0)
            with col2:
                end_row = st.number_input("End row", 0, len(st.session_state.df)-1, min(99, len(st.session_state.df)-1))
            selected_rows = list(range(int(start_row), int(end_row) + 1))
        
        elif row_selection == "Specific Rows":
            row_input = st.text_input("Row numbers (comma-separated):", help="e.g., 0,5,10,15")
            if row_input:
                try:
                    selected_rows = [int(x.strip()) for x in row_input.split(',') if x.strip().isdigit()]
                    selected_rows = [r for r in selected_rows if 0 <= r < len(st.session_state.df)]
                except:
                    st.error("Please enter valid row numbers")
        
        # Cleaning operations
        st.markdown("#### 🛠️ Select Operations")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Operations:**")
            remove_duplicates = st.checkbox("Remove Duplicates")
            handle_missing = st.checkbox("Handle Missing Values")
            trim_whitespace = st.checkbox("Trim Whitespace")
            remove_empty = st.checkbox("Remove Empty Rows")
        
        with col2:
            st.markdown("**Advanced Operations:**")
            standardize_text = st.checkbox("Standardize Text")
            fix_dates = st.checkbox("Fix Dates")
            remove_outliers = st.checkbox("Remove Outliers")
            convert_types = st.checkbox("Convert Data Types")
        
        # Operation settings
        if handle_missing:
            missing_method = st.selectbox("Missing values method:", 
                                        ["drop", "forward_fill", "mean", "median"])
        
        if standardize_text:
            text_ops = st.multiselect("Text operations:", 
                                    ["lowercase", "uppercase", "trim"], 
                                    default=["lowercase", "trim"])
        
        # Template saving (Pro+ feature)
        if user_data['plan'] in ['pro', 'enterprise']:
            st.markdown("#### 💾 Save as Template")
            template_name = st.text_input("Template name (optional):")
        
        # Apply cleaning
        if st.button("🧹 Clean Data", type="primary"):
            # Check operation limits
            can_clean, message = user_manager.can_perform_operation(user_data, 0)  # Size already checked
            if not can_clean:
                st.error(f"❌ {message}")
                return
            
            try:
                working_df = st.session_state.df.copy()
                operations_applied = []
                
                with st.spinner("Cleaning your data..."):
                    if remove_duplicates:
                        working_df = cleaner.remove_duplicates(working_df, selected_columns, selected_rows)
                        operations_applied.append("Removed duplicates")
                    
                    if handle_missing:
                        working_df = cleaner.handle_missing_values(working_df, selected_columns, selected_rows, missing_method)
                        operations_applied.append(f"Handled missing values ({missing_method})")
                    
                    if trim_whitespace:
                        working_df = cleaner.trim_whitespace(working_df, selected_columns, selected_rows)
                        operations_applied.append("Trimmed whitespace")
                    
                    if remove_empty:
                        working_df = cleaner.remove_empty_rows(working_df, selected_rows)
                        operations_applied.append("Removed empty rows")
                    
                    if standardize_text:
                        working_df = cleaner.standardize_text(working_df, selected_columns, selected_rows, text_ops)
                        operations_applied.append("Standardized text")
                    
                    if fix_dates:
                        working_df = cleaner.fix_dates(working_df, selected_columns, selected_rows)
                        operations_applied.append("Fixed dates")
                    
                    if remove_outliers:
                        working_df = cleaner.remove_outliers(working_df, selected_columns, selected_rows)
                        operations_applied.append("Removed outliers")
                
                # Update usage
                file_size_mb = len(st.session_state.df.to_csv().encode()) / (1024 * 1024)
                user_manager.increment_usage(st.session_state.current_user, file_size_mb)
                
                st.session_state.cleaned_df = working_df
                
                # Save to history
                cleaning_record = {
                    'timestamp': datetime.now().isoformat(),
                    'operations': operations_applied,
                    'original_shape': st.session_state.df.shape,
                    'cleaned_shape': working_df.shape,
                    'columns_affected': selected_columns or 'All columns',
                    'rows_affected': len(selected_rows) if selected_rows else 'All rows'
                }
                st.session_state.users[st.session_state.current_user]['cleaning_history'].append(cleaning_record)
                
                # Save template if requested
                if user_data['plan'] in ['pro', 'enterprise'] and template_name:
                    template_ops = {
                        'remove_duplicates': remove_duplicates,
                        'handle_missing': handle_missing,
                        'missing_method': missing_method if handle_missing else None,
                        'trim_whitespace': trim_whitespace,
                        'standardize_text': standardize_text,
                        'text_operations': text_ops if standardize_text else None
                    }
                    cleaner.save_cleaning_template(template_name, template_ops, user_data)
                    st.success(f"💾 Template '{template_name}' saved!")
                
                st.markdown("""
                <div class="success-banner">
                    <h3>✅ Data Cleaned Successfully!</h3>
                    <p>Applied {} operations. Check the Results tab!</p>
                </div>
                """.format(len(operations_applied)), unsafe_allow_html=True)
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Cleaning error: {str(e)}")
    
    with tab3:
        if st.session_state.cleaned_df is None:
            st.info("🧹 Clean your data first to see results here")
            return
        
        st.markdown("### 📊 Cleaning Results")
        
        # Before/After comparison
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📋 Before:**")
            st.metric("Rows", f"{len(st.session_state.df):,}")
            st.metric("Missing Values", st.session_state.df.isnull().sum().sum())
        
        with col2:
            st.markdown("**✨ After:**")
            st.metric("Rows", f"{len(st.session_state.cleaned_df):,}")
            st.metric("Missing Values", st.session_state.cleaned_df.isnull().sum().sum())
        
        st.dataframe(st.session_state.cleaned_df, use_container_width=True, height=400)
        
        # Downloads based on plan
        st.markdown("### 📥 Download Cleaned Data")
        plan_limits = user_manager.get_plan_limits(user_data['plan'])
        export_formats = plan_limits['export_formats']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'csv' in export_formats:
                csv_data = st.session_state.cleaned_df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv_data,
                    f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv",
                    use_container_width=True
                )
        
        with col2:
            if 'excel' in export_formats:
                try:
                    def create_excel():
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            st.session_state.cleaned_df.to_excel(writer, sheet_name='Cleaned_Data', index=False)
                            
                            # Summary sheet
                            summary = pd.DataFrame({
                                'Metric': ['Original Rows', 'Cleaned Rows', 'Rows Removed'],
                                'Value': [
                                    len(st.session_state.df),
                                    len(st.session_state.cleaned_df),
                                    len(st.session_state.df) - len(st.session_state.cleaned_df)
                                ]
                            })
                            summary.to_excel(writer, sheet_name='Summary', index=False)
                        return output.getvalue()
                    
                    excel_data = create_excel()
                    st.download_button(
                        "📊 Download Excel",
                        excel_data,
                        f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except ImportError:
                    st.button("📊 Excel (Install openpyxl)", disabled=True, use_container_width=True)
            else:
                st.button("📊 Excel (Pro+)", disabled=True, help="Upgrade to Pro for Excel export", use_container_width=True)
        
        with col3:
            if 'json' in export_formats:
                json_data = st.session_state.cleaned_df.to_json(orient='records', indent=2)
                st.download_button(
                    "🔗 Download JSON",
                    json_data,
                    f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json",
                    use_container_width=True
                )
            else:
                st.button("🔗 JSON (Pro+)", disabled=True, help="Upgrade to Pro for JSON export", use_container_width=True)
    
    with tab4:
        st.markdown("### 📋 Cleaning Templates")
        
        if user_data['plan'] == 'free':
            st.info("🚀 Upgrade to Pro to save and reuse cleaning templates!")
            if st.button("Upgrade to Pro"):
                st.session_state.show_settings = True
                st.rerun()
            return
        
        saved_templates = user_data.get('saved_templates', {})
        
        if saved_templates:
            st.markdown("#### 💾 Your Saved Templates")
            for name, template in saved_templates.items():
                with st.expander(f"📝 {name}"):
                    st.markdown(f"**Created:** {template['created_at'][:10]}")
                    st.markdown(f"**Used:** {template['usage_count']} times")
                    st.json(template['operations'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Apply {name}", key=f"apply_{name}"):
                            st.info("Template application feature coming soon!")
                    with col2:
                        if st.button(f"Delete {name}", key=f"delete_{name}"):
                            del user_data['saved_templates'][name]
                            st.success(f"Template '{name}' deleted!")
                            st.rerun()
        else:
            st.info("💾 No templates saved yet. Create templates while cleaning data!")
    
    with tab5:
        st.markdown("### 📈 Analytics & History")
        
        cleaning_history = user_data.get('cleaning_history', [])
        
        if cleaning_history:
            st.markdown(f"#### 📊 Cleaning History ({len(cleaning_history)} operations)")
            
            # Recent operations
            for i, record in enumerate(reversed(cleaning_history[-10:]), 1):  # Show last 10
                with st.expander(f"Operation {len(cleaning_history) - i + 1} - {record['timestamp'][:10]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Operations:** {', '.join(record['operations'])}")
                        st.markdown(f"**Columns:** {record['columns_affected']}")
                    with col2:
                        st.markdown(f"**Original Shape:** {record['original_shape']}")
                        st.markdown(f"**Final Shape:** {record['cleaned_shape']}")
                        st.markdown(f"**Rows Affected:** {record['rows_affected']}")
            
            # Usage analytics
            st.markdown("#### 📊 Usage Analytics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Operations", len(cleaning_history))
                st.metric("This Month", user_data['usage']['operations_this_month'])
            
            with col2:
                st.metric("Data Processed", f"{user_data['usage']['file_size_used_mb']:.1f} MB")
                st.metric("Templates Saved", len(saved_templates))
        
        else:
            st.info("📊 No operations performed yet. Start cleaning data to see analytics!")

if __name__ == "__main__":
    main()


