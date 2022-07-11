from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class Tapioca(Website):
    base_folder = constants.FOLDER_TAPIOCA
    title = constants.WEBSITE_TITLE_TAPIOCA
    keywords = ["https://tapioca.co.jp/", "Tapioca"]

    page_prefix = 'https://tapioca.co.jp'
    product_url_template = page_prefix + '/products/detail/%s'

    @classmethod
    def run(cls):
        cls.init()
        loop = True
        while loop:
            print('[INFO] %s Scraper' % cls.title)
            loop = cls.download_by_product_id()

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: https://tapioca.co.jp/products/detail/{product_id}')
        expr = input('Enter product IDs: ')
        if len(expr) == 0:
            return False
        product_ids = cls.get_sorted_page_numbers(expr)
        if len(product_ids) == 0:
            return True

        today = cls.get_today_date()
        if len(product_ids) == 1:
            cls.process_product_page(product_ids[0], today)
        else:
            max_processes = min(constants.MAX_PROCESSES, len(product_ids))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for product_id in product_ids:
                    result = p.apply_async(cls.process_product_page, (product_id, today))
                    results.append(result)
                for result in results:
                    result.wait()
        return True

    @classmethod
    def process_product_page(cls, product_id, folder=None):
        product_url = cls.product_url_template % product_id
        image_name_prefix = product_id
        try:
            soup = cls.get_soup(product_url)
            images = soup.select('#detail_image_box__slides img[src]')
            if len(images) == 0:
                print('[ERROR] Product ID %s not found.' % product_id)
                return
            elif len(images) == 1:
                image_url = cls.page_prefix + images[0]['src']
                image_name = image_name_prefix + '.jpg'
                if folder:
                    image_name = folder + '/' + image_name
                cls.download_image(image_url, image_name)
            else:
                num_max_length = len(str(len(images)))
                for i in range(len(images)):
                    image_url = cls.page_prefix + images[i]['src']
                    image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    if folder:
                        image_name = folder + '/' + image_name
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
