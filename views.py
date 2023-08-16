from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from markupsafe import escape
from models import User, Movie
# from utils import url_for

views = Blueprint(__name__,"views")
# !!!Since you have defined your views using a blueprint, all the endpoint names will be prefixed with the name of the blueprint.

@views.route('/')
def index():
    # user = User.query.first()  # 读取用户记录
    movies = Movie.query.all()  # 读取所有电影记录
    return render_template('index.html', movies=movies)
    # return render_template('index.html', name=name, movies=movies)
# 为了让模板正确渲染，我们还要把模板内部使用的变量(name, movies)通过关键字参数传入这个函数

# #404 错误处理函数 当 404 错误发生时，这个函数会被触发，返回值会作为响应主体返回给客户端
# @views.errorhandler(404)  # 传入要处理的错误代码
# def page_not_found(e):  # 接受异常对象作为参数
#     user = User.query.first()
#     return render_template('404.html', user=user), 404  # 返回模板和状态码

# @app.route('/')
# # @app.route('/index')
# # @app.route('/home')
# # 当用户在浏览器访问这个 URL 的时候，就会触发这个视图函数（view funciton）这里的 /指的是根地址
# def hello():
#     return '<h1>你好 Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

@views.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}'

@views.route('/test')
def test_url_for():
    # 下面是一些调用示例（请访问 http://localhost:5000/test 后在命令行窗口查看输出的 URL）：
    print(url_for('views.index'))  # 生成 hello 视图函数对应的 URL，将会输出：/
    # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
    print(url_for('views.user_page', name='greyli'))  # 输出：/user/greyli
    print(url_for('views.user_page', name='peter'))  # 输出：/user/peter
    print(url_for('views.test_url_for'))  # 输出：/test
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
    print(url_for('views.test_url_for', num=2))  # 输出：/test?num=2
    return 'Test page'