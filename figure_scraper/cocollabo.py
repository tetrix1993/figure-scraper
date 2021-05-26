from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class Cocollabo(Website):
    base_folder = constants.FOLDER_COCOLLABO
    title = constants.WEBSITE_TITLE_COCOLLABO
    keywords = ["https://www.cocollabo.net/"]

    page_prefix = 'https://www.cocollabo.net/'
    product_url_template = page_prefix + 'shop/g/%s/'
    category_url_template = page_prefix + 'shop/r/%s/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product ID')
            print('2: Download by Category')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.download_by_product_id()
                elif choice == 2:
                    cls.download_by_category_id()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except Exception:
                print('[ERROR] Invalid option.')

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: https://www.cocollabo.net/shop/g/{product_id}/')
        expr = input('Enter product IDs (separated by commas): ')
        product_ids = expr.split(',')
        final_product_ids = []
        folder = constants.SUBFOLDER_COCOLLABO_IMAGES
        for product_id in product_ids:
            if len(product_id) > 0:
                if cls.is_image_exists(folder + '/' + product_id + '_1', has_extension=True) \
                        or cls.is_image_exists(folder + '/' + product_id + '_01', has_extension=True):
                    print(f'[INFO] Product ID {product_id} already downloaded')
                    continue
                final_product_ids.append(product_id)

        if len(final_product_ids) == 0:
            return
        elif len(final_product_ids) == 1:
            cls.process_product_page(final_product_ids[0], folder)
        else:
            max_processes = constants.MAX_PROCESSES
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for product_id in final_product_ids:
                    result = p.apply_async(cls.process_product_page, (product_id, folder))
                    results.append(result)
                for result in results:
                    result.wait()

    @classmethod
    def download_by_category_id(cls):
        print('[INFO] URL is in the form: https://www.cocollabo.net/shop/r/{category_id}/')
        expr = input('Enter product IDs (separated by commas): ')
        category_ids = expr.split(',')
        final_category_ids = []
        for category_id in category_ids:
            if len(category_id) > 0:
                final_category_ids.append(category_id)

        folder = constants.SUBFOLDER_COCOLLABO_CATEGORY
        for category_id in category_ids:
            cls.process_category_page(category_id, folder + '/' + category_id)

    @classmethod
    def process_product_page(cls, product_id, folder):
        product_url = cls.product_url_template % product_id
        image_name_prefix = product_id
        try:
            soup = cls.get_soup(product_url)
            images = soup.select('div.pane-goods-left-side a')
            if len(images) == 0:
                print('[ERROR] Product ID %s not found.' % product_id)
                return
            num_max_length = len(str(len(images)))
            for i in range(len(images)):
                image_url = 'https:' + images[i]['href']
                image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                cls.download_image(image_url, folder + '/' + image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def process_category_page(cls, category_id, folder):
        category_url = cls.category_url_template % category_id
        try:
            page = 0
            while len(category_url) > 0:
                page += 1
                print(f'[INFO] Processing {category_id} (Page {page})')
                soup = cls.get_soup(category_url)
                a_tags = soup.select('ul.block-goods-detail-j--items dt a')
                product_ids = []
                for a_tag in a_tags:
                    if a_tag.has_attr('href'):
                        product_id = a_tag['href'].split('/')[-2]
                        if cls.is_image_exists(folder + '/' + product_id + '_1', has_extension=True) \
                                or cls.is_image_exists(folder + '/' + product_id + '_01', has_extension=True):
                            print(f'[INFO] Product ID {product_id} already downloaded')
                            continue
                        product_ids.append(product_id)

                if len(product_ids) == 1:
                    cls.process_product_page(product_ids[0], folder)
                elif len(product_ids) > 0:
                    max_processes = constants.MAX_PROCESSES
                    if max_processes <= 0:
                        max_processes = 1
                    with Pool(max_processes) as p:
                        results = []
                        for product_id in product_ids:
                            result = p.apply_async(cls.process_product_page, (product_id, folder))
                            results.append(result)
                        for result in results:
                            result.wait()

                category_url = ''
                next_page_a_tag = soup.select('li.pager-next a')
                if len(next_page_a_tag) > 0:
                    category_url = cls.page_prefix + next_page_a_tag[0]['href'][1:]
        except Exception as e:
            print('[ERROR] Error in processing %s' % category_url)
            print(e)
