from figure_scraper.website import Website
import figure_scraper.constants as constants


class Animebako(Website):
    base_folder = constants.FOLDER_ANIMEBAKO
    title = constants.WEBSITE_TITLE_ANIMEBAKO
    keywords = ["https://animebako.com/"]

    image_url_template = 'https://animebako.com/cdn/shop/files/%s_1.jpg'

    # https://animebako.com/cdn/shop/files/[JAN CODE]_1.jpg

    @classmethod
    def run(cls):
        cls.init()
        cls.download_by_jancode()

    @classmethod
    def download_by_jancode(cls):
        print('[INFO] %s Scraper' % cls.title)
        while True:
            try:
                expr = input('Enter expression (JAN code without checksum): ').strip()
                numbers = cls.get_sorted_page_numbers(expr)
                if len(numbers) == 0:
                    return
                today = cls.get_today_date()
                print('[INFO] Images will be saved at %s' % (cls.base_folder + '/' + today))
                for number in numbers:
                    try:
                        jancode = cls.complete_jancode(number)
                        if jancode is None or len(jancode) == 0:
                            continue
                    except:
                        print('[ERROR] Failed to complete JAN code: ' + str(number))
                        continue
                    image_url = cls.image_url_template % jancode
                    try:
                        image_name = today + '/' + str(jancode) + '.jpg'
                        cls.download_image(image_url, image_name, try_count=1)
                    except Exception as e:
                        print('[ERROR] Error in downloading %s' % image_url)
                        print(e)
            except Exception as e:
                print('[ERROR] Error in processing')
                print(e)
