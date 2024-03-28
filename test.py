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


link_list = ['/for-abiturients/vuz/programs/5692?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5986?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/51447?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5919?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5858?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5965?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5988?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5860?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5963?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5872?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5862?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5850?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/1155?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5873?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5868?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5932?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5882?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/13744?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5837?o=point&d=desc&_lt=r&ege_3_set=1&ege=1',
             '/for-abiturients/vuz/programs/5887?o=point&d=desc&_lt=r&ege_3_set=1&ege=1']

with pd.ExcelWriter('output_values.xlsx') as writer:
    for link in link_list:
        values_list = []
        url = f'https://www.ucheba.ru{link}'
        responce_text = make_request(url)
        soup = BeautifulSoup(responce_text, 'html.parser')
        section_tag_list = soup.find('div').find_all('section', class_="search-results-info-item")
        for section_tag in section_tag_list:
            values_dict = {}
            refer = section_tag.find('a').get('href')
            url_refer = f'https://www.ucheba.ru{refer}'
            responce_text = make_request(url_refer)
            soup = BeautifulSoup(responce_text, 'html.parser')
            values_dict['Направление'] = soup.find('div', class_='sc-baeece-7 iHNKNl').find('span',
                                                                                            class_='sc-f5d4cf80-0 iBBFyW').get_text()
            all_td_tag = soup.find('tbody', class_='sc-d6d6e896-0 hLChBQ').find_all('td', class_='sc-c71fa30f-0 eGNzLt')
            values_dict['Мест на бюджет'] = all_td_tag[2].get_text().split('/')[0]
            values_dict['Срок обучения'] = all_td_tag[5].get_text().split('/')[0]
            year_ball_tag = soup.find_all('div', class_="sc-9de6a9bb-2 gXYRAt")
            for tag in year_ball_tag:
                values_dict[f'Проходной балл в {tag.get_text()[0:4]}'] = tag.get_text()[4:8]
            values_list.append(values_dict)
        df = pd.DataFrame(values_list)
        df.to_excel(writer, sheet_name=f'Sheet', index=False)

