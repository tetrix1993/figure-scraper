from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time


class Alter(Website):
    base_folder = constants.FOLDER_ALTER
    title = constants.WEBSITE_TITLE_ALTER
    keywords = ['https://alter-web.jp/']

    page_url_prefix = 'https://alter-web.jp'
    product_url_template = page_url_prefix + '/products/%s/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Product Page URL is in the format: https://alter-web.jp/products/{product_id}/')
            expr = input('Enter expression (Product IDs): ').strip()
            if len(expr) == 0:
                return
            unfiltered_numbers = cls.get_numbers_from_expression(expr)
            numbers = []
            for number in unfiltered_numbers:
                if cls.is_image_exists(str(number), has_extension=True):
                    print(f'[INFO] Product ID {number} already downloaded')
                    continue
                numbers.append(number)
            if len(numbers) == 1:
                cls.process_product_page(numbers[0])
            elif len(numbers) > 1:
                max_processes = min(constants.MAX_PROCESSES, len(numbers))
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for number in numbers:
                        result = p.apply_async(cls.process_product_page, (number, ))
                        results.append(result)
                        time.sleep(constants.PROCESS_SPAWN_DELAY)
                    for result in results:
                        result.wait()

    @classmethod
    def process_product_page(cls, product_id):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url)
            div = soup.find('div', class_='item-mainimg')
            ul = soup.find('ul', class_='bxslider')
            if not div and not ul:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return

            if div:
                image = div.find('img')
                if image and image.has_attr('src'):
                    image_url = cls.page_url_prefix + image['src']
                    image_name = id_ + '.jpg'
                    cls.download_image(image_url, image_name)

            if ul:
                images = ul.find_all('img')
                num_max_length = len(str(len(images)))
                for i in range(len(images)):
                    if images[i].has_attr('src'):
                        image_url = cls.page_url_prefix + images[i]['src']
                        image_name = '%s_%s.jpg' % (id_, str(i + 1).zfill(num_max_length))
                        cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
