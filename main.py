#Importing Flask module
from flask import Flask, render_template, request, redirect, url_for, session
#importing regular expressions module - for string comparisons
import re
#Importing Sqlite database tools
import sqlite3
#Cryptography module, to encrypt password
from cryptography.fernet import Fernet
#Import csv module for bulk upload of jobs
import csv
#For uploading bulk upload files
import os
#Tools for checking file name of bulk upload file
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import numpy as np

#Secret Key for encrypting passwords
key = Fernet.generate_key()

#For bulk Job Upload
UPLOAD_FOLDER = 'static/files/'
ALLOWED_EXTENSIONS = {'csv'}

#Method for checking proper file extension format 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Method for changing filename of photo and resume to username
def can_file_name(filename,usrname):
    length=len(filename)
    count = 0
    for i in filename:
        if i != '.':
            count+=1
        else:
            break

    return usrname + filename[(count-length):]

#Method for calculating average, maximum and minimum pay
def pay_calc(match):
    cnt = 0
    count = 0
    max_pay = 0
    min_pay = 0
    for i in match:
        cnt+=1
    pay = 0
    for i in range(0,cnt):
        try:
            pay = pay + int(match[i][5])
            
        except:
            count+=1
    try:
        avg_pay = pay//(cnt-count)
    except:
        avg_pay=0
    for i in range(0,cnt):
        try:
            max_pay = int(match[i][5])
            min_pay = int(match[i][5])
            
            break
        except:
            pass
    
    if cnt > 1:
        for i in range(0,cnt):
            try:
                if int(match[i][5]) < min_pay:
                    min_pay = int(match[i][5])
                if int(match[i][5]) >= max_pay:
                    max_pay = int(match[i][5])
            except:
                pass

    return avg_pay, max_pay, min_pay

#Starting Flask
app = Flask(__name__)

# Secret key for the app
app.secret_key = '123456'
     
# http://localhost:5000/index.html, Starting page
@app.route('/', methods=['GET', 'POST'])
def login():
     
    # Output message if something goes wrong...
    msg = '' 
    # Checks if "username", "password" and "type" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check whether account exists in SQLite database
        with sqlite3.connect("Data_Analytics.db") as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (username, ))
            # Fetch one record and return result
            account = cur.fetchone()
            # If account exists in accounts table in database
            if account:
                key = account[6].encode()
                cipher_suite = Fernet(key)
                chk_pass = cipher_suite.decrypt(account[4])
                if username == "admin@gmail.com":
                    if chk_pass.decode() == password:
                        # Create session data, we can access this data from other pages
                        session['loggedin'] = True
                        session['username'] = username
                        session['fstname'] = account[1]
                        session['lstname'] = account[2]
                        # Redirect to home page
                        return redirect(url_for('adm_profile'))
                    else:
                        # Password incorrect
                        msg = 'Incorrect username/password!'
                else:
                    if chk_pass.decode() == password:
                        if account[14] == "Active":
                            # Create session data, we can access this data from other pages
                            session['loggedin'] = True
                            session['username'] = username
                            session['fstname'] = account[1]
                            session['lstname'] = account[2]
                            # Redirect to home page
                            return redirect(url_for('profile'))
                        else:
                            msg = 'Your Account has been suspended!!'
                    else:
                        # Password incorrect
                        msg = 'Incorrect username/password!'
            else:
                # Account doesnt exist
                msg = 'Incorrect username/password!'
                    
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


# http://localhost:5000/logout - this method will be do the logout action
@app.route('/logout')
def logout():
   # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


# http://localhost:5000/register - this will be the User registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    
    # Output message if something goes wrong...
    msg = ''
    user = ''
    mob = ''
    fstname = ''
    lstname = ''
    # Check if "username", "password"  "email" "mobile" etc. POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'password-confirm' in request.form:
        # Create variables for easy access
        fstname = request.form['fstname']
        lstname = request.form['lstname']
        user = request.form['email']
        mob = request.form['Mobile']
        agree = request.form['agree']
        if user[:5] != "admin":
            pass1 = request.form['password']
            pass2 = request.form['password-confirm']
            if pass1 == pass2:
                cipher_suite = Fernet(key)
                pas = cipher_suite.encrypt((request.form['password']).encode())
                # Check if account exists using SQLite
                with sqlite3.connect("Data_Analytics.db") as con:
                    cur = con.cursor()
                    cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (user,))
                    account = cur.fetchone()
                    # If account exists show error and validation checks
                    if account:
                        msg = 'Account already exists!'
                    elif not re.match(r'[^@]+@[^@]+\.[^@]+', user):
                        msg = 'Invalid email address!'
                    elif not user or not pas:
                        msg = 'Please fill out the form!'
                    elif agree == "N":
                        msg = 'To register, please accept the terms and conditions..'
                    else:
                        # Account doesnt exists and the form data is valid, now insert new account into accounts table
                        with sqlite3.connect("Data_Analytics.db") as con:
                            cur = con.cursor()
                            cur.execute("INSERT INTO User (Usr_Fname, Usr_Lname, Usr_usrname, Usr_Pass, Usr_Mob, Usr_cip, Usr_Sta) VALUES (?,?,?,?,?,?,?)",(fstname, lstname, user, pas, mob, key.decode(), "Active"))
                            con.commit()
                            msg = 'You have successfully registered!'
            else:
                msg='Passwords didn\'t match'
        else:
            msg="e-mail ID cannot start with \"admin\""

    # Show registration form with message (if any)
    
    return render_template('register.html', msg=msg, user=user, mob=mob, fstname=fstname, lstname=lstname)


# http://localhost:5000/profile - this will be the User profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
                account = cur.fetchone()
                # Show the profile page with account info
                return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))


# http://localhost:5000/adm_profile - this will be the Admin profile page, only accessible for loggedin administrator
@app.route('/adm_profile')
def adm_profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT count(Usr_ID) FROM User')
                usr_count = cur.fetchone()
                cur.execute('SELECT count(Job_ID) FROM Job')
                job_count = cur.fetchone()
                # Show the profile page with account info
                return render_template('adm_profile.html', usr_count=usr_count[0]-1, job_count=job_count[0])
    # User is not loggedin redirect to login page
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))


# http://localhost:5000/adm_usr_mgmt - Administrator manages the users through this page
@app.route('/adm_usr_mgmt')
def adm_usr_mgmt():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        with sqlite3.connect("Data_Analytics.db") as con:
           cur = con.cursor()
           cur.execute('SELECT * FROM User')
           items = cur.fetchall()
           cur.execute('Select count(Usr_usrname) from User')
           cnt = cur.fetchone()
           count = cnt[0]
           lst = []
           for i in range(0,count):
               if items[i][3] != 'admin@gmail.com':
                   tup = (i, items[i][3], items[i][1], items[i][2], items[i][5], items[i][14])
                   lst.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5]))
           con.commit()

        # Show the profile page with account info
        return render_template('adm_usr_mgmt.html', lst=lst, count=count-1)
    # User is not loggedin redirect to login page
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))

