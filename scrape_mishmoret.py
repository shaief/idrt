import os

from bs4 import BeautifulSoup
import requests

#from handle_data import insert_data_to_elasticsearch
from parse_pdf import extract_text

search_date = '01/01/2018'

base_url = 'http://www.justice.gov.il'

url = 'http://www.justice.gov.il/Units/mishmoret/Pages/muhzakim.aspx'


def download_pdf(url, destination):
    remote_pdf = requests.get(url)
    pdf_filename = remote_pdf.headers['Content-Disposition'].split('"')[1]
    local_pdf = os.path.join(destination, pdf_filename)
    with open(local_pdf, 'wb') as f:
        f.write(remote_pdf.content)
    return pdf_filename


def get_files_urls(a_href):
    return [a for a in a_href if 'OpenDocData' in a['href']]


def get_files(folder, a_href):
    pdf_a_href = get_files_urls(a_href)
    files = []

    for pdf in pdf_a_href:
        print(pdf['href'])
        pdf_url = base_url + pdf['href']
        filename = download_pdf(pdf_url, folder)
        files.append(filename)

    return files


def crawler(search_date):
    base_id = 'ctl00_m_g_c6628511_0779_423b_836b_1ab8b5cd8917_ctl00_'

    session = requests.Session()
    r = session.get(url)

    if r.status_code != 200:
        print('Could not get the relevant page...')
        r.raise_for_status()

    soup = BeautifulSoup(r.content, 'lxml')
    # searchTbl = soup.find_all(class_='searchTbl')
    medina = soup.find(id=f'{base_id}Ddl_Medina').findAll('option')
    countries = [(m.attrs['value'], m.contents[0]) for m in medina]
    dayanim = soup.find(id=f'{base_id}Ddl_DayanName').findAll('option')
    dayanim = [(d.attrs['value'], d.contents[0]) for d in dayanim]

    for country in countries[1:]:
        if country[0] == '6':
            print(f'************** {search_date} - {country} ***************')
            for dayan in dayanim:
                print(search_date, country, dayan)
                files, folder = crawl(session, r, soup, search_date, country, dayan)
                if dayan[0] == '0' and not files:
                    break

                if isinstance(files, list):
                    for f in files:
                        meta = {
                            'date': search_date,
                            'dayan': dayan[1],
                            'country': country[1],
                            'case_number': f.split('_')[0],
                            'filename': f,
                            'url': 'bbbbb.aaaa.com',
                        }
                        text = extract_text(os.path.join(folder, f))
                        # insert_data_to_elasticsearch(meta, text)


def crawl(session, r, soup, search_date, country, dayan):
    day, month, year = search_date.split('/')

    base_input = 'ctl00$m$g_c6628511_0779_423b_836b_1ab8b5cd8917$ctl00$'

    viewstate = soup.findAll("input",
                             {"type": "hidden",
                              "name": "__VIEWSTATE"})[0]['value']

    event_validation = soup.findAll(
        "input", {"type": "hidden",
                  "name": "__EVENTVALIDATION"})[0]['value']

    headers = {
        'Host': 'www.justice.gov.il',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': url,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
    }

    data = {
        'MSOWebPartPage_PostbackSource': '',
        'MSOTlPn_SelectedWpId': '',
        'MSOTlPn_View': '0',
        'MSOTlPn_ShowSettings': 'False',
        'MSOGallery_SelectedLibrary': '',
        'MSOGallery_FilterString': '',
        'MSOTlPn_Button': 'none',
        '__EVENTTARGET': f'{base_input}Btn_Search',
        '__VIEWSTATE': viewstate,
        'cmdSubmit': 'Submit',
        '__EVENTVALIDATION': event_validation,
        f'{base_input}Ddl_Medina': country[0],  # '0',
        f'{base_input}Ddl_DayanName': dayan[0],  # '0',
        f'{base_input}txt_idMuchzak': '',
        f'{base_input}FromDate$FromDateDate': search_date,
        f'{base_input}ToDate$ToDateDate': search_date,
    }

    response = session.post(
        'http://www.justice.gov.il/Units/mishmoret/Pages/muhzakim.aspx',
        headers=headers,
        data=data)

    # print(response.text)

    soup = BeautifulSoup(response.content, 'lxml')

    a_href = soup.find_all('a', href=True)
    # pages = [a for a in a_href if 'Page$' in a['href']]

    pdf_urls = get_files_urls(a_href)
    # print(pdf_urls)

    folder = os.path.join('files', f'{year:0>4}', f'{month:0>2}', f'{day:0>2}', f'{country[0]}')

    if dayan[0] == '0' and pdf_urls:
        os.makedirs(folder, exist_ok=True)
        return True, ''

    files = get_files(folder, a_href)

    return files, folder


if __name__ == '__main__':
    search_date = '10/01/2018'
    crawler(search_date)
