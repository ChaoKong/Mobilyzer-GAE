__author__ = ('hilarious0401@gmail.com (Yikai Lin), chaokong95@gmail.com (Chao Kong)')

appetiteMap = {
	'ping':{'battery':0.002, 'data':800},
	'traceroute':{'battery':0.1, 'data':8000}
}

def map(key):
	return appetiteMap[key]