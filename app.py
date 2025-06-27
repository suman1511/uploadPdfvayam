import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import os
import zipfile
import unicodedata

st.set_page_config(page_title="Certificate Generator", layout="centered")

st.title("🎓 Certificate Generator with Hindi Name Support")

uploaded_excel = st.file_uploader("📄 Upload Excel file with Name column", type=["xlsx"])
uploaded_template = st.file_uploader("🖼️ Upload Certificate Template (PNG)", type=["png"])
uploaded_font = st.file_uploader("🔤 Upload Hindi Font (TTF)", type=["ttf"])

if uploaded_excel and uploaded_template and uploaded_font:
    df = pd.read_excel(uploaded_excel)
    os.makedirs("output", exist_ok=True)

    font_path = "uploaded_font.ttf"
    template_path = "uploaded_template.png"
    with open(font_path, "wb") as f:
        f.write(uploaded_font.read())
    with open(template_path, "wb") as f:
        f.write(uploaded_template.read())

    font = ImageFont.truetype(font_path, 42)
    TEXT_COLOR = (191, 52, 49)
    TEXT_POSITION = (880, 480)  # adjust based on your template

    progress = st.progress(0)
    total = len(df)

    for index, row in df.iterrows():
        name = str(row["Name"]).strip()
        safe_name = unicodedata.normalize("NFC", name).replace(" ", "_")

        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        x = TEXT_POSITION[0] - text_width // 2
        y = TEXT_POSITION[1]

        draw.text((x, y), name, fill=TEXT_COLOR, font=font)

        temp_path = f"output/{index+1}_{safe_name}.png"
        img.save(temp_path)

        # Convert to PDF
        pdf = FPDF(unit="pt", format=img.size)
        pdf.add_page()
        pdf.image(temp_path, 0, 0)
        pdf.output(f"output/{index+1}_{safe_name}.pdf")
        os.remove(temp_path)

        progress.progress((index + 1) / total)

    # Zip all PDFs
    zip_path = "certificates.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for filename in os.listdir("output"):
            if filename.endswith(".pdf"):
                zipf.write(os.path.join("output", filename), arcname=filename)

    with open(zip_path, "rb") as f:
        st.success("🎉 Done! Download your ZIP file below.")
        st.download_button("📦 Download All Certificates (ZIP)", data=f, file_name="certificates.zip")
