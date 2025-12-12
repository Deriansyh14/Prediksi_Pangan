# 🌾 Prediksi Harga Pangan - Aplikasi ARIMA/SARIMA

Sistem Prediksi Harga Komoditas Pangan berbasis Time Series Analysis menggunakan model ARIMA dan SARIMA.

## 📋 Daftar Isi

- [Fitur](#fitur)
- [Instalasi](#instalasi)
- [Cara Menggunakan](#cara-menggunakan)
- [Format Dataset](#format-dataset)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## ✨ Fitur

### 1. **Per-Komoditas Analysis**
- Analisis setiap komoditas secara terpisah
- Parameter optimal untuk setiap komoditas

### 2. **Auto-ARIMA Tuning**
- Otomatis menentukan model terbaik (ARIMA atau SARIMA)
- Membandingkan AIC score untuk memilih model
- Hasil tuning otomatis tersimpan ke `best_params.json`

### 3. **Model Validation**
- Validasi dengan 80% train, 20% test split
- Akurasi per-komoditas (MAE, RMSE, MAPE)
- Tabel perbandingan aktual vs prediksi

### 4. **Interactive Visualization**
- Grafik Plotly dengan confidence interval (95%)
- Warna-beda untuk data training, test actual, dan prediksi
- Visualisasi untuk historis dan forecast masa depan

### 5. **Future Forecast**
- Prediksi 1-20 periode ke depan
- Confidence interval untuk setiap prediksi
- Export hasil dalam format CSV

## 📦 Instalasi

### Persyaratan
- Python 3.8+
- Virtual Environment (recommended)

### Setup Local

```bash
# Clone atau download repository
cd PSD

# Buat virtual environment
python -m venv .venv

# Aktivasi virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
streamlit run app.py
```

Aplikasi akan membuka di `http://localhost:8501`

## 🚀 Cara Menggunakan

### Langkah 1: Upload Dataset
1. Buka halaman "Prediksi Pangan" dari sidebar
2. Upload file CSV atau Excel di sidebar

### Langkah 2: Pilih Komoditas
1. Di Tab "Prediksi", pilih komoditas yang ingin dianalisis
2. Sistem akan menampilkan status tuning komoditas

### Langkah 3: Tuning Parameter
1. Klik tombol **"🔄 Jalankan Tuning"**
2. Sistem akan menjalankan Auto-ARIMA untuk menemukan model terbaik
3. Hasil tuning otomatis tersimpan ke `best_params.json`
4. Informasi: Model type (ARIMA/SARIMA), Order, AIC/BIC

### Langkah 4: Validasi Model
1. Klik **"✅ Jalankan Validasi Model"**
2. Sistem akan:
   - Split data 80:20 (train:test)
   - Hitung akurasi (MAE, RMSE, MAPE)
   - Tampilkan visualisasi dengan 3 traces
   - Tabel perbandingan aktual vs prediksi

### Langkah 5: Prediksi Masa Depan
1. Tentukan jumlah periode (1-20) dengan slider
2. Klik **"📉 Jalankan Prediksi"**
3. Hasil: Tabel prediksi, visualisasi, dan download CSV

## 📊 Format Dataset

### Struktur CSV/Excel

```
Periode    | Beras Premium | Bawang Merah | Bawang Putih | ...
-----------|---------------|-------------|-------------|----
01/01/2023 | 12500         | 35000       | 28000       | ...
08/01/2023 | 12700         | 36000       | 28500       | ...
15/01/2023 | 12600         | 35500       | 28200       | ...
```

### Persyaratan Format
- **Kolom Periode:** Format DD/MM/YYYY
- **Kolom Komoditas:** Numerik (harga)
- **Minimal:** 30 data points per komoditas
- **Komoditas Didukung:**
  - Beras Premium
  - Bawang Merah
  - Bawang Putih
  - Cabai Merah kriting
  - Telur Ayam Ras
  - Gula
  - Minyak Goreng Kemasan
  - Garam

## 🌐 Deployment

### Deployment ke Streamlit Cloud

1. **Push ke GitHub**
```bash
git add .
git commit -m "Deploy aplikasi prediksi pangan"
git push origin main
```

2. **Buka Streamlit Cloud** (https://streamlit.io/cloud)
3. **Create New App**
   - Repository: `sains-data/Stokastik_4_RB`
   - Branch: `main`
   - Main file path: `app.py`

4. **Deploy** - Streamlit akan otomatis build dan deploy

### Deployment ke Server Own (Linux/Ubuntu)

```bash
# Install Python & dependencies
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv

# Clone repository
git clone https://github.com/sains-data/Stokastik_4_RB.git
cd Stokastik_4_RB

# Setup virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Jalankan dengan gunicorn/systemd (recommended)
# Atau gunakan screen:
screen -S pangan
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Deployment ke Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build image
docker build -t prediksi-pangan .

# Run container
docker run -p 8501:8501 prediksi-pangan
```

## 📁 Struktur Folder

```
PSD/
├── app.py                          # Home page
├── requirements.txt                # Python dependencies
├── requirments.txt                 # (typo - untuk referensi lama)
├── check_env.py                    # Environment checker
├── README.md                        # Dokumentasi
├── DEPLOYMENT_GUIDE.md             # Panduan deployment
├── .streamlit/
│   └── config.toml                 # Streamlit config
├── models/
│   └── best_params.json            # Parameter ARIMA/SARIMA per komoditas
├── pages/
│   └── prediksi_pangan.py          # Halaman utama prediksi
├── src/
│   ├── __init__.py
│   ├── utils.py                    # Utility functions (load, preprocess, metrics)
│   ├── load_model.py               # Load & manage parameters
│   └── forecasting.py              # ARIMA/SARIMA modeling
└── __pycache__/
```

## 🔧 Troubleshooting

### Error: "pmdarima is not installed"
```bash
pip install pmdarima
```

### Error: "statsmodels is not installed"
```bash
pip install statsmodels
```

### Data tidak muncul di Tab Explorasi
- Pastikan format tanggal: DD/MM/YYYY
- Pastikan ada minimal 30 data points
- Cek tidak ada baris kosong di awal/akhir

### Tuning sangat lambat
- Normal untuk dataset besar (tuning = 2-10 menit)
- Gunakan dataset sample 52+ data points untuk testing
- Untuk production gunakan full dataset

### Memory issue saat prediksi
- Kurangi jumlah data atau periode forecast
- Restart Streamlit: `Ctrl+C` → `streamlit run app.py`

## 📊 Model Information

### ARIMA (AutoRegressive Integrated Moving Average)
- Untuk data non-seasonal
- Order: (p, d, q)
- Cocok untuk data trend sederhana

### SARIMA (Seasonal ARIMA)
- Untuk data dengan pola seasonal
- Order: (p, d, q) + Seasonal (P, D, Q, m)
- m = seasonal period (biasanya 52 untuk data mingguan)
- Cocok untuk data dengan pola musiman

### Metrics
- **MAE:** Mean Absolute Error - rata-rata error absolut
- **RMSE:** Root Mean Squared Error - menghukum error besar
- **MAPE:** Mean Absolute Percentage Error - persentase error

Interpretasi MAPE:
- < 5%: Akurasi Sangat Baik
- 5-10%: Akurasi Baik
- 10-20%: Akurasi Cukup
- > 20%: Akurasi Rendah

## 📈 Contoh Hasil

Setiap komoditas akan menunjukkan:

1. **Status Tuning**
   - Model type: ARIMA atau SARIMA
   - Order parameter
   - Tanggal tuning

2. **Akurasi Validasi**
   - MAE, RMSE, MAPE
   - Interpretasi akurasi (🟢/🔵/🟡/🔴)
   - Tabel perbandingan aktual vs prediksi

3. **Visualisasi**
   - Garis abu (training data 80%)
   - Garis biru (test actual 20%)
   - Garis merah dash (prediksi)
   - Area merah (confidence interval 95%)

4. **Prediksi Masa Depan**
   - Tabel dengan prediksi + CI lower/upper
   - Visualisasi historis + forecast
   - File CSV untuk download

## 📞 Support

Untuk pertanyaan atau issue, silakan buat issue di repository atau hubungi tim development.

---

**Last Updated:** December 2025
**Version:** 1.0
**Author:** Tim Data Science
