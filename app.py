from types import MethodDescriptorType
from flask import Flask, render_template
import sqlite3 
from sqlite3.dbapi2 import Cursor
import re
from flask import request  # request 처리 


from flask.wrappers import Request # 정규식

app = Flask(__name__, static_url_path="/static") 

DATABASE = './Database/prom.db'


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
    data = {'roi_rate': 0 }        
    #res_cnt default setting
    res_apl_cnt_list = [] 
    for i in range(0, 6):
        res_apl_cnt_list.append({'apl_cnt' : 0})
        
        
    # 프로모션 정보 확인 
    db = sqlite3.connect(DATABASE) 
    cursor = db.cursor()    
    current_page = 2
    pagesize = 3
    sql_read_prom_info = "SELECT PROM_ID, PROM_NM, OFFER_ID, OFFER_KIND_CD, PRVD_PRFT_TYPE_CD, PRVD_PRFT_VAL FROM PROM_HIST ORDER BY OFFER_ID DESC LIMIT "+str(pagesize)+" OFFSET "+str((current_page-1)*pagesize)
    res_prom_info = cursor.execute(sql_read_prom_info).fetchall()        

    return render_template('index.html', res=res, res_cnt=res_apl_cnt_list, res_prom_info=res_prom_info, data=data) # 예제 템플릿



@app.route('/promanaly', methods=['GET', 'POST']) # 접속할 URL
def promanaly():                
    # parameter get 
    OFFER_ID = request.form['offerid']

    #db 연결
    db = sqlite3.connect(DATABASE) 
    cursor = db.cursor()

    ######################## SQL1. 대시보드 데이터 read ########################
    sql_read_dashboard = "SELECT IFNULL(SUM(APL_AMT),0), IFNULL(SUM(SELLPRC),0), IFNULL((SUM(SELLPRC)-SUM(APL_AMT))*100/SUM(APL_AMT),0)   FROM OFFER_APL_HIST WHERE OFFER_ID = ?"

    res = cursor.execute(sql_read_dashboard, (OFFER_ID,)).fetchall()
    res_list = list()

    # 원단위 처리     
    for i in range(len(res[0])):            
        res_list.append(comma_machine(res[0][i]))                
    
    #################### SQL2. Earnings Overview data read ####################
    sql_read_dashboard = "SELECT APL_CNT  FROM OFFER_APL_HIST WHERE OFFER_ID = ? ORDER BY APL_DTS"
    res_apl_cnt = cursor.execute(sql_read_dashboard, (OFFER_ID,)).fetchall()

    res_apl_cnt_list = [] 
    for i in range(len(res_apl_cnt)):
        print(res_apl_cnt[i][0])
        res_apl_cnt_list.append({"apl_cnt" : res_apl_cnt[i][0]})

    #################### SQL3. DataTables ####################
    sql_read_prom_info = "SELECT PROM_ID, PROM_NM, OFFER_ID, OFFER_KIND_CD, PRVD_PRFT_TYPE_CD, PRVD_PRFT_VAL FROM PROM_HIST WHERE 1=1 AND OFFER_ID = "+ OFFER_ID
    res_prom_info = cursor.execute(sql_read_prom_info).fetchall()        


    # ROI javascript ( TODO : 재구매율 필요 )
    data = {  'roi_rate': res[0][2]  }                    

    # return render_template('index.html', res=res_list, ); 
    # data : roi rate progress bar 
    return render_template('index.html', res=res_list, res_cnt=res_apl_cnt_list, res_prom_info=res_prom_info, data=data); 


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


