import requests
from bs4 import BeautifulSoup
import json

HOST = 'https://www.avito.ru/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.60', 'accept': '*/*'}


def get_content(url):
    html = requests.get(url, headers=HEADERS)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all('div', class_='iva-item-list-2_PpT')
        data = read_db() # Читаем базу
        products = []
        for item in items:
            image = item.find('ul', class_='photo-slider-list-3Zt1Z').find('li')
            if image:
                image = image.get('data-marker').replace('slider-image/image-', '')
            else:
                image = 'https://static.avito.ru/@avito/bx-single-page-catalog/2.395.2/' \
                        'prod/web/resources/93ac49675b15.svg'
            item_id = item.get('data-item-id')
            if item_id in data["products"]:
                continue
            products.append({
                'id': item_id,
                'title': item.find('span', class_='title-root-395AQ').get_text(),
                'image': image,
                'price': item.find('span', class_='price-text-1HrJ_').get_text().replace('\xa0', ' '),
                'geo': item.find('div', class_='geo-root-1pUZ8').get_text(),
                'link': HOST + item.find('a', class_='link-link-39EVK').get('href')
            })
            if len(products) == 5:
                break
        record_to_db(products)
        return products
    else:
        print('Error')


def read_db():
    with open("db.json", "r") as jsonFile:
        data = json.load(jsonFile)
        jsonFile.close()
    return data


def record_to_db(new_item):
    new_id = [item["id"] for item in new_item]
    data = read_db()
    with open("db.json", "w") as jsonFile:
        data["products"] += new_id
        json.dump(data, jsonFile, indent=4)
        jsonFile.close()


# print(get_content('https://www.avito.ru/rostov-na-donu/audio_i_video?cd=1&s=104'))