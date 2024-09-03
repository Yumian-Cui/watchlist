from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app import db


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

class EmailConfirmationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    token = db.Column(db.String(100))
    used = db.Column(db.Boolean, default=False)
    

class Movie(db.Model):  # 模型类是Movie, 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份
    review = db.Column(db.Text, nullable=True)  # Add this line
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #将 User 表和 Movie 表建立关联 added a user_id column to the Movie table, which is a foreign key that references the id column in the User table
    board_id = db.Column(db.Integer, db.ForeignKey('board.id')) # will be a foreign key referencing the Board model's id
    # reviews = db.relationship('Review', back_populates='movie', lazy='dynamic', cascade='all, delete-orphan')

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movies = db.relationship('Movie', backref='board', lazy='dynamic') # one-to-many, one board can have multiple movies

# class Review(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.Text, nullable=False)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))

#     movie = db.relationship('Movie', back_populates='reviews')    



