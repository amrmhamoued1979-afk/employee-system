import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعدادات الصفحة وإخفاء القائمة العلوية نهائياً ---
st.set_page_config(page_title="نظام بيانات الموظفين - الجهاز المركزي للمحاسبات", layout="wide")

# كود لإخفاء Fork و GitHub وجميع أيقونات Streamlit العلوية
hide_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stAppDeployButton {display:none;}
            [data-testid="stHeader"] {display:none;}
            </style>
            """
st.markdown(hide_style, unsafe_allow_html=True)

# --- 2. عرض اللوجو والعنوان (تم تعديل طريقة العرض لتكون مضمونة) ---
# سنضع اللوجو في المنتصف مع العنوان بشكل احترافي
col1, col2, col3 = st.columns([1,2,1])
with col2:
    # رابط الصورة المباشر
    st.image("https://ibb.co", use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>الجهاز المركزي للمحاسبات</h2>", unsafe_allow_html=True)

st.divider()

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect('main_database_v9.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS employees 
             (emp_id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center_dept TEXT, branch TEXT, inspection TEXT, password TEXT)''')
conn.commit()

# --- 4. القائمة الجانبية والأمان ---
st.sidebar.title("🔐 بوابة النظام")

# خانة سرية لإظهار لوحة التحكم (كلمة السر: admin79)
admin_access = st.sidebar.text_input("كلمة سر الإدارة (لإظهار اللوحة)", type="password")

if admin_access == "admin79":
    menu = ["تسجيل بياناتي (لأول مرة)", "الاستعلام العام", "تعديل بياناتي (دخول الموظف)", "لوحة تحكم المسؤول (أنا فقط)"]
else:
    menu = ["تسجيل بياناتي (لأول مرة)", "الاستعلام العام", "تعديل بياناتي (دخول الموظف)"]

choice = st.sidebar.selectbox("اختر الإجراء:", menu)

# --- 5. تنفيذ الأقسام ---

# القسم الأول: تسجيل البيانات (الافتراضي)
if choice == "تسجيل بياناتي (لأول مرة)":
    st.markdown("<h3 style='text-align: center;'>📝 تسجيل حساب جديد</h3>", unsafe_allow_html=True)
    st.warning("يجب ملء كافة البيانات المطلوبة لإتمام عملية الحفظ")
    with st.form("reg_form"):
        c1, c2 = st.columns(2)
        with c1:
            r_id = st.text_input("رقم الموظف")
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
                    c.execute("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", 
                              (r_id, r_name, r_phone, r_prov, r_dept, r_branch, r_insp, r_pw))
                    conn.commit()
                    st.success("✅ تم حفظ بياناتك بنجاح!")
                except:
                    st.error("⚠️ رقم الموظف هذا مسجل بالفعل.")
            else:
                st.error("🛑 خطأ: يرجى ملء كافة الخانات المطلوبة قبل الحفظ.")

# القسم الثاني: الاستعلام العام (مع إظهار التليفون)
elif choice == "الاستعلام العام":
    st.header("🔍 استعلام جهات الفحص")
    df = pd.read_sql_query("SELECT name as 'الاسم', phone as 'رقم التليفون', province as 'المحافظة', inspection as 'جهة الفحص' FROM employees", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة حالياً.")

# القسم الثالث: تعديل الموظف لبياناته
elif choice == "تعديل بياناتي (دخول الموظف)":
    st.header("🔑 دخول الموظف للتعديل")
    l_id = st.text_input("أدخل رقم الموظف")
    l_pw = st.text_input("أدخل كلمة السر", type="password")
    if st.button("دخول"):
        user = c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?", (l_id, l_pw)).fetchone()
        if user:
            st.session_state['active_id'] = l_id
            st.success("تم تسجيل الدخول بنجاح.")
        else:
            st.error("بيانات الدخول غير صحيحة.")

    if 'active_id' in st.session_state:
        curr_id = st.session_state['active_id']
        data = c.execute("SELECT * FROM employees WHERE emp_id=?", (curr_id,)).fetchone()
        with st.form("update_form"):
            u_phone = st.text_input("تحديث رقم التليفون", value=data[2])
            u_insp = st.text_input("تحديث جهة الفحص", value=data[6])
            if st.form_submit_button("حفظ التعديلات الشخصية"):
                c.execute("UPDATE employees SET phone=?, inspection=? WHERE emp_id=?", (u_phone, u_insp, curr_id))
                conn.commit()
                st.success("تم التحديث بنجاح.")

# القسم الرابع: لوحة التحكم (تظهر بكلمة سر admin79)
elif choice == "لوحة تحكم المسؤول (أنا فقط)":
    st.header("🛠 لوحة الإدارة العليا")
    all_df = pd.read_sql_query("SELECT * FROM employees", conn)
    st.dataframe(all_df)
    del_id = st.text_input("أدخل رقم الموظف للحذف")
    if st.button("حذف السجل"):
        c.execute("DELETE FROM employees WHERE emp_id=?", (del_id,))
        conn.commit()
        st.rerun()
