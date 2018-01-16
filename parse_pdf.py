import re

import textract


def clean_line_numbers(text):
    return re.sub(r'\u202b\u202a\d+\u202c\u202c', '', text)


def clean_double_line_breaks(text):
    return re.sub(r'\n\n', '\n', text)


def extract_text(input, output):
    text = textract.process(input)
    decoded_text = text.decode()

    parsed_text = clean_line_numbers(decoded_text)
    parsed_text = clean_double_line_breaks(parsed_text)

    with open(output, 'w') as f:
        f.write(parsed_text)


if __name__ == '__main__':
    input = '/home/shaief/Downloads/9078426_14_01_2018.pdf'
    output = input.replace('pdf', 'txt')
    extract_text(input, output)
