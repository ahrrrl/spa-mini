# 필수 라이브러리
'''
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
'''
from flask import Flask, render_template, request, redirect, url_for, jsonify, json
app = Flask(__name__)
# DB 기본 코드
import os
import re
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

class Youtubes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(10000), nullable=False)
    link_url = db.Column(db.String(10000), nullable=False)


    def __repr__(self):
        return f'{self.username} {self.title} 추천 by {self.artist}'
    

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template('main.html')

@app.route("/youtubelinks/")
def youtubeLinks():
    song_list = Youtubes.query.all()
    return render_template('youtube.html', data=song_list)

@app.route('/youtubelinks/search/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        search_results = Youtubes.query.filter(
            (Youtubes.username.ilike(f'%{search_term}%')) |
            (Youtubes.title.ilike(f'%{search_term}%')) |
            (Youtubes.artist.ilike(f'%{search_term}%'))
        ).all()
        return render_template('youtube.html', data=search_results)
    return render_template('youtube.html')


@app.route("/youtubelinks/<username>/")
def render_youtubeLinks_filter(username):
    filter_list = Youtubes.query.filter_by(username=username).all()
    return render_template('youtube.html', data=filter_list)

def get_youtube_thumbnail_url(youtube_url):
    # 유튜브 ID 추출을 위한 정규식 패턴
    youtube_id_pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(youtube_id_pattern, youtube_url)
    if match:
        youtube_id = match.group(1)
        return f"https://img.youtube.com/vi/{youtube_id}/0.jpg"
    else:
        return None

@app.route("/youtubelinks/create/")
def youtubeLinks_create():
    #form에서 보낸 데이터 받아오기
    username_receive = request.args.get('username')
    title_receive = request.args.get('title')
    artist_receive = request.args.get('artist')
    link_url_receive = request.args.get('link_url')
    image_url_receive = get_youtube_thumbnail_url(link_url_receive)

    #데이터를 DB에 저장하기
    data = Youtubes(username=username_receive, title=title_receive, artist=artist_receive, image_url=image_url_receive, link_url = link_url_receive)
    db.session.add(data)
    db.session.commit()
    return redirect(url_for('render_youtubeLinks_filter', username=username_receive))
    

@app.route("/youtubelinks/delete/<int:id>", methods=['POST'])
def youtubeLinks_delete(id):
    youtube_to_delete = Youtubes.query.get_or_404(id)
    username = youtube_to_delete.username
    db.session.delete(youtube_to_delete)
    db.session.commit()
    return redirect(url_for('render_youtubeLinks_filter', username=username))

@app.route("/random_song/")
def random_song():
    random_youtube = Youtubes.query.order_by(func.random()).limit(3).all()
    if random_youtube:
        return jsonify([{
            'id': youtube.id,
            'username': youtube.username,
            'artist': youtube.artist,
            'title': youtube.title,
            'image_url': youtube.image_url,
            'link_url': youtube.link_url
        } for youtube in random_youtube])
    else:
        return jsonify({'error': 'No songs found'}), 404


# 방명록 데이터를 저장할 JSON 파일 경로
DATA_FILE = 'guestbook.json'

# JSON 파일에서 방명록 데이터를 읽어오는 함수
def read_data():
    try:
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    return data

# JSON 파일에 방명록 데이터를 저장하는 함수
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# 방명록 페이지 렌더링
@app.route('/guest')
def guest():
    return render_template('guest.html')

# 방명록 데이터 가져오기 API
@app.route('/entries', methods=['GET'])
def get_entries():
    data = read_data()
    return jsonify(data)

# 방명록 데이터 추가하기 API
@app.route('/add_entry', methods=['POST'])
def add_entry():
    name = remove_html_tags(request.json.get('name', '익명'))
    message = remove_html_tags(request.json['message'])
    password = request.json.get('password')

    data = read_data()
    data.append({'id': len(data) + 1, 'name': name, 'message': message, 'password': password})
    save_data(data)

    return jsonify({'success': True})

# 방명록 데이터 삭제하기 API
@app.route('/delete_entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    password = request.json['password']

    data = read_data()
    entry = next((entry for entry in data if entry['id'] == entry_id), None)
    if entry:
        if password == entry.get('password'):
            data.remove(entry)
            save_data(data)
            return jsonify({'success': True})
        else:
            return jsonify({'error': '비밀번호가 일치하지 않습니다.'}), 401
    else:
        return jsonify({'error': '해당 ID의 방명록을 찾을 수 없습니다.'}), 404

# 방명록 데이터 수정하기 API
@app.route('/edit_entry/<int:entry_id>', methods=['PUT'])
def edit_entry(entry_id):
    new_message = remove_html_tags(request.json['message'])
    password = request.json['password']

    data = read_data()
    entry = next((entry for entry in data if entry['id'] == entry_id), None)
    if entry:
        if password == entry.get('password'):
            entry['message'] = new_message
            save_data(data)
            return jsonify({'success': True})
        else:
            return jsonify({'error': '비밀번호가 일치하지 않습니다.'}), 401
    else:
        return jsonify({'error': '해당 ID의 방명록을 찾을 수 없습니다.'}), 404

if __name__ == "__main__":
    app.run(port=5001, debug=True)