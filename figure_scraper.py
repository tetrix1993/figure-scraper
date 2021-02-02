from figure_scraper import *


def run():
    print('Figure Scraper')
    websites = FigureWebsite.__subclasses__()
    while True:
        print('[INFO] Select a website to scrape: ')
        number_max_len = len(str(len(websites)))
        for i in range(len(websites)):
            number = i + 1
            number_str = str(number)
            if len(number_str) < number_max_len:
                for j in range(number_max_len - len(number_str)):
                    number_str = ' ' + number_str
            print('%s: %s' % (number_str, websites[i].title))
        try:
            choice = int(input('Enter choice: '))
        except:
            print('[ERROR] Invalid choice.')
            continue

        if choice <= 0 or choice > len(websites):
            break
        else:
            try:
                print('[INFO] %s selected.' % websites[choice - 1].title)
                websites[choice - 1].run()
            except Exception as e:
                print('[ERROR] Error in executing website')
                print(e)
    print('[INFO] Exiting...')


if __name__ == '__main__':
    run()
