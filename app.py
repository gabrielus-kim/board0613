from flask import Flask, render_template, request, session
from flask import abort, redirect
import pymysql
from datetime import datetime

app = Flask(__name__,
            template_folder= 'template')

db = pymysql.connect(user = 'root',
                    passwd = 'avante',
                    db = 'web',
                    host = 'localhost',
                    charset = 'utf8',
                    cursorclass = pymysql.cursors.DictCursor)

app.secret_key = 'who are you?'
app.config['ENV'] = 'Development'
app.config['DEBUG'] = True

def who_am_i():
    return session['user']['name'] if 'user' in session else "Hi ! Everybody ~"
def am_i_here():
    return True if 'user' in session else False

def get_menu():
    if am_i_here() == False:
        return '현재 시간은 '+ datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = db.cursor()
    cursor.execute(f"""
        select id, title from topic 
    """)
    title = cursor.fetchall()
    menu=[]
    for i in title:
        menu.append(f"""
        <li><a href='{i['id']}'>{i['title']}</a></li>
        """)
    return '\n'.join(menu)

@app.route("/")
def index():
    if am_i_here() == True:
        title = "게시판 사용"
    else:
        title = "login 을 하셔야 사용가능합니다."
    return render_template('template.html',
                            owner = who_am_i(),
                            title = title,
                            menu = get_menu())

@app.route('/<id>')
def get_post(id):
    if am_i_here() == False:
        return redirect('/')
    cursor = db.cursor()
    cursor.execute(f"""
        select id, title, description from topic
        where id = '{id}'
    """)
    post = cursor.fetchone()
    return render_template('template.html',
                            owner = who_am_i(),
                            id = id,
                            title = post['title'],
                            content = post['description'],
                            menu = get_menu())

@app.route('/write', methods = ["GET","POST"])
def write_post():

    return render_template('write_post.html',
                            owner = who_am_i(),
                            title = title,
                            menu = get_menu())

@app.route("/login", methods = ["GET","POST"])
def login():
    if am_i_here() == True:
        return redirect('/')
    if request.method == "POST":
        cursor = db.cursor()
        cursor.execute(f"""
            select name from author 
            where name = '{request.form['id']}'
        """)
        user = cursor.fetchone()
        if user != None:
            cursor = db.cursor()
            cursor.execute(f"""
                select id, name, password from author
                where name = "{request.form['id']}" and
                password = SHA2("{request.form['pw']}", 256)
            """)
            user = cursor.fetchone()
            if user != None:
                session['user'] = user
                return redirect('/')
            else:
                title = " 입력하신 Password 가 잘못되었읍니다. 다시 입력하세요."
        else:
            title = " 입력하신 login ID 는 등록이 안되어 있읍니다."
    else:
        title = " please, login first"
    return render_template('login.html',
                            owner = who_am_i(),
                            title = title)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/join', methods=['GET','POST'])
def join():
    if am_i_here() == True:
        return redirect('/')
    
    title = " 가입해 주십시요."
    if request.method == "POST":
        cursor = db.cursor()
        cursor.execute(f"""
            select name from author
            where name = '{request.form['id']}'
        """)
        user = cursor.fetchone()
        if user == None:
            cursor = db.cursor()
            cursor.execute(f"""
                insert into author (name, profile, password)
                values ( '{request.form['id']}',
                        '{request.form['pf']}',
                        SHA2('{request.form['pw']}', 256))

            """)
            db.commit()
            return redirect('/')
        else:
            title = '이미 가입한 login ID 입니다.'
    return render_template('join.html',
                            owner= who_am_i(),
                            title = title)

@app.route('/withdraw', methods = ['GET','POST'])
def withdraw():
    if am_i_here() == False:
        return redirect('/')
    if request.method == 'POST':
        if request.form['subject'] == 'yes':
            cursor = db.cursor()
            cursor.execute(f"""
                delete from author
                where name = '{session['user']['name']}'
            """)
            db.commit()
            title = session['user']['name'] + "님 정상적으로 회원 탈퇴가 되었읍니다."
            session.pop('user', None)
        else:
            title = " 회원 탈퇴 요청을 반려하셨읍니다. 감사합니다."
        return render_template('template.html',
                                owner = who_am_i(),
                                title = title,
                                menu = get_menu())
    else:
        title = '정말로 회원 탈퇴를 하시겠읍니까?'
    return render_template('withdraw.html',
                            title = title,
                            owner = who_am_i())

@app.route("/favicon.ico")
def favicon():
    return abort(404)

app.run(port='8000')