from figure_scraper.website import Website
import figure_scraper.constants as constants


class Neowing(Website):
    base_folder = constants.FOLDER_NEOWING
    title = constants.WEBSITE_TITLE_NEOWING
    keywords = ['https://www.neowing.co.jp/', 'https://www.cdjapan.co.jp/']

    product_url_template = 'https://www.neowing.co.jp/product/NEOGDS-%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Product Page URL is in the format: https://www.neowing.co.jp/product/NEOGDS-{product_id}')
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
                numbers = cls.get_numbers_from_expression(expr)
                for number in numbers:
                    cls.process_product_page(number, use_jan)

    @classmethod
    def process_product_page(cls, product_id, use_jan=False):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        image_name_prefix = id_
        try:
            soup = cls.get_soup(product_url)
            ul = soup.find('ul', class_='prod-thumb')
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
                    image_url = 'https:' + images[i]['src']
                    if len(images) == 1:
                        image_name = image_name_prefix + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @staticmethod
    def get_jan_code(soup):
        result = ''
        span = soup.find('span', {'itemprop': 'gtin13'})
        if span and span.has_attr('content'):
            result = span['content'].strip()
        return result
