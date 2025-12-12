"""
============================================
APLIKASI PREDIKSI HARGA PANGAN
Menggunakan Model ARIMA/SARIMA
============================================
"""

import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Prediksi Harga Pangan",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk styling professional
st.markdown("""
    <style>
    /* Main background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e8ecf1 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Headings */
    h1 {
        color: #2c3e50 !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
    }
    
    h2 {
        color: #34495e !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
        border-bottom: 2px solid #3498db !important;
        padding-bottom: 10px !important;
    }
    
    h3 {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        margin-top: 15px !important;
    }
    
    /* Info cards */
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        box-shadow: 0 2px 8px rgba(52, 73, 94, 0.1);
        margin: 15px 0;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(52, 73, 94, 0.15) !important;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 8px !important;
        padding: 15px !important;
        margin: 15px 0 !important;
    }
    
    /* Links & text */
    p {
        line-height: 1.6 !important;
        margin: 10px 0 !important;
    }
    
    ul {
        margin-left: 20px !important;
    }
    
    li {
        margin: 8px 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1>🌾 Prediksi Harga Pangan</h1>
        <p style="font-size: 1.1em; color: #7f8c8d; margin: 0;">
            Sistem Prediksi Harga Komoditas Pangan dengan ARIMA/SARIMA
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# Main content
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="info-card">
            <h3 style="color: #3498db; margin-top: 0;">📊 Fitur Utama</h3>
            <ul>
                <li><strong>Per-Komoditas Analysis:</strong> Analisis setiap komoditas secara terpisah</li>
                <li><strong>Auto-ARIMA Tuning:</strong> Otomatis menentukan model terbaik (ARIMA/SARIMA)</li>
                <li><strong>Model Validation:</strong> Validasi dengan 80% train, 20% test split</li>
                <li><strong>Accuracy Metrics:</strong> MAE, RMSE, MAPE per komoditas</li>
                <li><strong>Future Forecast:</strong> Prediksi 1-20 periode ke depan</li>
                <li><strong>Interactive Visualization:</strong> Grafik Plotly interaktif dengan confidence interval</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="info-card">
            <h3 style="color: #27ae60; margin-top: 0;">🚀 Cara Memulai</h3>
            <ol>
                <li><strong>Upload Dataset:</strong> Buka halaman "Prediksi Pangan" → Upload CSV/Excel</li>
                <li><strong>Pilih Komoditas:</strong> Pilih komoditas yang ingin dianalisis</li>
                <li><strong>Tuning Parameter:</strong> Klik "Jalankan Tuning" untuk menemukan model terbaik</li>
                <li><strong>Validasi Model:</strong> Klik "Jalankan Validasi" untuk uji akurasi</li>
                <li><strong>Prediksi Masa Depan:</strong> Tentukan periode & lihat hasil prediksi</li>
                <li><strong>Export Hasil:</strong> Download prediksi dalam format CSV</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Format dataset
st.markdown("## 📋 Format Dataset")

col_format1, col_format2 = st.columns([2, 1])

with col_format1:
    st.markdown("""
        Dataset harus memiliki format seperti berikut:
        
        | Periode    | Beras Premium | Bawang Merah | Bawang Putih |
        |-----------|---------------|-------------|-------------|
        | 01/01/2023 | 12500         | 35000       | 28000       |
        | 08/01/2023 | 12700         | 36000       | 28500       |
        | 15/01/2023 | 12600         | 35500       | 28200       |
        
        **Format persyaratan:**
        - Kolom pertama: Tanggal (DD/MM/YYYY)
        - Kolom lainnya: Harga komoditas (numerik)
    """)

with col_format2:
    st.markdown("""
        **Komoditas yang didukung:**
        - Beras Premium
        - Bawang Merah
        - Bawang Putih
        - Cabai Merah kriting
        - Telur Ayam Ras
        - Gula
        - Minyak Goreng Kemasan
        - Garam
    """)

st.divider()

# Technology stack
st.markdown("## 🛠️ Teknologi")

col_tech1, col_tech2, col_tech3 = st.columns(3)

with col_tech1:
    st.info("**Backend**\n\n- Python 3.12\n- statsmodels 0.14.6\n- pmdarima 2.1.1")

with col_tech2:
    st.info("**Data Processing**\n\n- Pandas 2.1.4\n- NumPy 1.26.3\n- scikit-learn 1.8.0")

with col_tech3:
    st.info("**Visualization**\n\n- Streamlit 1.31.0\n- Plotly 5.18.0\n- Interactive Charts")

st.divider()

# Footer
st.markdown("""
    <div style="text-align: center; color: #95a5a6; margin-top: 40px; padding: 20px; border-top: 1px solid #bdc3c7;">
        <p><strong>Prediksi Harga Pangan</strong> © 2025</p>
        <p style="font-size: 0.9em;">Sistem Prediksi Berbasis Time Series Analysis</p>
        <p style="font-size: 0.85em;">Mulai dengan menuju halaman <strong>Prediksi Pangan</strong> di sidebar →</p>
    </div>
""", unsafe_allow_html=True)