from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class MSFactory(Website):
    base_folder = constants.FOLDER_MSFACTORY
    title = constants.WEBSITE_TITLE_MSFACTORY
    keywords = ["https://shop.ms-factory.net/", "https://www.aieris.jp/", "M's"]

    page_prefix = 'https://shop.ms-factory.net/'
    product_url_template = page_prefix + 'items/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product ID')
            print('2: Download by Categories')
            print('3: Download by Items from Main Page')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.download_by_product_id()
                elif choice == 2:
                    cls.download_by_categories()
                elif choice == 3:
                    cls.download_from_main_page()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: https://shop.ms-factory.net/items/{product_id}/')
        input_str = input('Enter product IDs (if multiple, separate by comma): ')
        if len(input_str) == 0:
            return

        result = cls.get_use_jan_choice()
        use_jan = False
        if result == 1:
            use_jan = True
        elif result == -1:
            return

        product_ids = input_str.split(',')
        for product_id in product_ids:
            if len(product_id) > 0:
                cls.process_product_page(product_id, constants.SUBFOLDER_MSFACTORY_IMAGES, use_jan)

    @classmethod
    def download_by_categories(cls):
        print('[INFO] Coming soon...')

    @classmethod
    def download_from_main_page(cls):
        print('[INFO] Coming soon...')

    @classmethod
    def get_use_jan_choice(cls):
        while True:
            print('Select name of file to save as: ')
            print('1: Use Product ID as name')
            print('2: Use JAN code as name if possible')
            print('0: Return')

            try:
                choice = int(input('Enter choice: ').strip())
                if choice == 1:
                    return 0
                elif choice == 2:
                    return 1
                elif choice == 0:
                    return -1
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid choice.')

    @classmethod
    def get_sorted_page_numbers(cls, expr):
        numbers = cls.get_numbers_from_expression(expr)
        if len(numbers) > 0:
            numbers = list(set(numbers))
            numbers.sort()
            if numbers[0] == 0:
                return numbers[1:]
        return numbers

    @classmethod
    def process_product_page(cls, product_id, folder, use_jan=False):
        product_url = cls.product_url_template % product_id
        image_name_prefix = product_id
        try:
            soup = cls.get_soup(product_url)
            div = soup.find('div', class_='item__mainImage')
            if not div:
                print('[INFO] Product ID %s not found.' % product_id)
                return
            if use_jan:
                jan_code = cls.get_jan_code(soup)
                if len(jan_code) > 0:
                    image_name_prefix = jan_code
            a_tags = div.find_all('a')
            num_max_length = len(str(len(a_tags)))
            for i in range(len(a_tags)):
                if a_tags[i].has_attr('href'):
                    image_url = a_tags[i]['href']
                    if len(a_tags) == 1:
                        image_name = image_name_prefix + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    cls.download_image(image_url, folder + '/' + image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @staticmethod
    def get_jan_code(soup):
        result = ''
        h3 = soup.find('h3', class_='item__title')
        if h3:
            text = h3.text.strip()
            if len(text) > 14 and text[0] == '【':
                result = text[1:14]
        return result
