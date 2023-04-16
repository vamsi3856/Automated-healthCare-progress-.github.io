from flask import Flask, render_template, request, redirect, url_for,session,flash,jsonify,abort as ab
from mysql.connector import connect 
import traceback
import json
from collections import defaultdict
con=connect(host='localhost',
            port=3306,
            database='university',
            user='root')
app=Flask(__name__)
app.secret_key='hfygdfychgjfhdf'
session={}
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctor_register_form')
def form1():
    return render_template("doctor_register.html")

@app.route('/client_register_form')
def form2():
    return render_template("client_register.html")

@app.route('/doctor_login_form')
def form3():
    return render_template("doctor_login.html")

@app.route('/client_login_form')
def form4():
    return render_template("client_login.html")

@app.route('/doctor_register', methods=['GET','POST'])
def doctor():
    if request.method=="POST":
        username=request.form['username']
        specialization=request.form['specialization']
        gender=request.form['gender']
        age=request.form['age']
        password=request.form['password']
        contact=request.form['contact'] 
        cur=con.cursor()
        cur.execute("insert into doctors(username,specialization,Gender,Age,password,Phone_number) values(%s,%s,%s,%s,%s,%s)",(username,specialization,gender,age,password,contact))
        con.commit()
        return redirect('/')
    else:
        return None
      
@app.route('/client_register',methods=['GET','POST'])
def client():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        cnfpass=request.form['cnfpass']
        gender=request.form['gender']
        age=request.form['age']
        contact=request.form['contact']
        if password==cnfpass: 
            cur=con.cursor()
            cur.execute("insert into clients(username,password,Gender,Age,Phone_number) values(%s,%s,%s,%s,%s)",(username,password,gender,age,contact))
            con.commit()
            return redirect('/')
        else:
            return "Password not matched!!"
    else:
        return None

@app.route('/doctors_profile',methods=['GET','POST'])
def doctors_profiles():
    if not session.get('patient'):
        if request.method=="POST":
            username=request.form['username']
            password=request.form['password']
            session['patient']=username
            cur=con.cursor()
            cur.execute("SELECT * FROM clients where username=%s and password=%s",(username,password))
            res=cur.fetchall()
            # print(res)
            if res:
                try:
                    curs=con.cursor()
                    curs.execute("SELECT * FROM doctors")
                    res1=curs.fetchall()
                    session['pdata']=res1
                    print("result:",res1)
                    return render_template("doctors_profile.html",pdata=res1,username=username)
                except:
                    session.pop('patient',None)
                    return render_template("cases.html")
            else:
                return "invalid crentials"
        else:
            return redirect('/client_login_form')
    else:
        return render_template("doctors_profile.html",pdata=session.get('pdata'),username=session.get('patient'))
        
        

@app.route('/clients_profile',methods=['POST','GET'])
def client_profiles():
    if not session.get('doctor'):
        if request.method=="POST":
            docname=request.form['username']
            password=request.form['password']
            session['doctor']=docname
            cur=con.cursor()
            cur.execute("SELECT * FROM doctors where username=%s and password=%s",(docname,password))
            res=cur.fetchall()
            if res:
                try:
                    curs=con.cursor()
                    curs.execute("SELECT client,cause from appointments where doctor=%s",(docname,))
                    res1=curs.fetchall()
                    lnt=len(res1)
                    session['data']=res1
                    session['lnt']=lnt
                    return render_template("clients_profile.html",data=res1,username=docname,lnt=lnt)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    session.pop('doctors',None) 
                    return render_template("cases.html") 
                    
            else:
                return "invalid credientials"  
        else:
            return redirect('/doctor_login_form') 
    else:
        return render_template("clients_profile.html",data=session.get('data'),username=session.get('doctor'),lnt=session.get('lnt'))


@app.route('/filter/<string:name>',methods=['GET','POST'])
def filter(name):
    if session.get('patient'):
        if request.method=="POST":
            specialization=request.form['filter']
            # session['specialization']=specialization
            cur=con.cursor()
            cur.execute("SELECT * FROM doctors where specialization=%s",(specialization,))
            res=cur.fetchall()
            session['sata']=res
            session['spec']=specialization
            return render_template("filter.html",sdata=session.get('sata'),name=name,specialization=specialization)
        else:
            # return redirect('/client_login_form')
            return render_template("client_login.html")
    else:
        return render_template("filter.html",sdata=session.get('sata'),name=name,specialization=session.get("spec"))
        

