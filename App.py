import inspect
import urllib.parse
from datetime import datetime
import os

import pandas as pd
import streamlit as st

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

d = False
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
                st.session_state.order_history.append({
                    "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "customer": customer_name if customer_name else "Khách vãng lai",
                    "total_items": df_cart["Số lượng"].sum(),
                    "final_amount": final_price
                })
                st.balloons()

    # HIỂN THỊ MÃ QR & HÓA ĐƠN
    if st.session_state.get("invoice_paid") and st.session_state.cart:
        st.markdown("---")
        st.success("🎉 Đã hoàn tất tạo đơn! Vui lòng quét mã QR để chuyển khoản:")

        add_info_text = f"TT {customer_name if customer_name else 'Khach'}"
        acc_name_encoded = urllib.parse.quote(ACCOUNT_NAME)
        add_info_encoded = urllib.parse.quote(add_info_text)

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
        m2.metric("Tổng ly đã bán", f"{df_history['total_items'].sum()} ly")
        m3.metric("Tổng doanh thu", f"{df_history['final_amount'].sum():,} VNĐ")

        st.markdown("---")
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

d = False
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
                st.session_state.order_history.append({
                    "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "customer": customer_name if customer_name else "Khách vãng lai",
                    "total_items": df_cart["Số lượng"].sum(),
                    "final_amount": final_price
                })
                st.balloons()

    # HIỂN THỊ MÃ QR & HÓA ĐƠN
    if st.session_state.get("invoice_paid") and st.session_state.cart:
        st.markdown("---")
        st.success("🎉 Đã hoàn tất tạo đơn! Vui lòng quét mã QR để chuyển khoản:")

        add_info_text = f"TT {customer_name if customer_name else 'Khach'}"
        acc_name_encoded = urllib.parse.quote(ACCOUNT_NAME)
        add_info_encoded = urllib.parse.quote(add_info_text)

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
        m2.metric("Tổng ly đã bán", f"{df_history['total_items'].sum()} ly")
        m3.metric("Tổng doanh thu", f"{df_history['final_amount'].sum():,} VNĐ")

        st.markdown("---")
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
        #--------------CỘT PHẢI: GIỎ HÀNG -------------------
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
        )
        #---------------- CỘT PHẢI: GIỎ HÀNG -------------------
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
        #-------------- CỘT PHẢI: GIỎ HÀNG -------------------
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
