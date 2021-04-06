import sys, getopt
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import quote
from PIL import Image
import re
import time
from datetime import datetime

def storeImg(url: str, output_path: str):
	"""
	Opens the image and store in the output folder.
	"""
	req = Request(url, headers={'User-Agent': 'Mozilla/6.0'})
	err_cnt = 0
	while(err_cnt < 20):
		try:
			img = Image.open(urlopen(req))
			break
		except:
			err_cnt=1 
			time.sleep()

	if err_cnt < 20:
		imgName = 'img_'+datetime.now().strftime("%d%m%Y_%H%M%S%f")+'.jpg'
		try:
			img.save('{}'.format(output_path+imgName))
		except:
			print('Error while saving {} image.'.format(imgName))
	else:
		print('Couldn\'t retrieve image on {}'.format(url))

def FindStoreImgUrl(artwork_links: list, output_path: str):
	"""
	Finds the .jpg url in an artwork page and call the storeImg function.
	"""
	for url in artwork_links:
		err_cnt = 0
		while err_cnt < 20:
			try:
				result = requests.get(url)
				soup = BeautifulSoup(result.content, 'html.parser')
				imgArea = soup.find("div", {"id": "imgArea"})
				imgUrl = imgArea.find("img")['src']
				break

			except:
				err_cnt+=1
				time.sleep(1)

		if err_cnt < 20:
			baseUrl = '/'.join(imgUrl.split('/')[:6])
			imgUrl = '/'.join(imgUrl.split('/')[6:])

			storeImg(baseUrl + '/' + quote(imgUrl), output_path)
		else:
			print('Couldn\'t get image from {}'.format(url))
			
def FindStoreImg(artist: str, output_path: str):
	"""
	Main loop. It scraps an artnet artist's page to find all of his artworks' pages.
	"""
	curr_page = 0
	last_page = False

	fail_cnt = 0
	cnt = 0

	while (not last_page):
		curr_page+=1
		url = 'https://www.artnet.com/artistes/'+artist+'/'+str(curr_page)
		artwork_links_arr = []

		# Access the url
		try:
			result = requests.get(url)
			fail_cnt = fail_cnt-1 if fail_cnt>0 else 0
		except:
			print('Error while accessing the page.')
			fail_cnt+=1
			continue

		if result.status_code == 200:
			soup = BeautifulSoup(result.content, 'html.parser')

			previous_link = ''
			# Loop over the links that match an artwork page
			artwork_links = soup.find("div", {"class": "row results artworks"}).findAll('a', attrs={'class':'details-link'})
			#soup.findAll('a',	attrs={'href': re.compile("^/artistes/{}.+[a-zA-Z0-9-]+/.+[a-z]+.+[0-9]+".format(artist.split('-')[0]))})
			for link in artwork_links:
				link = link.get('href')
				print(link)
				# Links appear twice in the source ode
				if link != previous_link:
					artwork_links_arr.append('https://www.artnet.com'+link)
					previous_link = link
			
			cnt+=len(artwork_links_arr)

			
			FindStoreImgUrl(artwork_links_arr, output_path)

			print('{} images scrapped so far...'.format(cnt), end = '\r')

	if fail_cnt >= 20:
		print('Error while accessing the web page. Stopped at {}th iteration.'.format(curr_page))
	
	print('{} images saved.'.format(cnt))


def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hn:f:", ["name=", "img_folder="])
	except getopt.GetoptError:
		print('usage: artnet_scrapper.py -n <artist-name> -f <image folder>')
		sys.exit(2)
	
	for opt, arg in opts:
		if opt == '-h':
			print('usage: artnet_scrapper.py -n <artist-name> -f <image folder>\nExample: artnet_scrapper.py -n gustave-klimt -f img/')
			sys.exit()
		
		elif opt in ('-n', '--name'):
			artist = arg

		elif opt in ('-f', '--img_folder'):
			img_folder = arg

	try:
		print('Searching for {} art pieces on artnet. The images will be stored in {} folder.'.format(artist, img_folder))
	except:
		print('usage: artnet_scrapper.py -n <artist-name> -f <image folder>\nExample: artnet_scrapper.py -n gustave-klimt -f img/')
		sys.exit(2)

	FindStoreImg(artist, img_folder)


if __name__ == "__main__":
	main(sys.argv[1:])
