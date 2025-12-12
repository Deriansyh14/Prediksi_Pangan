"""
============================================
GENERATE PARAMS SCRIPT
Script untuk generate best_params.json dari hasil tuning
============================================

Cara pakai:
1. Copy hasil_tuning_df dari Colab
2. Jalankan script ini
3. File best_params.json akan otomatis dibuat
"""

import pandas as pd
import json
import os

def generate_params_from_dataframe(hasil_tuning_df):
    """
    Generate best_params.json dari DataFrame hasil tuning
    
    Args:
        hasil_tuning_df: DataFrame dengan kolom:
                        - Komoditas
                        - Order(p,d,q)
                        - Seasonal(P,D,Q,m)
                        - MAE
                        - RMSE
                        - MAPE
    """
    params_dict = {}
    
    for idx, row in hasil_tuning_df.iterrows():
        komoditas = row['Komoditas']
        
        # Extract order
        order = row['Order(p,d,q)']
        if isinstance(order, str):
            # Jika string, parse
            order = eval(order)
        order_list = list(order)
        
        # Extract seasonal_order
        seasonal = row['Seasonal(P,D,Q,m)']
        if isinstance(seasonal, str):
            # Jika string, parse
            seasonal = eval(seasonal)
        seasonal_list = list(seasonal)
        
        # Tambahkan ke dictionary
        params_dict[komoditas] = {
            "order": order_list,
            "seasonal_order": seasonal_list
        }
    
    return params_dict


def save_params_to_json(params_dict, filename='models/best_params.json'):
    """
    Simpan parameter ke file JSON
    
    Args:
        params_dict: Dictionary parameter
        filename: Nama file output
    """
    # Buat folder jika belum ada
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Simpan ke JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(params_dict, f, indent=4, ensure_ascii=False)
    
    print(f" File '{filename}' berhasil dibuat!")


# ===== CONTOH PENGGUNAAN =====

if __name__ == "__main__":
    
    # OPSI 1: Manual Input
    # Jika Anda punya data hasil tuning, masukkan manual
    
    manual_params = {
        "Beras Premium": {
            "order": [1, 1, 1],
            "seasonal_order": [1, 1, 1, 52]
        },
        "Bawang Merah": {
            "order": [2, 1, 2],
            "seasonal_order": [1, 1, 1, 52]
        },
        "Bawang Putih": {
            "order": [1, 1, 1],
            "seasonal_order": [1, 1, 0, 52]
        },
        "Cabai Merah kriting": {
            "order": [2, 1, 1],
            "seasonal_order": [1, 1, 1, 52]
        },
        "Telur Ayam Ras": {
            "order": [1, 1, 1],
            "seasonal_order": [1, 1, 1, 52]
        },
        "Gula": {
            "order": [1, 1, 1],
            "seasonal_order": [0, 1, 1, 52]
        },
        "Minyak Goreng Kemasan": {
            "order": [1, 1, 1],
            "seasonal_order": [1, 1, 1, 52]
        },
        "Garam": {
            "order": [1, 1, 1],
            "seasonal_order": [1, 1, 0, 52]
        }
    }
    
    save_params_to_json(manual_params)
    
    
    # OPSI 2: Dari DataFrame
    # Jika Anda punya hasil_tuning_df dari Colab, uncomment kode di bawah
    
    """
    # Contoh data
    data = {
        'Komoditas': ['Beras Premium', 'Bawang Merah'],
        'Order(p,d,q)': [(1,1,1), (2,1,2)],
        'Seasonal(P,D,Q,m)': [(1,1,1,52), (1,1,1,52)],
        'MAE': [100, 500],
        'RMSE': [120, 600],
        'MAPE': [2.5, 5.0]
    }
    
    hasil_tuning_df = pd.DataFrame(data)
    
    # Generate params
    params = generate_params_from_dataframe(hasil_tuning_df)
    
    # Simpan
    save_params_to_json(params)
    """
    
    print("\n Preview best_params.json:")
    print(json.dumps(manual_params, indent=4))
    
    print("\n Tips:")
    print("1. Copy hasil tuning dari Colab ke script ini")
    print("2. Jalankan: python generate_params.py")
    print("3. File best_params.json akan dibuat di folder models/")
    print("4. Upload file tersebut ke aplikasi Streamlit")


# ===== FUNGSI TAMBAHAN =====

def validate_params(params_dict):
    """
    Validasi format parameter
    
    Args:
        params_dict: Dictionary parameter
    
    Returns:
        bool: True jika valid
    """
    for komoditas, params in params_dict.items():
        # Cek order
        if 'order' not in params:
            print(f" Error: {komoditas} tidak punya 'order'")
            return False
        
        if len(params['order']) != 3:
            print(f" Error: {komoditas} order harus 3 elemen (p,d,q)")
            return False
        
        # Cek seasonal_order
        if 'seasonal_order' not in params:
            print(f" Error: {komoditas} tidak punya 'seasonal_order'")
            return False
        
        if len(params['seasonal_order']) != 4:
            print(f" Error: {komoditas} seasonal_order harus 4 elemen (P,D,Q,m)")
            return False
    
    print(" Semua parameter valid!")
    return True


def load_params_from_json(filename='models/best_params.json'):
    """
    Load parameter dari JSON
    
    Args:
        filename: Nama file JSON
    
    Returns:
        Dictionary parameter
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            params = json.load(f)
        
        print(f" Parameter berhasil dimuat dari '{filename}'")
        return params
    
    except FileNotFoundError:
        print(f" File '{filename}' tidak ditemukan!")
        return None
    except json.JSONDecodeError:
        print(f" Format JSON tidak valid!")
        return None


def compare_params(old_file='models/best_params_old.json', 
                  new_file='models/best_params.json'):
    """
    Bandingkan parameter lama dengan baru
    
    Args:
        old_file: File parameter lama
        new_file: File parameter baru
    """
    old_params = load_params_from_json(old_file)
    new_params = load_params_from_json(new_file)
    
    if old_params is None or new_params is None:
        return
    
    print("\n📊 Perbandingan Parameter:\n")
    
    for komoditas in new_params.keys():
        if komoditas in old_params:
            old = old_params[komoditas]
            new = new_params[komoditas]
            
            if old != new:
                print(f" {komoditas}:")
                print(f"   Lama: {old}")
                print(f"   Baru: {new}")
        else:
            print(f"➕ {komoditas}: (baru)")
            print(f"   {new_params[komoditas]}")