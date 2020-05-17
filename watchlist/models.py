from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from watchlist import db

class User(db.Model, UserMixin):  # 数据库表，表名为user
    id = db.Column(db.Integer, primary_key=True)  # 主键，个人理解应该是序号
    name = db.Column(db.String(20))  # 名字
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):
        """用来生成密码的散列值"""
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """验证输入密码与散列值是否一致"""
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键，个人理解应该是序号
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份