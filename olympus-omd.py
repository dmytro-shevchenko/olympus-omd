#!/usr/bin/python

import sys
import os
import argparse
import urllib
from urllib2 import urlopen
from bs4 import BeautifulSoup


class Olympus:

    def __init__(self, ip):
        self.ip = ip

    def info(self):
        """
        Return camera info
        :return:
        """
        url = 'http://{}/get_caminfo.cgi'.format(self.ip)
        response = urlopen(url).read()
        e = BeautifulSoup(response, "lxml")
        return str(e.caminfo.model.string)

    def list(self):
        """
        Return image list in format: "/DCIM/100OLYMP,P5140001.JPG,2841785,0,19118,1440"
        :return:
        """
        url = 'http://{}/get_imglist.cgi?DIR=/DCIM/100OLYMP'.format(self.ip)
        response = BeautifulSoup(urlopen(url), "lxml")
        return [i.strip() for i in response.body.text.split('\n') if not i.startswith('VER_') and i]

    def download(self, directory='.', first_image=None, force=False):
        """
        Download images to directory
        :param directory: destination directory
        :param first_image: start downloading from this image
        :param force: download end overwrite even if file exist
        :return:
        """
        images_raw = self.list()
        images = [i.split(',') for i in images_raw]
        if first_image:
            if first_image in [i[1] for i in images]:
                first_image_position = images.index(next(i for i in images if i[1] == first_image))
                images = images[first_image_position:]
            else:
                print('WARNING: First image not found in list, all files will be downloaded')
        if not os.path.exists(directory):
            os.makedirs(directory)
        for image in images:
            url = 'http://{ip}/{path}/{filename}'.format(ip=self.ip, path=image[0], filename=image[1])
            dest = '{path}/{filename}'.format(path=directory, filename=image[1])
            print ' ' + image[1],
            if not os.path.exists(dest) or force:
                urllib.urlretrieve(url, dest)
                print(' - OK'.format(image[1]))
            else:
                print(' - SKIPPED'.format(image[1]))

    def power_off(self):
        url = 'http://{}/exec_pwoff.cgi'.format(self.ip)
        urlopen(url).read()


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='192.168.0.10', help='Camera IP address, default 192.168.0.10')
    parser.add_argument('--poweroff', action='store_true', help='Power-off camera at the end')
    subparsers = parser.add_subparsers(help='commands', dest='command')
    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('list', action='store_true', help='Get image list')
    download_parser = subparsers.add_parser('download')
    download_parser.add_argument('--out', metavar='<path>', default='.', help='Output directory, default current')
    download_parser.add_argument('--first', metavar='<filename>', help='Start downloading from this file')
    download_parser.add_argument('--force', action='store_true', help='Download even if local file exist')
    return parser.parse_args()


def main():
    args = arguments()
    olympus = Olympus(args.ip)
    try:
        print('-------------\nOlympus OM-D image downloader')
        print('Camera found: {}\n'.format(olympus.info()))
    except Exception as error:
        print('Failed to get camera info: ' + str(error))
        sys.exit(1)
    if args.command == 'list':
        images = olympus.list()
        print('Image list:')
        for image in images:
            print(image.split(',')[1])
    elif args.command == 'download':
        print('Downloading images:')
        olympus.download(directory=args.out, first_image=args.first, force=args.force)
    if args.poweroff:
        olympus.power_off()
    print('Done.')


if __name__ == '__main__':
    main()