# http://localhost:5000/adm_usr_del - User delete action
@app.route('/adm_usr_del/<action>/<item_id>', methods=['GET', 'POST'])
def adm_usr_del(action=None, item_id=None):
    # Check if user is loggedin
    if 'loggedin' in session:
        msg = ''
        if action == 'delete':

            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('DELETE FROM User where Usr_usrname = ?', (item_id,))
                msg = "User with Username " + item_id + " deleted sucessfully"
                cur.execute('SELECT * FROM User')
                items = cur.fetchall()
                cur.execute('Select count(Usr_usrname) from User')
                cnt = cur.fetchone()
                count = cnt[0]
                lst = []
                for i in range(0,count):
                    if items[i][3] != "admin@gmail.com":
                        tup = (i+1, items[i][3], items[i][1], items[i][2], items[i][5], items[i][14]) 
                        lst.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5]))
                con.commit()

        # Show the profile page with account info        
        
        return render_template('adm_usr_mgmt.html', lst=lst, count=count-1, msg=msg)
    # User is not loggedin redirect to login page
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))

# http://localhost:5000/adm_usr_sus - User suspend action
@app.route('/adm_usr_sus/<action>/<item_id>', methods=['GET', 'POST'])
def adm_usr_sus(action=None, item_id=None):
    # Check if user is loggedin
    if 'loggedin' in session:
        msg = ''
        if action == 'suspend':

            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('update User set Usr_Sta = ? where Usr_usrname = ?', ("Suspended", item_id,))
                msg = "User with Username " + item_id + " is suspended"
                cur.execute('SELECT * FROM User')
                items = cur.fetchall()
                cur.execute('Select count(Usr_usrname) from User')
                cnt = cur.fetchone()
                count = cnt[0]
                lst = []
                for i in range(0,count):
                    if items[i][3] != "admin@gmail.com":
                        tup = (i+1, items[i][3], items[i][1], items[i][2], items[i][5], items[i][14]) 
                        lst.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5]))
                con.commit()
                print(lst)
        if action == 'revoke':
            
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('update User set Usr_Sta = ? where Usr_usrname = ?', ("Active", item_id,))
                msg = "User with Username " + item_id + " is now Active"
                cur.execute('SELECT * FROM User')
                items = cur.fetchall()
                cur.execute('Select count(Usr_usrname) from User')
                cnt = cur.fetchone()
                count = cnt[0]
                lst = []
                for i in range(0,count):
                    if items[i][3] != "admin@gmail.com":
                        tup = (i+1, items[i][3], items[i][1], items[i][2], items[i][5], items[i][14]) 
                        lst.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5]))
                con.commit()            
        # Show the profile page with account info        
        
        return render_template('adm_usr_mgmt.html', lst=lst, count=count-1, msg=msg)
    # User is not loggedin redirect to login page
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))

# http://localhost:5000/adm_job_mgmt - administrator manages jobs from this page
@app.route('/adm_job_mgmt', methods=['GET', 'POST'])
def adm_job_mgmt():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        with sqlite3.connect("Data_Analytics.db") as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM Job')
            items = cur.fetchall()
            cur.execute('Select count(Job_ID) from Job')
            cnt = cur.fetchone()
            con.commit()
            count = cnt[0]
            lst = []
            if count <= 20:
                for i in range(0,count):
                    tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                    lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                return render_template('adm_job_mgmt.html', lst=lst, count_t=count)
            else:
                count_t=20
                for i in range(0,20):
                    tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                    lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                return render_template('adm_job_mgmt_lst.html', lst=lst, count_t=count_t)
                  
    # User is not loggedin redirect to login page
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))
    
@app.route('/adm_job_mgmt_lst/<action>/<lst_from>', methods=['GET', 'POST'])
def adm_job_mgmt_lst(action=None, lst_from=None):
    # Check if user is loggedin
    if 'loggedin' in session:
        lst=[]
        if action == 'next':
            # We need all the account info for the user so we can display it on the profile page
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM Job')
                items = cur.fetchall()
                cur.execute('Select count(Job_ID) from Job')
                cnt = cur.fetchone()
                con.commit()
                count = cnt[0]
            if int(lst_from) + 20 == count:
                lst = []
                count_t=20
                for i in range(int(lst_from),int(lst_from) + 20):
                    tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                    lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                return render_template('adm_job_mgmt_prev.html', lst=lst, count_t=count_t)  
            elif int(lst_from) + 20 < count:
                count_t=20
                for i in range(int(lst_from),int(lst_from) + 20):
                    tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                    lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                return render_template('adm_job_mgmt_lst_prev.html', lst=lst, count_t=count_t)                
            else:
                lst=[]
                count_t = count - int(lst_from)
                for i in range(int(lst_from), int(lst_from) + count_t):
                    tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                    lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                return render_template('adm_job_mgmt_prev.html', lst=lst, count_t=count_t)   
        if action == 'previous':
            # We need all the account info for the user so we can display it on the profile page
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM Job')
                items = cur.fetchall()
                cur.execute('Select count(Job_ID) from Job')
                cnt = cur.fetchone()
                con.commit()
                count = cnt[0]
            lst = []
            count_1 = int(lst_from) % 20
            if count_1 == 0:
                if int(lst_from) - 20 == 20:
                    for i in range(0, 20):
                        tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                        lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                    return render_template('adm_job_mgmt_lst.html', lst=lst, count_t=20) 
                else:
                    for i in range(int(lst_from) - 40, int(lst_from) - 20):
                        tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                        lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                    return render_template('adm_job_mgmt_lst_prev.html', lst=lst, count_t=20)
            else:
                count_2 = int(lst_from) - count_1
                if count_2 == 20:
                    for i in range(0, 20):
                        tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                        lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                    return render_template('adm_job_mgmt_lst.html', lst=lst, count_t=20) 
                else:    
                    for i in range(count_2 - 20, count_2 + 1):
                        tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                        lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                    return render_template('adm_job_mgmt_lst_prev.html', lst=lst, count_t=20)                    

                 
        # Show the profile page with account info
        return render_template('adm_job_mgmt.html', lst=lst, count=count)
    # User is not loggedin redirect to login page
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))
    
