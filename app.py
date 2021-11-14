from flask import Flask, render_template
import sqlite3 
from sqlite3.dbapi2 import Cursor
import re # 정규식

app = Flask(__name__, static_url_path="/static") 

DATABASE = '/Database/prom.db'


# 콤마처리 공통함수 
def comma_machine(n):    
    strN = str(n) #문자화
    lenN = len(strN) #문자길이
    len_c = (lenN//3)*3 # 3의 배수단위로 개수구함
    str_list = []
    i = len_c
    str_list.append(strN[0:-(len_c)]) # 처음은 따로넣음 12000의 경우 '12'부분
    while i > 3 :
        str_list.append(strN[-(i):-(i-3)]) #3의배수 단위로 넣어줌
        i -= 3
    str_list.append(strN[-3::]) #끝은 따로 넣음
    a= ','        
    return a.join(str_list).strip(',')


@app.route('/') # 접속할 URL 
def bootstrap():
    res = [0, 0, 0, 0]
    return render_template('index.html', res=res) # 예제 템플릿



@app.route('/promanaly')
def hello():
    db = sqlite3.connect(DATABASE) 
    cursor = db.cursor()
    sql_read = "SELECT SUM(APL_AMT), SUM(SELLPRC), (SUM(SELLPRC)-SUM(APL_AMT))*100/SUM(APL_AMT)   FROM OFFER_APL_HIST"
    res = cursor.execute(sql_read).fetchall()
    res_list = list()
        
    for i in range(len(res[0])):        
        print(comma_machine(res[0][i]))
        # res[0][i] = comma_machine(res[0][i]).value
        res_list.append(comma_machine(res[0][i]))
        # print(comma_machine(re.sub(r'[^0-9]', '', res[0][i])))
                       
    return render_template('index.html', res=res_list); 


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


