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

# ---------------------------------------------------------
# TƯƠNG THÍCH NHIỀU PHIÊN BẢN STREAMLIT
# (use_container_width đã bị thay bằng width="stretch" ở bản mới)
# ---------------------------------------------------------
def _stretch(func):
    try:
        if "width" in inspect.signature(func).parameters:
            return {"width": "stretch"}
    except (TypeError, ValueError):
        pass
    return {"use_container_width": True}


FULL_BTN = _stretch(st.button)
FULL_IMG = _stretch(st.image)
FULL_DF = _stretch(st.dataframe)
FULL_TABLE_DL = _stretch(st.download_button)

# ---------------------------------------------------------
# GIAO DIỆN MÀU SẮC GEN Z (CSS)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #FFFDFB; }
    .main-title {
        text-align: center; color: #FF477E; font-family: 'Inter', sans-serif;
        font-weight: 900; font-size: 2.3rem; margin-bottom: 0px;
        text-shadow: 2px 2px 4px #FFD6E0;
    }
    .sub-title {
        text-align: center; color: #FF70A6; font-weight: 600;
        font-size: 1.1rem; margin-bottom: 15px;
    }
    .price-badge {
        background: linear-gradient(135deg, #FF70A6, #FF477E); color: white;
        padding: 6px 14px; border-radius: 20px; font-weight: bold;
        font-size: 1rem; display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# MENU BẢNG GIÁ & HÌNH ẢNH
# ---------------------------------------------------------
MENU_TEA = {
    "Trà Sữa Truyền Thống": {
        "price": 30000, "category": "Trà Sữa",
        "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?auto=format&fit=crop&w=600&q=80",
    },
    "Trà Sữa Trân Châu Đường Đen": {
        "price": 35000, "category": "Trà Sữa",
        "image": "https://images.unsplash.com/photo-1541658016709-82535e94bc69?auto=format&fit=crop&w=600&q=80",
    },
    "Trà Sữa Thái Xanh": {
        "price": 32000, "category": "Trà Sữa",
        "image": "https://images.unsplash.com/photo-1627522460108-212628122289?auto=format&fit=crop&w=600&q=80",
    },
    "Trà Sữa Ô Long": {
        "price": 35000, "category": "Trà Sữa",
        "image": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=600&q=80",
    },
    "Trà Sữa Matcha": {
        "price": 38000, "category": "Trà Sữa",
        "image": "https://images.unsplash.com/photo-1536256263959-770b48d82b0a?auto=format&fit=crop&w=600&q=80",
    },
    "Trà Sữa Dâu Tây": {
        "price": 35000, "category": "Trà Trái Cây",
        "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=600&q=80",
    },
    "Trà Đào Cam Sả": {
        "price": 35000, "category": "Trà Trái Cây",
        "image": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=600&q=80",
    },
    "Trà Dâu Tằm Mát Lạnh": {
        "price": 32000, "category": "Trà Trái Cây",
        "image": "https://images.unsplash.com/photo-1556881286-fc6915169721?auto=format&fit=crop&w=600&q=80",
    },
}

SIZE_OPTIONS = {"S (Vừa)": 0, "M (Lớn)": 5000, "L (Đặc biệt)": 10000}
TOPPING_OPTIONS = {
    "Trân châu đen 🧋": 5000,
    "Trân châu trắng 💎": 7000,
    "Thạch trái cây 🍓": 5000,
    "Pudding trứng 🍮": 8000,
    "Kem Cheese 🧀": 10000,
}
SUGAR_LEVELS = ["100% (Bình thường)", "70%", "50%", "30%", "0% (Không đường)"]
ICE_LEVELS = ["100% (Bình thường)", "70%", "50%", "30%", "0% (Không đá)"]

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "invoice" not in st.session_state:
    st.session_state.invoice = None      # ảnh chụp đơn đã tạo (chống lệch số tiền)
HISTORY_COLS = ["time", "customer", "total_items", "final_amount"]


def load_history() -> list:
    try:
        if os.path.exists(HISTORY_FILE):
            return pd.read_csv(HISTORY_FILE).to_dict("records")
    except Exception:
        pass
    return []


def save_history(rows: list) -> None:
    try:
        pd.DataFrame(rows, columns=HISTORY_COLS).to_csv(HISTORY_FILE, index=False)
    except Exception:
        pass  # môi trường chỉ-đọc: vẫn chạy bình thường, chỉ không lưu file


def to_ascii(text: str, max_len: int = 25) -> str:
    """Nội dung chuyển khoản ngân hàng không dấu, chỉ chữ/số/khoảng trắng."""
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^A-Za-z0-9 ]", "", text).strip()
    return text[:max_len] or "Khach"


if "order_history" not in st.session_state:
    st.session_state.order_history = load_history()


def clean_topping(label: str) -> str:
    """Bỏ emoji ở cuối, giữ nguyên tên đầy đủ: 'Trân châu đen 🧋' -> 'Trân châu đen'."""
    return label.rsplit(" ", 1)[0]


def create_txt_invoice(inv: dict) -> str:
    line = "=" * 40
    content = f"{line}\n{'HÓA ĐƠN BÁN HÀNG - MR KHẢI LỐC XOÁY':^40}\n{line}\n"
    content += f"Thời gian: {inv['time']}\n"
    content += f"Khách hàng: {inv['customer']}\n"
    if inv["note"]:
        content += f"Ghi chú: {inv['note']}\n"
    content += f"{'-' * 40}\n"
    for idx, item in enumerate(inv["cart"], 1):
        content += f"{idx}. {item['Tên món']} ({item['Size']})\n"
        content += f"   - Đường: {item['Đường']} | Đá: {item['Đá']}\n"
        if item["Topping"] != "Không":
            content += f"   - Topping: {item['Topping']}\n"
        content += f"   SL: {item['Số lượng']} x {item['Đơn giá']:,} = {item['Thành tiền']:,} VNĐ\n"
    content += f"{'-' * 40}\n"
    content += f"Tổng tiền món: {inv['total']:,} VNĐ\n"
    content += f"Giảm giá: {inv['discount']}%\n"
    content += f"TỔNG THANH TOÁN: {inv['final']:,} VNĐ\n"
    content += f"{line}\n{'Cảm ơn bạn đã ủng hộ Mr Khải Lốc Xoáy! 💕':^40}\n"
    return content


# ---------------------------------------------------------
# TIÊU ĐỀ & TABS
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>🧋 TRÀ SỮA MR KHẢI LỐC XOÁY 🌪️</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>✨ Đậm vị trà - Đậm gu Gen Z ✨</p>", unsafe_allow_html=True)

BANNER = os.path.join(BASE_DIR, "file_00000000d3fc8207810f0b04c88661e1.png")
if os.path.exists(BANNER):
    _, c_mid, _ = st.columns([1, 2, 1])
    with c_mid:
        st.image(BANNER, **FULL_IMG)

tab_order, tab_dashboard = st.tabs(["🛍️ Đặt Món & Thanh Toán", "📊 Báo Cáo Doanh Thu"])

# =========================================================
# TAB 1: ĐẶT MÓN & THANH TOÁN
# =========================================================
with tab_order:
    col_left, col_right = st.columns([1.25, 0.75])

    # ---------------- CỘT TRÁI: MENU ----------------
    with col_left:
        st.subheader("📋 Chọn Món Đồ Uống")

        c_search, c_filter = st.columns([2, 1])
        with c_search:
            search_query = st.text_input("🔍 Tìm tên món:", placeholder="Ví dụ: Matcha, Thái xanh...")
        with c_filter:
            category_filter = st.selectbox("📂 Danh mục:", ["Tất cả", "Trà Sữa", "Trà Trái Cây"])

        filtered_menu = {
            k: v
            for k, v in MENU_TEA.items()
            if (category_filter == "Tất cả" or v["category"] == category_filter)
            and (search_query.strip().lower() in k.lower())
        }

        if not filtered_menu:
            st.warning("Không tìm thấy món phù hợp!")
        else:
            selected_tea = st.selectbox("🥤 Chọn món uống:", list(filtered_menu.keys()))
            tea_info = MENU_TEA[selected_tea]

            with st.container(border=True):
                col_pic, col_opt = st.columns([1, 1.1])
                with col_pic:
                    st.image(tea_info["image"], caption=selected_tea, **FULL_IMG)
                with col_opt:
                    quantity = st.number_input("🔢 Số lượng:", min_value=1, value=1, step=1)
                    selected_size = st.selectbox("📏 Size:", list(SIZE_OPTIONS.keys()))
                    selected_sugar = st.selectbox("🍬 Đường:", SUGAR_LEVELS)
                    selected_ice = st.selectbox("🧊 Đá:", ICE_LEVELS)

                selected_toppings = st.multiselect("✨ Topping thêm:", options=list(TOPPING_OPTIONS.keys()))

                unit_price = (
                    tea_info["price"]
                    + SIZE_OPTIONS[selected_size]
                    + sum(TOPPING_OPTIONS[t] for t in selected_toppings)
                )
                item_total = unit_price * int(quantity)

                st.markdown(
                    f"<div class='price-badge'>💡 Đơn giá: {unit_price:,} VNĐ / ly</div>",
                    unsafe_allow_html=True,
                )
                st.write("")

                if st.button("➕ THÊM VÀO GIỎ HÀNG", type="primary", **FULL_BTN):
                    topping_str = (
                        ", ".join(clean_topping(t) for t in selected_toppings)
                        if selected_toppings
                        else "Không"
                    )
                    st.session_state.cart.append(
                        {
                            "Tên món": selected_tea,
                            "Size": selected_size.split()[0],
                            "Đường": selected_sugar.split()[0],
                            "Đá": selected_ice.split()[0],
                            "Topping": topping_str,
                            "Đơn giá": unit_price,
                            "Số lượng": int(quantity),
                            "Thành tiền": item_total,
                        }
                    )
                    st.session_state.invoice = None   # giỏ đổi -> hóa đơn cũ hết hiệu lực
                    st.toast(f"Đã thêm {quantity}x {selected_tea} vào giỏ!", icon="🧋")

    # ---------------- CỘT PHẢI: GIỎ HÀNG ----------------
    with col_right:
        st.subheader("🛒 Giỏ Hàng Mua Sắm")

        customer_name = st.text_input("👤 Tên khách hàng:", placeholder="Tên khách hàng...")
        order_note = st.text_input("📝 Ghi chú đơn hàng:", placeholder="Ví dụ: Mang đi, Ít ngọt...")

        if not st.session_state.cart:
            st.info("Giỏ hàng đang trống!")
        else:
            df_cart = pd.DataFrame(st.session_state.cart)
            st.dataframe(
                df_cart[["Tên món", "Size", "Topping", "Số lượng", "Thành tiền"]],
                hide_index=True,
                **FULL_DF,
            )

            rm_options = [
                f"{i + 1}. {r['Tên món']} ({r['Size']}) x{r['Số lượng']}"
                for i, r in enumerate(st.session_state.cart)
            ]
            rm_choice = st.selectbox("❌ Xóa 1 món khỏi giỏ:", ["— Chọn món —"] + rm_options)
            if rm_choice != "— Chọn món —" and st.button("Xóa món đã chọn"):
                st.session_state.cart.pop(rm_options.index(rm_choice))
                st.session_state.invoice = None
                st.rerun()

            if st.button("🗑️ Xóa toàn bộ giỏ hàng"):
                st.session_state.cart = []
                st.session_state.invoice = None
                st.rerun()

            st.markdown("---")
            total_price = int(df_cart["Thành tiền"].sum())
            discount = st.number_input("🎁 Khuyến mãi (%):", min_value=0, max_value=100, value=0, step=5)
            final_price = int(total_price * (1 - discount / 100))

            st.markdown(f"### Tổng tạm tính: **{total_price:,} VNĐ**")
            if discount > 0:
                st.markdown(
                    f"### 🔥 Sau giảm giá: <span style='color:#FF477E'>{final_price:,} VNĐ</span>",
                    unsafe_allow_html=True,
                )

            if st.button("💳 TẠO ĐƠN & QUÉT MÃ QR", type="primary", **FULL_BTN):
                now = datetime.now()
                customer = customer_name.strip() if customer_name.strip() else "Khách vãng lai"
                st.session_state.invoice = {
                    "time": now.strftime("%d/%m/%Y %H:%M:%S"),
                    "stamp": now.strftime("%Y%m%d_%H%M%S"),
                    "customer": customer,
                    "note": order_note.strip(),
                    "cart": [dict(i) for i in st.session_state.cart],
                    "total": total_price,
                    "discount": int(discount),
                    "final": final_price,
                }
                st.session_state.order_history.append(
                    {
                        "time": st.session_state.invoice["time"],
                        "customer": customer,
                        "total_items": int(df_cart["Số lượng"].sum()),
                        "final_amount": final_price,
                    }
                )
                save_history(st.session_state.order_history)
                st.balloons()

    # ---------------- HIỂN THỊ MÃ QR & HÓA ĐƠN ----------------
    inv = st.session_state.invoice
    if inv:
        st.markdown("---")
        st.success("🎉 Đã hoàn tất tạo đơn! Vui lòng quét mã QR để chuyển khoản:")

        raw_name = inv["customer"] if inv["customer"] != "Khách vãng lai" else "Khach"
        add_info_text = f"TT {to_ascii(raw_name)}"
        qr_url = (
            f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png"
            f"?amount={inv['final']}"
            f"&addInfo={urllib.parse.quote(add_info_text)}"
            f"&accountName={urllib.parse.quote(ACCOUNT_NAME)}"
        )

        col_qr1, col_qr2 = st.columns([1, 1.2])
        with col_qr1:
            st.image(qr_url, caption="Mã QR Agribank Tự Động", **FULL_IMG)
        with col_qr2:
            st.markdown("### 📲 Thông Tin Chuyển Khoản")
            st.write("🏦 **Ngân hàng:** Agribank")
            st.write(f"💳 **Số tài khoản:** `{ACCOUNT_NO}`")
            st.write(f"👤 **Chủ tài khoản:** {ACCOUNT_NAME}")
            st.write(f"💰 **Số tiền thanh toán:** `{inv['final']:,} VNĐ`")
            st.write(f"📝 **Nội dung chuyển khoản:** `{add_info_text}`")

        with st.container(border=True):
            st.markdown(
                "<h2 style='text-align: center; color: #FF477E;'>🧋 HÓA ĐƠN BÁN HÀNG - MR KHẢI LỐC XOÁY</h2>",
                unsafe_allow_html=True,
            )
            st.write(f"⏰ **Thời gian:** {inv['time']}")
            st.write(f"👤 **Khách hàng:** {inv['customer']}")
            if inv["note"]:
                st.write(f"📌 **Ghi chú:** {inv['note']}")

            st.table(
                pd.DataFrame(inv["cart"])[
                    ["Tên món", "Size", "Đường", "Đá", "Topping", "Số lượng", "Thành tiền"]
                ]
            )

            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Tổng tiền:** {inv['total']:,} VNĐ")
                st.write(f"**Giảm giá:** {inv['discount']}%")
            with c2:
                st.markdown(
                    f"### TỔNG CỦA BẠN: <span style='color:#FF477E'>{inv['final']:,} VNĐ</span>",
                    unsafe_allow_html=True,
                )

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 Tải hóa đơn file (.TXT)",
                data=create_txt_invoice(inv),
                file_name=f"HoaDon_{inv['stamp']}.txt",
                mime="text/plain",
                **FULL_TABLE_DL,
            )
        with col_dl2:
            if st.button("🔄 Đặt đơn tiếp theo", **FULL_BTN):
                st.session_state.cart = []
                st.session_state.invoice = None
                st.rerun()

# =========================================================
# TAB 2: BÁO CÁO DOANH THU
# =========================================================
with tab_dashboard:
    st.subheader("📈 Thống Kê Doanh Thu & Lịch Sử Bán Hàng")

    if not st.session_state.order_history:
        st.info("Chưa có đơn hàng nào trong phiên làm việc này.")
    else:
        df_history = pd.DataFrame(st.session_state.order_history)

        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng số đơn", f"{len(df_history)} đơn")
        m2.metric("Tổng ly đã bán", f"{int(df_history['total_items'].sum())} ly")
        m3.metric("Tổng doanh thu", f"{int(df_history['final_amount'].sum()):,} VNĐ")

        st.markdown("---")
        st.download_button(
            "📥 Tải báo cáo (.CSV)",
            data=df_history.to_csv(index=False).encode("utf-8-sig"),
            file_name="BaoCao_DoanhThu.csv",
            mime="text/csv",
        )
        st.dataframe(
            df_history.rename(
                columns={
                    "time": "Thời Gian",
                    "customer": "Khách Hàng",
                    "total_items": "Số Ly",
                    "final_amount": "Thành Tiền (VNĐ)",
                }
            ),
            hide_index=True,
            **FULL_DF,
)
