import os
from pypdf import PdfWriter

docs_dir = r"c:\Users\sapna\Downloads\the-hive\docs"
output_file = os.path.join(docs_dir, "The_Hive_Master_Report.pdf")

pdfs_to_merge = [
    "The_Hive_Whitepaper.pdf",
    "The_Hive_Comprehensive_Feature_Report.pdf",
    "The_Hive_Technical_Report.pdf",
    "The_Hive_Pipeline_and_Architecture_Report.pdf"
]

merger = PdfWriter()

for pdf in pdfs_to_merge:
    file_path = os.path.join(docs_dir, pdf)
    if os.path.exists(file_path):
        print(f"Adding: {pdf}")
        merger.append(file_path)
    else:
        print(f"File not found: {file_path}")

merger.write(output_file)
merger.close()

print(f"Successfully combined into: {output_file}")
