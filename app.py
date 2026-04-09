import streamlit as st
import pandas as pd
import sqlite3

# إعدادات واجهة الموقع
st.set_page_config(page_title="نظام الموظفين", layout="wide")

# إنشاء قاعدة بيانات بسيطة (SQLite)
conn = sqlite3.connect('my_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS emp_table 
             (id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center TEXT, branch TEXT, inspection TEXT, password TEXT)''')
conn.commit()

# --- واجهة المستخدم ---
st.sidebar.title("القائمة")
mode = st.sidebar.radio("اختر الإجراء:", ["دخول الموظف (تعديل)", "استعلام عام (جهات الفحص)"])

if mode == "دخول الموظف (تعديل)":
    st.header("🔑 تسجيل دخول الموظف")
    user_id = st.text_input("أدخل رقم الموظف")
    user_pw = st.text_input("أدخل الرقم السري", type="password")
    
    if st.button("دخول"):
        # التحقق من البيانات (للتجربة سنضيف سطر افتراضي إذا كانت القاعدة فارغة)
        res = c.execute("SELECT * FROM emp_table WHERE id=? AND password=?", (user_id, user_pw)).fetchone()
        
        if res:
            st.success(f"مرحباً بك: {res[1]}")
            with st.form("edit_form"):
                new_phone = st.text_input("تعديل التليفون", value=res[2])
                new_insp = st.text_input("تعديل جهة الفحص", value=res[6])
                if st.form_submit_button("حفظ التعديلات"):
                    c.execute("UPDATE emp_table SET phone=?, inspection=? WHERE id=?", (new_phone, new_insp, user_id))
                    conn.commit()
                    st.success("تم تحديث بياناتك بنجاح!")
        else:
            st.error("خطأ في رقم الموظف أو كلمة السر.")

elif mode == "استعلام عام (جهات الفحص)":
    st.header("🔍 استعلام عام عن جهات الفحص")
    df = pd.read_sql_query("SELECT name as 'الاسم', inspection as 'جهة الفحص' FROM emp_table", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة حالياً.")
