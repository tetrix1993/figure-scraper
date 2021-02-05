from figure_scraper.website import Website
import figure_scraper.constants as constants


class AniplexPlus(Website):
    base_folder = constants.FOLDER_ANIPLEXPLUS
    title = constants.WEBSITE_TITLE_ANIPLEXPLUS
    keywords = ['https://www.aniplexplus.com']

    product_url_prefix = 'https://www.aniplexplus.com'
    product_url_template = product_url_prefix + '/%s'

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        print('[INFO] Product ID is in the form: https://www.aniplexplus.com/{product_id}')
        product_id = input('Enter Product ID: ')
        if len(product_id) > 0:
            cls.process_product_page(product_id)

    @classmethod
    def process_product_page(cls, product_id):
        product_url = cls.product_url_template % product_id
        try:
            soup = cls.get_soup(product_url)
            uls = soup.find('ul', class_='itemView')
            if uls is None:
                print('[ERROR] Product ID %s does not exists.' % product_id)
                return
            lis = uls.find_all('li', class_='item')
            for i in range(len(lis)):
                image = lis[i].find('img')
                if image and image.has_attr('src'):
                    image_url = cls.product_url_prefix + image['src'].split('?')[0]
                    image_name = '%s_%s.jpg' % (product_id, str(i + 1).zfill(2))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
