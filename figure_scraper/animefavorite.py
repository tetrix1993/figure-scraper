from figure_scraper.website import Website
import figure_scraper.constants as constants


class AnimeFavorite(Website):
    base_folder = constants.FOLDER_ANIMEFAVORITE
    title = constants.WEBSITE_TITLE_ANIMEFAVORITE
    keywords = ["https://www.animefavorite.com/"]

    prefix = 'https://www.animefavorite.com/shopdetail/'

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        print('[INFO] Product Page URL in the form: https://www.animefavorite.com/shopdetail/{product_id}/')
        while True:
            expr = input('Enter expression (Product IDs): ')
            if len(expr) == 0:
                return
            numbers = cls.get_numbers_from_expression(expr)
            if len(numbers) == 0:
                continue
            folder = cls.get_today_date()
            cls.process_product_page(numbers, folder)

    @classmethod
    def process_product_page(cls, numbers, folder=None):
        for number in numbers:
            id_ = str(number).zfill(12)
            try:
                page_url = cls.prefix + id_
                soup = cls.get_soup(page_url)
                images = soup.select('.slider-slide .M_imageMainList-item img[src]')
                for image in images:
                    image_url = image['src'].split('?')[0]
                    image_name = image_url.split('/')[-1]
                    split1_ = image_name.split('.')
                    split1_name = split1_[0]
                    img_ext = split1_[1]
                    split2_ = split1_name.split('_')
                    img_name = split2_[1] + '_' + split2_[0]
                    cls.download_image(image_url, folder + '/' + img_name + '.' + img_ext)
            except Exception as e:
                print('[ERROR] Error in processing %s' % id_)
                print(e)
