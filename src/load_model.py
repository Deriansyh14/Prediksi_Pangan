"""
============================================
LOAD MODEL
Fungsi untuk load dan manage parameter model SARIMA
============================================
"""

import json
import os
import streamlit as st


class SARIMAParamsLoader:
    """
    Class untuk load dan manage parameter SARIMA dari file JSON
    """
    
    def __init__(self, params_file='models/best_params.json'):
        """
        Inisialisasi loader
        
        Args:
            params_file: Path ke file parameters JSON
        """
        self.params_file = params_file
        self.params = self.load_params()
    
    
    def load_params(self):
        """
        Load parameter dari file JSON - SELALU baca fresh dari file
        
        Returns:
            dict: Dictionary parameter atau None jika gagal
        """
        try:
            if os.path.exists(self.params_file):
                # Buka file fresh setiap kali dipanggil
                with open(self.params_file, 'r', encoding='utf-8') as f:
                    params = json.load(f)
                
                # Update internal params juga
                self.params = params
                return params
            else:
                st.warning(f"⚠️ File '{self.params_file}' tidak ditemukan!")
                return None
        
        except json.JSONDecodeError:
            st.error("❌ Format JSON tidak valid!")
            return None
        except Exception as e:
            st.error(f"❌ Error membaca parameter: {str(e)}")
            return None
    
    
    def get_komoditas_list(self):
        """
        Dapatkan list semua komoditas yang tersedia
        
        Returns:
            list: List nama komoditas
        """
        if self.params:
            return list(self.params.keys())
        return []
    
    
    def get_params_for_komoditas(self, komoditas):
        """
        Dapatkan parameter untuk komoditas tertentu
        
        Args:
            komoditas: Nama komoditas
        
        Returns:
            dict: Parameter (order dan seasonal_order) atau None
        """
        if self.params and komoditas in self.params:
            return self.params[komoditas]
        return None
    
    
    def validate_params(self):
        """
        Validasi format semua parameter
        
        Returns:
            bool: True jika semua parameter valid
        """
        if not self.params:
            return False
        
        for komoditas, params in self.params.items():
            # Cek order
            if 'order' not in params:
                st.error(f"❌ {komoditas} tidak punya 'order'")
                return False
            
            if len(params['order']) != 3:
                st.error(f"❌ {komoditas} order harus 3 elemen (p,d,q)")
                return False
            
            # Cek seasonal_order
            if 'seasonal_order' not in params:
                st.error(f"❌ {komoditas} tidak punya 'seasonal_order'")
                return False
            
            if len(params['seasonal_order']) != 4:
                st.error(f"❌ {komoditas} seasonal_order harus 4 elemen (P,D,Q,m)")
                return False
        
        return True
    
    
    def display_params_info(self):
        """
        Display informasi parameter dalam format yang readable
        """
        if not self.params:
            st.error("❌ Parameter tidak tersedia")
            return
        
        st.write("### 📊 Parameter SARIMA yang Dimuat:")
        
        for komoditas, params in self.params.items():
            with st.expander(f"🌾 {komoditas}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Order (p,d,q):** {params['order']}")
                
                with col2:
                    st.write(f"**Seasonal (P,D,Q,m):** {params['seasonal_order']}")


def create_default_params_file(output_file='models/best_params.json'):
    """
    Buat file parameter default jika belum ada
    
    Args:
        output_file: Path file output
    """
    try:
        # Parameter default
        default_params = {
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
        
        # Buat folder jika belum ada
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Simpan ke JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(default_params, f, indent=4, ensure_ascii=False)
        
        st.success(f"✅ File '{output_file}' berhasil dibuat!")
        
    except Exception as e:
        st.error(f"❌ Error membuat file: {str(e)}")


def reload_params(params_file='models/best_params.json'):
    """
    Reload parameter dari file (useful untuk Streamlit rerun)
    
    Args:
        params_file: Path ke file parameters
    
    Returns:
        SARIMAParamsLoader: Instance loader dengan parameter terbaru
    """
    return SARIMAParamsLoader(params_file)


def get_sarima_params(komoditas, params_file='models/best_params.json'):
    """
    Utility function untuk langsung dapatkan parameter SARIMA
    
    Args:
        komoditas: Nama komoditas
        params_file: Path ke file parameters
    
    Returns:
        tuple: (order, seasonal_order) atau (None, None)
    """
    loader = SARIMAParamsLoader(params_file)
    params = loader.get_params_for_komoditas(komoditas)
    
    if params:
        return tuple(params['order']), tuple(params['seasonal_order'])
    
    return None, None
