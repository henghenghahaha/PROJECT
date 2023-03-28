import config, threading, ast
import json
import pymysql
from flask import Flask, render_template, request, Response, make_response, jsonify
from flask_cors import CORS, cross_origin
from dbutils.pooled_db import PooledDB
from dbutils.persistent_db import PersistentDB

app = Flask(__name__, static_folder='', static_url_path='', template_folder='')
CORS(app, resources=r'/*')
app.config.from_object(config)


class MysqlHelper(object):
    conn = None

    def __init__(self, host, username, password, db=None, charset='utf8', port=3306):
        self.__pool = PooledDB(creator=pymysql,
                               mincached=10,
                               maxcached=0,
                               maxshared=20,
                               maxconnections=200,
                               maxusage=20,
                               blocking=True,
                               user=username,
                               passwd=password,
                               db=db,
                               host=host,
                               port=port)

    def connect(self):
        conn = self.__pool.connection()
        cursor = conn.cursor()
        # print("连接成功")
        return conn, cursor

    def close(self):
        conn, cursor = self.connect()
        cursor.close()
        conn.close()

    def get_one(self, sql, params=()):
        result = None
        title = []
        try:
            conn, cursor = self.connect()
            cursor.execute(sql, params)
            result = cursor.fetchone()
            des = cursor.description
            title = [item[0] for item in des]
            self.close()
        except Exception as e:
            print(e)
        return list(title), result

    def get_all(self, sql, params=()):
        list_data = ()
        title = []
        try:
            conn, cursor = self.connect()
            cursor.execute(sql, params)
            list_data = cursor.fetchall()
            des = cursor.description
            title = [item[0] for item in des]
            self.close()
        except Exception as e:
            print(e)
        return title, list_data

    def insert(self, sql, params=()):
        return self.__edit(sql, params)

    def update(self, sql, params=()):
        return self.__edit(sql, params)

    def delete(self, sql, params=()):
        return self.__edit(sql, params)

    def __edit(self, sql, params):
        count = 0
        try:
            conn, cursor = self.connect()
            count = cursor.execute(sql, params)
            conn.commit()
            self.close()
        except Exception as e:
            print(e)
        return count


mysql = MysqlHelper(
    host='127.0.0.1',  # MySQL服务端的IP地址
    port=3306,  # MySQL默认PORT地址(端口号)
    username='root',  # 用户名
    password='nzh278799',  # 密码,也可以简写为passwd
    db='project',  # 库名称,也可以简写为db
    charset='utf8'  # 字符编码
)
mysql.connect()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('templates/001_Home/index.html')


@app.route('/degree/', methods=['GET', 'POST'])
def set_result():
    # print(request)
    if request.method == 'POST':
        # result = request.form
        result = json.loads(request.get_data())
        # print(result)
        sql1 = """SELECT * FROM users WHERE users.ID = '{}'""".format(result['passport']) + """;"""
        _, tmp = mysql.get_all(sql1)
        sql2 = """SELECT * FROM course WHERE course.ID = '{}'""".format(result['passport']) + """;"""
        _, res = mysql.get_all(sql2)
        print(res,'&&&&&&&++++++')
        dict = {

        }
        academicyear = []
        for i in res:
            if i[2] not in academicyear:
                academicyear.append(i[2])
        for n in academicyear:
            dict.setdefault(n, [])
        for m in res:
            dict1 = {
                'courseNum': m[3],
                'courseName': m[4],
                'score': m[5],
                'GPA': m[6],
                'courseLength': m[7],
                'statement':m[8],
            }
            if m[2] in dict:
                dict.get(m[2]).append(dict1)
        print(dict,'567576567565765756567575')
        if len(tmp) > 0:
            result = {
                'ID': tmp[0][0],
                'name': tmp[0][1],
                'gender': tmp[0][2],
                'DateOfBirth': tmp[0][3],
                'Nationality': tmp[0][4],
                'Registration': tmp[0][5],
                'Major': tmp[0][6],
                'Degree': tmp[0][7],
                'GPA': tmp[0][8],
                'DateOfAttendance': tmp[0][9],
                'DateOfGraduation': tmp[0][10],
                'image': tmp[0][11],
                'totalCre': tmp[0][13],

            }
            return render_template("/static/007_request/index.html", result=result, course=dict, data='查询成功')
        else:
            return render_template('/static/error/index.html', result=None)
    return render_template('/static/006_degree/index.html', result=None)