@app.route('/connect_now/<string:name>/<string:doctor>/<string:disease>', methods=['POST','GET'])
def connect_now(name,doctor,disease):
    session['patient']=name 
    if request.method=="POST":
        cause=request.form['cause']
    curs=con.cursor()
    curs.execute("SELECT * FROM appointments where client=%s and doctor=%s",(name,doctor))
    rc=curs.fetchall()
    if rc:
        curs.execute("UPDATE appointments SET `Time and Date`= CURRENT_TIMESTAMP,`cause`=%s WHERE client =%s AND doctor =%s",(cause,name,doctor))  
        con.commit()
    # curs.execute("insert into appointments(client,doctor,desease) values(%s,%s,%s)",(name,doctor,disease))
    else:
        curs.execute("insert into appointments(client,doctor,desease,cause) values(%s,%s,%s,%s)",(name,doctor,disease,cause))
        curs.execute("insert into prescription(Doctor,name,disease,cause,prescription) values(%s,%s,%s,%s,%s)",(doctor,name,disease,cause,"prescript here"))
        con.commit()
    # Redirect to the page that displayed the table
    return render_template("connect_now.html",name=name,doctor=doctor,disease=disease)
    # return f"you are connected with the {doctor} regarding the {disease}"
 
@app.route('/patient_pres/<string:username>')
def pat_pres(username):
    cur=con.cursor()
    cur.execute("SELECT doctor from appointments where client=%s",(username,))
    res=cur.fetchall()
    l=[]
    for i in res:
        l.append(i[0])
    print("patients")
    print(l) 
    ####################################################
    output = {}
    for doctor in l:
        cur.execute("SELECT medicine, date FROM medicines WHERE doctor=%s AND patient=%s", (doctor,username))
        medicine_data = {}
        for row in cur.fetchall():
            medicine_data[row[0]] = row[1].strftime('%d-%m-%Y')
        cur.execute("SELECT test, date FROM tests WHERE doctor=%s AND patient=%s", (doctor,username))
        test_data = {}
        for row in cur.fetchall():
            test_data[row[0]] = row[1].strftime('%d-%m-%Y')
        cur.execute("SELECT diagnose, date FROM diagnosis WHERE doctor=%s AND patient=%s", (doctor,username))
        diagnosis_data = {}
        for row in cur.fetchall():
            diagnosis_data[row[0]] = row[1].strftime('%d-%m-%Y')
        output[doctor] = {'medicine': medicine_data, 'test': test_data, 'diagnosis': diagnosis_data}
    print("final dtaa") 
    print(output)
    ####################################################
    return render_template("patient_pre_history.html",output=output,username=username)
    # return "hello" 
    
    
@app.route('/detailed_profile/<string:client>/<string:username>',methods=['GET','POST'])
def detailed_profile(client,username):
    session['doctor']=None
    if not session.get('doctor'): 
        session['doctor']=username
        try:
            print("hi")
            cur=con.cursor()
            cur.execute("SELECT * from clients where username=%s",(client,))
            res1=cur.fetchall()
            cur.execute("SELECT cause from appointments where client=%s AND doctor=%s",(client,username))
            problem=cur.fetchall()
            session['res1']=res1
            session['problem']=problem
            ############################################
            cur.execute("SELECT medicine, DATE_FORMAT(`date`, '%d-%m-%y') as formatted_date FROM medicines WHERE doctor=%s AND patient=%s ORDER BY date DESC", (username, client))
            res2=cur.fetchall()
            cur.execute("SELECT test,DATE_FORMAT(`date`, '%d-%m-%y') as formatted_date FROM tests WHERE doctor=%s AND patient=%s ORDER BY date DESC", (username,client))
            res3=cur.fetchall()
            cur.execute("SELECT diagnose,DATE_FORMAT(`date`, '%d-%m-%y') as formatted_date FROM diagnosis WHERE doctor=%s AND patient=%s ORDER BY date DESC", (username,client))
            res4=cur.fetchall()
            session['res2']=res2
            session['res3']=res3
            session['res4']=res4
            
        except Exception as e:
           print(e)
           traceback.print_exc()
        return render_template("detailed_profile.html",data=res1,username=username,problem=problem,med=res2,tes=res3,dia=res4)
        # return render_template("example.html")
        
        # return "he"  
    else:
        print("doctor") 
        print(session['doctor'])
        return render_template("detailed_profile.html",data=session.get('res1'),username=session.get('doctor'),problem=session.get('problem'),med=session.get('res2'),tes=session.get('res3'),dis=session.get('res4'))
        # return "hel"
        # return render_template("example.html")
# try:
print("HELLLO")
@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicines():
    if request.method == 'POST':
        medicine = request.form['mymedicine']
        doctor=request.form['mydoctor']
        patient=request.form['mypatient']
        cur = con.cursor()
        print(patient,doctor,medicine)
        print(type(patient)) 
        print("pointer")
        cur.execute("INSERT INTO medicines(patient, doctor, medicine) VALUES (%s, %s, %s)",(patient, doctor, medicine))
        con.commit()
        response = {'message':'Data submitted successfully!'} 
        return jsonify(response)
    else: 
        # return statement
        return "hell" 
# except Exception as e:
#     traceback.print_exc()
#     print("exp",e)
    # session.pop('doctors',None)   
@app.route('/add_test', methods=['GET', 'POST'])
def add_tests():
    if request.method == 'POST':
        test = request.form['mytest']
        doctor=request.form['mydoctor']
        patient=request.form['mypatient']
        cur = con.cursor()
        cur.execute("INSERT INTO tests(patient, doctor,test) VALUES (%s, %s, %s)",(patient, doctor,test))
        con.commit()
        response = {'message':'Data submitted successfully!'} 
        return jsonify(response)
    else: 
        # return statement
        return "hell" 

