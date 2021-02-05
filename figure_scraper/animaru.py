from figure_scraper.website import Website
import figure_scraper.constants as constants


class Animaru(Website):
    base_folder = constants.FOLDER_ANIMARU
    title = constants.WEBSITE_TITLE_ANIMARU
    keywords = ['https://animaru.jp']

    product_page_prefix = 'https://animaru.jp'
    product_url_template = product_page_prefix + '/anmr/product/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Product Page URL is in the format: http://www.hobbystock.jp/item/view/{prefix}-{id}')
            prefix = input('Enter prefix (e.g. P): ').strip().upper()
            if len(prefix) == 0:
                return
            expr = input('Enter expression (Product IDs): ').strip()
            if len(expr) == 0:
                continue
            numbers = cls.get_numbers_from_expression(expr)
            for number in numbers:
                cls.process_product_page(prefix, number)

    @classmethod
    def process_product_page(cls, prefix, product_id):
        id_ = prefix + str(product_id)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url)
            divs = soup.find_all('div', class_='gallery__wrapper__slide')
            if len(divs) == 0:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return
            num_max_length = len(str(len(divs)))
            for i in range(len(divs)):
                image = divs[i].find('img')
                if image and image.has_attr('data-normal'):
                    image_url = cls.product_page_prefix + image['data-normal']
                    if len(divs) == 1:
                        image_name = id_ + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (id_, str(i + 1).zfill(num_max_length))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
