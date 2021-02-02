from figure_scraper.figure_website import FigureWebsite


class WaveCorporation(FigureWebsite):
    base_folder = 'download/wave'
    title = 'Wave Corporation'

    image_url_template_prefix = 'https://www.hobby-wave.com/wp-content/uploads/'
    image_url_template = image_url_template_prefix + '%s/%s/%s.jpg'
    image_url_pattern = 'https://www.hobby-wave.com/wp-content/uploads/{year}/{month}/{name}[-][num].jpg'
    product_page_prefix = 'https://www.hobby-wave.com/products/'
    product_page_pattern = product_page_prefix + '{product_id}/'

    @classmethod
    def run(cls):
        cls.init()
        print('1: Download by product ID (coming soon)')
        print('2: Download by guessing the image URL')
        try:
            choice = int(input('[INFO] Enter choice: '))
            if choice == 1:
                cls.download_by_product_id()
            elif choice == 2:
                cls.guess_url()
            else:
                raise Exception
        except:
            print('[ERROR] Invalid option.')
            return

    @classmethod
    def download_by_product_id(cls):
        print('Product Page URL is in the format: %s' % cls.product_page_pattern)
        product_id = input('Enter product ID: ').strip()
        product_url = cls.product_page_prefix + product_id
        try:
            soup = cls.get_soup(product_url)
            ul = soup.find('ul', class_='slides')
            if ul:
                lis = ul.find_all('li')
                for i in range(len(lis)):
                    a_tag = lis[i].find('a')
                    if a_tag and a_tag.has_attr('href'):
                        image_url = a_tag['href']
                        image_name = 'images/%s_%s.jpg' % (product_id, str(i + 1).zfill(2))
                        cls.download_image(image_url, image_name, print_error_message=False)
        except:
            print('[ERROR] Error in processing %s' % product_url)

    @classmethod
    def guess_url(cls):
        print('Image URL is in the format %s' % cls.image_url_pattern)
        year = input('Enter year: ')
        month = input('Enter month (e.g. 1 for January, 12 for December): ').zfill(2)
        for i in range(99):
            for j in range(99):
                if j == 0:
                    image_num = str(i + 1).zfill(2)
                else:
                    image_num = str(i + 1).zfill(2) + '-' + str(j)
                image_url = cls.image_url_template % (year, month, image_num)
                image_name = 'guess/%s/%s/%s.jpg' % (year, month, image_num)
                result = cls.download_image(image_url, image_name, print_error_message=False)
                if result == -1:
                    if j == 0:
                        return
                    break
