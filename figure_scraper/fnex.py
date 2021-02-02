from figure_scraper.figure_website import FigureWebsite


class Fnex(FigureWebsite):
    base_folder = 'download/fnex'
    title = 'F:Nex'

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
