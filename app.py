import os, sys, click, re

from flask import Flask, render_template, flash, redirect, request
from markupsafe import escape
from flask import url_for
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, PasswordField
from wtforms.validators import DataRequired, Length, Email
from datetime import datetime
from wtforms import widgets
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate # pip install -U bootstrap-flask
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
# from flask_security import Security, SQLAlchemyUserDatastore, \
#     UserMixin, RoleMixin, login_required, utils
# from wtforms import Field as BaseField
# from flask_security import UserMixin
# from flask_security import Security, SQLAlchemyUserDatastore, \
#     UserMixin, RoleMixin, login_required
# from flask_security.forms import LoginForm

# from views import views #import views from our views file
# from models import db, User, Movie

from wtforms import StringField as BaseStringField, PasswordField as BasePasswordField, Field as BaseField

class Field(BaseField):
    def __init__(self, label=None, validators=None, **kwargs):
        kwargs.setdefault('render_kw', {}).setdefault('class', 'form-field')
        super().__init__(label, validators, **kwargs)

class AuthStringField(Field, BaseStringField):
    pass

class AuthPasswordField(Field, BasePasswordField):
    pass

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
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

bootstrap = Bootstrap5(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com' # smtp.live.com
app.config['MAIL_PORT'] =  465 #587
# app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') # set your email with export EMAIL_USER=your-email-username in terminal
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') # set your password with export EMAIL_PASS=your-email-password in terminal


mail = Mail(app)

# DO THIS AFTER initialized with the correct configuration!!!
# db.init_app(app) # use the init_app method of the SQLAlchemy class to initialize the db object with the app object after it has been created

db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app
migrate = Migrate(app, db) # https://github.com/miguelgrinberg/Flask-Migrate

app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ('username','email')


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
        movie = Movie(title=title, year=year, user_id=current_user.id)  # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created.')  # 显示成功创建的提示
        return redirect(url_for('index'))
    movies = Movie.query.filter_by(user_id=current_user.id).all() if current_user.is_authenticated else [] # New: Only get the current user's movies
    # movies = Movie.query.all()
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
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            identifier = form.identifier.data
            password = form.password.data

            if not identifier or not password:
                flash('Invalid input.')
                return redirect(url_for('login'))
            
            # Check if identifier is a username or an email
            is_email = User.email == identifier
            user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
            if user is None:
                flash('User does not exist.')
                return redirect(url_for('register'))
            
            if is_email and not user.email_confirmed:
                flash('Email registered but not confirmed. A new confirmation has been sent. Please confirm it via your inbox first.')
                token = generate_confirmation_token(user.email, user.id)
                send_email_confirmation(user.email, token)
                return redirect(url_for('login'))
            
            # Validate the password
            if user.validate_password(password):
                login_user(user)  # Log in the user
                flash('Login success.')
                return redirect(url_for('index'))  # Redirect to the home page
            
            flash('Invalid username/email or password.')  # If validation fails, display an error message
            
            return redirect(url_for('login'))  # 重定向回登录页面


    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            email = form.email.data

            user = User.query.filter_by(username=username).first()
            if user is not None:
                flash('Username already exists. Please log in.')
                return redirect(url_for('login'))
            
            # Check if the email already exists
            user = User.query.filter_by(email=email).first()
            if user is not None:
                flash('Email already exists. Please use another one.')
                return redirect(url_for('register'))

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Generate a confirmation token and send a confirmation email
            # this try except logic might be revised in the future. 
            try:
                token = generate_confirmation_token(email, user.id)
                send_email_confirmation(email, token)
                flash('Registration successful. A confirmation email has been sent to your email address.')
            except Exception as e:
                # If sending the email fails, delete the user and the token from the database
                confirm_token = EmailConfirmationToken.query.filter_by(user_id=user.id).first()
                if confirm_token:
                    db.session.delete(confirm_token)
                db.session.delete(user)
                db.session.commit()
                flash('Error sending confirmation email. Please try again.' + str(e))
                return redirect(url_for('register'))           
        
            # login_user(user)  # log in the user
            return redirect(url_for('login'))  # redirect to the main page

    return render_template('register.html', form=form)

@app.route('/confirm-email/<token>')
def confirm_email(token):
    confirm_token = EmailConfirmationToken.query.filter_by(token=token).first()
    if confirm_token and not confirm_token.used:
        user = User.query.get(confirm_token.user_id)
        user.email_confirmed = True
        db.session.commit()
        confirm_token.used = True
        db.session.commit()
        # login_user(user)  # log in the user
        flash('Your email has been confirmed. You can now log in or use it for password reset.')
        return redirect(url_for('login'))
    else:
        flash('Invalid or expired confirmation token.')
    return redirect(url_for('index'))

def generate_confirmation_token(email, user_id):
    # s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps(email, salt='email-confirm')
    
    # Associate the token with the user and store it in the database
    confirm_token = EmailConfirmationToken(user_id=user_id, token=token)
    db.session.add(confirm_token)
    db.session.commit()

    return token

def send_email_confirmation(email, token):
    """
    Send a confirmation email to the given address.

    Args:
    email (str): The recipient's email address.
    token (str): The confirmation token to be included in the email.
    """
    msg = Message('Confirm your email', sender='noreply@wl.com', recipients=[email])
    msg.body = f"""\
Hello,

You're receiving this email because you've either registered a new account with us or prompted an email confirmation link.

Please click the following link to confirm your email address: {url_for('confirm_email', token=token, _external=True)}. You will then be redirected to login.

If you did not request this email, you can safely ignore it.

Best,
Watchlist App Team
    """
    mail.send(msg)


def send_password_reset(email, token):
    msg = Message('Reset your password', sender='noreply@wl.com', recipients=[email])
    msg.body = f"""\
Hello,

You're receiving this email because you've requested a password reset.

Please click the following link to reset: {url_for('reset_password_helper', token=token, _external=True)}.

If you did not request this email, you can safely ignore it.

Best,
Watchlist App Team
    """
    mail.send(msg)  

@app.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_password_helper(token):
    form = ResetPasswordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            try:
                # Attempt to load the email from the token
                email = s.loads(token, salt='reset-password', max_age=3600)  # Token is valid for 1 hour
            except Exception as e:
                flash("The password reset link is invalid or has expired.")
                return redirect(url_for('reset_password'))
            user = User.query.filter_by(email=email).first()
            new_password = form.new_password.data
            confirm_password = form.confirm_password.data
            if user:
                if not user.validate_password(new_password):
                    if new_password == confirm_password:  # check if both passwords match
                        user.set_password(new_password)
                        db.session.commit()
                        flash("Your password has been reset.")
                        # login_user(user)
                        return redirect(url_for('login'))
                    else:
                        flash("Passwords do not match.")  # return an error message if passwords do not match
                else:
                    flash("Your previous password cannot be reused.")
            else:
                flash("Invalid token or email address.")
    return render_template('reset_password_helper.html', form=form)


# One shouldn't need to request their username: they need to retrieve username based on email; if they remember email then they
# can log in with their unique email identifier

@app.route('/find_username', methods=['GET', 'POST'])
def find_username():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            if user.email_confirmed:
                flash('Email confirmed already. You may now log in using your email and find your username in the settings.')
                return redirect(url_for('login'))
            else:
                token = generate_confirmation_token(email, user.id)
                send_email_confirmation(email, token)
                flash('Your email is registered but not confirmed. Please confirm it via your inbox, log in with your email and find your username in the settings.')
        else:
            flash('No account found with that email.')
        return redirect(url_for('find_username'))
    return render_template('find_username.html')

@app.route('/reset_password', methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            if not user.email_confirmed:
                token = generate_confirmation_token(email, user.id)
                send_email_confirmation(email, token)
                flash('Your email is registered but not confirmed. Please confirm it via your inbox now and return to this page to proceed with password reset.')
                return redirect(url_for('reset_password'))
            token = s.dumps(email, salt='reset-password')
            # ... send `token` to user's email address ...
            try:
                send_password_reset(email, token)
            except:
                flash('Error sending reset email. Please try again.')
                return redirect(url_for('reset_password'))
            flash("Please check your email for a password reset link.")
        else:
            flash("Email address not found.")
    return render_template('reset_password.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页

#设置页面，支持修改用户的名字
#支持用户删除账户
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        if 'confirm_delete' in request.form:
            # User confirmed deletion
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            flash('Your account has been deleted.')
            return redirect(url_for('index'))

        # A dictionary to store the form fields that can be updated
        updatable_fields = {
            'name': {
                'max_length': 20,
                'error_message': 'Invalid name.'
            },
            'username': {
                'max_length': 20,
                'error_message': 'Invalid username.',
                'unique_error_message': 'Username already exists.'
            },
            'email': {
                'max_length': 50,
                'error_message': 'Invalid email.',
                'unique_error_message': 'Email already exists.'
            }
        }

        updated_fields = []
        for field, info in updatable_fields.items():
            value = request.form.get(field)
            if value and value.strip():  # Check if the field value is not empty or whitespace
                if len(value) <= info['max_length']: # TODO: this place should use form, otherwise, although browser might have built-in form validation, it is not caught here and might cause field to be updated
                    # Check if the field is unique
                    user_with_same_field = User.query.filter_by(**{field: value}).first()
                    if user_with_same_field is None or user_with_same_field.id == current_user.id:
                        old_email = current_user.email
                        setattr(current_user, field, value)
                        updated_fields.append(field)
                        # Currently, email is wrongly updated without form validation. TODO
                        if field == 'email':
                            if not current_user.email_confirmed:
                                # Generate a confirmation token and send a confirmation email
                                try:
                                    token = generate_confirmation_token(value, current_user.id)
                                    send_email_confirmation(value, token)
                                except Exception as e:
                                    flash('Failed to send email. Check if you accidentally misspelled it.')
                                    return redirect(url_for('settings'))
                                if old_email == current_user.email:
                                    flash('A confirmation email has been re-sent to your email address.')
                                else:
                                    flash('A confirmation email has been sent to your new email address.')
                    else:
                        flash(info['unique_error_message'])
                        return redirect(url_for('settings'))
                else:
                    flash(info['error_message'])
                    return redirect(url_for('settings'))

        if len(updated_fields) != 0:
            db.session.commit()
            flash('Settings updated: ' + ', '.join(updated_fields) + '.')
        # return redirect(url_for('index'))

        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name

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
    username = db.Column(db.String(20),unique=True)  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值   
    email = db.Column(db.String(120), unique=True) 
    email_confirmed = db.Column(db.Boolean, default=False)
    movies = db.relationship('Movie', backref='user', lazy='dynamic') #将 User 表和 Movie 表建立关联 added a movies relationship to the User class, which will allow us to easily access all the movies associated with a specific user

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值
    


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

class EmailConfirmationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    token = db.Column(db.String(100))
    used = db.Column(db.Boolean, default=False)


# #https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#one-to-many-relationships

# from wtforms.validators import ValidationError

# def validate_year(form, field):
#     if field.data > datetime.now().year:
#         raise ValidationError('Year cannot be after current year.')

#Create a new class that inherits from FlaskForm:
class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=60)]) #first argument is the label of the field, which is used to generate the label tag in the HTML form
    year = StringField('Year', validators=[DataRequired(), Length(min=4, max=4, message='Invalid year.')]) #length must be 4
    # year = DateField('year', validators=[DataRequired()], format='%Y')
    submit = SubmitField()

