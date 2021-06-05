from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class Fnex(Website):
    base_folder = constants.FOLDER_FNEX
    title = constants.WEBSITE_TITLE_FNEX
    keywords = ["https://fnex.jp/", 'furyu']

    image_name_template = 'fnx%s_%s.jpg'
    image_url_template = 'https://df73htivstjso.cloudfront.net/upload/save_image/' + image_name_template

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter expression (Product IDs): ')
            if len(expr) == 0:
                return
            numbers = cls.get_sorted_page_numbers(expr)
            if len(numbers) == 0:
                pass
            elif len(numbers) == 1:
                cls.process_product_id(numbers[0])
            else:
                max_processes = min(constants.MAX_PROCESSES, len(numbers))
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for number in numbers:
                        result = p.apply_async(cls.process_product_id, (number,))
                        results.append(result)
                    for result in results:
                        result.wait()

    @classmethod
    def process_product_id(cls, number):
        id_ = str(number).zfill(3)
        for i in range(99):
            num = str(i + 1).zfill(2)
            image_url = cls.image_url_template % (id_, num)
            image_name = cls.image_name_template % (id_, num)
            result = cls.download_image(image_url, image_name, print_error_message=False)
            if result == -1:
                if i == 0:
                    print('[INFO] Product ID %s not found.' % str(number))
                break
