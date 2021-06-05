from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class StellaNotes(Website):
    base_folder = constants.FOLDER_STELLANOTES
    title = constants.WEBSITE_TITLE_STELLANOTES
    keywords = ['https://stellanotes.kawaiishop.jp/', title]

    product_url_template = 'https://stellanotes.kawaiishop.jp/items/%s'
    load_item_category_url_template = 'https://stellanotes.kawaiishop.jp/load_items/categories/%s/%s'
    max_item_per_page = 24

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product ID')
            # print('2: Download by Categories')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.download_by_product_id()
                # elif choice == 2:
                #     cls.download_by_categories()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: https://stellanotes.kawaiishop.jp/items/{product_id}/')
        input_str = input('Enter product IDs (if multiple, separate by comma): ')
        if len(input_str) == 0:
            return

        product_ids = input_str.split(',')
        folder = constants.SUBFOLDER_STELLANOTES_IMAGES + '/' + cls.get_today_date()
        if len(product_ids) == 1:
            cls.process_product_page(product_ids[0], folder)
        elif len(product_ids) > 1:
            max_processes = min(constants.MAX_PROCESSES, len(product_ids))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for product_id in product_ids:
                    result = p.apply_async(cls.process_product_page, (product_id, folder))
                    results.append(result)
                for result in results:
                    result.wait()

    @classmethod
    def download_by_categories(cls):
        print('[INFO] URL is in the form: https://stellanotes.kawaiishop.jp/categories/{category_id}/')
        input_str = input('Enter category IDs (if multiple, separate by comma): ')
        if len(input_str) == 0:
            return
        split1 = input_str.split(',')
        categories = []
        for i in split1:
            if len(i) > 0:
                categories.append(i)
        if len(categories) == 0:
            return

        for category in categories:
            print('[INFO] Processing category %s' % category)
            folder = constants.SUBFOLDER_STELLANOTES_CATEGORY + '/' + category
            cls.process_category_page(category, folder)

    @classmethod
    def process_product_page(cls, product_id, folder):
        product_url = cls.product_url_template % product_id
        image_name_prefix = product_id
        try:
            soup = cls.get_soup(product_url)
            image_divs = soup.find_all('div', {'data-type': 'images'})
            image_tags = []
            for image_div in image_divs:
                image_tag = image_div.find('img')
                if image_tag and image_tag.has_attr('src') and '=' not in image_tag['src']:
                    image_tags.append(image_tag)
            num_max_length = len(str(len(image_tags)))
            for i in range(len(image_tags)):
                image_url = image_tags[i]['src']
                suffix = '.jpg'
                if image_url.endswith('.png'):
                    suffix = '.png'
                if len(image_tags) == 1:
                    image_name = image_name_prefix + suffix
                else:
                    image_name = '%s_%s%s' % (image_name_prefix, str(i + 1).zfill(num_max_length), suffix)
                cls.download_image(image_url, folder + '/' + image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def process_category_page(cls, category, folder):
        max_processes = constants.MAX_PROCESSES
        if max_processes <= 0:
            max_processes = 1
        with Pool(max_processes) as p:
            results = []
            for page in range(1, 100, 1):
                url = cls.load_item_category_url_template % (category, page)
                try:
                    soup = cls.get_soup(url)
                    a_tags = soup.select('div.itemImg a')
                    if len(a_tags) == 0:
                        break
                    for a_tag in a_tags:
                        if a_tag.has_attr('href'):
                            product_id = a_tag['href'].split('/')[-1]
                            result = p.apply_async(cls.process_product_page, (product_id, folder))
                            results.append(result)
                    if len(a_tags) == cls.max_item_per_page:
                        break
                except Exception as e:
                    print('[ERROR] Error in processing %s' % url)
                    print(e)
                    break

            for result in results:
                result.wait()
