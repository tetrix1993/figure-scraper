from figure_scraper.kujibikido import Website
import figure_scraper.constants as constants


class OnlineKujira(Website):
    base_folder = constants.FOLDER_ONLINEKUJIRA
    title = constants.WEBSITE_TITLE_ONLINEKUJIRA
    keywords = ["https://onlinekujira.com/"]

    product_url_prefix = 'https://onlinekujira.com/'
    product_url_template = product_url_prefix + 'lp/%s/'

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
            images = soup.select('.kvArea img, .itemLineup .prizeList img, .specialimage img')
            if len(images) == 0:
                print(f'[ERROR] {page_url} does not exists.')
                return
            for image in images:
                if image.has_attr('src') and image['src'].startswith('img'):
                    image_url = page_url + image['src']
                    image_name = image_url.split('/')[-1]
                    cls.download_image(image_url, page + '/' + image_name)
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')