# http://localhost:5000/adm_job_del - administrator deletes jobs
@app.route('/adm_job_del/<action>/<item_id>', methods=['GET', 'POST'])
def adm_job_del(action=None, item_id=None):
    # Check if user is loggedin
    if 'loggedin' in session:
        msg = ''
        if action == 'delete':

            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('DELETE FROM Job where Job_ID = ?', (item_id,))
                msg = "Job with Job ID " + item_id + " deleted sucessfully"
                cur.execute('SELECT * FROM Job')
                items = cur.fetchall()
                cur.execute('Select count(Job_ID) from Job')
                cnt = cur.fetchone()
                count = cnt[0]
                lst = []
                for i in range(0,count):
                    tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                    lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                con.commit()

        # Show the profile page with account info        
            if count <= 20:
                for i in range(0,count):
                    tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                    lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                return render_template('adm_job_mgmt.html', lst=lst, count_t=count, msg=msg)
            else:
                count_t=20
                for i in range(0,20):
                    tup = (i+1, items[i][1], items[i][2], items[i][3], items[i][9]) 
                    lst.append((tup[0], tup[1], tup[2], tup[3], tup[4]))
                return render_template('adm_job_mgmt_lst.html', lst=lst, count_t=count_t, msg=msg) 

    # User is not loggedin redirect to login page
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))

@app.route('/adm_job_edit/<action>/<item_id>', methods=['GET', 'POST'])
def adm_job_edit(action=None, item_id=None):
    # Check if user is loggedin
    if 'loggedin' in session:
        msg = ''
        if action == 'edit':
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('select * FROM Job where Job_ID = ?', (item_id,))
                items = cur.fetchone()
                con.commit()
                
            return render_template('adm_job_edit.html', items=items, msg=msg)        

    # User is not loggedin redirect to login page
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))    
    
@app.route('/adm_job_edit_update', methods=['GET', 'POST'])
def adm_job_edit_update():
    # Check if user is loggedin
    if 'loggedin' in session:
        msg = ''
        if request.method == 'POST':
            job_tit = request.form['job_tit']
            job_comp = request.form['job_comp']
            job_exp = request.form['job_exp']
            job_sal = request.form['job_sal']
            job_desc = request.form['job_desc']
            job_loc = request.form['job_loc']
            job_type = request.form['job_type']
            job_not_date = request.form['job_not_date']
            job_appl_lnk = request.form['job_appl_lnk']
            job_car_lvl = request.form['job_car_lvl']
            job_qual = request.form['job_qual']
            job_id = request.form['job_id']
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('select * FROM Job where Job_ID = ?', (job_id,))
                items = cur.fetchone()
                if job_tit:
                    cur.execute('update Job set Job_Tit = ? where Job_ID = ?', (job_tit, job_id))
                if job_comp:
                    cur.execute('update Job set Job_Comp = ? where Job_ID = ?', (job_comp, job_id))
                if job_exp:
                    cur.execute('update Job set Job_Exp = ? where Job_ID = ?', (job_exp, job_id))
                if job_sal:
                    cur.execute('update Job set Job_Sal = ? where Job_ID = ?', (job_sal, job_id))
                if job_desc:
                    cur.execute('update Job set Job_Des = ? where Job_ID = ?', (items[6], job_id))
                if job_loc:
                    cur.execute('update Job set Job_Loc = ? where Job_ID = ?', (job_loc, job_id))
                if job_type:
                    cur.execute('update Job set Job_Type = ? where Job_ID = ?', (job_type, job_id))
                if job_not_date:
                    cur.execute('update Job set Job_Not_Date = ? where Job_ID = ?', (job_not_date, job_id))
                if job_appl_lnk:
                    cur.execute('update Job set Job_Appl_Link = ? where Job_ID = ?', (job_appl_lnk, job_id))
                if job_car_lvl:
                    cur.execute('update Job set Job_Car_Lvl = ? where Job_ID = ?', (job_car_lvl, job_id))
                if job_qual:
                    cur.execute('update Job set Job_Qual = ? where Job_ID = ?', (job_qual, job_id))
                msg="Updation Successful!!!"
                con.commit()
                
            return render_template('adm_job_edit.html', items=items, msg=msg)        

    # User is not loggedin redirect to login page
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login')) 

# http://localhost:5000/adm_add_job 
@app.route('/adm_add_job', methods=['GET', 'POST'])
def adm_add_job():
    # Check if user is loggedin
    if 'loggedin' in session:
        # Output message if something goes wrong...
        msg = ''
        if request.method == 'POST'and 'job_tit' in request.form and 'job_comp' in request.form and 'job_exp' in request.form:
            # Create variables for easy access
            job_tit = request.form['job_tit']
            job_comp = request.form['job_comp']
            job_exp = request.form['job_exp']
            job_sal = request.form['job_sal']
            job_desc = request.form['job_desc']
            job_loc = request.form['job_loc']
            job_type = request.form['job_type']
            job_not_date = request.form['job_not_date']
            job_appl_lnk = request.form['job_appl_lnk']
            job_car_lvl = request.form['job_car_lvl']
            job_qual = request.form['job_qual']
            job_id = request.form['job_id']
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * from Job WHERE Job_ID = ?', (job_id,))
                job_ava_id = cur.fetchone()
                if job_ava_id is None:
                    cur.execute('INSERT INTO Job (Job_ID, Job_Tit, Job_Comp, Job_Exp, Job_Sal, Job_Des, Job_Loc, Job_Type, Job_Not_Date, Job_Appl_Link, Job_Car_Lvl, Job_Qual) values (?,?,?,?,?,?,?,?,?,?,?,?)',(job_id, job_tit, job_comp, job_exp, job_sal, job_desc, job_loc.upper(), job_type, job_not_date, job_appl_lnk, job_car_lvl, job_qual)) 
                    con.commit()
                    msg = 'Job Updated!'
                else:
                    msg = 'Job ID Already exists!!'
        # Show the profile page with account info
        return render_template('adm_add_job.html', msg=msg)
    else:
        # User is not loggedin redirect to login page
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))

    
# http://localhost:5000/usr_chg_pwd - this will be the page from which User will be able to change password, only accessible for loggedin users
@app.route('/usr_chg_pwd', methods=['GET', 'POST'])
def usr_chg_pwd():
    if 'loggedin' in session:
        with sqlite3.connect("Data_Analytics.db") as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
            account = cur.fetchone()
            key = account[6].encode()
            cipher_suite = Fernet(key)
            chk_pass = cipher_suite.decrypt(account[4])
            curr_pw_stored = chk_pass.decode()
        msg = ''
        # Settings for uploading Photos

        if request.method == 'POST' and 'curr_pwd' in request.form and 'new_pwd_1' in request.form and 'new_pwd_2' in request.form:
            curr_pw = request.form['curr_pwd']
            new_pw_1 = request.form['new_pwd_1']
            new_pw_2 = request.form['new_pwd_2']
            if curr_pw:
                if curr_pw != curr_pw_stored:
                    msg = "Current Password you have entered is Wrong"
                    session.pop('loggedin', None)
                    session.pop('username', None)
                    return redirect(url_for('login'))
                elif new_pw_1 != new_pw_2:
                    msg = "New Passwords don't match"
                    return render_template('usr_chg_pwd.html',account=account, msg=msg)  
                else:
                    cipher_suite = Fernet(key)
                    new_pw_1_enc = cipher_suite.encrypt(new_pw_1.encode())      
                    cur.execute('UPDATE User SET Usr_Pass = ? WHERE Usr_usrname = ?', (new_pw_1_enc, session['username'],))
                    cur.execute('UPDATE User SET Usr_cip = ? WHERE Usr_usrname = ?', (key.decode(), session['username'],))
                    con.commit()
                    msg = "Password changed Successfully!"
            else:
                msg = "Please enter all fields!"            
        return render_template('usr_chg_pwd.html',account=account, msg=msg)    
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))


