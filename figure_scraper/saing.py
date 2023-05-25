from figure_scraper.website import Website
import figure_scraper.constants as constants


class Saing(Website):
    base_folder = constants.FOLDER_SAING
    title = constants.WEBSITE_TITLE_SAING
    website = "https://www.saing.jp/"
    keywords = [website]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}

    page_prefix = website + 'shopdetail/'
    image_name_template = '%s_%s.jpg'

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        print('[INFO] Product Page URL in the form: ' + cls.website + 'shopdetail/{product_id}/')
        expr = input('Enter expression (Product IDs): ')
        numbers = cls.get_numbers_from_expression(expr)
        for number in numbers:
            id_ = str(number).zfill(12)
            page_url = cls.page_prefix + id_
            try:
                soup = cls.get_soup(page_url, headers=cls.headers)
                images = soup.select('#itemImg .M_imageMain img[src]')
                single_image = False
                if len(images) == 0:
                    images = soup.select('#itemImg img[src]')
                    single_image = True
                if len(images) == 0:
                    print('[INFO] Product ID %s not found.' % str(number))
                    continue
                for i in range(len(images)):
                    image_url = images[i]['src']
                    if len(images) == 1 or single_image:
                        image_name = id_
                    else:
                        image_name = id_ + '_' + str(i + 1)
                    cls.download_image(image_url, image_name + '.jpg', print_error_message=False)
                    if single_image:
                        break
            except:
                print('[ERROR] Error when processing Product ID %s.' % str(number))
                continue
