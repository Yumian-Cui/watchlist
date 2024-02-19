import unittest
from flask import url_for
from flask_login import current_user
from app import app, db, User, Movie, EmailConfirmationToken, forge, initdb  # Import your Flask application and models here

# app_context: application's environment, needed interact with the application setup or configuration, but no request is in progress
# test_request_context: 

# Test mostly user interactions with watchlist
# Here won't get into details pertaining email authentication
class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        # 更新配置
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            # SQLALCHEMY_DATABASE_URI='sqlite:///test.db',
            WTF_CSRF_ENABLED = False
        )
        # self.app = app # a reference to your Flask application instance
        # self.client = self.app.test_client() # use to make requests to your application in your tests
        # self.app.config['TESTING'] = True
        # self.app.config['WTF_CSRF_ENABLED'] = False # disable CSRF protection in testing environments
        # self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.context = app.test_request_context()
        self.context.push()
        db.create_all() # 创建数据库和表
        # 创建测试数据，一个用户，一个电影条目
        user = User(name='Test', username='test', email='test@example.com')
        user.set_password('123')
        db.session.add(user) # commit user first, otherwise id would be None if not committing it to db first
        db.session.commit()
        movie = Movie(title='Test Movie Title', year='2019', user_id=user.id)
        db.session.add(movie)
        db.session.commit()
        #创建用户2用于测试duplicate
        user2 = User(name='Test2', username='test_duplicate', email='test2@example.com')
        user2.set_password('1234')
        db.session.add(user2)
        db.session.commit()
        # 使用 add_all() 方法一次添加多个模型类实例，传入列表
        # db.session.add_all([user, movie])
        # db.session.commit()

        self.client = app.test_client()  # 创建测试客户端 用来模拟客户端请求
        self.runner = app.test_cli_runner()  # 创建测试命令运行器 用来触发自定义命令


    def tearDown(self):
        # db.session.close()
        db.session.remove() # 清除数据库会话
        db.drop_all() # 删除数据库表
        self.context.pop()

    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # 测试程序是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    # 测试 404 页面
    def test_404_page(self):
        response = self.client.get('/nothing')  # 传入目标 URL
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)  # 判断响应状态码

    # 辅助方法，用于登入用户
    def login(self):
        response = self.client.post('/login', data=dict(
            identifier='test',
            password='123'
        ), follow_redirects=True)
        return response

    def test_index_page_after_login(self):
        response = self.login()
        self.assertIn(b'Login success.', response.data) # flash message is in post request
        response = self.client.get('/') #flash messages are stored in the session and are only available in the next request after they are flashed
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)

    # 测试创建条目
    def test_create_item(self):
        self.login()

        # 测试创建条目操作
        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)
        self.assertIn('New Movie', data)

        # 测试创建条目操作，但电影标题为空
        response = self.client.post('/', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        # self.assertIn('Invalid input.', data)

        # 测试创建条目操作，但电影年份为空
        response = self.client.post('/', data=dict(
            title='New Movie',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        # self.assertIn('Invalid input.', data)

    # 测试更新条目
    def test_update_item(self):
        self.login()

        # 测试更新页面
        response = self.client.get('/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Test Movie Title', data)
        self.assertIn('2019', data)

        # 测试更新条目操作
        response = self.client.post('/edit/1', data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.', data)
        self.assertIn('New Movie Edited', data)

        # 测试更新条目操作，但电影标题为空
        response = self.client.post('/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('This field is required.', data)
        self.assertNotIn('Item updated.', data)
        # self.assertIn('Invalid input.', data)

        # 测试更新条目操作，但电影年份为空
        response = self.client.post('/edit/1', data=dict(
            title='New Movie Edited Again',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        # print(form.errors)
        self.assertNotIn('Item updated.', data)
        self.assertIn('This field is required.', data)
        # In tutorial's logic, if title or year is empty, then it will redirect to index page, flashing "Invalid input."
        # In my case, I used flask_wtf and wtforms to regulate all these, so there won't be redirects
        # self.assertNotIn('New Movie Edited Again', data) # comment out b/c does not apply
        # self.assertIn('Invalid input.', data)

    # 测试删除条目
    def test_delete_item(self):
        self.login()

        response = self.client.post('/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie Title', data)

    # 测试登录保护
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
        self.assertIn('Unknown\'s Watchlist', data)
        self.assertIn('Hello! Please log in to access your watchlist.', data)
        self.assertEqual(response.status_code, 200)

    # 测试登录
    def test_login(self):
        # 测试使用用户名登录
        response = self.client.post('/login', data=dict(
            identifier='test',
            password='123', 
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)

        # 测试使用邮箱登录 
        response = self.client.post('/login', data=dict(
            identifier='test@example.com',
            password='123', 
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)

        # 测试使用错误的密码登录
        response = self.client.post('/login', data=dict(
            identifier='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username/email or password.', data)

        # 测试使用错误的用户名登录
        response = self.client.post('/login', data=dict(
            identifier='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('User does not exist.', data)

        # 测试使用空用户名登录
        response = self.client.post('/login', data=dict(
            identifier='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        # self.assertIn('Invalid input.', data)

        # 测试使用空密码登录
        response = self.client.post('/login', data=dict(
            identifier='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        # self.assertIn('Invalid input.', data)

    # 测试登出
    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye.', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('<form method="post">', data)

    # 测试设置
    def test_settings(self):
        self.login()

        # 测试设置页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Name', data)
        self.assertIn('Username', data)
        self.assertIn('Email', data)
        self.assertIn('Delete your account (irreversible):', data)

        # Check if the appropriate message is displayed based on email confirmation status
        if current_user.email_confirmed:
            self.assertNotIn('Email not confirmed.', data)
        else:
            self.assertIn('Email not confirmed.', data)

        # 测试更新Name设置，名称为空
        response = self.client.post('/settings', data=dict(
            name='',
            username='test',
            email='test@example.com'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated', data)
        # self.assertIn('Please fill out this field.', data) #only exist in brower setting
        
        # 测试更新Name设置
        response = self.client.post('/settings', data=dict(
            name='Grey Li',
            username='test',
            email='test@example.com'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated: name.', data)
        self.assertIn('Grey Li', data)

        # 测试更新用户名，用户名和旧用户名一样
        response = self.client.post('/settings', data=dict(
            name='Test',
            username='test',
            email='test@example.com'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated: username.', data)
        self.assertIn('test', data)

        # 测试更新用户名，用户名唯一
        response = self.client.post('/settings', data=dict(
            name='Test',
            username='test_unique',
            email='test@example.com'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated: username.', data)
        self.assertIn('test_unique', data)

        # 测试更新用户名，用户名不唯一
        response = self.client.post('/settings', data=dict(
            name='Test',
            username='test_duplicate',
            email='test@example.com'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated: username.', data)
        self.assertIn('Username already exists.', data)
        # self.assertNotIn('test_duplicate', data)

        # 邮箱就不测试了，test环境比较复杂

    # 测试虚拟数据
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done.', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    # 测试初始化数据库
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    # 测试生成管理员账户
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username', 'grey', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'grey')
        self.assertTrue(User.query.first().validate_password('123'))

    # 测试更新管理员账户
    def test_admin_command_update(self):
        # 使用 args 参数给出完整的命令参数列表
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username', 'grey', '--password', '123'])
        result = self.runner.invoke(args=['admin', '--username', 'peter', '--password', '456'])
        # # Print all users
        # users = User.query.all()
        # for user in users:
        #     print(f'Username: {user.username}, Email: {user.email}')
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'peter')
        self.assertTrue(User.query.first().validate_password('456'))

    # 测试注册
        



# If user registered with a wrong email account, how to design the system to better remind them?

    

if __name__ == '__main__':
    unittest.main()
