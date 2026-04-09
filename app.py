import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="نظام الموظفين", layout="wide")

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('my_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS emp_table 
             (id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center TEXT, branch TEXT, inspection TEXT, password TEXT)''')
conn.commit()

# --- القائمة الجانبية ---
st.sidebar.title("القائمة الرئيسية")
mode = st.sidebar.radio("اختر الإجراء:", ["دخول الموظف (تعديل)", "تسجيل موظف جديد (للمسؤول)", "استعلام عام (جهات الفحص)"])

if mode == "تسجيل موظف جديد (للمسؤول)":
    st.header("📝 إضافة موظف جديد للقاعدة")
    with st.form("reg_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("رقم الموظف (كود الدخول)")
            new_name = st.text_input("الاسم الكامل")
            new_phone = st.text_input("رقم التليفون")
            new_pw = st.text_input("كلمة السر", type="password")
        with col2:
            new_prov = st.text_input("المحافظة")
            new_center = st.text_input("الإدارة المركزية")
            new_branch = st.selectbox("الفرع", ["الأول", "الثاني"])
            new_insp = st.text_input("جهة الفحص")
        
        if st.form_submit_button("حفظ الموظف"):
            try:
                c.execute("INSERT INTO emp_table VALUES (?,?,?,?,?,?,?,?)", 
                          (new_id, new_name, new_phone, new_prov, new_center, new_branch, new_insp, new_pw))
                conn.commit()
                st.success("تم تسجيل الموظف بنجاح! يمكنه الدخول الآن.")
            except:
                st.error("رقم الموظف موجود مسبقاً!")

elif mode == "دخول الموظف (تعديل)":
    st.header("🔑 تسجيل دخول الموظف")
    user_id = st.text_input("أدخل رقم الموظف")
    user_pw = st.text_input("أدخل الرقم السري", type="password")
    
    if st.button("دخول"):
        res = c.execute("SELECT * FROM emp_table WHERE id=? AND password=?", (user_id, user_pw)).fetchone()
        if res:
            st.session_state['logged_in'] = res
            st.success(f"مرحباً بك: {res[1]}")
        else:
            st.error("بيانات الدخول غير صحيحة.")
            
    if 'logged_in' in st.session_state:
        res = st.session_state['logged_in']
        with st.form("edit_form"):
            st.info("يمكنك تعديل بياناتك أدناه:")
            u_phone = st.text_input("التليفون", value=res[2])
            u_insp = st.text_input("جهة الفحص", value=res[6])
            if st.form_submit_button("تحديث بياناتي"):
                c.execute("UPDATE emp_table SET phone=?, inspection=? WHERE id=?", (u_phone, u_insp, res[0]))
                conn.commit()
                st.success("تم التحديث! يرجى إعادة الدخول لرؤية التغييرات.")

elif mode == "استعلام عام (جهات الفحص)":
    st.header("🔍 استعلام عام عن جهات الفحص")
    df = pd.read_sql_query("SELECT name as 'الاسم', province as 'المحافظة', inspection as 'جهة الفحص' FROM emp_table", conn)
    st.dataframe(df, use_container_width=True)
