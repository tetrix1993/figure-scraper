from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time


class Kotobukiya(Website):
    base_folder = constants.FOLDER_KOTOBUKIYA
    title = constants.WEBSITE_TITLE_KOTOBUKIYA
    keywords = ["https://www.kotobukiya.co.jp"]

    page_prefix = 'https://www.kotobukiya.co.jp'
    product_url_template = page_prefix + '/product/product-%s/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter expression (Product IDs): ').strip()
            if len(expr) == 0:
                return
            unfiltered_numbers = cls.get_numbers_from_expression(expr)
            numbers = []
            for number in unfiltered_numbers:
                product_id = str(number).zfill(10)
                if cls.is_image_exists(product_id, has_extension=True) \
                        or cls.is_image_exists(product_id + '_1', has_extension=True) \
                        or cls.is_image_exists(product_id + '_01', has_extension=True):
                    print(f'[INFO] Product ID {product_id} already downloaded')
                    continue
                numbers.append(number)
            if len(numbers) == 1:
                cls.process_product_page(numbers[0])
            elif len(numbers) > 1:
                max_processes = min(cls.max_processes, len(numbers))
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for number in numbers:
                        result = p.apply_async(cls.process_product_page, (number,))
                        results.append(result)
                        time.sleep(constants.PROCESS_SPAWN_DELAY)
                    for result in results:
                        result.wait()

    @classmethod
    def process_product_page(cls, product_id):
        id_ = str(product_id).zfill(10)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url)
            lis = soup.find_all('li', class_='slideshow-item')
            if len(lis) == 0:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return
            num_max_length = len(str(len(lis)))
            for i in range(len(lis)):
                a_tag = lis[i].find('a')
                if a_tag and a_tag.has_attr('href'):
                    image_url = cls.clear_resize_in_url(cls.page_prefix + a_tag['href'])
                    if len(lis) == 1:
                        image_name = id_ + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (id_, str(i + 1).zfill(num_max_length))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
