import re

import textract


def clean_line_numbers(text):
    return re.sub(r'\u202b\u202a\d+\u202c\u202c', '', text)


def clean_double_line_breaks(text):
    return re.sub(r'\n\n', '\n', text)


def extract_text(input_file):
    text = textract.process(input_file)
    # trying to use tesseract for better results:
    # text = textract.process(input_file, method='tesseract', language='heb')
    decoded_text = text.decode()

    parsed_text = clean_line_numbers(decoded_text)
    parsed_text = clean_double_line_breaks(parsed_text)

    return parsed_text


def save_text_to_file(text, output_file):
    with open(output_file, 'w') as f:
        f.write(text)
        print(output_file, ' saved!')


def extract_and_save(input_file, output_file):
    text = extract_text(input_file)
    save_text_to_file(text, output_file)



if __name__ == '__main__':
    input_file = 'files/1481827_05_01_2014.pdf'
    output_file = input_file.replace('pdf', 'txt')
    text = extract_text(input_file)
    save_text_to_file(text, output_file)
