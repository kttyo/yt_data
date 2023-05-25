import os
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import MySQLdb
import datetime
import time
import logging
import credentials


logging.basicConfig(level=logging.INFO)

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
api_service_name = 'youtube'
api_version = 'v3'

conn = MySQLdb.connect(host=credentials.DB_HOST, db=credentials.DATABASE,user=credentials.DB_USER,passwd=credentials.DB_PASSWORD,charset='utf8mb4')
c = conn.cursor()

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = credentials.GOOGLE_DEVELOPER_KEY)


def get_uploads_list():
    sql_string = 'select distinct uploads_list from yt_mst_cnl where uploads_list is not null'
    c.execute(sql_string)

    uploads_id_list = []
    for row in c.fetchall():
        uploads_id_list.append(row[0])

    return uploads_id_list


def get_mst_vid_list():
    sql_string = 'select distinct video_id from yt_mst_vid where video_id is not null order by video_id'
    c.execute(sql_string)

    mst_vid_list = []
    for row in c.fetchall():
        mst_vid_list.append(row[0])

    return mst_vid_list


def get_vid_list(playlist):
    request = youtube.playlistItems().list(
        part='snippet,contentDetails', # 取得したい情報の指定
        maxResults=50,
        playlistId= playlist
    )

    try:
        response = request.execute()
        items = response['items']
    except HttpError as error:
        logging.error(f"An HTTP error {error.resp.status} occurred:\n{error.content}")
        return []
    else:
        vid_list = []
        for item in items:
            vid = {
                'video_id': item['snippet']['resourceId']['videoId'],
                'video_name': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'] if len(item['snippet']['thumbnails']) else '',
                'channel_id': item['snippet']['channelId'],
                'published_at': item['snippet']['publishedAt'][0:10].replace('-','')
            }

            vid_list.append(vid)
        
        return vid_list


def insert_mysql(full_vid_list):
    values_list = []
    for video in full_vid_list:
        values = ('("'+
        video['video_id']+'","'+
        video['video_name'].replace('"','""')+'","'+
        video['description'].replace('"','""')+'","'+
        video['thumbnail']+'","'+
        video['channel_id']+'","'+
        video['published_at']+'","'+
        datetime.datetime.now().strftime('%Y%m%d')+
        '")')
        values_list.append(values)

    values_string = ','.join(values_list)

    sql_string = 'insert into yt_mst_vid values '+values_string+';'
    
    #print(sql_string)
    c.execute(sql_string)
    conn.commit()


def main():
    # get playlist of uploaded videos for each channel.
    uploads_id_list = get_uploads_list()
    logging.info('uploads_id_list: {}'.format(len(uploads_id_list)))


    # get list of videos existing in mst_vid table.
    mst_vid_list = get_mst_vid_list()
    logging.info('mst_vid_list: {}'.format(len(mst_vid_list)))

    # get videos in the playlists.
    new_vid_list = []
    for uploads_id in uploads_id_list:
        vid_list = get_vid_list(uploads_id)

        for video in vid_list:
            if video['video_id'] not in mst_vid_list:
                new_vid_list.append(video)

        print(len(new_vid_list))
        time.sleep(0.2)

    logging.info('new_vid_list: {}'.format(len(new_vid_list)))
    # insert video data into database.
    insert_mysql(new_vid_list)


if __name__ == '__main__':
    main()