"""
============================================
UTILITY FUNCTIONS
Fungsi-fungsi helper untuk preprocessing dan evaluasi
============================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error


def validate_file_type(uploaded_file):
    """
    Validasi tipe file yang di-upload
    
    Args:
        uploaded_file: File yang di-upload
    
    Returns:
        bool: True jika valid (CSV atau Excel)
    """
    allowed_types = ['csv', 'xlsx', 'xls']
    file_extension = uploaded_file.name.split('.')[-1].lower()
    return file_extension in allowed_types


def load_dataset(uploaded_file):
    """
    Load dataset dari file CSV atau Excel
    
    Args:
        uploaded_file: File yang di-upload
    
    Returns:
        pd.DataFrame: Dataset yang dimuat atau None jika gagal
    """
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            return None
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error membaca file: {str(e)}")
        return None


def preprocess_dataset(df):
    """
    Preprocessing dataset dengan validasi robust
    
    Args:
        df: DataFrame raw
    
    Returns:
        pd.DataFrame: DataFrame yang sudah diproses, atau None jika gagal/kosong
    """
    try:
        # Validasi input
        if df is None or len(df) == 0:
            st.error("❌ Dataset kosong atau tidak valid!")
            return None
        
        if len(df.columns) == 0:
            st.error("❌ Dataset tidak memiliki kolom!")
            return None
        
        df_processed = df.copy()
        
        # Rename kolom pertama menjadi 'Periode' jika belum
        first_col = df_processed.columns[0]
        if first_col.lower() != 'periode':
            df_processed.rename(columns={first_col: 'Periode'}, inplace=True)
        
        # Cek apakah kolom 'Periode' ada
        if 'Periode' not in df_processed.columns:
            st.error("❌ Kolom 'Periode' tidak ditemukan dalam dataset!")
            return None
        
        # Convert Periode ke datetime (coba berbagai format)
        periode_col = df_processed['Periode'].astype(str).str.strip()
        
        # Jika format range tanggal (misal '01/01/2024 - 07/01/2024'), ambil bagian depan saja
        # Deteksi jika ada '-' (indikator range)
        if periode_col.str.contains('-', regex=False).any():
            # Extract tanggal sebelum '-'
            periode_col = periode_col.str.split('-').str[0].str.strip()
        
        # Coba format DD/MM/YYYY terlebih dahulu
        df_processed['Periode'] = pd.to_datetime(
            periode_col, 
            format='%d/%m/%Y', 
            errors='coerce'
        )
        
        # Jika masih banyak NaT, coba format lain (ISO, US, etc)
        nat_count = df_processed['Periode'].isna().sum()
        if nat_count > len(df_processed) / 2:
            # Coba format yang lebih fleksibel
            df_processed['Periode'] = pd.to_datetime(periode_col, errors='coerce')
        
        # Drop rows dengan tanggal invalid
        df_processed = df_processed.dropna(subset=['Periode'])
        
        # Cek apakah ada data setelah drop tanggal invalid
        if len(df_processed) == 0:
            st.error("❌ Tidak ada data dengan tanggal yang valid! Cek format tanggal Anda (DD/MM/YYYY).")
            return None
        
        # Set Periode sebagai index
        df_processed.set_index('Periode', inplace=True)
        
        # Sort by index
        df_processed = df_processed.sort_index()
        
        # Cek apakah ada kolom data selain Periode
        if len(df_processed.columns) == 0:
            st.error("❌ Tidak ada kolom data (hanya Periode). Tambahkan kolom komoditas/harga!")
            return None
        
        # Convert semua kolom ke numeric
        for col in df_processed.columns:
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
        
        # Drop kolom yang semua value NaN
        df_processed = df_processed.dropna(axis=1, how='all')
        
        # Cek final result
        if df_processed.empty:
            st.error("❌ Semua data menjadi NaN setelah preprocessing. Cek format angka di dataset!")
            return None
        
        return df_processed
    
    except Exception as e:
        st.error(f"❌ Error preprocessing: {str(e)}")
        return None


def check_missing_values(df):
    """
    Cek missing values dalam dataset
    
    Args:
        df: DataFrame
    
    Returns:
        dict: Info missing values
    """
    missing_info = {}
    
    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_pct = (missing_count / len(df)) * 100
        
        if missing_count > 0:
            missing_info[col] = {
                'count': missing_count,
                'percentage': missing_pct
            }
    
    return missing_info


def train_test_split(df, test_size=0.2):
    """
    Split data menjadi train dan test
    
    Args:
        df: DataFrame
        test_size: Proporsi test (0-1)
    
    Returns:
        tuple: (train_df, test_df)
    """
    split_idx = int(len(df) * (1 - test_size))
    
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    return train_df, test_df


def format_number(num):
    """
    Format number dengan separator
    
    Args:
        num: Angka
    
    Returns:
        str: Angka yang diformat
    """
    if pd.isna(num):
        return "N/A"
    
    try:
        return f"{num:,.2f}"
    except:
        return str(num)


def calculate_mae(y_true, y_pred):
    """
    Hitung Mean Absolute Error
    
    Args:
        y_true: Nilai asli
        y_pred: Nilai prediksi
    
    Returns:
        float: MAE
    """
    try:
        return mean_absolute_error(y_true, y_pred)
    except:
        return None


def calculate_rmse(y_true, y_pred):
    """
    Hitung Root Mean Squared Error
    
    Args:
        y_true: Nilai asli
        y_pred: Nilai prediksi
    
    Returns:
        float: RMSE
    """
    try:
        mse = mean_squared_error(y_true, y_pred)
        return np.sqrt(mse)
    except:
        return None


def calculate_mape(y_true, y_pred):
    """
    Hitung Mean Absolute Percentage Error
    
    Args:
        y_true: Nilai asli
        y_pred: Nilai prediksi
    
    Returns:
        float: MAPE
    """
    try:
        # Tambahkan small value untuk menghindari division by zero
        return mean_absolute_percentage_error(y_true, y_pred)
    except:
        return None


def calculate_metrics_summary(y_true, y_pred):
    """
    Hitung semua metrik dan return dalam dictionary
    
    Args:
        y_true: Nilai asli
        y_pred: Nilai prediksi
    
    Returns:
        dict: Dictionary dengan MAE, RMSE, MAPE
    """
    metrics = {
        'MAE': calculate_mae(y_true, y_pred),
        'RMSE': calculate_rmse(y_true, y_pred),
        'MAPE': calculate_mape(y_true, y_pred)
    }
    
    return metrics


def convert_df_to_csv(df):
    """
    Convert DataFrame ke CSV bytes
    
    Args:
        df: DataFrame
    
    Returns:
        bytes: CSV data
    """
    return df.to_csv(index=True).encode('utf-8')


def get_date_range_info(df):
    """
    Dapatkan info range tanggal dari dataset
    
    Args:
        df: DataFrame dengan index datetime
    
    Returns:
        dict: Info range tanggal
    """
    try:
        if df is None or len(df) == 0:
            return None

        start = df.index.min()
        end = df.index.max()

        # If start or end are NaT, return None to signal invalid date range
        try:
            import pandas as _pd
            if _pd.isna(start) or _pd.isna(end):
                return None
        except Exception:
            # If pandas not available for some reason, fall back to checking None
            if start is None or end is None:
                return None

        date_info = {
            'start_date': start,
            'end_date': end,
            'total_periods': len(df)
        }
        return date_info
    except Exception:
        return None


def validate_column_selection(df, selected_columns):
    """
    Validasi apakah kolom yang dipilih tersedia dan valid
    
    Args:
        df: DataFrame
        selected_columns: List kolom yang dipilih
    
    Returns:
        bool: True jika valid
    """
    if not selected_columns:
        return False
    
    for col in selected_columns:
        if col not in df.columns:
            return False
    
    return True


def check_data_quality(df, column):
    """
    Check kualitas data dalam kolom tertentu
    
    Args:
        df: DataFrame
        column: Nama kolom
    
    Returns:
        dict: Info kualitas data
    """
    quality_info = {
        'total_records': len(df),
        'missing_values': df[column].isna().sum(),
        'min_value': df[column].min(),
        'max_value': df[column].max(),
        'mean_value': df[column].mean(),
        'std_dev': df[column].std()
    }
    
    return quality_info


def fill_missing_values(df, method='ffill'):
    """
    Fill missing values dalam DataFrame
    
    Args:
        df: DataFrame
        method: Method pengisian ('ffill', 'bfill', 'interpolate')
    
    Returns:
        pd.DataFrame: DataFrame dengan missing values terisi
    """
    df_filled = df.copy()
    
    if method == 'ffill':
        df_filled = df_filled.fillna(method='ffill')
    elif method == 'bfill':
        df_filled = df_filled.fillna(method='bfill')
    elif method == 'interpolate':
        df_filled = df_filled.interpolate(method='linear')
    
    # Fill sisa NaN dengan backward fill jika masih ada
    df_filled = df_filled.fillna(method='bfill')
    
    return df_filled


def convert_df_to_excel(df, filename='export.xlsx'):
    """
    Convert DataFrame ke Excel file
    
    Args:
        df: DataFrame
        filename: Nama file output
    
    Returns:
        bytes: Excel file data atau None
    """
    try:
        # Gunakan ExcelWriter untuk save ke bytes
        import io
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=True)
        
        output.seek(0)
        return output.getvalue()
    except:
        return None


def create_forecast_dates(last_date, periods, frequency='W'):
    """
    Create forecast dates
    
    Args:
        last_date: Tanggal terakhir dari data
        periods: Jumlah periode forecast
        frequency: Frekuensi ('D', 'W', 'M', dll)
    
    Returns:
        pd.DatetimeIndex: Index tanggal untuk forecast
    """
    forecast_dates = pd.date_range(start=last_date, periods=periods+1, freq=frequency)[1:]
    return forecast_dates
