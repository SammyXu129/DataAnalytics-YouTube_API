from googleapiclient.discovery import build
import os

api_key = os.environ["YOUTUBE_API_KEY"]
api_service_name = "youtube"
api_version = "v3"

channel_ids = ['UChVRfsT_ASBZk10o0An7Ucg',
               'UCsLF0qPTpkYKq81HsjgzhwQ',
               'UCTsM1dSAiXqiV5oZjuNw_Bg',
               'UCpis3RcTw6t47XO0R_KY4WQ',
               'UCpQ34afVgk8cRQBjSJ1xuJQ',
               'UCCgLoMYIyP0U56dEhEL1wXQ',
               'UC6TSBn2RAx036n04GaN6McA',
               'UCWN2FPlvg9r-LnUyepH9IaQ',
               'UCEbbyBuyQiHpKiOMj9GFhVw',
               'UCvGEK5_U-kLgO6-AMDPeTUQ',
               'UCiP6wD_tYlYLYh3agzbByWQ',
               'UCVQJZE_on7It_pEv6tn-jdA',
               'UCOpsZxrmeDARilha1uq4slA',
               'UCAxW1XT0iEJo0TYlRfn6rYQ']

# Get credentials and create an API client
youtube = build(
    api_service_name, api_version, developerKey=api_key)


def get_channel_stats(youtube, channel_ids):
    all_data = []

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()
    for item in response['items']:
        data = {
            'ChannelName': item['snippet']['title'],
            'subscribers': item['statistics']['subscriberCount'],
            'views': item['statistics']['viewCount'],
            'totalVideos': item['statistics']['videoCount'],
            'playListId': item['contentDetails']['relatedPlaylists']['uploads']
        }
        all_data.append(data)
    return pd.DataFrame(all_data)

channel_stats = get_channel_stats(youtube, channel_ids)
playlist_ids = channel_stats['playListId'].tolist()

def get_video_ids(youtube, playlist_ids):
    video_ids = []

    for playlist_id in playlist_ids:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
        while next_page_token is not None:
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token)
            response = request.execute()

            for item in response['items']:
                video_ids.append(item['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')

    return video_ids

video_ids = get_video_ids(youtube, playlist_ids)

def get_video_details(youtube, video_ids):
    all_video_info = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_ids[i:i + 50]
        )
        response = request.execute()

        for video in response['items']:
            stats_to_keep = {'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                             'statistics': ['viewCount', 'likeCount', 'favouriteCount', 'dislikeCount', 'commentCount'],
                             'contentDetails': ['duration', 'definition', 'caption']
                             }
            video_info = {}
            video_info['video_id'] = video['id']

            for key in stats_to_keep.keys():
                for value in stats_to_keep[key]:
                    try:
                        video_info[value] = video[key][value]
                    except:
                        video_info[value] = None
            all_video_info.append(video_info)
    return pd.DataFrame(all_video_info)

video_df = get_video_details(youtube, video_ids)
video_df.to_csv(r'/Users/jia/Documents/DATA LEARNING/YouTube_API/fitness_youtuber_video_data.csv')

# def get_comments_in_videos(youtube, video_ids):
#     all_comments = []
#     for video_id in video_ids:
#         request = youtube.commentThreads().list(
#             part="snippet,replies",
#             videoId=video_id
#         )
#         response = request.execute()
#
#         comments_in_video = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in response['items']]
#         comments_in_video_info = {'video_id': video_id,
#                                   'comments': comments_in_video}
#
#         all_comments.append(comments_in_video_info)
#
#     return pd.DataFrame(all_comments)

comment_df = get_comments_in_videos(youtube, video_ids)
comment_df.to_csv(r'/Users/jia/Documents/DATA LEARNING/YouTube_API/fitness_youtuber_comment_data.csv')