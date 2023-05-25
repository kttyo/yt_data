import collections
import logging
import os

import CaboCha
import googleapiclient.discovery
import xmltodict

import credentials
from os import path


if path.exists('/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd'):
    cabochac = CaboCha.Parser('-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd')
elif path.exists('/usr/local/lib/mecab/dic/mecab-ipadic-neologd'):
    cabochac = CaboCha.Parser('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
api_service_name = 'youtube'
api_version = 'v3'

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = credentials.GOOGLE_DEVELOPER_KEY)


def comment_thread_items(video_id):
    request_commentthreads = youtube.commentThreads().list(
        part="id,replies,snippet",
        maxResults=10,  # Maximum number of comment threads (100 is the limit)
        videoId=video_id,  # Video ID
        order="relevance"  # Order by relevance
    )
    try:
        response_commentthreads = request_commentthreads.execute()
        
    except:
        response_commentthreads = {
            'items':[]
        }

    return response_commentthreads['items']

def get_chunks(comment):
    tree = cabochac.parse(comment)
    xmltree = tree.toString(CaboCha.FORMAT_XML)
    comment_dict = xmltodict.parse(xmltree, attr_prefix='', cdata_key='surface', dict_constructor=dict)

    chunks = []
    if comment_dict['sentence']:  # sentence が存在する際に処理を行う
        if type(comment_dict['sentence']['chunk']) is not list:  # chunk を必ずリスト形式にする
            comment_dict['sentence']['chunk'] = [comment_dict['sentence']['chunk']]

        for chunk in comment_dict['sentence']['chunk']:
            if type(chunk['tok']) is not list:  # tok を必ずリスト形式にする
                chunk['tok'] = [chunk['tok']]

            for tok in chunk['tok']:
                feature_list = tok['feature'].split(',')  # feature をリスト形式に変換
                tok['feature'] = feature_list

        if comment_dict['sentence']['chunk']:  # chunk が存在する際に処理を行う
            for chunk in comment_dict['sentence']['chunk']:
                chunk_surface = ''
                for tok in chunk['tok']:
                    if tok['feature'][0] != '助詞' and tok['feature'][0] != '記号' and tok['feature'][0] != '連体詞':
                        chunk_surface += tok['surface']

                chunks.append(chunk_surface)

    return chunks


def get_most_used_words(video_id):
    comment_threads = comment_thread_items(video_id)
    # コメント文のリスト作成
    comments = []
    for item in comment_threads:
        #print(item['snippet']['topLevelComment']['snippet'])
        comments.append(item['snippet']['topLevelComment']['snippet']['textDisplay'].replace('\n','').replace('<br>','。'))

        if 'replies' in item.keys():
            for reply in item['replies']['comments']:
                comments.append(reply['snippet']['textDisplay'].replace('\n','').replace('<br>','。'))

    chunk_list = []
    for comment in comments:
        chunk_list += get_chunks(comment)
    collection = collections.Counter(chunk_list)
    
    most_used_words_list = []
    for word in collection.most_common(15):
        if len(word[0]) != 0:
            most_used_words_list.append(word[0])

    most_used_words = ','.join(most_used_words_list)

    return most_used_words

def main():
    print(get_most_used_words('i6oDthMc6oY'))

if __name__ == '__main__':
    main()