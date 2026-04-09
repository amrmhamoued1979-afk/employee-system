import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="الجهاز المركزي للمحاسبات - نظام البيانات", layout="wide")

# --- 2. عرض اللوجو (حل مشكلة الصورة المكسورة) ---
# سأستخدم رابطاً مباشراً للصورة التي أرسلتها سابقاً
st.image("https://ibb.co", caption="الجهاز المركزي للمحاسبات", use_container_width=True)
st.markdown("---")

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect('final_v4.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS employees 
             (emp_id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center_dept TEXT, branch TEXT, inspection TEXT, password TEXT)''')
conn.commit()

# --- 4. القائمة الجانبية ---
st.sidebar.title("🔐 بوابة النظام")
menu = ["الاستعلام العام", "تسجيل بياناتي (لأول مرة)", "تعديل بياناتي (دخول الموظف)", "لوحة تحكم المسؤول"]
choice = st.sidebar.selectbox("اختر الإجراء:", menu)

# --- القسم الأول: الاستعلام العام ---
if choice == "الاستعلام العام":
    st.header("🔍 استعلام جهات الفحص")
    df = pd.read_sql_query("SELECT name as 'الاسم', province as 'المحافظة', inspection as 'جهة الفحص' FROM employees", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("..لا توجد بيانات مسجلة حالياً")

# --- القسم الثاني: تسجيل بيانات الموظف (لأول مرة) ---
elif choice == "تسجيل بياناتي (لأول مرة)":
    st.header("📝 تسجيل حساب وبيانات جديدة")
    st.info("يجب ملء كافة الخانات لإتمام عملية الحفظ")
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            r_id = st.text_input("رقم الموظف")
            r_name = st.text_input("الاسم بالكامل")
            r_phone = st.text_input("رقم التليفون")
            r_pw = st.text_input("اختر كلمة سر خاصة بك", type="password")
        with col2:
            r_prov = st.text_input("المحافظة")
            r_dept = st.text_input("الإدارة المركزية")
            r_branch = st.selectbox("الفرع", ["الأول", "الثاني"])
            r_insp = st.text_input("جهة الفحص")
        
        if st.form_submit_button("إرسال وحفظ البيانات"):
            # شرط التأكد من أن جميع الخانات مكتملة
            if all([r_id, r_name, r_phone, r_pw, r_prov, r_dept, r_insp]):
                try:
                    c.execute("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", 
                              (r_id, r_name, r_phone, r_prov, r_dept, r_branch, r_insp, r_pw))
                    conn.commit()
                    st.success("✅ تم تسجيل بياناتك بنجاح. يمكنك الآن الاستعلام عنها.")
                except:
                    st.error("⚠️ رقم الموظف هذا مسجل مسبقاً في النظام")
            else:
                st.error("🛑 خطأ: يجب كتابة كافة البيانات المطلوبة قبل الحفظ")

# --- القسم الثالث: تعديل الموظف لبياناته ---
elif choice == "تعديل بياناتي (دخول الموظف)":
    st.header("🔑 دخول الموظف لتعديل بياناته")
    l_id = st.text_input("أدخل رقم الموظف")
    l_pw = st.text_input("أدخل كلمة السر", type="password")
    
    if st.button("دخول"):
        user = c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?", (l_id, l_pw)).fetchone()
        if user:
            st.session_state['active_user'] = l_id
            st.success("تم الدخول بنجاح")
        else:
            st.error("بيانات الدخول غير صحيحة")

    if 'active_user' in st.session_state:
        curr_id = st.session_state['active_user']
        user_data = c.execute("SELECT * FROM employees WHERE emp_id=?", (curr_id,)).fetchone()
        with st.form("update_form"):
            new_phone = st.text_input("تحديث التليفون", value=user_data[2])
            new_insp = st.text_input("تحديث جهة الفحص", value=user_data[6])
            if st.form_submit_button("حفظ التغييرات"):
                c.execute("UPDATE employees SET phone=?, inspection=? WHERE emp_id=?", (new_phone, new_insp, curr_id))
                conn.commit()
                st.success("تم التحديث")

# --- القسم الرابع: لوحة التحكم (المسؤول) ---
elif choice == "لوحة تحكم المسؤول":
    st.header("🛠 لوحة الإدارة")
    admin_pw = st.sidebar.text_input("كلمة سر الإدارة", type="password")
    if admin_pw == "admin79":
        st.write("بيانات جميع الموظفين المسجلين:")
        all_df = pd.read_sql_query("SELECT * FROM employees", conn)
        st.dataframe(all_df)
        del_id = st.text_input("رقم الموظف المراد حذفه")
        if st.button("حذف نهائي"):
            c.execute("DELETE FROM employees WHERE emp_id=?", (del_id,))
            conn.commit()
            st.rerun()
    else:
        st.error("هذا القسم محمي")
