from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time


class Amnibus(Website):
    base_folder = constants.FOLDER_AMNIBUS
    title = constants.WEBSITE_TITLE_AMNIBUS
    keywords = ['https://amnibus.com/', 'Arma Bianca']

    page_prefix = 'https://amnibus.com'
    product_url_template = page_prefix + '/products/detail/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Product Page URL is in the format: http://www.crux-onlinestore.com/shopdetail/{product_id}/')
            expr = input('Enter expression (Product IDs): ').strip()
            if len(expr) == 0:
                return
            numbers = cls.get_sorted_page_numbers(expr, start_from=1)
            if len(numbers) == 1:
                cls.process_product_page(numbers[0])
            elif len(numbers) > 1:
                max_processes = constants.MAX_PROCESSES
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
        image_name_prefix = id_
        try:
            soup = cls.get_soup(product_url)
            div = soup.find('div', class_='detail-slider')
            if not div:
                print('[ERROR] Product ID %s does not exists.' % str(product_id))
            images = div.find_all('img')
            num_max_length = len(str(len(images)))
            for i in range(len(images)):
                if images[i].has_attr('src'):
                    image_url = images[i]['src']
                    if len(images) == 1:
                        image_name = image_name_prefix + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
