from figure_scraper.website import Website
import figure_scraper.constants as constants


class Goodsmile(Website):
    base_folder = constants.FOLDER_GOODSMILE
    title = constants.WEBSITE_TITLE_GOODSMILE
    keywords = ["https://www.goodsmile.info/", "https://www.goodsmile.com/"]

    product_url_template_old = 'https://www.goodsmile.info/ja/product/%s/'
    product_url_template = 'https://www.goodsmile.com/ja/product/%s'
    prefix = 'https://www.goodsmile.com'

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
            images = soup.select('.c-photo-variable-grid__photo img[src]')
            for i in range(len(images)):
                image_url = cls.prefix + images[i]['src']
                image_name = id_ + '_' + str(i + 1).zfill(2) + '.jpg'
                cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def process_product_page_old(cls, product_id):
        id_ = str(product_id)
        product_url = cls.product_url_template_old % id_
        try:
            soup = cls.get_soup(product_url)
            item_photos = soup.find('div', class_='itemPhotos')
            if item_photos is None:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return
            a_tags = soup.find('div', class_='itemPhotos').find_all('a', class_='imagebox')
            for i in range(len(a_tags)):
                if a_tags[i] and a_tags[i].has_attr('href'):
                    image_url = 'https:' + a_tags[i]['href']
                    image_name = '%s_%s.jpg' % (id_, str(i + 1).zfill(2))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
