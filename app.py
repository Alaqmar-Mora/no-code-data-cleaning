summary_data = {
                                'Metric': ['Original Rows', 'Cleaned Rows', 'Rows Removed', 'Columns', 'Missing Values'],
                                'Value': [
                                    len(original_df),
                                    len(cleaned_df),
                                    len(original_df) - len(cleaned_df),
                                    len(cleaned_df.columns),
                                    cleaned_df.isnull().sum().sum()
                                ]
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
                        st.button("📊 Excel (Install openpyxl)", disabled=True, use_container_width=True,
                                help="Install openpyxl to enable Excel export")
                
                elif format_type == 'json':
                    json_data = cleaned_df.to_json(orient='records', indent=2)
                    st.download_button(
                        "🔗 Download JSON",
                        json_data,
                        f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        "application/json",
                        use_container_width=True
                    )

def render_analytics():
    """Render analytics and history page"""
    st.markdown("### 📊 Analytics & History")
    
    user_profile = st.session_state.user_profile
    usage_stats = user_profile.get('usage_stats', {})
    cleaning_history = user_profile.get('cleaning_history', [])
    
    # Usage overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>{}</h3>
            <p>Total Operations</p>
        </div>
        """.format(usage_stats.get('operations_used', 0)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>{}</h3>
            <p>Files Processed</p>
        </div>
        """.format(usage_stats.get('files_processed', 0)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>{:.1f} MB</h3>
            <p>Data Processed</p>
        </div>
        """.format(usage_stats.get('data_processed_mb', 0)), unsafe_allow_html=True)
    
    # Cleaning history
    if cleaning_history:
        st.markdown("#### 📋 Recent Operations")
        for i, operation in enumerate(reversed(cleaning_history[-10:]), 1):
            with st.expander(f"Operation {i} - {operation.get('timestamp', 'Unknown time')[:16]}"):
                st.write(f"**File:** {operation.get('filename', 'Unknown')}")
                st.write(f"**Operations:** {', '.join(operation.get('operations', []))}")
                st.write(f"**Rows processed:** {operation.get('rows_processed', 'Unknown')}")
                st.write(f"**Result:** {operation.get('result', 'Unknown')}")
    else:
        st.info("📊 No operations performed yet. Start cleaning data to see your history!")

def render_templates():
    """Render templates page (Pro+ feature)"""
    st.markdown("### 💾 Cleaning Templates")
    
    user_profile = st.session_state.user_profile
    
    if user_profile['plan'] == 'free':
        st.info("🚀 **Upgrade to Pro** to save and reuse cleaning templates!")
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 What are Templates?</h4>
            <p>Save your favorite cleaning operations as templates and reuse them instantly on new datasets. Perfect for recurring data cleaning tasks!</p>
            <ul>
                <li>✅ Save cleaning configurations</li>
                <li>✅ Apply to multiple files</li>
                <li>✅ Share with team members</li>
                <li>✅ Version control your workflows</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Upgrade to Pro", type="primary", use_container_width=True):
            st.session_state.current_page = 'settings'
            st.rerun()
        return
    
    # Pro+ template management
    saved_templates = user_profile.get('saved_templates', [])
    
    if saved_templates:
        st.markdown("#### 📝 Your Saved Templates")
        
        for i, template in enumerate(saved_templates):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{template['name']}**")
                st.caption(f"Created: {template['created_date'][:10]} | Used: {template['usage_count']} times")
            
            with col2:
                if st.button("📋 Use", key=f"use_{i}"):
                    st.info("Template application feature coming in next update!")
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    saved_templates.pop(i)
                    st.session_state.user_profile['saved_templates'] = saved_templates
                    st.success("Template deleted!")
                    st.rerun()
    else:
        st.info("💾 No templates saved yet. Clean some data first to save templates!")
    
    # Template creation (placeholder)
    st.markdown("#### ➕ Create New Template")
    st.info("🚧 Template creation will be available after you clean data. The system will automatically offer to save your cleaning operations as templates.")

def render_help():
    """Render help and documentation page"""
    st.markdown("### ❓ Help & Documentation")
    
    # Quick start guide
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
        - For large files, consider splitting into smaller chunks
        """)
    
    with st.expander("2. 🧹 Available Cleaning Operations"):
        st.markdown("""
        **Basic Operations:**
        - **Remove Duplicates:** Removes identical rows
        - **Handle Missing Values:** Fill or remove missing data
        - **Standardize Text:** Normalize text formatting
        
        **Advanced Operations:**
        - **Remove Outliers:** Statistical outlier detection using IQR
        - **Data Type Conversion:** Convert between text/numbers/dates
        - **Custom Rules:** Pro+ feature for advanced cleaning
        """)
    
    with st.expander("3. 📊 Understanding Results"):
        st.markdown("""
        **Before/After Comparison:**
        - Shows original vs cleaned data statistics
        - Highlights what was changed or removed
        
        **Download Options:**
        - **CSV:** Universal format, works everywhere
        - **Excel:** Includes summary sheet with cleaning report
        - **JSON:** For API integrations and web applications
        """)
    
    with st.expander("4. 💎 Plan Features"):
        st.markdown("""
        **Free Plan:**
        - 10 operations per month
        - 5 MB file limit
        - CSV export only
        
        **Pro Plan ($19/month):**
        - 1,000 operations per month
        - 100 MB file limit
        - All export formats
        - Cleaning templates
        - Email support
        
        **Enterprise Plan ($99/month):**
        - Unlimited operations
        - Unlimited file size
        - API access
        - Batch processing
        - Priority support
        """)
    
    # Common issues
    st.markdown("#### 🔧 Troubleshooting")
    
    with st.expander("File Upload Issues"):
        st.markdown("""
        **Excel files not working?**
        - Install required libraries: `pip install openpyxl xlrd`
        - Or convert Excel to CSV format first
        
        **File too large?**
        - Upgrade your plan for higher limits
        - Split large files into smaller chunks
        - Remove unnecessary columns before upload
        
        **Encoding errors?**
        - Save CSV with UTF-8 encoding
        - Try different text editors (VS Code, Notepad++)
        """)
    
    with st.expander("Cleaning Results Issues"):
        st.markdown("""
        **Too many rows removed?**
        - Check your outlier removal settings
        - Review missing value handling method
        - Preview operations before applying
        
        **Data looks wrong?**
        - Download original data to compare
        - Check cleaning operation logs
        - Contact support for complex issues
        """)
    
    # Contact information
    st.markdown("#### 📧 Need More Help?")
    
    user_plan = st.session_state.user_profile.get('plan', 'free')
    
    if user_plan == 'free':
        st.info("""
        **Free Plan Support:**
        - 📚 Documentation and guides (this page)
        - 💬 Community forum (coming soon)
        - 🚀 Upgrade to Pro for email support
        """)
    
    elif user_plan == 'pro':
        st.success("""
        **Pro Plan Support:**
        - ✅ Email support: support@datacleaner.pro
        - ✅ Response time: 24-48 hours
        - ✅ Feature requests welcomed
        """)
    
    else:  # Enterprise
        st.success("""
        **Enterprise Support:**
        - ✅ Priority email support: enterprise@datacleaner.pro
        - ✅ Response time: 4-8 hours
        - ✅ Phone support available
        - ✅ Custom integrations
        """)

def render_api_docs():
    """Render API documentation (Enterprise feature)"""
    st.markdown("### 🔗 API Documentation")
    
    user_profile = st.session_state.user_profile
    
    if user_profile['plan'] != 'enterprise':
        st.info("🏢 **API access is available with Enterprise plan only!**")
        
        st.markdown("""
        <div class="feature-card">
            <h4>🚀 Enterprise API Features</h4>
            <p>Integrate data cleaning into your applications and workflows:</p>
            <ul>
                <li>✅ RESTful API endpoints</li>
                <li>✅ Batch processing capabilities</li>
                <li>✅ Webhook notifications</li>
                <li>✅ Custom cleaning rules</li>
                <li>✅ Rate limiting and monitoring</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Upgrade to Enterprise", type="primary", use_container_width=True):
            st.session_state.current_page = 'settings'
            st.rerun()
        return
    
    # Enterprise API documentation
    st.success("🎉 **API Access Enabled!** Your Enterprise plan includes full API access.")
    
    # API key section
    st.markdown("#### 🔑 API Authentication")
    api_key = f"dc_ent_{user_profile['user_id'][:8]}_{hashlib.md5(user_profile['username'].encode()).hexdigest()[:8]}"
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.code(api_key, language=None)
    with col2:
        st.button("🔄 Regenerate", help="Contact support to regenerate API key")
    
    st.warning("⚠️ Keep your API key secure! Don't share it publicly.")
    
    # API endpoints
    st.markdown("#### 📡 Available Endpoints")
    
    with st.expander("POST /api/v1/clean - Clean Data"):
        st.markdown("""
        **Description:** Clean uploaded data with specified operations
        
        **Headers:**
        ```
        Authorization: Bearer YOUR_API_KEY
        Content-Type: multipart/form-data
        ```
        
        **Parameters:**
        - `file`: Data file (CSV/Excel)
        - `operations`: JSON string of cleaning operations
        
        **Example Request:**
        ```python
        import requests
        import json
        
        url = "https://api.datacleaner.pro/v1/clean"
        headers = {"Authorization": "Bearer YOUR_API_KEY"}
        files = {"file": open("data.csv", "rb")}
        data = {
            "operations": json.dumps({
                "remove_duplicates": True,
                "handle_missing": True,
                "missing_method": "drop"
            })
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        ```
        
        **Response:**
        ```json
        {
            "success": true,
            "cleaned_data_url": "https://cdn.datacleaner.pro/results/abc123.csv",
            "operations_applied": ["Removed 5 duplicates", "Handled 12 missing values"],
            "original_rows": 1000,
            "cleaned_rows": 983
        }
        ```
        """)
    
    with st.expander("GET /api/v1/usage - Usage Statistics"):
        st.markdown("""
        **Description:** Get current usage statistics
        
        **Headers:**
        ```
        Authorization: Bearer YOUR_API_KEY
        ```
        
        **Response:**
        ```json
        {
            "plan": "enterprise",
            "usage_this_month": {
                "api_calls": 145,
                "data_processed_mb": 2843.5,
                "files_processed": 67
            },
            "limits": {
                "api_calls_monthly": "unlimited",
                "max_file_size_mb": "unlimited"
            }
        }
        ```
        """)
    
    with st.expander("POST /api/v1/batch - Batch Processing"):
        st.markdown("""
        **Description:** Process multiple files in a single request
        
        **Headers:**
        ```
        Authorization: Bearer YOUR_API_KEY
        Content-Type: application/json
        ```
        
        **Request Body:**
        ```json
        {
            "files": [
                {"url": "https://example.com/data1.csv", "name": "dataset1"},
                {"url": "https://example.com/data2.csv", "name": "dataset2"}
            ],
            "operations": {
                "remove_duplicates": True,
                "handle_missing": True
            },
            "webhook_url": "https://your-app.com/webhook"
        }
        ```
        
        **Response:**
        ```json
        {
            "batch_id": "batch_abc123",
            "status": "processing",
            "estimated_completion": "2024-01-15T10:30:00Z"
        }
        ```
        """)
    
    # Rate limits and best practices
    st.markdown("#### ⚡ Rate Limits & Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Rate Limits:**
        - 1000 requests per hour
        - 10 concurrent requests
        - 1GB max file size per request
        """)
    
    with col2:
        st.markdown("""
        **Best Practices:**
        - Use batch processing for multiple files
        - Implement exponential backoff
        - Cache results when possible
        """)

def render_advanced_sidebar():
    """Enhanced sidebar with all navigation options"""
    with st.sidebar:
        if getattr(st.session_state, 'authenticated', False):
            user_profile = getattr(st.session_state, 'user_profile', {})
            
            if user_profile:
                plan_limits = UserManager.get_plan_limits(user_profile['plan'])
                
                # User profile section
                st.markdown(f"""
                <div class="sidebar-info">
                    <h4>👤 {user_profile['username']}</h4>
                    <p><strong>Plan:</strong> {user_profile['plan'].title()}</p>
                    <p><strong>Operations:</strong> {user_profile.get('usage_stats', {}).get('operations_used', 0)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Navigation menu
                st.markdown("### 🧭 Navigation")
                
                nav_options = [
                    ("🏠 Dashboard", "dashboard"),
                    ("🧹 Data Cleaner", "cleaner"),
                    ("📊 Analytics", "analytics"),
                    ("💾 Templates", "templates"),
                    ("⚙️ Settings", "settings"),
                    ("❓ Help", "help")
                ]
                
                # Add API docs for Enterprise users
                if user_profile.get('plan') == 'enterprise':
                    nav_options.append(("🔗 API Docs", "api"))
                
                for label, page_key in nav_options:
                    if st.button(label, use_container_width=True):
                        st.session_state.current_page = page_key
                        st.rerun()
                
                st.markdown("---")
                
                # Usage progress bar
                usage_stats = user_profile.get('usage_stats', {})
                operations_used = usage_stats.get('operations_used', 0)
                operations_limit = plan_limits['max_operations_monthly']
                
                if operations_limit != float('inf'):
                    usage_pct = (operations_used / operations_limit) * 100
                    st.markdown(f"**Monthly Usage: {usage_pct:.1f}%**")
                    st.progress(min(usage_pct / 100, 1.0))
                    
                    if usage_pct > 80:
                        st.warning(f"⚠️ {100 - usage_pct:.1f}% remaining")
                else:
                    st.markdown("**✨ Unlimited Usage**")
                
                # Upgrade prompt for free users
                if user_profile.get('plan') == 'free' and operations_used >= 7:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               padding: 1rem; border-radius: 10px; color: white; text-align: center;">
                        <p style="margin: 0;"><strong>🚀 Almost at limit!</strong><br>
                        Upgrade to Pro for 1000 operations/month</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Quick stats
                st.markdown("### 📈 Quick Stats")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Files", usage_stats.get('files_processed', 0))
                
                with col2:
                    data_mb = usage_stats.get('data_processed_mb', 0)
                    st.metric("Data", f"{data_mb:.1f}MB")
        
        else:
            # Non-authenticated sidebar
            st.markdown("""
            <div class="sidebar-info">
                <h4>🧹 Data Cleaner Pro</h4>
                <p>Professional data cleaning platform</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### ✨ Why Choose Us?")
            st.markdown("• 🎯 **Selective cleaning** - Choose exact data to process")
            st.markdown("• 📊 **Multi-format support** - CSV, Excel, JSON exports") 
            st.markdown("• ⚡ **Professional results** - Enterprise-grade cleaning")
            st.markdown("• 📈 **Usage analytics** - Track your data processing")
            st.markdown("• 🔗 **API access** - Integrate with your apps")
            
            st.markdown("### 💎 Pricing Plans")
            st.markdown("**🆓 Free:** 5MB files, 10 ops/month")
            st.markdown("**💼 Pro:** 100MB files, 1000 ops/month") 
            st.markdown("**🏢 Enterprise:** Unlimited + API access")
            
            st.markdown("---")
            st.markdown("**🚀 Ready to get started?**")
            st.info("Sign up above to begin cleaning your data professionally!")

def main():
    """Enhanced main application controller - PRODUCTION READY"""
    
    # CRITICAL: Always ensure initialization first
    try:
        initialize_app()
        
        # Validate session state is working
        if not hasattr(st.session_state, 'app_initialized'):
            st.error("🔄 Session state not initialized properly. Please refresh the page.")
            st.stop()
        
    except Exception as init_error:
        st.error(f"⚠️ Initialization Error: {str(init_error)}")
        st.info("Please refresh the page. If the problem persists, clear your browser cache.")
        st.stop()
    
    # Render enhanced sidebar
    render_advanced_sidebar()
    
    # Main content routing with comprehensive error handling
    try:
        # Safe access to authentication status
        is_authenticated = getattr(st.session_state, 'authenticated', False)
        current_page = getattr(st.session_state, 'current_page', 'auth')
        
        if not is_authenticated:
            render_authentication()
        
        else:
            # Validate user profile exists
            user_profile = getattr(st.session_state, 'user_profile', {})
            if not user_profile:
                st.error("❌ User session expired. Please sign in again.")
                st.session_state.authenticated = False
                st.session_state.current_user = ''
                st.session_state.user_profile = {}
                st.session_state.current_page = 'auth'
                st.rerun()
                return
            
            # Page routing with validation
            valid_pages = ['dashboard', 'cleaner', 'analytics', 'templates', 'settings', 'help', 'api']
            
            if current_page not in valid_pages:
                st.session_state.current_page = 'dashboard'
                st.rerun()
                return
            
            # Route to appropriate page
            if current_page == 'dashboard':
                render_dashboard()
                
                # Enhanced quick actions
                st.markdown("---")
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
                    plan = user_profile.get('plan', 'free')
                    if plan != 'free':
                        if st.button("💾 My Templates", use_container_width=True):
                            st.session_state.current_page = 'templates'
                            st.rerun()
                    else:
                        if st.button("🚀 Upgrade Plan", use_container_width=True):
                            st.session_state.current_page = 'settings'
                            st.rerun()
                
                # Activity summary
                render_dashboard_activity()
            
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
            
            elif current_page == 'api':
                render_api_docs()
    
    except Exception as app_error:
        # Comprehensive error handling
        st.error(f"⚠️ Application Error: {str(app_error)}")
        
        # Error details for debugging
        with st.expander("🔧 Error Details & Recovery Options"):
            st.code(f"Error Type: {type(app_error).__name__}\nError Message: {str(app_error)}")
            
            st.markdown("**🔧 Troubleshooting Steps:**")
            st.markdown("1. **Refresh the page** (Ctrl+F5 or Cmd+R)")
            st.markdown("2. **Clear browser cache** and cookies")
            st.markdown("3. **Try incognito/private browsing mode**")
            st.markdown("4. **Use emergency reset** (button below)")
            st.markdown("5. **Contact support** if issue persists")
        
        # Recovery options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Emergency Reset", type="primary", use_container_width=True):
                # Safe session state cleanup
                try:
                    for key in list(st.session_state.keys()):
                        if hasattr(st.session_state, key):
                            delattr(st.session_state, key)
                    
                    # Reinitialize
                    initialize_app()
                    st.success("✅ Application reset successfully!")
                    st.info("Please refresh the page to continue.")
                    
                except Exception as reset_error:
                    st.error(f"Reset failed: {str(reset_error)}")
                    st.info("Please manually refresh the page (Ctrl+F5)")
        
        with col2:
            if st.button("🏠 Return Home", use_container_width=True):
                try:
                    st.session_state.current_page = 'dashboard' if st.session_state.authenticated else 'auth'
                    st.rerun()
                except:
                    st.info("Please refresh the page manually.")
        
        with col3:
            if st.button("📧 Get Support", use_container_width=True):
                st.info("📧 **Contact Support:**\nEmail: support@datacleaner.pro\nInclude the error details above for faster resolution.")

def render_dashboard_activity():
    """Render dashboard activity section"""
    try:
        user_profile = getattr(st.session_state, 'user_profile', {})
        cleaning_history = user_profile.get('cleaning_history', [])
        
        if cleaning_history:
            st.markdown("### 📋 Recent Activity")
            recent_ops = cleaning_history[-3:]  # Show last 3
            
            for i, activity in enumerate(reversed(recent_ops), 1):
                with st.expander(f"Operation {len(cleaning_history) - len(recent_ops) + i} - {activity.get('timestamp', 'Unknown')[:10]}"):
                    st.write(f"**File:** {activity.get('filename', 'Unknown')}")
                    st.write(f"**Operations:** {', '.join(activity.get('operations', []))}")
                    st.write(f"**Result:** {activity.get('result', 'Completed successfully')}")
            
            if len(cleaning_history) > 3:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 View All Activity", use_container_width=True):
                        st.session_state.current_page = 'analytics'
                        st.rerun()
        else:
            st.markdown("""
            <div class="feature-card">
                <h4>🎯 Welcome to Data Cleaner Pro!</h4>
                <p>Ready to clean your first dataset? Here's your step-by-step guide:</p>
                <ol>
                    <li><strong>Upload:</strong> Click "Start Cleaning" and upload your CSV/Excel file</li>
                    <li><strong>Preview:</strong> Review your data statistics and structure</li>
                    <li><strong>Clean:</strong> Choose operations like removing duplicates or handling missing values</li>
                    <li><strong>Download:</strong> Get your cleaned data in professional formats</li>
                </ol>
                <p><strong>💡 Pro tip:</strong> Start with a small test file to familiarize yourself with the tools!</p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.warning(f"Could not load activity: {str(e)}")

# Validate requirements function
def validate_environment():
    """Check if all required packages are available"""
    missing_packages = []
    
    try:
        import pandas as pd
    except ImportError:
        missing_packages.append("pandas")
    
    try:
        import numpy as np
    except ImportError:
        missing_packages.append("numpy")
    
    # Optional packages
    optional_missing = []
    try:
        import openpyxl
    except ImportError:
        optional_missing.append("openpyxl (for Excel export)")
    
    try:
        import xlrd
    except ImportError:
        optional_missing.append("xlrd (for legacy Excel files)")
    
    if missing_packages:
        st.error(f"❌ Missing required packages: {', '.join(missing_packages)}")
        st.code(f"pip install {' '.join(missing_packages)}")
        return False
    
    if optional_missing:
        st.warning(f"⚠️ Optional packages missing: {', '.join(optional_missing)}")
        st.info("Install for full functionality: pip install openpyxl xlrd")
    
    return True

# Production health check
def production_health_check():
    """Production readiness checks"""
    checks = {
        "Streamlit Version": True,
        "Session State": hasattr(st, 'session_state'),
        "Core Imports": True,
        "Memory Usage": True
    }
    
    # Check Streamlit version
    try:
        import streamlit as st_version
        version = st_version.__version__
        checks["Streamlit Version"] = version >= "1.28.0"
    except:
        checks["Streamlit Version"] = False
    
    # Return health status
    return all(checks.values()), checks

# Application entry point with environment validation
if __name__ == "__main__":
    # Validate environment before running
    if validate_environment():
        main()
    else:
        st.stop()
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

# Global Session State Initialization - FIRST THING TO RUN
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
        'processing_step': 0
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Initialize immediately when module loads
initialize_app()

# Professional CSS Styling
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
        """Securely hash password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def create_account(username: str, email: str, password: str, plan: str = 'free') -> Tuple[bool, str]:
        """Create new user account"""
        try:
            if not username or not email or not password:
                return False, "All fields are required"
            
            if len(password) < 6:
                return False, "Password must be at least 6 characters"
            
            if username in st.session_state.user_database:
                return False, "Username already exists"
            
            # Create user profile
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
                    'data_processed_mb': 0.0,
                    'last_active': datetime.now().isoformat()
                },
                'cleaning_history': [],
                'saved_templates': []
            }
            
            st.session_state.user_database[username] = user_profile
            return True, "Account created successfully!"
            
        except Exception as e:
            return False, f"Error creating account: {str(e)}"
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Tuple[bool, str]:
        """Authenticate user login"""
        try:
            if not username or not password:
                return False, "Username and password required"
            
            if username not in st.session_state.user_database:
                return False, "Invalid username or password"
            
            user_profile = st.session_state.user_database[username]
            if user_profile['password_hash'] == UserManager.hash_password(password):
                # Set authenticated session
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.session_state.user_profile = user_profile
                st.session_state.current_page = 'dashboard'
                
                # Update last active
                user_profile['usage_stats']['last_active'] = datetime.now().isoformat()
                
                return True, "Login successful!"
            else:
                return False, "Invalid username or password"
                
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    @staticmethod
    def logout():
        """Safely logout user"""
        st.session_state.authenticated = False
        st.session_state.current_user = ''
        st.session_state.user_profile = {}
        st.session_state.current_page = 'auth'
        st.session_state.uploaded_data = None
        st.session_state.cleaned_data = None
    
    @staticmethod
    def get_plan_limits(plan: str) -> Dict[str, Any]:
        """Get plan limitations and features"""
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
                'features': ['All cleaning operations', 'Multi-format export', 'Templates', 'Email support'],
                'price': 19
            },
            'enterprise': {
                'max_file_size_mb': float('inf'),
                'max_operations_monthly': float('inf'),
                'export_formats': ['csv', 'excel', 'json', 'parquet'],
                'features': ['Unlimited everything', 'API access', 'Batch processing', 'Priority support'],
                'price': 99
            }
        }
        return plan_limits.get(plan, plan_limits['free'])
    
    @staticmethod
    def can_perform_operation(user_profile: Dict, file_size_mb: float = 0) -> Tuple[bool, str]:
        """Check if user can perform operation based on plan limits"""
        try:
            plan = user_profile.get('plan', 'free')
            limits = UserManager.get_plan_limits(plan)
            usage = user_profile.get('usage_stats', {})
            
            # Check file size limit
            if file_size_mb > limits['max_file_size_mb']:
                return False, f"File size exceeds {limits['max_file_size_mb']}MB limit for {plan} plan"
            
            # Check operations limit
            operations_used = usage.get('operations_used', 0)
            if operations_used >= limits['max_operations_monthly']:
                return False, f"Monthly operations limit ({limits['max_operations_monthly']}) reached"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error checking limits: {str(e)}"

