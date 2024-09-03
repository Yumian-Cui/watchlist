from flask_wtf.csrf import CSRFError
from flask import render_template, redirect, request

from watchlist import app

#Refresh the page when The CSRF token has expired
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return redirect(request.url)

#404 错误处理函数 当 404 错误发生时，这个函数会被触发，返回值会作为响应主体返回给客户端
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    # user = User.query.first()
    return render_template('errors/404.html'), 404  # 返回模板和状态码

#400 错误处理函数 当 400 错误发生时，这个函数会被触发，返回值会作为响应主体返回给客户端
@app.errorhandler(400)  # 传入要处理的错误代码
def bad_request(e):  # 接受异常对象作为参数
    # user = User.query.first()
    return render_template('errors/400.html'), 400  # 返回模板和状态码

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(405)
def internal_server_error(e):
    return render_template('errors/405.html'), 405