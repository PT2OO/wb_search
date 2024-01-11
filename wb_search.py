import requests
import urllib3
from termcolor import colored
import threading
import time
import argparse
from datetime import date, timedelta
import os
from bs4 import BeautifulSoup
import re
import signal



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def handler(signum, frame):
	global RETRY_TARGET
	res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
	if res == 'y':
		if len(RETRY_TARGET) > 0:
			print("[INFO] List of domains needed to retry: ")
			for domain in list(dict.fromkeys(RETRY_TARGET)):
				print(domain)
		exit(1)

def save_response(domain, fulltime, data, status_code, saveRes):
	if saveRes is not None:
		directory_path = "{}/{}".format(saveRes, domain.replace(".","_"))
		if not os.path.exists(directory_path):
			os.makedirs(directory_path)

		with open(directory_path + "/{}__{}__{}__{}.html".format(status_code, str(len(data)), domain.replace(".","_"), fulltime), 'w') as file:
			file.write(data)
			# print("writed")

def save_response_link(domain, path, fulltime, data, status_code, saveRes):
	if saveRes is not None:
		directory_path = "{}/{}".format(saveRes, domain.replace(".","_"))
		if not os.path.exists(directory_path):
			os.makedirs(directory_path)
		if path is None or path == "/":
			with open(directory_path + "/{}__{}__{}__{}.html".format(status_code, str(len(data)), domain.replace(".","_"), fulltime), 'w') as file1:
				file1.write(data)
				# print("writed1 - {}".format(directory_path + "/{}__{}__{}__{}.html".format(status_code, str(len(data)), domain.replace(".","_"), fulltime)))
		else:
			if "." in path:
				with open(directory_path + "/{}__{}__{}__{}.{}".format(status_code, str(len(data)), path.replace("/","%").split(".")[0], fulltime, path.replace("/","-").split(".")[1]), 'w') as file2:
					file2.write(data)
					# print("writed2 - {}".format(directory_path + "/{}__{}__{}__{}.{}".format(status_code, str(len(data)), path.replace("/","%").split(".")[0], fulltime, path.replace("/","-").split(".")[1])))
			else:
				with open(directory_path + "/{}__{}__{}__{}.html".format(status_code, str(len(data)), path.replace("/","%"), fulltime), 'w') as file3:
					file3.write(data)
					# print("writed3 - {}".format(directory_path + "/{}__{}__{}__{}.html".format(status_code, str(len(data)), path.replace("/","%"), fulltime)))
			



def send_request(domain, api, data, headers, retry_record=False):
	global RETRY_TARGET
	retry_count = 0
	retry = True	
	global HTTP_CONFIG
	while retry and retry_count < 10: 
		try:
			print("debug1")
			r = requests.get("https://{}".format(domain) + api, params=data, headers=headers, proxies=HTTP_CONFIG, verify=False, allow_redirects=True, timeout=20)
			retry = False
			# print(colored("[Info] Connected to {}".format(domain), "green"))
			return r
		except:
			retry = True
			retry_count += 1
			print("debug2")
			print(colored("[Error] [{}] Can't connect to {}".format(str(retry_count), domain), "red"))
			
			time.sleep(5)
	if retry_record:
		print("debug3")
		print(colored("[INFO] SKIP {}".format("https://{}".format(domain) + api), "yellow"))
		RETRY_TARGET.append(domain)
	return None

def send_request_2(url, retry_record=False):
	global RETRY_TARGET
	retry_count = 0
	retry = True	
	global HTTP_CONFIG
	while retry and retry_count < 10: 
		try:	
			r = requests.get(url, verify=False, allow_redirects=True, timeout=20)
			retry = False
			# print(colored("[Info] Connected to {}".format(domain), "green"))
			return r
		except:
			retry = True
			print(colored("[Error] [{}] Can't connect to {}".format(str(retry_count),url), "red"))
			retry_count += 1
			time.sleep(5)
	if retry_record:
		print(colored("[INFO] SKIP {}".format(url), "yellow"))
		RETRY_TARGET.append(url)
	return None

			
