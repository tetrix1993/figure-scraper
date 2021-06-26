from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class Fnex(Website):
    base_folder = constants.FOLDER_FNEX
    title = constants.WEBSITE_TITLE_FNEX
    keywords = ["https://fnex.jp/", 'furyu']

    image_name_template = '%s_%s.jpg'
    product_page_url = 'https://fnex.jp/products/detail.php?product_id=%s'
    image_url_prefix = 'https://df73htivstjso.cloudfront.net/upload/save_image/'
    #image_name_template = 'fnx%s_%s.jpg'
    #image_url_template = 'https://df73htivstjso.cloudfront.net/upload/save_image/' + image_name_template

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
                cls.process_product_page(numbers[0])
            else:
                max_processes = min(constants.MAX_PROCESSES, len(numbers))
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for number in numbers:
                        result = p.apply_async(cls.process_product_page, (number,))
                        results.append(result)
                    for result in results:
                        result.wait()

    @classmethod
    def process_product_page(cls, number):
        product_url = cls.product_page_url % str(number)
        try:
            soup = cls.get_soup(product_url)
            images = soup.select('img')
            max_number = 0
            curr_prefix_template = None
            for image in images:
                if image.has_attr('src') and image['src'].startswith(cls.image_url_prefix)\
                        and image['src'].endswith('.jpg') and not image['src'].endswith('m.jpg'):
                    split1 = image['src'].split('/')[-1].split('.jpg')[0]
                    if curr_prefix_template is None:
                        curr_prefix_template = cls.image_url_prefix\
                                               + image['src'].split(cls.image_url_prefix)[1].split('_')[0] + '_%s.jpg'
                    if '_' in split1 and split1.split('_')[1].isnumeric():
                        num = int(split1.split('_')[1])
                        if num > max_number:
                            max_number = num
            if curr_prefix_template is None:
                raise Exception('Image prefix not found')
            id_ = str(number).zfill(3)
            for i in range(max_number):
                num = str(i + 1).zfill(2)
                image_url = curr_prefix_template % num
                image_name = cls.image_name_template % (id_, num)
                result = cls.download_image(image_url, image_name, print_error_message=False)
                if result == -1:
                    if i == 0:
                        print('[INFO] Product ID %s not found.' % str(number))
                    break
        except Exception as e:
            print('Error in accessing url %s' % product_url)
            print(e)
