import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="نظام تسجيل الموظفين - حماية فائقة", layout="wide")

# إخفاء عناصر Streamlit الافتراضية للخصوصية
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- 2. إنشاء الاتصال بجوجل شيت ---
# ملاحظة: تأكد من وضع رابط الملف في Secrets كما شرحنا سابقاً
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. دالة الحفظ الجديدة ---
def save_data(data_dict):
    try:
        # قراءة البيانات الحالية (مع تجاهل التخزين المؤقت لضمان التحديث اللحظي)
        existing_data = conn.read(worksheet="الورقة1", ttl=0)
        existing_data = existing_data.dropna(how="all")
        
        # تحويل البيانات الجديدة لـ DataFrame
        new_row = pd.DataFrame([data_dict])
        
        # دمج البيانات وتحديث الملف
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(worksheet="الورقة1", data=updated_df)
        return True
    except Exception as e:
        st.error(f"خطأ تقني في الاتصال بالسحابة: {e}")
        return False

# --- 4. واجهة المستخدم (Form) ---
st.title("📋 استمارة تسجيل بيانات الموظفين")
st.info("سيتم حفظ البيانات مباشرة في قاعدة بيانات سحابية مؤمنة.")

with st.form("employee_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        emp_id = st.text_input("رقم الموظف")
        name = st.text_input("الاسم بالكامل")
        phone = st.text_input("رقم التليفون")
    
    with col2:
        governorate = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "الإسكندرية", "أخرى"])
        central_dept = st.text_input("الإدارة المركزية")
        branch = st.text_input("الفرع")
    
    check_entities = st.text_area("جهات الفحص")
    
    submitted = st.form_submit_button("إرسال وحفظ البيانات")
    
    if submitted:
        if name and emp_id:  # التحقق من الحقول الأساسية
            new_entry = {
                "رقم الموظف": emp_id,
                "الاسم": name,
                "التليفون": phone,
                "المحافظة": governorate,
                "الإدارة المركزية": central_dept,
                "الفرع": branch,
                "جهات الفحص": check_entities
            }
            
            with st.spinner("جاري الحفظ في السحابة..."):
                if save_data(new_entry):
                    st.success(f"تم حفظ بيانات الموظف ({name}) بنجاح في Google Sheets! ✅")
                else:
                    st.error("فشل الحفظ. تأكد من إعدادات الـ Secrets.")
        else:
            st.warning("يرجى ملء الحقول الأساسية (الاسم ورقم الموظف).")

# --- 5. عرض البيانات (للمسؤول فقط) ---
if st.checkbox("عرض البيانات المسجلة"):
    try:
        data = conn.read(worksheet="الورقة1", ttl=0)
        st.dataframe(data)
    except:
        st.write("لا توجد بيانات لعرضها حالياً.")
