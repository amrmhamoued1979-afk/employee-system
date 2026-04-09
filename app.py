import streamlit as st
import pandas as pd
import sqlite3

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الإدارة الآمن", layout="wide")

# 2. الاتصال بقاعدة البيانات
conn = sqlite3.connect('my_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS emp_table 
             (id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center TEXT, branch TEXT, inspection TEXT, password TEXT, status TEXT)''')
conn.commit()

# --- القائمة الجانبية ---
st.sidebar.title("🔐 بوابة النظام")
choice = st.sidebar.radio("انتقل إلى:", ["الاستعلام العام", "إرسال بيانات موظف", "لوحة تحكم المسؤول فقط"])

# --- القسم الأول: الاستعلام العام (للكل) ---
if choice == "الاستعلام العام":
    st.header("🔍 استعلام جهات الفحص")
    df = pd.read_sql_query("SELECT name, province, inspection FROM emp_table WHERE status='مقبول'", conn)
    if not df.empty:
        st.table(df)
    else:
        st.info("لا توجد بيانات معتمدة حالياً.")

# --- القسم الثاني: إرسال البيانات (الموظف يدخل بياناته لكن لا تعدل فوراً) ---
elif choice == "إرسال بيانات موظف":
    st.header("📝 إدخال بيانات جديدة")
    st.info("ملاحظة: البيانات لن تظهر في النظام إلا بعد مراجعة المسؤول واعتمادها.")
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            e_id = st.text_input("رقم الموظف")
            e_name = st.text_input("الاسم")
            e_phone = st.text_input("التليفون")
        with col2:
            e_prov = st.text_input("المحافظة")
            e_insp = st.text_input("جهة الفحص")
        
        if st.form_submit_button("إرسال للمراجعة"):
            try:
                c.execute("INSERT INTO emp_table VALUES (?,?,?,?,?,?,?,?,?)", 
                          (e_id, e_name, e_phone, e_prov, "", "", e_insp, "", "قيد الانتظار"))
                conn.commit()
                st.success("تم إرسال بياناتك بنجاح، بانتظار اعتماد المسؤول.")
            except:
                st.error("هذا الرقم مسجل مسبقاً، يرجى مراجعة الإدارة للتعديل.")

# --- القسم الثالث: لوحة تحكم المسؤول (أنت فقط) ---
elif choice == "لوحة تحكم المسؤول فقط":
    st.header("🛠 لوحة الإدارة والتحكم")
    password = st.sidebar.text_input("أدخل كلمة سر الإدارة", type="password")
    
    # ضع كلمة سرك الخاصة هنا (بدلاً من 1234)
    if password == "admin79": 
        st.write("### إدارة الطلبات والموافقة")
        pending = pd.read_sql_query("SELECT * FROM emp_table WHERE status='قيد الانتظار'", conn)
        
        if not pending.empty:
            st.dataframe(pending)
            user_to_mod = st.selectbox("اختر رقم الموظف لاعتماده أو تعديله:", pending['id'])
            
            if st.button("✅ اعتماد البيانات وظهورها للجميع"):
                c.execute("UPDATE emp_table SET status='مقبول' WHERE id=?", (user_to_mod,))
                conn.commit()
                st.success(f"تم اعتماد بيانات الموظف {user_to_mod}")
                st.rerun()
                
            if st.button("❌ حذف الطلب"):
                c.execute("DELETE FROM emp_table WHERE id=?", (user_to_mod,))
                conn.commit()
                st.warning("تم حذف الطلب.")
                st.rerun()
        else:
            st.info("لا توجد طلبات جديدة للمراجعة.")
    else:
        st.error("هذا القسم محمي، يرجى إدخال كلمة السر الصحيحة في القائمة الجانبية.")
