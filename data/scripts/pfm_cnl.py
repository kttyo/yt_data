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

conn = MySQLdb.connect(host=credentials.DB_HOST, db=credentials.DATABASE,user=credentials.DB_USER,passwd=credentials.DB_PASSWORD,charset='utf8mb4')
c = conn.cursor()

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = credentials.GOOGLE_DEVELOPER_KEY)


def get_channel_list():
    sql_string = 'select distinct channel_id from yt_mst_cnl where uploads_list is not null'
    c.execute(sql_string)

    channel_list = []
    for row in c.fetchall():
        channel_list.append(row[0])

    return channel_list

def get_cnl_pfm_list(id_list):
    channels = ','.join(id_list)
    request = youtube.channels().list(
        part="statistics", # 取得したい情報の指定
        id=channels
    )
    response = request.execute()

    items = response['items']
    #print(items)
    
    cnl_pfm_list = []
    
    for item in items:
        cnl = {}
        cnl['channel_id'] = item['id']
        cnl['subscriber_count'] = item['statistics']['subscriberCount'] if 'subscriberCount' in item['statistics'].keys() else 0
        cnl['hidden_subscriber_count'] = 1 if item['statistics']['hiddenSubscriberCount'] == True else 0
        cnl['view_count'] = item['statistics']['viewCount']
        cnl['video_count'] = item['statistics']['videoCount']
        cnl_pfm_list.append(cnl)
        
    return cnl_pfm_list


def insert_mysql(cnl_pfm_list):
    values_list = []
    for cnl in cnl_pfm_list:
        values = ('("'+
        cnl['channel_id']+'","'+
        str(cnl['subscriber_count'])+'","'+
        str(cnl['hidden_subscriber_count'])+'","'+
        str(cnl['view_count'])+'","'+
        str(cnl['video_count'])+'","'+
        datetime.datetime.now().strftime('%Y%m%d')+
        '")')
        values_list.append(values)
    
    values_string = ','.join(values_list)

    sql_string = 'insert into yt_pfm_cnl values '+values_string+';'
    
    #print(sql_string)
    c.execute(sql_string)
    conn.commit()


def main():
    # get a list of distinct channel ids from database.
    cnl_list = get_channel_list()
    logging.info('cnl_list: {}'.format(len(cnl_list)))

    cnl_pfm_list = []
    # split the list into groups of 50 records and get channel stats.
    if len(cnl_list) > 50:
        start = 0
        end = 50
        while start < len(cnl_list):
            cnl_pfm_list_batch = get_cnl_pfm_list(cnl_list[start:end])
            for cnl_pfm in cnl_pfm_list_batch:
                cnl_pfm_list.append(cnl_pfm)
            logging.info('cnl_pfm_list: {}'.format(len(cnl_pfm_list)))
            start += 50
            end += 50
            time.sleep(0.5)

    else:
        cnl_pfm_list_batch = get_cnl_pfm_list(cnl_list)
        for cnl_pfm in cnl_pfm_list_batch:
            cnl_pfm_list.append(cnl_pfm)

    # insert channel stats into database.
    insert_mysql(cnl_pfm_list)


if __name__ == '__main__':
    main()