@app.route('/update/', methods=['GET', 'POST'])
def updata():
    req = json.loads(request.get_json().get('data'))

    data = []
    course = []
    for i in req.get('course'):
        course.append(req.get('passport'))
        course.append(i.get('Academic_Year'))
        for n in i.get('addInputArr'):
            course.append(n.get('value1'))
            course.append(n.get('value2'))
            course.append(n.get('value3'))
            course.append(n.get('value4'))
            course.append(n.get('value5'))
            course.append(i.get('statement'))
            data.append(tuple(course))
            course.pop()
            course.pop()
            course.pop()
            course.pop()
            course.pop()
            course.pop()
        course = []

    sql1 = """INSERT INTO `project`.`users` (`ID`, `name`, `Gender`, `date_of_birth`, `nationality`, `Registration_Number`, 
    `major`, `degree`, `GPA`, `DateOfAttendance`, `DateOfGraduation`, `image`, `courseStr`,`totalCre`) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    sql2 = """INSERT INTO `project`.`course` (`ID`, `academicYear`, `courseNum`, `courseName`, `score`, `gpa`, `courselength`, `statement`) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""

    sql3 = """DELETE  FROM users WHERE users.ID = '{}'""".format(req.get('passport')) + """;"""
    sql4 = """DELETE  FROM course WHERE course.ID = '{}'""".format(req.get('passport')) + """;"""

    try:
        mysql.delete(sql3)
        mysql.delete(sql4)
    except Exception as e:
        print(e, 'delete')
    try:
        mysql.insert(sql1, params=(req.get('passport'), req.get('name'), req.get('gender'), req.get('DateOfBirth'),
                                   req.get('nationality'), req.get('Registration_Number'), req.get('Major'),
                                   req.get('Degree_awarded'), req.get('GpA'), req.get('DateOfAttendence'),
                                   req.get('DateOfGraduation'), req.get('img'), str(req.get('course')), req.get('totalCre')))

        for i in range(len(data)):
            mysql.insert(sql2, params=data[i])
    except Exception as e:
        # print(e, 'insert')
        return jsonify(info='上传失败')
    return jsonify(info='上传成功')


@app.route('/alter/', methods=['GET', 'POST'])
def alter():
    if request.method == 'POST':
        req = json.loads(request.get_json().get('data'))
        sql1 = """SELECT * FROM users WHERE users.ID = '{}'""".format(req['_value']) + """;"""
        _, tmp = mysql.get_all(sql1)
        if len(tmp) > 0:
            result = {
                'ID': tmp[0][0],
                'name': tmp[0][1],
                'gender': tmp[0][2],
                'DateOfBirth': tmp[0][3],
                'Nationality': tmp[0][4],
                'Registration': tmp[0][5],
                'Major': tmp[0][6],
                'Degree': tmp[0][7],
                'GPA': tmp[0][8],
                'DateOfAttendance': tmp[0][9],
                'DateOfGraduation': tmp[0][10],
                'image': tmp[0][11],
                'totalCre': tmp[0][13],

            }
            if len(tmp[0][12]) == 2:
                # print('78789798798789')
                return jsonify(info='该学生无课程信息', result=result, course={'key':'not'})
            else:
                return jsonify(info='查询成功', result=result, course=ast.literal_eval(tmp[0][12]))
        else:
            return jsonify(info='抱歉未查询到')
    return jsonify(info='抱歉未查询到')


