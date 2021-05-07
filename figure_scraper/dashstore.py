from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class Dashstore(Website):
    base_folder = constants.FOLDER_DASHSTORE
    title = constants.WEBSITE_TITLE_DASHSTORE
    keywords = ["http://dashstore.net/", "Dash Store"]

    page_url_prefix = 'http://dashstore.net/'
    product_page_template = page_url_prefix + 'title_item/%s/'

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        while True:
            print('[INFO] URL is in the form: http://dashstore.net/title_item/{event_id}/')
            event_id = input('Enter event ID: ')
            if len(event_id) == 0:
                return
            cls.process_event_page(event_id)


    @classmethod
    def process_event_page(cls, event_id):
        url = cls.product_page_template % event_id
        print('[INFO] Processing ' + url)
        try:
            soup = cls.get_soup(url)
            images = soup.select('div.gds03 img')
            banner_imgs = soup.select('div.slideimg img')
            if len(banner_imgs) > 0:
                images = [banner_imgs[0]] + images
            max_processes = constants.MAX_PROCESSES
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for image in images:
                    if image.has_attr('src'):
                        image_url = image['src']
                        image_name = image_url.split('/')[-1]
                        result = p.apply_async(cls.download_single_image, (image_url, event_id + '/' + image_name))
                        results.append(result)
                for result in results:
                    result.wait()
        except Exception as e:
            print('[ERROR] Error in processing %s' % url)
            print(e)

    @classmethod
    def download_single_image(cls, image_url, filepath):
        cls.download_image(image_url, filepath)
