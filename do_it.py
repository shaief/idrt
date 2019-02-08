from parse_pdf import extract_text

from scrape_mishmoret import crawler

files = crawler('01/01/2018')

for input in files:
    output = input.replace('pdf', 'txt')
    extract_text(input, output)
