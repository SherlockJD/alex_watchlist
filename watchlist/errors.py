from flask import render_template

from watchlist import app

@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):
    # user = User.query.first()
    return render_template('errors/404.html'), 404