from __future__ import print_function, division
import eventlet
eventlet.monkey_patch()
import math
import os
import requests
import json
import random
from bs4 import BeautifulSoup
from time import sleep, time

def load_from_json(file):
	try:
		with open(file, 'r') as myfile:
			return json.load(myfile)
	except IOError:
		with open(file, 'w') as myfile:
			json.dump({}, myfile)
		return {}

config = load_from_json('config.json')
proxy_sites = config['proxySites']
free_proxy_list = config['freeProxyList']
test_site = config['testSite']
total_proxies = config['totalProxies']
output = config['output']
timeout = config['timeout']
width = config['width']

def center(text, spacer=' ', length=width, clear=False, display=True):
	if clear:
		os.system('cls' if os.name == 'nt' else 'clear')
	count = int(math.ceil((length - len(text)) / 2))
	if count > 0:
		if display:
			print(spacer * count + text + spacer * count)
		else:
			return (spacer * count + text + spacer * count)
	else:
		if display:
			print(text)
		else:
			return text

def smart_sleep(delay):
	if delay > 0:
		for a in range(delay, 0, -1):
			print('{}\r'.format(center('Sleeping for {} seconds...'.format(str(a)), display=False)), end='')
			sleep(1)
		center('Sleeping for {} seconds complete!'.format(str(delay)))

def format_proxy(proxy):
	try:
		proxy_parts = proxy.split(':')
		ip, port, username, password = proxy_parts[0], proxy_parts[1], proxy_parts[2], proxy_parts[3]
		return {
			'http': 'http://{}:{}@{}:{}'.format(username, password, ip, port),
			'https': 'https://{}:{}@{}:{}'.format(username, password, ip, port)
		}
	except IndexError:
		if 'socks' in proxy:
			return {'http': proxy, 'https': proxy}
		else:
			return {'http': 'http://' + proxy, 'https': 'https://' + proxy}

def test_proxy(proxy, site):
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
	proxies = format_proxy(proxy)
	try:
		with eventlet.Timeout(timeout):
			try:
				response = requests.get(site, headers=headers, proxies=proxies)
				return True
			except (requests.exceptions.RequestException, RecursionError):
				return False
	except eventlet.timeout.Timeout:
		return False

def header():
	center(' ', clear=True)
	center('Proxy Scraper by @DefNotAvg')
	center('-', '-')

def gather_proxies(site):
	headers = {
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		'accept-encoding': 'gzip, deflate',
		'accept-language': 'en-US,en;q=0.9',
	}
	if proxy_sites[site]:
		headers['authority'] = proxy_sites[site]
	try:
		response = requests.get(site, headers=headers)
	except requests.exceptions.RequestException:
		return []
	if any(item == site for item in free_proxy_list):
		return gather_free_proxy_list(response)
	elif site == 'https://www.socks-proxy.net/':
		return gather_free_proxy_list(response, True)
	elif site == 'http://proxy-daily.com/':
		return gather_proxy_daily(response)

def gather_free_proxy_list(response, socks=False):
	soup = BeautifulSoup(response.content, 'html.parser')
	table = [item.get_text() for item in soup.find('tbody').find_all('td')]
	addresses = table[::8]
	ports = table[1::8]
	if socks:
		versions = table[4::8]
		return ['{}://{}:{}'.format(version.lower(), address, port) for address, port, version in zip(addresses, ports, versions)]
	else:
		return ['{}:{}'.format(address, port) for address, port in zip(addresses, ports)]

def gather_proxy_daily(response):
	result = []
	soup = BeautifulSoup(response.content, 'html.parser')
	tables = [item.get_text() for item in soup.find_all('div') if item.get('class') and ' '.join(item.get('class')) == 'centeredProxyList freeProxyStyle']
	for i in range(0, len(tables)):
		table = tables[i]
		if i == 0:
			proxies = [item for item in table.split('\n') if item != '']
		else:
			proxies = ['socks{}://{}'.format(str(i + 3), item) for item in table.split('\n') if item != '']
		result.extend(proxies)
	return result

header()
proxies = []
print('{}\r'.format(center('Gathering proxies...', display=False)), end='')
for site in proxy_sites.keys():
	proxies.extend(gather_proxies(site))
proxies = list(set(proxies))
random.shuffle(proxies)
if proxies:
	if len(proxies) == 1:
		center('Successfully gathered 1 proxy :(')
	else:
		center('Successfully gathered {} proxies!!'.format(str(len(proxies))))
	valid_proxies = []
	center('Testing proxies...')
	for i in range(0, len(proxies)):
		if len(valid_proxies) == total_proxies:
			break
		if proxies[i] not in valid_proxies:
			if test_proxy(proxies[i], test_site):
				valid_proxies.append(proxies[i])
		if len(valid_proxies) == 1:
			print('{}\r'.format(center('[{}/{}] Gathered 1 valid proxy...'.format(str(i + 1), str(len(proxies))), display=False)), end='')
		else:
			print('{}\r'.format(center('[{}/{}] Gathered {} valid proxies...'.format(str(i + 1), str(len(proxies)), str(len(valid_proxies))), display=False)), end='')
	if valid_proxies:
		if len(valid_proxies) == 1:
			center('Gathered 1 valid proxy :(')
		else:
			center('Gathered {} valid proxies!!'.format(str(len(valid_proxies))))
		with open(output, 'w') as myfile:
			myfile.write('\n'.join(valid_proxies))
	else:
		center('Unable to gather any valid proxies.')
else:
	center('Unable to gather proxies.')