# http://localhost:5000/adm_chg_pwd - this will be the page from which Admin will be able to change password, only accessible for loggedin users
@app.route('/adm_chg_pwd', methods=['GET', 'POST'])
def adm_chg_pwd():
    if 'loggedin' in session:
        with sqlite3.connect("Data_Analytics.db") as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
            account = cur.fetchone()
            key = account[6].encode()
            cipher_suite = Fernet(key)
            chk_pass = cipher_suite.decrypt(account[4])
            curr_pw_stored = chk_pass.decode()
        msg = ''
        # Settings for uploading Photos

        if request.method == 'POST' and 'curr_pwd' in request.form and 'new_pwd_1' in request.form and 'new_pwd_2' in request.form:
            curr_pw = request.form['curr_pwd']
            new_pw_1 = request.form['new_pwd_1']
            new_pw_2 = request.form['new_pwd_2']
            if curr_pw:
                if curr_pw != curr_pw_stored:
                    msg = "Current Password you have entered is Wrong"
                    session.pop('loggedin', None)
                    session.pop('username', None)
                    return redirect(url_for('login'))
                elif new_pw_1 != new_pw_2:
                    msg = "New Passwords don't match"
                    return render_template('adm_chg_pwd.html',account=account, msg=msg)  
                else:
                    cipher_suite = Fernet(key)
                    new_pw_1_enc = cipher_suite.encrypt(new_pw_1.encode())      
                    cur.execute('UPDATE User SET Usr_Pass = ? WHERE Usr_usrname = ?', (new_pw_1_enc, session['username'],))
                    cur.execute('UPDATE User SET Usr_cip = ? WHERE Usr_usrname = ?', (key.decode(), session['username'],))
                    con.commit()
                    msg = "Password changed Successfully!"
            else:
                msg = "Please enter all fields!"            
        return render_template('adm_chg_pwd.html',account=account, msg=msg)    
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))


# http://localhost:5000/usr_profile_update - this will be the User profile updation page, only accessible for loggedin users
@app.route('/usr_profile_update', methods=['GET', 'POST'])
def usr_profile_update():
    if 'loggedin' in session:
        with sqlite3.connect("Data_Analytics.db") as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
            account = cur.fetchone()
        msg = ''
        # Check if "username", "password"  "email" "mobile" etc. POST requests exist (user submitted form)
        if request.method == 'POST':
            # Create variables for easy access
            mob = request.form['mobile']
            fstname = request.form['fstname']
            lstname = request.form['lstname']
            # Check which elements are present in the form and update those
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
                account = cur.fetchone()
                if mob:
                    if len(str(mob)) != 10:
                        msg = 'Invalid Mobile Number'
                        return render_template('usr_profile_update.html',account=account, msg=msg)
                    else:
                        cur.execute("UPDATE User SET Usr_Mob = ? WHERE Usr_usrname = ?",(mob, session['username']))
                        msg = 'Updation Sucessful!'
                if fstname:
                    cur.execute("UPDATE User SET Usr_Fname = ? WHERE Usr_usrname = ?",(fstname, session['username']))                    
                    msg = 'Updation Sucessful!'
                if lstname:
                    cur.execute("UPDATE User SET Usr_Lname = ? WHERE Usr_usrname = ?",(lstname, session['username']))                    
                    msg = 'Updation Sucessful!'                
                con.commit()  
        return render_template('usr_profile_update.html',account=account, msg=msg)
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))


# http://localhost:5000/usr_cur_work_prof 
@app.route('/usr_cur_work_prof', methods=['GET', 'POST'])
def usr_cur_work_prof():
    if 'loggedin' in session:
        with sqlite3.connect("Data_Analytics.db") as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
            account = cur.fetchone()
        msg = ''
        return render_template('usr_cur_work_prof.html',account=account, msg=msg)
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))


# http://localhost:5000/usr_cur_work_prof_upd 
@app.route('/usr_cur_work_prof_upd', methods=['GET', 'POST'])
def usr_cur_work_prof_upd():
    if 'loggedin' in session:
        with sqlite3.connect("Data_Analytics.db") as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
            account = cur.fetchone()
            con.commit()
        msg = ''
        # Check if "username", "password"  "email" "mobile" etc. POST requests exist (user submitted form)
        if request.method == 'POST':
            # Create variables for easy access
            edu_qua = request.form['edu_qua']
            con_wrk_exp = request.form['con_wrk_exp']
            pre_wrk_pos = request.form['pre_wrk_pos']
            pre_car_lvl = request.form['pre_car_lvl']
            lst_wrk_ten = request.form['lst_wrk_ten']
            exp_pos = request.form['exp_pos']
            exp_car_lvl = request.form['exp_car_lvl']
            # Check which elements are present in the form and update those
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
                account = cur.fetchone()
                if edu_qua:
                    cur.execute("UPDATE User SET Usr_edu_qual = ? WHERE Usr_usrname = ?",(edu_qua, session['username']))                    
                    msg = 'Updation Sucessful!'
                if con_wrk_exp:
                    cur.execute("UPDATE User SET Usr_con_wrk_exp = ? WHERE Usr_usrname = ?",(con_wrk_exp, session['username']))                    
                    msg = 'Updation Sucessful!'
                if pre_wrk_pos:
                    cur.execute("UPDATE User SET Usr_pre_wrk_pos = ? WHERE Usr_usrname = ?",(pre_wrk_pos, session['username']))                    
                    msg = 'Updation Sucessful!'  
                if pre_car_lvl:
                    cur.execute("UPDATE User SET Usr_pre_car_lvl = ? WHERE Usr_usrname = ?",(pre_car_lvl, session['username']))                    
                    msg = 'Updation Sucessful!' 
                if lst_wrk_ten:
                    cur.execute("UPDATE User SET Usr_lst_wrk_ten = ? WHERE Usr_usrname = ?",(lst_wrk_ten, session['username']))                    
                    msg = 'Updation Sucessful!'
                if exp_pos:
                    cur.execute("UPDATE User SET Usr_exp_pos = ? WHERE Usr_usrname = ?",(exp_pos, session['username']))                    
                    msg = 'Updation Sucessful!'
                if exp_car_lvl:
                    cur.execute("UPDATE User SET Usr_exp_car_lvl = ? WHERE Usr_usrname = ?",(exp_car_lvl, session['username']))                    
                    msg = 'Updation Sucessful!'  

                con.commit()  
        with sqlite3.connect("Data_Analytics.db") as con:
            cur = con.cursor()
            job_list_pri = []
            cur.execute('SELECT * FROM Job')
            jobs_list = cur.fetchall()
            cur.execute('SELECT count(Job_ID) from Job')
            jobs_count = cur.fetchone()
            con.commit()
            for i in range(0,jobs_count[0]):
                job_list_pri.append(jobs_list[i][2])
                job_list_sec = set(job_list_pri)
                job_list = list(job_list_sec)
        return render_template('usr_cur_work_prof_upd.html',account=account, msg=msg, job_list=job_list)
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))


