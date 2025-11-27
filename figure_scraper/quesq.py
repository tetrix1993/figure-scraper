from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class Quesq(Website):
    base_folder = constants.FOLDER_QUESQ
    title = constants.WEBSITE_TITLE_QUESQ
    keywords = ["http://www.quesq.net/", "QuesQ"]

    page_url_prefix = 'http://www.quesq.net/'
    product_page_template = page_url_prefix + 'products/%s/'

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        while True:
            print('[INFO] URL is in the form: http://www.quesq.net/products/{product_id}/')
            expr = input('Enter product IDs (expression) separated by comma: ')
            if len(expr) == 0:
                return
            product_ids_arr = expr.split(',')
            product_ids = []
            for id_ in product_ids_arr:
                if len(id_) > 0:
                    product_ids.append(id_)

            if len(product_ids) == 1:
                cls.process_product_page(product_ids[0])
            elif len(product_ids) > 1:
                max_processes = min(cls.max_processes, len(product_ids))
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for product_id in product_ids:
                        result = p.apply_async(cls.process_product_page, (product_id,))
                        results.append(result)
                    for result in results:
                        result.wait()

    @classmethod
    def process_product_page(cls, product_id):
        url = cls.product_page_template % product_id
        print('[INFO] Processing ' + url)
        try:
            soup = cls.get_soup(url)
            images = soup.select('div.product_photo img')
            for image in images:
                if image.has_attr('src'):
                    image_url = url + image['src']
                    image_name = image_url.split('/')[-1]
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % url)
            print(e)