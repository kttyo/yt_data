import datetime
import logging
import os
import time

import googleapiclient.discovery
import MySQLdb

import credentials
from comment_nlp import get_most_used_words
from os import path

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')


# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
api_service_name = 'youtube'
api_version = 'v3'


conn = MySQLdb.connect(host=credentials.DB_HOST, db=credentials.DATABASE,user=credentials.DB_USER,passwd=credentials.DB_PASSWORD,charset='utf8mb4')
c = conn.cursor()

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = credentials.GOOGLE_DEVELOPER_KEY)


def get_vid_list():
    today = datetime.datetime.now()
    filter_date = today - datetime.timedelta(7) # goes back 7 days
    filter_date_str = filter_date.strftime('%Y%m%d')

    sql_string = f'select distinct video_id from yt_mst_vid where video_id is not null and published_at >= {filter_date_str}'
    c.execute(sql_string)

    vid_list = []
    for row in c.fetchall():
        vid_list.append(row[0])

    #print(len(vid_list))

    return vid_list


def get_vid_pfm_list(id_list):
    vid_list = ','.join(id_list)
    request = youtube.videos().list(
        part="statistics", # 取得したい情報の指定
        id=vid_list
    )
    response = request.execute()

    items = response['items']
    #print(items)
    
    vid_pfm_list = []
    
    for item in items:
        vid = {
            'video_id': item['id'],
            'view_count': item['statistics']['viewCount'] if 'viewCount' in item['statistics'].keys() else 0,
            'like_count': item['statistics']['likeCount'] if 'likeCount' in item['statistics'].keys() else 0,
            'dislike_count': item['statistics']['dislikeCount'] if 'dislikeCount' in item['statistics'].keys() else 0,
            'favorite_count': item['statistics']['favoriteCount'],
            'comment_count': item['statistics']['commentCount'] if 'commentCount' in item['statistics'].keys() else 0,
            'most_used_words': get_most_used_words(item['id']) if 'commentCount' in item['statistics'].keys() else '',
        }
        #print(vid)
        vid_pfm_list.append(vid)
        logging.info('video_id: {} was processed.'.format(item['id']))
        time.sleep(0.2)
        
    return vid_pfm_list


def truncate_insert_mysql(vid_pfm_list):
    values_list = []
    for vid in vid_pfm_list:
        values = ('("'+
        vid['video_id']+'","'+
        str(vid['view_count'])+'","'+
        str(vid['like_count'])+'","'+
        str(vid['dislike_count'])+'","'+
        str(vid['favorite_count'])+'","'+
        str(vid['comment_count'])+'","'+
        str(vid['most_used_words'])+'","'+
        datetime.datetime.now().strftime('%Y%m%d')+
        '")')
        values_list.append(values)
    
    values_string = ','.join(values_list)

    c.execute('truncate table yt_pfm_vid;')
    c.execute('insert into yt_pfm_vid values '+values_string+';')

    conn.commit()


def main():
    # get a list of videos of certain range of published dates from database.
    vid_list = get_vid_list()
    logging.info('vid_list: {}'.format(len(vid_list)))

    vid_pfm_list = []
    # split the list into groups of 50 records and get video stats.


    if len(vid_list) > 50:
        start = 0
        end = 50
        while start < len(vid_list):
            logging.info('Processing: {} to {}'.format(start, end))
            vid_pfm_list_batch = get_vid_pfm_list(vid_list[start:end])
            for i in vid_pfm_list_batch:
                vid_pfm_list.append(i)
            logging.info('vid_pfm_list: {}'.format(len(vid_pfm_list)))
            start += 50
            end += 50
            time.sleep(0.2)

    else:
        vid_pfm_list_batch = get_vid_pfm_list(vid_list)
        for i in vid_pfm_list_batch:
            vid_pfm_list.append(i)
            

    # insert video stats into database.
    truncate_insert_mysql(vid_pfm_list)
    logging.info('truncate-insert completed')

if __name__ == '__main__':
    main()