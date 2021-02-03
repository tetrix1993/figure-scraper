from figure_scraper.website import Website
import figure_scraper.constants as constants


class Kotobukiya(Website):
    base_folder = constants.FOLDER_KOTOBUKIYA
    title = constants.WEBSITE_TITLE_KOTOBUKIYA

    page_prefix = 'https://www.kotobukiya.co.jp'
    product_url_template = page_prefix + '/product/product-%s/'

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
        id_ = str(product_id).zfill(10)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url)
            lis = soup.find_all('li', class_='slideshow-item')
            if len(lis) == 0:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return
            for i in range(len(lis)):
                a_tag = lis[i].find('a')
                if a_tag and a_tag.has_attr('href'):
                    image_url = cls.clear_resize_in_url(cls.page_prefix + a_tag['href'])
                    image_name = '%s_%s.jpg' % (id_, str(i + 1).zfill(2))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
