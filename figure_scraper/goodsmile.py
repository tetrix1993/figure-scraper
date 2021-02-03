from figure_scraper.website import Website
import figure_scraper.constants as constants


class Goodsmile(Website):
    base_folder = constants.FOLDER_GOODSMILE
    title = constants.WEBSITE_TITLE_GOODSMILE

    product_url_template = 'https://www.goodsmile.info/ja/product/%s/'

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        expr = input('Enter expression (Product IDs): ')
        numbers = cls.get_numbers_from_expression(expr)
        for number in numbers:
            cls.process_product_page(number)

    @classmethod
    def process_product_page(cls, product_id):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url)
            a_tags = soup.find('div', class_='itemPhotos').find_all('a', class_='imagebox')
            for i in range(len(a_tags)):
                if a_tags[i] and a_tags[i].has_attr('href'):
                    image_url = 'https:' + a_tags[i]['href']
                    image_name = '%s_%s.jpg' % (id_, str(i + 1).zfill(2))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
