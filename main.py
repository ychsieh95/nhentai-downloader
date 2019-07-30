import argparse
import datetime
import errno
import json
import os
from progress_bar import ProgressBar
import requests
from bs4 import BeautifulSoup

website_url = 'https://nhentai.net'

def download_result(type, gallery_id):
    status = {
        0: '[  OK  ] Downloaded gallery {} successfully'.format(gallery_id),
        1: '[FAILED] Gallery {} not found'.format(gallery_id),
        2: '[FAILED] Create directory for gallery {} failed'.format(gallery_id),
        3: '[FAILED] Download gallery {} failed'.format(gallery_id)
    }
    return status[type]

def clean_str(src_str):
    return src_str.replace('\t', '').replace('\r', '').replace('\n', '')

def json_to_file(data, filename='info', save_dir='.'):
    with open('{}/{}.json'.format(save_dir, filename), 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def download_image(url, filename, save_dir='.'):
    with open('{}/{}.jpg'.format(save_dir, filename), 'wb') as file:
        file.write(requests.get(url).content)

def get_page_range(url):
    response = requests.get(url)
    content = response.content.decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')

    last_anchor = soup.find('a', class_='last').get('href')
    first_page = 1
    last_page = last_anchor[last_anchor.index('=')+1:]

    return int(first_page), int(last_page)

def get_galleries(url):
    response = requests.get(url)
    content = response.content.decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')

    galleries = []
    for tag in soup.find_all('div', class_='gallery'):
        anchor = tag.find('a', class_='cover')
        id = anchor.get('href')
        name = anchor.find('div', class_='caption').contents[0]
        galleries.append([id[3:len(id)-1], name])

    return galleries

def get_gallery_info(div_info):
    info = {}

    # title
    info['title'] = div_info.find('h1').text

    # tags
    info['tags'] = {}
    tags_section = div_info.find('section', id='tags')
    for tag_container in tags_section.find_all('div'):
        tag_type = tag_container.contents[0].rstrip(':')

        tag_type = tag_container.contents[0][:-1]
        tag_names = {}
        for tag in tag_container.find_all('a'):
            tag_name = tag.contents[0].rstrip()
            tag_count = tag.find('span').contents[0]
            tag_names[tag_name] = int(tag_count[1:len(tag_count)-1].replace(',', ''))
        info['tags'][tag_type] = tag_names

    # pages
    pages_div = tags_section.next_sibling
    info['pages'] = pages_div.contents[0]
    info['pages'] = int(info['pages'][:info['pages'].index(' ')])

    # uploaded datetime
    uploaded_div = pages_div.next_sibling
    info['uploaded_datetime'] = uploaded_div.find('time').get('datetime')

    return info

def download_gallery(gallery_id, gallery_dir='.'):
    response = requests.get('{}/g/{}'.format(website_url, gallery_id))
    content = clean_str(response.content.decode('utf-8'))
    soup = BeautifulSoup(content, 'html.parser')

    # check gallery exists or not
    if soup.find('h1').contents[0] == '404 – Not Found':
        return 1

    # create directory
    try:
        os.makedirs(gallery_dir, exist_ok=True)
    except FileExistsError:
        return 2

    # get gallery info
    info = get_gallery_info(soup.find('div', id='info'))
    out_info = {
        'gallery': info,
        'created_datetime': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()}
    json_to_file(out_info, filename='info', save_dir=gallery_dir)

    # download gallery cover
    cover_div = soup.find('div', id='cover')
    cover_img_url = cover_div.find('a').find('img').get('data-src')
    download_image(cover_img_url, filename='cover', save_dir=gallery_dir)

    # download gallery content
    images_ids = cover_img_url.split('/')
    images_id  = images_ids[len(images_ids)-2]
    progress_bar = ProgressBar(info['pages'], length=20, padding=8)
    for page in range(1, info['pages'] + 1):
        try:
            download_image(
                'https://i.nhentai.net/galleries/{}/{}.jpg'.format(images_id, page),
                filename=page,
                save_dir=gallery_dir)
            progress_bar.display(page)
        except:
            return 3

    return 0

def check_gallery(gallery_id, gallery_dir='.'):
    json_path = '{}/info.json'.format(gallery_dir)
    if not os.path.isfile(json_path):
        return False
    elif not os.path.isfile('{}/cover.jpg'.format(gallery_dir)):
        return False
    else:
        try:
            with open(json_path, encoding='utf-8') as file:
                info = json.load(file)['gallery']
            for i in range(1, info['pages'] + 1):
                if not os.path.isfile('{}/{}.jpg'.format(gallery_dir, i)):
                    return False
            return True
        except:
            return False

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='A CLI tool to batch-download nHentai gallery.')
    parser.add_argument(
        '-i', '--id',
        action='store',
        type=int,
        help='gallery id to download')
    parser.add_argument(
        '-bg', '--begin-id',
        action='store',
        type=int,
        help='gallery id for begin download')
    parser.add_argument(
        '-eg', '--end-id',
        action='store',
        type=int,
        help='gallery id for end download')
    parser.add_argument(
        '-u', '--url',
        action='store',
        help='url for galleries list to download')
    parser.add_argument(
        '-bp', '--begin-page',
        action='store',
        type=int,
        help='page which in url for begin download')
    parser.add_argument(
        '-ep', '--end-page',
        action='store',
        type=int,
        help='page which in url for end download')
    parser.add_argument(
        '-s', '--save-dir',
        action='store',
        default='.',
        help='path for saving galleries.')
    parser.add_argument(
        '-es', '--exists-stop',
        action='store_true',
        help='stop downloading when gallery exists')
    parser.add_argument(
        '-ow', '--overwrite',
        action='store_true',
        help='overwrite or not when gallery exists')
    parser.add_argument(
        '-l', '--limit',
        action='store',
        type=int,
        default=-1,
        help='limit of download (-1 means unlimit)')
    parser.add_argument(
        '-ob', '--orderby',
        action='store',
        default='ascending',
        help='order of downloading, should be \'ascending\' or \'descending\'')

    args = parser.parse_args()
    print('[ INFO ] Options:', args)

    if args.id:
        # download gallery
        gallery_dir = '{}/{}'.format(args.save_dir, args.id)
        if os.path.isdir(gallery_dir) and not args.overwrite:
            print('[ WARN ] Pass gallery {} cause it exists'.format(gallery_id))
        else:
            print(download_result(
                type=download_gallery(args.id, '{}/{}'.format(args.save_dir, args.id)),
                gallery_id=args.id))

    elif args.begin_id and args.end_id:
        # check range of id
        if args.begin_id > args.end_id:
            print('[FAILED] Wrong range of begin_id ({}) to end_id ({})'.format(args.begin_id, args.end_id))
        else:
            # generate the range of galleries
            galleries = list(range(args.begin_id, args.end_id + 1))
            if args.orderby == 'descending':
                id_list.reverse()

            # download every gallery
            success, failure = 0, 0
            for gallery_id, gallery_name in galleries:
                # check the count of downloaded
                if args.limit >= 0 and success >= args.limit:
                    print('[ INFO ] Over the limit ({})'.format(args.limit))
                    exit(0)

                # check gallery exists or not
                gallery_dir = '{}/{}'.format(args.save_dir, gallery_id)
                if os.path.isdir(gallery_dir):
                    if args.exists_stop:
                        print('[ WARN ] Stop downloading cause gallery {} exists'.format(gallery_id))
                        exit(0)
                    elif args.overwrite:
                        print('[ WARN ] Downloading and overwriting gallery {}'.format(gallery_id))
                    else:
                        if not check_gallery(gallery_id, gallery_dir=gallery_dir):
                            print('[ WARN ] Overwrite gallery {} cause it exists but is damaged'.format(gallery_id))
                        else:
                            print('[ WARN ] Pass gallery {} cause it exists'.format(gallery_id))
                            continue
                else:
                    print('[ INFO ] Downloading gallery {}'.format(gallery_id))

                # download gallery
                status = download_gallery(gallery_id, gallery_dir=gallery_dir)
                if status == 0:
                    success += 1
                else:
                    failure += 1
                print('{} ({} / {})'.format(download_result(type=status, gallery_id=gallery_id), success, failure))

    elif args.url:
        # generate the range of pages
        first_page, last_page = get_page_range(args.url)
        if args.begin_page:
            first_page = args.begin_page
        if args.end_page:
            last_page = args.end_page
        pages = list(range(first_page, last_page + 1))

        # decide orderby
        if args.orderby == 'descending':
            page_list.reverse()

        # get galleries in every page
        success, failure = 0, 0
        for page in pages:
            galleries = get_galleries('{}?page={}'.format(args.url, page))
            print('[ INFO ] Page {} detected {} galleries'.format(page, len(galleries)))

            # download every gallery
            for gallery_id, gallery_name in galleries:
                # check the count of downloaded
                if args.limit >= 0 and success >= args.limit:
                    print('[ INFO ] Over the limit ({})'.format(args.limit))
                    exit(0)

                # check gallery exists or not
                gallery_dir = '{}/{}'.format(args.save_dir, gallery_id)
                if os.path.isdir(gallery_dir):
                    if args.exists_stop:
                        print('[ WARN ] Stop downloading cause gallery {} exists'.format(gallery_id))
                        exit(0)
                    elif args.overwrite:
                        print('[ WARN ] Downloading and overwriting gallery {}'.format(gallery_id))
                    else:
                        if not check_gallery(gallery_id, gallery_dir=gallery_dir):
                            print('[ WARN ] Overwrite gallery {} cause it exists but is damaged'.format(gallery_id))
                        else:
                            print('[ WARN ] Pass gallery {} cause it exists'.format(gallery_id))
                            continue
                else:
                    print('[ INFO ] Downloading gallery {}'.format(gallery_id))

                # download gallery
                status = download_gallery(gallery_id, gallery_dir=gallery_dir)
                if status == 0:
                    success += 1
                else:
                    failure += 1
                print('{} ({} / {})'.format(download_result(type=status, gallery_id=gallery_id), success, failure))
    else:
        print('[ INFO ] Do not detect any download option (id/url)')