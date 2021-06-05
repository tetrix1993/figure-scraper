from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class HobbySearch(Website):
    base_folder = constants.FOLDER_HOBBYSEARCH
    title = constants.WEBSITE_TITLE_HOBBYSEARCH
    keywords = ['https://www.1999.co.jp/']

    page_prefix = 'https://www.1999.co.jp'
    product_url_template = 'https://www.1999.co.jp/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Product Page URL is in the format: https://www.1999.co.jp/{product_id}')
            expr = input('Enter expression (Product IDs): ').strip()
            if len(expr) == 0:
                return
            evaluate = True
            use_jan = False
            while True:
                print('Select name of file to save as: ')
                print('1: Use Product ID as name')
                print('2: Use JAN code as name if possible')
                print('0: Return')

                try:
                    choice = int(input('Enter choice: ').strip())
                    if choice == 1:
                        break
                    elif choice == 2:
                        use_jan = True
                        break
                    elif choice == 0:
                        evaluate = False
                        break
                    else:
                        raise Exception
                except:
                    print('[ERROR] Invalid choice.')
            if evaluate:
                numbers = cls.get_sorted_page_numbers(expr)
                today = cls.get_today_date()
                print('[INFO] Images will be saved at %s' % (cls.base_folder + '/' + today))
                if len(numbers) == 1:
                    cls.process_product_page(numbers[0], use_jan, today)
                elif len(numbers) > 1:
                    max_processes = min(constants.MAX_PROCESSES, len(numbers))
                    if max_processes <= 0:
                        max_processes = 1
                    with Pool(max_processes) as p:
                        results = []
                        for number in numbers:
                            result = p.apply_async(cls.process_product_page, (number, use_jan, today))
                            results.append(result)
                        for result in results:
                            result.wait()

    @classmethod
    def process_product_page(cls, product_id, use_jan=False, folder=None):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        image_name_prefix = id_
        try:
            soup = cls.get_soup(product_url)
            a_tags = soup.find_all('a', {'target': '_blank'})
            a_tag = None
            for tag in a_tags:
                if tag.has_attr('href') and 'image' in tag['href']:
                    a_tag = tag
                    break
            if not a_tag:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return
            if use_jan:
                jan_code = cls.get_jan_code(soup)
                if len(jan_code) > 0:
                    image_name_prefix = jan_code
            image_found = False
            if a_tag:
                gallery_url = cls.page_prefix + a_tag['href']
                gallery_soup = cls.get_soup(gallery_url)
                imgbox2 = gallery_soup.find('span', class_='imgbox2')
                if imgbox2:
                    a_img_tags = imgbox2.find_all('a')
                    if len(a_img_tags) > 0:
                        image_found = True
                        num_max_length = len(str(len(a_img_tags)))
                        for i in range(len(a_img_tags)):
                            if a_img_tags[i].has_attr('onmouseover') and "myChgPic('" in a_img_tags[i]['onmouseover']:
                                image_url = a_img_tags[i]['onmouseover'].split("myChgPic('")[1].split("'")[0]
                                if len(a_img_tags) == 1:
                                    image_name = image_name_prefix + '.jpg'
                                else:
                                    image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                                if folder:
                                    image_name = folder + '/' + image_name
                                cls.download_image(image_url, image_name)
            if not image_found:
                print('[ERROR] Product ID %s does not have image.' % id_)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @staticmethod
    def get_jan_code(soup):
        result = ''
        tr = soup.find('tr', id='masterBody_trJanCode')
        if tr:
            tds = tr.find_all('td')
            if len(tds) > 1:
                result = tds[-1].text
        return result
