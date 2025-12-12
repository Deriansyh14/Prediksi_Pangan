#!/usr/bin/env python3
"""
Test script untuk debug masalah tuning parameter
"""
import sys
import os
import json
sys.path.append(os.path.dirname(__file__))

# Dummy streamlit untuk bypass st.error, st.success
class DummySt:
    def error(self, msg):
        print(f"❌ {msg}")
    def success(self, msg):
        print(f"✅ {msg}")
    def warning(self, msg):
        print(f"⚠️ {msg}")
    def spinner(self, msg):
        class Ctx:
            def __enter__(self):
                print(f"🔄 {msg}")
                return self
            def __exit__(self, *args):
                pass
        return Ctx()

# Replace st
import streamlit as st
for attr in dir(DummySt()):
    if not attr.startswith('_'):
        setattr(st, attr, getattr(DummySt(), attr))

import pandas as pd
import numpy as np
from src.forecasting import auto_tune_per_commodity
from src.load_model import SARIMAParamsLoader

# Load test data
print("=" * 60)
print("TEST: Tuning Parameter")
print("=" * 60)

# Create dummy data
np.random.seed(42)
dates = pd.date_range('2020-01-01', periods=100, freq='W')
data = np.random.randint(20000, 40000, 100)
series = pd.Series(data, index=dates)

print(f"✓ Data shape: {series.shape}")
print(f"✓ Data range: {series.min()} - {series.max()}")

# Run tuning
print("\n--- Running Tuning ---")
result = auto_tune_per_commodity(series, 'Beras Premium')

print("\n--- Tuning Result ---")
if result and result.get('success'):
    print(f"✓ Success: {result['success']}")
    print(f"✓ Model Type: {result['model_type']}")
    print(f"✓ Order: {result['order']}")
    print(f"✓ Seasonal Order: {result['seasonal_order']}")
    print(f"✓ AIC: {result['aic']:.2f}")
    print(f"✓ Saved to file: {result['saved_to_file']}")
else:
    print(f"✗ Failed: {result.get('error', 'unknown error')}")
    sys.exit(1)

# Verify file was saved
print("\n--- Verifying File Save ---")
with open('models/best_params.json', 'r', encoding='utf-8') as f:
    params = json.load(f)
    beras = params.get('Beras Premium', {})
    
    print(f"✓ is_tuned: {beras.get('is_tuned')}")
    print(f"✓ model_type: {beras.get('model_type')}")
    print(f"✓ aic: {beras.get('aic')}")
    print(f"✓ tuning_date: {beras.get('tuning_date')}")
    
    if beras.get('is_tuned'):
        print("\n✅ SUCCESS: Parameter saved correctly!")
    else:
        print("\n❌ FAILURE: is_tuned is still False!")
        sys.exit(1)

# Verify params loader can read it
print("\n--- Verifying Params Loader ---")
loader = SARIMAParamsLoader()
params_loaded = loader.load_params()
beras_loaded = params_loaded.get('Beras Premium', {})

print(f"✓ Loaded is_tuned: {beras_loaded.get('is_tuned')}")
print(f"✓ Loaded model_type: {beras_loaded.get('model_type')}")

if beras_loaded.get('is_tuned'):
    print("\n✅ SUCCESS: Params loader reads correctly!")
else:
    print("\n❌ FAILURE: Params loader cannot read is_tuned!")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
