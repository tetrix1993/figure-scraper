from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time


class Medicos(Website):
    base_folder = constants.FOLDER_MEDICOS
    title = constants.WEBSITE_TITLE_MEDICOS
    keywords = ["https://medicos-e-shop.net"]

    product_url_prefix = 'https://medicos-e-shop.net'
    product_url_template = product_url_prefix + '/products/detail/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            stop_loop = True
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter expression (Product IDs): ')
            if len(expr) == 0:
                return

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
                numbers = cls.get_numbers_from_expression(expr)
                today = cls.get_today_date()
                if len(numbers) == 1:
                    cls.process_product_page(numbers[0], use_jan, today)
                elif len(numbers) > 0:
                    max_processes = min(cls.max_processes, len(numbers))
                    if max_processes <= 0:
                        max_processes = 1
                    with Pool(max_processes) as p:
                        results = []
                        for number in numbers:
                            result = p.apply_async(cls.process_product_page, (number, use_jan, today))
                            results.append(result)
                            time.sleep(constants.PROCESS_SPAWN_DELAY)
                        for result in results:
                            result.wait()

    @classmethod
    def process_product_page(cls, product_id, use_jan=False, folder=None):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url)
            imgs = soup.select('div.product-gallery .swiper-slide img[src]')
            if len(imgs) == 0:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return
            prefix = id_
            if use_jan:
                prefix = cls.get_jan_code(id_, soup)
            num_max_length = len(str(len(imgs)))
            for i in range(len(imgs)):
                if i > 0 and i == len(imgs) - 1:  # Exclude last image (ignore bonus)
                    continue
                image = imgs[i]
                image_url = image['src']
                index = image_url.find('/html/')  # To get better color picture
                if index > 0:
                    image_url = cls.product_url_prefix + image_url[index:]
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
        span = soup.find('span', class_='product-code-default')
        if span and len(span.text.strip()) > 0:
            text = span.text.strip()
            index1 = text.find('【JAN:')
            index2 = text.find('【BOXJAN:')
            l_index = -1
            if index1 >= 0:
                l_index = index1 + 5
            elif index2 >= 0:
                l_index = index2 + 8
            if l_index >= 0:
                r_index = text.find('】')
                if l_index < r_index:
                    return text[l_index:r_index]
        return product_id
