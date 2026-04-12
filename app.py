import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعدادات الصفحة والحماية القصوى ---
st.set_page_config(page_title="نظام الصحبة الطيبة - حماية فائقة", layout="wide")

hide_style = """
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stHeader"] {display:none;}
    [data-testid="stSidebar"] {display: none;}
    * { -webkit-user-select: none !important; user-select: none !important; }
</style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- 2. الواجهة العلوية ---
st.markdown("""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-top: 8px solid #ce1126; border-bottom: 5px solid #000; text-align: center;">
        <h1 style="color: #000; margin: 0;">🇪🇬 الصحبة الطيبة 🇪🇬</h1>
        <p style="color: #d32f2f; font-weight: bold; margin-top: 10px;">⚠️ نظام بيانات مؤمن: يمنع النسخ أو التصوير تماماً</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect('sohba_secure_v16.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS employees 
             (emp_id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center_dept TEXT, branch TEXT, inspection TEXT, password TEXT)''')
conn.commit()

# --- 4. عداد المسجلين ---
employee_count = pd.read_sql_query("SELECT COUNT(*) as count FROM employees", conn).iloc[0]['count']
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown(f"""
        <div style="background-color: #1E3A8A; color: white; padding: 15px; border-radius: 20px; text-align: center; margin-top: 15px; border: 2px solid #ce1126;">
            <p style="margin: 0; font-size: 16px;">إجمالي عدد المسجلين حالياً</p>
            <h2 style="margin: 0; font-size: 40px; font-weight: bold;">{employee_count}</h2>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 5. خيارات التنقل ---
choice = st.selectbox("### ⬇️ اختر الإجراء المطلوب:", ["📝 تسجيل بياناتي (لأول مرة)", "🔍 الاستعلام العام (للمسجلين فقط)", "🔑 تعديل بياناتي الشخصية"])

# --- 6. تنفيذ الأقسام ---

# القسم الأول: تسجيل البيانات
if choice == "📝 تسجيل بياناتي (لأول مرة)":
    st.markdown("<h3 style='text-align: center;'>📝 تسجيل بيانات عضو جديد</h3>", unsafe_allow_html=True)
    with st.form("reg_form"):
        c1, c2 = st.columns(2)
        with c1:
            r_id = st.text_input("رقم الموظف / الكود")
            r_name = st.text_input("الاسم بالكامل")
            r_phone = st.text_input("رقم التليفون")
            r_pw = st.text_input("اختر كلمة سر خاصة بك", type="password")
        with c2:
            r_prov = st.text_input("المحافظة")
            r_dept = st.text_input("الإدارة المركزية")
            r_branch = st.selectbox("الفرع", ["الأول", "الثاني"])
            r_insp = st.text_area("جهة الفحص")
        
        if st.form_submit_button("إرسال وحفظ البيانات"):
            if all([r_id, r_name, r_phone, r_pw, r_prov, r_dept, r_insp]):
                if c.execute("SELECT * FROM employees WHERE name=? OR emp_id=?", (r_name, r_id)).fetchone():
                    st.error("🛑 هذا الاسم أو الرقم مسجل مسبقاً!")
                else:
                    c.execute("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", (r_id, r_name, r_phone, r_prov, r_dept, r_branch, r_insp, r_pw))
                    conn.commit()
                    st.success("✅ تم حفظ بياناتك بنجاح!")
                    st.rerun()
            else: st.error("🛑 يرجى ملء كافة الخانات.")

# القسم الثاني: الاستعلام العام (محمي بالدخول)
elif choice == "🔍 الاستعلام العام (للمسجلين فقط)":
    st.header("🔍 استعلام جهات الفحص")
    
    # طلب تسجيل الدخول أولاً لرؤية الجدول
    if 'view_auth' not in st.session_state:
        st.warning("⚠️ لاطلاع على جهات الفحص، يرجى تسجيل الدخول أولاً برقمك الوظيفي وكلمة السر.")
        with st.container():
            v_id = st.text_input("رقم الموظف", key="v_id")
            v_pw = st.text_input("كلمة السر", type="password", key="v_pw")
            if st.button("دخول للاستعلام"):
                user = c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?", (v_id, v_pw)).fetchone()
                if user:
                    st.session_state['view_auth'] = True
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة.")
    else:
        # إذا تم التأكد من الهوية، يظهر الجدول
        st.success("🔓 تم التحقق من الهوية. يمكنك الآن الاطلاع على البيانات.")
        df = pd.read_sql_query("SELECT name as 'الاسم', phone as 'رقم التليفون', province as 'المحافظة', inspection as 'جهة الفحص' FROM employees", conn)
        if not df.empty:
            df.insert(0, 'م', range(1, len(df) + 1))
            st.table(df)
            if st.button("خروج وإغلاق الاستعلام"):
                del st.session_state['view_auth']
                st.rerun()
        else:
            st.info("لا توجد بيانات مسجلة حالياً.")

# القسم الثالث: تعديل البيانات الشخصية
elif choice == "🔑 تعديل بياناتي الشخصية":
    st.header("🔑 دخول لتعديل بياناتك")
    l_id = st.text_input("أدخل رقم الموظف")
    l_pw = st.text_input("أدخل كلمة السر", type="password")
    if st.button("دخول للتعديل"):
        user = c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?", (l_id, l_pw)).fetchone()
        if user:
            st.session_state['active_id'] = l_id
            st.success("تم الدخول بنجاح.")
        else: st.error("بيانات الدخول غير صحيحة.")
    
    if 'active_id' in st.session_state:
        uid = st.session_state['active_id']
        u_data = c.execute("SELECT * FROM employees WHERE emp_id=?", (uid,)).fetchone()
        with st.form("edit_form"):
            new_ph = st.text_input("تعديل التليفون", value=u_data[2])
            new_is = st.text_area("تعديل جهة الفحص", value=u_data[6])
            if st.form_submit_button("حفظ التعديلات"):
                c.execute("UPDATE employees SET phone=?, inspection=? WHERE emp_id=?", (new_ph, new_is, uid))
                conn.commit()
                st.success("✅ تم تحديث بياناتك.")

# --- 7. بوابة الإدارة ---
st.divider()
with st.expander("🛠 بوابة الإدارة والتحكم (للمسؤول فقط)"):
    admin_pw = st.text_input("كلمة سر المسؤول", type="password")
    if admin_pw == "admin79":
        all_df = pd.read_sql_query("SELECT * FROM employees", conn)
        st.dataframe(all_df, hide_index=True)
        del_id = st.text_input("رقم الموظف للحذف")
        if st.button("حذف نهائي"):
            c.execute("DELETE FROM employees WHERE emp_id=?", (del_id,))
            conn.commit()
            st.rerun()
