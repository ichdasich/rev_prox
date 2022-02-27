# What is this tool?

This tool creates an includable NGINX configuration that provides reverse proxy
services for a set of websites. This allows users to access these sites as long
as the server running NGINX can access the site, and the server acting as a 
reverse proxy can be accessed by the users. It is intended as a low-barrier tool
so a wide variety of people can setup reverse proxies, which in turn enable users
around the world to access potentially censored sites if they are unable to install,
e.g., the TOR browser.

## What do I need to use this?

To run this software, you need:
- A public IP address (v4/v6)
- A (sub)domain to use for this service on which you can configure a catch-all DNS entry
- A system running NGINX with the `ngx_http_sub_module` (http://nginx.org/en/docs/http/ngx_http_sub_module.html)
- A wild-card certificate for the (sub)domain you are using (needs the ability to set TXT records)

## Configuring the domain
In you DNS settings, assuming your domain is `example.com`, you have to set the 
following records:

```
example.com IN A $YOUR_IP
example.com IN AAAA $YOUR_IPv6 ; if available
*.example.com IN A $YOUR_IP
*.example.com IN AAAA $YOUR_IPv6 ; if available
```

## Enable the sub_filter module
On Ubuntu 20.04, the sub_filter module is available out of the box. On other
operating systems you might have to recompile NGINX from source.

See http://nginx.org/en/docs/http/ngx_http_sub_module.html for further details.

## Obtain TLS certificates
To get TLS rolling, issue:
```
certbot certonly --manual --preferred-challenges dns --server https://acme-v02.api.letsencrypt.org/directory -d example.com -d \*.example.com
```
On your machine after setting the necessary DNS records.

## Configure the web-server

In NGINX, you have to create the base-vhost to supply the index page, as well
as an include for the files created by the script.

On a fresh ubuntu, add the following to /etc/nginx/sites-enabled/default:
```
       server {
               listen       443;
               server_name  example.com;
               root         /var/www/html;

               ssl                  on;
               ssl_certificate      /etc/letsencrypt/live/example.com/fullchain.pem;
               ssl_certificate_key  /etc/letsencrypt/live/example.com/privkey.pem;

               ssl_session_timeout  5m;
               ssl_session_cache    shared:SSL:1m;

               ssl_ciphers  HIGH:!aNULL:!MD5:!RC4;
               ssl_prefer_server_ciphers   on;
               location / {
                       index index.html;
                       root "/var/www/html";
               }
       }
```

Afterwards, run `prox_gen.py` for your domain:
```
./prox_gen.py example.com
```

This creates two files:
- nginx-include.conf
- index.html

Copy index.html to `/var/www/html/` or whatever webroot you use, and 
`nginx-include.conf` to `/etc/nginx/sites-enabled/` and restart nginx.

```
service nginx restart
```

Afterwards, you can go to https://example.com/ and check that the reverse
proxies configured by default work.

# Adding sites and helping out
This is a rather quick automation hack around the problem that for some reason
some websites might be unavailable in some regions. Help in improving the 
toolchain would be appreciated (pull requests).

## Adding sites
The hart of the script is a large python dict in the beginning. It has entries
of the following form:
```
	'target.site': {
		'target.site': '',
		'subresource.target.site': '',
	},
```

These are then used to create a reverse proxy structure for the target.

## Things to improve
This script is a quick hack. The nginx config is most likely crap. It does not
work with many sites. What would be needed most:
- Some translations of the index page might be nice to have
- A small form field that allows you to put in a deep link from a proxied website to get the service link might be nice
- Far too many resources are not yet proxied.
- Add more sites and verify they are working. cnn,com, bbc,com etc... all make problems
- Make the configuration better(tm)
- Improve the documentation. I typed this down at 3:30 after far too many drinks, and i guess it shows.
- Deploy this on your own domain(s) and IP(s)
