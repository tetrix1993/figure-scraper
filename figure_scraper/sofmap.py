from figure_scraper.website import Website
import figure_scraper.constants as constants


class Sofmap(Website):
    base_folder = constants.FOLDER_SOFMAP
    title = constants.WEBSITE_TITLE_SOFMAP
    keywords = ["https://a.sofmap.com/"]

    event_prefix = 'https://a.sofmap.com/contents/?id=animega-online&sid='
    image_url_template = 'https://image.sofmap.com/images/product/pim/%s_A01.jpg'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Event ID')
            print('2: Download by JAN Code')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.process_event_page()
                elif choice == 2:
                    cls.download_by_jancode()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def process_event_page(cls):
        print('[INFO] URL is in the form: https://a.sofmap.com/contents/?id=animega-online&sid={event_id}')
        event_id = input('Enter event ID: ').strip()
        if len(event_id) == 0:
            return
        folder = constants.SUBFOLDER_SOFMAP_EVENT + '/' + event_id
        event_url = cls.event_prefix + event_id
        try:
            soup = cls.get_soup(event_url)
            images = soup.select('.columnbox img[src]')
            if len(images) == 0:
                print('[INFO] No images found.')
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

    @classmethod
    def download_by_jancode(cls):
        try:
            expr = input('Enter expression (JAN code without checksum): ').strip()
            numbers = cls.get_sorted_page_numbers(expr)
            today = cls.get_today_date()
            if len(numbers) == 0:
                return
            print('[INFO] Images will be saved at %s' % (cls.base_folder + '/' + today))
            for number in numbers:
                try:
                    jancode = cls.complete_jancode(number)
                    if jancode is None or len(jancode) == 0:
                        continue
                except:
                    print('[ERROR] Failed to complete JAN code: ' + str(number))
                    continue
                image_url = cls.image_url_template % str(jancode)
                try:
                    image_name = today + '/' + str(jancode) + '.jpg'
                    cls.download_image(image_url, image_name)
                except Exception as e:
                    print('[ERROR] Error in downloading %s' % image_url)
                    print(e)
        except Exception as e:
            print('[ERROR] Error in processing')
            print(e)
