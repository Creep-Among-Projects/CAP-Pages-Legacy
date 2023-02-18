import os
import time

import requests

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

GENERAL_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
                  'Safari/537.36 Edg/110.0.1587.46'
}

PEXELS_HEADERS = {
    'Authorization': os.getenv('PEXELS_API_KEY'),
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
                  'Safari/537.36 Edg/110.0.1587.46'
}

PEXELS_QUERY = ['nature', 'sunset', 'sea']

HITOKOTO_URL = 'https://international.v1.hitokoto.cn/?c=d&c=f&c=h&c=i&c=k&max_length=25'

engine = sqlalchemy.engine.create_engine('sqlite:///./apps/qod/db.db?check_same_thread=False', echo=True)
Base = sqlalchemy.ext.declarative.declarative_base()


class Backgrounds(Base):
    __tablename__ = 'backgrounds'
    ID = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    pexels_id = sqlalchemy.Column(sqlalchemy.Integer)
    url = sqlalchemy.Column(sqlalchemy.String(200))
    avg_color = sqlalchemy.Column(sqlalchemy.String(7))
    src = sqlalchemy.Column(sqlalchemy.String(200))
    alt = sqlalchemy.Column(sqlalchemy.String(200))
    time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=sqlalchemy.func.current_timestamp())


class Quotes(Base):
    __tablename__ = 'quotes'
    ID = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    uuid = sqlalchemy.Column(sqlalchemy.String(36))
    hitokoto = sqlalchemy.Column(sqlalchemy.String(100))
    typ = sqlalchemy.Column(sqlalchemy.String(1))
    src = sqlalchemy.Column(sqlalchemy.String(100))
    author = sqlalchemy.Column(sqlalchemy.String(50))
    time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=sqlalchemy.func.current_timestamp())


Base.metadata.create_all(engine, checkfirst=True)
session = sqlalchemy.orm.create_session(bind=engine)

print('IP Address:', requests.get('http://ip-api.com/json', headers=GENERAL_HEADERS).json()['query'])

# Fetch Pexels Images
images_url = []

for _ in PEXELS_QUERY:
    for c in range(10):
        pexels_search_result = requests.get('https://api.pexels.com/v1/search', headers=PEXELS_HEADERS,
                                            params={'query': _, 'orientation': 'landscape'}).json()
        for _i in pexels_search_result['photos']:
            if session.query(Backgrounds).filter_by(pexels_id=_i['id']).all():
                continue
            print('Picture Information', _i['id'], _i['alt'].replace(' ', '_'), sep='.')
            new_image = Backgrounds(
                alt=_i['alt'],
                avg_color=_i['avg_color'],
                pexels_id=_i['id'],
                src=_i['src']['original'],
                url=_i['url']
            )
            session.add(new_image)
            session.commit()
            images_url.append(_i['id'])
            break
        else:
            time.sleep(0.1)
            continue
        break
    else:
        print('No More Pictures!')

print(images_url)

# Download Pexels Images to Temporary Folder
os.mkdir('cache')
for _ in images_url:
    try:
        print('Downloading', _)
        with open(f'./cache/{_}.jpg', 'wb') as f:
            f.write(requests.get(f'https://images.pexels.com/photos/{_}/pexels-photo.jpg',
                                 headers=GENERAL_HEADERS).content)
    except:
        pass

downloaded_images = [_ for _ in os.walk('cache')]
print('Download finished:', downloaded_images)

# Fetch Quotes
quotes = []
while len(quotes) < len(downloaded_images):
    hitokoto_result = requests.get(HITOKOTO_URL, headers=GENERAL_HEADERS).json()
    break
