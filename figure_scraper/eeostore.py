from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import requests


class EeoStore(Website):
    base_folder = constants.FOLDER_EEOSTORE
    title = constants.WEBSITE_TITLE_EEOSTORE
    keywords = ["https://eeo.today/", "Eeo Store", "A3"]

    page_prefix = 'https://eeo.today'
    product_page_template = page_prefix + '/store/101/products/detail/%s'

    @classmethod
    def run(cls):
        cls.init()
        loop = True
        while loop:
            print('[INFO] %s Scraper' % cls.title)
            loop = cls.download_by_product_id()

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: https://eeo.today/store/101/products/detail/{product_id}')
        expr = input('Enter product IDs: ')
        if len(expr) == 0:
            return False
        product_ids = cls.get_sorted_page_numbers(expr)
        if len(product_ids) == 0:
            return True
        jan_choice = cls.get_use_jan_choice()
        use_jan = False
        if jan_choice == 1:
            use_jan = True

        today = cls.get_today_date()
        max_processes = min(constants.MAX_PROCESSES, len(product_ids))
        if max_processes <= 0:
            max_processes = 1
        with Pool(max_processes) as p:
            results = []
            for product_id in product_ids:
                result = p.apply_async(cls.process_product_page, (product_id, today, use_jan))
                results.append(result)
            for result in results:
                result.wait()
        return True

    @classmethod
    def process_product_page(cls, product_id, folder=None, use_jan=False):
        product_url = cls.product_page_template % str(product_id)
        try:
            soup = cls.get_soup(product_url)
            jan = product_id
            if use_jan:
                content = str(requests.get(product_url).content)
                keyword = '"product_code":"'
                index_1 = content.index(keyword)
                index_2 = content[index_1 + len(keyword):].index('"') + index_1 + len(keyword)
                jan = content[index_1 + len(keyword):index_2]
            images = soup.select('div.slide-item img')
            num_max_length = len(str(len(images)))
            for i in range(len(images)):
                image_url = cls.page_prefix + images[i]['src']
                if len(images) == 1:
                    image_name = jan + '.jpg'
                else:
                    image_name = '%s_%s.jpg' % (jan, str(i + 1).zfill(num_max_length))
                if folder:
                    image_name = folder + '/' + image_name
                cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
