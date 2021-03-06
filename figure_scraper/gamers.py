from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class Gamers(Website):
    base_folder = constants.FOLDER_GAMERS
    title = constants.WEBSITE_TITLE_GAMERS
    keywords = ['https://www.gamers.co.jp/']

    product_url_template = 'https://www.gamers.co.jp/pn/pd/%s/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Product Page URL is in the format: https://www.gamers.co.jp/pn/pd/{product_id}/')
            expr = input('Enter expression (Product IDs): ').strip()
            if len(expr) == 0:
                return
            evaluate = True
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
                        evaluate = False
                        break
                    else:
                        raise Exception
                except:
                    print('[ERROR] Invalid choice.')
            if evaluate:
                numbers = cls.get_sorted_page_numbers(expr)
                today = cls.get_today_date()
                print('[INFO] Images will be saved at %s' % (cls.base_folder + '/' + today))
                if len(numbers) == 1:
                    cls.process_product_page(numbers[0], use_jan, today)
                elif len(numbers) > 1:
                    max_processes = min(constants.MAX_PROCESSES, len(numbers))
                    if max_processes <= 0:
                        max_processes = 1
                    with Pool(max_processes) as p:
                        results = []
                        for number in numbers:
                            result = p.apply_async(cls.process_product_page, (number, use_jan, today))
                            results.append(result)
                        for result in results:
                            result.wait()

    @classmethod
    def process_product_page(cls, product_id, use_jan=False, folder=None):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        image_name_prefix = id_
        try:
            soup = cls.get_soup(product_url)
            ul = soup.find('ul', class_='item_img_main')
            if not ul:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return
            if use_jan:
                jan_code = cls.get_jan_code(soup)
                if len(jan_code) > 0:
                    image_name_prefix = jan_code
            images = ul.find_all('img')
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

    @staticmethod
    def get_jan_code(soup):
        result = ''
        a_tag = soup.find('a', id='opener')
        if a_tag:
            text = a_tag.text.strip()
            if len(text) > 12:
                result = a_tag.text.strip()[-13:]
        return result