def print_next(input_string, target_substring, num_next):
	index = input_string.find(target_substring)

	if index != -1:
		next_10_chars = input_string[index + len(target_substring):index + len(target_substring) + num_next]
		return target_substring + next_10_chars
	else:
		return None
	
def find_re(input_string, pattern):
	founds = re.findall(r'{}'.format(pattern), input_string)
	return founds

def print_all_days_in_year(year):
	found = []
	start_date = date(year, 1, 1)
	end_date = date(year, 12, 31)

	current_date = start_date
	while current_date <= end_date:
		formatted_date = current_date.strftime('%Y%m%d')
		# print(formatted_date)
		found.append(formatted_date)
		current_date += timedelta(days=1)
	return found

def print_all_months_in_year(year):
	found = []
	start_date = date(year, 1, 1)
	end_date = date(year, 12, 31)

	current_date = start_date
	while current_date <= end_date:
		formatted_date = current_date.strftime('%Y%m')
		found.append(formatted_date)
		# Move to the first day of the next month
		current_date = date(current_date.year + (current_date.month // 12), ((current_date.month % 12) + 1), 1)
	return found


def get_year(url):
	global HTTP_CONFIG
	found_years = []
	headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
		"Accept": "*/*",
		"Accept-Language": "en-GB,en;q=0.5",
		"Accept-Encoding": "gzip, deflate, br",
		"Sec-Fetch-Dest": "empty",
		"Referer": "https://web.archive.org/",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "same-origin",
		"X-Pwnfox-Color": "green",
		"Te": "trailers"
	}
	api = "/__wb/sparkline"
	data = "output=json&url={}&collection=web".format(url)
	domain = "web.archive.org"

	# r = requests.get("https://web.archive.org" + api, params=data, headers=headers, proxies=HTTP_CONFIG, verify=False, allow_redirects=True)
	r = send_request(domain, api, data, headers)
	while r.status_code == 429:
		print(colored("429 Too Many Requests! Paused in 20s. Please change your IP!", "red"))
		time.sleep(20)
		# r = requests.get("https://web.archive.org" + api, params=data, headers=headers, proxies=HTTP_CONFIG, verify=False, allow_redirects=True)
		r = send_request(domain, api, data, headers)

	if r.status_code == 200 :
		for year in r.json()["years"]:
			found_years.append(year)
		return found_years
	return found_years


def get_mmdd(url,year):
	global HTTP_CONFIG
	found_days = []
	headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
		"Accept": "*/*",
		"Accept-Language": "en-GB,en;q=0.5",
		"Accept-Encoding": "gzip, deflate, br",
		"Sec-Fetch-Dest": "empty",
		"Referer": "https://web.archive.org/",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "same-origin",
		"X-Pwnfox-Color": "green",
		"Te": "trailers"
	}
	api = "/__wb/calendarcaptures/2"
	data = "url={}&date={}&groupby=day".format(url, year)
	domain = "web.archive.org"

	# r = requests.get("https://web.archive.org" + api, params=data, headers=headers, proxies=HTTP_CONFIG, verify=False, allow_redirects=True)
	r = send_request(domain, api, data, headers)
	while r.status_code == 429:
		print(colored("429 Too Many Requests! Paused in 20s. Please change your IP!", "red"))
		time.sleep(20)
		# r = requests.get("https://web.archive.org" + api, params=data, headers=headers, proxies=HTTP_CONFIG, verify=False, allow_redirects=True)
		r = send_request(domain, api, data, headers)

	if r.status_code == 200:
		for list_date in r.json()["items"]:
			# print(list_date)
			found_days.append(str(list_date[0]))
		return found_days
	return found_days