class DataProcessor:
    """Professional Data Cleaning Engine"""
    
    @staticmethod
    def load_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
        """Load uploaded file safely"""
        try:
            if uploaded_file.name.endswith('.csv'):
                # Try multiple encodings for CSV
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
                    
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                try:
                    # Check for multiple sheets
                    excel_file = pd.ExcelFile(uploaded_file)
                    if len(excel_file.sheet_names) > 1:
                        st.info(f"📑 Found {len(excel_file.sheet_names)} sheets. Using first sheet: '{excel_file.sheet_names[0]}'")
                    
                    df = pd.read_excel(uploaded_file, sheet_name=0)
                    
                    # Clean Excel artifacts
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                    
                except ImportError:
                    return None, "Excel support not available. Install: pip install openpyxl"
                except Exception as e:
                    return None, f"Error reading Excel file: {str(e)}"
            else:
                return None, "Unsupported file format"
            
            # Basic validation
            if df.empty:
                return None, "File is empty"
            
            if len(df.columns) == 0:
                return None, "No columns found"
            
            return df, "File loaded successfully!"
            
        except Exception as e:
            return None, f"Error loading file: {str(e)}"
    
    @staticmethod
    def clean_data(df: pd.DataFrame, operations: Dict) -> Tuple[Optional[pd.DataFrame], List[str]]:
        """Apply selected cleaning operations"""
        try:
            cleaned_df = df.copy()
            applied_operations = []
            
            # Remove duplicates
            if operations.get('remove_duplicates', False):
                initial_rows = len(cleaned_df)
                cleaned_df = cleaned_df.drop_duplicates()
                removed_rows = initial_rows - len(cleaned_df)
                if removed_rows > 0:
                    applied_operations.append(f"Removed {removed_rows} duplicate rows")
            
            # Handle missing values
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
                    applied_operations.append(f"Handled {handled_missing} missing values ({method})")
            
            # Standardize text
            if operations.get('standardize_text', False):
                text_columns = cleaned_df.select_dtypes(include=['object']).columns
                for col in text_columns:
                    if operations.get('text_lowercase', False):
                        cleaned_df[col] = cleaned_df[col].astype(str).str.lower()
                    if operations.get('text_trim', True):
                        cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                
                if len(text_columns) > 0:
                    applied_operations.append(f"Standardized text in {len(text_columns)} columns")
            
            # Remove outliers (simple IQR method)
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
    
    # Create two columns for login and signup
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
            
            # Show plan benefits
            plan_info = UserManager.get_plan_limits(signup_plan)
            st.info(f"**{signup_plan.title()} Plan**: {plan_info['max_file_size_mb']}MB files, {plan_info['max_operations_monthly']} operations/month")
            
            signup_submit = st.form_submit_button("📝 Create Account", use_container_width=True)
            
            if signup_submit:
                success, message = UserManager.create_account(
                    signup_username, signup_email, signup_password, signup_plan
                )
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
            <p>Choose exactly which data to clean - columns, rows, or specific conditions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Multi-Format Support</h4>
            <p>Works with CSV, Excel files. Export to multiple formats instantly</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>⚡ Professional Results</h4>
            <p>Enterprise-grade cleaning with detailed reports and analytics</p>
        </div>
        """, unsafe_allow_html=True)

def render_dashboard():
    """Render user dashboard"""
    user_profile = st.session_state.user_profile
    
    # Header with user info and controls
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"### Welcome back, **{user_profile['username']}**! 👋")
        plan_info = UserManager.get_plan_limits(user_profile['plan'])
        st.markdown(f"**{user_profile['plan'].title()} Plan** • Member since {user_profile['created_date'][:10]}")
    
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
    plan_limits = UserManager.get_plan_limits(user_profile['plan'])
    
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
    
    # Quick upgrade prompt for free users
    if user_profile['plan'] == 'free' and operations_used >= 8:  # 80% of limit
        st.markdown("""
        <div class="feature-card" style="border-left-color: #f5576c;">
            <h4>🚀 You're almost at your limit!</h4>
            <p>Upgrade to Pro for 1000 operations per month and advanced features.</p>
        </div>
        """, unsafe_allow_html=True)

def render_data_cleaner():
    """Render the main data cleaning interface"""
    st.markdown("### 🧹 Data Cleaning Workspace")
    
    user_profile = st.session_state.user_profile
    plan_limits = UserManager.get_plan_limits(user_profile['plan'])
    
    # File upload section
    st.markdown("#### 📁 Upload Your Data")
    st.info(f"**{user_profile['plan'].title()} Plan**: Max file size {plan_limits['max_file_size_mb']}MB")
    
    uploaded_file = st.file_uploader(
        "Choose CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help=f"Upload files up to {plan_limits['max_file_size_mb']}MB"
    )
    
    if uploaded_file is not None:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        # Check if user can upload this file
        can_upload, error_msg = UserManager.can_perform_operation(user_profile, file_size_mb)
        
        if not can_upload:
            st.error(f"❌ {error_msg}")
            if user_profile['plan'] == 'free':
                st.info("🚀 **Upgrade to Pro** for 100MB files and 1000 operations per month!")
            return
        
        # Load the file
        df, load_message = DataProcessor.load_file(uploaded_file)
        
        if df is not None:
            st.success(f"✅ {load_message}")
            st.session_state.uploaded_data = df
            
            # Show file statistics
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
    
    # Cleaning operations (only show if data is uploaded)
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        
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
        
        with col2:
            st.markdown("**Advanced Operations:**")
            standardize_text = st.checkbox("📝 Standardize text format")
            if standardize_text:
                text_lowercase = st.checkbox("Convert to lowercase", value=True)
                text_trim = st.checkbox("Remove extra spaces", value=True)
            
            remove_outliers = st.checkbox("📊 Remove statistical outliers")
        
        # Apply cleaning button
        if st.button("🧹 Clean Data", type="primary", use_container_width=True):
            # Check operation limits
            can_operate, error_msg = UserManager.can_perform_operation(user_profile)
            if not can_operate:
                st.error(f"❌ {error_msg}")
                return
            
            # Prepare operations dictionary
            operations = {
                'remove_duplicates': remove_duplicates,
                'handle_missing': handle_missing,
                'missing_method': missing_method if handle_missing else 'drop',
                'standardize_text': standardize_text,
                'text_lowercase': text_lowercase if standardize_text else False,
                'text_trim': text_trim if standardize_text else False,
                'remove_outliers': remove_outliers
            }
            
            # Apply cleaning operations
            with st.spinner("🔄 Cleaning your data..."):
                cleaned_df, applied_operations = DataProcessor.clean_data(df, operations)
            
            if cleaned_df is not None:
                st.session_state.cleaned_data = cleaned_df
                
                # Update user usage statistics
                st.session_state.user_profile['usage_stats']['operations_used'] += 1
                st.session_state.user_profile['usage_stats']['files_processed'] += 1
                st.session_state.user_profile['usage_stats']['data_processed_mb'] += file_size_mb
                
                # Update database
                username = st.session_state.current_user
                st.session_state.user_database[username] = st.session_state.user_profile
                
                # Show success message
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
    
    # Results section (only show if data is cleaned)
    if st.session_state.cleaned_data is not None:
        cleaned_df = st.session_state.cleaned_data
        original_df = st.session_state.uploaded_data
        
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
        
        # Show cleaned data
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
                            
                            # Add summary sheet
                            summary_data = {
                                'Metric': ['Original Rows', 'Cleaned Rows', 'Rows Removed', 'Columns', 'Missing Values'],
                                'Value': [
                                    len(original_df),
                                    len(cleaned_df),
                                    len(original_df) - len(cleaned_df),
                                    len(cleaned_df.columns),
                                    cleaned_df.isnull().sum().sum()
                                ]
                            }
