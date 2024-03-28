import lxml
import pandas as pd
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


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
    responce_text = make_request(url)
    soup = BeautifulSoup(responce_text, 'html.parser')
    div_tag = soup.find('div', class_="search-results")
    tag_list = div_tag.find_all('a', class_='search-results-more-info js-search-results-more-info js_show_all_programs')
    for tag in tag_list:
        link_list.append(tag.get('data-programs-url'))
    return link_list


url_list = ['https://www.ucheba.ru/for-abiturients/vuz?o=point&d=desc&_lt=r&ege_3_set=1&ege=1&s=20',
            'https://www.ucheba.ru/for-abiturients/vuz?o=point&d=desc&s=40&_lt=r&ege_3_set=1&ege=1',
            'https://www.ucheba.ru/for-abiturients/vuz?o=point&d=desc&s=60&_lt=r&ege_3_set=1&ege=1']

page = 1

for url in url_list:
    page += 1
    with pd.ExcelWriter(f'output_values_{page}.xlsx') as writer:

        for link in get_links(url):

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

                if soup.find('div', class_='sc-f5d4cf80-0 eWMPFe'):
                    name = soup.find('div', class_='sc-f5d4cf80-0 eWMPFe').get_text()
                    print(name)

                if soup.find('div', class_='sc-baeece-7 iHNKNl'):
                    values_dict['Направление'] = soup.find('div', class_='sc-baeece-7 iHNKNl').find('span', class_='sc-f5d4cf80-0 iBBFyW').get_text()
                else:
                    values_dict['Направление'] = '-'

                if soup.find('tbody', class_='sc-d6d6e896-0 hLChBQ'):
                    all_td_tag = soup.find('tbody', class_='sc-d6d6e896-0 hLChBQ').find_all('td', class_='sc-c71fa30f-0 eGNzLt')
                    values_dict['Мест на бюджет'] = all_td_tag[2].get_text().split('/')[0]
                    values_dict['Срок обучения'] = all_td_tag[5].get_text().split('/')[0]

                if soup.find_all('div', class_="sc-9de6a9bb-2 gXYRAt"):
                    year_ball_tag = soup.find_all('div', class_="sc-9de6a9bb-2 gXYRAt")

                    for tag in year_ball_tag:
                        values_dict[f'Проходной балл в {tag.get_text()[0:4]}'] = tag.get_text()[4:8]

                    values_list.append(values_dict)

            df = pd.DataFrame(values_list)
            df.to_excel(writer, sheet_name=f'{name}', index=False)

