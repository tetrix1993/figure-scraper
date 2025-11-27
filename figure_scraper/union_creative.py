from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class UnionCreative(Website):
    base_folder = constants.FOLDER_UNION_CREATIVE
    title = constants.WEBSITE_TITLE_UNION_CREATIVE
    keywords = ["https://union-creative.jp/"]

    image_name_template = '%s.jpg'
    image_url_template = 'https://union-creative.jp/photo/item/%s/' + image_name_template

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter expression (Image IDs): ')
            if len(expr) == 0:
                return
            numbers = cls.get_sorted_page_numbers(expr)
            if len(numbers) == 0:
                pass
            elif len(numbers) == 1:
                cls.process_image_id(numbers[0])
            else:
                max_processes = min(cls.max_processes, len(numbers))
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for number in numbers:
                        result = p.apply_async(cls.process_image_id, (number, ))
                        results.append(result)
                    for result in results:
                        result.wait()

    @classmethod
    def process_image_id(cls, number):
        id_ = str(number)
        for i in range(100):
            if i == 0:
                num = id_
            else:
                num = id_ + '_' + str(i)
            image_url = cls.image_url_template % (id_, num)
            image_name = cls.image_name_template % num
            result = cls.download_image(image_url, image_name, print_error_message=False)
            if result == -1:
                if i == 0:
                    print('[INFO] Product ID %s not found.' % str(number))
                break
