#!/usr/bin/env python3

import sys
import os
import random
import string

DOM = sys.argv[1]
SITES = {
	'www.dw.com': {
		'www.dw.com': "",
		'cdn.jwplayer.com': "",
		'code.jquery.com': "",
		'commons.dw.com': "",
		'logs1242.xiti.com': "",
		'peach-static.ebu.io': "",
		'player.h-cdn.com': "",
#		'sslp.jwpcdn.com': "",
		'p.dw.com': "",
		'downloads.dw.com': '',
		'static.dw.com': "",
		'tvdownloaddw-a.akamaihd.net': "",
		'www.google-analytics.com': "",
		'www.google.com': "",
		'www.googletagmanager.com': "",
		'www.gstatic.com': "",
	},
	'www.tagesschau.de': {
		'www.tagesschau.de': "",
		'player.h-cdn.com': '',
		'script.ioam.de': '',
		'www1.sportschau.de': '',
	},
	'www.torproject.org': {
		'www.torproject.org': '',
		'support.torproject.org': '',
		'community.torproject.org': '',
		'blog.torproject.org': '',
		'donate.torproject.org': '',
		'dist.torproject.org': '',
	},
	'rsf.org': {
		'rsf.org': '',
		'www.rsf.org': '',
		'helpdesk.rsf.org': '',
		'index.rsf.org': '',
		'wiki.rsf.org': '',
		'hello.myfonts.net': '',
		'cdnjs.cloudflare.com': '',
		'code.jquery.com': '',
		'script.hotjar.com': '',
		'static.hotjar.com': '',
	},
	'www.theguardian.com': {
		'www.theguardian.com': '',
		'assets.guim.co.uk': '',
		'contributions.guardianapis.com': '',
		'i.guim.co.uk': '',
		'interactive.guim.co.uk': '',
		'sourcepoint.theguardian.com': '',
		'static.theguardian.com': '',
	},
	'www.bbc.com': {
		'www.bbc.com': '',
		'ichef.bbci.co.uk': '',
		'ychef.files.bbci.co.uk': '',
		'search.bbc.co.uk': '',
		'mybbc-analytics.files.bbci.co.uk': '',
		'c.files.bbci.co.uk': '',
		'gn-web-assets.api.bbc.com':'',
		'm.files.bbci.co.uk':'',
		'a1.api.bbc.co.uk': '',
		'bbc.co.uk': '',
		'www.bbc.co.uk':'',
		'downloads.bbc.co.uk':'',
		'emp.bbci.co.uk':'',
		'ichef.bbc.co.uk':'',
		'idcta.api.bbc.co.uk':'',
		'mybbc.files.bbci.co.uk':'',
		'static.bbci.co.uk':'',
		'static.files.bbci.co.uk': '',
		'nav.files.bbci.co.uk':'',
		'static.chartbeat.com':'',
		'ping.chartbeat.net':'',
		'cdn.optimizely.com':'',
		'bbci.co.uk':'',
		'bbc.com':'',
	},
### Sites not yet working OOTB, needing further debugging
#	'edition.cnn.com': {
#		'edition.cnn.com': '',
#		'cdn.cnn.com': '',
#		'edition.i.cdn.cnn.com': '',
#		'lightning.cnn.com': '',
#		's.cdn.turner.com': '',
#	},
#	'twitter.com': {
#		'twitter.com': '',
#		'abs-0.twimg.com': '',
#		'abs.twimg.com': '',
#		'pbs.twimg.com': '',
#		'api.twitter.com': '',
#		'ton.twitter.com': '',
#		'analytics.twitter.com': '',
#	}
}

def get_rand_site(site):
	letters = string.ascii_lowercase
	pref = ''.join(random.choice(letters) for i in range(10))
	return pref+'.'+DOM

def get_sub_filter(site, sub):
	return '		sub_filter "{site}" "{sub}";'.format(site=site, sub=sub)

def get_site_config(main, site, sub):
	global SITES, DOM
	head = """
server {{
	listen       443;
	listen       [::]:443;
	server_name  {sub};
	root         /var/www/htdocs;
	
	ssl                  on;
	ssl_certificate      /etc/letsencrypt/live/{DOM}/fullchain.pem;
	ssl_certificate_key  /etc/letsencrypt/live/{DOM}/privkey.pem;
	
	ssl_session_timeout  5m;
	ssl_session_cache    shared:SSL:1m;
	
	ssl_ciphers  HIGH:!aNULL:!MD5:!RC4;
	ssl_prefer_server_ciphers   on;
	location / {{
		proxy_ssl_server_name on;
		proxy_busy_buffers_size   512k;
		proxy_buffers   4 512k;
		proxy_buffer_size   256k;
		proxy_pass https://{site}/;
		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "Upgrade";
		proxy_set_header Host {site};
		proxy_set_header X-Forwarded-Host $host;
		proxy_set_header X-Forwarded-Proto $scheme;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Accept-Encoding "";
""".format(sub=sub, site=site, DOM=DOM)
	
	for i in SITES[main]:
		fltr = get_sub_filter(i, SITES[main][i])
		head = head + fltr + '\n'

	tail = """
		sub_filter_once off;
	}
}
"""
	head = head + tail
	
	return head