# END CLASS
# Assuming 'User' is your user model and it includes the fields 'email' and 'password'
# class ExtendedLoginForm(LoginForm):
#     identifier = StringField('Username or Email', [DataRequired()])
#     # password = PasswordField('Password', validators=[DataRequired()])
#     # submit = SubmitField('Log In')

# Setup Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, User)
# security = Security(app, user_datastore, login_form=ExtendedLoginForm)

# Authentification form fields follow a different styling than MovieForm
class LoginForm(FlaskForm):
    identifier = AuthStringField('Username or Email', validators=[DataRequired()])
    password = AuthPasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    username = AuthStringField('Username', validators=[DataRequired()])
    email = AuthStringField('Email', validators=[DataRequired(), Email()])
    password = AuthPasswordField('Password', validators=[DataRequired()])
    create = SubmitField('Create')

class ResetPasswordForm(FlaskForm):
    new_password = AuthPasswordField('New Password', validators=[DataRequired()])
    confirm_password = AuthPasswordField('Confirm Password', validators=[DataRequired()])
    reset = SubmitField('Reset')

# class SettingForm(FlaskForm):




    
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

#==========================================================================


# if __name__ == '__main__':
#     app.run(debug=True, port=5000) #debug mode 调试模式开启后，当程序出错，浏览器页面上会显示错误信息；代码出现变动后，程序会自动重载。

# . env/Scripts/activate
