import config, threading, ast
import json

import pandas as pd
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


@app.route('/execl/', methods=['GET', 'POST'])
def Execl():
    file = request.files['file']
    print(file)
    execl = pd.read_excel(file, header=0)
    basedata = execl.iloc[1]
    courseData = execl.iloc[5:-2]

    def yearEnter(datestr):
        strlist = datestr.split('--')
        dataStart = strlist[0].split('/')
        return dataStart[2]

    def dateconvert1(datestr):
        dateDict = {
            'JAN': '01',
            'FEB': '02',
            'MAR': '03',
            'APR': '04',
            'MAY': '05',
            'JUN': '06',
            'JUL': '07',
            'AUG': '08',
            'SEP': '09',
            'OCT': '10',
            'NOV': '11',
            'DEC': '12'
        }
        strlist = datestr.split('-')
        return strlist[2] + '-' + dateDict.get(strlist[1]) + '-' + strlist[0]

    def dateconvert2(datestr):
        strlist = datestr.split('--')
        dataStart = strlist[0].split('/')
        dataEnd = strlist[1].split('/')
        dataStart = dataStart[2] + '-' + dataStart[0] + '-' + dataStart[1]
        dataEnd = dataEnd[2] + '-' + dataEnd[0] + '-' + dataEnd[1]
        return dataStart, dataEnd

    dateStart, dateEnd = dateconvert2(basedata[9])

    imgStr = 'data:image/webp;base64,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'

    YearEnter = yearEnter(basedata[9])
    listCourse = []
    Yeardict = {'Academic_Year': '',
                'addInputArr': [],
                'key': '', 'labelPosition': 'right', 'prop': '',
                'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance',
                'value': ''}
    Yearlist = []
    for index, row in courseData.iterrows():
        addinputarrdict = {'key': '', 'labelPosition': 'right', 'prop': '', 'value1': str(row[2]),
                           'value2': str(row[3]), 'value3': str(row[4]), 'value4': str(row[5]), 'value5': str(row[6])}
        Yearacademic = str(int(row[0]) - 1 + int(YearEnter)) + str('    ') + row[1] + str(' ') + 'Semester'
        if len(Yearlist) == 0 or Yearlist[-1] != Yearacademic:
            if len(Yeardict.get('addInputArr')) > 0:
                listCourse.append(Yeardict)
                Yearlist.append(Yearacademic)
            Yeardict = {'Academic_Year': '',
                        'addInputArr': [],
                        'key': '', 'labelPosition': 'right', 'prop': '',
                        'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance',
                        'value': ''}
            Yearlist.append(Yearacademic)
            Yeardict['Academic_Year'] = Yearacademic
            Yeardict.get('addInputArr').append(addinputarrdict)
        elif Yearlist[-1] == Yearacademic:
            Yeardict.get('addInputArr').append(addinputarrdict)
            if (index - 5 + 1) == len(courseData):
                listCourse.append(Yeardict)
                Yearlist.append(Yearacademic)

    dict1 = {'name': basedata[1], 'passport': str(basedata[5]), 'gender': basedata[2], 'nationality': basedata[4],
            'DateOfBirth': dateconvert1(basedata[3]),
            'Registration_Number': str(basedata[6]), 'Degree_awarded': basedata[8], 'Major': basedata[7],
            'GpA': str(basedata[10]),
            'DateOfAttendence': dateStart, 'DateOfGraduation': dateEnd,
            'img': imgStr,
            'course': listCourse,
            'totalCre': str(basedata[11])}

    req = dict1
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
        return jsonify(id=req.get('passport'), info='execl上传失败')
    return jsonify(id=req.get('passport'), info='execl上传成功')

if __name__ == '__main__':
    app.run()
