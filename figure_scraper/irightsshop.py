from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time


class IRightsShop(Website):
    base_folder = constants.FOLDER_IRIGHTSSHOP
    title = constants.WEBSITE_TITLE_IRIGHTSSHOP
    keywords = ["https://www.i-rightsshop.com/", 'irights']

    product_page_prefix = 'https://www.i-rightsshop.com/SHOP/%s.html'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Page')
            print('2: Download by Template')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.download_by_page()
                elif choice == 2:
                    cls.download_by_template()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def download_by_page(cls):
        product_id_template = 'IR-%1-%0'
        template = cls.product_page_prefix % product_id_template
        while True:
            stop_loop = True
            print(f'[INFO] Download by page: {template}')
            p1 = input('Enter %1: ')
            if len(p1) == 0:
                break
            expr = input('Enter expression (Product IDs): ')
            if len(expr) == 0:
                continue
            numbers = cls.get_numbers_from_expression(expr)
            if len(numbers) == 0:
                continue

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
                        stop_loop = False
                        break
                    else:
                        raise Exception
                except:
                    print('[ERROR] Invalid choice.')
            if stop_loop:
                folder = constants.SUBFOLDER_IRIGHTSSHOP_PAGE + '/' + cls.get_today_date()
                if len(numbers) == 1:
                    product_id = product_id_template.replace('%1', p1).replace('%0', str(numbers[0]).zfill(3))
                    cls.process_product_page(product_id, use_jan, folder)
                elif len(numbers) > 0:
                    max_processes = min(cls.max_processes, len(numbers))
                    if max_processes <= 0:
                        max_processes = 1
                    with Pool(max_processes) as p:
                        results = []
                        for number in numbers:
                            product_id = product_id_template.replace('%1', p1).replace('%0', str(number).zfill(3))
                            result = p.apply_async(cls.process_product_page, (product_id, use_jan, folder))
                            results.append(result)
                            time.sleep(constants.PROCESS_SPAWN_DELAY)
                        for result in results:
                            result.wait()

    @classmethod
    def process_product_page(cls, product_id, use_jan=False, folder=None):
        id_ = str(product_id)
        product_url = cls.product_page_prefix % id_
        try:
            soup = cls.get_soup(product_url)
            imgs = soup.select('img[src].fl_main_img')
            if len(imgs) == 0:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return
            prefix = id_
            if use_jan:
                prefix = cls.get_jan_code(id_, soup)
            num_max_length = len(str(len(imgs)))
            for i in range(len(imgs)):
                image_url = imgs[i]['src']
                if len(imgs) == 1:
                    image_name = prefix + '.jpg'
                else:
                    image_name = '%s_%s.jpg' % (prefix, str(i + 1).zfill(num_max_length))
                if folder:
                    image_name = folder + '/' + image_name
                cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def get_jan_code(cls, product_id, soup):
        td = soup.select('tr.jan>td')
        if len(td) > 0:
            return td[0].text[0:13]
        return product_id

    @classmethod
    def download_by_template(cls):
        template = 'https://image1.shopserve.jp/i-rightsshop.com/pic-labo/IR-%1-%0.jpg'
        while True:
            print(f'[INFO] Download by template: {template}')
            p1 = input('Enter %1: ')
            if len(p1) == 0:
                break
            template_url = template.replace('%1', p1)
            expr = input('Enter expression (Product IDs): ')
            if len(expr) == 0:
                continue
            numbers = cls.get_numbers_from_expression(expr)
            if len(numbers) == 0:
                continue
            for num in numbers:
                image_url = template_url.replace('%0', str(num).zfill(3))
                image_name = f'{constants.SUBFOLDER_IRIGHTSSHOP_TEMPLATE}/{p1}/{image_url.split("/")[-1]}'
                try:
                    cls.download_image(image_url, image_name)
                except:
                    print(f'[ERROR] Error downloading {image_url}')
