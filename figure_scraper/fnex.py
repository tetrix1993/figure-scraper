from figure_scraper.website import Website
import figure_scraper.constants as constants


class Fnex(Website):
    base_folder = constants.FOLDER_FNEX
    title = constants.WEBSITE_TITLE_FNEX

    image_name_template = 'fnx%s_%s.jpg'
    image_url_template = 'https://df73htivstjso.cloudfront.net/upload/save_image/' + image_name_template

    @classmethod
    def run(cls):
        cls.init()
        expr = input('Enter expression (Image IDs): ')
        numbers = cls.get_numbers_from_expression(expr)
        for number in numbers:
            id = str(number).zfill(3)
            for i in range(99):
                num = str(i + 1).zfill(2)
                image_url = cls.image_url_template % (id, num)
                image_name = cls.image_name_template % (id, num)
                result = cls.download_image(image_url, image_name, print_error_message=False)
                if result == -1:
                    break
