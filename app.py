import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import io

# --- 1. CLEAN WHITE & GOLD THEME ---
st.set_page_config(page_title="JD GOLD HUB", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3 { color: #D4AF37; text-align: center; font-family: 'serif'; }
    /* Black Fonts for inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
        color: #000000 !important; border: 1px solid #D4AF37 !important; 
    }
    .stTabs [aria-selected="true"] { color: #D4AF37; border-bottom: 2px solid #D4AF37; }
    .stButton>button { 
        background: linear-gradient(45deg, #D4AF37, #B8860B); 
        color: white; font-weight: bold; border-radius: 8px; 
    }
    .streamlit-expanderHeader { background-color: #FDFCF0 !important; color: #000 !important; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PRECISION STAMPING ENGINE WITH FONT CONTROL ---
def create_page_overlay(data, draft_mode, font_size):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # APPLY USER SELECTED FONT SIZE
    can.setFont("Helvetica-Bold", font_size)
    can.setFillColor(colors.black)

    # A. CLIENT DATA (Right Side)
    can.drawString(420, 750, f"NAME: {data['name']}")
    can.drawString(420, 735, f"SSN: {data['ssn']}")
    can.drawString(420, 720, f"DOB: {data['dob']}")
    can.drawString(420, 705, f"TEL: {data['phone']}")
    can.drawString(420, 690, f"EMAIL: {data['email']}")
    
    # B. ADDRESS & CRIME (Lower Section)
    can.drawString(420, 660, f"ADDR: {data['address'][:30]}...") # Shortened for fit
    can.drawString(420, 645, f"CRIME: {data['crime']}")

    # C. ADVOCATE DATA (Lower Middle Left)
    can.drawString(50, 300, f"ADVOCATE: {data['adv_name']}")
    can.drawString(50, 285, f"ID NO: {data['adv_id']}")

    # D. IMAGES (Lower Middle)
    try:
        if data['img_r1']:
            can.drawImage(ImageReader(data['img_r1']), 400, 250, width=100, height=70)
        if data['img_r2']:
            can.drawImage(ImageReader(data['img_r2']), 510, 250, width=100, height=70)
        if data['img_l1']:
            can.drawImage(ImageReader(data['img_l1']), 50, 200, width=100, height=70)
    except:
        pass # Prevents crashing if image format is weird

    # E. DRAFT GRID
    if draft_mode:
        can.setStrokeColor(colors.red)
        for i in range(0, 650, 50):
            can.line(i, 0, i, 850); can.drawString(i, 10, str(i))
        for j in range(0, 850, 50):
            can.line(0, j, 650, j); can.drawString(10, j, str(j))
            
    can.save()
    packet.seek(0)
    return PdfReader(packet)

# --- 3. INTERFACE ---
st.markdown("<h1>👑 JD GOLD HUB</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ PDF SETTINGS")
    pdf_font_size = st.slider("Adjust PDF Font Size", 6, 20, 10)
    draft_mode = st.checkbox("🛠️ Show Coordinate Grid")
    st.divider()
    st.write("Current Theme: **White & Gold**")

template_file = st.file_uploader("📥 UPLOAD MASTER DOCUMENT", type="pdf")

if template_file:
    reader = PdfReader(template_file)
    num_pages = len(reader.pages)
    st.info(f"System Ready: {num_pages} Pages Loaded.")

    all_page_data = []

    for i in range(num_pages):
        with st.expander(f"📄 PAGE {i+1} CONTROLS", expanded=(i==0)):
            c1, c2, c3 = st.columns(3)
            with c1:
                p_name = st.text_input(f"Name (P{i+1})", key=f"n{i}")
                p_ssn = st.text_input(f"SSN (P{i+1})", key=f"s{i}")
                p_dob = st.text_input(f"DOB (P{i+1})", key=f"d{i}")
            with c2:
                p_phone = st.text_input(f"Phone (P{i+1})", key=f"ph{i}")
                p_email = st.text_input(f"Email (P{i+1})", key=f"em{i}")
                p_crime = st.text_input(f"Crime (P{i+1})", key=f"cr{i}")
            with c3:
                p_addr = st.text_area(f"Address (P{i+1})", key=f"ad{i}", height=100)
            
            st.divider()
            col_img = st.columns(4)
            with col_img[0]: p_adv = st.text_input(f"Advocate (P{i+1})", key=f"an{i}")
            with col_img[1]: p_adv_id = st.text_input(f"Advocate ID (P{i+1})", key=f"ai{i}")
            with col_img[2]: img_l1 = st.file_uploader(f"Left Img (P{i+1})", key=f"il{i}")
            with col_img[3]: 
                img_r1 = st.file_uploader(f"Right Img 1 (P{i+1})", key=f"ir1{i}")
                img_r2 = st.file_uploader(f"Right Img 2 (P{i+1})", key=f"ir2{i}")
            
            all_page_data.append({
                "name": p_name, "ssn": p_ssn, "dob": p_dob, "phone": p_phone,
                "email": p_email, "crime": p_crime, "address": p_addr,
                "adv_name": p_adv, "adv_id": p_adv_id,
                "img_l1": img_l1, "img_r1": img_r1, "img_r2": img_r2
            })

    # --- 4. GENERATION ---
    st.divider()
    if st.button("⚜️ GENERATE FINAL GOLD PDF"):
        writer = PdfWriter()
        for i in range(num_pages):
            page = reader.pages[i]
            overlay = create_page_overlay(all_page_data[i], draft_mode, pdf_font_size)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

        final_pdf = io.BytesIO()
        writer.write(final_pdf)
        st.success("✅ Document Finalized.")
        st.download_button("📥 DOWNLOAD COMPLETED CASE FILE", final_pdf.getvalue(), "JD_GOLD_FINAL.pdf")
