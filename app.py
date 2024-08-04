import os
import re
from pypdf import PdfReader, PdfWriter

def sanitize_filename(filename):
    # 定义不能作为文件名的字符
    forbidden_chars = r'[\/:*?"<>|]'
    
    # 使用正则表达式替换这些字符为空字符串
    sanitized_filename = re.sub(forbidden_chars, '', filename)
    
    return sanitized_filename

def create_directory_structure(base_path, bookmarks):
    for bookmark in bookmarks:
        path = os.path.join(base_path, *bookmark['titles'])
        os.makedirs(path, exist_ok=True)

def extract_bookmarks(pdf_reader):
    
    def _extract(bookmarks, titles=[], ind=0):
        extracted = []
        for bookmark in bookmarks:
            # print(titles, ind)
            if isinstance(bookmark, list):
                extracted += _extract(bookmark, titles, ind+1)
            else:
                titles = titles[0:ind]
                titles.append(sanitize_filename(bookmark.title.strip()))
                extracted.append({'titles': titles, 'page': pdf_reader.get_destination_page_number(bookmark)})
        return extracted
    return _extract(pdf_reader.outline, [], 0)

def split_pdf_by_bookmarks(pdf_reader, output_dir, bookmarks):
    for i, bookmark in enumerate(bookmarks):
        output_pdf = PdfWriter()
        start_page = bookmark['page']  # Page numbers are 1-based in bookmarks, 0-based in PyPDF2
        if (start_page):
            if (i + 1) < len(bookmarks) and 'page' in bookmarks[i + 1] and bookmarks[i + 1]['page']:
                end_page = bookmarks[i + 1]['page']
            else:
                end_page = len(pdf_reader.pages)
            if (bookmark['page'] == end_page):
                end_page += 1
            
            print(bookmark['titles'], bookmark['page'], end_page)
            for page_num in range(start_page, end_page):
                output_pdf.add_page(pdf_reader.pages[page_num])

            output_path = os.path.join(output_dir, *bookmark['titles'], f"{bookmark['titles'][-1]}.pdf")
            with open(output_path, 'wb') as output_file:
                output_pdf.write(output_file)

def main(pdf_path, output_dir):
    pdf_reader = PdfReader(pdf_path)
    bookmarks = extract_bookmarks(pdf_reader)
    create_directory_structure(output_dir, bookmarks)
    split_pdf_by_bookmarks(pdf_reader, output_dir, bookmarks)

if __name__ == "__main__":
    pdf_path = "./input.pdf"
    output_dir = "./output"
    main(pdf_path, output_dir)
