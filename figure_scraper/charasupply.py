from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class CharaSupply(Website):
    base_folder = constants.FOLDER_CHARASUPPLY
    title = constants.WEBSITE_TITLE_CHARASUPPLY
    keywords = ["http://chara-supply.com/", "Chara Supply", "Movic"]

    page_prefix = 'http://chara-supply.com/'
    image_url_template = page_prefix + '/uploads/sleeve%s%s.jpg'

    @classmethod
    def run(cls):
        cls.init()
        loop = True
        while loop:
            print('[INFO] %s Scraper' % cls.title)
            loop = cls.download_by_product_id()

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: http://chara-supply.com/product/sleeve{prefix}{product_id}/')
        prefix = input('Input prefix (e.g. mt): ')
        if len(prefix) == 0:
            return False
        expr = input('Enter product IDs: ')
        if len(expr) == 0:
            return True
        product_ids = cls.get_sorted_page_numbers(expr)
        if len(product_ids) == 0:
            return True

        today = cls.get_today_date()
        max_processes = min(cls.max_processes, len(product_ids))
        if max_processes <= 0:
            max_processes = 1
        with Pool(max_processes) as p:
            results = []
            for product_id in product_ids:
                result = p.apply_async(cls.process_product_page, (prefix, product_id, today))
                results.append(result)
            for result in results:
                result.wait()
        return True

    @classmethod
    def process_product_page(cls, prefix, product_id, folder=None):
        image_url = cls.image_url_template % (prefix, str(product_id).zfill(3))
        image_name = image_url.split('/')[-1]
        if folder:
            image_name = folder + '/' + image_name
        try:
            cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % image_url)
            print(e)
