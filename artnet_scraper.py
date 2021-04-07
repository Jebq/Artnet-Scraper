import sys, getopt
import os
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import quote
from PIL import Image
import time
from datetime import datetime


def storeImg(url: str, output_path: str) -> None:
    """
    Opens the image and store in the output folder.
    """
    req = Request(url, headers={'User-Agent': 'Mozilla/6.0'})
    try:
        img = Image.open(urlopen(req))
        imgName = 'img_' + datetime.now().strftime("%d%m%Y_%H%M%S%f") + '.jpg'
        img.save(f'{output_path + imgName}')
    except:
        time.sleep(0.1)


def FindStoreImgUrl(artwork_links: list, output_path: str) -> None:
    """
    Finds the .jpg url in an artwork page and call the storeImg function.
    """
    total = len(artwork_links)
    for i, url in enumerate(artwork_links):
        try:
            result = requests.get(url)
            soup = BeautifulSoup(result.content, 'html.parser')
            imgArea = soup.find("div", {"id": "imgArea"})
            imgUrl = imgArea.find("img")['src']
            baseUrl = '/'.join(imgUrl.split('/')[:6])
            imgUrl = '/'.join(imgUrl.split('/')[6:])
            storeImg(baseUrl + '/' + quote(imgUrl), output_path)
        except:
            time.sleep(0.1)

        percent = 100.0 * i / total
        sys.stdout.write('\r')
        sys.stdout.write("Completed: [{:{}}] {:>3}%".format('='*int(percent/(100.0/50)+5), 50, int(percent)+5))  # this needs fixing in future
        sys.stdout.flush()


def FindStoreImg(artist: str, output_path: str) -> None:
    """
    Main loop. It scraps an artnet artist's page to find all of his artworks' pages.
    """
    curr_page = 0
    last_page = False

    fail_cnt = 0
    cnt = 0

    while (not last_page):
        curr_page += 1
        print(f'Scraping images from page: {str(curr_page)}')
        url = f'https://www.artnet.com/artistes/{artist}/{str(curr_page)}'
        artwork_links_arr = []

        # Access the url
        try:
            result = requests.get(url)
            fail_cnt = fail_cnt - 1 if fail_cnt > 0 else 0
        except:
            print('Error while accessing the page.')
            fail_cnt += 1
            continue

        if result.status_code == 200:
            soup = BeautifulSoup(result.content, 'html.parser')

            previous_link = ''
            # Loop over the links that match an artwork page
            artwork_links = soup.find("div", {"class": "row results artworks"}).findAll('a', attrs={'class': 'details-link'})

            for link in artwork_links:
                link = link.get('href')
                # Links appear twice in the source ode
                if link != previous_link:
                    artwork_links_arr.append('https://www.artnet.com' + link)
                    previous_link = link

            cnt += len(artwork_links_arr)

            FindStoreImgUrl(artwork_links_arr, output_path)
            print('')
            print(f'{cnt} images scraped so far.')

        elif result.status_code == 404:
            print('404 error.')
            fail_cnt += 1

    if fail_cnt >= 10:
        print(f'\nError while accessing the web page. Stopped at {curr_page}th iteration.')

    print('\n{} images saved.'.format(cnt))


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hn:f:", ["name=", "img_folder="])
    except getopt.GetoptError:
        print('usage: artnet_scraper.py -n <artist-name> -f <image folder>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('usage: artnet_scraper.py -n <artist-name> -f <image folder>\nExample: artnet_scraper.py -n gustave-klimt -f img/')
            sys.exit()

        elif opt in ('-n', '--name'):
            artist = arg

        elif opt in ('-f', '--img_folder'):
            img_folder = arg

    try:
        if not os.path.exists(img_folder):
            print(f'{img_folder} doesn\'t exist - creating it.')
            os.mkdir(img_folder)

        print(f'Searching for {artist} art pieces on artnet. The images will be stored in {img_folder} folder.')

    except:
        print('usage: artnet_scraper.py -n <artist-name> -f <image folder>\nExample: artnet_scraper.py -n gustave-klimt -f img/')
        sys.exit(2)

    FindStoreImg(artist, img_folder)


if __name__ == "__main__":
    main(sys.argv[1:])
