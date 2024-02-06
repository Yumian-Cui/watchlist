import unittest
from flask import url_for
from app import app, db, User, Movie, EmailConfirmationToken  # Import your Flask application and models here

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
        user = User(name='Test', username='test')
        user.set_password('123')
        db.session.add(user) # commit user first, otherwise id would be None if not committing it to db first
        db.session.commit()
        movie = Movie(title='Test Movie Title', year='2019', user_id=user.id)
        db.session.add(movie)
        db.session.commit()
        # 使用 add_all() 方法一次添加多个模型类实例，传入列表
        # db.session.add_all([user, movie])
        # db.session.commit()

        self.client = app.test_client()  # 创建测试客户端 用来模拟客户端请求
        self.runner = app.test_cli_runner()  # 创建测试命令运行器 用来触发自定义命令


    def tearDown(self):
        db.session.close()
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

    # 测试主页, not logged in
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Unknown\'s Watchlist', data)
        self.assertIn('Hello! Please log in to access your watchlist.', data)
        self.assertEqual(response.status_code, 200)

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
        # self.assertNotIn('New Movie Edited Again', data) TODO
        # self.assertIn('Invalid input.', data)

    # 测试删除条目
    def test_delete_item(self):
        self.login()

        response = self.client.post('/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie Title', data)

    

    # def test_index(self):
    #     # with self.app.test_request_context():
    #     response = self.client.get(url_for('index'))
    #     self.assertEqual(response.status_code, 200)

    # def test_login(self):
    #     # with self.app.test_request_context():
    #     user = User(username='test', email='test@example.com')
    #     user.set_password('testpassword')
    #     db.session.add(user)
    #     db.session.commit()

    #     # uses the test client to make a POST request to the login route, passing in the username and password as form data
    #     response = self.client.post(url_for('login'), data=dict(
    #         identifier='test',
    #         password='testpassword'
    #     ), follow_redirects=True)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Login success.', response.data)

    # Add more tests as needed

if __name__ == '__main__':
    unittest.main()
