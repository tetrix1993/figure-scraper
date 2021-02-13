from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class Crux(Website):
    base_folder = constants.FOLDER_CRUX
    title = constants.WEBSITE_TITLE_CRUX
    keywords = ['http://www.crux-onlinestore.com/']

    page_prefix = 'http://www.crux-onlinestore.com'
    product_url_template = page_prefix + '/shopdetail/%s/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product IDs')
            print('2: Download by Category')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.download_by_product_id()
                elif choice == 2:
                    cls.download_by_category()
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def download_by_product_id(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Product Page URL is in the format: http://www.crux-onlinestore.com/shopdetail/{product_id}/')
            expr = input('Enter expression (Product IDs): ').strip()
            if len(expr) == 0:
                return
            numbers = cls.get_sorted_page_numbers(expr, start_from=1)
            if len(numbers) == 1:
                cls.process_product_page(numbers[0], constants.SUBFOLDER_CRUX_IMAGES)
            elif len(numbers) > 1:
                max_processes = constants.MAX_PROCESSES
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for number in numbers:
                        result = p.apply_async(cls.process_product_page, (number, constants.SUBFOLDER_CRUX_IMAGES))
                        results.append(result)
                    for result in results:
                        result.wait()

    @classmethod
    def download_by_category(cls):
        print('[INFO] Coming soon...')

    @classmethod
    def process_product_page(cls, product_id, folder):
        id_ = str(product_id).zfill(12)
        product_url = cls.product_url_template % id_
        image_name_prefix = folder + '/' + str(product_id)
        try:
            soup = cls.get_soup(product_url)
            div = soup.find('div', class_='M_imageMain')
            if not div:
                # Page only has one image
                div = soup.find('div', id='itemImg')
                if not div:
                    print('[ERROR] Product ID %s does not exists.' % id_)
                    return
                image = div.find('img')
                if image:
                    images = [image]
                else:
                    print('[ERROR] Product ID %s does not exists.' % id_)
                    return
            else:
                images = div.find_all('img')
            num_max_length = len(str(len(images)))
            for i in range(len(images)):
                if images[i].has_attr('src'):
                    image_url = images[i]['src'].split('?')[0]
                    if len(images) == 1:
                        image_name = image_name_prefix + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
