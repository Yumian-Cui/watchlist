import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta
from flask_mail import Mail


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
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
s = URLSafeTimedSerializer(app.config['SECRET_KEY']) # TODO

bootstrap = Bootstrap5(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com' # smtp.live.com
app.config['MAIL_PORT'] =  465 #587
# app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') # set your email with export EMAIL_USER=your-email-username in terminal
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') # set your password with export EMAIL_PASS=your-email-password in terminal


mail = Mail(app) # TODO

# DO THIS AFTER initialized with the correct configuration!!!
# db.init_app(app) # use the init_app method of the SQLAlchemy class to initialize the db object with the app object after it has been created

db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app
migrate = Migrate(app, db) # https://github.com/miguelgrinberg/Flask-Migrate

app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ('username','email')

csrf = CSRFProtect(app)

login_manager = LoginManager(app)  # 实例化扩展类

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    from app.models import User
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

login_manager.login_view = 'login'
login_manager.login_message = "You do not have access to that content. Please login first or contact administrator."



@app.context_processor
def inject_user():  # 函数名可以随意修改
    from app.models import User
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于 return {'user': user}

from app import views, errors, commands