import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import re
import datetime

from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.scriptrunner import get_script_run_ctx
def rerun():
    raise RerunException(get_script_run_ctx())

# ==== ฟังก์ชันจัดการไฟล์ users.json ====
USER_FILE = "users.json"
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

# ==== ฟังก์ชันจัดการ log อัปโหลด ====
LOG_FILE = "upload_log.json"
def load_upload_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump({}, f)
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_upload_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def add_upload_log(username, filename):
    log = load_upload_log()
    entry = {
        "filename": filename,
        "upload_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if username not in log:
        log[username] = []
    log[username].append(entry)
    save_upload_log(log)

# ==== ตรวจสอบรหัสผ่าน (คืน username) ====
def check_login(identifier, password):
    users = load_users()
    for username, info in users.items():
        if isinstance(info, dict):
            if identifier == username or identifier == info.get("email"):
                if info.get("password") == password:
                    return username
        else:
            if identifier == username and info == password:
                return username
    return None

# ==== สมัครสมาชิก ====
def signup(username, email, password):
    users = load_users()
    if username in users:
        return False
    users[username] = {"email": email, "password": password}
    save_users(users)
    return True

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# ==== ตั้งค่าเริ่มต้น session_state ====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "username" not in st.session_state:
    st.session_state.username = None

# ==== CSS ไฮโซทางการ ====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600&display=swap');
body, .main {
    font-family: 'Sarabun', sans-serif;
    background: #f8f9fa;
    color: #1c1c1c;
}
.main > div {
    background-color: #fff;
    border-radius: 12px;
    padding: 2rem 3rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    margin-top: 30px;
}
h1, h2, h3, .stSubheader {
    color: #002147;
    font-weight: 600;
    margin-bottom: 1rem;
    text-align: center;
}
.stButton > button {
    background-color: #004080;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1.25rem;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background-color: #002f5f;
    transform: scale(1.02);
}
.logout-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: #dc3545;
    color: #fff;
    padding: 0.5rem 1.25rem;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    font-size: 0.95rem;
    z-index: 999;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    transition: background-color 0.3s ease;
}
.logout-btn:hover {
    background-color: #b02a37;
}
.card {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ==== หน้า LOGIN / SIGNUP ====
if not st.session_state.logged_in:
    # แสดงโลโก้ + ชื่อระบบเฉพาะหน้า login/signup เท่านั้น
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; background-color: #ffffff; padding: 1rem 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);'>
        <img src='https://www.cpa.go.th/cpawebsite/uploads/ABH-LOGO-GEEEN.png' style='height: 70px;'>
        <div>
            <h1 style='margin: 0; color: #002147; font-size: 1.8rem;'>ระบบจัดการรายงานข้อมูล</h1>
            <p style='margin: 0; color: #666;'>โรงพยาบาลเจ้าพระยาอภัยภูเบศร</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.page == "login":
            st.markdown("<h2 style='text-align:center; color:#4a90e2;'>🔐 เข้าสู่ระบบ</h2>", unsafe_allow_html=True)
            with st.form("login_form"):
                identifier = st.text_input("👤 ชื่อผู้ใช้หรืออีเมล", placeholder="ชื่อผู้ใช้ หรือ อีเมล")
                password = st.text_input("🔒 รหัสผ่าน", type="password", placeholder="รหัสผ่านของคุณ")
                submitted = st.form_submit_button("เข้าสู่ระบบ")
            if submitted:
                user = check_login(identifier.strip(), password.strip())
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.success("✅ เข้าสู่ระบบสำเร็จ")
                    rerun()
                else:
                    st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            if st.button("📌 สมัครสมาชิก"):
                st.session_state.page = "signup"
                rerun()

        elif st.session_state.page == "signup":
            st.markdown("<h2 style='text-align:center; color:#4a90e2;'>📝 สมัครสมาชิกใหม่</h2>", unsafe_allow_html=True)
            with st.form("signup_form"):
                new_user = st.text_input("👤 ชื่อผู้ใช้", placeholder="ชื่อผู้ใช้ที่ต้องการ")
                new_email = st.text_input("📧 อีเมล", placeholder="example@mail.com")
                new_pass = st.text_input("🔒 รหัสผ่าน", type="password", placeholder="รหัสผ่าน")
                submitted = st.form_submit_button("สร้างบัญชี")
            if submitted:
                if not new_user or not new_email or not new_pass:
                    st.error("❗ กรุณากรอกข้อมูลให้ครบถ้วน")
                elif not is_valid_email(new_email):
                    st.error("📧 อีเมลไม่ถูกต้อง")
                elif signup(new_user.strip(), new_email.strip(), new_pass.strip()):
                    st.success("✅ สมัครสำเร็จ! กรุณาเข้าสู่ระบบ")
                    st.session_state.page = "login"
                    st.experimental_rerun()
                else:
                    st.error("ชื่อผู้ใช้นี้มีอยู่แล้ว")
            if st.button("← กลับเข้าสู่ระบบ"):
                st.session_state.page = "login"
                rerun()
    st.stop()

# ==== ส่วนของหน้าเว็บหลัง login ==== 

# Sidebar โลโก้และเมนู (ไม่แสดงชื่อระบบซ้ำในนี้)
st.sidebar.markdown("""
<div style='text-align:center; margin-bottom: 1.5rem;'>
    <img src='https://www.cpa.go.th/cpawebsite/uploads/ABH-LOGO-GEEEN.png' width='100' style='margin-bottom: 10px;'/>
</div>
<hr>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("📌 เลือกเมนู", ["หน้าแรก", "อัปโหลดและกราฟ", "ประวัติการอัปโหลด"])

st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 ผู้ใช้: **{st.session_state.username}**")
if st.sidebar.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False
    st.session_state.username = None
    rerun()

if menu == "หน้าแรก":
    st.markdown(f"""
    <h1 style='text-align:center; color:#003366;'>📊 ระบบจัดการและวิเคราะห์ข้อมูล</h1>
    <p style='text-align:center; font-size: 1.1rem;'>ยินดีต้อนรับคุณ <strong>{st.session_state.username}</strong> สู่ระบบของโรงพยาบาลเจ้าพระยาอภัยภูเบศร</p>
    """, unsafe_allow_html=True)
    st.markdown("<div class='card'>เลือกเมนูจากด้านซ้ายเพื่อดำเนินการ เช่น อัปโหลดไฟล์ หรือดูประวัติการใช้งาน</div>", unsafe_allow_html=True)

elif menu == "อัปโหลดและกราฟ":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📂 อัปโหลดรายงานประจำวัน (Excel)")
    uploaded_file = st.file_uploader("", type=["xlsx"])
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("🧾 ข้อมูลในไฟล์ Excel")
            st.dataframe(df, use_container_width=True)
            st.success(f"✅ อัปโหลดไฟล์ '{uploaded_file.name}' เสร็จเรียบร้อยแล้ว")
            current_user = st.session_state.get("username", None)
            if current_user:
                add_upload_log(current_user, uploaded_file.name)

            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            non_numeric_cols = df.select_dtypes(exclude='number').columns.tolist()

            if numeric_cols and non_numeric_cols:
                x_col = non_numeric_cols[0]
                y_col = numeric_cols[0]
                filtered_df = df[df[x_col].notnull()]
                if not filtered_df.empty:
                    fig_bar = px.bar(filtered_df, x=x_col, y=y_col, title=f'{y_col} ตาม {x_col}', text=y_col, color=x_col)
                    fig_bar.update_traces(textposition='outside')
                    st.plotly_chart(fig_bar, use_container_width=True)

                    fig_pie = px.pie(filtered_df, names=x_col, values=y_col, title=f'กราฟวงกลม {y_col} ตาม {x_col}')
                    fig_pie.update_traces(textinfo='value+label')
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.warning("⚠️ ไม่มีข้อมูลเหมาะสมหลังกรอง null")
            else:
                st.info("ℹ️ ต้องมีทั้งคอลัมน์ตัวเลขและตัวหนังสือเพื่อสร้างกราฟ")
            st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

elif menu == "ประวัติการอัปโหลด":
    current_user = st.session_state.get("username", None)
    if current_user:
        log = load_upload_log()
        user_logs = log.get(current_user, [])

        st.markdown("""
        <div class='card'>
            <h2 style='text-align:center; color:#003366;'>📜 ประวัติการอัปโหลดรายงาน</h2>
            <p style='text-align:center; font-size: 1.05rem;'>ดูรายการไฟล์ที่คุณเคยอัปโหลด พร้อมวันเวลาย้อนหลัง</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("search_form"):
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🔎 ค้นหารายการอัปโหลด")
            search = st.text_input("พิมพ์ชื่อไฟล์หรือวันที่ (YYYY-MM-DD)", placeholder="เช่น report.xlsx หรือ 2025-06-13")
            submitted = st.form_submit_button("ค้นหา")
            st.markdown("</div>", unsafe_allow_html=True)

        # ฟังก์ชันกรอง
        def filter_logs(logs, keyword):
            return [entry for entry in logs if keyword.lower() in entry['filename'].lower() or keyword in entry['upload_time']]

        # ผลลัพธ์
        results = filter_logs(user_logs, search.strip()) if submitted else user_logs

        if results:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#1e88e5;'>✅ พบ {len(results)} รายการ {'ที่ตรงกับคำค้นหา' if submitted else 'ทั้งหมด'}</h4>", unsafe_allow_html=True)
            df = pd.DataFrame(results)
            df.index += 1
            df.rename_axis("ลำดับ", inplace=True)
            df.rename(columns={
                "filename": "📁 ชื่อไฟล์",
                "upload_time": "⏰ เวลาที่อัปโหลด"
            }, inplace=True)
            st.dataframe(df, use_container_width=True)

            # สรุปไฟล์ล่าสุด
            last_upload = results[-1]
            st.markdown(f"<p style='color:#4caf50;'>📌 ไฟล์ล่าสุด: <strong>{last_upload['filename']}</strong> เมื่อ <strong>{last_upload['upload_time']}</strong></p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # ปุ่มดาวน์โหลด CSV
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 ดาวน์โหลดเป็นไฟล์ CSV",
                data=csv,
                file_name="upload_history.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.warning("🔍 ไม่พบรายการที่ตรงกับคำค้นหา")
            st.markdown("</div>")
