import mysql.connector

class DBC:
    def __init__(self):
        pass

    def connect(self):
        self.con = mysql.connector.connect(host='localhost', user='root', password='123', database='blog')
        self.cur = self.con.cursor(buffered=True)

    def close(self):
        self.cur.close()
        self.con.close()

    def get(self, sql):
        self.connect()
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.close()
        return result

    def add(self, sql):
        self.connect()
        self.cur.execute(sql)
        self.con.commit()
        self.close()

    def updateHits(self, pid, isNew=False):
        if isNew:
            sql = "INSERT INTO hits VALUES(%s, default)" % pid
        else:
            sql = "UPDATE hits SET hits = hits + 1 WHERE pid = %s" % pid
        self.add(sql)

    def getRecent(self):
        sql = "SELECT post.pid, title FROM post, hits where post.pid = hits.pid ORDER BY hits.hits DESC LIMIT 10"
        ret = self.get(sql)
        result = [dict(pid=row[0], title=row[1]) for row in ret]
        return result

    def getArticles(self):
        sql = 'SELECT pid, title, entry, (SELECT COUNT(comment) FROM comment WHERE pid=post.pid) AS cc, (SELECT hits FROM hits WHERE pid=post.pid) AS hits FROM post ORDER BY pid DESC LIMIT 10'
        ret = self.get(sql)
        result = [dict(pid=row[0], title=row[1], entry=row[2][:200], cc=row[3], hits=row[4]) for row in ret]
        return result

    def getArticle(self, pid):
        sql = "SELECT title, entry FROM post WHERE pid = '%s'" % pid
        ret = self.get(sql)
        result = [dict(title=row[0], entry=row[1]) for row in ret]
        self.updateHits(pid)
        return result

    def updateArticle(self, pid, title, entry):
        sql = "UPDATE post set title='%s', entry='%s' WHERE pid = '%s'" %(title, entry, pid)
        self.add(sql)

    def deleteArticle(self, pid):
        sql1 = "DELETE FROM hits where pid = '%s'" %pid
        sql2 = "DELETE FROM post where pid = '%s'" %pid
        self.add(sql1)
        self.add(sql2)

    def post(self, title, body):
        sql1 = "INSERT INTO post VALUES(default, '%s', '%s')" %(title, body)
        sql2 = "INSERT INTO hits VALUES( (SELECT pid FROM post ORDER BY pid DESC LIMIT 1), default)"
        self.add(sql1)
        self.add(sql2)

    def auth(self, username, password):
        sql = "SELECT COUNT(username) FROM auth WHERE username='%s' AND password=md5('%s')" %(username, password)
        ret = self.get(sql)
        result = ret[0][0]
        if result == 1:
            return True
        else:
            return False

    def addComment(self, pid, name, comment):
        sql = "INSERT INTO comment VALUES(default, %s, '%s', '%s')" %(pid, name, comment)
        self.add(sql)

    def getComments(self, pid, limited=True):
        if limited:
            sql = "SELECT name, comment FROM comment where pid = %s ORDER BY id DESC LIMIT 20" %pid
        else:
            sql = "SELECT name, comment FROM comment where pid = %s ORDER BY id DESC" %pid

        result = [dict(name=row[0], comment=row[1]) for row in self.get(sql)]
        return result

    def getCommentCount(self, pid):
        sql = "SELECT COUNT(*) FROM comment where pid=%s" %pid
        result = self.get(sql)[0][0]
        return result

    def addFeedback(self, name, email, feedback):
        sql = "INSERT INTO feedback VALUES(default, '%s', '%s', '%s')" %(name, email, feedback)
        self.add(sql)

    def getFeedbacks(self):
        sql = "SELECT name, email, feedback FROM feedback ORDER BY id DESC LIMIT 20"
        ret = self.get(sql)
        result = [dict(name=row[0], email=row[1], feedback=row[2]) for row in ret]
        return result
