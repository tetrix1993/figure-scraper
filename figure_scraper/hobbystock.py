from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time


class HobbyStock(Website):
    base_folder = constants.FOLDER_HOBBYSTOCK
    title = constants.WEBSITE_TITLE_HOBBYSTOCK
    keywords = ["http://www.hobbystock.jp/"]

    product_url_template = 'http://www.hobbystock.jp/item/view/%s'
    image_url_full_template = 'https://s3-ap-northeast-1.amazonaws.com/hobbystock/img/item/%s/pc_detail_0.jpg'
    image_url_thumb_template = 'https://s3-ap-northeast-1.amazonaws.com/hobbystock/img/item/%s/pc_thumbnail.jpg'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product ID')
            print('2: Download by Image ID')
            print('0: Exit')
            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.process_by_product_id()
                elif choice == 2:
                    cls.process_by_image_id()
                elif choice == 0:
                    return
                else:
                    print('[ERROR] Invalid option.')
                    continue
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def process_by_product_id(cls):
        print('[INFO] Product Page URL is in the format: http://www.hobbystock.jp/item/view/{prefix}-{id}')
        prefix = input('Enter prefix (e.g. hso-ccg): ').strip().lower()
        if len(prefix) == 0:
            return
        expr = input('Enter expression (Product IDs): ').strip()
        if len(expr) == 0:
            return
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
            images = soup.select('.productMainBox__left img[src]')
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

    @classmethod
    def process_by_image_id(cls):
        is_thumbnail = False
        while True:
            print('[INFO] Select an option: ')
            print('1: Download full image')
            print('2: Download thumbnail')
            print('0: Return')
            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 0:
                    return
                elif choice != 1 and choice != 2:
                    print('[ERROR] Invalid option.')
                    continue
            except:
                print('[ERROR] Invalid option.')
                continue
            if choice == 1:
                image_url_template = cls.image_url_full_template
                break
            elif choice == 2:
                is_thumbnail = True
                image_url_template = cls.image_url_thumb_template
                break
            else:
                continue

        expr = input('Enter expression (Image IDs): ').strip()
        if len(expr) == 0:
            return
        unfiltered_numbers = cls.get_numbers_from_expression(expr)
        today = cls.get_today_date()
        numbers = []
        for number in unfiltered_numbers:
            image_id = str(number).zfill(11)
            filepath = today + '/' + image_id
            if cls.is_image_exists(filepath, has_extension=True) \
                    or cls.is_image_exists(filepath + '_1', has_extension=True) \
                    or cls.is_image_exists(filepath + '_01', has_extension=True):
                print(f'[INFO] Image ID {image_id} already downloaded')
                continue
            numbers.append(number)
        if len(numbers) == 1:
            image_id = str(numbers[0]).zfill(11)
            if is_thumbnail:
                image_name = today + '/' + image_id + '_t.jpg'
            else:
                image_name = today + '/' + image_id + '.jpg'
            image_url = image_url_template % image_id
            cls.download_image_by_url(image_name, image_url)
        elif len(numbers) > 1:
            max_processes = min(constants.MAX_PROCESSES, len(numbers))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for number in numbers:
                    image_id = str(number).zfill(11)
                    if is_thumbnail:
                        image_name = today + '/' + image_id + '_t.jpg'
                    else:
                        image_name = today + '/' + image_id + '.jpg'
                    image_url = image_url_template % image_id
                    result = p.apply_async(cls.download_image_by_url, (image_name, image_url))
                    results.append(result)
                    time.sleep(constants.PROCESS_SPAWN_DELAY)
                for result in results:
                    result.wait()

    @classmethod
    def download_image_by_url(cls, image_name, image_url):
        cls.download_image(image_url, image_name)
