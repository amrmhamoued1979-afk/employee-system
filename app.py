import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعدادات الصفحة وإخفاء القائمة العلوية نهائياً ---
st.set_page_config(page_title="نظام بيانات - الصحبة الطيبة", layout="wide")

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

# --- 2. الواجهة الجمالية (الصحبة الطيبة وعلم مصر) ---
# تصميم الجزء العلوي باستخدام HTML لعرض علم مصر واسم المجموعة
st.markdown("""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 10px solid #ce1126; border-right: 10px solid #000000; text-align: center;">
        <h1 style="color: #000; margin-bottom: 0;">🇪🇬 الصحبة الطيبة 🇪🇬</h1>
        <p style="color: #666; font-size: 18px;">نظام إدارة البيانات والاستعلام</p>
        <div style="height: 5px; background: linear-gradient(to right, #ce1126 33%, #ffffff 33%, #ffffff 66%, #000000 66%); margin-top: 10px;"></div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect('sohba_database_v1.db', check_same_thread=False)
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
    st.markdown("<h3 style='text-align: center;'>📝 تسجيل بيانات عضو جديد</h3>", unsafe_allow_html=True)
    st.warning("يجب ملء كافة البيانات المطلوبة لإتمام عملية الحفظ")
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
                    c.execute("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", 
                              (r_id, r_name, r_phone, r_prov, r_dept, r_branch, r_insp, r_pw))
                    conn.commit()
                    st.success("✅ تم حفظ بياناتك بنجاح في مجموعة الصحبة الطيبة!")
                except:
                    st.error("⚠️ هذا الرقم مسجل بالفعل في النظام.")
            else:
                st.error("🛑 خطأ: يرجى ملء كافة الخانات المطلوبة قبل الحفظ.")

# القسم الثاني: الاستعلام العام
elif choice == "الاستعلام العام":
    st.header("🔍 استعلام جهات الفحص")
    df = pd.read_sql_query("SELECT name as 'الاسم', phone as 'رقم التليفون', province as 'المحافظة', inspection as 'جهة الفحص' FROM employees", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة حالياً.")

# القسم الثالث: تعديل البيانات
elif choice == "تعديل بياناتي (دخول الموظف)":
    st.header("🔑 دخول العضو للتعديل")
    l_id = st.text_input("أدخل رقم العضو")
    l_pw = st.text_input("أدخل كلمة السر", type="password")
    if st.button("دخول"):
        user = c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?", (l_id, l_pw)).fetchone()
        if user:
            st.session_state['active_id'] = l_id
            st.success("تم تسجيل الدخول بنجاح.")
        else:
            st.error("بيانات الدخول غير صحيحة")

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

# القسم الرابع: لوحة التحكم (مخفية بكلمة سر admin79)
elif choice == "لوحة تحكم المسؤول (أنا فقط)":
    st.header("🛠 لوحة إدارة الصحبة الطيبة")
    all_df = pd.read_sql_query("SELECT * FROM employees", conn)
    st.dataframe(all_df)
    del_id = st.text_input("أدخل رقم العضو للحذف")
    if st.button("حذف السجل نهائياً"):
        c.execute("DELETE FROM employees WHERE emp_id=?", (del_id,))
        conn.commit()
        st.rerun()
