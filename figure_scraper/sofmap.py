from figure_scraper.website import Website
import figure_scraper.constants as constants


class Sofmap(Website):
    base_folder = constants.FOLDER_SOFMAP
    title = constants.WEBSITE_TITLE_SOFMAP
    keywords = ["https://a.sofmap.com/"]

    event_prefix = 'https://a.sofmap.com/contents/?id=animega-online&sid='

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] URL is in the form: https://a.sofmap.com/contents/?id=animega-online&sid={event_id}')
            event_id = input('Enter event ID: ').strip()
            if len(event_id) == 0:
                return
            folder = constants.SUBFOLDER_SOFMAP_EVENT + '/' + event_id
            cls.process_event_page(event_id, folder)

    @classmethod
    def process_event_page(cls, event_id, folder):
        event_url = cls.event_prefix + event_id
        try:
            soup = cls.get_soup(event_url)
            images = soup.select('.columnbox img[src]')
            if len(images) == 0:
                print('[INFO] No images found.' % event_id)
                return
            for image in images:
                image_url = image['src']
                if '/large/' not in image_url or not image_url.endswith('.jpg'):
                    continue
                image_name = image_url.split('/')[-1]
                image_url = image_url.replace('/large/', '/pim/').replace('.jpg', '_A01.jpg')
                cls.download_image(image_url, folder + '/' + image_name, try_count=1)
        except Exception as e:
            print('[ERROR] Error in processing event %s' % event_id)
            print(e)
