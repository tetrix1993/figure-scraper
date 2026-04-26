from figure_scraper.website import Website
import figure_scraper.constants as constants


class KujiRoad(Website):
    base_folder = constants.FOLDER_KUJIROAD
    title = constants.WEBSITE_TITLE_KUJIROAD
    keywords = ["kujiroad"]

    product_url_prefix = 'https://kujiroad-portal.com/'
    product_url_template = product_url_prefix + 'products/%s/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter page name: ')
            if len(expr) == 0:
                return

            cls.process_product_page(expr)

    @classmethod
    def process_product_page(cls, page):
        page_url = cls.product_url_template % page
        try:
            soup = cls.get_soup(page_url)
            images = soup.select('.productDetail__heroImg img[src],.productDetail__lineupSpeImg img[src],.productDetail__lineupsSubimg--imgLink img[src]')
            if len(images) == 0:
                print(f'[ERROR] {page_url} does not exists.')
                return
            for image in images:
                image_url = cls.clear_resize_in_url(image['src'])
                image_name = image_url.split('/')[-1]
                cls.download_image(image_url, page + '/' + image_name)
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')
