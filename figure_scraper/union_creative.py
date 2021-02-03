from figure_scraper.website import Website
import figure_scraper.constants as constants


class UnionCreative(Website):
    base_folder = constants.FOLDER_UNION_CREATIVE
    title = constants.WEBSITE_TITLE_UNION_CREATIVE

    image_name_template = '%s.jpg'
    image_url_template = 'https://union-creative.jp/photo/item/%s/' + image_name_template

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        expr = input('Enter expression (Image IDs): ')
        numbers = cls.get_numbers_from_expression(expr)
        for number in numbers:
            id_ = str(number)
            for i in range(100):
                if i == 0:
                    num = id_
                else:
                    num = id_ + '_' + str(i)
                image_url = cls.image_url_template % (id_, num)
                image_name = cls.image_name_template % num
                result = cls.download_image(image_url, image_name, print_error_message=False)
                if result == -1:
                    break