def get_time_by_day(url, time_by_day):
	global HTTP_CONFIG
	found_times= []
	headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
		"Accept": "*/*",
		"Accept-Language": "en-GB,en;q=0.5",
		"Accept-Encoding": "gzip, deflate, br",
		"Referer": "https://web.archive.org/",
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "same-origin",
		"X-Pwnfox-Color": "green",
		"Te": "trailers"
	}
	api = "/__wb/calendarcaptures/2"
	data = "url={}&date={}".format(url, time_by_day)
	domain = "web.archive.org"

	# r = requests.get("https://web.archive.org" + api, params=data, headers=headers, proxies=HTTP_CONFIG, verify=False, allow_redirects=True)
	r = send_request(domain, api, data, headers)

	while r.status_code == 429:
		print(colored("429 Too Many Requests! Paused in 20s. Please change your IP!", "red"))
		time.sleep(20)
		# r = requests.get("https://web.archive.org" + api, params=data, headers=headers, proxies=HTTP_CONFIG, verify=False, allow_redirects=True)
		r = send_request(domain, api, data, headers)

	if r.status_code == 200:
		try:
			for list_date in r.json()["items"]:
				found_times.append(str(list_date[0]))
		except:
			print(colored("Error when getting time by day: {}".format(time_by_day), "red"))
			return found_times
		return found_times
	return found_times



def isExcludedExt(input):
	excluded_ext = [".jpg", ".jpeg", ".png", ".gif", ".css",".svg", ".mp4", ".mp3", ".webp"]
	for ext in excluded_ext:
		if ext in input:
			return True
	return False

def get_all_links(url):
	
	found = []
	# Make a request to the URL
	response = send_request_2(url)

	if response is None:
		return found

	# Check if the request was successful (status code 200)
	if response.status_code == 200:
		# Parse the HTML content using BeautifulSoup
		soup = BeautifulSoup(response.text, 'html.parser')

		# Find all the <a> tags which contain links
		links = soup.find_all('a')
		for link in links:
			href = link.get('href')
			if href:
				# print(f"Link (from <a>): {href}")
				if "/web/" in href:
					if isExcludedExt(href) == False:
						found.append(href.replace("https://web.archive.org","").replace("//web.archive.org",""))

		# Find all tags with src attributes (e.g., <img>, <script>, etc.)
		src_tags = soup.find_all(src=True)
		for src_tag in src_tags:
			src = src_tag['src']
			# print(f"Source (from {src_tag.name}): {src}")\
			# found.append(href.replace("https://web.archive.org",""))
			if "/web/" in src:
					if isExcludedExt(src) == False:
						found.append(src.replace("https://web.archive.org","").replace("//web.archive.org",""))

	else:
		print(colored(f"Error: Unable to fetch the page. Status code: {response.status_code}", "red"))
	return found


def get_content_link(url, full_time, list_find_str, saveRes, list_pattern, more_print=20, verbose="false"):
	result = []
	global HTTP_CONFIG
	headers = {
		"Accept-Encoding": "gzip, deflate, br",
		"Accept": "*/*",
		"Accept-Language": "en-US;q=0.9,en;q=0.8",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.70 Safari/537.36",
		"Cache-Control": "max-age=0"
	}
	api = url
	data = ""
	domain = "web.archive.org"

	retry = True
	while retry:
		try:
			r = send_request(domain, api, data, headers)
			if r is None:
				return result
			if verbose == "true":
				print("https://web.archive.org" + url)
			if r.status_code == 429:
				print(colored("429 Too Many Requests! Paused in 7s, please change your IP!", "red"))
				time.sleep(7)
				retry = True
			if r.status_code == 200:
				domain_link = url.replace("https://","").replace("http://","").split("/")[3]
				save_response_link(domain_link, url.split(domain_link)[1], url.replace("https://","").replace("http://","").split("/")[2], r.text, str(r.status_code), saveRes)
				

			if len(list_find_str) > 0:
				for find_str in list_find_str:
					if find_str.split("\t")[1] in r.text and r.status_code == 200:
						lines = r.text.split("\n")
						for line in lines:
							if find_str.split("\t")[1] in line:
								result.append("https://web.archive.org{} ===> {} ".format(url, print_next(line, find_str.split("\t")[1], int(more_print))))
								print(colored("[Found] ({}) {}".format(find_str.split("\t")[0] ,"https://web.archive.org{} ===> {} ".format( url, print_next(line, find_str.split("\t")[1], int(more_print)))), "green"))
			
			if len(list_pattern) > 0:
				for pattern in list_pattern:
					if r.status_code == 200:
						res_text = r.text
						re_founds = find_re(res_text, pattern.split("\t")[1])
						if len(re_founds) > 0:
							for re_found in re_founds:
								result.append("https://web.archive.org{} ===> {} ({})".format(url, re_found, pattern.split("\t")[0]))
								print(colored("[Found] ({}) {}".format(pattern.split("\t")[0] , "https://web.archive.org{} ===> {}".format(url, re_found)), "green"))

							
			retry = False
		except:
			retry =True

	return result

