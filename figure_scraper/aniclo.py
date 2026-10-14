from figure_scraper.website import Website
import figure_scraper.constants as constants


class Aniclo(Website):
    base_folder = constants.FOLDER_ANICLO
    title = constants.WEBSITE_TITLE_ANICLO
    keywords = ["https://aniclo.jp/"]

    image_url_prefix = 'https://aniclo.jp/cdn/shop/files/'

    # https://aniclo.jp/cdn/shop/files/[JAN CODE].jpg

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
                suffix = input('Enter suffix: ').strip()
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
                    image_url = cls.image_url_prefix + jancode + suffix
                    try:
                        period_idx = suffix.rfind('.')
                        if period_idx > 0:
                            extension = suffix[period_idx + 1:].split('?')[0]
                            image_name = jancode + suffix[:period_idx] + '.' + extension
                        else:
                            image_name = jancode + '.jpg'
                        image_name = today + '/' + image_name
                        cls.download_image(image_url, image_name, try_count=1)
                    except Exception as e:
                        print('[ERROR] Error in downloading %s' % image_url)
                        print(e)
            except Exception as e:
                print('[ERROR] Error in processing')
                print(e)
