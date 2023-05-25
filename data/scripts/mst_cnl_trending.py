import os
import googleapiclient.discovery
import MySQLdb
import datetime
import time
import logging
import credentials


logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
api_service_name = 'youtube'
api_version = 'v3'

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = credentials.GOOGLE_DEVELOPER_KEY)


conn = MySQLdb.connect(host=credentials.DB_HOST, db=credentials.DATABASE,user=credentials.DB_USER,passwd=credentials.DB_PASSWORD,charset='utf8mb4')
c = conn.cursor()


def get_channel_id_list():
    request = youtube.videos().list(
        part='snippet', # 取得したい情報の指定
        chart='mostPopular', # chart に「mostPopular」を指定
        maxResults=50, # 最大件数
        regionCode='JP' # 地域コード
    )
    response = request.execute()

    channel_id_set = set()
    for video_item in response['items']:
        channel_id_set.add(video_item['snippet']['channelId'])

    return channel_id_set


def get_existing_id_list():
    sql_string = 'select distinct channel_id from yt_mst_cnl'
    c.execute(sql_string)

    uploads_id_list = set()
    for row in c.fetchall():
        uploads_id_list.add(row[0])

    return uploads_id_list


def get_channel_attr_list(id_list):
    channels = ','.join(id_list)
    request = youtube.channels().list(
        part='id,snippet,contentDetails', # 取得したい情報の指定
        id=channels
    )
    response = request.execute()
    
    channel_attr_list = []
    for channel_item in response['items']:
        channel_attr = {}
        channel_attr['channel_id'] = channel_item['id']
        channel_attr['channel_name'] = channel_item['snippet']['title']
        channel_attr['description'] = channel_item['snippet']['description']
        channel_attr['thumbnail'] = channel_item['snippet']['thumbnails']['default']['url']
        channel_attr['uploads_list'] = channel_item['contentDetails']['relatedPlaylists']['uploads']
        channel_attr['published_at'] = channel_item['snippet']['publishedAt'][0:10].replace('-','')
        channel_attr_list.append(channel_attr)

    return channel_attr_list

def insert_mysql(attr_list):
    conn = MySQLdb.connect(
        host=credentials.DB_HOST,
        db=credentials.DATABASE,
        user=credentials.DB_USER,
        passwd=credentials.DB_PASSWORD,
        charset='utf8mb4'
    )
    c = conn.cursor()

    values_list = []
    for channel in attr_list:
        values = ('("'+
        channel['channel_id']+'","'+
        channel['channel_name'].replace('"','""')+'","'+
        channel['description'].replace('"','""')+'","'+
        channel['thumbnail']+'","'+
        channel['uploads_list']+'","'+
        channel['published_at']+'","'+
        datetime.datetime.now().strftime('%Y%m%d')+
        '")')
        values_list.append(values)
    
    values_string = ','.join(values_list)
    
    sql_string = 'insert into yt_mst_cnl values '+values_string+';'
    c.execute(sql_string)
    
    conn.commit()

    c.close()
    conn.close()


def main():
    # get videos from youtube data API, and create a list of channels.
    trending_channels = get_channel_id_list()
    existing_channels = get_existing_id_list()

    channel_id_list = list(trending_channels - existing_channels)

    # get channel attributes from youtube data API.
    if len(channel_id_list) > 0:
        logging.info(f'{len(channel_id_list)} new channel id(s) were discovered.')
        channel_attr_list = get_channel_attr_list(channel_id_list)
        # insert channel attributes on the day to database.
        insert_mysql(channel_attr_list)
    else:
        logging.info('No new channel id was discovered.')


if __name__ == '__main__':
    main()