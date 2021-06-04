from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class Dezaegg(Website):
    base_folder = constants.FOLDER_DEZAEGG
    title = constants.WEBSITE_TITLE_DEZAEGG
    keywords = ["http://dezaegg.com/", "Dezaegg", "License Agent"]

    page_prefix = 'http://dezaegg.com'
    product_url_template = page_prefix + '/products/detail.php?product_id=%s'

    @classmethod
    def run(cls):
        cls.init()
        loop = True
        while loop:
            print('[INFO] %s Scraper' % cls.title)
            loop = cls.download_by_product_id()

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: http://dezaegg.com/products/detail.php?product_id={product_id}')
        expr = input('Enter product IDs: ')
        if len(expr) == 0:
            return False
        product_ids = cls.get_sorted_page_numbers(expr)
        if len(product_ids) == 0:
            return True

        use_jan = False
        while True:
            print('Select name of file to save as: ')
            print('1: Use Product ID as name')
            print('2: Use JAN code as name if possible')
            print('0: Return')

            try:
                choice = int(input('Enter choice: ').strip())
                if choice == 1:
                    break
                elif choice == 2:
                    use_jan = True
                    break
                elif choice == 0:
                    return True
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid choice.')

        today = cls.get_today_date()
        if len(product_ids) == 1:
            cls.process_product_page(product_ids[0], use_jan, today)
        else:
            max_processes = constants.MAX_PROCESSES
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for product_id in product_ids:
                    result = p.apply_async(cls.process_product_page, (product_id, use_jan, today))
                    results.append(result)
                for result in results:
                    result.wait()
        return True

    @classmethod
    def process_product_page(cls, product_id, use_jan=False, folder=None):
        product_url = cls.product_url_template % product_id
        image_name_prefix = product_id
        try:
            soup = cls.get_soup(product_url)
            if use_jan:
                jan_code = cls.get_jan_code(soup)
                if len(jan_code) > 0:
                    image_name_prefix = jan_code
            images = soup.select('div.photo a')
            if len(images) == 0:
                print('[ERROR] Product ID %s not found.' % product_id)
                return
            elif len(images) == 1:
                image_url = cls.page_prefix + images[0]['href']
                image_name = image_name_prefix + '.jpg'
                if folder:
                    image_name = folder + '/' + image_name
                cls.download_image(image_url, image_name)
            else:
                num_max_length = len(str(len(images)))
                for i in range(len(images)):
                    image_url = cls.page_prefix + images[i]['href']
                    image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    if folder:
                        image_name = folder + '/' + image_name
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @staticmethod
    def get_jan_code(soup):
        result = ''
        elem = soup.select('p.jan_code')
        if len(elem) > 0:
            result = elem[0].text.strip()
        return result
