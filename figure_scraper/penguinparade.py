from figure_scraper.website import Website
import figure_scraper.constants as constants


class PenguinParade(Website):
    base_folder = constants.FOLDER_PENGUINPARADE
    title = constants.WEBSITE_TITLE_PENGUINPARADE
    keywords = ["http://www.penguinparade.jp/"]

    image_name_template = '%s_%s.jpg'
    image_url_template = 'http://webftp1.makeshop.jp/shopimages/ONME007018/%s_%s.jpg'

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        print('[INFO] Product Page URL in the form: http://www.penguinparade.jp/shopdetail/{product_id}/')
        expr = input('Enter expression (Product IDs): ')
        numbers = cls.get_numbers_from_expression(expr)
        for number in numbers:
            id_ = str(number).zfill(12)
            for i in range(99):
                image_url = cls.image_url_template % (str(i), id_)
                image_name = cls.image_name_template % (str(number), str(i))
                result = cls.download_image(image_url, image_name, print_error_message=False)
                if result == -1:
                    if i == 0:
                        print('[INFO] Product ID %s not found.' % str(number))
                    break
