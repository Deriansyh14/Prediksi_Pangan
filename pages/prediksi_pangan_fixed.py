"""
============================================
HALAMAN PREDIKSI PANGAN
Halaman utama untuk analisis dan prediksi
============================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
import json

# Tambahkan path src ke system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils import (
    validate_file_type, load_dataset, preprocess_dataset,
    check_missing_values, train_test_split, format_number,
    calculate_metrics_summary, convert_df_to_csv,
    get_date_range_info
)
from src.load_model import SARIMAParamsLoader, create_default_params_file
from src.forecasting import (
    train_and_evaluate, forecast_future, auto_tune_sarima, auto_tune_per_commodity
)

# Konfigurasi halaman
st.set_page_config(
    page_title="Prediksi Harga Pangan",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional Design
st.markdown("""
    <style>
    /* Main background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e8ecf1 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Sidebar text - improved contrast */
    [data-testid="stSidebar"] {
        color: #ecf0f1 !important;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #ecf0f1 !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ecf0f1 !important;
        font-weight: 600 !important;
        margin-bottom: 12px !important;
    }
    
    [data-testid="stSidebar"] button {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Input fields in sidebar - better visibility */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select {
        color: #2c3e50 !important;
        background-color: #ecf0f1 !important;
    }
    
    /* Title styling */
    h1 {
        color: #2c3e50 !important;
        font-weight: 700 !important;
        margin-bottom: 20px !important;
    }
    
    h2 {
        color: #34495e !important;
        font-weight: 600 !important;
        margin-top: 25px !important;
        margin-bottom: 15px !important;
        padding-bottom: 10px !important;
        border-bottom: 2px solid #3498db !important;
    }
    
    h3 {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    h4 {
        color: #34495e !important;
        font-weight: 500 !important;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        box-shadow: 0 2px 8px rgba(52, 73, 94, 0.1);
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 8px !important;
        padding: 12px 15px !important;
        margin: 15px 0 !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(52, 73, 94, 0.15) !important;
    }
    
    /* Selectbox & input */
    .stSelectbox, .stSlider, .stNumberInput {
        margin: 10px 0 !important;
    }
    
    /* Dataframe */
    .stDataframe {
        margin: 15px 0 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #ecf0f1 0%, #f8f9fa 100%) !important;
        border-radius: 6px !important;
    }
    
    /* Text spacing */
    p {
        line-height: 1.6 !important;
        margin: 10px 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Header dengan logo dan deskripsi
col_header1, col_header2 = st.columns([1, 4])
with col_header1:
    st.write("📊")
with col_header2:
    st.title("Prediksi Harga Pangan")
    st.caption("Sistem Prediksi Harga Komoditas Pangan dengan ARIMA/SARIMA")

st.markdown("---")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'params_loader' not in st.session_state:
    st.session_state.params_loader = SARIMAParamsLoader()
if 'tune_result' not in st.session_state:
    st.session_state.tune_result = None
if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None
if 'forecast_result' not in st.session_state:
    st.session_state.forecast_result = None
if 'validation_commodity' not in st.session_state:
    st.session_state.validation_commodity = None

# ===== SIDEBAR =====
with st.sidebar:
    st.header("📁 Pengaturan Dataset")
    
    # Upload dataset
    st.subheader("Upload Dataset")
    uploaded_file = st.file_uploader(
        "Pilih file CSV atau Excel",
        type=['csv', 'xlsx', 'xls']
    )
    
    if uploaded_file:
        if validate_file_type(uploaded_file):
            with st.spinner("⏳ Memuat dataset..."):
                df_raw = load_dataset(uploaded_file)
                
                if df_raw is not None:
                    df_processed = preprocess_dataset(df_raw)
                    st.session_state.df = df_processed
                    st.session_state.current_dataset_file = uploaded_file.name
                    
                    # RESET TUNING STATUS ketika dataset baru diupload
                    params = st.session_state.params_loader.load_params()
                    for commodity in params.keys():
                        params[commodity]['is_tuned'] = False
                        params[commodity]['aic'] = None
                        params[commodity]['bic'] = None
                        params[commodity]['tuning_date'] = None
                    
                    # Save reset params
                    os.makedirs('models', exist_ok=True)
                    with open('models/best_params.json', 'w', encoding='utf-8') as f:
                        json.dump(params, f, indent=4, ensure_ascii=False)
                    st.session_state.params_loader = SARIMAParamsLoader()
                    
                    st.success("✅ Dataset berhasil dimuat! Status tuning di-reset.")
                    
                    # Tampilkan info dataset
                    with st.expander("📊 Info Dataset", expanded=True):
                        date_info = get_date_range_info(st.session_state.df)
                        # Safely handle missing/invalid dates
                        if date_info and date_info.get('start_date') is not None and not pd.isna(date_info.get('start_date')) \
                                and date_info.get('end_date') is not None and not pd.isna(date_info.get('end_date')):
                            st.write(f"📅 Periode: **{date_info['start_date'].strftime('%d/%m/%Y')} - {date_info['end_date'].strftime('%d/%m/%Y')}**")
                        else:
                            st.write("📅 Periode: Tidak tersedia")

                        if date_info and date_info.get('total_periods') is not None:
                            st.write(f"📈 Total Data: **{date_info['total_periods']} periode**")
                        else:
                            st.write(f"📈 Total Data: **{len(st.session_state.df)} periode**")

                        st.write(f"🌾 Komoditas: **{len(st.session_state.df.columns)}** komoditas")
        else:
            st.error("❌ Format file tidak valid! Gunakan CSV atau Excel.")
    
    # Divider
    st.markdown("---")
    
    # Utilitas
    st.subheader("⚙️ Utilitas")
    if st.button("🔄 Buat Parameter Default", use_container_width=True):
        create_default_params_file()
        st.session_state.params_loader = SARIMAParamsLoader()
        st.success("✅ File parameter default dibuat!")

# ===== MAIN CONTENT =====
if st.session_state.df is None:
    # Tampilan ketika belum ada dataset
    st.info("👈 **Silakan upload dataset terlebih dahulu** dari sidebar di sebelah kiri untuk memulai analisis.")
    
    st.markdown("""
    ---
    
    ## 📋 Format Dataset yang Diperlukan
    
    Dataset harus memiliki struktur berikut:
    
    | Periode | Beras Premium | Bawang Merah | Bawang Putih |
    |---------|---------------|-------------|-------------|
    | 01/01/2023 | 12500 | 35000 | 28000 |
    | 08/01/2023 | 12700 | 36000 | 28500 |
    | 15/01/2023 | 12600 | 35500 | 28200 |
    
    ### ✅ Persyaratan Format:
    - **Kolom pertama:** Tanggal/Periode (format: DD/MM/YYYY)
    - **Kolom selanjutnya:** Harga komoditas (angka)
    - **Range tanggal:** Sistem otomatis mengambil tanggal awal
    
    ### 📊 Fitur Aplikasi:
    1. **Explorasi Data** - Visualisasi dan statistik dataset
    2. **Prediksi** - Tuning → Validasi → Forecasting per komoditas
    3. **Evaluasi Model** - Info parameter dan akurasi
    4. **Auto-Tuning** - Manual tuning dengan referensi
    """)
    
else:
    df = st.session_state.df
    
    # Tab navigasi
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Explorasi Data", 
        "🔮 Prediksi", 
        "📈 Evaluasi Model",
        "🔍 Auto-Tuning"
    ])
    
    # ===== TAB 1: EXPLORASI DATA =====
    with tab1:
        st.header("📊 Explorasi Data Time Series")
        
        # Validasi DataFrame tidak kosong
        if df is None or len(df) == 0 or len(df.columns) == 0:
            st.error("❌ Dataset kosong!")
        else:
            # Row 1: Statistik Deskriptif
            st.subheader("Statistik Deskriptif Dataset")
            col_stat1, col_stat2 = st.columns([2, 1])
            
            with col_stat1:
                # Tabel statistik
                st.dataframe(df.describe().T, use_container_width=True)
            
            with col_stat2:
                # Missing values
                st.markdown("**Missing Values:**")
                missing = check_missing_values(df)
                if missing and any(missing.values()):
                    for col, count in missing.items():
                        if count > 0:
                            st.warning(f"{col}: {count} ({count/len(df)*100:.1f}%)")
                else:
                    st.success("✅ Tidak ada missing values")
        
        # Row 2: Visualisasi
        st.subheader("📈 Visualisasi Time Series")
        commodities = df.columns.tolist()
        
        col_select, col_button = st.columns([3, 1])
        with col_select:
            selected_commodity = st.selectbox(
                "Pilih komoditas untuk ditampilkan:",
                commodities,
                key="explore_commodity"
            )
        
        # Plot time series
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[selected_commodity],
            mode='lines',
            name=selected_commodity,
            line=dict(color='#667eea', width=2)
        ))
        
        fig.update_layout(
            title=f"Time Series Harga {selected_commodity}",
            xaxis_title="Tanggal",
            yaxis_title="Harga",
            hovermode='x unified',
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Plot semua komoditas
        with st.expander("📊 Lihat Semua Komoditas"):
            fig_all = go.Figure()
            
            for col in commodities:
                fig_all.add_trace(go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode='lines',
                    name=col
                ))
            
            fig_all.update_layout(
                title="Time Series Semua Komoditas",
                xaxis_title="Tanggal",
                yaxis_title="Harga",
                hovermode='x unified',
                height=600,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_all, use_container_width=True)
    
    # ===== TAB 2: PREDIKSI =====
    with tab2:
        st.header("🔮 Prediksi Harga Pangan - Per Komoditas")
        
        st.info("""
        **Workflow Prediksi:**
        1️⃣ **Tuning Parameter** - Auto-ARIMA akan menentukan model terbaik (ARIMA/SARIMA)
        2️⃣ **Validasi Model** - Uji akurasi dengan 80% train, 20% test
        3️⃣ **Prediksi Masa Depan** - Buat prediksi untuk periode ke depan
        """)
        
        # Load parameter FRESH dari file
        params = st.session_state.params_loader.load_params()
        if not params:
            st.error("❌ Gagal memuat parameter model. Pastikan file `models/best_params.json` tersedia.")
            st.stop()
        
        # Pilih komoditas
        available_commodities = st.session_state.params_loader.get_komoditas_list()
        available_in_df = [c for c in available_commodities if c in df.columns]
        
        if not available_in_df:
            st.error("❌ Tidak ada komoditas yang tersedia di dataset!")
            st.stop()
        
        selected_pred_commodity = st.selectbox(
            "Pilih Komoditas untuk Analisis:",
            available_in_df,
            key="pred_commodity"
        )
        
        # Ambil data
        series = df[selected_pred_commodity].dropna()
        
        if len(series) < 30:
            st.error("❌ Data terlalu sedikit untuk prediksi (minimal 30 data points)")
            st.stop()
        
        # ===== TUNING PARAMETER =====
        st.subheader("Tuning Parameter Auto-ARIMA")
        
        # SELALU RELOAD FRESH dari file
        params_fresh = st.session_state.params_loader.load_params()
        commodity_params = params_fresh.get(selected_pred_commodity, {})
        is_tuned = commodity_params.get('is_tuned', False)
        model_type = commodity_params.get('model_type', 'SARIMA')
        tuning_date = commodity_params.get('tuning_date')
        
        col_tune1, col_tune2 = st.columns([3, 1])
        
        with col_tune1:
            if is_tuned:
                st.write(f"✅ **Status:** Sudah di-tune")
                st.write(f"**Model:** {model_type}")
                st.write(f"**Tanggal:** {tuning_date}")
            else:
                st.write(f"⏳ **Status:** Belum di-tune")
        
        with col_tune2:
            if st.button("🔄 Jalankan Tuning", key="tune_btn", type="primary"):
                tuning_result = auto_tune_per_commodity(series, selected_pred_commodity)
                
                if tuning_result and tuning_result.get('success'):
                    st.success(f"✅ Tuning selesai! Model: {tuning_result['model_type']}")
                    
                    # Tampilkan hasil detail
                    st.markdown("**Hasil Tuning:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Model Terbaik", tuning_result['model_type'])
                    with col2:
                        st.metric("Order (p,d,q)", str(tuning_result['order']))
                    with col3:
                        st.metric("AIC", f"{tuning_result['aic']:.2f}")
                    
                    if tuning_result['model_type'] == 'SARIMA':
                        st.write(f"**Seasonal Order (P,D,Q,m):** {tuning_result['seasonal_order']}")
                    
                    st.write(f"**Perbandingan AIC:**")
                    st.write(f"- SARIMA AIC: {tuning_result['aic_sarima']:.2f}")
                    st.write(f"- ARIMA AIC: {tuning_result['aic_arima']:.2f}")
                    st.write(f"→ Model terpilih: **{tuning_result['model_type']}** (AIC lebih kecil)")
                    
                    st.balloons()
                    
                    # Delay untuk memastikan file tersimpan
                    import time
                    time.sleep(1)
                    
                    # Reload params loader
                    st.session_state.params_loader = SARIMAParamsLoader()
                    st.rerun()
                else:
                    error_msg = tuning_result.get('error', 'Unknown error') if tuning_result else 'Unknown error'
                    st.error(f"❌ Gagal melakukan tuning: {error_msg}")
        
        st.divider()
        
        # ===== VALIDASI MODEL =====
        st.subheader("Validasi Model (80% Train, 20% Test)")
        
        if not is_tuned:
            st.warning("⚠️ Lakukan tuning parameter terlebih dahulu!")
        else:
            # RELOAD FRESH params untuk validasi
            params_fresh = st.session_state.params_loader.load_params()
            commodity_params = params_fresh[selected_pred_commodity]
            
            order = tuple(commodity_params['order'])
            seasonal_order = tuple(commodity_params['seasonal_order'])
            model_type = commodity_params.get('model_type', 'SARIMA')
            
            if st.button("✅ Jalankan Validasi Model", key="validate_btn", type="primary"):
                with st.spinner(f"⏳ Validasi {model_type} model untuk {selected_pred_commodity}..."):
                    eval_result = train_and_evaluate(
                        series, order, seasonal_order, 
                        model_type=model_type, test_size=0.2
                    )
                    
                    if eval_result and eval_result.get('success'):
                        st.success("✅ Validasi model selesai!")
                        st.session_state.validation_result = eval_result
                        st.session_state.validation_commodity = selected_pred_commodity
                        st.rerun()
                    else:
                        st.error("❌ Gagal melakukan validasi model!")
        
        # Display validation result if exists
        if st.session_state.validation_result:
            eval_result = st.session_state.validation_result
            
            # Info model
            st.markdown("#### 📊 Informasi Model")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Model Type", eval_result['model_type'])
            with col2:
                st.metric("Order (p,d,q)", str(eval_result['order']))
            with col3:
                if eval_result['model_type'] == 'SARIMA':
                    st.metric("Seasonal (P,D,Q,m)", str(eval_result['seasonal_order']))
            
            # Tampilkan metrik akurasi
            st.markdown("#### 📈 Akurasi Prediksi pada Test Set (20%)")
            metrics = eval_result['metrics']
            
            mae_val = metrics.get('MAE', 0)
            rmse_val = metrics.get('RMSE', 0)
            mape_val = metrics.get('MAPE', 0)
            accuracy_percent = 100 - mape_val if mape_val else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "MAE",
                    f"{format_number(mae_val)}",
                    help="Mean Absolute Error - rata-rata error absolut"
                )
            with col2:
                st.metric(
                    "RMSE",
                    f"{format_number(rmse_val)}",
                    help="Root Mean Squared Error"
                )
            with col3:
                st.metric(
                    "MAPE",
                    f"{mape_val:.2f}%" if mape_val else "N/A",
                    help="Mean Absolute Percentage Error"
                )
            with col4:
                st.metric(
                    "Akurasi",
                    f"{accuracy_percent:.2f}%",
                    help="100% - MAPE"
                )
            
            # Interpretasi akurasi
            st.markdown("#### 🎯 Interpretasi Akurasi")
            if mape_val is not None:
                if mape_val < 5:
                    st.success("🟢 **AKURASI SANGAT BAIK** (MAPE < 5%)")
                    st.write("Model ini memiliki performa excellent dan dapat diandalkan untuk prediksi.")
                elif mape_val < 10:
                    st.info("🔵 **AKURASI BAIK** (MAPE 5-10%)")
                    st.write("Model ini memiliki performa baik dan cukup dapat diandalkan.")
                elif mape_val < 20:
                    st.warning("🟡 **AKURASI CUKUP** (MAPE 10-20%)")
                    st.write("Model ini memiliki akurasi yang cukup. Pertimbangkan untuk tuning ulang.")
                else:
                    st.error("🔴 **AKURASI RENDAH** (MAPE > 20%)")
                    st.write("Model ini memiliki akurasi rendah. Disarankan untuk tuning ulang parameter.")
            
            # Tabel perbandingan aktual vs prediksi
            st.markdown("#### 📋 Tabel Perbandingan Aktual vs Prediksi (Test Set)")
            
            test_data = eval_result.get('test_data', pd.Series())
            forecast_df = eval_result.get('forecast', pd.DataFrame())
            
            if len(test_data) > 0 and len(forecast_df) > 0:
                comparison_df = pd.DataFrame({
                    'Tanggal': test_data.index,
                    'Aktual': test_data.values,
                    'Prediksi': forecast_df['forecast'].values,
                    'Error': test_data.values - forecast_df['forecast'].values,
                    'Error %': ((test_data.values - forecast_df['forecast'].values) / test_data.values * 100).round(2)
                })
                
                st.dataframe(comparison_df.set_index('Tanggal'), use_container_width=True)
            
            # Plot: Data Train, Test, dan Prediksi dengan CI
            st.markdown("#### 📉 Visualisasi Validasi Model")
            
            fig = go.Figure()
            
            # Data Training (80%)
            train_data = eval_result.get('train_data', pd.Series())
            if len(train_data) > 0:
                fig.add_trace(go.Scatter(
                    x=train_data.index,
                    y=train_data.values,
                    mode='lines',
                    name='Data Training (80%)',
                    line=dict(color='#95a5a6', width=2),
                    opacity=0.7
                ))
            
            # Data Test Aktual (20%)
            if len(test_data) > 0:
                fig.add_trace(go.Scatter(
                    x=test_data.index,
                    y=test_data.values,
                    mode='lines+markers',
                    name='Data Test Aktual (20%)',
                    line=dict(color='#3498db', width=2.5),
                    marker=dict(size=7, symbol='circle')
                ))
            
            # Prediksi pada Test Set
            if len(forecast_df) > 0:
                fig.add_trace(go.Scatter(
                    x=forecast_df.index,
                    y=forecast_df['forecast'].values,
                    mode='lines+markers',
                    name='Prediksi Model',
                    line=dict(color='#e74c3c', width=2.5, dash='dash'),
                    marker=dict(size=7, symbol='diamond')
                ))
                
                # Confidence interval
                if 'upper' in forecast_df.columns and 'lower' in forecast_df.columns:
                    fig.add_trace(go.Scatter(
                        x=list(forecast_df.index) + list(reversed(forecast_df.index)),
                        y=list(forecast_df['upper'].values) + list(reversed(forecast_df['lower'].values)),
                        fill='toself',
                        fillcolor='rgba(231, 76, 60, 0.15)',
                        line=dict(color='rgba(231,76,60,0)'),
                        showlegend=True,
                        name='Confidence Interval (95%)',
                        hoverinfo='skip'
                    ))
            
            fig.update_layout(
                title=f"Validasi Model {eval_result['model_type']} - {selected_pred_commodity}",
                xaxis_title="Tanggal",
                yaxis_title="Harga (Rp)",
                hovermode='x unified',
                height=550,
                template="plotly_white",
                legend=dict(x=0.01, y=0.99)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # ===== PREDIKSI MASA DEPAN =====
        st.subheader("Prediksi Masa Depan (1-20 Periode)")
        
        if not is_tuned:
            st.warning("⚠️ Lakukan tuning parameter terlebih dahulu!")
        else:
            # RELOAD FRESH params untuk forecast
            params_fresh = st.session_state.params_loader.load_params()
            commodity_params = params_fresh[selected_pred_commodity]
            
            order = tuple(commodity_params['order'])
            seasonal_order = tuple(commodity_params['seasonal_order'])
            model_type = commodity_params.get('model_type', 'SARIMA')
            
            col_forecast1, col_forecast2 = st.columns([2, 1])
            
            with col_forecast1:
                n_forecast = st.slider(
                    "Jumlah Periode Forecast:",
                    min_value=1,
                    max_value=20,
                    value=12,
                    help="Jumlah minggu yang akan diprediksi ke depan"
                )
            
            with col_forecast2:
                forecast_button = st.button("📉 Jalankan Prediksi", key="forecast_btn", type="primary")
            
            if forecast_button:
                with st.spinner(f"⏳ Prediksi masa depan untuk {selected_pred_commodity} ({n_forecast} periode)..."):
                    future_result = forecast_future(
                        series, order, seasonal_order,
                        model_type=model_type, periods=n_forecast, full_data=True
                    )
                    
                    if future_result and future_result.get('success'):
                        st.success(f"✅ Prediksi selesai untuk {n_forecast} periode ke depan!")
                        st.session_state.forecast_result = future_result
                        st.rerun()
                    else:
                        st.error("❌ Gagal melakukan prediksi!")
        
        # Display forecast result if exists
        if st.session_state.forecast_result:
            future_result = st.session_state.forecast_result
            forecast_df = future_result['forecast']
            original_series = future_result['original_series']
            
            # Hitung akurasi dari validation result jika tersedia
            if st.session_state.validation_result:
                val_result = st.session_state.validation_result
                mape_val = val_result['metrics'].get('MAPE', 0)
                accuracy_percent = 100 - mape_val if mape_val else 0
                
                st.markdown("#### 📊 Akurasi Model (dari Validasi)")
                st.metric("Akurasi Prediksi", f"{accuracy_percent:.2f}%", help="100% - MAPE dari validation")
            
            # Tabel prediksi
            st.markdown(f"#### 📋 Tabel Prediksi Harga {selected_pred_commodity}")
            
            forecast_table = pd.DataFrame({
                'Periode': forecast_df.index,
                'Prediksi Harga (Rp)': forecast_df['forecast'].values.round(0).astype(int),
                'Lower 95% CI (Rp)': forecast_df['lower'].values.round(0).astype(int),
                'Upper 95% CI (Rp)': forecast_df['upper'].values.round(0).astype(int),
            }).reset_index(drop=True)
            
            forecast_table.index = forecast_table.index + 1
            st.dataframe(forecast_table, use_container_width=True)
            
            # Visualisasi prediksi
            st.markdown("#### 📉 Visualisasi Prediksi Masa Depan")
            
            fig_future = go.Figure()
            
            # Data historis
            fig_future.add_trace(go.Scatter(
                x=original_series.index,
                y=original_series.values,
                mode='lines',
                name='Data Historis',
                line=dict(color='#3498db', width=2)
            ))
            
            # Prediksi masa depan
            fig_future.add_trace(go.Scatter(
                x=forecast_df.index,
                y=forecast_df['forecast'].values,
                mode='lines+markers',
                name='Prediksi Masa Depan',
                line=dict(color='#e74c3c', width=2.5, dash='dash'),
                marker=dict(size=7, symbol='diamond')
            ))
            
            # Confidence interval
            fig_future.add_trace(go.Scatter(
                x=list(forecast_df.index) + list(reversed(forecast_df.index)),
                y=list(forecast_df['upper'].values) + list(reversed(forecast_df['lower'].values)),
                fill='toself',
                fillcolor='rgba(231, 76, 60, 0.15)',
                line=dict(color='rgba(231,76,60,0)'),
                showlegend=True,
                name='Confidence Interval (95%)',
                hoverinfo='skip'
            ))
            
            fig_future.update_layout(
                title=f"Prediksi Harga {selected_pred_commodity} ({future_result['periods']} Periode Ke Depan)",
                xaxis_title="Tanggal",
                yaxis_title="Harga (Rp)",
                hovermode='x unified',
                height=550,
                template="plotly_white",
                legend=dict(x=0.01, y=0.99)
            )
            
            st.plotly_chart(fig_future, use_container_width=True)
            
            # Download CSV
            csv = forecast_table.to_csv(index=True)
            st.download_button(
                label="📥 Download Prediksi sebagai CSV",
                data=csv,
                file_name=f"prediksi_{selected_pred_commodity}_{future_result['periods']}_periode.csv",
                mime="text/csv"
            )
    
    # ===== TAB 3: EVALUASI MODEL (INFO SAJA) =====
    with tab3:
        st.header("📈 Info Akurasi Model & Parameter")
        
        st.info("""
        ℹ️ **Cara Menggunakan Aplikasi:**
        
        **Tab "Prediksi"** adalah tempat Anda melakukan analisis per komoditas:
        1. Pilih komoditas yang ingin diprediksi
        2. Jalankan **Tuning Parameter** untuk menentukan model terbaik (ARIMA atau SARIMA)
        3. Jalankan **Validasi Model** untuk melihat akurasi (MAE, RMSE, MAPE) pada test set
        4. Jalankan **Prediksi Masa Depan** untuk melihat prediksi 1-20 periode ke depan
        """)
        
        st.markdown("#### 📊 Parameter Model yang Sudah di-Tune:")
        
        # Tampilkan semua parameter model - RELOAD FRESH
        params = st.session_state.params_loader.load_params()
        if params:
            for commodity, param_dict in params.items():
                status = "✅ Sudah di-tune" if param_dict.get('is_tuned', False) else "⏳ Belum di-tune"
                model_type = param_dict.get('model_type', 'N/A')
                
                with st.expander(f"🌾 {commodity} - {status}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Model Type:** `{model_type}`")
                        st.write(f"**Order (p,d,q):** `{param_dict['order']}`")
                    with col2:
                        st.write(f"**Seasonal (P,D,Q,m):** `{param_dict['seasonal_order']}`")
                        if param_dict.get('tuning_date'):
                            st.write(f"**Tanggal Tuning:** {param_dict['tuning_date']}")
                    
                    if param_dict.get('aic'):
                        st.write(f"**AIC:** {param_dict['aic']:.2f} | **BIC:** {param_dict.get('bic', 'N/A')}")
                    
                    # Tampilkan metrik akurasi jika tersedia
                    if st.session_state.validation_result and 'validation_commodity' in st.session_state and st.session_state.validation_commodity == commodity:
                        val_result = st.session_state.validation_result
                        metrics = val_result['metrics']
                        mae_val = metrics.get('MAE', 0)
                        rmse_val = metrics.get('RMSE', 0)
                        mape_val = metrics.get('MAPE', 0)
                        accuracy_percent = 100 - mape_val if mape_val else 0
                        
                        st.divider()
                        st.markdown("**Metrik Akurasi (Test Set):**")
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        with col_m1:
                            st.metric("MAE", f"{format_number(mae_val)}")
                        with col_m2:
                            st.metric("RMSE", f"{format_number(rmse_val)}")
                        with col_m3:
                            st.metric("MAPE", f"{mape_val:.2f}%")
                        with col_m4:
                            st.metric("Akurasi", f"{accuracy_percent:.2f}%")
    
    # ===== TAB 4: AUTO-TUNING REFERENCE =====
    with tab4:
        st.header("🔍 Auto-Tuning Reference (Manual)")
        
        st.info("""
        **ℹ️ Fitur Auto-Tuning (Reference)**
        
        Fitur ini memungkinkan Anda untuk melakukan auto-tuning secara manual jika ingin bereksperimen 
        dengan parameter yang berbeda. Namun, **gunakan Tab "Prediksi" untuk tuning yang tersimpan otomatis**.
        """)
        
        tune_commodity = st.selectbox(
            "Pilih Komoditas untuk Auto-Tuning Manual:",
            df.columns.tolist() if st.session_state.df is not None else [],
            key="tune_commodity"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            use_seasonal = st.checkbox("Gunakan Seasonal", value=True)
        
        with col2:
            if use_seasonal:
                seasonal_period = st.number_input(
                    "Periode Seasonal (m):",
                    min_value=2,
                    max_value=52,
                    value=52,
                    help="Biasanya 52 untuk data mingguan (1 tahun)"
                )
            else:
                seasonal_period = 0
        
        if st.button("🔍 Jalankan Auto-Tuning Manual", type="primary"):
            if st.session_state.df is not None:
                series = st.session_state.df[tune_commodity].dropna()
                
                tune_result = auto_tune_sarima(series, use_seasonal, seasonal_period)
                
                if tune_result and tune_result.get('success'):
                    st.success("✅ Auto-tuning selesai!")
                    
                    # Tampilkan hasil
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.metric("Order (p,d,q)", str(tune_result['order']))
                        st.metric("AIC", f"{tune_result['aic']:.2f}")
                    
                    with col_b:
                        st.metric("Seasonal (P,D,Q,m)", str(tune_result['seasonal_order']))
                        st.metric("BIC", f"{tune_result['bic']:.2f}")
                    
                    st.warning("⚠️ Hasil ini untuk referensi saja. Gunakan **Tab Prediksi** untuk tuning otomatis yang tersimpan.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d;">
    <p>💡 <b>Tips:</b> Untuk hasil terbaik, pastikan data time series Anda stasioner dan tidak memiliki outlier ekstrem</p>
    <p style="font-size: 0.9em;">Setiap komoditas akan di-tune secara otomatis menggunakan Auto-ARIMA untuk menentukan model terbaik (ARIMA atau SARIMA)</p>
</div>
""", unsafe_allow_html=True)
