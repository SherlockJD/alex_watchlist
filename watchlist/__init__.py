# coding = gbk
from flask import Flask

from flask_login import LoginManager
# 导入操作数据库的库
from flask_sqlalchemy import SQLAlchemy
import os
import sys

from datetime import timedelta

# 判断程序运行的系统是否为Windows
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

# 创建web框架实例
app = Flask(__name__)
# 配置变量，告诉SQLAlchemy数据库连接地址
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 设置静态文件缓存过期时间，避免修改css文件网页未更新，如果此方法不生效，使用ctrl+F5刷新页面
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
# 设置缓存签名
app.config['SECRET_KEY'] = 'dev'
# 初始化扩展，传入程序实例app
db = SQLAlchemy(app)

login_manager = LoginManager(app)  # 实例化扩展类

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """创建用户加载回调函数，接受用户id作为参数"""
    from watchlist.models import User
    user = User.query.get(int(user_id))
    return user

@app.context_processor  # 装饰器
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)  # 将user信息传入字典

from watchlist import views,errors,commands

