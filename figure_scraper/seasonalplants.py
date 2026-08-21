from figure_scraper.website import Website
import figure_scraper.constants as constants


class SeasonalPlants(Website):
    base_folder = constants.FOLDER_SEASONALPLANTS
    title = constants.WEBSITE_TITLE_SEASONALPLANTS
    keywords = ["http://www.seasonal-plants.co.jp/"]

    event_page_template = 'http://www.seasonal-plants.co.jp/event/%s/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter event page name: ')
            if len(expr) == 0:
                return

            cls.process_product_page(expr)

    @classmethod
    def process_product_page(cls, page):
        event_page_prefix = cls.event_page_template % page
        page_url = event_page_prefix + 'index.html'
        try:
            soup = cls.get_soup(page_url)
            images = soup.select('.galleryList img[src^="goods/"]')
            if len(images) == 0:
                print(f'[ERROR] {page_url} does not exists.')
                return
            for image in images:
                image_url = event_page_prefix + image['src']
                image_name = image['src'].split('/')[-1]
                cls.download_image(image_url, page + '/' + image_name)
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')