@app.route('/changeInfo/', methods=['GET', 'POST'])
def changeInfo():
    # print(request.form.to_dict().get('data'))
    # print(request.get_json().get('data'))
    req = json.loads(request.get_json().get('data'))

    # print(req)
    # print(req.get('name'), req.get('DateOfGraduation'))
    # print('--------------------------------')
    # print(req.get('course'))

    data = []
    course = []
    for i in req.get('course'):
        course.append(req.get('passport'))
        course.append(i.get('Academic_Year'))
        for n in i.get('addInputArr'):
            course.append(n.get('value1'))
            course.append(n.get('value2'))
            course.append(n.get('value3'))
            course.append(n.get('value4'))
            course.append(n.get('value5'))
            course.append(i.get('statement'))
            data.append(tuple(course))
            course.pop()
            course.pop()
            course.pop()
            course.pop()
            course.pop()
            course.pop()
        course = []

    sql1 = """INSERT INTO `project`.`users` (`ID`, `name`, `Gender`, `date_of_birth`, `nationality`, `Registration_Number`, 
    `major`, `degree`, `GPA`, `DateOfAttendance`, `DateOfGraduation`, `image`, `courseStr`,`totalCre`) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    sql2 = """INSERT INTO `project`.`course` (`ID`, `academicYear`, `courseNum`, `courseName`, `score`, `gpa`, `courselength`, `statement`) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
    sql3 = """DELETE  FROM users WHERE users.ID = '{}'""".format(req.get('passport')) + """;"""
    sql4 = """DELETE  FROM course WHERE course.ID = '{}'""".format(req.get('passport')) + """;"""

    try:
        mysql.delete(sql3)
        mysql.delete(sql4)
    except Exception as e:
        print(e, 'delete')
    try:
        mysql.insert(sql1, params=(req.get('passport'), req.get('name'), req.get('gender'), req.get('DateOfBirth'),
                                   req.get('nationality'), req.get('Registration_Number'), req.get('Major'),
                                   req.get('Degree_awarded'), req.get('GpA'), req.get('DateOfAttendence'),
                                   req.get('DateOfGraduation'), req.get('img'), str(req.get('course')), req.get('totalCre')))

        for i in range(len(data)):
            mysql.insert(sql2, params=data[i])
    except Exception as e:
        # print(e, 'insert')
        return jsonify(info='修改失败')
    return jsonify(info='修改成功')


@app.route('/querylog/', methods=['GET', 'POST'])
def querylog():
    sql1 = """SELECT * FROM addAndalterlog;"""
    try:
        _, req = mysql.get_all(sql1)
        req1 = []
        for i in req:
            req1.append({
                "ID": i[1],
                "admin": i[2],
                "ADDTime": i[3],
                "Type": i[4]
            })
        # print(req1,'zzzzzzzzzzzz')
        return jsonify(result=req1)
    except Exception as e:
        # print(e, 'insert')
        return jsonify(info='修改失败')


@app.route('/addlog/', methods=['GET', 'POST'])
def addlog():
    req = json.loads(request.get_json().get('data'))
    # print(req)

    sql1 = """INSERT INTO `project`.`addandalterlog` (`ID`, `admin`, `ADDTime`, `Type`)
    VALUES (%s, %s, %s, %s);"""

    try:
        mysql.insert(sql1, params=(req.get('ID'), req.get('admin'), req.get('ADDTime'), req.get('Type')))
    except Exception as e:
        # print(e, 'addlog')
        return jsonify(info='添加失败')
    return jsonify(info='添加成功')

@app.route('/modifylog/', methods=['GET', 'POST'])
def changelog():
    req = json.loads(request.get_json().get('data'))
    # print(req)

    sql1 = """INSERT INTO `project`.`addandalterlog` (`ID`, `admin`, `ADDTime`, `Type`)
    VALUES (%s, %s, %s, %s);"""

    try:
        mysql.insert(sql1, params=(req.get('ID'), req.get('admin'), req.get('ADDTime'), req.get('Type')))
    except Exception as e:
        # print(e, 'addlog')
        return jsonify(info='添加失败')
    return jsonify(info='添加成功')



if __name__ == '__main__':
    app.run()
