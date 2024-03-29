import openpyxl
import pandas as pd
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import lxml

def make_request(url):
    session = requests.Session()
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        responce = session.get(url, headers=headers)
        responce.encoding = 'utf-8'
        if responce.status_code == 200:
            return responce.text
        else:
            return f"Ошибка: получен статус-код {responce.status_code}"
    except Exception as e:
        return f"Произошла ошибка: {e}"


def get_links(url):
    link_list = []
    university_list = []
    responce_text = make_request(url)
    soup = BeautifulSoup(responce_text, 'lxml')
    div_tag = soup.find('div', class_="search-results")
    tag_list_university = div_tag.find_all('h2', class_='search-results-title')
    tag_list_link = div_tag.find_all('a', class_='search-results-more-info js-search-results-more-info js_show_all_programs')
    for tag in tag_list_link:
        link_list.append(tag.get('data-programs-url'))
    for tag in tag_list_university:
        university_list.append(tag.find('a').get_text())
    return link_list, university_list


def get_direction(text):
    start_index = text.find('«') + 1
    end_index = text.find('»')
    text_name = text[start_index:end_index]
    return text_name


def get_number(text):
    text_code = '-'
    if text.find('код') != -1:
        text_code = text.split('код')[1].strip()
    return text_code


url_list = ['https://www.ucheba.ru/for-abiturients/vuz?o=point&d=desc&_lt=r&ege_9_set=1&ege=1']
page = 1

for url in url_list:
    page += 1
    with pd.ExcelWriter(f'Биология_страница_куча_{page}.xlsx') as writer:

        link_list, university_list = get_links(url)
        for i in range(len(link_list)):

            link = link_list[i]
            university = university_list[i]

            name = university

            values_list = []

            url_link = f'https://www.ucheba.ru{link}'
            responce_text = make_request(url_link)
            soup = BeautifulSoup(responce_text, 'html.parser')
            section_tag_list = soup.find('div').find_all('section', class_="search-results-info-item")

            for section_tag in section_tag_list:

                values_dict = {}

                refer = section_tag.find('a').get('href')

                url_refer = f'https://www.ucheba.ru{refer}'
                responce_text = make_request(url_refer)
                soup = BeautifulSoup(responce_text, 'html.parser')

                values_dict['ВУЗ'] = name

                if soup.find('div', class_='sc-f5d4cf80-0 eWMPFe'):
                    name_department = soup.find('div', class_='sc-f5d4cf80-0 eWMPFe').get_text()
                    values_dict['Факультет'] = name_department

                if soup.find('div', class_='sc-f5d4cf80-0 jUrkjv'):
                    text = soup.find('div', class_='sc-f5d4cf80-0 jUrkjv').get_text()
                    values_dict['Направление'] = get_direction(text)
                    values_dict['Код направления'] = get_number(text)

                if soup.find('div', class_='sc-baeece-7 iHNKNl'):
                    values_dict['Программа'] = soup.find('div', class_='sc-baeece-7 iHNKNl').find('span',
                                                                                                  class_='sc-f5d4cf80-0 iBBFyW').get_text()
                else:
                    values_dict['Программа'] = '-'

                if soup.find('tbody', class_='sc-d6d6e896-0 hLChBQ'):
                    all_td_tag = soup.find('tbody', class_='sc-d6d6e896-0 hLChBQ').find_all('td',
                                                                                            class_='sc-c71fa30f-0 eGNzLt')
                    values_dict['Мест на бюджет'] = all_td_tag[2].get_text().split('/')[0]
                    values_dict['Срок обучения'] = all_td_tag[5].get_text().split('/')[0]

                if soup.find_all('div', class_="sc-9de6a9bb-2 gXYRAt"):
                    year_ball_tag = soup.find_all('div', class_="sc-9de6a9bb-2 gXYRAt")

                    for tag in year_ball_tag:
                        values_dict[f'Проходной балл в {tag.get_text()[0:4]}'] = tag.get_text()[4:8]

                else:
                    values_dict['Проходной балл в 2023'] = all_td_tag[1].get_text().split('/')[0]

                values_list.append(values_dict)

            df = pd.DataFrame(values_list)
            df.to_excel(writer, sheet_name=f'{name[:31]}', index=False)
