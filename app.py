import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import uuid
import io
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Page Configuration
st.set_page_config(
    page_title="No-Code Data Cleaner Pro",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# BULLETPROOF Session State Initialization
def initialize_app():
    """Initialize all session state variables safely"""
    defaults = {
        'authenticated': False,
        'current_user': '',
        'user_database': {},
        'user_profile': {},
        'uploaded_data': None,
        'cleaned_data': None,
        'current_page': 'auth',
        'app_initialized': True
    }
    
    for key, default_value in defaults.items():
        if not hasattr(st.session_state, key):
            setattr(st.session_state, key, default_value)

# Initialize immediately
initialize_app()

# Professional CSS
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
    .auth-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 500px;
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
        margin: 1rem 0;
    }
    .success-alert {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .pricing-card {
        background: white;
        border: 2px solid #e1e5e9;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem;
        text-align: center;
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
        position: relative;
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
    .sidebar-info {
        background: #f8f9ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class UserManager:
    """Bulletproof User Management System"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def create_user(username: str, email: str, password: str, plan: str = 'free') -> Tuple[bool, str]:
        try:
            if not username or not email or not password:
                return False, "All fields are required"
            
            if len(password) < 6:
                return False, "Password must be at least 6 characters"
            
            user_database = getattr(st.session_state, 'user_database', {})
            if username in user_database:
                return False, "Username already exists"
            
            user_profile = {
                'user_id': str(uuid.uuid4()),
                'username': username,
                'email': email,
                'password_hash': UserManager.hash_password(password),
                'plan': plan,
                'created_date': datetime.now().isoformat(),
                'usage_stats': {
                    'operations_used': 0,
                    'files_processed': 0,
                    'data_processed_mb': 0.0
                },
                'cleaning_history': [],
                'saved_templates': []
            }
            
            user_database[username] = user_profile
            st.session_state.user_database = user_database
            return True, "Account created successfully!"
            
        except Exception as e:
            return False, f"Error creating account: {str(e)}"
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Tuple[bool, str]:
        try:
            if not username or not password:
                return False, "Username and password required"
            
            user_database = getattr(st.session_state, 'user_database', {})
            if username not in user_database:
                return False, "Invalid username or password"
            
            user_profile = user_database[username]
            if user_profile['password_hash'] == UserManager.hash_password(password):
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.session_state.user_profile = user_profile
                st.session_state.current_page = 'dashboard'
                return True, "Login successful!"
            else:
                return False, "Invalid username or password"
                
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    @staticmethod
    def logout():
        st.session_state.authenticated = False
        st.session_state.current_user = ''
        st.session_state.user_profile = {}
        st.session_state.current_page = 'auth'
        st.session_state.uploaded_data = None
        st.session_state.cleaned_data = None
    
    @staticmethod
    def get_plan_limits(plan: str) -> Dict[str, Any]:
        plan_limits = {
            'free': {
                'max_file_size_mb': 5,
                'max_operations_monthly': 10,
                'export_formats': ['csv'],
                'features': ['Basic cleaning', 'CSV export'],
                'price': 0
            },
            'pro': {
                'max_file_size_mb': 100,
                'max_operations_monthly': 1000,
                'export_formats': ['csv', 'excel', 'json'],
                'features': ['All cleaning operations', 'Multi-format export', 'Templates'],
                'price': 19
            },
            'enterprise': {
                'max_file_size_mb': float('inf'),
                'max_operations_monthly': float('inf'),
                'export_formats': ['csv', 'excel', 'json'],
                'features': ['Unlimited everything', 'API access', 'Priority support'],
                'price': 99
            }
        }
        return plan_limits.get(plan, plan_limits['free'])
    
    @staticmethod
    def can_perform_operation(user_profile: Dict, file_size_mb: float = 0) -> Tuple[bool, str]:
        try:
            plan = user_profile.get('plan', 'free')
            limits = UserManager.get_plan_limits(plan)
            usage = user_profile.get('usage_stats', {})
            
            if file_size_mb > limits['max_file_size_mb']:
                return False, f"File size exceeds {limits['max_file_size_mb']}MB limit"
            
            operations_used = usage.get('operations_used', 0)
            if operations_used >= limits['max_operations_monthly']:
                return False, f"Monthly operations limit ({limits['max_operations_monthly']}) reached"
            
            return True, ""
            
        except Exception:
            return False, "Error checking limits"

class DataProcessor:
    """Professional Data Cleaning Engine"""
    
    @staticmethod
    def load_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
        try:
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
                    
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                try:
                    df = pd.read_excel(uploaded_file)
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                except ImportError:
                    return None, "Excel support not available. Install: pip install openpyxl"
                except Exception as e:
                    return None, f"Error reading Excel file: {str(e)}"
            else:
                return None, "Unsupported file format"
            
            if df.empty:
                return None, "File is empty"
            
            return df, "File loaded successfully!"
            
        except Exception as e:
            return None, f"Error loading file: {str(e)}"
    
    @staticmethod
    def clean_data(df: pd.DataFrame, operations: Dict) -> Tuple[Optional[pd.DataFrame], List[str]]:
        try:
            cleaned_df = df.copy()
            applied_operations = []
            
            if operations.get('remove_duplicates', False):
                initial_rows = len(cleaned_df)
                cleaned_df = cleaned_df.drop_duplicates()
                removed_rows = initial_rows - len(cleaned_df)
                if removed_rows > 0:
                    applied_operations.append(f"Removed {removed_rows} duplicate rows")
            
            if operations.get('handle_missing', False):
                method = operations.get('missing_method', 'drop')
                initial_missing = cleaned_df.isnull().sum().sum()
                
                if method == 'drop':
                    cleaned_df = cleaned_df.dropna()
                elif method == 'fill_mean':
                    numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
                    cleaned_df[numeric_columns] = cleaned_df[numeric_columns].fillna(
                        cleaned_df[numeric_columns].mean()
                    )
                elif method == 'fill_forward':
                    cleaned_df = cleaned_df.fillna(method='ffill')
                
                final_missing = cleaned_df.isnull().sum().sum()
                handled_missing = initial_missing - final_missing
                if handled_missing > 0:
                    applied_operations.append(f"Handled {handled_missing} missing values")
            
            if operations.get('standardize_text', False):
                text_columns = cleaned_df.select_dtypes(include=['object']).columns
                for col in text_columns:
                    if operations.get('text_lowercase', False):
                        cleaned_df[col] = cleaned_df[col].astype(str).str.lower()
                    if operations.get('text_trim', True):
                        cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                
                if len(text_columns) > 0:
                    applied_operations.append(f"Standardized text in {len(text_columns)} columns")
            
            if operations.get('remove_outliers', False):
                numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
                initial_rows = len(cleaned_df)
                
                for col in numeric_columns:
                    Q1 = cleaned_df[col].quantile(0.25)
                    Q3 = cleaned_df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    cleaned_df = cleaned_df[
                        (cleaned_df[col] >= lower_bound) & (cleaned_df[col] <= upper_bound)
                    ]
                
                removed_outliers = initial_rows - len(cleaned_df)
                if removed_outliers > 0:
                    applied_operations.append(f"Removed {removed_outliers} outlier rows")
            
            return cleaned_df, applied_operations
            
        except Exception as e:
            return None, [f"Error during cleaning: {str(e)}"]

def render_authentication():
    """Render login/signup interface"""
    st.markdown("""
    <div class="main-header">
        <h1>🧹 No-Code Data Cleaner Pro</h1>
        <p>Professional data cleaning platform for modern businesses</p>
        <p><strong>Join thousands of data professionals worldwide</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="auth-card">
            <h3 style="text-align: center; color: #667eea;">Sign In</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=True):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_submit = st.form_submit_button("🔑 Sign In", use_container_width=True)
            
            if login_submit:
                success, message = UserManager.authenticate_user(login_username, login_password)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    with col2:
        st.markdown("""
        <div class="auth-card">
            <h3 style="text-align: center; color: #667eea;">Create Account</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("signup_form", clear_on_submit=True):
            signup_username = st.text_input("Choose Username", key="signup_username")
            signup_email = st.text_input("Email Address", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_plan = st.selectbox("Choose Plan", ["free", "pro", "enterprise"])
            
            plan_info = UserManager.get_plan_limits(signup_plan)
            st.info(f"**{signup_plan.title()} Plan**: {plan_info['max_file_size_mb']}MB files, {plan_info['max_operations_monthly']} operations/month")
            
            signup_submit = st.form_submit_button("📝 Create Account", use_container_width=True)
            
            if signup_submit:
                success, message = UserManager.create_user(signup_username, signup_email, signup_password, signup_plan)
                if success:
                    st.success(f"✅ {message}")
                    st.info("👆 Now sign in with your new account!")
                else:
                    st.error(f"❌ {message}")
    
    # Feature showcase
    st.markdown("### 🚀 Why Choose Our Platform?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 Selective Cleaning</h4>
            <p>Choose exactly which data to clean with precision controls</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Multi-Format Support</h4>
            <p>Works with CSV, Excel files. Export to multiple formats</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>⚡ Professional Results</h4>
            <p>Enterprise-grade cleaning with detailed analytics</p>
        </div>
        """, unsafe_allow_html=True)

def render_dashboard():
    """Render user dashboard"""
    user_profile = getattr(st.session_state, 'user_profile', {})
    
    if not user_profile:
        st.error("❌ Please sign in again.")
        UserManager.logout()
        st.rerun()
        return
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        username = user_profile.get('username', 'User')
        plan = user_profile.get('plan', 'free')
        st.markdown(f"### Welcome back, **{username}**! 👋")
        st.markdown(f"**{plan.title()} Plan** • Member since {user_profile.get('created_date', '')[:10]}")
    
    with col2:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = 'settings'
            st.rerun()
    
    with col3:
        if st.button("🚪 Sign Out", use_container_width=True):
            UserManager.logout()
            st.rerun()
    
    # Usage statistics
    st.markdown("### 📊 Your Usage Dashboard")
    usage_stats = user_profile.get('usage_stats', {})
    plan_limits = UserManager.get_plan_limits(plan)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        operations_used = usage_stats.get('operations_used', 0)
        operations_limit = plan_limits['max_operations_monthly']
        st.markdown(f"""
        <div class="metric-card">
            <h3>{operations_used}</h3>
            <p>Operations Used</p>
            <small>Limit: {operations_limit if operations_limit != float('inf') else '∞'}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        files_processed = usage_stats.get('files_processed', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{files_processed}</h3>
            <p>Files Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        data_processed = usage_stats.get('data_processed_mb', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{data_processed:.1f} MB</h3>
            <p>Data Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        templates_saved = len(user_profile.get('saved_templates', []))
        st.markdown(f"""
        <div class="metric-card">
            <h3>{templates_saved}</h3>
            <p>Templates Saved</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Start Cleaning", use_container_width=True, type="primary"):
            st.session_state.current_page = 'cleaner'
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = 'analytics'
            st.rerun()
    
    with col3:
        if plan != 'free':
            if st.button("💾 My Templates", use_container_width=True):
                st.session_state.current_page = 'templates'
                st.rerun()
        else:
            if st.button("🚀 Upgrade Plan", use_container_width=True):
                st.session_state.current_page = 'settings'
                st.rerun()
    
    # Upgrade prompt for free users
    if plan == 'free' and operations_used >= 8:
        st.markdown("""
        <div class="feature-card" style="border-left-color: #f5576c;">
            <h4>🚀 You're almost at your limit!</h4>
            <p>Upgrade to Pro for 1000 operations per month and advanced features.</p>
        </div>
        """, unsafe_allow_html=True)

def render_data_cleaner():
    """Render data cleaning interface"""
    st.markdown("### 🧹 Data Cleaning Workspace")
    
    user_profile = getattr(st.session_state, 'user_profile', {})
    if not user_profile:
        st.error("❌ Please sign in again.")
        return
    
    plan = user_profile.get('plan', 'free')
    plan_limits = UserManager.get_plan_limits(plan)
    
    # File upload
    st.markdown("#### 📁 Upload Your Data")
    st.info(f"**{plan.title()} Plan**: Max file size {plan_limits['max_file_size_mb']}MB")
    
    uploaded_file = st.file_uploader(
        "Choose CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help=f"Upload files up to {plan_limits['max_file_size_mb']}MB"
    )
    
    if uploaded_file is not None:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        can_upload, error_msg = UserManager.can_perform_operation(user_profile, file_size_mb)
        
        if not can_upload:
            st.error(f"❌ {error_msg}")
            if plan == 'free':
                st.info("🚀 **Upgrade to Pro** for 100MB files and 1000 operations per month!")
            return
        
        df, load_message = DataProcessor.load_file(uploaded_file)
        
        if df is not None:
            st.success(f"✅ {load_message}")
            st.session_state.uploaded_data = df
            
            # File statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Rows", f"{len(df):,}")
            with col2:
                st.metric("📋 Columns", len(df.columns))
            with col3:
                st.metric("💾 Size", f"{file_size_mb:.2f} MB")
            with col4:
                missing_values = df.isnull().sum().sum()
                st.metric("❓ Missing Values", f"{missing_values:,}")
            
            # Data preview
            st.markdown("#### 👀 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.error(f"❌ {load_message}")
            return
    
    # Cleaning operations
    uploaded_data = getattr(st.session_state, 'uploaded_data', None)
    if uploaded_data is not None:
        df = uploaded_data
        
        st.markdown("#### 🛠️ Cleaning Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Operations:**")
            remove_duplicates = st.checkbox("🔄 Remove duplicate rows")
            handle_missing = st.checkbox("❓ Handle missing values")
            if handle_missing:
                missing_method = st.selectbox(
                    "Missing value method:",
                    ['drop', 'fill_mean', 'fill_forward'],
                    format_func=lambda x: {
                        'drop': 'Remove rows with missing values',
                        'fill_mean': 'Fill with column average',
                        'fill_forward': 'Fill with previous value'
                    }[x]
                )
            else:
                missing_method = 'drop'
        
        with col2:
            st.markdown("**Advanced Operations:**")
            standardize_text = st.checkbox("📝 Standardize text format")
            if standardize_text:
                text_lowercase = st.checkbox("Convert to lowercase", value=True)
                text_trim = st.checkbox("Remove extra spaces", value=True)
            else:
                text_lowercase = False
                text_trim = False
            
            remove_outliers = st.checkbox("📊 Remove statistical outliers")
        
        # Apply cleaning
        if st.button("🧹 Clean Data", type="primary", use_container_width=True):
            can_operate, error_msg = UserManager.can_perform_operation(user_profile)
            if not can_operate:
                st.error(f"❌ {error_msg}")
                return
            
            operations = {
                'remove_duplicates': remove_duplicates,
                'handle_missing': handle_missing,
                'missing_method': missing_method,
                'standardize_text': standardize_text,
                'text_lowercase': text_lowercase,
                'text_trim': text_trim,
                'remove_outliers': remove_outliers
            }
            
            with st.spinner("🔄 Cleaning your data..."):
                cleaned_df, applied_operations = DataProcessor.clean_data(df, operations)
            
            if cleaned_df is not None:
                st.session_state.cleaned_data = cleaned_df
                
                # Update usage statistics
                try:
                    current_user = getattr(st.session_state, 'current_user', '')
                    user_database = getattr(st.session_state, 'user_database', {})
                    
                    if current_user and current_user in user_database:
                        user_database[current_user]['usage_stats']['operations_used'] += 1
                        user_database[current_user]['usage_stats']['files_processed'] += 1
                        user_database[current_user]['usage_stats']['data_processed_mb'] += file_size_mb
                        
                        st.session_state.user_database = user_database
                        st.session_state.user_profile = user_database[current_user]
                
                except Exception:
                    pass  # Silently continue if update fails
                
                st.markdown(f"""
                <div class="success-alert">
                    <h4>✅ Data Cleaned Successfully!</h4>
                    <p>Applied {len(applied_operations)} operations:</p>
                    <ul>{"".join(f"<li>{op}</li>" for op in applied_operations)}</ul>
                </div>
                """, unsafe_allow_html=True)
                
                st.balloons()
            else:
                st.error("❌ Error during data cleaning. Please try again.")
    
    # Results section
    cleaned_data = getattr(st.session_state, 'cleaned_data', None)
    if cleaned_data is not None:
        cleaned_df = cleaned_data
        original_df = uploaded_data
        
        st.markdown("#### 📊 Cleaning Results")
        
        # Before/After comparison
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📋 Before Cleaning:**")
            st.write(f"• Rows: {len(original_df):,}")
            st.write(f"• Columns: {len(original_df.columns)}")
            st.write(f"• Missing values: {original_df.isnull().sum().sum():,}")
        
        with col2:
            st.markdown("**✨ After Cleaning:**")
            st.write(f"• Rows: {len(cleaned_df):,}")
            st.write(f"• Columns: {len(cleaned_df.columns)}")
            st.write(f"• Missing values: {cleaned_df.isnull().sum().sum():,}")
        
        st.markdown("**🎯 Cleaned Data Preview:**")
        st.dataframe(cleaned_df.head(20), use_container_width=True)
        
        # Download options
        st.markdown("#### 📥 Download Cleaned Data")
        
        export_formats = plan_limits['export_formats']
        download_cols = st.columns(len(export_formats))
        
        for i, format_type in enumerate(export_formats):
            with download_cols[i]:
                if format_type == 'csv':
                    csv_data = cleaned_df.to_csv(index=False)
                    st.download_button(
                        "📄 Download CSV",
                        csv_data,
                        f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                elif format_type == 'excel':
                    try:
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            cleaned_df.to_excel(writer, sheet_name='Cleaned_Data', index=False)
                            
                            summary_data = {
                                'Metric': ['Original Rows', 'Cleaned Rows', 'Rows Removed'],
                                'Value': [len(original_df), len(cleaned_df), len(original_df) - len(cleaned_df)]
                            }
                            summary_df = pd.DataFrame(summary_data)
                            summary_df.to_excel(writer, sheet_name='Summary', index=False)
                        
                        excel_data = excel_buffer.getvalue()
                        st.download_button(
                            "📊 Download Excel",
                            excel_data,
                            f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except ImportError:
                        st.button("📊 Excel (Install openpyxl)", disabled=True, use_container_width=True)
                
                elif format_type == 'json':
                    json_data = cleaned_df.to_json(orient='records', indent=2)
                    st.download_button(
                        "🔗 Download JSON",
                        json_data,
                        f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        "application/json",
                        use_container_width=True
                    )

def render_settings():
    """Render settings and pricing page"""
    st.markdown("### ⚙️ Account Settings")
    
    user_profile = getattr(st.session_state, 'user_profile', {})
    if not user_profile:
        st.error("❌ Please sign in again.")
        return
    
    # User profile section
    st.markdown("#### 👤 Profile Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Username:** {user_profile.get('username', 'Unknown')}")
        st.info(f"**Email:** {user_profile.get('email', 'Unknown')}")
    
    with col2:
        st.info(f"**Plan:** {user_profile.get('plan', 'free').title()}")
        st.info(f"**Member Since:** {user_profile.get('created_date', 'Unknown')[:10]}")
    
    # Pricing plans
    st.markdown("#### 💎 Choose Your Plan")
    
    col1, col2, col3 = st.columns(3)
    
    current_plan = user_profile.get('plan', 'free')
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3>🆓 Free Plan</h3>
            <h2>$0<small>/month</small></h2>
            <hr>
            <p>✅ 5MB file limit</p>
            <p>✅ 10 operations/month</p>
            <p>✅ CSV export only</p>
            <p>✅ Community support</p>
        </div>
        """, unsafe_allow_html=True)
        
        if current_plan == 'free':
            st.success("✅ Current Plan")
        else:
            if st.button("Downgrade to Free", key="free_plan"):
                st.session_state.user_profile['plan'] = 'free'
                current_user = getattr(st.session_state, 'current_user', '')
                if current_user:
                    user_database = getattr(st.session_state, 'user_database', {})
                    user_database[current_user] = st.session_state.user_profile
                    st.session_state.user_database = user_database
                st.success("Plan changed to Free!")
                st.rerun()
    
    with col2:
        st.markdown("""
        <div class="pricing-card popular">
            <h3>💼 Pro Plan</h3>
            <h2>$19<small>/month</small></h2>
            <hr>
            <p>✅ 100MB file limit</p>
            <p>✅ 1,000 operations/month</p>
            <p>✅ Multi-format export</p>
            <p>✅ All cleaning operations</p>
            <p>✅ Email support</p>
        </div>
        """, unsafe_allow_html=True)
        
        if current_plan == 'pro':
            st.success("✅ Current Plan")
        else:
            if st.button("Upgrade to Pro", key="pro_plan", type="primary"):
                st.session_state.user_profile['plan'] = 'pro'
                current_user = getattr(st.session_state, 'current_user', '')
                if current_user:
                    user_database = getattr(st.session_state, 'user_database', {})
                    user_database[current_user] = st.session_state.user_profile
                    st.session_state.user_database = user_database
                st.success("🎉 Upgraded to Pro! (Demo Mode)")
                st.balloons()
                st.rerun()
    
    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3>🏢 Enterprise Plan</h3>
            <h2>$99<small>/month</small></h2>
            <hr>
            <p>✅ Unlimited file size</p>
            <p>✅ Unlimited operations</p>
            <p>✅ All export formats</p>
            <p>✅ API access</p>
            <p>✅ Priority support</p>
        </div>
        """, unsafe_allow_html=True)
        
        if current_plan == 'enterprise':
            st.success("✅ Current Plan")
        else:
            if st.button("Upgrade to Enterprise", key="enterprise_plan", type="primary"):
                st.session_state.user_profile['plan'] = 'enterprise'
                current_user = getattr(st.session_state, 'current_user', '')
                if current_user:
                    user_database = getattr(st.session_state, 'user_database', {})
                    user_database[current_user] = st.session_state.user_profile
                    st.session_state.user_database = user_database
                st.success("🎉 Upgraded to Enterprise! (Demo Mode)")
                st.balloons()
                st.rerun()
    
    # Back button
    st.markdown("---")
    if st.button("← Back to Dashboard", use_container_width=True):
        st.session_state.current_page = 'dashboard'
        st.rerun()

def render_analytics():
    """Render analytics page"""
    st.markdown("### 📊 Analytics & History")
    
    user_profile = getattr(st.session_state, 'user_profile', {})
    if not user_profile:
        st.error("❌ Please sign in again.")
        return
    
    usage_stats = user_profile.get('usage_stats', {})
    
    # Usage overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{usage_stats.get('operations_used', 0)}</h3>
            <p>Total Operations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{usage_stats.get('files_processed', 0)}</h3>
            <p>Files Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{usage_stats.get('data_processed_mb', 0):.1f} MB</h3>
            <p>Data Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Cleaning history
    cleaning_history = user_profile.get('cleaning_history', [])
    
    if cleaning_history:
        st.markdown("#### 📋 Recent Operations")
        for i, operation in enumerate(reversed(cleaning_history[-10:]), 1):
            with st.expander(f"Operation {i} - {operation.get('timestamp', 'Unknown')[:16]}"):
                st.write(f"**File:** {operation.get('filename', 'Unknown')}")
                st.write(f"**Operations:** {', '.join(operation.get('operations', []))}")
                st.write(f"**Rows processed:** {operation.get('rows_processed', 'Unknown')}")
                st.write(f"**Result:** {operation.get('result', 'Completed')}")
    else:
        st.info("📊 No operations performed yet. Start cleaning data to see your history!")

def render_templates():
    """Render templates page"""
    st.markdown("### 💾 Cleaning Templates")
    
    user_profile = getattr(st.session_state, 'user_profile', {})
    if not user_profile:
        st.error("❌ Please sign in again.")
        return
    
    if user_profile.get('plan') == 'free':
        st.info("🚀 **Upgrade to Pro** to save and reuse cleaning templates!")
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 What are Templates?</h4>
            <p>Save your favorite cleaning operations as templates and reuse them on new datasets.</p>
            <ul>
                <li>✅ Save cleaning configurations</li>
                <li>✅ Apply to multiple files</li>
                <li>✅ Share with team members</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Upgrade to Pro", type="primary", use_container_width=True):
            st.session_state.current_page = 'settings'
            st.rerun()
        return
    
    st.info("💾 Template management will be available in the next update!")

def render_help():
    """Render help page"""
    st.markdown("### ❓ Help & Documentation")
    
    st.markdown("#### 🚀 Quick Start Guide")
    
    with st.expander("1. 📁 How to Upload Data"):
        st.markdown("""
        **Supported formats:** CSV, Excel (.xlsx, .xls)
        
        **File size limits:**
        - Free: 5 MB
        - Pro: 100 MB  
        - Enterprise: Unlimited
        
        **Tips:**
        - Ensure your data has proper column headers
        - Remove any merged cells in Excel files
        """)
    
    with st.expander("2. 🧹 Available Cleaning Operations"):
        st.markdown("""
        **Basic Operations:**
        - **Remove Duplicates:** Removes identical rows
        - **Handle Missing Values:** Fill or remove missing data
        - **Standardize Text:** Normalize text formatting
        
        **Advanced Operations:**
        - **Remove Outliers:** Statistical outlier detection
        """)
    
    with st.expander("3. 📊 Understanding Results"):
        st.markdown("""
        **Before/After Comparison:**
        - Shows original vs cleaned data statistics
        
        **Download Options:**
        - **CSV:** Universal format
        - **Excel:** Includes summary sheet (Pro+)
        - **JSON:** For API integrations (Pro+)
        """)
    
    # Contact information
    st.markdown("#### 📧 Need More Help?")
    
    user_plan = getattr(st.session_state, 'user_profile', {}).get('plan', 'free')
    
    if user_plan == 'free':
        st.info("**Free Plan Support:** Documentation and community forum")
    elif user_plan == 'pro':
        st.success("**Pro Plan Support:** Email support with 24-48h response")
    else:
        st.success("**Enterprise Support:** Priority support with 4-8h response")

def render_sidebar():
    """Render sidebar"""
    with st.sidebar:
        is_authenticated = getattr(st.session_state, 'authenticated', False)
        
        if is_authenticated:
            user_profile = getattr(st.session_state, 'user_profile', {})
            
            if user_profile:
                st.markdown(f"""
                <div class="sidebar-info">
                    <h4>👤 {user_profile.get('username', 'User')}</h4>
                    <p><strong>Plan:</strong> {user_profile.get('plan', 'free').title()}</p>
                    <p><strong>Operations:</strong> {user_profile.get('usage_stats', {}).get('operations_used', 0)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 🧭 Navigation")
                
                nav_options = [
                    ("🏠 Dashboard", "dashboard"),
                    ("🧹 Data Cleaner", "cleaner"),
                    ("📊 Analytics", "analytics"),
                    ("💾 Templates", "templates"),
                    ("⚙️ Settings", "settings"),
                    ("❓ Help", "help")
                ]
                
                for label, page_key in nav_options:
                    if st.button(label, use_container_width=True):
                        st.session_state.current_page = page_key
                        st.rerun()
                
                st.markdown("---")
                
                # Usage progress
                usage_stats = user_profile.get('usage_stats', {})
                plan_limits = UserManager.get_plan_limits(user_profile.get('plan', 'free'))
                operations_used = usage_stats.get('operations_used', 0)
                operations_limit = plan_limits['max_operations_monthly']
                
                if operations_limit != float('inf'):
                    usage_pct = (operations_used / operations_limit) * 100
                    st.markdown(f"**Monthly Usage: {usage_pct:.1f}%**")
                    st.progress(min(usage_pct / 100, 1.0))
                else:
                    st.markdown("**✨ Unlimited Usage**")
        
        else:
            st.markdown("""
            <div class="sidebar-info">
                <h4>🧹 Data Cleaner Pro</h4>
                <p>Professional data cleaning platform</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### ✨ Features")
            st.markdown("• 🎯 Selective cleaning")
            st.markdown("• 📊 Multi-format support") 
            st.markdown("• ⚡ Professional results")
            st.markdown("• 📈 Usage analytics")

def main():
    """Main application controller"""
    
    try:
        initialize_app()
        
        if not hasattr(st.session_state, 'app_initialized'):
            st.error("🔄 Please refresh the page.")
            st.stop()
        
    except Exception as e:
        st.error(f"⚠️ Initialization Error: {str(e)}")
        st.stop()
    
    render_sidebar()
    
    try:
        is_authenticated = getattr(st.session_state, 'authenticated', False)
        current_page = getattr(st.session_state, 'current_page', 'auth')
        
        if not is_authenticated:
            render_authentication()
        else:
            user_profile = getattr(st.session_state, 'user_profile', {})
            if not user_profile:
                st.error("❌ Session expired. Please sign in again.")
                UserManager.logout()
                st.rerun()
                return
            
            if current_page == 'dashboard':
                render_dashboard()
            elif current_page == 'cleaner':
                render_data_cleaner()
            elif current_page == 'analytics':
                render_analytics()
            elif current_page == 'templates':
                render_templates()
            elif current_page == 'settings':
                render_settings()
            elif current_page == 'help':
                render_help()
            else:
                st.session_state.current_page = 'dashboard'
                st.rerun()
    
    except Exception as e:
        st.error(f"⚠️ Application Error: {str(e)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset Application", type="primary"):
                for key in list(st.session_state.keys()):
                    if hasattr(st.session_state, key):
                        delattr(st.session_state, key)
                initialize_app()
                st.success("✅ Application reset!")
                st.rerun()
        
        with col2:
            if st.button("🏠 Return Home"):
                st.session_state.current_page = 'dashboard' if getattr(st.session_state, 'authenticated', False) else 'auth'
                st.rerun()

# Run the application
if __name__ == "__main__":
    main()
