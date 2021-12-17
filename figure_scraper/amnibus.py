from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time


class Amnibus(Website):
    base_folder = constants.FOLDER_AMNIBUS
    title = constants.WEBSITE_TITLE_AMNIBUS
    keywords = ['https://amnibus.com/', 'Arma Bianca']

    page_prefix = 'https://amnibus.com'
    product_url_template = page_prefix + '/products/detail/%s'
    event_url_template = 'https://event.amnibus.com/%s/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('Select scraper: ')
            print('1: Download by Product ID')
            print('2: Download by Event ID')
            print('0: Return')

            try:
                result = input('Enter choice: ')
                if len(result) == 0:
                    return

                choice = int(result)
                if choice == 1:
                    cls.process_product_id_input()
                elif choice == 2:
                    cls.process_event_id_input()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid choice.')

    @classmethod
    def process_product_id_input(cls):
        while True:
            print('[INFO] Product Page URL is in the format: https://amnibus.com/products/detail/{product_id}')
            expr = input('Enter expression (Product IDs): ').strip()
            if len(expr) == 0:
                return
            numbers = cls.get_sorted_page_numbers(expr, start_from=1)
            folder = constants.SUBFOLDER_AMNIBUS_IMAGES + '/' + cls.get_today_date()
            if len(numbers) == 1:
                cls.process_product_page(numbers[0], folder)
            elif len(numbers) > 1:
                max_processes = min(constants.MAX_PROCESSES, len(numbers))
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for number in numbers:
                        result = p.apply_async(cls.process_product_page, (number, folder))
                        results.append(result)
                        time.sleep(constants.PROCESS_SPAWN_DELAY)
                    for result in results:
                        result.wait()

    @classmethod
    def process_product_page(cls, product_id, folder=None):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        image_name_prefix = id_
        try:
            soup = cls.get_soup(product_url)
            div = soup.find('div', class_='detail-slider')
            if not div:
                print('[ERROR] Product ID %s does not exists.' % str(product_id))
            images = div.find_all('img')
            num_max_length = len(str(len(images)))
            for i in range(len(images)):
                if images[i].has_attr('src'):
                    image_url = images[i]['src']
                    if len(images) == 1:
                        image_name = image_name_prefix + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    if folder:
                        image_name = folder + '/' + image_name
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def process_event_id_input(cls):
        while True:
            print('[INFO] Page URL is in the format: https://event.amnibus.com/{event_id}/')
            expr = input('Enter Event ID: ').strip()
            if len(expr) == 0:
                return
            cls.download_event(expr, constants.SUBFOLDER_AMNIBUS_EVENT + '/' + expr)

    @classmethod
    def download_event(cls, event_id, folder=None):
        id_ = str(event_id)
        event_url = cls.event_url_template % id_
        try:
            soup = cls.get_soup(event_url)
            images = soup.select('h2 img, img.base-image')
            image_urls = set()
            for image in images:
                if image.has_attr('src') and image['src'] not in image_urls:
                    image_urls.add(image['src'])

            for image_url in image_urls:
                image_name = image_url.split('?')[0].split('/')[-1]
                if folder:
                    image_name = folder + '/' + image_name
                cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % event_url)
            print(e)
