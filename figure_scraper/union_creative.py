from figure_scraper.figure_website import FigureWebsite


class UnionCreative(FigureWebsite):
    base_folder = 'download/union-creative'
    title = 'Union Creative'

    image_name_template = '%s.jpg'
    image_url_template = 'https://union-creative.jp/photo/item/%s/' + image_name_template

    @classmethod
    def run(cls):
        cls.init()
        expr = input('Enter expression (Image IDs): ')
        numbers = cls.get_numbers_from_expression(expr)
        for number in numbers:
            id = str(number)
            for i in range(100):
                if i == 0:
                    num = id
                else:
                    num = id + '_' + str(i)
                image_url = cls.image_url_template % (id, num)
                image_name = cls.image_name_template % num
                result = cls.download_image(image_url, image_name, print_error_message=False)
                if result == -1:
                    break
