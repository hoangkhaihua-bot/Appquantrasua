import inspect
import os
import re
import unicodedata
import urllib.parse
from datetime import datetime

import pandas as pd
import streamlit as st

# set_page_config PHẢI là lệnh Streamlit đầu tiên
st.set_page_config(
    page_title="Trà Sữa Mr Khải Lốc Xoáy 🌪️🧋",
    page_icon="🧋",
    layout="wide",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "order_history.csv")

# ---------------------------------------------------------
# THÔNG TIN TÀI KHOẢN NGÂN HÀNG
# (Khuyến nghị: đặt trong .streamlit/secrets.toml hoặc mục Secrets
#  của Streamlit Cloud để không lộ số tài khoản trên GitHub công khai)
# ---------------------------------------------------------
def _secret(key, default):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


BANK_ID = _secret("BANK_ID", "VBA")                       # Agribank
ACCOUNT_NO = _secret("ACCOUNT_NO", "8888889040806")
ACCOUNT_NAME = _secret("ACCOUNT_NAME", "HUA HOANG KHAI")
