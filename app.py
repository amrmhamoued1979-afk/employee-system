import streamlit as st
import pandas as pd
import sqlite3

# --- 1. إعدادات الصفحة ونظام الحماية القصوى ضد النسخ والتصوير ---
st.set_page_config(page_title="نظام الصحبة الطيبة - حماية فائقة", layout="wide")

# كود الحماية (منع النسخ + علامة مائية مكررة + إخفاء القوائم + منع النقر اليمين)
protection_code = """
<style>
    /* إخفاء القوائم العلوية والسفلى نهائياً */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stHeader"] {display:none;}
    [data-testid="stSidebar"] {display: none;}

    /* 1. منع تحديد النصوص تماماً (Anti-Copy) */
    * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }

    /* 2. إضافة علامة مائية كثيفة مكررة خلف البيانات لمنع التصوير بالموبايل */
    .main::before {
        content: "الصحبة الطيبة - نسخة محمية - يمنع التصوير  الصحبة الطيبة - نسخة محمية - يمنع التصوير";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        font-size: 30px;
        color: rgba(200, 200, 200, 0.07);
        display: flex;
        align-items: center;
        justify-content: center;
        transform: rotate(-20deg);
        pointer-events: none;
        z-index: 1000;
        white-space: pre-wrap;
    }

    /* 3. تنسيق الجداول لتكون واضحة وصعبة في النسخ */
    .stTable {
        border: 2px solid #000 !important;
    }
</style>

<script>
    /* 4. منع النقر بزر الفأرة الأيمن */
    document.addEventListener('contextmenu', event => event.preventDefault());

    /* 5. منع اختصارات النسخ والطباعة وتصوير الشاشة */
    document.onkeydown = function(e) {
        if (e.ctrlKey && (e.keyCode === 67 || e.keyCode === 86 || e.keyCode === 85 || e.keyCode === 83 || e.keyCode === 80 || e.keyCode === 70)) {
            return false;
        }
    };
</script>
"""
st.markdown(protection_code, unsafe_allow_html=True)

# --- 2. الواجهة العلوية (علم مصر والاسم) ---
st.markdown("""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-top: 8px solid #ce1126; border-bottom: 8px solid #000; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
        <h1 style="color: #000; margin: 0;">🇪🇬 الصحبة الطيبة 🇪🇬</h1>
        <p style="color: #d32f2f; font-weight: bold; margin-top: 10px;">⚠️ نظام بيانات مؤمن: يمنع النسخ أو التصوير تماماً</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect('secure_sohba_final_system.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS employees 
             (emp_id TEXT PRIMARY KEY, name TEXT, phone TEXT, province TEXT, 
              center_dept TEXT, branch TEXT, inspection TEXT, password TEXT)''')
conn.commit()

# --- 4. عداد الموظفين (الرقم الضخم) ---
employee_count = pd.read_sql_query("SELECT COUNT(*) as count FROM employees", conn).iloc[0]['count']

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
        <div style="background-color: #1E3A8A; color: white; padding: 15px; border-radius: 20px; text-align: center; margin-top: 15px; border: 2px solid #ce1126;">
            <p style="margin: 0; font-size: 16px;">إجمالي عدد المسجلين حالياً</p>
            <h2 style="margin: 0; font-size: 40px; font-weight: bold;">{employee_count}</h2>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 5. خيارات التنقل (مرتبة حسب طلبك) ---
st.write("### ⬇️ اختر الإجراء المطلوب:")
choice = st.selectbox("", ["📝 تسجيل بياناتي (لأول مرة)", "🔑 تعديل بياناتي (دخول العضو)", "🔍 الاستعلام العام (محمي)"])

# --- 6. تنفيذ الأقسام ---

# القسم الأول: تسجيل البيانات (مع حماية التكرار)
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
            r_insp = st.text_input("جهة الفحص")
        
        if st.form_submit_button("إرسال وحفظ البيانات"):
            if all([r_id, r_name, r_phone, r_pw, r_prov, r_dept, r_insp]):
                # التحقق من عدم تكرار الاسم أو الرقم
                if c.execute("SELECT * FROM employees WHERE name=? OR emp_id=?", (r_name, r_id)).fetchone():
                    st.error("🛑 خطأ: هذا الاسم أو رقم الموظف مسجل مسبقاً!")
                else:
                    try:
                        c.execute("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", (r_id, r_name, r_phone, r_prov, r_dept, r_branch, r_insp, r_pw))
                        conn.commit()
                        st.success("✅ تم حفظ بياناتك بنجاح في الصحبة الطيبة!")
                        st.rerun()
                    except: st.error("⚠️ حدث خطأ غير متوقع.")
            else: st.error("🛑 يرجى ملء كافة الخانات المطلوبة.")

# القسم الثاني: تعديل البيانات
elif choice == "🔑 تعديل بياناتي (دخول العضو)":
    st.header("🔑 دخول العضو لتعديل بياناته")
    l_id = st.text_input("أدخل رقم العضو")
    l_pw = st.text_input("أدخل كلمة السر", type="password")
    if st.button("دخول"):
        user = c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?", (l_id, l_pw)).fetchone()
        if user:
            st.session_state['user_auth'] = l_id
            st.success("تم الدخول بنجاح.")
        else: st.error("بيانات الدخول غير صحيحة.")
    
    if 'user_auth' in st.session_state:
        uid = st.session_state['user_auth']
        u_data = c.execute("SELECT * FROM employees WHERE emp_id=?", (uid,)).fetchone()
        with st.form("edit_form"):
            new_ph = st.text_input("تعديل رقم التليفون", value=u_data[2])
            new_is = st.text_input("تعديل جهة الفحص", value=u_data[6])
            if st.form_submit_button("حفظ التعديلات"):
                c.execute("UPDATE employees SET phone=?, inspection=? WHERE emp_id=?", (new_ph, new_is, uid))
                conn.commit()
                st.success("✅ تم تحديث بياناتك.")

# القسم الثالث: الاستعلام العام (محمي بالكامل)
elif choice == "🔍 الاستعلام العام (محمي)":
    st.header("🔍 استعلام جهات الفحص")
    st.info("💡 هذه البيانات محمية ضد النسخ والتصوير بعلامات مائية شفافة.")
    df = pd.read_sql_query("SELECT name as 'الاسم', phone as 'رقم التليفون', province as 'المحافظة', inspection as 'جهة الفحص' FROM employees", conn)
    if not df.empty:
        # إضافة الرقم المسلسل (م)
        df.insert(0, 'م', range(1, len(df) + 1))
        # عرض الجدول بصيغة st.table لأنها أكثر أماناً وتظهر تحتها العلامة المائية بشكل أفضل
        st.table(df)
    else: st.info("لا توجد بيانات مسجلة حالياً.")

# --- 7. بوابة الإدارة (تحت خالص) ---
st.divider()
with st.expander("🛠 بوابة الإدارة والتحكم (للمسؤول فقط)"):
    admin_pw = st.text_input("كلمة سر المسؤول", type="password")
    if admin_pw == "admin79":
        all_df = pd.read_sql_query("SELECT * FROM employees", conn)
        if not all_df.empty:
            all_df.insert(0, 'م', range(1, len(all_df) + 1))
            st.dataframe(all_df, hide_index=True)
        del_id = st.text_input("رقم العضو للحذف")
        if st.button("حذف نهائي"):
            c.execute("DELETE FROM employees WHERE emp_id=?", (del_id,))
            conn.commit()
            st.rerun()