@app.route('/usr_job_search', methods=['GET', 'POST'])
def usr_job_search():
    if 'loggedin' in session:
        msg=''
        if request.method == 'POST' and 'city' in request.form:
            city = request.form['city']
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
                account = cur.fetchone()
                usr_pref_pos = account[12]
                usr_pref_car_lvl = account[13]
                usr_pref_exp = account[8]
                cur.execute('SELECT * FROM Job WHERE Job_Loc = ? and Job_Tit = ? and Job_Car_Lvl = ? and Job_Exp = ?', (city, usr_pref_pos, usr_pref_car_lvl, usr_pref_exp))
                match_jobs = cur.fetchall()
                con.commit()
        
            match_count=len(match_jobs)
            lst = []
            for i in range(0,match_count):
                tup = (i+1, match_jobs[i][1], match_jobs[i][2], match_jobs[i][3], match_jobs[i][11], match_jobs[i][5], match_jobs[i][6], match_jobs[i][7], match_jobs[i][10]) 
                lst.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8]))
            
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                city_list_pri = []
                cur.execute('SELECT * FROM Job')
                jobs_list = cur.fetchall()
                cur.execute('SELECT count(Job_ID) from Job')
                jobs_count = cur.fetchone()
                con.commit()
                for i in range(0,jobs_count[0]):
                    city_list_pri.append(jobs_list[i][7])
                city_list_sec = set(city_list_pri)
                city_list = list(city_list_sec)
                city_list.sort()
            return render_template('usr_job_search.html', msg=msg, lst=lst, match_count=match_count, account=account, city_list=city_list, city=city)
        else:
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
                account = cur.fetchone()
                usr_pref_pos = account[12]
                usr_pref_car_lvl = account[13]
                usr_pref_exp = account[8]
                cur.execute('SELECT * FROM Job WHERE Job_Tit = ? and Job_Car_Lvl = ? and Job_Exp = ?', (usr_pref_pos, usr_pref_car_lvl, usr_pref_exp))
                match_jobs = cur.fetchall()
                con.commit()
        
            match_count=len(match_jobs)
            lst = []
            for i in range(0,match_count):
                tup = (i+1, match_jobs[i][1], match_jobs[i][2], match_jobs[i][3], match_jobs[i][11], match_jobs[i][5], match_jobs[i][6], match_jobs[i][7], match_jobs[i][10]) 
                lst.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8]))

            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                city_list_pri = []
                cur.execute('SELECT * FROM Job')
                jobs_list = cur.fetchall()
                cur.execute('SELECT count(Job_ID) from Job')
                jobs_count = cur.fetchone()
                con.commit()
                for i in range(0,jobs_count[0]):
                    city_list_pri.append(jobs_list[i][7])
                city_list_sec = set(city_list_pri)
                city_list = list(city_list_sec)
                city_list.sort()
            return render_template('usr_job_search.html', msg=msg, lst=lst, match_count=match_count, account=account, city_list=city_list)    
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))

   
@app.route('/usr_job_search_sugg', methods=['GET', 'POST'])
def usr_job_search_sugg():
    if 'loggedin' in session:
        msg=''
        if request.method == 'POST' and 'city' in request.form:
            city = request.form['city']
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
                account = cur.fetchone()
                usr_pref_car_lvl = account[13]
                usr_pref_exp = account[8]
                cur.execute('SELECT * FROM Job WHERE Job_Loc = ? and Job_Car_Lvl = ? and Job_Exp = ?', (city, usr_pref_car_lvl, usr_pref_exp))
                match_jobs = cur.fetchall()
                con.commit()
        
            match_count=len(match_jobs)
            lst = []
            for i in range(0,match_count):
                tup = (i+1, match_jobs[i][1], match_jobs[i][2], match_jobs[i][3], match_jobs[i][4], match_jobs[i][11], match_jobs[i][5], match_jobs[i][6], match_jobs[i][7], match_jobs[i][10]) 
                lst.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8], tup[9]))
            
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                city_list_pri = []
                cur.execute('SELECT * FROM Job')
                jobs_list = cur.fetchall()
                cur.execute('SELECT count(Job_ID) from Job')
                jobs_count = cur.fetchone()
                con.commit()
                for i in range(0,jobs_count[0]):
                    city_list_pri.append(jobs_list[i][7])
                city_list_sec = set(city_list_pri)
                city_list = list(city_list_sec)
                city_list.sort()
            return render_template('usr_job_search_sugg.html', msg=msg, lst=lst, match_count=match_count, account=account, city_list=city_list, city=city)
        else:
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
                account = cur.fetchone()
                usr_pref_car_lvl = account[13]
                usr_pref_exp = account[8]
                cur.execute('SELECT * FROM Job WHERE Job_Car_Lvl = ? and Job_Exp = ?', (usr_pref_car_lvl, usr_pref_exp))
                match_jobs = cur.fetchall()
                con.commit()
        
            match_count=len(match_jobs)
            lst = []
            for i in range(0,match_count):
                tup = (i+1, match_jobs[i][1], match_jobs[i][2], match_jobs[i][3], match_jobs[i][4], match_jobs[i][11], match_jobs[i][5], match_jobs[i][6], match_jobs[i][7], match_jobs[i][10]) 
                lst.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8], tup[9]))

            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                city_list_pri = []
                cur.execute('SELECT * FROM Job')
                jobs_list = cur.fetchall()
                cur.execute('SELECT count(Job_ID) from Job')
                jobs_count = cur.fetchone()
                con.commit()
                for i in range(0,jobs_count[0]):
                    city_list_pri.append(jobs_list[i][7])
                city_list_sec = set(city_list_pri)
                city_list = list(city_list_sec)
                city_list.sort()
            return render_template('usr_job_search_sugg.html', msg=msg, lst=lst, match_count=match_count, account=account, city_list=city_list)    
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))


