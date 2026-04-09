import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعدادات الصفحة وإخفاء القوائم ---
st.set_page_config(page_title="الصحبة الطيبة - نظام البيانات", layout="wide")

hide_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stAppDeployButton {display:none;}
            [data-testid="stHeader"] {display:none;}
            [data-testid="stSidebar"] {display: none;}
            </style>
            """
st.markdown(hide_style, unsafe_allow_html=True)

# --- 2. الواجهة العلوية ---
st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-top: 5px solid #ce1126; border-bottom: 5px solid #000; text-align: center;">
        <h1 style="color: #000; margin: 0;">🇪🇬 الصحبة الطيبة 🇪🇬</h1>
        <p style="color: #666; font-size: 16px; margin: 5px 0;">نظام إدارة البيانات والاستعلام العام</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect('sohba_final_v10.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS employees 
             (emp_id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center_dept TEXT, branch TEXT, inspection TEXT, password TEXT)''')
conn.commit()

# --- 4. عداد الموظفين المسجلين ---
# جلب العدد من قاعدة البيانات
employee_count = pd.read_sql_query("SELECT COUNT(*) as count FROM employees", conn).iloc[0]['count']

# عرض العداد بشكل جميل
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.markdown(f"""
        <div style="background-color: #1E3A8A; color: white; padding: 10px; border-radius: 15px; text-align: center; margin-top: 10px; border: 2px solid #ce1126;">
            <p style="margin: 0; font-size: 14px;">عدد المسجلين حالياً</p>
            <h2 style="margin: 0; font-size: 32px; font-weight: bold;">{employee_count}</h2>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 5. خيارات التنقل ---
st.write("### ⬇️ اختر الإجراء المطلوب:")
choice = st.selectbox("", ["الاستعلام العام", "تسجيل بياناتي (لأول مرة)", "تعديل بياناتي (دخول العضو)"])

# --- 6. تنفيذ الأقسام ---

# تم جعل الاستعلام هو الأول لسهولة الرؤية
if choice == "الاستعلام العام":
    st.header("🔍 استعلام جهات الفحص")
    df = pd.read_sql_query("SELECT name as 'الاسم', phone as 'رقم التليفون', province as 'المحافظة', inspection as 'جهة الفحص' FROM employees", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة حالياً.")

elif choice == "تسجيل بياناتي (لأول مرة)":
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
                    st.success("✅ تم الحفظ بنجاح! سيتم تحديث العداد الآن.")
                    st.rerun() # إعادة التشغيل لتحديث العداد فوراً
                except:
                    st.error("⚠️ هذا الرقم مسجل مسبقاً.")
            else:
                st.error("🛑 يجب ملء كافة الخانات.")

elif choice == "تعديل بياناتي (دخول العضو)":
    st.header("🔑 دخول العضو للتعديل")
    l_id = st.text_input("رقم العضو")
    l_pw = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        user = c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?", (l_id, l_pw)).fetchone()
        if user:
            st.session_state['active_id'] = l_id
            st.success("تم الدخول بنجاح")
        else:
            st.error("بيانات الدخول خاطئة")
    
    if 'active_id' in st.session_state:
        curr_id = st.session_state['active_id']
        user_data = c.execute("SELECT * FROM employees WHERE emp_id=?", (curr_id,)).fetchone()
        with st.form("edit_form"):
            u_phone = st.text_input("رقم التليفون الجديد", value=user_data)
            u_insp = st.text_input("جهة الفحص الجديدة", value=user_data)
            if st.form_submit_button("حفظ التعديلات"):
                c.execute("UPDATE employees SET phone=?, inspection=? WHERE emp_id=?", (u_phone, u_insp, curr_id))
                conn.commit()
                st.success("تم التحديث بنجاح!")

# --- 7. بوابة الإدارة (تحت خالص) ---
st.write("---")
with st.expander("🛠 بوابة الإدارة والتحكم (للمسؤول فقط)"):
    admin_pw = st.text_input("كلمة سر المسؤول", type="password")
    if admin_pw == "admin79":
        all_df = pd.read_sql_query("SELECT * FROM employees", conn)
        st.dataframe(all_df)
        del_id = st.text_input("رقم العضو المراد حذفه")
        if st.button("حذف نهائي"):
            c.execute("DELETE FROM employees WHERE emp_id=?", (del_id,))
            conn.commit()
            st.rerun()
