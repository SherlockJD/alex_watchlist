from flask import render_template,request, flash, redirect,url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from watchlist import app,db
from watchlist.models import User,Movie

@app.route('/alex')
def hello():  # 视图函数，输入/alex的网址返回的内容为该函数的返回值
    return "Welcome to Alex's watchlist!"


# 根目录
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":  # 判断是否是POST请求
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        # 获取输入的电影名
        title = request.form.get('title')
        # 获取输入的电影年份
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('输入错误！')  # 弹出错误信息
            return redirect(url_for('index'))  # 重定向至首页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)
        db.session.add(movie)  # 保存至数据库
        db.session.commit()  # 提交数据库更改
        flash('条目创建成功！')
        return redirect(url_for('index'))  # 重定向至首页

    # user = User.query.first()
    movies = Movie.query.all()  # 读取数据库中所有电影记录
    # 调用render_templates()函数，将实际的变量传入index.html（即模板）中的变量
    return render_template('index.html', movies=movies)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('请输入用户名或密码！')
            return redirect(url_for('login'))
        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login successfully!')
            return redirect(url_for('index'))

        flash('用户名或密码错误！')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """用户退出"""
    logout_user()
    flash('再见！')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """用户设置界面"""
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('用户名输入错误！')
            return redirect(url_for('settings'))
        current_user.username = name
        db.session.commit()
        flash('设置已更新！')
        return redirect(url_for('index'))
    return render_template('settings.html')


# 编辑表单函数
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    """编辑表单函数"""
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("输入错误！")
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向至表单编辑页面
        movie.title = title  # 更新电影标题
        movie.year = year  # 更新电影年份
        db.session.commit()
        flash("条目已更新！")
        return redirect(url_for('index'))
    return render_template('edit.html', movie=movie)


# 删除表单
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    """删除表单数据"""
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)
    db.session.commit()
    flash('条目已删除！')
    return redirect(url_for('index'))

@app.route('/song')
def hello_song():
    return '<h1>Hello Song</h1><img src="http://helloflask.com/totoro.gif">'


@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name


@app.route('/test')
def test_url_for():
    """调用端点示例"""
    print(url_for("hello"))
    print(url_for("user_page", name='Alex Song'))
    print(url_for("user_page", name='Masilu'))
    print(url_for("hello_alex"))
    return "test page"