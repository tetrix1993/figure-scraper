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
            soup = cls.get_soup(url, impersonate=True)
            a_tags = soup.select('.news_item_thmb a[href]')
            for a_tag in a_tags:
                href_idx = a_tag['href'].rfind('/')
                image_name = a_tag['href'][href_idx + 1:]
                image = a_tag.select('img[src]')
                if len(image) == 0:
                    continue
                idx = image[0]['src'].rfind('/')
                if idx == -1:
                    continue
                image_url = image[0]['src'][0:idx] + '/fit=cover,f=jpg'
                image_name = constants.SUBFOLDER_BELLHOUSE_NEWS + '/' + news_id + '/' + image_name + '.jpg'
                cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % url)
            print(e)

    @classmethod
    def process_product_page(cls, product_id):
        url = cls.product_url_template % product_id
        try:
            soup = cls.get_soup(url, impersonate=True)
            images = soup.select('.main_content_gallery_image img[src]')
            for i in range(len(images)):
                idx = images[i]['src'].rfind('/')
                if idx == -1:
                    continue
                image_url = images[i]['src'][0:idx] + '/fit=cover,f=jpg'
                image_name = constants.SUBFOLDER_BELLHOUSE_IMAGES + '/' + product_id + '_' + str(i + 1) + '.jpg'
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