@app.route('/add_diag',methods=['GET','POST'])
def add_diag():
    if request.method == 'POST':
        diag = request.form['diag']
        doctor=request.form['mydoctor']
        patient=request.form['mypatient']
        cur = con.cursor()
        cur.execute("INSERT INTO diagnosis(patient, doctor,diagnose) VALUES (%s, %s, %s)",(patient, doctor,diag))
        con.commit()
        response = {'message':'Data submitted successfully!'} 
        return jsonify(response)
    else: 
        # return statement 
        return "hell" 

@app.route('/order_medicine',methods=['GET','POST'])
def order_medicines():
    if request.method=='POST':
        print("entered") 
        name = request.form['name']
        print(name)
        contact=request.form['contact']
        print(contact)
        medicine=request.form['patmed'] 
        print(medicine) 
        ordermode=request.form['ordermode']
        address=request.form['address']
        city=request.form['city']
        pincode=request.form['pincode']
        cur = con.cursor()
        print(name,contact,medicine) 
        print("pointer1")
        cur.execute("INSERT INTO medicine_order(name, contact,medicine,order_mode,address,city,pincode) VALUES (%s, %s, %s,%s,%s,%s,%s)",(name,contact, medicine,ordermode,address,city,pincode))
        con.commit()
        response = {'message':'order successfull check your orders!'}
        return jsonify(response)
    else:
        # return statement
        return "hell" 
@app.route('/order_test',methods=['GET','POST'])
def order_test():
    if request.method=='POST':
        print("entered") 
        name = request.form['name1']
        print(name)
        contact=request.form['contact1']
        print(contact)
        test=request.form['patmed1'] 
        print(test) 
        testmode=request.form['testmode1']
        address=request.form['address1']
        city=request.form['city1']
        pincode1=request.form['pincode1']
        cur = con.cursor()
        print(name,contact,test) 
        print("pointer1")
        cur.execute("INSERT INTO test_order(name, contact,test,test_mode,address,city,pincode) VALUES (%s, %s, %s,%s,%s,%s,%s)",(name,contact, test,testmode,address,city,pincode1))
        con.commit()
        response = {'message':'order successfull check your orders!'}
        return jsonify(response)
    else:
        # return statement
        return "hell" 
################################################################################################
@app.route('/order_diag',methods=['GET','POST'])
def order_diag():
    if request.method=='POST':
        print("entered") 
        name = request.form['name2']
        print(name)
        contact=request.form['contact2']
        print(contact)
        test=request.form['patmed2'] 
        print(test) 
        diag_date=request.form['diag_date']
        address=request.form['address2']
        city=request.form['city2']
        pincode2=request.form['pincode2']
        cur = con.cursor()
        print(name,contact,test) 
        print("pointer1")
        cur.execute("INSERT INTO diag_order(name, contact,diagnosis,diag_date,address,city,pincode) VALUES (%s, %s, %s,%s,%s,%s,%s)",(name,contact, test,diag_date,address,city,pincode2))
        con.commit()
        response = {'message':'order successfull check your orders!'}
        return jsonify(response)
    else:
        # return statement
        return "hell" 

@app.route('/open_medical')
def openmed():
    return render_template("mc_login.html")

@app.route('/open_test')
def opentest():
    return render_template("tc_login.html")

@app.route('/open_diagnose')
def opendiiag():
    return render_template("dc_login.html")

@app.route('/medical_admin',methods=['GET','POST'])
def medical_admin():
    if request.method=='POST':
        name=request.form['username']
        password=request.form['password']
        cur=con.cursor() 
        cur.execute('SELECT * from admin')
        res=cur.fetchall()
        print("i don't")
        print(res)
        if res[0][0]==name and res[0][1]==password:
            return render_template("medical_orders.html")
        else:
            return "invalid credientials"
    else:
        return "get method"
@app.route('/test_admin',methods=['GET','POST'])
def test_admin():
    if request.method=='POST':
        name=request.form['username']
        password=request.form['password']
        cur=con.cursor()
        cur.execute('SELECT * from admin')
        res=cur.fetchall()
        if res[0][0]==name and res[0][1]==password:
            return render_template("test_orders.html")
        else:
            return "invalid credientials"
    else:
        return "get method"

@app.route('/diagnosis_admin',methods=['GET','POST'])
def diag_admin():
    if request.method=='POST':
        name=request.form['username']
        password=request.form['password']
        cur=con.cursor()
        cur.execute('SELECT * from admin')
        res=cur.fetchall()
        if res[0][0]==name and res[0][1]==password:
            return render_template("diagnosis_orders.html")
        else:
            return "invalid credientials"
    else:
        return "get method"

    
@app.route('/logout')
def logout():
    session['patient']=None
    session['doctor']=None
    session['data']=None 

    session['pdata']=None 
    session['sdata']=None
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)