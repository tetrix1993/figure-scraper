from figure_scraper.website import Website
import figure_scraper.constants as constants


class Amakuni(Website):
    base_folder = constants.FOLDER_AMAKUNI
    title = constants.WEBSITE_TITLE_AMAKUNI
    keywords = ["http://amakuni.info/"]

    image_name_template = '%s_%s_%s.jpg'
    image_url_template = 'http://amakuni.info/images/item/%s/%s/%s.jpg'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] The image URL is in the form http://amakuni.info/images/item/{year}/{product_id}/{num}.jpg')
            year = input('Enter year: ')
            if len(year) == 0:
                return
            expr = input('Enter expression (Product IDs): ')
            if len(expr) == 0:
                continue
            numbers = cls.get_numbers_from_expression(expr)
            for number in numbers:
                id_ = str(number).zfill(3)
                for i in range(99):
                    if i == 0:
                        num = 'main'
                    else:
                        num = str(i).zfill(3)
                    image_url = cls.image_url_template % (year, id_, num)
                    image_name = cls.image_name_template % (year, id_, str(i).zfill(3))
                    result = cls.download_image(image_url, image_name, print_error_message=False)
                    if result == -1:
                        if i == 0:
                            print('[INFO] Product ID %s not found.' % str(number))
                        break
