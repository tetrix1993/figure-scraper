from figure_scraper.website import Website
import figure_scraper.constants as constants
import json
from multiprocessing import Pool


class Aucoop(Website):
    base_folder = constants.FOLDER_AUCOOP
    title = constants.WEBSITE_TITLE_AUCOOP
    keywords = ["https://au-coop.jp/", "Aucoop", "Anime University COOP"]

    page_prefix = 'https://au-coop.jp'
    product_url_prefix = page_prefix + '/collections/'
    maximum_processes = constants.MAX_PROCESSES

    @classmethod
    def run(cls):
        cls.init()
        loop = True
        while loop:
            print('[INFO] %s Scraper' % cls.title)
            loop = cls.download_by_product_id()

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: https://au-coop.jp/collections/{pattern}')
        pattern = input('Enter pattern: ')
        if len(pattern) == 0:
            return False
        expr = input('Enter product IDs: ')
        if len(expr) == 0:
            return True
        product_ids = cls.get_sorted_page_numbers(expr)
        if len(product_ids) == 0:
            return True

        for i in range(len(product_ids)):
            product_ids[i] = pattern % str(product_ids[i]).zfill(4)

        use_jan = False
        while True:
            print('Select name of file to save as: ')
            print('1: Use Product ID as name')
            print('2: Use JAN code as name if possible')
            print('0: Return')

            try:
                choice = int(input('Enter choice: ').strip())
                if choice == 1:
                    break
                elif choice == 2:
                    use_jan = True
                    break
                elif choice == 0:
                    return True
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid choice.')

        today = cls.get_today_date()
        if len(product_ids) == 1:
            cls.process_product_page(product_ids[0], use_jan, today)
        else:
            max_processes = min(cls.maximum_processes, len(product_ids))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for product_id in product_ids:
                    result = p.apply_async(cls.process_product_page, (product_id, use_jan, today))
                    results.append(result)
                for result in results:
                    result.wait()
        return True

    @classmethod
    def process_product_page(cls, product_id, use_jan=False, folder=None):
        product_url = cls.product_url_prefix + product_id
        try:
            soup = cls.get_soup(product_url)
            script_tag = soup.select('script[data-product-json]')
            if len(script_tag) == 0:
                return
            json_obj = json.loads(script_tag[0].string)
            if 'product' in json_obj:
                product = json_obj['product']
                if use_jan and 'variants' in product and len(product['variants']) > 0 and 'barcode' in product['variants'][0]:
                    image_name_prefix = product['variants'][0]['barcode']
                else:
                    image_name_prefix = product_id
                if 'images' in product:
                    for i in range(len(product['images'])):
                        image_url = 'https:' + product['images'][i].split('?')[0]
                        if len(product['images']) > 1:
                            if len(product['images']) > 9:
                                image_name = image_name_prefix + '_' + str(i + 1).zfill(2)
                            else:
                                image_name = image_name_prefix + '_' + str(i + 1)
                        else:
                            image_name = image_name_prefix
                        if folder:
                            image_name = folder + '/' + image_name
                        cls.download_image(image_url, image_name + '.webp')
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
