import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ---------------------------------------------------------
# THÔNG TIN TÀI KHOẢN NGÂN HÀNG
# ---------------------------------------------------------
BANK_ID = "VBA"                # Agribank (Mã VietQR chuẩn: VBA)
ACCOUNT_NO = "8888889040806"   # Số tài khoản
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
# CẤU HÌNH GIAO DIỆN MÀU SẮC GEN Z & STYLING
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFDFB;
    }
    
    .main-title {
        text-align: center;
        color: #FF477E;
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 2.5rem;
        margin-bottom: 0px;
        text-shadow: 2px 2px 4px #FFD6E0;
    }
    
    .sub-title {
        text-align: center;
        color: #FF70A6;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 15px;
    }

    .price-badge {
        background: linear-gradient(135deg, #FF70A6, #FF477E);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1rem;
        display: inline-block;
    }

    .card-container {
        border: 1px solid #FFE3EC;
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0px 4px 12px rgba(255, 71, 126, 0.08);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MENU CÓ HÌNH ẢNH CHUẨN THỰC TẾ & BẢNG GIÁ
# ---------------------------------------------------------
MENU_TEA = {
    "Trà Sữa Truyền Thống": {
        "price": 30000,
        "category": "Trà Sữa",
        "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?auto=format&fit=crop&w=600&q=80"
    },
    "Trà Sữa Trân Châu Đường Đen": {
        "price": 35000,
        "category": "Trà Sữa",
        "image": "https://images.unsplash.com/photo-1541658016709-82535e94bc69?auto=format&fit=crop&w=600&q=80"
    },
    "Trà Sữa Thái Xanh": {
        "price": 32000,
        "category": "Trà Sữa",
        "image": "https://images.unsplash.com/photo-1627522460108-212628122289?auto=format&fit=crop&w=600&q=80"
    },
    "Trà Sữa Ô Long": {
        "price": 35000,
        "category": "Trà Sữa",
        "image": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=600&q=80"
    },
    "Trà Sữa Matcha": {
        "price": 38000,
        "category": "Trà Sữa",
        "image": "https://images.unsplash.com/photo-1536256263959-770b48d82b0a?auto=format&fit=crop&w=600&q=80"
    },
    "Trà Sữa Dâu Tây": {
        "price": 35000,
        "category": "Trà Trái Cây",
        "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=600&q=80"
    },
    "Trà Đào Cam Sả": {
        "price": 35000,
        "category": "Trà Trái Cây",
        "image": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=600&q=80"
    },
    "Trà Dâu Tằm Mát Lạnh": {
        "price": 32000,
        "category": "Trà Trái Cây",
        "image": "https://images.unsplash.com/photo-1556881286-fc6915169721?auto=format&fit=crop&w=600&q=80"
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

# Khởi tạo Session State
if "cart" not in st.session_state:
    st.session_state.cart = []
if "invoice_paid" not in st.session_state:
    st.session_state.invoice_paid = False
if "order_history" not in st.session_state:
    st.session_state.order_history = []

# ---------------------------------------------------------
# HÀM XUẤT HÓA ĐƠN (.TXT)
# ---------------------------------------------------------
def create_txt_invoice(customer_name, cart, total_amount, discount, final_amount, note):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    content = f"{'='*40}\n"
    content += f"{'HÓA ĐƠN BÁN HÀNG - MR KHẢI LỐC XOÁY':^40}\n"
    content += f"{'='*40}\n"
    content += f"Thời gian: {now}\n"
    content += f"Khách hàng: {customer_name if customer_name else 'Khách vãng lai'}\n"
    if note:
        content += f"Ghi chú: {note}\n"
    content += f"{'-'*40}\n"
    
    for idx, item in enumerate(cart, 1):
        content += f"{idx}. {item['Tên món']} ({item['Size']})\n"
        content += f"   - Đường: {item['Đường']} | Đá: {item['Đá']}\n"
        if item['Topping'] != "Không":
            content += f"   - Topping: {item['Topping']}\n"
        content += f"   SL: {item['Số lượng']} x {item['Đơn giá']:,} = {item['Thành tiền']:,} VNĐ\n"
        
    content += f"{'-'*40}\n"
    content += f"Tổng tiền món: {total_amount:,} VNĐ\n"
    content += f"Giảm giá: {discount}%\n"
    content += f"TỔNG THANH TOÁN: {final_amount:,} VNĐ\n"
    content += f"{'='*40}\n"
    content += f"{'Cảm ơn bạn đã ủng hộ Mr Khải Lốc Xoáy! 💕':^40}\n"
    return content

# ---------------------------------------------------------
# HEADER VÀ NAVIGATION (TABS)
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>🧋 TRÀ SỮA MR KHẢI LỐC XOÁY 🌪️</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>✨ Đậm vị trà - Đậm gu Gen Z ✨</p>", unsafe_allow_html=True)

if os.path.exists("file_00000000d3fc8207810f0b04c88661e1.png"):
    col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
    with col_img2:
        st.image("file_00000000d3fc8207810f0b04c88661e1.png", use_container_width=True)

tab_order, tab_dashboard = st.tabs(["🛍️ Đặt Món & Thanh Toán", "📊 Báo Cáo Doanh Thu (Dành cho chủ quán)"])

# =========================================================
# TAB 1: ĐẶT MÓN & THANH TOÁN
# =========================================================
with tab_order:
    col_left, col_right = st.columns([1.25, 0.75])

    # ------------------- CỘT TRÁI: MENU CHỌN MÓN -------------------
    with col_left:
        st.subheader("📋 Chọn Món Đồ Uống")

        # Bộ lọc & Tìm kiếm
        c_search, c_filter = st.columns([2, 1])
        with c_search:
            search_query = st.text_input("🔍 Tìm tên món:", placeholder="Nhập tên món ví dụ: Matcha, Thái xanh...")
        with c_filter:
            category_filter = st.selectbox("📂 Danh mục:", ["Tất cả", "Trà Sữa", "Trà Trái Cây"])

        # Lọc danh sách món
        filtered_menu = {
            k: v for k, v in MENU_TEA.items()
            if (category_filter == "Tất cả" or v["category"] == category_filter)
            and (search_query.lower() in k.lower())
        }

        if not filtered_menu:
            st.warning("Không tìm thấy món phù hợp với từ khóa tìm kiếm!")
        else:
            selected_tea = st.selectbox("🥤 Chọn món uống yêu thích:", list(filtered_menu.keys()))
            tea_info = MENU_TEA[selected_tea]

            # Hiển thị card thông tin món chọn
            with st.container():
                st.markdown("<div class='card-container'>", unsafe_allow_html=True)
                col_pic, col_opt = st.columns([1, 1.1])
                
                with col_pic:
                    st.image(tea_info["image"], caption=selected_tea, use_container_width=True)
                    
                with col_opt:
                    quantity = st.number_input("🔢 Số lượng ly:", min_value=1, value=1, step=1)
                    selected_size = st.selectbox("📏 Size:", list(SIZE_OPTIONS.keys()))
                    selected_sugar = st.selectbox("🍬 Đường:", SUGAR_LEVELS)
                    selected_ice = st.selectbox("🧊 Đá:", ICE_LEVELS)

                selected_toppings = st.multiselect(
                    "✨ Topping thêm:",
                    options=list(TOPPING_OPTIONS.keys())
                )

                # Tính giá
                base_price = tea_info["price"]
                size_price = SIZE_OPTIONS[selected_size]
                topping_price = sum(TOPPING_OPTIONS[t] for t in selected_toppings)
                unit_price = base_price + size_price + topping_price
                item_total = unit_price * quantity

                st.markdown(f"<div class='price-badge'>💡 Đơn giá: {unit_price:,} VNĐ / ly</div>", unsafe_allow_html=True)
                st.write("")

                if st.button("➕ THÊM VÀO GIỎ HÀNG", type="primary", use_container_width=True):
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
                st.markdown("</div>", unsafe_allow_html=True)

    # ------------------- CỘT PHẢI: GIỎ HÀNG -------------------
    with col_right:
        st.subheader("🛒 Giỏ Hàng Mua Sắm")
        
        customer_name = st.text_input("👤 Tên khách hàng:", placeholder="Tên khách hàng...")
        order_note = st.text_input("📝 Ghi chú đơn hàng (nếu có):", placeholder="Ví dụ: Mang đi, Ít ngọt...")

        if not st.session_state.cart:
            st.info("Giỏ hàng đang trống! Chọn món ngon ở bên trái nhé 👈")
        else:
            df_cart = pd.DataFrame(st.session_state.cart)
            st.dataframe(
                df_cart[["Tên món", "Size", "Topping", "Số lượng", "Thành tiền"]],
                use_container_width=True,
                hide_index=True
            )

            if st.button("🗑️ Xóa toàn bộ giỏ hàng"):
                st.session_state.cart = []
                st.session_state.invoice_paid = False
                st.rerun()

            st.markdown("---")
            total_price = df_cart["Thành tiền"].sum()
            
            discount = st.number_input("🎁 Khuyến mãi (%):", min_value=0, max_value=100, value=0, step=5)
            final_price = int(total_price * (1 - discount / 100))

            st.markdown(f"### Tổng tạm tính: **{total_price:,} VNĐ**")
            if discount > 0:
                st.markdown(f"### 🔥 Sau giảm giá: <span style='color:#FF477E'>{final_price:,} VNĐ</span>", unsafe_allow_html=True)

            if st.button("💳 TẠO ĐƠN & QUÉT MÃ QR", type="primary", use_container_width=True):
                st.session_state.invoice_paid = True
                
                # Lưu vào lịch sử đơn hàng
                st.session_state.order_history.append({
                    "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "customer": customer_name if customer_name else "Khách vãng lai",
                    "total_items": df_cart["Số lượng"].sum(),
                    "final_amount": final_price
                })
                st.balloons()

    # ------------------- KHU VỰC HIỂN THỊ MÃ QR & HÓA ĐƠN -------------------
    if st.session_state.get("invoice_paid") and st.session_state.cart:
        st.markdown("---")
        st.success("🎉 Đã hoàn tất tạo đơn! Vui lòng quét mã QR bên dưới để chuyển khoản:")

        add_info_text = f"TT {customer_name if customer_name else 'Khach'}"
        acc_name_encoded = urllib.parse.quote(ACCOUNT_NAME)
        add_info_encoded = urllib.parse.quote(add_info_text)

        # Mã VietQR chuẩn cho Agribank là VBA
        qr_url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png?amount={final_price}&addInfo={add_info_encoded}&accountName={acc_name_encoded}"

        col_qr1, col_qr2 = st.columns([1, 1.2])
        with col_qr1:
            st.image(qr_url, caption="Mã QR Agribank Tự Động", use_container_width=True)
        with col_qr2:
            st.markdown("### 📲 Thông Tin Chuyển Khoản")
            st.write(f"🏦 **Ngân hàng:** Agribank")
            st.write(f"💳 **Số tài khoản:** `{ACCOUNT_NO}`")
            st.write(f"👤 **Chủ tài khoản:** {ACCOUNT_NAME}")
            st.write(f"💰 **Số tiền thanh toán:** `{final_price:,} VNĐ`")
            st.write(f"📝 **Nội dung chuyển khoản:** `{add_info_text}`")

        invoice_box = st.container(border=True)
        with invoice_box:
            st.markdown("<h2 style='text-align: center; color: #FF477E;'>🧋 HÓA ĐƠN BÁN HÀNG - MR KHẢI LỐC XOÁY</h2>", unsafe_allow_html=True)
            st.write(f"⏰ **Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            st.write(f"👤 **Khách hàng:** {customer_name if customer_name else 'Khách vãng lai'}")
            if order_note:
                st.write(f"📌 **Ghi chú:** {order_note}")
            
            st.table(pd.DataFrame(st.session_state.cart)[["Tên món", "Size", "Đường", "Đá", "Topping", "Số lượng", "Thành tiền"]])
            
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Tổng tiền:** {total_price:,} VNĐ")
                st.write(f"**Giảm giá:** {discount}%")
            with c2:
                st.markdown(f"### TỔNG CỦA BẠN: <span style='color:#FF477E'>{final_price:,} VNĐ</span>", unsafe_allow_html=True)

        txt_data = create_txt_invoice(customer_name, st.session_state.cart, total_price, discount, final_price, order_note)
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 Tải hóa đơn file (.TXT)",
                data=txt_data,
                file_name=f"HoaDon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_dl2:
            if st.button("🔄 Đặt đơn tiếp theo", use_container_width=True):
                st.session_state.cart = []
                st.session_state.invoice_paid = False
                st.rerun()

# =========================================================
# TAB 2: BÁO CÁO DOANH THU & LỊCH SỬ ĐƠN HÀNG
# =========================================================
with tab_dashboard:
    st.subheader("📈 Thống Kê Doanh Thu & Lịch Sử Bán Hàng")

    if not st.session_state.order_history:
        st.info("Chưa có đơn hàng nào được ghi nhận trong phiên làm việc này.")
    else:
        df_history = pd.DataFrame(st.session_state.order_history)
        
        # Thống kê nhanh
        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng số đơn hàng", f"{len(df_history)} đơn")
        m2.metric("Tổng ly đã bán", f"{df_history['total_items'].sum()} ly")
        m3.metric("Tổng doanh thu", f"{df_history['final_amount'].sum():,} VNĐ")

        st.markdown("---")
        st.markdown("#### 📜 Danh Sách Đơn Hàng Vừa Bán")
        st.dataframe(
            df_history.rename(columns={
                "time": "Thời Gian",
                "customer": "Khách Hàng",
                "total_items": "Số Ly",
                "final_amount": "Thành Tiền (VNĐ)"
            }),
            use_container_width=True,
            hide_index=True
                    )
        #--------------- CỘT PHẢI: GIỎ HÀNG -------------------
    with col_right:
        st.subheader("🛒 Giỏ Hàng Mua Sắm")
        
        customer_name = st.text_input("👤 Tên khách hàng:", placeholder="Tên khách hàng...")
        order_note = st.text_input("📝 Ghi chú đơn hàng (nếu có):", placeholder="Ví dụ: Mang đi, Ít ngọt...")

        if not st.session_state.cart:
            st.info("Giỏ hàng đang trống! Chọn món ngon ở bên trái nhé 👈")
        else:
            df_cart = pd.DataFrame(st.session_state.cart)
            st.dataframe(
                df_cart[["Tên món", "Size", "Topping", "Số lượng", "Thành tiền"]],
                use_container_width=True,
                hide_index=True
            )

            if st.button("🗑️ Xóa toàn bộ giỏ hàng"):
                st.session_state.cart = []
                st.session_state.invoice_paid = False
                st.rerun()

            st.markdown("---")
            total_price = df_cart["Thành tiền"].sum()
            
            discount = st.number_input("🎁 Khuyến mãi (%):", min_value=0, max_value=100, value=0, step=5)
            final_price = int(total_price * (1 - discount / 100))

            st.markdown(f"### Tổng tạm tính: **{total_price:,} VNĐ**")
            if discount > 0:
                st.markdown(f"### 🔥 Sau giảm giá: <span style='color:#FF477E'>{final_price:,} VNĐ</span>", unsafe_allow_html=True)

            if st.button("💳 TẠO ĐƠN & QUÉT MÃ QR", type="primary", use_container_width=True):
                st.session_state.invoice_paid = True
                
                # Lưu vào lịch sử đơn hàng
                st.session_state.order_history.append({
                    "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "customer": customer_name if customer_name else "Khách vãng lai",
                    "total_items": df_cart["Số lượng"].sum(),
                    "final_amount": final_price
                })
                st.balloons()

    # ------------------- KHU VỰC HIỂN THỊ MÃ QR & HÓA ĐƠN -------------------
    if st.session_state.get("invoice_paid") and st.session_state.cart:
        st.markdown("---")
        st.success("🎉 Đã hoàn tất tạo đơn! Vui lòng quét mã QR bên dưới để chuyển khoản:")

        add_info_text = f"TT {customer_name if customer_name else 'Khach'}"
        acc_name_encoded = urllib.parse.quote(ACCOUNT_NAME)
        add_info_encoded = urllib.parse.quote(add_info_text)

        # Mã VietQR chuẩn cho Agribank là VBA
        qr_url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png?amount={final_price}&addInfo={add_info_encoded}&accountName={acc_name_encoded}"

        col_qr1, col_qr2 = st.columns([1, 1.2])
        with col_qr1:
            st.image(qr_url, caption="Mã QR Agribank Tự Động", use_container_width=True)
        with col_qr2:
            st.markdown("### 📲 Thông Tin Chuyển Khoản")
            st.write(f"🏦 **Ngân hàng:** Agribank")
            st.write(f"💳 **Số tài khoản:** `{ACCOUNT_NO}`")
            st.write(f"👤 **Chủ tài khoản:** {ACCOUNT_NAME}")
            st.write(f"💰 **Số tiền thanh toán:** `{final_price:,} VNĐ`")
            st.write(f"📝 **Nội dung chuyển khoản:** `{add_info_text}`")

        invoice_box = st.container(border=True)
        with invoice_box:
            st.markdown("<h2 style='text-align: center; color: #FF477E;'>🧋 HÓA ĐƠN BÁN HÀNG - MR KHẢI LỐC XOÁY</h2>", unsafe_allow_html=True)
            st.write(f"⏰ **Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            st.write(f"👤 **Khách hàng:** {customer_name if customer_name else 'Khách vãng lai'}")
            if order_note:
                st.write(f"📌 **Ghi chú:** {order_note}")
            
            st.table(pd.DataFrame(st.session_state.cart)[["Tên món", "Size", "Đường", "Đá", "Topping", "Số lượng", "Thành tiền"]])
            
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Tổng tiền:** {total_price:,} VNĐ")
                st.write(f"**Giảm giá:** {discount}%")
            with c2:
                st.markdown(f"### TỔNG CỦA BẠN: <span style='color:#FF477E'>{final_price:,} VNĐ</span>", unsafe_allow_html=True)

        txt_data = create_txt_invoice(customer_name, st.session_state.cart, total_price, discount, final_price, order_note)
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 Tải hóa đơn file (.TXT)",
                data=txt_data,
                file_name=f"HoaDon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_dl2:
            if st.button("🔄 Đặt đơn tiếp theo", use_container_width=True):
                st.session_state.cart = []
                st.session_state.invoice_paid = False
                st.rerun()

# =========================================================
# TAB 2: BÁO CÁO DOANH THU & LỊCH SỬ ĐƠN HÀNG
# =========================================================
with tab_dashboard:
    st.subheader("📈 Thống Kê Doanh Thu & Lịch Sử Bán Hàng")

    if not st.session_state.order_history:
        st.info("Chưa có đơn hàng nào được ghi nhận trong phiên làm việc này.")
    else:
        df_history = pd.DataFrame(st.session_state.order_history)
        
        # Thống kê nhanh
        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng số đơn hàng", f"{len(df_history)} đơn")
        m2.metric("Tổng ly đã bán", f"{df_history['total_items'].sum()} ly")
        m3.metric("Tổng doanh thu", f"{df_history['final_amount'].sum():,} VNĐ")

        st.markdown("---")
        st.markdown("#### 📜 Danh Sách Đơn Hàng Vừa Bán")
        st.dataframe(
            df_history.rename(columns={
                "time": "Thời Gian",
                "customer": "Khách Hàng",
                "total_items": "Số Ly",
                "final_amount": "Thành Tiền (VNĐ)"
            }),
            use_container_width=True,
            hide_index=True
        )ỘT PHẢI: GIỎ HÀNG -------------------
    with col_right:
        st.subheader("🛒 Giỏ Hàng Mua Sắm")
        
        customer_name = st.text_input("👤 Tên khách hàng:", placeholder="Tên khách hàng...")
        order_note = st.text_input("📝 Ghi chú đơn hàng (nếu có):", placeholder="Ví dụ: Mang đi, Ít ngọt...")

        if not st.session_state.cart:
            st.info("Giỏ hàng đang trống! Chọn món ngon ở bên trái nhé 👈")
        else:
            df_cart = pd.DataFrame(st.session_state.cart)
            st.dataframe(
                df_cart[["Tên món", "Size", "Topping", "Số lượng", "Thành tiền"]],
                use_container_width=True,
                hide_index=True
            )

            if st.button("🗑️ Xóa toàn bộ giỏ hàng"):
                st.session_state.cart = []
                st.session_state.invoice_paid = False
                st.rerun()

            st.markdown("---")
            total_price = df_cart["Thành tiền"].sum()
            
            discount = st.number_input("🎁 Khuyến mãi (%):", min_value=0, max_value=100, value=0, step=5)
            final_price = int(total_price * (1 - discount / 100))

            st.markdown(f"### Tổng tạm tính: **{total_price:,} VNĐ**")
            if discount > 0:
                st.markdown(f"### 🔥 Sau giảm giá: <span style='color:#FF477E'>{final_price:,} VNĐ</span>", unsafe_allow_html=True)

            if st.button("💳 TẠO ĐƠN & QUÉT MÃ QR", type="primary", use_container_width=True):
                st.session_state.invoice_paid = True
                
                # Lưu vào lịch sử đơn hàng
                st.session_state.order_history.append({
                    "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "customer": customer_name if customer_name else "Khách vãng lai",
                    "total_items": df_cart["Số lượng"].sum(),
                    "final_amount": final_price
                })
                st.balloons()

    # ------------------- KHU VỰC HIỂN THỊ MÃ QR & HÓA ĐƠN -------------------
    if st.session_state.get("invoice_paid") and st.session_state.cart:
        st.markdown("---")
        st.success("🎉 Đã hoàn tất tạo đơn! Vui lòng quét mã QR bên dưới để chuyển khoản:")

        add_info_text = f"TT {customer_name if customer_name else 'Khach'}"
        acc_name_encoded = urllib.parse.quote(ACCOUNT_NAME)
        add_info_encoded = urllib.parse.quote(add_info_text)

        # Mã VietQR chuẩn cho Agribank là VBA
        qr_url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png?amount={final_price}&addInfo={add_info_encoded}&accountName={acc_name_encoded}"

        col_qr1, col_qr2 = st.columns([1, 1.2])
        with col_qr1:
            st.image(qr_url, caption="Mã QR Agribank Tự Động", use_container_width=True)
        with col_qr2:
            st.markdown("### 📲 Thông Tin Chuyển Khoản")
            st.write(f"🏦 **Ngân hàng:** Agribank")
            st.write(f"💳 **Số tài khoản:** `{ACCOUNT_NO}`")
            st.write(f"👤 **Chủ tài khoản:** {ACCOUNT_NAME}")
            st.write(f"💰 **Số tiền thanh toán:** `{final_price:,} VNĐ`")
            st.write(f"📝 **Nội dung chuyển khoản:** `{add_info_text}`")

        invoice_box = st.container(border=True)
        with invoice_box:
            st.markdown("<h2 style='text-align: center; color: #FF477E;'>🧋 HÓA ĐƠN BÁN HÀNG - MR KHẢI LỐC XOÁY</h2>", unsafe_allow_html=True)
            st.write(f"⏰ **Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            st.write(f"👤 **Khách hàng:** {customer_name if customer_name else 'Khách vãng lai'}")
            if order_note:
                st.write(f"📌 **Ghi chú:** {order_note}")
            
            st.table(pd.DataFrame(st.session_state.cart)[["Tên món", "Size", "Đường", "Đá", "Topping", "Số lượng", "Thành tiền"]])
            
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Tổng tiền:** {total_price:,} VNĐ")
                st.write(f"**Giảm giá:** {discount}%")
            with c2:
                st.markdown(f"### TỔNG CỦA BẠN: <span style='color:#FF477E'>{final_price:,} VNĐ</span>", unsafe_allow_html=True)

        txt_data = create_txt_invoice(customer_name, st.session_state.cart, total_price, discount, final_price, order_note)
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 Tải hóa đơn file (.TXT)",
                data=txt_data,
                file_name=f"HoaDon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_dl2:
            if st.button("🔄 Đặt đơn tiếp theo", use_container_width=True):
                st.session_state.cart = []
                st.session_state.invoice_paid = False
                st.rerun()

# =========================================================
# TAB 2: BÁO CÁO DOANH THU & LỊCH SỬ ĐƠN HÀNG
# =========================================================
with tab_dashboard:
    st.subheader("📈 Thống Kê Doanh Thu & Lịch Sử Bán Hàng")

    if not st.session_state.order_history:
        st.info("Chưa có đơn hàng nào được ghi nhận trong phiên làm việc này.")
    else:
        df_history = pd.DataFrame(st.session_state.order_history)
        
        # Thống kê nhanh
        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng số đơn hàng", f"{len(df_history)} đơn")
        m2.metric("Tổng ly đã bán", f"{df_history['total_items'].sum()} ly")
        m3.metric("Tổng doanh thu", f"{df_history['final_amount'].sum():,} VNĐ")

        st.markdown("---")
        st.markdown("#### 📜 Danh Sách Đơn Hàng Vừa Bán")
        st.dataframe(
            df_history.rename(columns={
                "time": "Thời Gian",
                "customer": "Khách Hàng",
                "total_items": "Số Ly",
                "final_amount": "Thành Tiền (VNĐ)"
            }),
            use_container_width=True,
            hide_index=True
        )T PHẢI: GIỎ HÀNG -------------------
    with col_right:
        st.subheader("🛒 Giỏ Hàng Mua Sắm")
        
        customer_name = st.text_input("👤 Tên khách hàng:", placeholder="Tên khách hàng...")
        order_note = st.text_input("📝 Ghi chú đơn hàng (nếu có):", placeholder="Ví dụ: Mang đi, Ít ngọt...")

        if not st.session_state.cart:
            st.info("Giỏ hàng đang trống! Chọn món ngon ở bên trái nhé 👈")
        else:
            df_cart = pd.DataFrame(st.session_state.cart)
            st.dataframe(
                df_cart[["Tên món", "Size", "Topping", "Số lượng", "Thành tiền"]],
                use_container_width=True,
                hide_index=True
            )

            if st.button("🗑️ Xóa toàn bộ giỏ hàng"):
                st.session_state.cart = []
                st.session_state.invoice_paid = False
                st.rerun()

            st.markdown("---")
            total_price = df_cart["Thành tiền"].sum()
            
            discount = st.number_input("🎁 Khuyến mãi (%):", min_value=0, max_value=100, value=0, step=5)
            final_price = int(total_price * (1 - discount / 100))

            st.markdown(f"### Tổng tạm tính: **{total_price:,} VNĐ**")
            if discount > 0:
                st.markdown(f"### 🔥 Sau giảm giá: <span style='color:#FF477E'>{final_price:,} VNĐ</span>", unsafe_allow_html=True)

            if st.button("💳 TẠO ĐƠN & QUÉT MÃ QR", type="primary", use_container_width=True):
                st.session_state.invoice_paid = True
                
                # Lưu vào lịch sử đơn hàng
                st.session_state.order_history.append({
                    "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "customer": customer_name if customer_name else "Khách vãng lai",
                    "total_items": df_cart["Số lượng"].sum(),
                    "final_amount": final_price
                })
                st.balloons()

    # ------------------- KHU VỰC HIỂN THỊ MÃ QR & HÓA ĐƠN -------------------
    if st.session_state.get("invoice_paid") and st.session_state.cart:
        st.markdown("---")
        st.success("🎉 Đã hoàn tất tạo đơn! Vui lòng quét mã QR bên dưới để chuyển khoản:")

        add_info_text = f"TT {customer_name if customer_name else 'Khach'}"
        acc_name_encoded = urllib.parse.quote(ACCOUNT_NAME)
        add_info_encoded = urllib.parse.quote(add_info_text)

        # Mã VietQR chuẩn cho Agribank là VBA
        qr_url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png?amount={final_price}&addInfo={add_info_encoded}&accountName={acc_name_encoded}"

        col_qr1, col_qr2 = st.columns([1, 1.2])
        with col_qr1:
            st.image(qr_url, caption="Mã QR Agribank Tự Động", use_container_width=True)
        with col_qr2:
            st.markdown("### 📲 Thông Tin Chuyển Khoản")
            st.write(f"🏦 **Ngân hàng:** Agribank")
            st.write(f"💳 **Số tài khoản:** `{ACCOUNT_NO}`")
            st.write(f"👤 **Chủ tài khoản:** {ACCOUNT_NAME}")
            st.write(f"💰 **Số tiền thanh toán:** `{final_price:,} VNĐ`")
            st.write(f"📝 **Nội dung chuyển khoản:** `{add_info_text}`")

        invoice_box = st.container(border=True)
        with invoice_box:
            st.markdown("<h2 style='text-align: center; color: #FF477E;'>🧋 HÓA ĐƠN BÁN HÀNG - MR KHẢI LỐC XOÁY</h2>", unsafe_allow_html=True)
            st.write(f"⏰ **Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            st.write(f"👤 **Khách hàng:** {customer_name if customer_name else 'Khách vãng lai'}")
            if order_note:
                st.write(f"📌 **Ghi chú:** {order_note}")
            
            st.table(pd.DataFrame(st.session_state.cart)[["Tên món", "Size", "Đường", "Đá", "Topping", "Số lượng", "Thành tiền"]])
            
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Tổng tiền:** {total_price:,} VNĐ")
                st.write(f"**Giảm giá:** {discount}%")
            with c2:
                st.markdown(f"### TỔNG CỦA BẠN: <span style='color:#FF477E'>{final_price:,} VNĐ</span>", unsafe_allow_html=True)

        txt_data = create_txt_invoice(customer_name, st.session_state.cart, total_price, discount, final_price, order_note)
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 Tải hóa đơn file (.TXT)",
                data=txt_data,
                file_name=f"HoaDon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_dl2:
            if st.button("🔄 Đặt đơn tiếp theo", use_container_width=True):
                st.session_state.cart = []
                st.session_state.invoice_paid = False
                st.rerun()

# =========================================================
# TAB 2: BÁO CÁO DOANH THU & LỊCH SỬ ĐƠN HÀNG
# =========================================================
with tab_dashboard:
    st.subheader("📈 Thống Kê Doanh Thu & Lịch Sử Bán Hàng")

    if not st.session_state.order_history:
        st.info("Chưa có đơn hàng nào được ghi nhận trong phiên làm việc này.")
    else:
        df_history = pd.DataFrame(st.session_state.order_history)
        
        # Thống kê nhanh
        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng số đơn hàng", f"{len(df_history)} đơn")
        m2.metric("Tổng ly đã bán", f"{df_history['total_items'].sum()} ly")
        m3.metric("Tổng doanh thu", f"{df_history['final_amount'].sum():,} VNĐ")

        st.markdown("---")
        st.markdown("#### 📜 Danh Sách Đơn Hàng Vừa Bán")
        st.dataframe(
            df_history.rename(columns={
                "time": "Thời Gian",
                "customer": "Khách Hàng",
                "total_items": "Số Ly",
                "final_amount": "Thành Tiền (VNĐ)"
            }),
            use_container_width=True,
            hide_index=True
                ) f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png?amount={final_price}&addInfo={add_info_encoded}&accountName={acc_name_encoded}"

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
