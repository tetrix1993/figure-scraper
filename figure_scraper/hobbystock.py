from figure_scraper.website import Website
import figure_scraper.constants as constants


class HobbyStock(Website):
    base_folder = constants.FOLDER_HOBBYSTOCK
    title = constants.WEBSITE_TITLE_HOBBYSTOCK
    keywords = ["http://www.hobbystock.jp/"]

    product_url_template = 'http://www.hobbystock.jp/item/view/%s'

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        print('[INFO] Product Page URL is in the format: http://www.hobbystock.jp/item/view/{prefix}-{id}')
        prefix = input('Enter prefix (e.g. hso-ccg): ').strip().lower()
        if len(prefix) == 0:
            return
        expr = input('Enter expression (Product IDs): ').strip()
        if len(expr) == 0:
            return
        numbers = cls.get_numbers_from_expression(expr)
        for number in numbers:
            cls.process_product_page(prefix, number)

    @classmethod
    def process_product_page(cls, prefix, product_id):
        id_ = prefix + '-' + str(product_id).zfill(8)
        product_url = cls.product_url_template % id_
        try:
            soup = cls.get_soup(product_url)
            div = soup.find('div', class_='imageList')
            if div:
                images = div.find_all('img')
                num_max_length = len(str(len(images)))
                for i in range(len(images)):
                    if images[i].has_attr('src'):
                        image_url = images[i]['src']
                        if len(images) == 1:
                            image_name = id_ + '.jpg'
                        else:
                            image_name = '%s_%s.jpg' % (id_, str(i + 1).zfill(num_max_length))
                        cls.download_image(image_url, image_name)
            else:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return

        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
