from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time


class TeamEc(Website):
    base_folder = constants.FOLDER_TEAMEC
    title = constants.WEBSITE_TITLE_TEAMEC
    keywords = ["https://team-ec.jp/"]

    product_url_template = 'https://team-ec.jp/product/%s'

    @classmethod
    def run(cls):
        cls.init()
        cls.process_by_product_id()

    @classmethod
    def process_by_product_id(cls):
        print('[INFO] Product Page URL is in the format: https://team-ec.jp/product/{id}')
        expr = input('Enter expression (Product IDs): ').strip()
        if len(expr) == 0:
            return
        unfiltered_numbers = cls.get_numbers_from_expression(expr)
        today = cls.get_today_date()
        numbers = []
        for number in unfiltered_numbers:
            product_id = str(number)
            filepath = today + '/' + product_id
            if cls.is_image_exists(filepath, has_extension=True) \
                    or cls.is_image_exists(filepath + '_1', has_extension=True) \
                    or cls.is_image_exists(filepath + '_01', has_extension=True):
                print(f'[INFO] Product ID {product_id} already downloaded')
                continue
            numbers.append(number)

        if len(numbers) == 1:
            cls.process_product_page(numbers[0], today)
        elif len(numbers) > 1:
            max_processes = min(constants.MAX_PROCESSES, len(numbers))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for number in numbers:
                    result = p.apply_async(cls.process_product_page, (number, today))
                    results.append(result)
                    time.sleep(constants.PROCESS_SPAWN_DELAY)
                for result in results:
                    result.wait()

    @classmethod
    def process_product_page(cls, product_id, folder=None):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url, verify=False)
            images = soup.select('img.products-main-image[src]')
            image_urls = set()
            for image in images:
                image_urls.add(image['src'].split('?')[0])
            if len(image_urls) > 0:
                num_max_length = len(str(len(image_urls)))
                i = 0
                for image_url in image_urls:
                    i += 1
                    if len(image_urls) == 1:
                        image_name = id_ + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (id_, str(i).zfill(num_max_length))
                    if folder:
                        image_name = folder + '/' + image_name
                    cls.download_image(image_url, image_name)
            else:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return

        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