@app.route('/adm_bulk_upload', methods=['GET', 'POST'])
def adm_bulk_upload():
    if 'loggedin' in session:
        msg = ''
        error_upto = ''
        reject_list = []
        count = 0
        if request.method == 'POST' and 'bulk_file' in request.files:
            file = request.files['bulk_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_name = can_file_name(filename,"bulk_upload")
                file.save(os.path.join(UPLOAD_FOLDER, file_name))
                csv_file_name= "static/files/bulk_upload.csv"
                try:
                    with open(csv_file_name, 'r') as csv_file:
                        csvreader = csv.reader(csv_file)
                        head = next(csvreader)
                        if head[0] == 'Job ID' and head[1] == 'Position' and head[2] == 'Company' and head[3] == 'Experience' and head[4] == 'Salary' and head[5] == 'Description' and head[6] == 'Location' and head[7] == 'Type' and head[8] == 'Notification Date' and head[9] == 'Application Link' and head[10] == 'Career Level' and head[11] == 'Qualification':
                            rows = []
                            for row in csvreader:
                                rows.append(row)
                                for row in rows:
                                    job_id = row[0]
                                    job_tit = row[1]
                                    job_comp = row[2]
                                    job_exp = row[3]
                                    job_sal = row[4]
                                    job_desc = row[5]
                                    job_loc = row[6]
                                    job_type = row[7]
                                    job_not_date = row[8]
                                    job_appl_lnk = row[9]
                                    job_car_lvl = row[10]
                                    job_qual = row[11]
                        
                                with sqlite3.connect("Data_Analytics.db") as con:
                                    cur = con.cursor()
                                    cur.execute('SELECT * from Job WHERE Job_ID = ?', (job_id,))
                                    job_ava_id = cur.fetchone()
                                    if job_ava_id is None:
                                        cur.execute('INSERT INTO Job (Job_ID, Job_Tit, Job_Comp, Job_Exp, Job_Sal, Job_Des, Job_Loc, Job_Type, Job_Not_Date, Job_Appl_Link, Job_Car_Lvl, Job_Qual) values (?,?,?,?,?,?,?,?,?,?,?,?)',(job_id, job_tit, job_comp, job_exp, job_sal, job_desc, job_loc.upper(), job_type, job_not_date, job_appl_lnk, job_car_lvl, job_qual)) 
                                        con.commit()
                                        msg = 'Job Updated!'
                                    else:
                                        count+=1
                                        reject_list.append((job_id, job_tit, job_comp, job_loc))
                                        msg = 'Job Updated!, The following Jobs were rejected as they already exists in the database'
                        else:
                            msg = "The CSV file is not in proper format, Please verify!!!"
                except:
                    error_upto = "The entries starting from ", row[0], "could not be added"
                    msg = "The CSV file is not in proper format, Please verify!!!"

            else:
                msg = "The bulk update file should be in CSV format"
        
        
        return render_template("adm_bulk_upload.html", msg=msg, reject_list=reject_list, count=count, error_upto=error_upto)
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))

