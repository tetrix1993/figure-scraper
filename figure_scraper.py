from figure_scraper import *


def run():
    websites = Website.__subclasses__()
    while True:
        print('[INFO] Figure Scraper')
        print('[INFO] Select a website to scrape: ')
        number_max_len = len(str(len(websites)))
        for i in range(len(websites)):
            number = i + 1
            number_str = str(number)
            if len(number_str) < number_max_len:
                for j in range(number_max_len - len(number_str)):
                    number_str = ' ' + number_str
            print('%s: %s' % (number_str, websites[i].title))

        zero_str = '0'
        for i in range(number_max_len - 1):
            zero_str = ' ' + zero_str
        print('%s: Exit' % zero_str)

        try:
            choice = int(input('Enter choice: '))
        except:
            print('[ERROR] Invalid choice.')
            continue

        if choice == 0:
            break
        elif choice < 0 or choice > len(websites):
            print('[ERROR] Invalid choice.')
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
