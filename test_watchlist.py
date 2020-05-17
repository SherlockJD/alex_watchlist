# coding = gbk
import unittest

from watchlist import app,db
from watchlist.models import Movie,User
from watchlist.commands import forge,initdb

class WatchlistTestCase(unittest.TestCase):
    """测试类"""

    def setUp(self):
        """固件测试"""
        # 更新固件
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        # 创建数据库和表
        db.create_all()
        # 创建测试数据，一个用户，一个电影条目
        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='Test movie title', year='2020')
        # 使用add_all()方法一次添加多个模型类实例，传入列表
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()  # 创建测试客户端
        self.runner = app.test_cli_runner()  # 创建测试命令运行器

    def tearDown(self):
        db.session.remove()  # 清除数据库会话
        db.drop_all()  # 删除数据库

    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # 测试程序是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def test_404_page(self):
        """测试404页面"""
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)  # 判断响应状态码

    def test_index_page(self):
        """测试主页"""
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('test\'s Watchlist', data)
        self.assertIn('Test movie title', data)
        self.assertEqual(response.status_code, 200)

    def login(self):
        """登录用户"""
        self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

    def test_create_item(self):
        """测试创建条目"""
        self.login()
        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2020'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('条目创建成功', data)
        self.assertIn('New Movie', data)

        # 测试创建条目，但电影标题为空
        response = self.client.post('/', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('条目创建成功！', data)
        self.assertIn('输入错误！', data)

        # 测试创建条目，但电影年份为空
        response = self.client.post('/', data=dict(
            title='New Movie',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('条目创建成功！', data)
        self.assertIn('输入错误！', data)

        # 测试更新条目

    def test_updata_item(self):
        """测试更新条目"""
        self.login()

        # 测试更新页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('编辑条目', data)
        self.assertIn('Test movie title', data)
        self.assertIn('2020', data)

        # 测试更新条目操作
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('条目已更新！', data)
        self.assertIn('New Movie Edited', data)

        # 测试更新条目但电影标题为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('条目已更新！', data)
        self.assertIn('输入错误！', data)

        # 测试更新条目但电影年份为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited again',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertNotIn('New Movie Edited Again', data)
        self.assertIn('输入错误！', data)

    def test_delete_item(self):
        """测试删除条目"""
        self.login()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('条目已删除！', data)
        self.assertNotIn('Test Movie Title', data)

    def test_login_protection(self):
        """测试登录保护"""
        response = self.client.post('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)

    def test_login(self):
        """测试登录"""
        response = self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login successfully!', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)

        # 测试使用错误的密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login successfully!', data)
        self.assertIn('用户名或密码错误！', data)

        # 测试使用错误的用户名登录
        response = self.client.post('/login', data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login successfully!', data)
        self.assertIn('用户名或密码错误！', data)

        # 测试使用空用户名登录
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login successfully!', data)
        self.assertIn('请输入用户名或密码！', data)

        # 测试使用空密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login successfully!', data)
        self.assertIn('请输入用户名或密码！', data)

    def test_logout(self):
        """测试登出"""
        self.login()

        response = self.client.get('/logout', follow_redirects=True)

        data = response.get_data(as_text=True)
        self.assertIn('再见！', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('<form method="post">', data)

    def test_settings(self):
        """测试设置"""
        self.login()

        # 测试设置页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Your name:', data)

        # 测试更新设置
        response = self.client.post('/settings', data=dict(
            name='alex song'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('设置已更新！', data)
        self.assertIn('alex song', data)

        # 测试更新设置，名称为空
        response = self.client.post('/settings', data=dict(
            name=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('设置已更新！', data)
        # self.assertIn('', data)

    def test_forge_command(self):
        """测试虚拟函数"""
        result = self.runner.invoke(forge)
        self.assertIn('Done!', result.output)
        # self.assertNotIn(Movie.query.count(),str(0))

    # 测试初始化数据库
    def test_initdb_command(self):
        """测试初始化数据库"""
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    # 测试生成管理员账户
    def test_admin_command(self):
        """测试生成管理员账户"""
        db.drop_all()

        db.create_all()
        result = self.runner.invoke(args=['admin', '--username',
                                          'alex', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done!', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'alex')
        self.assertTrue(User.query.first().validate_password('123'))

    def test_admin_command_update(self):
        """测试更改管理员"""
        # 使用 args 参数给出完整的命令参数列表
        result = self.runner.invoke(args=['admin', '--username',
                                          'peter', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done!', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'peter')
        self.assertTrue(User.query.first().validate_password('456'))


if __name__ == '__main__':
    unittest.main()
