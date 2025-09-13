import streamlit
print("Streamlit version:", streamlit.__version__)

try:
    import plotly
    print("Plotly OK")
except ImportError:
    print("Plotly not installed")

try:
    import pandas
    print("Pandas OK")
except ImportError:
    print("Pandas not installed")

print("All imports test completed")
