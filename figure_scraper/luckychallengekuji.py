from figure_scraper.website import Website
import figure_scraper.constants as constants
import requests
import json


class LuckyChallengeKuji(Website):
    base_folder = constants.FOLDER_LUCKYCHALLENGEKUJI
    title = constants.WEBSITE_TITLE_LUCKYCHALLENGEKUJI
    keywords = ["https://luckychallenge-kuji.com/"]

    product_url_template = 'https://luckychallenge-kuji.com/lotteries/%s'
    api_key_url = 'https://api1.api-kujilab.com/system'
    api_url_template = '%s/lottery/%s/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter page name: ')
            if len(expr) == 0:
                return
            # cls.process_product_page(expr)
            cls.process_page_by_api(expr)

    @classmethod
    def process_page_by_api(cls, page):
        try:
            headers = constants.HTTP_HEADER_USER_AGENT
            headers['Origin'] = 'https://luckychallenge-kuji.com/'
            r = requests.get(cls.api_key_url, headers=headers)
            api_key_obj = json.loads(r.content)
            tenant_id = api_key_obj['tenantId']
            api_origin_name = api_key_obj['apiOriginName']
            api_key = api_key_obj['apikey']
        except Exception as e:
            print(f'[ERROR] Error in calling get API key url: {e}')
            return

        try:
            headers = constants.HTTP_HEADER_USER_AGENT
            headers['x_dtw_signature'] = api_key
            api_url = cls.api_url_template % (api_origin_name, tenant_id, page)
            r = requests.get(api_url, headers=headers)
            page_obj = json.loads(r.content)
            image_list = []
            for prize in page_obj[0]['prizeDefinitions']:
                rank = prize['rank']
                for variation in prize['prizeVariationDefinitions']:
                    code = str(variation['code'])
                    image_url = variation['itemImage']
                    img_ext = image_url.split('?')[0].split('.')[-1]
                    image_name = rank + '-' + code + '.' + img_ext
                    image_list.append({'name': image_name, 'url': image_url})
            for benefit in page_obj[0]['benefits']:
                for variation in benefit['benefitVariations']:
                    image_url = variation['itemImage']
                    img_ext = image_url.split('?')[0].split('.')[-1]
                    image_name = 'benefit' + '_' + str(variation['benefitId']) + '_' + str(variation['code'])\
                                 + '.' + img_ext
                    image_list.append({'name': image_name, 'url': image_url})
            if len(image_list) == 0:
                print(f'[ERROR] No images found.')
                return
            for image in image_list:
                cls.download_image(image['url'], page + '/' + image['name'])
        except Exception as e:
            print(f'[ERROR] Error in calling get API page url: {e}')

    @classmethod
    def process_product_page(cls, page):
        page_url = cls.product_url_template % page
        image_list = []
        try:
            soup = cls.get_soup(page_url)

            sections = soup.select('.lotteries_container section')
            for section in sections:
                if section.has_attr('class') and len(section['class']) > 0:
                    class_name = section['class'][0]
                    images = section.select('img[src], img[data-src]')
                    for i in range(len(images)):
                        if images[i].has_attr('data-src'):
                            image_url = images[i]['data-src']
                        else:
                            image_url = images[i]['src']
                        image_name = class_name + '_' + str(i + 1).zfill(2) + '.jpg'
                        image_list.append({'name': image_name, 'url': image_url})

            rank_banners = soup.select('section.area')
            for banner in rank_banners:
                if not banner.has_attr('id'):
                    continue
                id_name = banner['id']
                images = banner.select('img[data-src]')
                for i in range(len(images)):
                    image_name = id_name + '_' + str(i + 1).zfill(2) + '.jpg'
                    image_url = images[i]['data-src']
                    image_list.append({'name': image_name, 'url': image_url})

            if len(image_list) == 0:
                print(f'[ERROR] {page_url} does not exists.')
                return
            for image in image_list:
                cls.download_image(image['url'], page + '/' + image['name'])
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')
