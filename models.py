# DEPRECATED FILE

# from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
# # from app import app

# db = SQLAlchemy()  # 初始化扩展，传入程序实例 app

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

# # #编写一个自定义命令来自动执行创建数据库表操作
# # import click
# # @app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
# # @click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
# # def initdb(drop):
# #     """Initialize the database."""
# #     if drop:  # 判断是否输入了选项
# #         db.drop_all()
# #     db.create_all()
# #     click.echo('Initialized database.')  # 输出提示信息
# # #如果你想在不破坏数据库内的数据的前提下变更表的结构，需要使用数据库迁移工具，比如集成了 Alembic 的 Flask-Migrate(https://github.com/miguelgrinberg/Flask-Migrate) 扩展

# # #执行 flask forge 命令就会把所有虚拟数据添加到数据库里
# # @app.cli.command()
# # def forge():
# #     """Generate fake data."""
# #     db.create_all()

# #     # 全局的两个变量移动到这个函数内
# #     name = 'Lumi'
# #     movies = [
# #         {'title': 'My Neighbor Totoro', 'year': '1988'},
# #         {'title': 'Dead Poets Society', 'year': '1989'},
# #         {'title': 'A Perfect World', 'year': '1993'},
# #         {'title': 'Leon', 'year': '1994'},
# #         {'title': 'Mahjong', 'year': '1996'},
# #         {'title': 'Swallowtail Butterfly', 'year': '1996'},
# #         {'title': 'King of Comedy', 'year': '1999'},
# #         {'title': 'Devils on the Doorstep', 'year': '1999'},
# #         {'title': 'WALL-E', 'year': '2008'},
# #         {'title': 'The Pork of Music', 'year': '2012'},
# #     ]

# #     user = User(name=name)
# #     db.session.add(user)
# #     for m in movies:
# #         movie = Movie(title=m['title'], year=m['year'])
# #         movie.user_id = user.id
# #         db.session.add(movie)

# #     db.session.commit()
# #     click.echo('Done.')