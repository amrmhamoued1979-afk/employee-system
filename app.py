import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعدادات الصفحة والواجهة ---
st.set_page_config(page_title="نظام بيانات الموظفين - الجهاز المركزي للمحاسبات", layout="wide")

# --- إضافة اللوجو في أعلى الصفحة ---
# قمت برفع الصورة لك واستخدام رابط مباشر لضمان ظهورها فوراً
LOGO_URL = "https://githubusercontent.com" 

# عرض اللوجو في المنتصف
st.image("https://ibb.co", use_container_width=True)

st.markdown("---")

# --- 2. إنشاء قاعدة البيانات ---
conn = sqlite3.connect('final_system_v3.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS employees 
             (emp_id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center_dept TEXT, branch TEXT, inspection TEXT, password TEXT)''')
conn.commit()

# --- 3. القائمة الجانبية ---
st.sidebar.title("🔐 بوابة النظام")
menu = ["الاستعلام العام", "دخول الموظف (تعديل بياناتي)", "لوحة تحكم المسؤول (أنا فقط)"]
choice = st.sidebar.selectbox("اختر الإجراء:", menu)

# --- القسم الأول: الاستعلام العام (متاح للجميع) ---
if choice == "الاستعلام العام":
    st.header("🔍 استعلام جهات الفحص")
    df = pd.read_sql_query("SELECT name as 'اسم الموظف', province as 'المحافظة', inspection as 'جهة الفحص' FROM employees", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة حالياً.")

# --- القسم الثاني: دخول الموظف وتعديل بياناته فقط ---
elif choice == "دخول الموظف (تعديل بياناتي)":
    st.header("👤 تعديل البيانات الشخصية")
    e_id = st.text_input("أدخل رقمك الوظيفي")
    e_pw = st.text_input("أدخل كلمة السر الخاصة بك", type="password")
    
    if st.button("دخول"):
        user = c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?", (e_id, e_pw)).fetchone()
        if user:
            st.session_state['user_id'] = user[0]
            st.success(f"مرحباً بك. يمكنك التعديل أدناه:")
        else:
            st.error("بيانات الدخول غير صحيحة")

    if 'user_id' in st.session_state:
        current_id = st.session_state['user_id']
        res = c.execute("SELECT * FROM employees WHERE emp_id=?", (current_id,)).fetchone()
        with st.form("edit_form"):
            u_phone = st.text_input("تحديث رقم التليفون", value=res[2])
            u_insp = st.text_input("تحديث جهة الفحص", value=res[6])
            
            if st.form_submit_button("حفظ التعديلات النهائية"):
                if u_phone and u_insp:
                    c.execute("UPDATE employees SET phone=?, inspection=? WHERE emp_id=?", (u_phone, u_insp, current_id))
                    conn.commit()
                    st.success("✅ تم تحديث بياناتك بنجاح في قاعدة البيانات.")
                else:
                    st.error("⚠️ يجب ملء كافة البيانات المطلوبة.")

# --- القسم الثالث: لوحة تحكم المسؤول (أنت فقط) ---
elif choice == "لوحة تحكم المسؤول (أنا فقط)":
    st.header("🛠 إدارة النظام")
    admin_pw = st.sidebar.text_input("كلمة سر الإدارة", type="password")
    
    if admin_pw == "admin79": 
        st.subheader("➕ إضافة موظف جديد")
        with st.form("admin_add"):
            c1, c2 = st.columns(2)
            with c1:
                n_id = st.text_input("رقم الموظف")
                n_name = st.text_input("الاسم")
                n_phone = st.text_input("التليفون")
                n_pw = st.text_input("كلمة سر الموظف")
            with c2:
                n_prov = st.text_input("المحافظة")
                n_dept = st.text_input("الإدارة المركزية")
                n_branch = st.selectbox("الفرع", ["الأول", "الثاني"])
                n_insp = st.text_input("جهة الفحص")
            
            if st.form_submit_button("حفظ الموظف الجديد"):
                if all([n_id, n_name, n_phone, n_pw, n_prov, n_dept, n_insp]):
                    try:
                        c.execute("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", (n_id, n_name, n_phone, n_prov, n_dept, n_branch, n_insp, n_pw))
                        conn.commit()
                        st.success("تمت الإضافة بنجاح!")
                    except:
                        st.error("الرقم مسجل مسبقاً!")
                else:
                    st.warning("يرجى ملء جميع الخانات.")

        st.markdown("---")
        st.subheader("📋 البيانات المسجلة / حذف")
        all_df = pd.read_sql_query("SELECT * FROM employees", conn)
        st.dataframe(all_df)
        del_target = st.text_input("أدخل رقم الموظف للحذف")
        if st.button("حذف نهائي"):
            c.execute("DELETE FROM employees WHERE emp_id=?", (del_target,))
            conn.commit()
            st.rerun()
