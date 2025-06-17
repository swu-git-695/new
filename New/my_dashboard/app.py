import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import re
import datetime

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
    return re.match(r"[^@]+@[^@]+\\.[^@]+", email)

# ==== ตั้งค่าเริ่มต้น session_state ====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "username" not in st.session_state:
    st.session_state.username = None

# ==== CSS Styling ใหม่ ====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@400;600&display=swap');
body, .main {
    font-family: 'Kanit', sans-serif;
    background: linear-gradient(to right, #e3f2fd, #ffffff);
    color: #2b2d42;
}
.main > div {
    background-color: white;
    border-radius: 16px;
    padding: 2rem 3rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    margin-top: 30px;
}
h1, h2, h3, .stSubheader {
    color: #003366;
    font-weight: 600;
    margin-bottom: 1rem;
    text-align: center;
}
.stButton > button {
    background: linear-gradient(to right, #2196f3, #1e88e5);
    color: white;
    border-radius: 30px;
    padding: 0.6rem 1.5rem;
    font-weight: bold;
    border: none;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background: #1565c0;
    transform: scale(1.03);
}
.logout-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: #e53935;
    color: #fff;
    padding: 0.6rem 1.5rem;
    font-weight: bold;
    border: none;
    border-radius: 30px;
    font-size: 1rem;
    z-index: 999;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    transition: background-color 0.3s ease;
}
.logout-btn:hover {
    background-color: #c62828;
}
.card {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ==== หน้า LOGIN / SIGNUP ====
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.page == "login":
            st.markdown("<h2 style='text-align:center; color:#4a90e2;'>🔐 เข้าสู่ระบบ</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#555;'>กรุณากรอกชื่อผู้ใช้หรืออีเมล และรหัสผ่านเพื่อเข้าสู่ระบบ</p>", unsafe_allow_html=True)
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
                    st.rerun()
                else:
                    st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            st.markdown("---")
            st.markdown("ยังไม่มีบัญชีใช่ไหม?")
            if st.button("📌 สมัครสมาชิก"):
                st.session_state.page = "signup"
                st.rerun()

        elif st.session_state.page == "signup":
            st.markdown("<h2 style='text-align:center; color:#4a90e2;'>📝 สมัครสมาชิกใหม่</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#555;'>กรอกข้อมูลด้านล่างเพื่อสร้างบัญชีใหม่</p>", unsafe_allow_html=True)
            with st.form("signup_form"):
                new_user = st.text_input("👤 ชื่อผู้ใช้", placeholder="ชื่อผู้ใช้ที่ต้องการ")
                new_email = st.text_input("📧 อีเมล", placeholder="ตัวอย่าง: example@mail.com")
                new_pass = st.text_input("🔒 รหัสผ่าน", type="password", placeholder="ตั้งรหัสผ่านของคุณ")
                submitted = st.form_submit_button("สร้างบัญชี")
            if submitted:
                if not new_user or not new_email or not new_pass:
                    st.error("❗ กรุณากรอกข้อมูลให้ครบถ้วน")
                elif not is_valid_email(new_email):
                    st.error("📧 อีเมลไม่ถูกต้อง กรุณากรอกใหม่")
                elif signup(new_user.strip(), new_email.strip(), new_pass.strip()):
                    st.success("✅ สมัครสมาชิกเรียบร้อย! กรุณาเข้าสู่ระบบ")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error("ชื่อผู้ใช้นี้มีอยู่แล้ว กรุณาใช้ชื่ออื่น")
            if st.button("← กลับไปหน้าเข้าสู่ระบบ"):
                st.session_state.page = "login"
                st.rerun()
    st.stop()

# ==== DASHBOARD ====

# ปุ่มออกจากระบบแบบสวยๆ มุมขวาบน แบบ fixed
if st.button("🚪 ออกจากระบบ", key="logout", help="ออกจากระบบ", on_click=lambda: (setattr(st.session_state, "logged_in", False), setattr(st.session_state, "username", None), st.rerun()), args=None):
    pass

# เนื่องจาก Streamlit ไม่มีวิธีง่ายๆ ทำ fixed button ผมจะใช้ st.markdown กับ html+css เพื่อปุ่มออกจากระบบแบบ fixed
st.markdown("""
    <button class="logout-btn" onclick="document.querySelector('button[kind=logout]').click();">
        🚪 ออกจากระบบ
    </button>
    <script>
    // ซ่อนปุ่ม logout แบบปกติ (ในกรณีแสดงซ้ำ)
    const btns = window.parent.document.querySelectorAll('button[kind=logout]');
    btns.forEach(b=>b.style.display='none');
    </script>
""", unsafe_allow_html=True)

st.markdown(f"""
<h1 style='text-align:center; color:#003366;'>📊 ระบบจัดการและวิเคราะห์ข้อมูล</h1>
<p style='text-align:center; font-size: 1.1rem;'>ยินดีต้อนรับคุณ <strong>{st.session_state.username}</strong> สู่ระบบของโรงพยาบาลเจ้าพระยาอภัยภูเบศร</p>
""", unsafe_allow_html=True)

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
        st.markdown("**ชื่อคอลัมน์ในไฟล์ Excel:** " + ", ".join(df.columns.tolist()))
        
        # แจ้งเตือนเมื่ออัปโหลดเสร็จ
        st.success(f"✅ อัปโหลดไฟล์ '{uploaded_file.name}' เสร็จเรียบร้อยแล้ว")

        current_user = st.session_state.get("username", None)
        if current_user:
            add_upload_log(current_user, uploaded_file.name)

        # ... (ส่วนที่เหลือของโค้ดเดิม)
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        non_numeric_cols = df.select_dtypes(exclude='number').columns.tolist()

        if numeric_cols and non_numeric_cols:
            x_col = non_numeric_cols[0]
            y_col = numeric_cols[0]

            filtered_df = df[df[x_col].notnull()]

            if not filtered_df.empty:
                fig_bar = px.bar(
                    filtered_df,
                    x=x_col,
                    y=y_col,
                    title=f'กราฟ {y_col} ตาม {x_col}',
                    text=y_col,
                    color=x_col,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_bar.update_traces(textposition='outside')
                fig_bar.update_layout(
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    uniformtext_minsize=8,
                    uniformtext_mode='hide',
                    xaxis_tickangle=-45,
                    plot_bgcolor='white',
                    margin=dict(t=50, b=150)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                fig_pie = px.pie(
                    filtered_df,
                    names=x_col,
                    values=y_col,
                    title=f'กราฟวงกลม {y_col} ตาม {x_col}'
                )
                fig_pie.update_traces(textinfo='value+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning("⚠️ ไม่มีข้อมูลที่เหมาะสมสำหรับกราฟหลังกรองค่า null")
        else:
            st.info("ℹ️ ไฟล์นี้ไม่มีข้อมูลที่เหมาะสำหรับการสร้างกราฟ (ต้องมีทั้งคอลัมน์ตัวเลขและไม่ใช่ตัวเลข)")

        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")

current_user = st.session_state.get("username", None)
if current_user:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 📜 ประวัติการอัปโหลดรายงาน")
    st.markdown(f"<p style='font-size: 1.05rem;'>🔎 ค้นหารายงานของคุณ <b>{current_user}</b> ด้วยชื่อไฟล์หรือวันที่อัปโหลด (รูปแบบ: <code>2025-06-13</code>)</p>", unsafe_allow_html=True)

    with st.form("search_form", clear_on_submit=False):
        search_col1, search_col2 = st.columns([4, 1])
        with search_col1:
            search = st.text_input("ค้นหาชื่อไฟล์หรือวันที่", placeholder="เช่น report.xlsx หรือ 2025-06-13")
        with search_col2:
            submitted = st.form_submit_button("🔍 ค้นหา")

    log = load_upload_log()
    user_logs = log.get(current_user, [])

    if submitted:
        search = search.strip()
        if search:
            filtered_logs = [entry for entry in user_logs
                             if search.lower() in entry['filename'].lower() or search in entry['upload_time']]
            if filtered_logs:
                st.success(f"✅ พบ {len(filtered_logs)} รายการที่ตรงกับ \"{search}\"")
                df_filtered = pd.DataFrame(filtered_logs)
                df_filtered.index += 1
                df_filtered.rename_axis("ลำดับ", inplace=True)
                df_filtered.rename(columns={"filename": "📁 ชื่อไฟล์", "upload_time": "⏰ เวลาที่อัปโหลด"}, inplace=True)
                st.table(df_filtered)
            else:
                st.warning("❌ ไม่พบรายการที่ตรงกับคำค้นหา กรุณาลองใหม่อีกครั้ง")
        else:
            st.info("ℹ️ กรุณากรอกคำค้นหาเพื่อแสดงผล")
    else:
        st.markdown("<p style='color:gray; font-size: 0.95rem;'>ยังไม่ได้ค้นหา กรุณากรอกคำค้นหาแล้วกด 'ค้นหา'</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
