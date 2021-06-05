from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time


class HobbyStock(Website):
    base_folder = constants.FOLDER_HOBBYSTOCK
    title = constants.WEBSITE_TITLE_HOBBYSTOCK
    keywords = ["http://www.hobbystock.jp/"]

    product_url_template = 'http://www.hobbystock.jp/item/view/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Product Page URL is in the format: http://www.hobbystock.jp/item/view/{prefix}-{id}')
            prefix = input('Enter prefix (e.g. hso-ccg): ').strip().lower()
            if len(prefix) == 0:
                return
            expr = input('Enter expression (Product IDs): ').strip()
            if len(expr) == 0:
                continue
            unfiltered_numbers = cls.get_numbers_from_expression(expr)
            today = cls.get_today_date()
            numbers = []
            for number in unfiltered_numbers:
                product_id = prefix + '-' + str(number).zfill(8)
                filepath = today + '/' + product_id
                if cls.is_image_exists(filepath, has_extension=True) \
                        or cls.is_image_exists(filepath + '_1', has_extension=True) \
                        or cls.is_image_exists(filepath + '_01', has_extension=True):
                    print(f'[INFO] Product ID {product_id} already downloaded')
                    continue
                numbers.append(number)
            if len(numbers) == 1:
                cls.process_product_page(prefix, numbers[0], today)
            elif len(numbers) > 1:
                max_processes = min(constants.MAX_PROCESSES, len(numbers))
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for number in numbers:
                        result = p.apply_async(cls.process_product_page, (prefix, number, today))
                        results.append(result)
                        time.sleep(constants.PROCESS_SPAWN_DELAY)
                    for result in results:
                        result.wait()

    @classmethod
    def process_product_page(cls, prefix, product_id, folder=None):
        id_ = prefix + '-' + str(product_id).zfill(8)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url)
            div = soup.find('div', class_='imageList')
            if div:
                images = div.find_all('img')
                num_max_length = len(str(len(images)))
                for i in range(len(images)):
                    if images[i].has_attr('src'):
                        image_url = images[i]['src']
                        if len(images) == 1:
                            image_name = id_ + '.jpg'
                        else:
                            image_name = '%s_%s.jpg' % (id_, str(i + 1).zfill(num_max_length))
                        if folder:
                            image_name = folder + '/' + image_name
                        cls.download_image(image_url, image_name)
            else:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return

        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
