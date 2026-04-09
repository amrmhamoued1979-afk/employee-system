import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعدادات الصفحة وإخفاء القوائم العلوية ---
st.set_page_config(page_title="الصحبة الطيبة - نظام البيانات", layout="wide")

hide_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stAppDeployButton {display:none;}
            [data-testid="stHeader"] {display:none;}
            /* إخفاء القائمة الجانبية تماماً */
            [data-testid="stSidebar"] {display: none;}
            </style>
            """
st.markdown(hide_style, unsafe_allow_html=True)

# --- 2. الواجهة العلوية (علم مصر واسم الصحبة الطيبة) ---
st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-top: 5px solid #ce1126; border-bottom: 5px solid #000; text-align: center;">
        <h1 style="color: #000; margin: 0;">🇪🇬 الصحبة الطيبة 🇪🇬</h1>
        <p style="color: #666; font-size: 16px; margin: 5px 0;">نظام إدارة البيانات والاستعلام العام</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect('sohba_final_v9.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS employees 
             (emp_id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center_dept TEXT, branch TEXT, inspection TEXT, password TEXT)''')
conn.commit()

# --- 4. خيارات التنقل في منتصف الصفحة (بدلاً من الجانب) ---
st.write("### اختر الإجراء المطلوب:")
# جعل الاختيارات تظهر بشكل عرضي جميل
choice = st.selectbox("", ["تسجيل بياناتي (لأول مرة)", "الاستعلام العام", "تعديل بياناتي (دخول العضو)"])

st.divider()

# --- 5. تنفيذ الأقسام ---

if choice == "تسجيل بياناتي (لأول مرة)":
    st.markdown("<h3 style='text-align: center;'>📝 تسجيل بيانات عضو جديد</h3>", unsafe_allow_html=True)
    with st.form("reg_form"):
        c1, c2 = st.columns(2)
        with c1:
            r_id = st.text_input("رقم العضو / الكود")
            r_name = st.text_input("الاسم بالكامل")
            r_phone = st.text_input("رقم التليفون")
            r_pw = st.text_input("اختر كلمة سر خاصة بك", type="password")
        with c2:
            r_prov = st.text_input("المحافظة")
            r_dept = st.text_input("الإدارة المركزية")
            r_branch = st.selectbox("الفرع", ["الأول", "الثاني"])
            r_insp = st.text_input("جهة الفحص")
        
        if st.form_submit_button("إرسال وحفظ البيانات"):
            if all([r_id, r_name, r_phone, r_pw, r_prov, r_dept, r_insp]):
                try:
                    c.execute("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", (r_id, r_name, r_phone, r_prov, r_dept, r_branch, r_insp, r_pw))
                    conn.commit()
                    st.success("✅ تم الحفظ بنجاح في نظام الصحبة الطيبة!")
                except: st.error("⚠️ هذا الرقم مسجل مسبقاً.")
            else: st.error("🛑 يجب ملء كافة الخانات.")

elif choice == "الاستعلام العام":
    st.header("🔍 استعلام جهات الفحص")
    df = pd.read_sql_query("SELECT name as 'الاسم', phone as 'رقم التليفون', province as 'المحافظة', inspection as 'جهة الفحص' FROM employees", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else: st.info("لا توجد بيانات مسجلة حالياً.")

elif choice == "تعديل بياناتي (دخول العضو)":
    st.header("🔑 دخول العضو للتعديل")
    l_id = st.text_input("رقم العضو")
    l_pw = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        user = c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?", (l_id, l_pw)).fetchone()
        if user:
            st.session_state['active_id'] = l_id
            st.success("تم الدخول بنجاح")
        else: st.error("بيانات الدخول خاطئة")
    
    if 'active_id' in st.session_state:
        curr_id = st.session_state['active_id']
        data = c.execute("SELECT * FROM employees WHERE emp_id=?", (curr_id,)).fetchone()
        with st.form("edit_form"):
            u_phone = st.text_input("رقم التليفون", value=data[2])
            u_insp = st.text_input("جهة الفحص", value=data[6])
            if st.form_submit_button("حفظ التعديلات"):
                c.execute("UPDATE employees SET phone=?, inspection=? WHERE emp_id=?", (u_phone, u_insp, curr_id))
                conn.commit()
                st.success("تم التحديث!")

# --- 6. بوابة الإدارة (في أسفل الصفحة تماماً) ---
st.divider()
st.write("---")
with st.expander("🛠 بوابة الإدارة والتحكم (للمسؤول فقط)"):
    admin_pw = st.text_input("كلمة سر المسؤول", type="password")
    if admin_pw == "admin79":
        all_df = pd.read_sql_query("SELECT * FROM employees", conn)
        st.dataframe(all_df)
        del_id = st.text_input("رقم العضو للحذف")
        if st.button("حذف السجل نهائياً"):
            c.execute("DELETE FROM employees WHERE emp_id=?", (del_id,))
            conn.commit()
            st.rerun()