def get_content(url, full_time, list_find_str, saveRes, list_pattern, more_print=20, verbose="false"):
	result = []
	global HTTP_CONFIG
	headers = {
		"Accept-Encoding": "gzip, deflate, br",
		"Accept": "*/*",
		"Accept-Language": "en-US;q=0.9,en;q=0.8",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.70 Safari/537.36",
		"Cache-Control": "max-age=0"
	}
	api = "/web/{}/https://{}".format(full_time, url)
	data = ""
	domain = "web.archive.org"

	retry = True
	while retry:
		try:
			r = send_request(domain, api, data, headers, retry_record=True)
			if r is None:
				return result
			
			if verbose == "true":
				print("https://web.archive.org" + api)
			if r.status_code == 429:
				print(colored("429 Too Many Requests! Paused in 7s, please change your IP!", "red"))
				time.sleep(7)
				retry = True
			if r.status_code == 200:
				save_response(url, full_time, r.text, str(r.status_code), saveRes)

			if len(list_find_str) > 0:
				for find_str in list_find_str:
					if find_str.split("\t")[1] in r.text and r.status_code == 200:
						lines = r.text.split("\n")
						for line in lines:
							if find_str.split("\t")[1] in line:
								result.append("https://web.archive.org{} ===> {} ".format(url, print_next(line, find_str.split("\t")[1], int(more_print))))
								print(colored("[Found] ({}) {}".format(find_str.split("\t")[0] ,"https://web.archive.org{} ===> {} ".format( url, print_next(line, find_str.split("\t")[1], int(more_print)))), "green"))

			if len(list_pattern) > 0:
				for pattern in list_pattern:
					if r.status_code == 200:
						res_text = r.text
						re_founds = find_re(res_text, pattern.split("\t")[1])
						if len(re_founds) > 0:
							for re_found in re_founds:
								result.append("https://web.archive.org{} ===> {} ({})".format(url, re_found, pattern.split("\t")[0]))
								print(colored("[Found] ({}) {}".format(pattern.split("\t")[0] , "https://web.archive.org{} ===> {}".format(url, re_found)), "green"))


			retry = False
		except:
			retry =True

	return result


def check_by_yyyy(url, year=None, month=None):
	found_fulltimes = []
	input_years =  []
	found_years = get_year(url)
	if year == None:
		input_years =  found_years
	else:
		input_years.append(year)

	for check_year in input_years:
		if check_year in found_years:
			check_days = []
			found_days = get_mmdd(url, check_year)
			# print(found_days)
			if len(found_days) > 0:
				if month == None:
					check_days = found_days
				else:
					for found_day in found_days:
						# print(found_day[0:-2])
						if month == found_day[0:-2]:
							check_days.append(found_day)

			# print(check_days)
			if len(check_days) > 0:
				for check_day in check_days:
					if len(check_day) != 4:
						prefix1 = "0" * (4-len(check_day))
						check_day = prefix1 + check_day
					found_times = get_time_by_day(url, check_year + check_day)
					for found_time in found_times:
						if len(found_time) != 6:
							prefix2 = "0" * (6-len(found_time))
							found_time = prefix2 + found_time
						# print(check_year + check_day + found_time)
						found_fulltimes.append(check_year + check_day + found_time)
			else:
				print("{} no record!".format(check_year))
				exit(0)
			
		else:
			print("Year is not found!")
			exit(0)
	return found_fulltimes

