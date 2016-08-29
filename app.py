from flask import Flask, request, render_template, session, redirect, url_for, flash
import DBC

app = Flask(__name__)
dbc = DBC.DBC()

@app.route('/')
def index():
    recent = dbc.getRecent()
    post = dbc.getArticles()

    admin = False
    if 'admin' in session:
        admin = True
    return render_template('index.html', recent=recent, post=post, admin=admin)

@app.route('/a/<int:pid>/')
def article(pid):
    post = dbc.getArticle(pid)[0]
    comments = dbc.getComments(pid)
    return render_template('article.html', title=post['title'], entry=post['entry'], comments=comments)

@app.route('/new/')
def new():
    if 'admin' in session:
        return render_template('newarticle.html')
    else:
        flash('You need to login before post an Article')
        return redirect(url_for('login'))

@app.route('/new/post/', methods=['POST'])
def postArticle():
    title = request.form['title']
    body = request.form['body']
    dbc.post(title, body)
    return 'Article Posted'

@app.route('/edit/')
def edit():
    data = dbc.getArticles()
    return render_template('editarticles.html', data=data)

@app.route('/edit/<int:pid>/')
def editArticle(pid):
    if 'admin' in session:
        data = dbc.getArticle(pid)
        if data:
            return render_template('edit.html', data=data[0])
        else:
            flash('Invalid article index')
            return redirect(url_for('index'))
    else:
        flash('You need to login before edit an Article')
        return redirect(url_for('login'))

@app.route('/edit/<int:pid>/post/', methods=['POST'])
def update(pid):
    title = request.form['title']
    entry = request.form['entry']
    dbc.updateArticle(pid, title, entry)
    flash('Article updated successfully')
    return 'ok'

@app.route('/edit/del/<int:pid>/')
def delete(pid):
    dbc.deleteArticle(pid)
    flash('Article deleted successfully')
    return redirect(url_for('edit'))

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/login/auth/', methods=['POST'])
def auth():
    username = request.form['username']
    password = request.form['password']

    if dbc.auth(username, password):
        session['admin'] = 'ok'
        flash('Successfully loged in')
        return 'Ok'
    else:
        flash('Invalid login')
        return 'login'

@app.route('/logout/')
def logout():
    if 'admin' in session:
        session.pop('admin', None)
    flash('Successfully loged out')
    return redirect(url_for('index'))

@app.route('/feedback/')
def feedback():
    return render_template('feedback.html')

@app.route('/feedback/submit/', methods=['POST'])
def submitFeedback():
    name = request.form['name']
    email = request.form['email']
    feedback = request.form['feedback']

    dbc.addFeedback(name, email, feedback)
    flash('Thank you for your valuble feedback')
    return 'Ok'

@app.route('/feedback/view/')
def viewFeedbacks():
    result = dbc.getFeedbacks()
    return render_template('viewfeedback.html', feedbacks=result)

@app.route('/comment/<int:pid>/')
def addComment(pid):
    article = dbc.getArticle(pid)
    data = {'title': article[0]['title'], 'entry':article[0]['entry'][:200]}
    return render_template('comment.html', data=data)

@app.route('/comment/<int:pid>/post/', methods=['POST'])
def postComment(pid):
    name = request.form['name']
    comment = request.form['comment']
    dbc.addComment(pid, name, comment)
    flash('Comment posted successfully')
    return 'ok'

@app.route('/comment/view/<int:pid>/')
def viewComments(pid):
    article = dbc.getArticle(pid)
    comments = dbc.getComments(pid, limited=False)
    data = {'title': article[0]['title'], 'entry':article[0]['entry'][:200]}
    return render_template('viewcomment.html', data=data, comments=comments)

app.secret_key = "\x8a\xe1$O\x96\xd2y\xcbp\xfc\x8e(F|3\xb9\xae\x83\xdd\xd2\r4yF"
