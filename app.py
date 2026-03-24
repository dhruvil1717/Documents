import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import io

# --- 1. CONFIG & ANIMATED THEME ---
st.set_page_config(page_title="JD GOLD HUB", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    h1 { color: #D4AF37; text-align: center; font-family: 'serif'; }
    /* Animated Expander */
    .streamlit-expanderHeader { background-color: #1A1A1A !important; color: #D4AF37 !important; border: 1px solid #D4AF37 !important; border-radius: 5px; }
    .stButton>button { background: linear-gradient(45deg, #D4AF37, #F9E27D); color: black; font-weight: bold; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE PRECISION STAMPING ENGINE ---
def create_page_overlay(data, draft_mode):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 10)
    can.setFillColor(colors.black)

    # A. TEXT DATA (Right Side)
    can.drawString(420, 750, f"NAME: {data['name']}")
    can.drawString(420, 735, f"SSN: {data['ssn']}")

    # B. ADVOCATE DATA (Lower Middle Left)
    can.drawString(50, 300, f"ADVOCATE: {data['adv_name']}")
    can.drawString(50, 285, f"ID NO: {data['adv_id']}")

    # C. IMAGES (Lower Middle)
    # Right Side 1 & 2
    if data['img_r1']:
        can.drawImage(ImageReader(data['img_r1']), 400, 250, width=100, height=70)
    if data['img_r2']:
        can.drawImage(ImageReader(data['img_r2']), 510, 250, width=100, height=70)
    # Left Side 1
    if data['img_l1']:
        can.drawImage(ImageReader(data['img_l1']), 50, 200, width=100, height=70)

    # DRAFT GRID
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
st.markdown("<h1>👑 JD GOLD HUB: SMART PORTAL</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ GLOBAL SETTINGS")
    draft_mode = st.checkbox("🛠️ Show Coordinate Grid")

template_file = st.file_uploader("📥 UPLOAD MASTER DOCUMENT (Multi-page)", type="pdf")

if template_file:
    reader = PdfReader(template_file)
    num_pages = len(reader.pages)
    st.success(f"Document Loaded: {num_pages} Pages found.")

    # STORAGE FOR PAGE-SPECIFIC DATA
    all_page_data = []

    st.markdown("### ✍️ INDIVIDUAL PAGE EDITING")
    
    for i in range(num_pages):
        with st.expander(f"📄 PAGE {i+1} SETTINGS", expanded=(i==0)):
            col1, col2 = st.columns(2)
            with col1:
                p_name = st.text_input(f"Client Name (P{i+1})", key=f"n{i}")
                p_ssn = st.text_input(f"SSN (P{i+1})", key=f"s{i}")
                p_adv = st.text_input(f"Advocate Name (P{i+1})", key=f"an{i}")
                p_adv_id = st.text_input(f"Advocate ID (P{i+1})", key=f"ai{i}")
            with col2:
                img_l1 = st.file_uploader(f"Left Image (P{i+1})", type=['jpg','png'], key=f"il{i}")
                img_r1 = st.file_uploader(f"Right Image 1 (P{i+1})", type=['jpg','png'], key=f"ir1{i}")
                img_r2 = st.file_uploader(f"Right Image 2 (P{i+1})", type=['jpg','png'], key=f"ir2{i}")
            
            all_page_data.append({
                "name": p_name, "ssn": p_ssn, "adv_name": p_adv, "adv_id": p_adv_id,
                "img_l1": img_l1, "img_r1": img_r1, "img_r2": img_r2
            })

    # --- 4. GENERATION ---
    st.divider()
    if st.button("⚜️ GENERATE FULL COMPOSITE DOCUMENT"):
        writer = PdfWriter()
        
        for i in range(num_pages):
            page = reader.pages[i]
            # Create a unique overlay for this specific page
            overlay = create_page_overlay(all_page_data[i], draft_mode)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

        final_pdf = io.BytesIO()
        writer.write(final_pdf)
        st.balloons()
        st.download_button("📥 DOWNLOAD COMPLETED CASE FILE", final_pdf.getvalue(), "JD_GOLD_FINAL.pdf")
