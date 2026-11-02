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
    event_url_template = 'https://%s.amnibus.com/%s/'
    drawdraw_api_prefix = 'https://amnibus.com/drawdraw/api/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('Select scraper: ')
            print('1: Download by Product ID')
            print('2: Download by Event ID')
            print('3: Download Draw!Draw! (Kuji)')
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
                elif choice == 3:
                    cls.process_drawdraw_id_input()
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
                max_processes = min(cls.max_processes, len(numbers))
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
            images = soup.select('.productDetail__imgsContainer--main img[src],.detailPresent img[src]')
            if len(images) == 0:
                print('[ERROR] Product ID %s does not exists.' % str(product_id))
                return
            num_max_length = len(str(len(images)))
            for i in range(len(images)):
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
            print('[INFO] Page URL is in the format: https://{type}.amnibus.com/{event_id}/')
            link_type = input('Enter type (event or store): ').strip()
            if len(link_type) == 0:
                return
            expr = input('Enter Event ID: ').strip()
            if len(expr) == 0:
                continue
            cls.download_event(expr, link_type, constants.SUBFOLDER_AMNIBUS_EVENT + '/' + expr)

    @classmethod
    def download_event(cls, event_id, link_type, folder=None):
        id_ = str(event_id)
        event_url = cls.event_url_template % (link_type, id_)
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

    @classmethod
    def process_drawdraw_id_input(cls):
        while True:
            print('[INFO] Page URL is in the format: https://amnibus.com/drawdraw/collection/{id}')
            drawdraw_id = input('Enter Draw!Draw! ID: ').strip()
            if len(drawdraw_id) == 0:
                return
            cls.download_drawdraw(drawdraw_id, constants.SUBFOLDER_AMNIBUS_DRAWDRAW + '/' + drawdraw_id)

    @classmethod
    def download_drawdraw(cls, drawdraw_id, folder=None):
        id_ = str(drawdraw_id)
        main_url = cls.drawdraw_api_prefix % id_
        prizes_url = main_url + '/prizes'
        presents_url = main_url + '/presents'

        # Main
        try:
            obj = cls.get_json(main_url)
            if 'lottery' in obj and 'mainListImage' in obj['lottery']:
                image = obj['lottery']['mainListImage']
                image_url = None
                if 'originImage' in image:
                    image_url = image['originImage']
                elif 'mainImage' in image:
                    image_url = image['mainImage']
                if image_url is not None and len(image_url) > 0:
                    img_ext = image_url.split('?')[0].rsplit('.', maxsplit=1)[-1]
                    image_name = 'main.' + img_ext
                    if folder:
                        image_name = folder + '/' + image_name
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % main_url)
            print(e)

        # Prizes
        try:
            obj = cls.get_json(prizes_url)
            if 'prizes' in obj:
                for prize in obj['prizes']:
                    if 'products' not in prize:
                        continue
                    for product in prize['products']:
                        if 'prizeNumber' not in product or 'image' not in product:
                            continue
                        image = product['image']
                        image_url = None
                        if 'originImage' in image:
                            image_url = image['originImage']
                        elif 'mainImage' in image:
                            image_url = image['mainImage']
                        if image_url is None or len(image_url) == 0:
                            continue
                        img_ext = image_url.split('?')[0].rsplit('.', maxsplit=1)[-1]
                        image_name = product['prizeNumber'] + '.' + img_ext
                        if folder:
                            image_name = folder + '/' + image_name
                        cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % prizes_url)
            print(e)

        # Presents
        i = 0
        try:
            obj = cls.get_json(presents_url)
            if 'presents' in obj:
                for present in obj['presents']:
                    if 'image' not in present or 'mainImage' not in present['image']:
                        continue
                    image = present['image']
                    image_url = None
                    if 'originImage' in image:
                        image_url = image['originImage']
                    elif 'mainImage' in image:
                        image_url = image['originImage']
                    if image_url is None or len(image_url) == 0:
                        continue
                    img_ext = image_url.split('?')[0].rsplit('.', maxsplit=1)[-1]
                    i += 1
                    image_name = 'present' + str(i) + '.' + img_ext
                    if folder:
                        image_name = folder + '/' + image_name
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % presents_url)
            print(e)
