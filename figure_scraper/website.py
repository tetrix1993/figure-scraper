import os
import re
import requests
import figure_scraper.constants as constants
from bs4 import BeautifulSoup as bs
from datetime import datetime


class Website:
    base_folder = constants.FOLDER_BASE
    title = constants.WEBSITE_TITLE_BASE
    keywords = []

    @classmethod
    def init(cls):
        if not os.path.exists(cls.base_folder):
            os.makedirs(cls.base_folder)

    @classmethod
    def download_image(cls, url, filename, print_error_message=True, headers=None):
        # Check local directory if the file exists
        filepath = cls.base_folder + '/' + filename
        if os.path.exists(filepath):
            print("[INFO] File exists: " + filepath)
            return 1

        try:
            save_folder = filepath[0: len(filepath) - len(filepath.split('/')[-1]) - 1]
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
        except:
            pass

        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        # Download image:
        try:
            with requests.get(url, stream=True, headers=headers) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            print("[INFO] Downloaded " + url)
            cls.generate_log(url, filepath)
            return 0
        except Exception as e:
            if print_error_message:
                print("[ERROR] Failed to download " + url + ' - ' + str(e))
            return -1

    @classmethod
    def is_image_exists(cls, filename):
        return os.path.exists(cls.base_folder + '/' + filename)

    @staticmethod
    def get_soup(url, headers=None, decode=False):
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        try:
            result = requests.get(url, headers=headers)
            if decode:
                return bs(result.content.decode(), 'html.parser')
            else:
                return bs(result.content, 'html.parser')
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def get_numbers_from_expression(expr):
        results = []

        valid_chars = "0123456789-,"

        for i in expr:
            if i not in valid_chars:
                return []

        split1 = expr.split(",")
        for ex in split1:
            split2 = ex.split("-")
            if len(split2) == 1:
                try:
                    results.append(int(split2[0]))
                except:
                    return []
            elif len(split2) == 2:
                try:
                    first_num = int(split2[0])
                    last_num = int(split2[1])
                    for j in range(first_num, last_num + 1, 1):
                        results.append(j)
                except:
                    return []
            else:
                return []
        return results

    @staticmethod
    def generate_log(url, filepath):
        timenow = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        with open(constants.DOWNLOAD_LOG_FILE, 'a+', encoding='utf-8') as f:
            f.write('%s\t%s\t%s\n' % (timenow, filepath, url))

    @staticmethod
    def clear_resize_in_url(url):
        # Change url in the form http://abc.com/image_name-800x600.jpg to http://abc.com/image-name.jpg
        regex = '(-[0-9]+x[0-9]+.)([A-Za-z]+)$'
        result = re.compile(regex).findall(url)
        if len(result) > 0 and len(result[0]) == 2:
            return url[0:len(url) - len(result[0][0]) - len(result[0][1])] + '.' + result[0][1]
        else:
            return url
