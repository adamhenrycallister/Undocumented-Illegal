import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from textblob import TextBlob
import pandas as pd


def corpusScraper(website):
	"""Scrapes data from the Corpus of Contemporary American English (COCA)
		To get the website for your search, follow these steps:
			1) go to https://www.english-corpora.org/coca/
			2) click on "not logged in" or the yellow person icon
			3) click on register 
			4) Register for an account
			5) Do a search while logged in to your account
			6) Go to Account tab
			7) click on see history
			8) click on the check mark under "Share Link" for the particular search you're interested in
			9) copy the link and pass it as an argument to this function
		Note: the link will not work indefinitely, you may have to go back and retrieve a new version from "Share Link" every once in a while
	"""

	#Chrome driver with selenium 
	browser = webdriver.Chrome()

	#Open COCA website with specific search results
	try:
		browser.get(website)

		#Navigate to search term and click it to see results
		try:
			frame2 = browser.find_elements_by_name('x2')[0]
			browser.switch_to.frame(frame2)
			word = browser.find_elements_by_xpath("//a[@target='x3']")[3]
			name = word.text
			word.click()

		#Error will raise if you enter a website that doesn't work--including a COCA link that just goes to the homepage insted of to the search results
		except:
			print("Update website link")
			raise

		#Switch frames to get to search results data
		try:
			browser.switch_to.window(browser.current_window_handle)
			frame3 = browser.find_elements_by_name('x3')[0]
			browser.switch_to.frame(frame3)

		except NoSuchElementException:
			print("Couldn't find frame :/")
			raise

		#Keep track of description, polarity of description, subjectivity of description, year, source, and source type for each instance
		descriptions = []
		polarity = []
		subjectivity = []
		years = []
		source = []
		types = []

		#Possible source types
		possible_types = re.compile(r"MAG|NEWS|SPOK|ACAD|FIC")
		# ['MAG', 'NEWS', 'SPOK', 'ACAD', 'FIC']

		#Make sure it's a year
		year_check = re.compile(r"^(1|2)[0-9][0-9][0-9]$")

		#Make sure it's a source
		source_check = re.compile(r".*([a-z]|\_|[A-Z]).*")


		#use Beautiful Soup html parser on search results data
		soup = BeautifulSoup(browser.page_source, "html.parser")

		#tags with the context in which the term was used for each instance
		description_tags = soup.find_all('span', id = True)

		#tags with either the year or the source of the instance
		year_source_tags = soup.find_all('a', href = True, target = 'x4')

		#iterate through description tags to pull out context, polarity score, and subjectivity score
		for x in description_tags:
			#context
			text = str(x.text).replace('\xa0\xa0','')
			if (text != 'CLICK FOR MORE CONTEXT') & (text != 'A') & (text != 'B') & (text != 'C') & (len(text) > 20):
				#context
				descriptions.append(text)
				#calculate polarity and subjectiviey with TextBlob
				text1 = TextBlob(text).sentiment
				#polarity
				polarity.append(text1.polarity)
				#subjectivity
				subjectivity.append(text1.subjectivity)

		#iterate through year and source tags
		for y in year_source_tags:
			#either year or source of instance
			year_source = str(y.text)
			if (len(year_source) > 1):
				#if it matches as a year, add it to the years list
				if (re.match(year_check, year_source) != None):
					years.append(year_source)
				#if it's in the list of source types, add it to source types list
				elif (re.match(possible_types, year_source) != None):
					types.append(year_source)
				#if it matches as a source, add it to the source list
				elif (re.match(source_check, year_source) != None):
					source.append(year_source)


		#get total pages in search results
		total_pages = soup.find_all(text=re.compile(r"[\xa0][0-9]* / [0-9]*"))

		#if there is more than one page to go through 
		if len(total_pages) != 0:
			total_pages = re.findall(re.compile(r"[0-9]*"), total_pages[0])
			page_nums = []
			for z in total_pages:
				if len(z) != 0:
					page_nums.append(int(z))

			current_page = page_nums[0]
			total_pages = page_nums[1]
	  
			while (current_page < total_pages):

				#Navigate to next page in search results
				try: 
					next_arrow = browser.find_elements_by_xpath("//b[contains(text(), '>')]")[0]
					next_arrow.click()
				except:
					break

				#use Beautiful Soup html parser on search results data
				soup = BeautifulSoup(browser.page_source, "html.parser")

				#tags with the context in which the term was used for each instance
				description_tags = soup.find_all('span', id = True)

				#tags with either the year or the source of the instance
				year_source_tags = soup.find_all('a', href = True, target = 'x4')

				#iterate through description tags to pull out context, polarity score, and subjectivity score
				for x in description_tags:
					#context
					text = str(x.text).replace('\xa0\xa0','')
					if (text != 'CLICK FOR MORE CONTEXT') & (text != 'A') & (text != 'B') & (text != 'C') & (len(text) > 20):
						#context
						descriptions.append(text)
						#calculate polarity and subjectiviey with TextBlob
						text1 = TextBlob(text).sentiment
						#polarity
						polarity.append(text1.polarity)
						#subjectivity
						subjectivity.append(text1.subjectivity)

				#iterate through year and source tags
				for y in year_source_tags:
					#either year or source of instance
					year_source = str(y.text)
					if (len(year_source) > 1):
						#if it matches as a year, add it to the years list
						if (re.match(year_check, year_source) != None):
							years.append(year_source)
						#if it's in the list of source types, add it to source types list
						elif (re.match(possible_types, year_source) != None):
							types.append(year_source)
						#if it matches as a source, add it to the source list
						elif (re.match(source_check, year_source) != None):
							source.append(year_source)

				#Check what page it's on
				page_number = soup.find_all(text=re.compile(r"[\xa0][0-9]* / [0-9]*"))
				page_number = re.findall(re.compile(r"[0-9]*"), page_number[0])
				for n in page_number:
					if len(n) != 0:
						current_page = int(n)
						break

		#Store data in pandas data frame, then write it to a csv file
		data = pd.DataFrame({'Year': years, 'Type': types, 'Source': source, 'Text': descriptions, 'Polarity': polarity, 'Subjectivity': subjectivity})
		data = data.drop_duplicates()
		export_csv = data.to_csv (str(name) + '.csv', index = None, header=True)
			
	#Close Chrome driver
	finally:
		browser.close()



