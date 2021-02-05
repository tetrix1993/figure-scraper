from figure_scraper.website import Website
import figure_scraper.constants as constants


class BellHouse(Website):
    base_folder = constants.FOLDER_BELLHOUSE
    title = constants.WEBSITE_TITLE_BELLHOUSE
    keywords = ["https://bellhouse-shop.com/"]

    news_url_template = 'https://bellhouse-shop.com/news/%s'
    product_url_template = 'https://bellhouse-shop.com/items/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by item ID')
            print('2: Download items by news ID')
            print('0: Exit')
            try:
                choice = int(input('Enter choice: ').strip())
                if choice == 1:
                    print('[INFO] Page Format: https://bellhouse-shop.com/items/{item_id}')
                    item_ids = input('Enter item IDs (if multiple, separate by comma): ').strip()
                    if len(item_ids) == 0:
                        continue
                    for item_id in item_ids.split(','):
                        cls.process_product_page(item_id)
                elif choice == 2:
                    print('[INFO] Page Format: https://bellhouse-shop.com/news/{news_id}')
                    news_ids = input('Enter news ID (if multiple, separate by comma): ').strip()
                    if len(news_ids) == 0:
                        continue
                    for news_id in news_ids.split(','):
                        cls.process_news_page(news_id)
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid choice.')

    @classmethod
    def process_news_page(cls, news_id):
        url = cls.news_url_template % news_id
        try:
            soup = cls.get_soup(url)
            p_tags = soup.find_all('p', class_='news_item_thmb')
            for tag in p_tags:
                a_tag = tag.find('a')
                image = tag.find('img')
                if a_tag and image and a_tag.has_attr('href') and image.has_attr('src'):
                    image_url = cls.get_full_image_url(image['src'])
                    image_name = constants.SUBFOLDER_BELLHOUSE_NEWS + '/' + news_id + '/'\
                        + a_tag['href'].split('/')[-1] + '.jpg'
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % url)
            print(e)

    @classmethod
    def process_product_page(cls, product_id):
        url = cls.product_url_template % product_id
        try:
            soup = cls.get_soup(url)
            div = soup.find('div', class_='main_content_gallery_image')
            if div:
                image = div.find('img')
                if image and image.has_attr('src'):
                    image_url = cls.get_full_image_url(image['src'])
                    image_name = constants.SUBFOLDER_BELLHOUSE_IMAGES + '/' + product_id + '.jpg'
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % url)
            print(e)

    @staticmethod
    def get_full_image_url(url):
        split1 = url.split('/')
        split_skip = []
        for i in range(len(split1)):
            if 'c!' in split1[i] or 'w=' in split1[i]:
                split_skip.append(i)
        image_url = ''
        for i in range(len(split1)):
            if i in split_skip:
                continue
            image_url += split1[i]
            if i < len(split1) - 1:
                image_url += '/'
        return image_url