def get_snapshot_fulltime(url, year=None, month=None):
	global HTTP_CONFIG
	found_fulltimes = []
	headers = {
		"Accept-Encoding": "gzip, deflate, br",
		"Accept": "*/*",
		"Accept-Language": "en-US;q=0.9,en;q=0.8",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36",
		"Cache-Control": "max-age=0"
	}
	api = "/__wb/calendarcaptures/2"
	data = "url=https://{}&date=20".format(url)
	domain = "web.archive.org"

	# r = requests.get("https://web.archive.org" + api, params=data, headers=headers, proxies=HTTP_CONFIG, verify=False, allow_redirects=True)
	r = send_request(domain, api, data, headers, retry_record=True)


	if r is not None:
		while r.status_code == 429:
			print(colored("429 Too Many Requests! Paused in 20s. Please change your IP!", "red"))
			time.sleep(10)
			# r = requests.get(url+api, params=data, headers=headers, proxies=HTTP_CONFIG, verify=False, allow_redirects=True)
			r = send_request(domain, api, data, headers, retry_record=True)
			if r is None:
				return found_fulltimes

	if len(r.json()) > 0:
		all = r.json()["items"]
		for snapshot in all:
			snapshot_hour = str(snapshot[0])[-6:]
			snapshot_day = str(snapshot[0])[-8:-6]
			snapshot_month = str(snapshot[0])[-10:-8]
			snapshot_year = "20" + str(snapshot[0]).replace(snapshot_month + snapshot_day + snapshot_hour, "").zfill(2)
			fulltime = snapshot_year + snapshot_month + snapshot_day + snapshot_hour
			if year is not None:
				if month is not None:
					if "{}{}".format(year,month) == fulltime[0:6]:
						found_fulltimes.append(fulltime)
				else:
					if year == fulltime[0:4]:
						found_fulltimes.append(fulltime)
			else:
				if month is not None:
					if month == fulltime[4:6]:
						found_fulltimes.append(fulltime)
				else:
						found_fulltimes.append(fulltime)
				

	return found_fulltimes

	
class myThread (threading.Thread):
	def __init__(self, threadID, url, full_time, list_find_str, timestamp, more_print, output, verbose, saveRes, list_pattern):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.url = url
		self.full_time = full_time
		self.list_find_str = list_find_str
		self.timestamp = timestamp
		self.more_print = more_print
		self.output = output
		self.verbose = verbose
		self.saveRes = saveRes
		self.list_pattern = list_pattern
		
	def run(self):
		founds = get_content(self.url, self.full_time, self.list_find_str, self.saveRes, self.list_pattern, self.more_print, self.verbose)
		found_links = get_all_links("https://web.archive.org/web/{}/https://{}/".format(self.full_time, self.url))
		dedup_found_links = list(set(found_links))

		if len(dedup_found_links) > 0:
			for link in dedup_found_links:
				founds_via_link = get_content_link(link, self.full_time, list_find_str, self.saveRes, self.list_pattern, self.more_print, self.verbose)
				founds.extend(founds_via_link)
		# else:
		# 	print("Debug")
			
		if len(founds) > 0:
			for found in founds:
				if os.path.exists("{}/{}_{}.txt".format(self.output, self.url, self.timestamp)) == False:
					with open("{}/{}_{}.txt".format(self.output, self.url, self.timestamp), "w") as f1:
						pass
				with open("{}/{}_{}.txt".format(self.output, self.url, self.timestamp), "a") as f:
					f.writelines(found + "\n")
		


def send_request_multiThread(url, found_fulltimes, list_find_str, numOfThreads, timestamp, more_print, output, verbose, saveRes, list_pattern):
	threads = []
	# for url in url_list:
	#     i = 1
	#     threads.append(myThread(i, url, platform))
	#     i += 1

	split_arrays = [found_fulltimes[i:i+int(numOfThreads)] for i in range(0, len(found_fulltimes), int(numOfThreads))]
	for i, split_array in enumerate(split_arrays):
		# print(f"Split Array {i+1}: {split_array}")
		threads_1 = []
		for full_time in split_array:
			threads_1.append(myThread(1, url, full_time, list_find_str, timestamp, more_print, output, verbose, saveRes, list_pattern))
		
		threads = []
		for t1 in threads_1:
			t1.start()
			threads.append(t1)
		
		for t in threads:
			t.join()
	

