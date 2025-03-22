import os
from pdfminer.high_level import extract_text

# Directory containing the PDFs
pdf_dir = 'papers'
# Output file path
output_file = 'extracted_papers.txt'

# Get all PDF files from the directory
pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]

# Process each PDF and write to output file
with open(output_file, 'w', encoding='utf-8') as outfile:
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f'Processing: {pdf_file}')
        
        try:
            # Extract text from the PDF
            text = extract_text(pdf_path)
            
            # Write a header for this paper
            outfile.write(f'\n\n{"="*80}\n')
            outfile.write(f'Content from: {pdf_file}\n')
            outfile.write(f'{"="*80}\n\n')
            
            # Write the extracted text
            outfile.write(text)
            
        except Exception as e:
            print(f'Error processing {pdf_file}: {str(e)}')

print('\nText extraction complete! Check extracted_papers.txt for the results.') 