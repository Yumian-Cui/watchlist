import os
import sys

from flask import Flask, render_template
from markupsafe import escape
from flask import url_for
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
from views import views #import views from our views file
from models import db, User, Movie

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

#为了便于理解，你可以把 Web 程序看作是一堆这样的视图函数的集合：编写不同的函数处理对应 URL 的请求
app = Flask(__name__)
# app.register_blueprint(views)
app.register_blueprint(views, url_prefix="/")
#配置变量
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

# DO THIS AFTER initialized with the correct configuration!!!
db.init_app(app) # use the init_app method of the SQLAlchemy class to initialize the db object with the app object after it has been created

# db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app

#==========================================================================
# #创建了两个模型类来表示两类数据：用户信息和电影条目信息
# #模型类要声明继承 db.Model
# #记住！如果你改动了模型类，想重新生成表模式，那么需要先使用 db.drop_all() 删除表，然后重新创建（自定义命令 initdb，用flask initdb --drop删除表后重新创建）
# #注意这会一并删除所有数据，如果你想在不破坏数据库内的数据的前提下变更表的结构，需要使用数据库迁移工具，比如集成了 Alembic 的 Flask-Migrate（https://github.com/miguelgrinberg/Flask-Migrate） 扩展

# class User(db.Model):  # 模型类是User,表名将会是 user（自动生成，小写处理）
#     id = db.Column(db.Integer, primary_key=True)  # 主键
#     name = db.Column(db.String(20))  # 名字
#     movies = db.relationship('Movie', backref='user', lazy='dynamic') #将 User 表和 Movie 表建立关联 added a movies relationship to the User class, which will allow us to easily access all the movies associated with a specific user

# class Movie(db.Model):  # 模型类是Movie, 表名将会是 movie
#     id = db.Column(db.Integer, primary_key=True)  # 主键
#     title = db.Column(db.String(60))  # 电影标题
#     year = db.Column(db.String(4))  # 电影年份
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #将 User 表和 Movie 表建立关联 added a user_id column to the Movie table, which is a foreign key that references the id column in the User table

# #https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#one-to-many-relationships

@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于 return {'user': user}

#404 错误处理函数 当 404 错误发生时，这个函数会被触发，返回值会作为响应主体返回给客户端
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    # user = User.query.first()
    return render_template('404.html'), 404  # 返回模板和状态码


#编写一个自定义命令来自动执行创建数据库表操作
import click
@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息
#如果你想在不破坏数据库内的数据的前提下变更表的结构，需要使用数据库迁移工具，比如集成了 Alembic 的 Flask-Migrate(https://github.com/miguelgrinberg/Flask-Migrate) 扩展

#执行 flask forge 命令就会把所有虚拟数据添加到数据库里
@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = 'Lumi'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        movie.user_id = user.id
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')


#==========================================================================

# @app.route('/')
# def index():
#     user = User.query.first()  # 读取用户记录
#     movies = Movie.query.all()  # 读取所有电影记录
#     return render_template('index.html', user=user, movies=movies)
#     # return render_template('index.html', name=name, movies=movies)
# # 为了让模板正确渲染，我们还要把模板内部使用的变量(name, movies)通过关键字参数传入这个函数

# # @app.route('/')
# # # @app.route('/index')
# # # @app.route('/home')
# # # 当用户在浏览器访问这个 URL 的时候，就会触发这个视图函数（view funciton）这里的 /指的是根地址
# # def hello():
# #     return '<h1>你好 Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

# @app.route('/user/<name>')
# def user_page(name):
#     return f'User: {escape(name)}'

# @app.route('/test')
# def test_url_for():
#     # 下面是一些调用示例（请访问 http://localhost:5000/test 后在命令行窗口查看输出的 URL）：
#     print(url_for('hello'))  # 生成 hello 视图函数对应的 URL，将会输出：/
#     # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
#     print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
#     print(url_for('user_page', name='peter'))  # 输出：/user/peter
#     print(url_for('test_url_for'))  # 输出：/test
#     # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
#     print(url_for('test_url_for', num=2))  # 输出：/test?num=2
#     return 'Test page'

#==========================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5000) #debug mode 调试模式开启后，当程序出错，浏览器页面上会显示错误信息；代码出现变动后，程序会自动重载。

# . env/Scripts/activate