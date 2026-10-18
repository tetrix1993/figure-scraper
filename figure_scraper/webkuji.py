from figure_scraper.website import Website
import figure_scraper.constants as constants


class WebKuji(Website):
    base_folder = constants.FOLDER_WEBKUJI
    title = constants.WEBSITE_TITLE_WEBKUJI
    keywords = ["web-kuji.jp", 'web kuji', 'webkuji']

    product_url_prefix = 'https://web-kuji.jp/lotteries/'

    system_api = 'https://api1.api-kujilab.com/system'
    origin = 'https://web-kuji.jp'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter page (https://web-kuji.jp/lotteries/{page}): ')
            if len(expr) == 0:
                return
            cls.process_product_page(expr)

    @classmethod
    def process_product_page(cls, page):
        page_url = cls.product_url_prefix + page
        try:
            api_system_json = cls.get_json(cls.system_api, headers={'origin': cls.origin})
            if 'error' in api_system_json:
                print(f'[ERROR] Error in processing {page_url}')
                return
            if 'tenantId' not in api_system_json:
                print(f'[ERROR] Error in processing {page_url} - Cannot retrieve tenantId')
                return
            if 'apiOriginName' not in api_system_json:
                print(f'[ERROR] Error in processing {page_url} - Cannot retrieve apiOriginName')
                return
            if 'apikey' not in api_system_json:
                print(f'[ERROR] Error in processing {page_url} - Cannot retrieve apiKey')
                return
            tenant_id = api_system_json['tenantId']
            api_origin_name = api_system_json['apiOriginName']
            api_key = api_system_json['apikey']

            api_url = f'{api_origin_name}/lottery/{tenant_id}/{page}'
            obj = cls.get_json(api_url, headers={'x_dtw_signature': api_key,
                                                 'origin': cls.origin})

            if len(obj) > 0:
                item = obj[0]
                images = []
                # Banner
                if 'mainImage' in item:
                    image_ext = item['mainImage'].split('.')[-1]
                    images.append(('mainImage.' + image_ext, item['mainImage']))

                # Prizes
                if 'prizeDefinitions' in item:
                    for prize_def in item['prizeDefinitions']:
                        if 'prizeVariationDefinitions' not in prize_def:
                            continue
                        rank = prize_def['rank'] if 'rank' in prize_def else ''
                        for prize in prize_def['prizeVariationDefinitions']:
                            if 'itemImage' in prize:
                                code = prize['code'] if 'code' in prize else ''
                                if len(rank) == 0 or len(code) == 0:
                                    image_name = prize['itemImage'].split('/')[-1]
                                else:
                                    image_ext = prize['itemImage'].split('.')[-1]
                                    image_name = rank + '-' + code.zfill(2) + '.' + image_ext
                                images.append((image_name, prize['itemImage']))

                # Benefits
                if 'benefits' in item:
                    for benefit in item['benefits']:
                        if 'benefitVariations' not in benefit:
                            continue
                        for benefit_var in benefit['benefitVariations']:
                            if 'itemImage' not in benefit_var:
                                continue
                            image_name = benefit_var['itemImage'].split('/')[-1]
                            images.append((image_name, benefit_var['itemImage']))

                # Last Prize
                if 'prizeStoryImages' in item:
                    for i in range(len(item['prizeStoryImages'])):
                        prize_story = item['prizeStoryImages'][i]
                        if 'image' not in prize_story:
                            continue
                        image_url = prize_story['image']
                        image_ext = image_url.split('.')[-1]
                        images.append((f'prizestory{i + 1}.{image_ext}', image_url))
                for image in images:
                    image_url = image[1]
                    image_name = image[0]
                    cls.download_image(image_url, page + '/' + image_name)
            else:
                print(f'[ERROR] Error in processing {page_url} - API response returns empty object')
                return
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')
