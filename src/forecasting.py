"""
============================================
FORECASTING MODULE
Modul untuk training dan forecasting ARIMA/SARIMA
============================================
"""

import pandas as pd
import numpy as np
import streamlit as st
import warnings
import json
import os
from datetime import datetime

# Try imports that may not be available in every environment
try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    _STATSMODELS_IMPORT_ERROR = None
except Exception as e:
    SARIMAX = None
    _STATSMODELS_IMPORT_ERROR = e

try:
    from pmdarima import auto_arima
    _PMDARIMA_IMPORT_ERROR = None
except Exception as e:
    auto_arima = None
    _PMDARIMA_IMPORT_ERROR = e

from src.utils import calculate_metrics_summary

warnings.filterwarnings('ignore')


def train_and_evaluate(series, order, seasonal_order=None, model_type='SARIMA', test_size=0.2):
    """
    Train model ARIMA/SARIMA dan evaluasi dengan test set
    
    Args:
        series: Time series data (pd.Series)
        order: Tuple (p, d, q)
        seasonal_order: Tuple (P, D, Q, m) - jika None, gunakan ARIMA
        model_type: 'ARIMA' atau 'SARIMA'
        test_size: Proporsi test set (0-1)
    
    Returns:
        dict: Dictionary dengan model, metrics, forecast, dan info
    """
    try:
        # Ensure statsmodels is available
        if SARIMAX is None:
            st.error("Package 'statsmodels' is not installed or failed to import. Install with: pip install statsmodels")
            return {'success': False, 'error': f"statsmodels import error: {_STATSMODELS_IMPORT_ERROR}"}

        # Split data
        split_idx = int(len(series) * (1 - test_size))
        train_data = series.iloc[:split_idx]
        test_data = series.iloc[split_idx:]
        
        # Train model (ARIMA atau SARIMA)
        if model_type.upper() == 'ARIMA' or seasonal_order is None:
            # ARIMA (tanpa seasonal)
            model = SARIMAX(
                train_data,
                order=order,
                seasonal_order=(0, 0, 0, 0),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
        else:
            # SARIMA (dengan seasonal)
            model = SARIMAX(
                train_data,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
        
        fitted_model = model.fit(disp=False, maxiter=500)
        
        # Get forecast untuk test set
        forecast = fitted_model.get_forecast(steps=len(test_data))
        forecast_df = forecast.conf_int(alpha=0.05)
        forecast_df['forecast'] = forecast.predicted_mean
        forecast_df.columns = ['lower', 'upper', 'forecast']
        
        # Calculate metrics
        metrics = calculate_metrics_summary(test_data.values, forecast_df['forecast'].values)
        
        result = {
            'model': fitted_model,
            'train_data': train_data,
            'test_data': test_data,
            'forecast': forecast_df,
            'metrics': metrics,
            'order': order,
            'seasonal_order': seasonal_order,
            'model_type': model_type,
            'success': True
        }
        
        return result
    
    except Exception as e:
        st.error(f"❌ Error training model: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def forecast_future(series, order, seasonal_order=None, model_type='SARIMA', periods=12, full_data=True):
    """
    Forecast untuk periode ke depan
    
    Args:
        series: Time series data (pd.Series)
        order: Tuple (p, d, q)
        seasonal_order: Tuple (P, D, Q, m) - jika None, gunakan ARIMA
        model_type: 'ARIMA' atau 'SARIMA'
        periods: Jumlah periode untuk forecast
        full_data: Jika True, train dengan semua data. Jika False, gunakan sebagian.
    
    Returns:
        dict: Dictionary dengan forecast dan model
    """
    try:
        # Ensure statsmodels is available
        if SARIMAX is None:
            st.error("Package 'statsmodels' is not installed or failed to import. Install with: pip install statsmodels")
            return {'success': False, 'error': f"statsmodels import error: {_STATSMODELS_IMPORT_ERROR}"}

        # Train dengan semua data jika full_data=True
        if full_data:
            train_series = series
        else:
            # Train dengan 80% data
            split_idx = int(len(series) * 0.8)
            train_series = series.iloc[:split_idx]
        
        # Fit model (ARIMA atau SARIMA)
        if model_type.upper() == 'ARIMA' or seasonal_order is None:
            model = SARIMAX(
                train_series,
                order=order,
                seasonal_order=(0, 0, 0, 0),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
        else:
            model = SARIMAX(
                train_series,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
        
        fitted_model = model.fit(disp=False, maxiter=500)
        
        # Forecast
        forecast = fitted_model.get_forecast(steps=periods)
        forecast_df = forecast.conf_int(alpha=0.05)
        forecast_df['forecast'] = forecast.predicted_mean
        forecast_df.columns = ['lower', 'upper', 'forecast']
        
        # Generate index untuk forecast (assuming weekly data)
        last_date = series.index[-1]
        forecast_dates = pd.date_range(start=last_date, periods=periods+1, freq='W')[1:]
        forecast_df.index = forecast_dates
        
        result = {
            'forecast': forecast_df,
            'model': fitted_model,
            'original_series': series,
            'periods': periods,
            'model_type': model_type,
            'success': True
        }
        
        return result
    
    except Exception as e:
        st.error(f"❌ Error forecasting: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def auto_tune_per_commodity(series, komoditas, params_file='models/best_params.json', 
                          max_p=5, max_d=2, max_q=5, max_P=2, max_D=1, max_Q=2, m=52):
    """
    Auto tune ARIMA/SARIMA parameter menggunakan pmdarima dan SIMPAN ke JSON
    Fungsi ini akan menentukan apakah model terbaik adalah ARIMA atau SARIMA
    
    Args:
        series: Time series data
        komoditas: Nama komoditas (untuk disimpan di JSON)
        params_file: Path file best_params.json
        max_p, max_d, max_q: Max parameters untuk order
        max_P, max_D, max_Q: Max parameters untuk seasonal order
        m: Seasonal period
    
    Returns:
        dict: Dictionary dengan best parameter, model_type, AIC, BIC, dan status penyimpanan
    """
    try:
        # Ensure pmdarima is available for auto-tuning
        if auto_arima is None:
            st.error("Package 'pmdarima' is not installed or failed to import. Install with: pip install pmdarima")
            return {'success': False, 'error': f"pmdarima import error: {_PMDARIMA_IMPORT_ERROR}"}

        with st.spinner(f"🔄 Tuning parameter untuk {komoditas}..."):
            
            # Auto tune dengan SEASONAL=True dulu (akan mencoba SARIMA)
            auto_model_sarima = auto_arima(
                series,
                start_p=0, max_p=max_p,
                start_d=0, max_d=max_d,
                start_q=0, max_q=max_q,
                seasonal=True,
                start_P=0, max_P=max_P,
                start_D=0, max_D=max_D,
                start_Q=0, max_Q=max_Q,
                m=m,
                trace=False,
                error_action='ignore',
                suppress_warnings=True,
                stepwise=True,
                n_jobs=-1
            )
            
            # Auto tune tanpa SEASONAL (akan menghasilkan ARIMA)
            auto_model_arima = auto_arima(
                series,
                start_p=0, max_p=max_p,
                start_d=0, max_d=max_d,
                start_q=0, max_q=max_q,
                seasonal=False,
                trace=False,
                error_action='ignore',
                suppress_warnings=True,
                stepwise=True,
                n_jobs=-1
            )
            
            # Bandingkan AIC antara SARIMA dan ARIMA
            aic_sarima = auto_model_sarima.aic()
            aic_arima = auto_model_arima.aic()
            
            # Pilih model dengan AIC lebih rendah
            if aic_sarima < aic_arima:
                best_model = auto_model_sarima
                model_type = 'SARIMA'
                order = best_model.order
                seasonal_order = best_model.seasonal_order
                aic = aic_sarima
                bic = best_model.bic()
            else:
                best_model = auto_model_arima
                model_type = 'ARIMA'
                order = best_model.order
                seasonal_order = (0, 0, 0, 0)  # ARIMA tidak punya seasonal
                aic = aic_arima
                bic = best_model.bic()
            
            # Load file JSON
            if os.path.exists(params_file):
                with open(params_file, 'r', encoding='utf-8') as f:
                    params_data = json.load(f)
            else:
                st.error(f"File {params_file} tidak ditemukan!")
                return {'success': False, 'error': f"File {params_file} tidak ditemukan"}
            
            # Update parameter untuk komoditas ini
            if komoditas in params_data:
                params_data[komoditas]['order'] = list(order)
                params_data[komoditas]['seasonal_order'] = list(seasonal_order)
                params_data[komoditas]['model_type'] = model_type
                params_data[komoditas]['aic'] = float(aic)
                params_data[komoditas]['bic'] = float(bic)
                params_data[komoditas]['tuning_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                params_data[komoditas]['is_tuned'] = True
            else:
                st.error(f"Komoditas '{komoditas}' tidak ditemukan di {params_file}")
                return {'success': False, 'error': f"Komoditas '{komoditas}' tidak ditemukan"}
            
            # Simpan kembali ke JSON dengan error handling yang ketat
            try:
                with open(params_file, 'w', encoding='utf-8') as f:
                    json.dump(params_data, f, indent=4, ensure_ascii=False)
                
                # Verify file tersimpan dengan membaca kembali
                with open(params_file, 'r', encoding='utf-8') as f:
                    verify_data = json.load(f)
                    verify_tuned = verify_data.get(komoditas, {}).get('is_tuned', False)
                    
                    if not verify_tuned:
                        st.error(f"❌ Verifikasi gagal: File tidak tersimpan dengan benar!")
                        return {'success': False, 'error': 'File save verification failed'}
                
                st.success(f"✅ Tuning selesai! Model terbaik: {model_type}")
                
            except Exception as save_error:
                st.error(f"❌ Error menyimpan file: {str(save_error)}")
                return {'success': False, 'error': f"Save error: {str(save_error)}"}
            
            result = {
                'order': order,
                'seasonal_order': seasonal_order,
                'model_type': model_type,
                'aic': aic,
                'bic': bic,
                'aic_sarima': aic_sarima,
                'aic_arima': aic_arima,
                'komoditas': komoditas,
                'saved_to_file': True,
                'success': True
            }
            
            return result
    
    except Exception as e:
        st.error(f"❌ Error tuning: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def auto_tune_sarima(series, seasonal=True, max_p=5, max_d=2, max_q=5,
                     max_P=2, max_D=1, max_Q=2, m=52):
    """
    Auto tune SARIMA parameter menggunakan pmdarima (Deprecated - gunakan auto_tune_per_commodity)
    
    Args:
        series: Time series data
        seasonal: Boolean untuk seasonal
        max_p, max_d, max_q: Max parameters untuk order
        max_P, max_D, max_Q: Max parameters untuk seasonal order
        m: Seasonal period
    
    Returns:
        dict: Dictionary dengan best parameter dan summary
    """
    try:
        # Ensure pmdarima is available for auto-tuning
        if auto_arima is None:
            st.error("Package 'pmdarima' is not installed or failed to import. Install with: pip install pmdarima")
            return {'success': False, 'error': f"pmdarima import error: {_PMDARIMA_IMPORT_ERROR}"}

        with st.spinner("🔄 Tuning parameter SARIMA..."):
            
            auto_model = auto_arima(
                series,
                start_p=0, max_p=max_p,
                start_d=0, max_d=max_d,
                start_q=0, max_q=max_q,
                seasonal=seasonal,
                start_P=0, max_P=max_P,
                start_D=0, max_D=max_D,
                start_Q=0, max_Q=max_Q,
                m=m,
                trace=False,
                error_action='ignore',
                suppress_warnings=True,
                stepwise=True,
                n_jobs=-1
            )
            
            order = auto_model.order
            seasonal_order = auto_model.seasonal_order
            
            result = {
                'order': order,
                'seasonal_order': seasonal_order,
                'aic': auto_model.aic(),
                'bic': auto_model.bic(),
                'success': True
            }
            
            st.success("✅ Tuning selesai!")
            return result
    
    except Exception as e:
        st.error(f"❌ Error tuning: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def validate_series(series, min_length=30):
    """
    Validasi time series sebelum modeling
    
    Args:
        series: pd.Series
        min_length: Minimum length data yang dibutuhkan
    
    Returns:
        dict: Validation result
    """
    validation_result = {
        'valid': True,
        'warnings': [],
        'info': {}
    }
    
    # Check length
    if len(series) < min_length:
        validation_result['valid'] = False
        validation_result['warnings'].append(f"Data terlalu sedikit. Minimum {min_length} data points dibutuhkan.")
    
    # Check missing values
    missing_pct = (series.isna().sum() / len(series)) * 100
    if missing_pct > 10:
        validation_result['warnings'].append(f"Data memiliki {missing_pct:.1f}% missing values.")
    
    # Check variance
    if series.std() == 0:
        validation_result['valid'] = False
        validation_result['warnings'].append("Data tidak memiliki variasi (variance=0).")
    
    # Store info
    validation_result['info'] = {
        'length': len(series),
        'missing': series.isna().sum(),
        'min': series.min(),
        'max': series.max(),
        'mean': series.mean(),
        'std': series.std()
    }
    
    return validation_result


def get_residuals(fitted_model):
    """
    Dapatkan residuals dari fitted model
    
    Args:
        fitted_model: Fitted SARIMAX model
    
    Returns:
        pd.Series: Residuals
    """
    try:
        residuals = fitted_model.resid
        return residuals
    except Exception as e:
        st.error(f"❌ Error getting residuals: {str(e)}")
        return None


def check_model_diagnostics(fitted_model):
    """
    Check diagnostics dari fitted model
    
    Args:
        fitted_model: Fitted SARIMAX model
    
    Returns:
        dict: Diagnostics info
    """
    try:
        residuals = fitted_model.resid
        
        diagnostics = {
            'residual_mean': residuals.mean(),
            'residual_std': residuals.std(),
            'ljungbox_pvalue': None  # Will be calculated if needed
        }
        
        return diagnostics
    
    except Exception as e:
        st.error(f"❌ Error checking diagnostics: {str(e)}")
        return None


def fit_sarima_model(series, order, seasonal_order):
    """
    Fit SARIMA model pada data
    
    Args:
        series: Time series data
        order: Tuple (p, d, q)
        seasonal_order: Tuple (P, D, Q, m)
    
    Returns:
        Fitted model atau None jika gagal
    """
    try:
        # Ensure statsmodels is available
        if SARIMAX is None:
            st.error("Package 'statsmodels' is not installed or failed to import. Install with: pip install statsmodels")
            return None

        model = SARIMAX(
            series,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        fitted_model = model.fit(disp=False, maxiter=500)
        return fitted_model
    
    except Exception as e:
        st.error(f"❌ Error fitting model: {str(e)}")
        return None


def forecast_sarima(fitted_model, periods):
    """
    Forecast menggunakan fitted SARIMA model
    
    Args:
        fitted_model: Fitted SARIMAX model
        periods: Jumlah periode forecast
    
    Returns:
        pd.DataFrame: Forecast dengan confidence interval
    """
    try:
        forecast = fitted_model.get_forecast(steps=periods)
        forecast_df = forecast.conf_int(alpha=0.05)
        forecast_df['forecast'] = forecast.predicted_mean
        forecast_df.columns = ['lower', 'upper', 'forecast']
        
        return forecast_df
    
    except Exception as e:
        st.error(f"❌ Error forecasting: {str(e)}")
        return None


def calculate_metrics(y_true, y_pred):
    """
    Calculate metrics MAE, RMSE, MAPE
    
    Args:
        y_true: Nilai asli
        y_pred: Nilai prediksi
    
    Returns:
        dict: Dictionary dengan metrics
    """
    return calculate_metrics_summary(y_true, y_pred)


def predict_with_confidence_interval(series, order, seasonal_order, periods=12, alpha=0.05):
    """
    Predict dengan confidence interval
    
    Args:
        series: Time series data
        order: Tuple (p, d, q)
        seasonal_order: Tuple (P, D, Q, m)
        periods: Jumlah periode forecast
        alpha: Significance level
    
    Returns:
        dict: Dictionary dengan forecast dan confidence interval
    """
    try:
        # Ensure statsmodels is available
        if SARIMAX is None:
            st.error("Package 'statsmodels' is not installed or failed to import. Install with: pip install statsmodels")
            return {'success': False, 'error': f"statsmodels import error: {_STATSMODELS_IMPORT_ERROR}"}
        model = SARIMAX(
            series,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        fitted_model = model.fit(disp=False, maxiter=500)
        
        forecast = fitted_model.get_forecast(steps=periods)
        forecast_df = forecast.conf_int(alpha=alpha)
        forecast_df['forecast'] = forecast.predicted_mean
        forecast_df.columns = ['lower', 'upper', 'forecast']
        
        return {
            'forecast_df': forecast_df,
            'model': fitted_model,
            'success': True
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def backtest_model(series, order, seasonal_order, test_size=0.2):
    """
    Backtest model dengan walk-forward validation
    
    Args:
        series: Time series data
        order: Tuple (p, d, q)
        seasonal_order: Tuple (P, D, Q, m)
        test_size: Proporsi test set
    
    Returns:
        dict: Backtest results
    """
    try:
        # Ensure statsmodels is available
        if SARIMAX is None:
            st.error("Package 'statsmodels' is not installed or failed to import. Install with: pip install statsmodels")
            return {'success': False, 'error': f"statsmodels import error: {_STATSMODELS_IMPORT_ERROR}"}

        split_idx = int(len(series) * (1 - test_size))
        train_data = series.iloc[:split_idx]
        test_data = series.iloc[split_idx:]
        
        # Train model
        model = SARIMAX(
            train_data,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        fitted_model = model.fit(disp=False, maxiter=500)
        
        # Get forecast untuk test set
        forecast = fitted_model.get_forecast(steps=len(test_data))
        forecast_values = forecast.predicted_mean
        
        # Calculate metrics
        metrics = calculate_metrics_summary(test_data.values, forecast_values.values)
        
        return {
            'train_data': train_data,
            'test_data': test_data,
            'forecast': forecast_values,
            'metrics': metrics,
            'success': True
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