def find(url, found_fulltimes, list_find_str, num_of_threads, timestamp, more_print, output, verbose, saveRes, list_pattern):
	# print(colored("==> Checking domain {}".format(url), "yellow"))
	# print(colored("    [#] String:", "yellow"))
	# for x in list_find_str:
	# 	print(colored("                {}".format(x), "yellow"))

	# print(colored("    [#] Regex pattern:", "yellow"))
	# for y in list_pattern:
	# 	print(colored("                {}".format(y), "yellow"))
	# for full_time in found_fulltimes:
		# get_content(url, full_time, find_str)
	send_request_multiThread(url, found_fulltimes, list_find_str, num_of_threads, timestamp, more_print, output, verbose, saveRes, list_pattern)


def add_to_checked_list(url, file_path):
	with open(file_path, 'a') as file:
		file.write('{}\n'.format(url))


def is_line_in_file(file_path, url):
	try:
		with open(file_path, 'r') as file:
			for line in file:
				if line.strip() == url:
					return True
		return False
	except FileNotFoundError:
		print(f"Error: File '{file_path}' not found.")
		exit()


parser = argparse.ArgumentParser()
parser.add_argument('--d', type=str, help='Domain needed to wayback')
parser.add_argument('--file', type=str, help='--file /path_to_file/domains.txt')
parser.add_argument('--s', type=str, help='Find this string in respond of each records')
parser.add_argument('--sf', type=str, help='Path to file of strings to find respond of each records')
parser.add_argument('--sre', type=str, help='Find regex pattern in respond of each records')
parser.add_argument('--sref', type=str, help='Path to file of regex patterns to find respond of each records')
parser.add_argument('--more_print', type=str, help='Get more nums of character after found string, default is 20')
parser.add_argument('--y', type=str, help='Do wayback for this year, blank for all years')
parser.add_argument('--m', type=str, help='Do wayback for this month, blank for all years')
parser.add_argument('--extract', type=str, help='Extract found wayback url. Example: "--extract true" (default is None)')
parser.add_argument('--eachMonth', type=str, help='Only get 1 snapshot in each months. Example: "--eachMonth true" (default is None)')
parser.add_argument('--eachDay', type=str, help='Only get 1 snapshot in each days. Example: "--eachDay true" (default is None)')
parser.add_argument('--output', type=str, help='Path to directory to save result file')
parser.add_argument('--saveRes', type=str, help='Path to directory to save responses')
parser.add_argument('--verbose', type=str, help='Verbose')
parser.add_argument('--proxy', type=str, help='--proxy http://127.0.0.1:8080')
parser.add_argument('--example', type=str, help='python3 wb_search.py --d www.metronet.com --sref wb_search_patterns.txt --sf wb_search_strings.txt --more_print 50 --y 2023 --eachDay true --m 10 --saveRes "/tmp/WB_DB" --verbose true')

args = parser.parse_args()

HTTP_CONFIG = {}

RETRY_TARGET = []

if args.proxy != None:
	HTTP_CONFIG = {
		'http': args.proxy,
		'https': args.proxy
	}

url = args.d
find_str = args.s
path_find_str = args.sf
year = args.y
month = args.m
num_of_threads = "10"
extract = args.extract
eachMonth = args.eachMonth
eachDay = args.eachDay
file = args.file
more_print = args.more_print
output = args.output
saveRes = args.saveRes
sre = args.sre
sref = args.sref
verbose = args.verbose

if saveRes is not None:
	if not os.path.exists(saveRes):
		print(colored("[Error] Directory {} not found".format(output), "red"))
		exit()
	
if output is None:
	output = os.getcwd()
else:
	if os.path.exists(output) == False:
		print(colored("[Error] Directory {} not found".format(output), "red"))
		exit()

if args.more_print == None:
	more_print = 20

list_find_str = []

if find_str is None and path_find_str is not None:
	if os.path.exists(path_find_str) == False:
		print(colored("[Error] File {} not found".format(path_find_str), "red"))
		exit()
	with open(path_find_str, "r") as f:
		for line in f:
			list_find_str.append(line.strip().replace("\n",""))

if find_str is not None:
	list_find_str.append("String\t" + find_str)


	
list_pattern = []

