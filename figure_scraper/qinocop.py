from figure_scraper.website import Website
import figure_scraper.constants as constants
import json


class Qinocop(Website):
    base_folder = constants.FOLDER_QINOCOP
    title = constants.WEBSITE_TITLE_QINOCOP
    max_processes = 1
    keywords = ["https://qinocop.com/"]

    product_url_template = 'https://qinocop.com/pages/%s'

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        cls.process_by_page_id()

    @classmethod
    def process_by_page_id(cls):
        print('[INFO] Product Page URL is in the format: https://qinocop.com/pages/{id}')
        page = input('Enter Page ID: ').strip()
        if len(page) == 0:
            return
        today = cls.get_today_date()

        use_jan = False
        is_scan = False
        while True:
            print('Select name of file to save as: ')
            print('1: Use image name as name')
            print('2: Use JAN code as name if possible')
            # print('3: Scan for JAN code instead of downloading images')
            print('0: Return')

            try:
                choice = int(input('Enter choice: ').strip())
                if choice == 1:
                    break
                elif choice == 2:
                    use_jan = True
                    break
                # elif choice == 3:
                #    is_scan = True
                #    break
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid choice.')

        product_url = cls.product_url_template % page
        try:
            soup = cls.get_soup(product_url)
            a_tags = soup.select('.card__content h3.h5 a[href]')
            for a_tag in a_tags:
                page_url = 'https://qinocop.com' + a_tag['href']
                cls.process_product_page(page_url, page, use_jan)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def process_product_page(cls, page_url, folder=None, use_jan=False):
        try:
            soup = cls.get_soup(page_url, verify=False)
            json_obj = cls.get_product_json(soup)
            if json_obj is None:
                return
            if 'hasVariant' in json_obj:
                for item in json_obj['hasVariant']:
                    cls.process_download_image(item, folder, use_jan)
            else:
                cls.process_download_image(json_obj, folder, use_jan)
        except Exception as e:
            print('[ERROR] Error in processing %s' % page_url)
            print(e)

    @classmethod
    def process_download_image(cls, item_json, folder=None, use_jan=False):
        if 'image' not in item_json:
            return
        image_url = item_json['image']
        img_name = image_url.split('/')[-1].split('?')[0]
        if len(img_name) == 0:
            return
        image_name = img_name
        image_ext = image_name.split('.')[-1]
        if use_jan and 'gtin' in item_json:
            image_name = item_json['gtin'] + '.' + image_ext
        if len(img_name) == 0:
            image_name = img_name
        if folder:
            image_name = folder + '/' + image_name
        cls.download_image(image_url, image_name)

    @staticmethod
    def get_product_json(soup):
        try:
            script_tag = soup.select('script[type="application/ld+json"]')
            if len(script_tag) == 0:
                return
            for s in script_tag:
                json_obj = json.loads(s.string)
                if '@type' in json_obj:
                    if json_obj['@type'] == 'ProductGroup' or json_obj['@type'] == 'Product':
                        return json_obj
            return None
        except:
            return None