def get_sites():
	if not os.path.isfile('./conf/'+DOM+'.conf'):
		return {}
	f = open('./conf/'+DOM+'.conf')
	ret = {}
	server = 0
	site = ''
	for l in f:
			
		if 'sub_filter ' in l:
			n = l.strip().strip(';').split()
			if server == 1 and not site in ret:
				site = n[1].strip('"')
				ret[site] = {}
			ret[site][n[1].strip('"')] = n[-1].strip('"')
			server += 1
		if 'sub_filter_once off;' in l:
			server = 0
			site = ''
		if 'proxy_set_header Accept-Encoding "";' in l:
			server = 1
	return ret

d = get_sites()

for s in SITES:
	for name in SITES[s]:
		if name in d[s]:
			SITES[s][name] = d[s][name]
		else:
			SITES[s][name] = get_rand_site(name)

nginx_conf = open('./conf/'+DOM+'-nginx-include.conf','w+')
for s in SITES:
	for name in SITES[s]:
		cfg = get_site_config(s, name, SITES[s][name])
		nginx_conf.write(cfg)

nginx_conf.close()

idx = open('./sites/'+DOM+'-index.html','w+')
idx.write('<html>\n')
idx.write('<head>\n')
idx.write('<meta charset=utf-8>\n')
idx.write('<title>???????????? ???????????????? ??????????</title>\n')
idx.write('</head>\n')
idx.write('<body>\n')
idx.write('<p style="color:#FF0000;">\n')
idx.write('<h3 align="center" style="color:#FF0000;">WARNING: This service is for censorship circumvention/reading sites.</h3>\n')
#idx.write('<h3 align="center">DO NOT LOG INTO ANY SITES ACCESSIBLE VIA THIS SERVICE! DO NOT ENTER ANY CREDENTIALS! THIS SERVICE DOES NOT PROVIDE ANONYMITY AGAINST LOCAL AUTHORITIES!</h3>\n')
idx.write('<h5 align="center" style="color:#FF0000;">TO LOG-IN TO SITES: USE THE TOR BROWSER <a href="https://www.torproject.org/">https://www.torproject.org/</a> (PROXY BELOW)</h5>\n')
idx.write('<h3 align="center">- - - - - - - - - - - - - </h3>\n')
idx.write('<h3 align="center" style="color:#FF0000;">????????????????: ???????? ???????????? ???????????????????????? ?????? ???????????????????? ??????????????.</h3>\n')
#idx.write('<h3 align="center">???? ?????????????????? ???????????????????????? ?????????? ?????????? ?????????? ?????????????????? ?????????? ???????? ????????????! ???? ?????????????? ?????????????? ????????????! ???????? ???????????? ???? ?????????????????????????? ?????????????????????? ???? ?????????????? ??????????????!</h3>\n')
idx.write('<h5 align="center" style="color:#FF0000;">?????? ?????????? ???? ??????????: ?????????????????????? ?????????????? ??????: <a href="https://www.torproject.org/">https://www.torproject.org/</a> (PROXY BELOW)</h5>\n')
idx.write('<h3 align="center">- - - - - - - - - - - - - </h3>\n')
idx.write('<p align="center">\n')
idx.write('???????????? ???????????????? ?????????? - ???????????? ???????????????? ?????????? - ???????????? ?????????? ?????????? - ???????????? ????-????-???? - ???????????? ??????????????\n')
idx.write('</p>\n')
idx.write('</br>\n')
idx.write('</br>\n')
idx.write('<p align="center">\n')
for s in SITES:
	idx.write('Site: {site} - <a href="https://{url}/">{url}</a></br>\n'.format(site=s, url=SITES[s][s]))
idx.write('</p>\n')
idx.write('</br>\n')
idx.write('</br>\n')
idx.write('</br>\n')
idx.write('</br>\n')
idx.write('See <a href="https://github.com/ichdasich/rev_prox">https://github.com/ichdasich/rev_prox</a> to setup your own reverse proxy.</br>\n')
idx.write('<p style="color:#FFFFFF;">We are network admins, to us data is just protocol overhead</p>\n')
idx.write('</br>\n')
idx.write('</br>\n')
idx.write('</body>\n')
idx.write('</html>\n')


idx.close()



