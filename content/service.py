import os
import calendar
import time
import pathlib
from django.core.files import File
from django.conf import settings
from bs4 import BeautifulSoup
import urllib3
import urllib.request
import requests
from PIL import Image
from io import BytesIO


def get_favicon(link):
    url = 'https://' + link.split('//', 2)[1].split('/', 1)[0]
    site = link.split('//', 2)[1].split('/', 1)[0]
    http = urllib3.PoolManager()
    try:
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, 'html.parser')

        element = soup.head.findAll('link', attrs={'rel': 'shortcut icon'})
        if len(element) > 0:
            for i in element:
                if i["href"].startswith('https://'):
                    return i["href"], site
                elif i["href"].startswith('http://'):
                    return i["href"], site
                elif i["href"].startswith('/'):
                    return url + i["href"], site
        else:
            element = soup.head.findAll('link', attrs={'rel': 'icon'})
            if len(element) > 0:
                for i in element:
                    if i["href"].startswith('https://'):
                        return i["href"], site
                    elif i["href"].startswith('http://'):
                        return i["href"], site
                    elif i["href"].startswith('/'):
                        return url+i["href"], site
            else:
                return url+'/favicon.ico', site
    except Exception as r:
        return None


def ico_to_png(ico_link, site):
    try:
        response = requests.get(ico_link, stream=True)
        site_name = site
        img = Image.open(BytesIO(response.content))

        fname = 'favicon'
        img = img.convert("RGBA")
        path = settings.MEDIA_ROOT + '/tmp/'

        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                print(exc)

        if site_name.startswith('www.'):
            site_name = site.split('www.')[1]

        img.save(path + fname + '-' + site_name + '.png', 'png')
        link = path + fname + '-' + site_name + '.png'

        return link
    except Exception as e:
        return None


def get_picture(link):
    r = requests.get(link, stream=True)
    ct = r.headers['content-type']
    if ct.startswith('image') and r.status_code == requests.codes.ok:
        file_ext = ct.split('/')[1]
        fname = str(calendar.timegm(time.gmtime())) + '.' + file_ext
        image = urllib.request.urlretrieve(link, fname)
        file_path = str(pathlib.Path(image[0]).parent.absolute()) + '/' + fname
        file = File(open(image[0], 'rb'))
        return file, file_path
    else:
        return None
