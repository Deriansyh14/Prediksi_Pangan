"""
Environment check script for the project.
Run with: python check_env.py
"""

import importlib
import sys

reqs = [
    'streamlit', 'pandas', 'numpy', 'statsmodels', 'pmdarima',
    'scikit-learn', 'plotly', 'matplotlib', 'seaborn',
    'openpyxl', 'xlrd', 'python_dateutil'
]

# Map to import names where they differ
import_map = {
    'python_dateutil': 'dateutil'
}

results = {}
missing = []

print(f"Python executable: {sys.executable}")
print(f"Platform: {sys.platform}\n")

for pkg in reqs:
    import_name = import_map.get(pkg, pkg)
    try:
        mod = importlib.import_module(import_name)
        # get version attribute safely
        version = getattr(mod, '__version__', None) or getattr(mod, 'version', None)
        print(f"OK  - {pkg}: version={version}")
        results[pkg] = {'installed': True, 'version': str(version)}
    except Exception as e:
        print(f"MISSING - {pkg}: {e.__class__.__name__}: {e}")
        results[pkg] = {'installed': False, 'error': str(e)}
        missing.append(pkg)

print('\nSummary:')
if not missing:
    print('All required packages appear to be installed.')
else:
    print(f'Missing packages: {missing}')
    print('\nSuggested install command:')
    print('python -m pip install ' + ' '.join([p for p in missing if p != 'python_dateutil']))

# small exit code for CI use
sys.exit(0)
