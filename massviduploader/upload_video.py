import time
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build


videos_subidos = 0


def upload_video(credentials, video_file_path, title, description, category, keywords, privacy_status, publish_at):
    youtube = build('youtube', 'v3', credentials=credentials)
    global videos_subidos
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': keywords.split(','),
            'categoryId': category
        },
        'status': {
            'privacyStatus': privacy_status,
            'madeForKids': False
        }
    }

    # Configura la fecha y hora de publicación solo si el video es privado
    if privacy_status == "private" and publish_at:
        body['status']['publishAt'] = publish_at

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(
            video_file_path, chunksize=-1, resumable=True)
    )

    response = None
    error = None
    try:
        print('Uploading file...')
        response = insert_request.execute()
        print('Upload successful! Video ID:', response['id'])
        videos_subidos += 1
        if videos_subidos % 6 == 0:
            print(
                "Limite de cuota alcanzado. Esperando para continuar con la subida de videos...")
            time.sleep(24.5 * 3600)  # Espera 24 horas y media
    except Exception as e:
        print('An error occurred:', e)
        error = e

    return response, error


def get_category_id(youtube, category_name):
    categories_list = youtube.videoCategories().list(
        part='snippet',
        regionCode='US'  # O tu código de región específico
    ).execute()

    for category in categories_list.get('items', []):
        if category['snippet']['title'].lower() == category_name.lower():
            return category['id']
    return None
