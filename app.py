import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
import io
from typing import List, Dict, Any

# Page configuration for professional SaaS look
st.set_page_config(
    page_title="No-Code Data Cleaner Pro",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern SaaS design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
    }
    .success-banner {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class DataCleaner:
    """Advanced Data Cleaning Engine for No-Code Data Cleaner SaaS"""
    
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
    
    def remove_duplicates(self, df: pd.DataFrame, columns: List[str] = None, rows: List[int] = None) -> pd.DataFrame:
        """Remove duplicate rows based on selected columns"""
        if rows is not None:
            # Apply only to selected rows
            selected_df = df.iloc[rows]
            other_df = df.drop(df.index[rows])
            cleaned_selected = selected_df.drop_duplicates(subset=columns)
            return pd.concat([other_df, cleaned_selected]).sort_index()
        else:
            return df.drop_duplicates(subset=columns)
    
    def handle_missing_values(self, df: pd.DataFrame, columns: List[str] = None, 
                            rows: List[int] = None, method: str = 'drop') -> pd.DataFrame:
        """Handle missing values with various methods"""
        working_df = df.copy()
        
        if columns is None:
            columns = df.columns.tolist()
        
        if rows is not None:
            # Apply only to selected rows and columns
            mask = working_df.index.isin(rows)
            for col in columns:
                if col in working_df.columns:
                    if method == 'drop':
                        working_df = working_df.dropna(subset=[col])
                    elif method == 'forward_fill':
                        working_df.loc[mask, col] = working_df.loc[mask, col].fillna(method='ffill')
                    elif method == 'backward_fill':
                        working_df.loc[mask, col] = working_df.loc[mask, col].fillna(method='bfill')
                    elif method == 'mean' and working_df[col].dtype in ['int64', 'float64']:
                        mean_val = working_df.loc[mask, col].mean()
                        working_df.loc[mask, col] = working_df.loc[mask, col].fillna(mean_val)
                    elif method == 'median' and working_df[col].dtype in ['int64', 'float64']:
                        median_val = working_df.loc[mask, col].median()
                        working_df.loc[mask, col] = working_df.loc[mask, col].fillna(median_val)
                    elif method == 'mode':
                        mode_val = working_df.loc[mask, col].mode()
                        if not mode_val.empty:
                            working_df.loc[mask, col] = working_df.loc[mask, col].fillna(mode_val[0])
        else:
            # Apply to all selected columns
            for col in columns:
                if col in working_df.columns:
                    if method == 'drop':
                        working_df = working_df.dropna(subset=[col])
                    elif method == 'forward_fill':
                        working_df[col] = working_df[col].fillna(method='ffill')
                    elif method == 'backward_fill':
                        working_df[col] = working_df[col].fillna(method='bfill')
                    elif method == 'mean' and working_df[col].dtype in ['int64', 'float64']:
                        working_df[col] = working_df[col].fillna(working_df[col].mean())
                    elif method == 'median' and working_df[col].dtype in ['int64', 'float64']:
                        working_df[col] = working_df[col].fillna(working_df[col].median())
                    elif method == 'mode':
                        mode_val = working_df[col].mode()
                        if not mode_val.empty:
                            working_df[col] = working_df[col].fillna(mode_val[0])
        
        return working_df
    
    def standardize_text(self, df: pd.DataFrame, columns: List[str] = None, 
                        rows: List[int] = None, operations: List[str] = None) -> pd.DataFrame:
        """Standardize text in selected columns and rows"""
        working_df = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns.tolist()
        
        if operations is None:
            operations = ['lowercase', 'trim', 'remove_special']
        
        for col in columns:
            if col in working_df.columns and working_df[col].dtype == 'object':
                if rows is not None:
                    mask = working_df.index.isin(rows)
                    if 'lowercase' in operations:
                        working_df.loc[mask, col] = working_df.loc[mask, col].str.lower()
                    if 'uppercase' in operations:
                        working_df.loc[mask, col] = working_df.loc[mask, col].str.upper()
                    if 'title' in operations:
                        working_df.loc[mask, col] = working_df.loc[mask, col].str.title()
                    if 'trim' in operations:
                        working_df.loc[mask, col] = working_df.loc[mask, col].str.strip()
                    if 'remove_special' in operations:
                        working_df.loc[mask, col] = working_df.loc[mask, col].str.replace(r'[^\w\s]', '', regex=True)
                else:
                    if 'lowercase' in operations:
                        working_df[col] = working_df[col].str.lower()
                    if 'uppercase' in operations:
                        working_df[col] = working_df[col].str.upper()
                    if 'title' in operations:
                        working_df[col] = working_df[col].str.title()
                    if 'trim' in operations:
                        working_df[col] = working_df[col].str.strip()
                    if 'remove_special' in operations:
                        working_df[col] = working_df[col].str.replace(r'[^\w\s]', '', regex=True)
        
        return working_df
    
    def fix_dates(self, df: pd.DataFrame, columns: List[str] = None, 
                  rows: List[int] = None, target_format: str = '%Y-%m-%d') -> pd.DataFrame:
        """Fix and standardize date formats"""
        working_df = df.copy()
        
        if columns is None:
            # Auto-detect potential date columns
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
        """Check if text looks like a date"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        return any(re.match(pattern, str(text)) for pattern in date_patterns)
    
    def remove_outliers(self, df: pd.DataFrame, columns: List[str] = None, 
                       rows: List[int] = None, method: str = 'iqr') -> pd.DataFrame:
        """Remove outliers using IQR or Z-score method"""
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
                elif method == 'zscore':
                    z_scores = np.abs((data - data.mean()) / data.std())
                    outlier_mask = z_scores > 3
                
                if rows is not None:
                    row_indices = working_df.index[working_df.index.isin(rows)]
                    outlier_indices = row_indices[outlier_mask]
                else:
                    outlier_indices = working_df.index[outlier_mask]
                
                working_df = working_df.drop(outlier_indices)
        
        return working_df
    
    def trim_whitespace(self, df: pd.DataFrame, columns: List[str] = None, 
                       rows: List[int] = None) -> pd.DataFrame:
        """Remove leading/trailing whitespace"""
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
        """Convert data types for selected columns"""
        working_df = df.copy()
        
        for col, target_type in conversions.items():
            if col in working_df.columns:
                try:
                    if rows is not None:
                        mask = working_df.index.isin(rows)
                        if target_type == 'numeric':
                            working_df.loc[mask, col] = pd.to_numeric(working_df.loc[mask, col], errors='coerce')
                        elif target_type == 'string':
                            working_df.loc[mask, col] = working_df.loc[mask, col].astype(str)
                        elif target_type == 'datetime':
                            working_df.loc[mask, col] = pd.to_datetime(working_df.loc[mask, col], errors='coerce')
                    else:
                        if target_type == 'numeric':
                            working_df[col] = pd.to_numeric(working_df[col], errors='coerce')
                        elif target_type == 'string':
                            working_df[col] = working_df[col].astype(str)
                        elif target_type == 'datetime':
                            working_df[col] = pd.to_datetime(working_df[col], errors='coerce')
                except Exception as e:
                    st.warning(f"Could not convert {col} to {target_type}: {str(e)}")
        
        return working_df
    
    def remove_empty_rows(self, df: pd.DataFrame, rows: List[int] = None) -> pd.DataFrame:
        """Remove completely empty rows"""
        if rows is not None:
            selected_rows = df.iloc[rows]
            other_rows = df.drop(df.index[rows])
            cleaned_selected = selected_rows.dropna(how='all')
            return pd.concat([other_rows, cleaned_selected]).sort_index()
        else:
            return df.dropna(how='all')

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧹 No-Code Data Cleaner Pro</h1>
        <p>Clean your data with precision - Choose exactly which columns and rows to process</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'cleaned_df' not in st.session_state:
        st.session_state.cleaned_df = None
    if 'cleaning_history' not in st.session_state:
        st.session_state.cleaning_history = []
    
    # Initialize cleaner
    cleaner = DataCleaner()
    
    # Sidebar for file upload and basic info
    with st.sidebar:
        st.markdown("### 📁 Upload Your Data")
        uploaded_file = st.file_uploader(
            "Choose CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your data file to start cleaning"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    st.session_state.df = pd.read_csv(uploaded_file)
                else:
                    st.session_state.df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File loaded successfully!")
                st.markdown(f"**Rows:** {len(st.session_state.df)}")
                st.markdown(f"**Columns:** {len(st.session_state.df.columns)}")
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    if st.session_state.df is not None:
        # Main content area
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 Data Preview", "🧹 Selective Cleaning", "📊 Results", "📋 History"])
        
        with tab1:
            st.markdown("### 📋 Your Data Preview")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3>{}</h3>
                    <p>Total Rows</p>
                </div>
                """.format(len(st.session_state.df)), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h3>{}</h3>
                    <p>Total Columns</p>
                </div>
                """.format(len(st.session_state.df.columns)), unsafe_allow_html=True)
            
            with col3:
                missing_count = st.session_state.df.isnull().sum().sum()
                st.markdown("""
                <div class="metric-card">
                    <h3>{}</h3>
                    <p>Missing Values</p>
                </div>
                """.format(missing_count), unsafe_allow_html=True)
            
            st.dataframe(st.session_state.df, use_container_width=True, height=400)
        
        with tab2:
            st.markdown("### 🎯 Selective Data Cleaning")
            
            # Column selection
            st.markdown("#### 📊 Choose Columns to Clean")
            all_columns = st.session_state.df.columns.tolist()
            selected_columns = st.multiselect(
                "Select specific columns (leave empty to apply to all columns):",
                options=all_columns,
                help="Choose which columns you want to clean"
            )
            
            # Row selection options
            st.markdown("#### 📄 Choose Rows to Clean")
            row_selection_type = st.radio(
                "How do you want to select rows?",
                ["All Rows", "Row Range", "Specific Rows", "Conditional Selection"],
                help="Choose your row selection method"
            )
            
            selected_rows = None
            
            if row_selection_type == "Row Range":
                col1, col2 = st.columns(2)
                with col1:
                    start_row = st.number_input("Start Row", min_value=0, max_value=len(st.session_state.df)-1, value=0)
                with col2:
                    end_row = st.number_input("End Row", min_value=0, max_value=len(st.session_state.df)-1, value=min(100, len(st.session_state.df)-1))
                selected_rows = list(range(int(start_row), int(end_row) + 1))
                st.info(f"Selected {len(selected_rows)} rows for cleaning")
                
            elif row_selection_type == "Specific Rows":
                row_input = st.text_input(
                    "Enter row numbers (comma-separated, 0-indexed):",
                    help="Example: 0,5,10,15"
                )
                if row_input:
                    try:
                        selected_rows = [int(x.strip()) for x in row_input.split(',') if x.strip().isdigit()]
                        selected_rows = [r for r in selected_rows if 0 <= r < len(st.session_state.df)]
                        st.info(f"Selected {len(selected_rows)} specific rows")
                    except:
                        st.error("Please enter valid row numbers")
                        
            elif row_selection_type == "Conditional Selection":
                if selected_columns:
                    condition_col = st.selectbox("Select column for condition:", selected_columns)
                    condition_type = st.selectbox("Condition type:", ["Contains", "Equals", "Greater than", "Less than", "Is null", "Is not null"])
                    
                    if condition_type not in ["Is null", "Is not null"]:
                        condition_value = st.text_input("Condition value:")
                    else:
                        condition_value = None
                    
                    if st.button("Apply Condition"):
                        try:
                            if condition_type == "Contains" and condition_value:
                                mask = st.session_state.df[condition_col].astype(str).str.contains(condition_value, na=False)
                            elif condition_type == "Equals" and condition_value:
                                mask = st.session_state.df[condition_col] == condition_value
                            elif condition_type == "Greater than" and condition_value:
                                mask = pd.to_numeric(st.session_state.df[condition_col], errors='coerce') > float(condition_value)
                            elif condition_type == "Less than" and condition_value:
                                mask = pd.to_numeric(st.session_state.df[condition_col], errors='coerce') < float(condition_value)
                            elif condition_type == "Is null":
                                mask = st.session_state.df[condition_col].isnull()
                            elif condition_type == "Is not null":
                                mask = st.session_state.df[condition_col].notnull()
                            
                            selected_rows = st.session_state.df[mask].index.tolist()
                            st.info(f"Found {len(selected_rows)} rows matching the condition")
                        except Exception as e:
                            st.error(f"Error applying condition: {str(e)}")
            
            # Cleaning operations
            st.markdown("#### 🛠️ Select Cleaning Operations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Basic Cleaning:**")
                remove_duplicates = st.checkbox("Remove Duplicates")
                handle_missing = st.checkbox("Handle Missing Values")
                trim_whitespace = st.checkbox("Trim Whitespace")
                remove_empty_rows = st.checkbox("Remove Empty Rows")
                
            with col2:
                st.markdown("**Advanced Cleaning:**")
                standardize_text = st.checkbox("Standardize Text")
                fix_dates = st.checkbox("Fix Date Formats")
                remove_outliers = st.checkbox("Remove Outliers")
                convert_types = st.checkbox("Convert Data Types")
            
            # Operation-specific settings
            if handle_missing:
                missing_method = st.selectbox(
                    "Missing values method:",
                    ["drop", "forward_fill", "backward_fill", "mean", "median", "mode"]
                )
            
            if standardize_text:
                text_operations = st.multiselect(
                    "Text standardization options:",
                    ["lowercase", "uppercase", "title", "trim", "remove_special"],
                    default=["lowercase", "trim"]
                )
            
            if fix_dates:
                date_format = st.selectbox(
                    "Target date format:",
                    ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"]
                )
            
            if remove_outliers:
                outlier_method = st.selectbox("Outlier detection method:", ["iqr", "zscore"])
            
            if convert_types:
                st.markdown("**Data Type Conversions:**")
                conversions = {}
                if selected_columns or not selected_columns:
                    cols_to_convert = selected_columns if selected_columns else all_columns[:5]  # Limit to prevent UI overflow
                    for col in cols_to_convert:
                        new_type = st.selectbox(
                            f"Convert {col} to:",
                            ["Keep current", "numeric", "string", "datetime"],
                            key=f"convert_{col}"
                        )
                        if new_type != "Keep current":
                            conversions[col] = new_type
            
            # Apply cleaning
            if st.button("🧹 Clean Data", type="primary"):
                try:
                    working_df = st.session_state.df.copy()
                    operations_applied = []
                    
                    with st.spinner("Cleaning your data..."):
                        if remove_duplicates:
                            working_df = cleaner.remove_duplicates(working_df, selected_columns, selected_rows)
                            operations_applied.append("Removed duplicates")
                        
                        if handle_missing:
                            working_df = cleaner.handle_missing_values(
                                working_df, selected_columns, selected_rows, missing_method
                            )
                            operations_applied.append(f"Handled missing values ({missing_method})")
                        
                        if trim_whitespace:
                            working_df = cleaner.trim_whitespace(working_df, selected_columns, selected_rows)
                            operations_applied.append("Trimmed whitespace")
                        
                        if remove_empty_rows:
                            working_df = cleaner.remove_empty_rows(working_df, selected_rows)
                            operations_applied.append("Removed empty rows")
                        
                        if standardize_text:
                            working_df = cleaner.standardize_text(
                                working_df, selected_columns, selected_rows, text_operations
                            )
                            operations_applied.append(f"Standardized text ({', '.join(text_operations)})")
                        
                        if fix_dates:
                            working_df = cleaner.fix_dates(working_df, selected_columns, selected_rows, date_format)
                            operations_applied.append(f"Fixed dates to {date_format}")
                        
                        if remove_outliers:
                            working_df = cleaner.remove_outliers(
                                working_df, selected_columns, selected_rows, outlier_method
                            )
                            operations_applied.append(f"Removed outliers ({outlier_method})")
                        
                        if convert_types and conversions:
                            working_df = cleaner.convert_data_types(working_df, conversions, selected_rows)
                            operations_applied.append(f"Converted data types: {conversions}")
                    
                    st.session_state.cleaned_df = working_df
                    st.session_state.cleaning_history.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'operations': operations_applied,
                        'columns_affected': selected_columns if selected_columns else 'All columns',
                        'rows_affected': f"{len(selected_rows)} specific rows" if selected_rows else "All rows",
                        'original_shape': st.session_state.df.shape,
                        'cleaned_shape': working_df.shape
                    })
                    
                    st.markdown("""
                    <div class="success-banner">
                        <h3>✅ Data Cleaned Successfully!</h3>
                        <p>Applied {} operations to your selected data</p>
                    </div>
                    """.format(len(operations_applied)), unsafe_allow_html=True)
                    
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Error during cleaning: {str(e)}")
        
        with tab3:
            if st.session_state.cleaned_df is not None:
                st.markdown("### 📊 Cleaning Results")
                
                # Before and after comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Before Cleaning:**")
                    st.markdown(f"Rows: {len(st.session_state.df)}")
                    st.markdown(f"Columns: {len(st.session_state.df.columns)}")
                    st.markdown(f"Missing values: {st.session_state.df.isnull().sum().sum()}")
                
                with col2:
                    st.markdown("**After Cleaning:**")
                    st.markdown(f"Rows: {len(st.session_state.cleaned_df)}")
                    st.markdown(f"Columns: {len(st.session_state.cleaned_df.columns)}")
                    st.markdown(f"Missing values: {st.session_state.cleaned_df.isnull().sum().sum()}")
                
                st.markdown("### 📋 Cleaned Data Preview")
                st.dataframe(st.session_state.cleaned_df, use_container_width=True, height=400)
                
                # Download buttons for multiple formats
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # CSV Download (always available)
                    csv_data = st.session_state.cleaned_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv_data,
                        file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # Excel Download (if openpyxl is available)
                    if OPENPYXL_AVAILABLE:
                        def create_excel_download():
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                st.session_state.cleaned_df.to_excel(writer, sheet_name='Cleaned_Data', index=False)
                                
                                # Add a summary sheet
                                summary_data = {
                                    'Metric': ['Original Rows', 'Cleaned Rows', 'Original Columns', 'Cleaned Columns', 'Missing Values Removed'],
                                    'Value': [
                                        len(st.session_state.df),
                                        len(st.session_state.cleaned_df),
                                        len(st.session_state.df.columns),
                                        len(st.session_state.cleaned_df.columns),
                                        st.session_state.df.isnull().sum().sum() - st.session_state.cleaned_df.isnull().sum().sum()
                                    ]
                                }
                                summary_df = pd.DataFrame(summary_data)
                                summary_df.to_excel(writer, sheet_name='Cleaning_Summary', index=False)
                            
                            return output.getvalue()
                        
                        excel_data = create_excel_download()
                        st.download_button(
                            label="📊 Download as Excel",
                            data=excel_data,
                            file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.button(
                            "📊 Excel Export (Install openpyxl)",
                            disabled=True,
                            help="Install openpyxl to enable Excel export",
                            use_container_width=True
                        )
                
                with col3:
                    # JSON Download (always available)
                    json_data = st.session_state.cleaned_df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="🔗 Download as JSON",
                        data=json_data,
                        file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            else:
                st.info("No cleaned data available. Please run cleaning operations first.")
        
        with tab4:
            st.markdown("### 📋 Cleaning History")
            if st.session_state.cleaning_history:
                for i, operation in enumerate(reversed(st.session_state.cleaning_history), 1):
                    with st.expander(f"Operation {i} - {operation['timestamp']}"):
                        st.markdown(f"**Operations Applied:** {', '.join(operation['operations'])}")
                        st.markdown(f"**Columns Affected:** {operation['columns_affected']}")
                        st.markdown(f"**Rows Affected:** {operation['rows_affected']}")
                        st.markdown(f"**Original Shape:** {operation['original_shape']}")
                        st.markdown(f"**Final Shape:** {operation['cleaned_shape']}")
            else:
                st.info("No cleaning operations performed yet.")
    
    else:
        # Landing section when no file is uploaded
        st.markdown("""
        <div class="feature-card">
            <h3>🚀 Welcome to No-Code Data Cleaner Pro</h3>
            <p>The most advanced selective data cleaning platform for businesses and data professionals.</p>
            <ul>
                <li>✅ <strong>Selective Column Cleaning</strong> - Choose exactly which columns to process</li>
                <li>🎯 <strong>Precise Row Selection</strong> - Target specific rows, ranges, or conditions</li>
                <li>🔧 <strong>8+ Cleaning Operations</strong> - From duplicates to outliers and data types</li>
                <li>📊 <strong>Real-time Preview</strong> - See changes before applying</li>
                <li>📈 <strong>Operation History</strong> - Track all your cleaning steps</li>
                <li>⬇️ <strong>Instant Download</strong> - Get your cleaned data immediately</li>
            </ul>
        </div>
        
        <div class="feature-card">
            <h4>🎯 Perfect For:</h4>
            <p><strong>Data Analysts</strong> who need precision cleaning • <strong>Business Users</strong> who want no-code solutions • <strong>Teams</strong> processing large datasets</p>
        </div>
        
        <div style="text-align: center; margin-top: 2rem;">
            <p style="font-size: 1.2em; color: #667eea;"><strong>👆 Upload your CSV or Excel file in the sidebar to get started!</strong></p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
