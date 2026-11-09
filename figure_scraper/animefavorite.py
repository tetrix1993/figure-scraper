from figure_scraper.website import Website
import figure_scraper.constants as constants


class AnimeFavorite(Website):
    base_folder = constants.FOLDER_ANIMEFAVORITE
    title = constants.WEBSITE_TITLE_ANIMEFAVORITE
    keywords = ["https://www.animefavorite.com/"]

    prefix = 'https://www.animefavorite.com/shopdetail/'

    image_url_template = 'https://makeshop-multi-images.akamaized.net/gencoshop/shopimages/%s/%s/%s_%s.%s'

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
            print('[INFO] Select options: ')
            print('1: Download by processing product page')
            print('2: Download by item url')
            choice = input('Enter choice: ')
            if choice == '1':
                cls.process_product_page(numbers, folder)
            elif choice == '2':
                cls.process_item_url(numbers, folder)

    @classmethod
    def process_product_page(cls, numbers, folder=None):
        for number in numbers:
            id_ = str(number).zfill(12)
            try:
                page_url = cls.prefix + id_
                soup = cls.get_soup(page_url)
                images = soup.select('.slider-slide img[src]')
                for i in range(len(images)):
                    image_url = images[i]['src'].split('?')[0]
                    image_name = image_url.split('/')[-1]
                    img_ext = image_name.split('.')[1]
                    if len(images) == 1:
                        img_name = id_
                    else:
                        img_name = id_ + '_' + str(i + 1)
                    cls.download_image(image_url, folder + '/' + img_name + '.' + img_ext)
            except Exception as e:
                print('[ERROR] Error in processing %s' % id_)
                print(e)

    @classmethod
    def process_item_url(cls, numbers, folder=None):
        for number in numbers:
            expr = input(f'Enter expression (item numbers) for {str(number)}: ')
            if len(expr) == 0:
                continue
            img_nums = cls.get_numbers_from_expression(expr)
            if len(img_nums) == 0:
                continue
            ext = input('Enter file extension (e.g. jpg): ')
            id_ = str(number).zfill(12)
            for img_num in img_nums:
                try:
                    image_url = cls.image_url_template % (id_[-2:], id_[-4:-2], str(img_num), id_, ext)
                    img_name = id_ + '_' + str(img_num) + '.' + ext
                    cls.download_image(image_url, folder + '/' + img_name)
                except Exception as e:
                    print('[ERROR] Error in processing %s' % id_)
                    print(e)
