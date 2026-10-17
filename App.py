import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ---------------------------------------------------------
# THÔNG TIN TÀI KHOẢN NGÂN HÀNG
# ---------------------------------------------------------
BANK_ID = "VBA"                # Agribank (Mã VietQR chuẩn: VBA)
ACCOUNT_NO = "8888889040806"   # Số tài khoản của bạn
ACCOUNT_NAME = "HUA HOANG KHAI"# Tên chủ tài khoản

# ---------------------------------------------------------
# CẤU HÌNH TRANG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Trà Sữa Mr Khải Lốc Xoáy 🌪️🧋",
    page_icon="🧋",
    layout="wide"
)

# ---------------------------------------------------------
# CẤU HÌNH GIAO DIỆN MÀU SẮC GEN Z (CSS)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Theme màu chủ đạo: Hồng Đào & Cam Coral */
    .stApp {
        background-color: #FFF9F5;
    }
    
    /* Header chính */
    .main-title {
        text-align: center;
        color: #FF5E7E;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
        font-size: 2.3rem;
        margin-bottom: 0px;
        text-shadow: 1px 1px 2px #FFD1DC;
    }
    
    .sub-title {
        text-align: center;
        color: #FFA07A;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }

    /* Style khung Container */
    [data-testid="stVerticalBlock"] > div {
        border-radius: 15px;
    }
    
    /* Highlight giá tiền */
    .price-tag {
        background-color: #FFE4E1;
        color: #FF4500;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        font-size: 1.1rem;
    }

    /* Bảng hóa đơn */
    .stTable {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CƠ SỞ DỮ LIỆU SẢN PHẨM & HÌNH ẢNH MINH HỌA
# ---------------------------------------------------------
MENU_TEA = {
    "Trà Sữa Truyền Thống": {
        "price": 30000,
        "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?w=500&q=80"
    },
    "Trà Sữa Trân Châu Đường Đen": {
        "price": 35000,
        "image": "https://images.unsplash.com/photo-1541658016709-82535e94bc69?w=500&q=80"
    },
    "Trà Sữa Thái Xanh": {
        "price": 32000,
        "image": "https://images.unsplash.com/photo-1627522460108-212628122289?w=500&q=80"
    },
    "Trà Sữa Ô Long": {
        "price": 35000,
        "image": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&q=80"
    },
    "Trà Sữa Matcha": {
        "price": 38000,
        "image": "https://images.unsplash.com/photo-1536256263959-770b48d82b0a?w=500&q=80"
    },
    "Trà Sữa Dâu Tây": {
        "price": 35000,
        "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&q=80"
    },
    "Trà Đào Cam Sả": {
        "price": 35000,
        "image": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&q=80"
    },
    "Trà Dâu Tằm": {
        "price": 32000,
        "image": "https://images.unsplash.com/photo-1556881286-fc6915169721?w=500&q=80"
    },
}

SIZE_OPTIONS = {
    "S (Vừa)": 0,
    "M (Lớn)": 5000,
    "L (Đặc biệt)": 10000
}

TOPPING_OPTIONS = {
    "Trân châu đen 🧋": 5000,
    "Trân châu trắng 💎": 7000,
    "Thạch trái cây 🍓": 5000,
    "Pudding trứng 🍮": 8000,
    "Kem Cheese 🧀": 10000
}

SUGAR_LEVELS = ["100% (Bình thường)", "70%", "50%", "30%", "0% (Không đường)"]
ICE_LEVELS = ["100% (Bình thường)", "70%", "50%", "30%", "0% (Không đá)"]

if "cart" not in st.session_state:
    st.session_state.cart = []
if "invoice_paid" not in st.session_state:
    st.session_state.invoice_paid = False

# ---------------------------------------------------------
# HÀM XUẤT HÓA ĐƠN (.TXT)
# ---------------------------------------------------------
def create_txt_invoice(customer_name, cart, total_amount, discount, final_amount):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    content = f"{'='*40}\n"
    content += f"{'HÓA ĐƠN BÁN HÀNG - MR KHẢI LỐC XOÁY':^40}\n"
    content += f"{'='*40}\n"
    content += f"Thời gian: {now}\n"
    content += f"Khách hàng: {customer_name if customer_name else 'Khách vãng lai'}\n"
    content += f"{'-'*40}\n"
    
    for idx, item in enumerate(cart, 1):
        content += f"{idx}. {item['Tên món']} ({item['Size']})\n"
        content += f"   - Đường: {item['Đường']} | Đá: {item['Đá']}\n"
        if item['Topping'] != "Không":
            content += f"   - Topping: {item['Topping']}\n"
        content += f"   SL: {item['Số lượng']} x {item['Đơn giá']:,} = {item['Thành tiền']:,} VNĐ\n"
        
    content += f"{'-'*40}\n"
    content += f"Tổng tiền gốc: {total_amount:,} VNĐ\n"
    content += f"Giảm giá: {discount}%\n"
    content += f"TỔNG THANH TOÁN: {final_amount:,} VNĐ\n"
    content += f"{'='*40}\n"
    content += f"{'Cảm ơn bạn đã ủng hộ Mr Khải Lốc Xoáy! 💕':^40}\n"
    return content

# ---------------------------------------------------------
# HEADER VÀ TIÊU ĐỀ
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>🧋 TRÀ SỮA MR KHẢI LỐC XOÁY 🌪️</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>✨ Đậm vị trà - Đậm gu Gen Z ✨</p>", unsafe_allow_html=True)

# Hiển thị Logo nếu có
if os.path.exists("file_00000000d3fc8207810f0b04c88661e1.png"):
    col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
    with col_img2:
        st.image("file_00000000d3fc8207810f0b04c88661e1.png", use_container_width=True)

st.markdown("---")

col_left, col_right = st.columns([1.2, 0.8])

# ==================== CỘT TRÁI: ĐẶT MÓN ====================
with col_left:
    st.subheader("📋 Order Món Ngay")
    
    customer_name = st.text_input("👤 Tên khách hàng (hoặc biệt danh):", placeholder="Ví dụ: Khải Lốc Xoáy, Bé Dâu...")

    # Chọn món
    selected_tea = st.selectbox("🍹 Chọn loại nước mát lạnh:", list(MENU_TEA.keys()))
    
    # Hiển thị hình ảnh minh họa thực tế của món
    tea_info = MENU_TEA[selected_tea]
    col_pic, col_opt = st.columns([1, 1.2])
    
    with col_pic:
        st.image(tea_info["image"], caption=selected_tea, use_container_width=True)
        
    with col_opt:
        quantity = st.number_input("🔢 Số lượng ly:", min_value=1, value=1, step=1)
        selected_size = st.selectbox("📏 Chọn Size:", list(SIZE_OPTIONS.keys()))
        selected_sugar = st.selectbox("🍬 Mức đường:", SUGAR_LEVELS)
        selected_ice = st.selectbox("🧊 Mức đá:", ICE_LEVELS)

    # Chọn Topping
    selected_toppings = st.multiselect(
        "✨ Thêm Topping mê ly:",
        options=list(TOPPING_OPTIONS.keys())
    )

    # Tính toán giá tiền
    base_price = tea_info["price"]
    size_price = SIZE_OPTIONS[selected_size]
    topping_price = sum(TOPPING_OPTIONS[t] for t in selected_toppings)
    unit_price = base_price + size_price + topping_price
    item_total = unit_price * quantity

    st.markdown(f"<div class='price-tag'>💡 Đơn giá: {unit_price:,} VNĐ / ly</div>", unsafe_allow_html=True)
    st.write("")

    if st.button("🛍️ THÊM VÀO GIỎ HÀNG", type="primary", use_container_width=True):
        topping_clean = [t.split()[0] + " " + t.split()[1] for t in selected_toppings]
        topping_str = ", ".join(topping_clean) if topping_clean else "Không"
        
        item_data = {
            "Tên món": selected_tea,
            "Size": selected_size.split()[0],
            "Đường": selected_sugar.split()[0],
            "Đá": selected_ice.split()[0],
            "Topping": topping_str,
            "Đơn giá": unit_price,
            "Số lượng": quantity,
            "Thành tiền": item_total
        }
        st.session_state.cart.append(item_data)
        st.session_state.invoice_paid = False
        st.toast(f"Đã thêm **{quantity}x {selected_tea}** vào giỏ hàng!", icon="🧋")

# ==================== CỘT PHẢI: GIỎ HÀNG ====================
with col_right:
    st.subheader("🛒 Giỏ Hàng Của Bạn")

    if not st.session_state.cart:
        st.info("Giỏ hàng đang trống nè! Hãy chọn món ngon ở bên trái nhé 👈")
    else:
        df_cart = pd.DataFrame(st.session_state.cart)
        st.dataframe(
            df_cart[["Tên món", "Size", "Topping", "Số lượng", "Thành tiền"]],
            use_container_width=True,
            hide_index=True
        )

        if st.button("🗑️ Làm mới giỏ hàng"):
            st.session_state.cart = []
            st.session_state.invoice_paid = False
            st.rerun()

        st.markdown("---")
        total_price = df_cart["Thành tiền"].sum()
        
        col_disc, col_dummy = st.columns(2)
        with col_disc:
            discount = st.number_input("🎁 Mã giảm giá (%):", min_value=0, max_value=100, value=0, step=5)
        
        final_price = int(total_price * (1 - discount / 100))

        st.markdown(f"### 💵 Tổng tạm tính: **{total_price:,} VNĐ**")
        if discount > 0:
            st.markdown(f"### 🔥 Sau giảm giá ({discount}%): <span style='color:#FF5E7E'>{final_price:,} VNĐ</span>", unsafe_allow_html=True)

        if st.button("💳 XÁC NHẬN CHUYỂN KHOẢN", type="primary", use_container_width=True):
            st.session_state.invoice_paid = True
            st.balloons()

# ---------------------------------------------------------
# KHU VỰC MA QR THANH TOÁN & HÓA ĐƠN
# ---------------------------------------------------------
if st.session_state.get("invoice_paid") and st.session_state.cart:
    st.markdown("---")
    st.success("🎉 Đơn hàng đã sẵn sàng! Vui lòng quét mã QR Agribank dưới đây để thanh toán:")

    # 1. TẠO MÃ QR VIETQR TỰ ĐỘNG
    add_info_text = f"TT {customer_name if customer_name else 'Khach'}"
    acc_name_encoded = urllib.parse.quote(ACCOUNT_NAME)
    add_info_encoded = urllib.parse.quote(add_info_text)

    # Mã VietQR chuẩn cho Agribank là VBA
    qr_url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png?amount={final_price}&addInfo={add_info_encoded}&accountName={acc_name_encoded}"

    col_qr1, col_qr2 = st.columns([1, 1.2])
    with col_qr1:
        st.image(qr_url, caption="Mã QR Chuyển Khoản Tự Động", use_container_width=True)
    with col_qr2:
        st.markdown("### 📲 Thông Tin Chuyển Khoản")
        st.write(f"🏦 **Ngân hàng:** Agribank")
        st.write(f"💳 **Số tài khoản:** `{ACCOUNT_NO}`")
        st.write(f"👤 **Chủ tài khoản:** {ACCOUNT_NAME}")
        st.write(f"💰 **Số tiền:** `{final_price:,} VNĐ`")
        st.write(f"📝 **Nội dung:** `{add_info_text}`")

    # 2. HÓA ĐƠN CHI TIẾT
    invoice_box = st.container(border=True)
    with invoice_box:
        st.markdown("<h2 style='text-align: center; color: #FF5E7E;'>🧋 HÓA ĐƠN BAN HÀNG - MR KHẢI LỐC XOÁY</h2>", unsafe_allow_html=True)
        st.write(f"⏰ **Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.write(f"👤 **Khách hàng:** {customer_name if customer_name else 'Khách vãng lai'}")
        
        st.table(pd.DataFrame(st.session_state.cart)[["Tên món", "Size", "Đường", "Đá", "Topping", "Số lượng", "Thành tiền"]])
        
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Tổng tiền món:** {total_price:,} VNĐ")
            st.write(f"**Giảm giá:** {discount}%")
        with c2:
            st.markdown(f"### TỔNG THANH TOÁN: <span style='color:#FF5E7E'>{final_price:,} VNĐ</span>", unsafe_allow_html=True)

    txt_data = create_txt_invoice(customer_name, st.session_state.cart, total_price, discount, final_price)
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📥 Tải hóa đơn (.TXT)",
            data=txt_data,
            file_name=f"HoaDon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_dl2:
        if st.button("🔄 Tạo đơn hàng mới", use_container_width=True):
            st.session_state.cart = []
            st.session_state.invoice_paid = False
            st.rerun()