@app.route('/usr_sal_insights', methods=['GET', 'POST'])
def usr_sal_insights():
    if 'loggedin' in session:
        msg=''
        if request.method == 'POST' and 'city' in request.form:
            city = request.form['city']
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
                account = cur.fetchone()
                usr_pref_pos = account[12]
                usr_pref_car_lvl = account[13]
                
                cur.execute('SELECT * FROM Job WHERE Job_Tit = ? and Job_Loc = ?', (usr_pref_pos,city))
                match_jobs = cur.fetchall()

                pay = pay_calc(match_jobs)
                avg_pay = pay[0]
                max_pay = pay[1]
                min_pay = pay[2]
                
                cur.execute('SELECT * FROM Job WHERE Job_Tit = ? and Job_Sal = ? and Job_Loc = ?', (usr_pref_pos, max_pay, city))
                max_pay_job = cur.fetchall()
                
                cur.execute('SELECT * FROM Job WHERE Job_Tit = ? and Job_Sal = ? and Job_Loc = ?', (usr_pref_pos, min_pay, city))
                min_pay_job = cur.fetchall()
                
                cur.execute('SELECT * FROM Job WHERE Job_Car_Lvl = ? and Job_Loc = ?', (usr_pref_car_lvl,city))

                match_jobs_car_lvl = cur.fetchall()
                pay = pay_calc(match_jobs_car_lvl)
                avg_pay_car_lvl = pay[0]
                max_pay_car_lvl = pay[1]
                min_pay_car_lvl = pay[2]                
               
                cur.execute('SELECT * FROM Job WHERE Job_Car_Lvl = ? and Job_Sal = ? and Job_Loc = ?', (usr_pref_car_lvl, max_pay_car_lvl, city))
                max_pay_job_car_lvl = cur.fetchall()                
                
                cur.execute('SELECT * FROM Job WHERE Job_Car_Lvl = ? and Job_Sal = ? and Job_Loc = ?', (usr_pref_car_lvl, min_pay_car_lvl, city))
                min_pay_job_car_lvl = cur.fetchall()
                con.commit()
            
            match_count_max_pay=len(max_pay_job)
            lst_max_pay_job = []
            for i in range(0,match_count_max_pay):
                tup = (i+1, max_pay_job[i][1], max_pay_job[i][2], max_pay_job[i][3], max_pay_job[i][4], max_pay_job[i][5], max_pay_job[i][6], max_pay_job[i][7], max_pay_job[i][10]) 
                lst_max_pay_job.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8]))
            
            match_count_min_pay=len(min_pay_job)
            lst_min_pay_job = []
            for i in range(0,match_count_min_pay):
                tup = (i+1, min_pay_job[i][1], min_pay_job[i][2], min_pay_job[i][3], min_pay_job[i][4], min_pay_job[i][5], min_pay_job[i][6], min_pay_job[i][7], min_pay_job[i][10]) 
                lst_min_pay_job.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8]))
            
            match_count_max_pay_car_lvl=len(max_pay_job_car_lvl)
            lst_max_pay_job_car_lvl = []
            for i in range(0,match_count_max_pay_car_lvl):
                tup = (i+1, max_pay_job_car_lvl[i][1], max_pay_job_car_lvl[i][2], max_pay_job_car_lvl[i][3], max_pay_job_car_lvl[i][4], max_pay_job_car_lvl[i][5], max_pay_job_car_lvl[i][6], max_pay_job_car_lvl[i][7], max_pay_job_car_lvl[i][10]) 
                lst_max_pay_job_car_lvl.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8]))
            
            match_count_min_pay_car_lvl=len(min_pay_job_car_lvl)
            lst_min_pay_job_car_lvl = []
            for i in range(0,match_count_min_pay_car_lvl):
                tup = (i+1, min_pay_job_car_lvl[i][1], min_pay_job_car_lvl[i][2], min_pay_job_car_lvl[i][3], min_pay_job_car_lvl[i][4], min_pay_job_car_lvl[i][5], min_pay_job_car_lvl[i][6], min_pay_job_car_lvl[i][7], min_pay_job_car_lvl[i][10]) 
                lst_min_pay_job_car_lvl.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8]))
            
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                city_list_pri = []
                cur.execute('SELECT * FROM Job')
                jobs_list = cur.fetchall()
                cur.execute('SELECT count(Job_ID) from Job')
                jobs_count = cur.fetchone()
                con.commit()
                for i in range(0,jobs_count[0]):
                    city_list_pri.append(jobs_list[i][7])
                city_list_sec = set(city_list_pri)
                city_list = list(city_list_sec)
                city_list.sort()
            return render_template('usr_sal_insights.html', msg=msg, usr_pref_pos=usr_pref_pos, usr_pref_car_lvl=usr_pref_car_lvl, avg_pay=avg_pay, max_pay=max_pay, min_pay=min_pay, avg_pay_car_lvl=avg_pay_car_lvl, max_pay_car_lvl=max_pay_car_lvl, min_pay_car_lvl=min_pay_car_lvl, account=account, match_count_max_pay=match_count_max_pay, match_count_min_pay=match_count_min_pay, lst_max_pay_job=lst_max_pay_job, lst_min_pay_job=lst_min_pay_job, match_count_max_pay_car_lvl=match_count_max_pay_car_lvl, match_count_min_pay_car_lvl=match_count_min_pay_car_lvl,lst_max_pay_job_car_lvl=lst_max_pay_job_car_lvl, lst_min_pay_job_car_lvl=lst_min_pay_job_car_lvl, city_list=city_list, city=city)
        
        else:
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM User WHERE Usr_usrname = ?', (session['username'],))
                account = cur.fetchone()
                usr_pref_pos = account[12]
                usr_pref_car_lvl = account[13]
                
                cur.execute('SELECT * FROM Job WHERE Job_Tit = ?', (usr_pref_pos,))
                match_jobs = cur.fetchall()

                pay = pay_calc(match_jobs)
                avg_pay = pay[0]
                max_pay = pay[1]
                min_pay = pay[2]
                
                cur.execute('SELECT * FROM Job WHERE Job_Tit = ? and Job_Sal = ?', (usr_pref_pos, max_pay))
                max_pay_job = cur.fetchall()
                
                cur.execute('SELECT * FROM Job WHERE Job_Tit = ? and Job_Sal = ?', (usr_pref_pos, min_pay))
                min_pay_job = cur.fetchall()
                
                cur.execute('SELECT * FROM Job WHERE Job_Car_Lvl = ?', (usr_pref_car_lvl,))

                match_jobs_car_lvl = cur.fetchall()
                pay = pay_calc(match_jobs_car_lvl)
                avg_pay_car_lvl = pay[0]
                max_pay_car_lvl = pay[1]
                min_pay_car_lvl = pay[2]               
               
                cur.execute('SELECT * FROM Job WHERE Job_Car_Lvl = ? and Job_Sal = ?', (usr_pref_car_lvl, max_pay_car_lvl))
                max_pay_job_car_lvl = cur.fetchall()                
                
                cur.execute('SELECT * FROM Job WHERE Job_Car_Lvl = ? and Job_Sal = ?', (usr_pref_car_lvl, min_pay_car_lvl))
                min_pay_job_car_lvl = cur.fetchall()
                con.commit()
            
            match_count_max_pay=len(max_pay_job)
            lst_max_pay_job = []
            for i in range(0,match_count_max_pay):
                tup = (i+1, max_pay_job[i][1], max_pay_job[i][2], max_pay_job[i][3], max_pay_job[i][4], max_pay_job[i][5], max_pay_job[i][6], max_pay_job[i][7], max_pay_job[i][10]) 
                lst_max_pay_job.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8]))
            
            match_count_min_pay=len(min_pay_job)
            lst_min_pay_job = []
            for i in range(0,match_count_min_pay):
                tup = (i+1, min_pay_job[i][1], min_pay_job[i][2], min_pay_job[i][3], min_pay_job[i][4], min_pay_job[i][5], min_pay_job[i][6], min_pay_job[i][7], min_pay_job[i][10]) 
                lst_min_pay_job.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8]))
            
            match_count_max_pay_car_lvl=len(max_pay_job_car_lvl)
            lst_max_pay_job_car_lvl = []
            for i in range(0,match_count_max_pay_car_lvl):
                tup = (i+1, max_pay_job_car_lvl[i][1], max_pay_job_car_lvl[i][2], max_pay_job_car_lvl[i][3], max_pay_job_car_lvl[i][4], max_pay_job_car_lvl[i][5], max_pay_job_car_lvl[i][6], max_pay_job_car_lvl[i][7], max_pay_job_car_lvl[i][10]) 
                lst_max_pay_job_car_lvl.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8]))
            
            match_count_min_pay_car_lvl=len(min_pay_job_car_lvl)
            lst_min_pay_job_car_lvl = []
            for i in range(0,match_count_min_pay_car_lvl):
                tup = (i+1, min_pay_job_car_lvl[i][1], min_pay_job_car_lvl[i][2], min_pay_job_car_lvl[i][3], min_pay_job_car_lvl[i][4], min_pay_job_car_lvl[i][5], min_pay_job_car_lvl[i][6], min_pay_job_car_lvl[i][7], min_pay_job_car_lvl[i][10]) 
                lst_min_pay_job_car_lvl.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7], tup[8]))
                
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                city_list_pri = []
                cur.execute('SELECT * FROM Job')
                jobs_list = cur.fetchall()
                cur.execute('SELECT count(Job_ID) from Job')
                jobs_count = cur.fetchone()
                con.commit()
                for i in range(0,jobs_count[0]):
                    city_list_pri.append(jobs_list[i][7])
                city_list_sec = set(city_list_pri)
                city_list = list(city_list_sec)
                city_list.sort()
            return render_template('usr_sal_insights.html', msg=msg, usr_pref_pos=usr_pref_pos, usr_pref_car_lvl=usr_pref_car_lvl, avg_pay=avg_pay, max_pay=max_pay, min_pay=min_pay, avg_pay_car_lvl=avg_pay_car_lvl, max_pay_car_lvl=max_pay_car_lvl, min_pay_car_lvl=min_pay_car_lvl, account=account, match_count_max_pay=match_count_max_pay, match_count_min_pay=match_count_min_pay, lst_max_pay_job=lst_max_pay_job, lst_min_pay_job=lst_min_pay_job, match_count_max_pay_car_lvl=match_count_max_pay_car_lvl, match_count_min_pay_car_lvl=match_count_min_pay_car_lvl,lst_max_pay_job_car_lvl=lst_max_pay_job_car_lvl, lst_min_pay_job_car_lvl=lst_min_pay_job_car_lvl, city_list=city_list)    
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))
    
