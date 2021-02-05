from figure_scraper.website import Website
import figure_scraper.constants as constants


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
                for number in numbers:
                    cls.process_product_page(number, use_jan)
                break

    @classmethod
    def process_product_page(cls, product_id, use_jan=False):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url)
            divs = soup.find_all('div', class_='slide-item')
            if len(divs) == 0:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return
            prefix = id_
            if use_jan:
                prefix = cls.get_jan_code(id_, soup)
            for i in range(len(divs)):
                image = divs[i].find('img')
                if image and image.has_attr('src'):
                    image_url = cls.product_url_prefix + image['src']
                    image_name = '%s_%s.jpg' % (prefix, str(i + 1).zfill(2))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def get_jan_code(cls, product_id, soup):
        span = soup.find('span', class_='product-code-default')
        if span and len(span.text.strip()) > 0:
            text = span.text.strip()
            if '【JAN:' in text[0:5] and '】' in text[-1]:
                return text.split('【JAN:')[1].split('】')[0]
        return product_id
