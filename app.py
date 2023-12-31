import os, sys, click

from flask import Flask, render_template, flash, redirect, request
from markupsafe import escape
from flask import url_for
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField
from wtforms.validators import DataRequired, Length
from datetime import datetime
from wtforms import widgets
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import login_required, logout_user, current_user

# from views import views #import views from our views file
# from models import db, User, Movie

# ******************************************** APP ********************************************

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

#为了便于理解，你可以把 Web 程序看作是一堆这样的视图函数的集合：编写不同的函数处理对应 URL 的请求
app = Flask(__name__)
# app.register_blueprint(views)
# app.register_blueprint(views, url_prefix="/")
#配置变量
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'

bootstrap = Bootstrap5(app)

# DO THIS AFTER initialized with the correct configuration!!!
# db.init_app(app) # use the init_app method of the SQLAlchemy class to initialize the db object with the app object after it has been created

db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app
migrate = Migrate(app, db) # https://github.com/miguelgrinberg/Flask-Migrate

@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于 return {'user': user}

#404 错误处理函数 当 404 错误发生时，这个函数会被触发，返回值会作为响应主体返回给客户端
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    # user = User.query.first()
    return render_template('404.html'), 404  # 返回模板和状态码

#400 错误处理函数 当 400 错误发生时，这个函数会被触发，返回值会作为响应主体返回给客户端
@app.errorhandler(400)  # 传入要处理的错误代码
def bad_request(e):  # 接受异常对象作为参数
    # user = User.query.first()
    return render_template('400.html'), 400  # 返回模板和状态码

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


#编写一个自定义命令来自动执行创建数据库表操作
@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
# flask initdb 
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

# END APP

# ******************************************** VIEWS ********************************************

@app.route('/', methods=['GET', 'POST'])
# 当用户在浏览器访问这个 URL 的时候，就会触发这个视图函数（view funciton）这里的 /指的是根地址
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页
    form = MovieForm()
    if form.validate_on_submit():
        title = form.title.data
        year = form.year.data
        # Add movie to database here...
        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created.')  # 显示成功创建的提示
        return redirect(url_for('index'))
    movies = Movie.query.all()
    return render_template('index.html', movies=movies, form=form)

@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm(obj=movie)
    if form.validate_on_submit():
        movie.title = form.title.data
        movie.year = form.year.data
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))
    return render_template('edit.html', movie=movie, form=form) # 传入被编辑的电影记录

@app.route('/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required  # 登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页

#设置页面，支持修改用户的名字
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')

@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}'

@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请访问 http://localhost:5000/test 后在命令行窗口查看输出的 URL）：
    print(url_for('index'))  # 生成 hello 视图函数对应的 URL，将会输出：/
    # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
    print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
    print(url_for('user_page', name='peter'))  # 输出：/user/peter
    print(url_for('test_url_for'))  # 输出：/test
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
    print(url_for('test_url_for', num=2))  # 输出：/test?num=2
    return 'Test page'

# END VIEWS

# ******************************************** CLASS ********************************************

# #创建了两个模型类来表示两类数据：用户信息和电影条目信息
# #模型类要声明继承 db.Model
# #记住！如果你改动了模型类，想重新生成表模式，那么需要先使用 db.drop_all() 删除表，然后重新创建（自定义命令 initdb，用flask initdb --drop删除表后重新创建）
# #注意这会一并删除所有数据，如果你想在不破坏数据库内的数据的前提下变更表的结构，需要使用数据库迁移工具，比如集成了 Alembic 的 Flask-Migrate（https://github.com/miguelgrinberg/Flask-Migrate） 扩展

class User(db.Model, UserMixin):  # 模型类是User,表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值    
    movies = db.relationship('Movie', backref='user', lazy='dynamic') #将 User 表和 Movie 表建立关联 added a movies relationship to the User class, which will allow us to easily access all the movies associated with a specific user

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值


# 编写一个命令来创建管理员账户
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')

@app.cli.command()
def delusers():
    """Delete all users."""
    click.confirm('This will delete all users. Do you want to continue?', abort=True)

    num_deleted = User.query.delete()
    db.session.commit()

    click.echo(f'Deleted {num_deleted} users.')

login_manager = LoginManager(app)  # 实例化扩展类

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

login_manager.login_view = 'login'
login_manager.login_message = "You do not have access to that content. Please login first or contact administrator."

class Movie(db.Model):  # 模型类是Movie, 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #将 User 表和 Movie 表建立关联 added a user_id column to the Movie table, which is a foreign key that references the id column in the User table

# #https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#one-to-many-relationships

# from wtforms.validators import ValidationError

# def validate_year(form, field):
#     if field.data > datetime.now().year:
#         raise ValidationError('Year cannot be after current year.')

#Create a new class that inherits from FlaskForm:
class MovieForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(max=60)]) #first argument is the label of the field, which is used to generate the label tag in the HTML form
    year = StringField('year', validators=[DataRequired(), Length(min=4, max=4, message='Invalid year.')]) #length must be 4
    # year = DateField('year', validators=[DataRequired()], format='%Y')
    submit = SubmitField()

# END CLASS

#==========================================================================


# if __name__ == '__main__':
#     app.run(debug=True, port=5000) #debug mode 调试模式开启后，当程序出错，浏览器页面上会显示错误信息；代码出现变动后，程序会自动重载。

# . env/Scripts/activate
