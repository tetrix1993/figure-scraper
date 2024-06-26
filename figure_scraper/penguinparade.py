from figure_scraper.website import Website
import figure_scraper.constants as constants


class PenguinParade(Website):
    base_folder = constants.FOLDER_PENGUINPARADE
    title = constants.WEBSITE_TITLE_PENGUINPARADE
    keywords = ["http://www.penguinparade.jp/"]

    prefix = 'https://www.penguinparade.jp/shopdetail/'
    admin_id = 'ONME007018'
    image_name_template = '%s_%s.jpg'
    image_url_template = f'http://webftp1.makeshop.jp/shopimages/{admin_id}/%s_%s.jpg'
    product_url_template = 'http://www.penguinparade.jp/shopdetail/%s/'
    image_list_template = f'http://webftp1.makeshop.jp/addimg/viewimageiframeimg.html?adminuser={admin_id}&brandcode=%s&maxsize=400&multi_image_display_type=1'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Host': 'www.penguinparade.jp'
    }

    @classmethod
    def run(cls):
        cls.init()
        print('[INFO] %s Scraper' % cls.title)
        print('[INFO] Product Page URL in the form: http://www.penguinparade.jp/shopdetail/{product_id}/')
        while True:
            expr = input('Enter expression (Product IDs): ')
            if len(expr) == 0:
                return
            numbers = cls.get_numbers_from_expression(expr)
            folder = cls.get_today_date()
            result = cls.get_use_jan_choice()
            if result == 0:
                cls.process_product_page_without_jan(numbers, folder)
            elif result == 1:
                cls.process_product_page_with_jan(numbers, folder)
            else:
                continue

    @classmethod
    def process_product_page_without_jan(cls, numbers, folder=None):
        for number in numbers:
            id_ = str(number).zfill(12)
            try:
                page_url = cls.prefix + id_
                soup = cls.get_soup(page_url, headers=cls.headers)
                images = soup.select('.M_imageWrap>div>a img[src]')
                for image in images:
                    image_url = image['src'].split('?')[0]
                    if '/shopimages/' in image_url:
                        image_name = image_url.split('/shopimages/')[1].replace('/', '_')
                    else:
                        image_name = image_url.split('/')[-1]
                    cls.download_image(image_url, folder + '/' + image_name)
            except Exception as e:
                print('[ERROR] Error in processing %s' % id_)
                print(e)

            '''
            for i in range(99):
                image_url = cls.image_url_template % (str(i), id_)
                image_name = cls.image_name_template % (str(number), str(i))
                if folder:
                    image_name = folder + '/' + image_name
                result = cls.download_image(image_url, image_name, print_error_message=False)
                if result == -1:
                    if i == 0:
                        print('[INFO] Product ID %s not found.' % str(number))
                    break
            '''

    @classmethod
    def process_product_page_with_jan(cls, numbers, folder=None):
        for number in numbers:
            id_ = str(number).zfill(12)
            product_url = cls.product_url_template % id_
            jan_codes = []
            image_count = 0
            try:
                soup = cls.get_soup(product_url, headers=cls.headers, decode=True, charset='EUC-JP')
                if soup is not None:
                    items = soup.select('.detailTxt')
                    if len(items) > 0:
                        jan_codes = cls.get_jan_codes(items[0].contents[0].text)
                img_soup = cls.get_soup(cls.image_list_template % id_, headers=cls.headers, decode=True, charset='EUC-JP')
                if img_soup is not None:
                    image_count = len(img_soup.select('img[src]'))
            except Exception as e:
                print('[ERROR] Error in processing %s' % product_url)
                print(e)
            if len(jan_codes) == 0 or image_count == 0 or (len(jan_codes) != image_count and len(jan_codes) != 1):
                cls.process_product_page_without_jan([number], folder)
                continue

            for i in range(image_count):
                image_url = cls.image_url_template % (str(i), id_)
                if len(jan_codes) == 1:
                    image_name = cls.image_name_template % (jan_codes[0], str(i))
                else:
                    image_name = jan_codes[i] + '.jpg'
                if folder:
                    image_name = folder + '/' + image_name
                result = cls.download_image(image_url, image_name, print_error_message=False)
                if result == -1:
                    if i == 0:
                        print('[INFO] Product ID %s not found.' % str(number))
                    break

    @classmethod
    def get_jan_codes(cls, text):
        if 'JAN：' not in text:
            return []
        splits = text.split('JAN：')[1].split('\r\n')
        results = []
        for s in splits:
            if '：' in s:
                result = s.split('：')[1].strip()
            else:
                result = s.strip()
            if len(result) == 0:
                continue
            results.append(result)
        return results
