from figure_scraper.website import Website
import figure_scraper.constants as constants


class AmiAmi(Website):
    base_folder = constants.FOLDER_AMIAMI
    title = constants.WEBSITE_TITLE_AMIAMI
    keywords = ['https://amiami.jp/']

    product_url_template = 'https://www.amiami.jp/top/detail/detail?gcode=%s'

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        print('[INFO] Product Page URL is in the format: https://www.amiami.jp/top/detail/detail?gcode={prefix}-{product_id}')
        prefix = input('Enter prefix (e.g.: FIGURE): ').strip().upper()
        if len(prefix) == 0:
            return
        expr = input('Enter expression (Product IDs): ').strip()
        if len(expr) == 0:
            return
        numbers = cls.get_numbers_from_expression(expr)
        for number in numbers:
            cls.process_product_page(prefix, number)

    @classmethod
    def process_product_page(cls, prefix, product_id):
        padding = cls.get_padding_count(prefix)
        if padding == 0:
            print('[INFO] The scraper does not support %s' % prefix)
            return
        id_ = prefix + '-' + str(product_id).zfill(padding)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url)
            main_image_div = soup.find('div', class_='main_image_area_inner')
            if main_image_div:
                main_image = main_image_div.find('img')
                if main_image and main_image.has_attr('src'):
                    cls.download_image(main_image['src'], id_ + '.jpg')
            else:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return

            divs = soup.find_all('div', class_='gallery_item_review')
            if len(divs) == 0:
                return
            num_max_length = len(str(len(divs)))
            for i in range(len(divs)):
                a_tag = divs[i].find('a')
                if a_tag and a_tag.has_attr('href'):
                    image_url = a_tag['href']
                    image_name = '%s_%s.jpg' % (id_, str(i + 1).zfill(num_max_length))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def get_padding_count(cls, prefix):
        if prefix in ['TC-IDL', 'TOY-GDM', 'TOY-RBT']:
            return 4
        elif prefix in ['MED-CD2', 'MED-DVD2', 'RAIL', 'TOY-SCL2', 'TOY-SCL3']:
            return 5
        elif prefix in ['FIGURE', 'JIGS', 'MED-BOOK', 'TOY']:
            return 6
        elif prefix in ['GAME']:
            return 7
        elif prefix in ['GOODS', 'CARD', 'TOL']:
            return 8
        else:
            return 0