@app.route('/usr_earn_index', methods=['GET', 'POST'])
def usr_earn_index():

    if 'loggedin' in session:
        try:
            if request.method == 'POST' and 'position' in request.form:
                position = request.form['position']        
                city_list = []
                col_list = []
                sal_max_list = []
                sal_min_list = []
                sal_avg_list = []
                sal_cal = []
                job_count = []
                earning_ind = []
                earning_ind_city = []
                with sqlite3.connect("Data_Analytics.db") as con:
                    cur = con.cursor()
                    cur.execute('Select * from Job where Job_Tit = ?', (position,))
                    pos_list = cur.fetchall()
                    con.commit()
                for i in range(0,len(pos_list)):
                    city_list.append(pos_list[i][7])
                city_list = list(set(city_list))
                city_list.sort()
                with sqlite3.connect("Data_Analytics.db") as con:
                    cur = con.cursor()
                    for i in city_list:
                        cur.execute('Select Job_Sal from Job where Job_Loc = ? and Job_Tit = ?',(i,position))
                        temp = cur.fetchall()
                        job_count.append(len(temp))
                        if len(temp) > 1:
                            avg_cal = 0
                            for j in range(0,len(temp)):
                                sal_cal.append(int(temp[j][0]))
                                avg_cal+=int(temp[j][0])
                            sal_cal.sort()
                            min_pay = int(sal_cal[0])
                            max_pay = sal_cal[len(temp)-1]
                            avg_pay = avg_cal // len(temp)
                            sal_max_list.append(max_pay)
                            sal_min_list.append(min_pay)
                            sal_avg_list.append(avg_pay)
                            sal_cal = []

                        else:
                            sal_min_list.append(int(temp[0][0]))
                            sal_max_list.append(int(temp[0][0]))
                            sal_avg_list.append(int(temp[0][0]))
                        cur.execute('Select City_COL from COL where City_Name = ?',(i,))
                        temp = cur.fetchall()
                        col_list.append(temp[0][0])
                    con.commit()
            
                data = {"cities": [], "max_sal": [], "min_sal": [], "avg_sal": [], "avg_col": []}
                leng = len(city_list)
                for i in range(0,leng):
                    data["cities"] = city_list[i]
                    data["max_sal"] = sal_max_list[i]
                    data["min_sal"] = sal_min_list[i]
                    data["avg_sal"] = sal_avg_list[i]
                    data["avg_col"] = col_list[i]

                plt.figure(figsize=(15, 10))
                xpos = np.arange(len(city_list))
            
                plt.barh(xpos + 0.4, sal_max_list, height=0.2, label="Maximum Salary", color="#00bfff", edgecolor="black")
                plt.barh(xpos + 0.2, sal_avg_list, height=0.2, label="Average Salary", color="#ffff00", edgecolor="black")
                plt.barh(xpos, sal_min_list, height=0.2, label="Minimum Salary", color="#ff8000", edgecolor="black")
                plt.barh(xpos - 0.2, col_list, height=0.2, label="Average Cost of Living", color="#C0C0C0", edgecolor="black")
                plt.legend()
                plt.ylabel("Cities")
                plt.xlabel("Euros / year")
                plt.yticks(xpos, city_list)

                plt.savefig('static/' + position +'.png')
                for i in range(0,leng):
                    earning_ind_city.append(city_list[i])
                    earn_ind = round(((sal_avg_list[i] - col_list[i])/(sal_avg_list[i])),2)
                    earning_ind.append(earn_ind)
                with sqlite3.connect("Data_Analytics.db") as con:
                    cur = con.cursor()
                    cur.execute('Select * from Job')
                    all_list = cur.fetchall()
                    pos_list = []
                    for i in range(len(all_list)):
                        pos_list.append(all_list[i][2])
                    pos_list.sort()
                    con.commit()  
            
                return render_template('usr_earn_index.html', pos=position + '.png', posi=position, pos_list=list(set(pos_list)), city=earning_ind_city, ind=earning_ind, leng=leng)
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('Select * from Job')
                all_list = cur.fetchall()
                pos_list = []
                for i in range(len(all_list)):
                    pos_list.append(all_list[i][2])
                pos_list.sort()
                con.commit()        
            return render_template('usr_earn_index_ini.html', pos_list=list(set(pos_list)))
        except:
            msg='Please enter a Job Position'
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('Select * from Job')
                all_list = cur.fetchall()
                pos_list = []
                for i in range(len(all_list)):
                    pos_list.append(all_list[i][2])
                pos_list.sort()
                con.commit()   
            return render_template('usr_earn_index_ini.html', msg=msg, pos_list=list(set(pos_list)))
        
  
    else:
        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for('login'))

@app.route('/usr_reset_pass', methods=['GET', 'POST'])  
def usr_reset_pass():
    msg=""
    try:
        if request.method == 'POST' and 'username' in request.form and 'Mobile' in request.form and 'pass1' in request.form and 'pass2' in request.form:
            username = request.form['username']  
            mob = request.form['Mobile']
            new_pw_1 = request.form['pass1']
            new_pw_2 = request.form['pass2']
            with sqlite3.connect("Data_Analytics.db") as con:
                cur = con.cursor()
                cur.execute('Select * from User where Usr_usrname = ? and Usr_Mob = ?', (username, int(mob)))
                account = cur.fetchone()
                if account:
                    if new_pw_1 != new_pw_2:
                        msg = "New Passwords don't match"
                        return render_template('usr_reset_pass.html', msg=msg)  
                    else:
                        cipher_suite = Fernet(key)
                        new_pw_1_enc = cipher_suite.encrypt(new_pw_1.encode())
                        with sqlite3.connect("Data_Analytics.db") as con:
                            cur = con.cursor()
                            cur.execute('UPDATE User SET Usr_Pass = ? WHERE Usr_usrname = ?', (new_pw_1_enc, username))
                            cur.execute('UPDATE User SET Usr_cip = ? WHERE Usr_usrname = ?', (key.decode(), username))
                            con.commit()
                            msg = "Password changed Successfully!"
                else:
                    msg = "Enter valid details"
                    return render_template("usr_reset_pass.html", msg=msg)
        return render_template("usr_reset_pass.html", msg=msg)
    except:
        msg = "Enter valid details"
        return render_template("usr_reset_pass.html", msg=msg)
 
            
if __name__ == '__main__':
   app.run(debug = True, use_reloader=False)