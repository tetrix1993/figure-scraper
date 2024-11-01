from figure_scraper.website import Website
import figure_scraper.constants as constants
import os
from multiprocessing import Pool


class Midobeyo(Website):
    base_folder = constants.FOLDER_MIDOBEYO
    title = constants.WEBSITE_TITLE_MIDOBEYO
    keywords = ['https://midoccolybeyond.shop-pro.jp/', 'midobeyo']
    product_url_template = 'https://midoccolybeyond.shop-pro.jp/?pid=%s'
    category_url_template = 'https://midoccolybeyond.shop-pro.jp/?mode=cate&cbid=%s&csid=0&sort=p'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            is_scan = False
            is_category = False
            while True:
                print('[INFO] Select choice: ')
                print('1: Download images by Product IDs')
                print('2: Scan product information by Product IDs')
                print('3: Download images by Category ID')
                print('4: Scan product information by Category ID')
                print('0: Return')
                try:
                    choice = int(input('Enter choice: ').strip())
                    if choice == 1:
                        break
                    elif choice == 2:
                        is_scan = True
                        break
                    elif choice == 3:
                        is_category = True
                        break
                    elif choice == 4:
                        is_category = True
                        is_scan = True
                        break
                    elif choice == 0:
                        return
                    else:
                        raise Exception
                except:
                    print('[ERROR] Invalid choice.')

            category_id = ''
            expr = ''

            if not is_category:
                print('[INFO] Product Page URL is in the format: https://midoccolybeyond.shop-pro.jp/?pid={product_id}')
                expr = input('Enter expression (Product IDs): ').strip()
                if len(expr) == 0:
                    return
            else:
                print('[INFO] Category URL is in the format: https://midoccolybeyond.shop-pro.jp/?mode=cate&cbid={category_id}&csid=0&sort=p')
                category_id = input('Enter Category ID: ').strip()
                if len(category_id) == 0:
                    return

            evaluate = True
            use_jan = False
            while True and not is_scan:
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
                if is_category:
                    numbers = cls.get_product_ids_by_category_id(category_id)
                else:
                    numbers = cls.get_sorted_page_numbers(expr)
                if len(numbers) == 0:
                    continue
                today = cls.get_today_date()
                if is_scan:
                    output_file = constants.FILE_MIDOBEYO_SCAN_OUTPUT % today
                    print('The result of the scan is saved at: %s' % output_file)
                    temp_folder = cls.base_folder + '/' + constants.SUBFOLDER_MIDOBEYO_TEMP
                    if not os.path.exists(temp_folder):
                        os.makedirs(temp_folder)
                    if len(numbers) == 1:
                        cls.scan_product_page(numbers[0])
                    else:
                        max_processes = min(constants.MAX_PROCESSES, len(numbers))
                        if max_processes <= 0:
                            max_processes = 1
                        with Pool(max_processes) as p:
                            results = []
                            for number in numbers:
                                result = p.apply_async(cls.scan_product_page, (number, ))
                                results.append(result)
                            for result in results:
                                result.wait()

                    item_list = []
                    for number in numbers:
                        filepath = temp_folder + '/' + str(number)
                        if os.path.exists(filepath):
                            if os.path.exists(filepath):
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    line = f.readline()
                                    split1 = line.replace('\n', '').split('\t')
                                    if len(split1) == 3:
                                        item_list.append({'id': split1[0], 'jan': split1[1], 'title': split1[2]})
                    with open(output_file, 'a+', encoding='utf-8') as f:
                        for item in item_list:
                            f.write('%s\t%s\t%s\n' % (item['id'], item['jan'], item['title']))
                    for number in numbers:
                        filepath = temp_folder + '/' + str(number)
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    if os.path.exists(temp_folder):
                        os.removedirs(temp_folder)
                else:
                    print('[INFO] Images will be saved at %s' % (cls.base_folder + '/' + today))
                    if len(numbers) == 1:
                        cls.process_product_page(numbers[0], use_jan, today)
                    else:
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
        id_ = str(product_id).zfill(11)
        product_url = cls.product_url_template % id_
        image_name_prefix = id_
        try:
            soup = cls.get_soup(product_url)
            images = soup.select('table.box a[target="_blank"] img[src],.detail_img img[src]')
            if use_jan:
                jan_code = cls.get_jan_code(soup)
                if len(jan_code) > 0:
                    image_name_prefix = jan_code
            num_max_length = len(str(len(images)))
            for i in range(len(images)):
                image_url = images[i]['src']
                file_extension = image_url.split('?')[0].split('/')[-1].split('.')[-1]
                if len(file_extension) == 0:
                    file_extension = 'jpg'
                if len(images) == 1:
                    image_name = image_name_prefix + '.' + file_extension
                else:
                    image_name = f'%s_%s.{file_extension}' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                if folder:
                    image_name = folder + '/' + image_name
                cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def scan_product_page(cls, product_id):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        if not os.path.exists(constants.SUBFOLDER_MIDOBEYO_SCAN):
            os.makedirs(constants.SUBFOLDER_MIDOBEYO_SCAN)
        try:
            soup = cls.get_soup(product_url, decode=True, charset='EUC-JP')
            title = cls.get_product_title(soup)
            jan = cls.get_jan_code(soup)
            if len(title) == 0 or len(jan) == 0:
                print('[ERROR] Product ID %s does not exists.' % str(product_id))
                return
            filepath = cls.base_folder + '/' + constants.SUBFOLDER_MIDOBEYO_TEMP + '/' + str(product_id)
            with open(filepath, 'a+', encoding='utf-8') as f:
                f.write('%s\t%s\t%s' % (str(product_id), jan, title))
            print('Processed %s' % product_url)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @staticmethod
    def get_jan_code(soup):
        result = ''
        td = soup.select('table.spec td')
        if len(td) > 0:
            text = td[0].text.strip()
            if len(text) > 12:
                result = text[0:13]
        return result

    @staticmethod
    def get_product_title(soup):
        result = ''
        title = soup.select('.category_title')
        if len(title) > 0:
            return title[0].text.strip()
        return result

    @classmethod
    def get_product_ids_by_category_id(cls, category_id):
        numbers = []
        category_url = cls.category_url_template % category_id
        try:
            soup = cls.get_soup(category_url)
            a_tags = soup.select('.name a[href]')
            for a_tag in a_tags:
                if '=' not in a_tag['href']:
                    continue
                product_id = a_tag['href'].split('=')[-1]
                if len(product_id) > 0:
                    numbers.append(product_id)
        except Exception as e:
            print('[ERROR] Error in processing %s' % category_url)
            print(e)
        return numbers
