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
		'bbc.com':'',
		'a1.api.bbc.co.uk': '',
		'bbc.co.uk': '',
		'www.bbc.co.uk':'',
		'emp.bbci.co.uk':'',
		'ichef.bbc.co.uk':'',
		'idcta.api.bbc.co.uk':'',
		'mybbc.files.bbci.co.uk':'',
		'bbci.co.uk':'',
		'static.bbci.co.uk':'',
		'static.files.bbci.co.uk': '',
		'nav.files.bbci.co.uk':'',
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


for s in SITES:
	for name in SITES[s]:
		SITES[s][name] = get_rand_site(name)

nginx_conf = open('./nginx-include.conf','w+')
for s in SITES:
	for name in SITES[s]:
		cfg = get_site_config(s, name, SITES[s][name])
		nginx_conf.write(cfg)

nginx_conf.close()

idx = open('./index.html','w+')
idx.write('<p style="color:#FF0000;">\n')
idx.write('<h3 style="color:#FF0000;">WARNING: This service is for censorship circumvention and breaks encryption.</h3>\n')
idx.write('<h3 align="center">         DO NOT LOG INTO ANY SITES ACCESSIBLE VIA THIS SERVICE!</h3>\n')
idx.write('<h3 align="center">         DO NOT ENTER ANY CREDENTIALS!</h3>\n')
idx.write('<h3 align="center">         THIS SERVICE DOES NOT PROVIDE ANONYMITY AGAINST LOCAL AUTHORITIES!</h3>\n')
idx.write('<h3 align="center" style="color:#FF0000;">         INSTEAD OF THIS SERVICE: USE THE TOR BROWSER <a href="https://www.torproject.org/">https://www.torproject.org/</a> (PROXY BELOW)</h5>\n')
idx.write('</p>\n')
idx.write('</br>')
idx.write('</br>')
for s in SITES:
	idx.write('Site: {site} - <a href="https://{url}/">{url}</a></br>\n'.format(site=s, url=SITES[s][s]))
idx.write('</br>')
idx.write('</br>')
idx.write('</br>')
idx.write('</br>')
idx.write('See <a href="https://github.com/ichdasich/rev_prox">https://github.com/ichdasich/rev_prox</a> to setup your own reverse proxy.')
idx.write('<p style="color:#FFFFFF;">We are network admins, to us data is just protocol overhead</p>\n')
idx.write('</br>\n')
idx.write('</br>\n')


idx.close()



