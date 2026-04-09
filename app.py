import streamlit as st
import pandas as pd
import sqlite3

# 1. إعدادات الصفحة والواجهة
st.set_page_config(page_title="نظام بيانات الموظفين", layout="wide")

# 2. إنشاء قاعدة البيانات والجدول بالأعمدة المطلوبة
conn = sqlite3.connect('employees_v2.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS data_table 
             (emp_id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center_dept TEXT, branch TEXT, inspection TEXT)''')
conn.commit()

# --- القائمة الجانبية (Sidebar) ---
st.sidebar.title("🔐 بوابة النظام")
choice = st.sidebar.radio("انتقل إلى:", ["الاستعلام العام", "إدخال بيانات الموظف", "لوحة تحكم المسؤول (تعديل/حذف)"])

# --- القسم الأول: الاستعلام العام (متاح للجميع) ---
if choice == "الاستعلام العام":
    st.header("🔍 استعلام عن جهات الفحص")
    df = pd.read_sql_query("SELECT name as 'الاسم', province as 'المحافظة', inspection as 'جهة الفحص' FROM data_table", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة حالياً.")

# --- القسم الثاني: إدخال بيانات الموظف (يظهر فوراً) ---
elif choice == "إدخال بيانات الموظف":
    st.header("📝 إدخال بيانات موظف جديد")
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            e_id = st.text_input("رقم الموظف")
            e_name = st.text_input("الاسم")
            e_phone = st.text_input("رقم التليفون")
            e_prov = st.text_input("المحافظة")
        with col2:
            e_dept = st.text_input("الإدارة المركزية")
            e_branch = st.selectbox("الفرع", ["الأول", "الثاني"])
            e_insp = st.text_input("جهة الفحص")
        
        if st.form_submit_button("حفظ البيانات"):
            if e_id and e_name:
                try:
                    c.execute("INSERT INTO data_table VALUES (?,?,?,?,?,?,?)", 
                              (e_id, e_name, e_phone, e_prov, e_dept, e_branch, e_insp))
                    conn.commit()
                    st.success("تم حفظ البيانات بنجاح وظهورها في الاستعلام العام.")
                except:
                    st.error("عذراً، رقم الموظف هذا مسجل مسبقاً!")
            else:
                st.warning("يرجى إدخال رقم الموظف والاسم على الأقل.")

# --- القسم الثالث: لوحة التحكم (لك أنت فقط للتعديل أو الحذف) ---
elif choice == "لوحة تحكم المسؤول (تعديل/حذف)":
    st.header("🛠 إدارة قاعدة البيانات")
    admin_pw = st.sidebar.text_input("كلمة سر الإدارة", type="password")
    
    # كلمة السر هي admin79 (يمكنك تغييرها من هنا)
    if admin_pw == "admin79":
        st.subheader("تعديل أو حذف بيانات الموظفين")
        all_data = pd.read_sql_query("SELECT * FROM data_table", conn)
        
        if not all_data.empty:
            st.dataframe(all_data)
            selected_id = st.selectbox("اختر رقم الموظف للإجراء:", all_data['emp_id'])
            
            col_del, col_edit = st.columns(2)
            with col_del:
                if st.button("❌ حذف الموظف المختار"):
                    c.execute("DELETE FROM data_table WHERE emp_id=?", (selected_id,))
                    conn.commit()
                    st.warning(f"تم حذف الموظف رقم {selected_id}")
                    st.rerun()
            
            with col_edit:
                st.write("لتعديل بيانات الموظف، يفضل حذفه وإعادة إدخاله بالبيانات الصحيحة حالياً.")
        else:
            st.info("قاعدة البيانات فارغة.")
    else:
        st.error("هذا القسم محمي للمسؤول فقط. يرجى إدخال كلمة السر في القائمة الجانبية.")