if sre is None and sref is not None:
	if os.path.exists(sref) == False:
		print(colored("[Error] File {} not found".format(sref), "red"))
		exit()
	with open(sref, "r") as f1:
		for line in f1:
			list_pattern.append(line.strip().replace("\n",""))

if sre is not None:
	list_pattern.append("Pattern\t" + sre)

	
if len(list_pattern) == 0 and len(list_find_str) == 0:
	print(colored("[Error] No string/pattern to find", "red"))
	exit()

print(colored("    [#] String:", "yellow"))
for x in list_find_str:
	print(colored("                {}".format(x), "yellow"))

print(colored("    [#] Regex pattern:", "yellow"))
for y in list_pattern:
	print(colored("                {}".format(y), "yellow"))

timestamp = str(int(time.time()))

if eachDay == "true" and eachMonth == "true":
	print(colored("Only eachDay or eachMonth !!!"))
	exit()

filtered_fulltimes = []

#year/month: None/blank => Check all 

if url is not None and file is None:
	print(colored("==> Checking domain {}".format(url), "yellow"))
	found_fulltimes = get_snapshot_fulltime(url, year, month)

	if len(found_fulltimes) > 0:
		if eachMonth == "true":
			for y in range(2000, 2030):
				for m in print_all_months_in_year(y):
					for fulltime in found_fulltimes:
						if m in fulltime:
							filtered_fulltimes.append(fulltime)
							break
					continue


		if eachDay == "true":
			for y in range(2000, 2030):
				for d in print_all_days_in_year(y):
					for fulltime in found_fulltimes:
						if d in fulltime:
							filtered_fulltimes.append(fulltime)
							break
					continue
	
	print(colored("[Info] Found {}/{} (filtered/full) records for {} in {}/{}".format(len(filtered_fulltimes),len(found_fulltimes), url, year, month), "yellow"))

	if eachMonth == "true" or eachDay == "true":
		find(url, filtered_fulltimes, list_find_str, num_of_threads, timestamp, more_print, output, verbose, saveRes, list_pattern)

	if len(found_fulltimes) > 0 and eachDay is None and eachMonth is None:
		find(url, found_fulltimes, list_find_str, num_of_threads, timestamp, more_print, output, verbose, saveRes, list_pattern)
	
	print(colored("Saved result to {}".format("{}/{}_{}.txt".format(output, url, timestamp)), "yellow"))
	


if url is None and file is not None:
	checked_file_path = "{}/checked_domains.txt".format(os.getcwd(), )
	if os.path.exists(checked_file_path) == False:
					with open(checked_file_path, "w") as f1:
						pass

	with open(file, 'r') as f2:
		for line in f2:
			url = line.strip().replace("\n", "")
			if is_line_in_file(checked_file_path, url) == False:
				print(colored("==> Checking domain {}".format(url), "yellow"))
				found_fulltimes = get_snapshot_fulltime(url, year, month)
				if len(found_fulltimes) > 0:
					if eachMonth == "true":
						for y in range(2000, 2030):
							for m in print_all_months_in_year(y):
								for fulltime in found_fulltimes:
									if m in fulltime:
										filtered_fulltimes.append(fulltime)
										break
								continue

					if eachDay == "true":
						for y in range(2000, 2030):
							for d in print_all_days_in_year(y):
								for fulltime in found_fulltimes:
									if d in fulltime:
										filtered_fulltimes.append(fulltime)
										break
								continue

				if eachMonth == "true":
					find(url, filtered_fulltimes, list_find_str, num_of_threads, timestamp, more_print, output, verbose, saveRes, list_pattern)

				if eachDay == "true":
					find(url, filtered_fulltimes, list_find_str, num_of_threads, timestamp, more_print, output, verbose, saveRes, list_pattern)
					
				if len(found_fulltimes) > 0 and eachDay is None and eachMonth is None:
					find(url, filtered_fulltimes, list_find_str, num_of_threads, timestamp, more_print, output, verbose, saveRes, list_pattern)

				print(colored("Saved result to {}".format("{}/{}_{}.txt".format(output, url, timestamp)), "yellow"))
				add_to_checked_list(url, checked_file_path)


