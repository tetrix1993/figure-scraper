from figure_scraper.website import Website
import figure_scraper.constants as constants


class LibertasDream(Website):
    base_folder = constants.FOLDER_LIBERTASDREAM
    title = constants.WEBSITE_TITLE_LIBERTASDREAM
    keywords = ["https://libertasdream.com/"]

    image_url_prefix = 'https://libertasdream.com/cdn/shop/files/'

    @classmethod
    def run(cls):
        cls.init()
        cls.download_by_jancode()

    @classmethod
    def download_by_jancode(cls):
        print('[INFO] %s Scraper' % cls.title)
        print('URL Template: https://libertasdream.com/cdn/shop/files/{prefix}{num}.webp')
        while True:
            try:
                print('Template Choice')
                print('1: https://libertasdream.com/cdn/shop/files/{prefix}{num1}.webp')
                print('2: https://libertasdream.com/cdn/shop/files/{prefix}{num4}{suffix}.webp')
                choice = input('Enter choice: ').strip()
                if len(choice) == 0:
                    return
                if choice != '1' and choice != '2':
                    continue
                prefix = input('Enter prefix: ').strip()
                if len(prefix) == 0:
                    return
                expr = input('Enter expression: ').strip()
                numbers = cls.get_sorted_page_numbers(expr)
                if len(numbers) == 0:
                    continue

                suffix = ''
                if choice == '2':
                    suffix = input('Enter suffix: ').strip()
                today = cls.get_today_date()
                print('[INFO] Images will be saved at %s' % (cls.base_folder + '/' + today))
                for number in numbers:

                    if choice == '1':
                        image_name = prefix + str(number) + suffix + '.webp'
                    elif choice == '2':
                        image_name = prefix + str(number).zfill(4) + suffix + '.webp'
                    else:
                        return
                    image_url = cls.image_url_prefix + image_name
                    try:
                        cls.download_image(image_url, today + '/' + image_name, try_count=1)
                    except Exception as e:
                        print('[ERROR] Error in downloading %s' % image_url)
                        print(e)
            except Exception as e:
                print('[ERROR] Error in processing')
                print(e)
