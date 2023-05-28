from json import dumps

from flask import Flask, jsonify
from flask import flash
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask_mail import Mail
from flask_mail import Message
from datetime import datetime,timedelta
import mysql.connector
from mysql.connector import FieldType
import connect
from datetime import datetime
from datetime import date
import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'fmsreadonly@gmail.com'
# This is temporary password. This is going to be changed to environment variable.
app.config['MAIL_PASSWORD'] = 'usfhxqhpiccbwgbl'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'readonly@fms.com'
mail = Mail(app)

dbconn = None
connection = None
MAIL_DEFAULT_SENDER = 'readonly@fms.com'

# Database connection
def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


# Get current user name
def currentUserName():
    if 'loggedin' in session:
        return session['username']
    else:
        return "Guest"

# Check if user is logged in
def loggedIn():
    if 'loggedin' in session:
        return True
    else:
        return False

# Get current user role
def currentUserRole():
    if 'loggedin' in session:
        return session['role']
    else:
        return "Guest"

# Route for landing page - Default route
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# Route for member page
@app.route("/member")
def member():
    # Check if user is loggedin
    if 'loggedin' in session and (session['role'] == 'Admin' or session['role'] == 'Manager'):
        connection = getCursor()
        connection.execute("""SELECT u.user_name,u.first_name,
                                u.last_name,
                                u.date_of_birth,
                                u.street_address,
                                u.state,
                                u.postal_code,
                                u.city,
                                u.phone,
                                mt.name,
                                ms.name
                            FROM user AS u
                            LEFT JOIN user_role AS ur ON ur.user_id = u.id
                            LEFT JOIN membership AS m ON m.user_id = u.id
                            LEFT JOIN membership_type AS mt ON m.membership_type_id = mt.id
                            LEFT JOIN membership_status AS ms ON m.membership_status_id = ms.id
                            WHERE ur.role_id = 4;""")
        memberList = connection.fetchall()
        return render_template("member.html", memberlist = memberList)  
     
     # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Route for attendance page
@app.route("/attendance")
def attendance():
    # Check if user is loggedin
    if 'loggedin' in session and (session['role'] == 'Admin' or session['role'] == 'Manager'):
        connection = getCursor()
        connection.execute("""SELECT u.id,u.first_name,u.last_name,att.name,
                                a.date,TIME(a.time_start) AS time_start,TIME(a.time_end) AS time_end
                            FROM attendance AS a
                            INNER JOIN user AS u ON u.id = a.member_id
                            INNER JOIN attendance_type AS att ON att.id = a.attendance_type_id;""")
        attendancelist = connection.fetchall()
        return render_template("attendance.html", attendancelist = attendancelist)

     # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Route for training session page
@app.route("/trainingsession", methods=["POST"])
def trainingsession():
    # Check if user is loggedin
    if 'loggedin' in session and (session['role'] == 'Admin' or session['role'] == 'Manager'):
        memberid = request.form.get('memberid')
        connection = getCursor()
        connection.execute("""SELECT u.first_name,u.last_name,t.name,ut.first_name,ut.last_name,
                                t.amount,t.date,TIME(t.time_start) AS time_start,TIME(t.time_end) AS time_end
                            FROM training AS t
                            INNER JOIN training_session AS ts ON ts.training_id = t.id
                            INNER JOIN user AS u ON u.id = ts.member_id
                            INNER JOIN user AS ut ON ut.id = t.trainer_id
                            WHERE ts.member_id=%s;""", (memberid,))
        trainingsessionlist = connection.fetchall()
        return render_template("trainingsession.html", trainingsessionlist = trainingsessionlist)

     # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Route for login page
@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    # Get request - Render login page
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        user_name = request.form.get('username')
        password = request.form.get('password')
        connection = getCursor()
        connection.execute("""SELECT u.id, u.user_name, u.first_name, u.last_name, r.name
                            FROM user AS u
                            LEFT JOIN user_role AS ur ON ur.user_id = u.id
                            LEFT JOIN role AS r ON r.id = ur.role_id
                            WHERE u.user_name = %s AND u.password = %s;""", (user_name, password))
        user = connection.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            session['userfirstname'] = user[2]
            # not allow the deactivated memeber to login
            if session['role'] == 'Member':
                connection = getCursor()
                connection.execute("""SELECT is_active 
                            FROM `user_role`
                            WHERE user_id = %s;""", (session['id'], ))
                status = connection.fetchone()[0]
                if status == 0:
                    if 'loggedin' in session:
                        logout() 
                    error = 'Your membership has expired. Please contact the club to renew.'
                    return render_template("login.html", error=error)
                else:
                    return redirect("/classdetails")

            return redirect("/classdetails")
        else:
            error = 'Invalid username or password'
            return render_template("login.html", error=error)

# Rounte for view and edit user profile
@app.route('/profile')
def profile():
        # Check if user is loggedin
    if 'loggedin' in session:
        username = session['username']
        connection = getCursor()
        connection.execute("""SELECT u.first_name,
                            u.last_name,
                            u.date_of_birth,
                            u.street_address,
                            u.state,
                            u.postal_code,
                            u.city,
                            u.email,
                            u.phone,
                            u.user_name,
                            mt.name,
                            ms.name
                        FROM user AS u
                        LEFT JOIN user_role AS ur ON ur.user_id = u.id
                        LEFT JOIN membership AS m ON m.user_id = u.id
                        LEFT JOIN membership_type AS mt ON m.membership_type_id = mt.id
                        LEFT JOIN membership_status AS ms ON m.membership_status_id = ms.id
                        WHERE u.user_name = %s;""",(username,))
        memberDetail = connection.fetchone()
        return render_template("editmember.html", member = memberDetail)  
     
     # User is not loggedin redirect to login page
    return redirect(url_for('login'))
    #return redirect ("/")

# Route for logout
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('role', None)
   session.pop('userfirstname', None)
   return redirect("/")

# Route for cancel
@app.route('/cancel')
def cancel():
   # Redirect to login page
    return redirect("/") 

# For adding a new member
@app.route("/addmember", methods=["GET","POST"])
def addmember():
    # Check if user is loggedin
    if 'loggedin' in session and (session['role'] == 'Admin' or session['role'] == 'Manager'):
        # User is loggedin show them the home page
        if request.method == 'GET':
            return render_template("addmember.html")
        elif request.method == 'POST':
            first_name = request.form.get('firstname')
            last_name = request.form.get('lastname')
            date_of_birth = request.form.get('dateofbirth')
            street_address = request.form.get('streetaddress')
            state = request.form.get('state')
            postal_code = request.form.get('postalcode')
            city = request.form.get('city')
            email = request.form.get('email')
            phone = request.form.get('phone')
            user_name = request.form.get('username')
            password = request.form.get('password')
            connection = getCursor()
            try:
                # create a list of tuples containing the field name and value to check
                fields_to_check = [('user_name', user_name), ('email', email), ('phone', phone)]
                for field, value in fields_to_check:
                    connection.execute(f"SELECT user_name FROM user WHERE {field} = %s;", (value,))
                    rows = connection.fetchall()
                    if len(rows) > 0:
                         flash(f"{field.capitalize()} already exists")
                         return redirect("/member")
                else:
                    connection.execute("""INSERT INTO user 
                                (first_name, last_name, 
                                date_of_birth, street_address, state, postal_code, city, 
                                email, phone, user_name, password) 
                                VALUES(%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s);""", 
                                (first_name, last_name, 
                                    date_of_birth,street_address, state, postal_code, city, email, phone,
                                    user_name, password))
                
                    # Assign user as a member
                    connection.execute("""INSERT INTO user_role
                                    (user_id, role_id, is_active)
                                    VALUES(%s, %s, %s);""",
                                    (connection.lastrowid, 4, 1))
                
                    # Add membership to user
                    connection.execute("""INSERT INTO membership
                                    (user_id, membership_status_id, membership_type_id)
                                    VALUES(%s, %s, %s);""",
                                    (connection.lastrowid, 1, 1))
                    flash('You were successfully added new membership')
                    return redirect("/member") 
                
            except:
                flash('Something went wrong')
                return redirect("/member")
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
        

# List member details
@app.route("/memberdetails", methods=["GET","POST"])
def memberdetails():
      if request.method == 'GET':
        return render_template("member.html")
      elif request.method == 'POST': 
           username = request.form.get('memberid')   
           connection = getCursor()
           connection.execute("""SELECT u.first_name,
                            u.last_name,
                            u.date_of_birth,
                            u.street_address,
                            u.state,
                            u.postal_code,
                            u.city,
                            u.email,
                            u.phone,
                            u.user_name,
                            mt.name,
                            ms.name
                        FROM user AS u
                        LEFT JOIN user_role AS ur ON ur.user_id = u.id
                        LEFT JOIN membership AS m ON m.user_id = u.id
                        LEFT JOIN membership_type AS mt ON m.membership_type_id = mt.id
                        LEFT JOIN membership_status AS ms ON m.membership_status_id = ms.id
                        WHERE u.user_name = %s;""",(username,))
           memberDetail = connection.fetchone()
           return render_template("editmember.html", member = memberDetail) 

#update member details
@app.route("/updatemember", methods=["GET","POST"])
def updatemember():
    if request.method == 'GET':
        return render_template("editmember.html")
    elif request.method == 'POST':
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        date_of_birth = request.form.get('dateofbirth')
        street_address = request.form.get('streetaddress')
        state = request.form.get('state')
        postal_code = request.form.get('postalcode')
        city = request.form.get('city')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form.get('memberid')
 
        connection = getCursor()
        connection.execute("""UPDATE user SET
                            first_name=%s, last_name=%s, 
                            date_of_birth=%s, street_address=%s, state=%s, postal_code=%s, city=%s, 
                            email=%s, phone=%s WHERE user_name=%s;""",
                            (first_name, last_name, 
                                date_of_birth,street_address, state, postal_code, city, email, phone,
                                username,))
        print(phone)
        flash('You were successfully updated profile')
        return redirect("/") 


# For getting training details
@app.route("/training", methods=["GET", "POST"])
def training():
    trainer_id = 0
    if request.method == 'POST':
        trainer_id = request.form.get('trainer_id')

    username = session.get('username')
    connection = getCursor()
    if username:
        connection.execute("""SELECT 
                            t.id,
                            t.name,
                            CONCAT(u.first_name, ' ', u.last_name) AS trainer,
                            t.date,
                            Time(t.time_start),
                            Time(t.time_end),
                            t.amount
                        FROM training AS t
                        LEFT JOIN user AS u on u.id = t.trainer_id
                        WHERE t.id NOT IN (SELECT training_id FROM training_session AS ts 
                            LEFT JOIN user AS u ON u.id = ts.member_id 
                            WHERE u.user_name = %s) AND (t.trainer_id = %s OR %s = 0);""", (username, trainer_id, trainer_id))
    else:
        connection.execute("""SELECT 
                            t.id,
                            t.name,
                            CONCAT(u.first_name, ' ', u.last_name) AS trainer,
                            t.date,
                            Time(t.time_start),
                            Time(t.time_end),
                            t.amount
                        FROM training AS t
                        LEFT JOIN user AS u on u.id = t.trainer_id
                        WHERE (t.trainer_id = %s OR %s = 0);""", (trainer_id, trainer_id))
    programlist = connection.fetchall()

    connection.execute("""SELECT u.id,u.first_name,u.last_name FROM `user` u
                        INNER JOIN user_role ur ON ur.user_id=u.id
                        INNER JOIN role r ON r.id=ur.role_id
                        WHERE r.`name`='Trainer';""")
    trainerlist = connection.fetchall()
    result = {"programlist" : programlist, "trainerlist" : trainerlist}
    
    return render_template("training.html", result=result)


# Enrol for training
@app.route("/enroltraining", methods=["GET","POST"])
def enroltrining():
    if request.method == 'GET':
        return render_template("training.html")
    elif request.method == 'POST':
        training_id = request.form.get('trainingid')
        # TODO: Once payment portal is ready, get payment details from there and insert into trasaction table.
        cardholdername = request.form.get('cardholdername')
        cardnumber = request.form.get('cardnumber')
        expirydate = request.form.get('expirydate')
        cvc = request.form.get('cvc')
        paymentamount = request.form.get('paymentamount')
        paymentcategory = 2
        paymenttype = 1
        paymentstatus = 1
        description = "Training payment"
        username = session['username']
        connection = getCursor()
        connection.execute("""SELECT id FROM user WHERE user_name = %s;""", (username,))
        user_id = connection.fetchone()[0]
        # TODO: Check if user is already enrolled for training and is there any time conflict
        connection.execute("""INSERT INTO training_session
                            (member_id, training_id)
                            VALUES(%s, %s);""", (user_id, training_id))
        
        connection.execute("""INSERT INTO payment (member_id, payment_category_id, payment_type_id, payment_status_id, session_id, amount, description) 
                           VALUES(%s, %s, %s, %s, %s, %s, %s);""", (user_id, paymentcategory, paymenttype, paymentstatus, training_id, paymentamount, description))
        # TODO: Add payment transaction details to payment_transaction table
        # TODO: Cancel the training if payment is not successful
        flash('You were successfully enrolled for training')
        return redirect("/training")
    
# For getting my training details
@app.route("/mytraining", methods=["GET"])
def mytraining():
    username = session['username']
    connection = getCursor()
    connection.execute("""SELECT 
                            t.id,
                            t.name,
                            CONCAT(u.first_name, ' ', u.last_name) AS trainer,
                            t.date,
                            Time(t.time_start) AS time_start,
                            Time(t.time_end) As time_end,
                            t.amount
                        FROM training AS t
                        LEFT JOIN user AS u on u.id = t.trainer_id
                        WHERE t.id IN (SELECT training_id FROM training_session AS ts 
                                            LEFT JOIN user AS u ON u.id = ts.member_id 
                                            WHERE u.user_name = %s);""", (username,))
    programlist = connection.fetchall()
    return render_template("mytraining.html", programlist = programlist)

# For cancel my training
@app.route("/canceltraining", methods=["GET","POST"])
def canceltraining():
    error = None
    username = session['username']
    if request.method == 'GET':
        return render_template("mytraining.html")
    elif request.method == 'POST':
        training_id = request.form.get('trainingid')
        username = session['username']
        connection = getCursor()
        connection.execute("""SELECT id FROM user WHERE user_name = %s;""", (username,))
        user_id = connection.fetchone()[0]
        # Check payment status
        connection.execute("""SELECT payment_status_id FROM payment WHERE member_id = %s AND session_id = %s;""", (user_id, training_id))
        payment_status = connection.fetchone()
        if payment_status is not None:
            if payment_status[0] == 2:
                connection.execute("""SELECT 
                            t.id,
                            t.name,
                            CONCAT(u.first_name, ' ', u.last_name) AS trainer,
                            t.date,
                            Time(t.time_start) AS time_start,
                            Time(t.time_end) As time_end,
                            t.amount
                        FROM training AS t
                        LEFT JOIN user AS u on u.id = t.trainer_id
                        WHERE t.id IN (SELECT training_id FROM training_session AS ts 
                                            LEFT JOIN user AS u ON u.id = ts.member_id 
                                            WHERE u.user_name = %s);""", (username,))
                programlist = connection.fetchall()
                error = 'You cannot cancel training as payment is already made'
                return render_template("mytraining.html", error=error, programlist = programlist)

        # Delete training session
        print(user_id)
        print(training_id)
        connection.execute("""DELETE FROM training_session WHERE member_id = %s AND training_id = %s;""", (user_id, training_id))
        # Update payment status to cancelled
        connection.execute("""UPDATE payment SET payment_status_id = 4 WHERE member_id = %s AND session_id = %s;""", (user_id, training_id))
        flash('You were successfully cancelled training')
        return redirect("/mytraining")
 
 
# For getting class details
@app.route("/classdetails", methods=["GET"])
def classdetails():
    username = session.get('username')
    connection = getCursor()
    if username:
        connection.execute("""SELECT 
                            c.id,
                            c.name,
                            c.description,
                            c.date,
                            Time(c.time_start),
                            Time(c.time_end),
                            (c.total_capacity - (SELECT count(*) FROM booking AS b WHERE b.class_id = c.id)) AS available_capacity
                        FROM class AS c
                        WHERE c.id NOT IN (SELECT class_id FROM booking AS b 
                                            LEFT JOIN user AS u ON u.id = b.member_id 
                                            WHERE c.id = b.class_id AND u.user_name = %s);""", (username,))
    else:
        connection.execute("""SELECT 
                                c.id,
                                c.name,
                                c.description,
                                c.date,
                                Time(c.time_start),
                                Time(c.time_end),
                                (c.total_capacity - (SELECT count(*) FROM booking AS b WHERE b.class_id = c.id)) AS available_capacity
                            FROM class AS c;""")
    classlist = connection.fetchall()
    return render_template("class.html", classlist = classlist)

# Enrol class
@app.route("/enrolclass", methods=["GET","POST"])
def enrolclass():
    if request.method == 'GET':
        return render_template("class.html")
    elif request.method == 'POST':
        class_id = request.form.get('classid')
        username = session['username']
        bookingstatusid = 2
        connection = getCursor()
        connection.execute("""SELECT id FROM user WHERE user_name = %s;""", (username,))
        user_id = connection.fetchone()[0]
        connection.execute("""INSERT INTO booking (member_id, class_id, booking_status_id) VALUES(%s, %s, %s);""", (user_id, class_id, bookingstatusid))
        connection.execute("""UPDATE class SET available_capacity = available_capacity - 1 WHERE id = %s;""", (class_id,))
        # NOTE: Class enrol email to member (Recipients type 3 = Member)
        # Notification type 5 = Class cancellation
        # Notification status 1 = pending
        # Make sure notification type "Class Enrol" for member is active on conifguration page
        notification_type = 5
        recipient_type = 3
        recipient = user_id     
        createNotification(notification_type, recipient_type, recipient, 1)
        flash('You were successfully enrolled for class')
        return redirect("/classdetails")
    
# Route for my class
@app.route("/myclass", methods=["GET"])
def myclass():
    username = session['username']
    connection = getCursor()
    connection.execute("""SELECT 
                            c.id,
                            c.name,
                            c.description,
                            c.date,
                            Time(c.time_start),
                            Time(c.time_end)
                        FROM class AS c
                        WHERE c.id IN (SELECT class_id FROM booking AS b 
                                            LEFT JOIN user AS u ON u.id = b.member_id 
                                            WHERE c.id = b.class_id AND u.user_name = %s);""", (username,))
    classlist = connection.fetchall()
    return render_template("myclass.html", classlist = classlist)
    
# Rount for cancelling class
@app.route("/cancelclass", methods=["GET","POST"])
def cancelclass():
    if request.method == 'GET':
        return render_template("classdetails.html")
    elif request.method == 'POST':
        class_id = request.form.get('classid')
        username = session['username']
        connection = getCursor()
        connection.execute("""SELECT id FROM user WHERE user_name = %s;""", (username,))
        user_id = connection.fetchone()[0]
        connection.execute("""DELETE FROM booking WHERE member_id = %s AND class_id = %s;""", (user_id, class_id))
        connection.execute("""UPDATE class SET available_capacity = available_capacity + 1 WHERE id = %s;""", (class_id,))
        
        # NOTE: Class cancellation email to member (Recipients type 3 = Member)
        # Notification type 6 = Class cancellation
        # Make sure notification type "Class cancellation" for member is active on conifguration page
        notification_type = 6
        recipient_type = 3
        recipient = user_id     
        createNotification(notification_type, recipient_type, recipient, 1)
        
        flash('You were successfully cancelled class')
        return redirect("/myclass")
    
# For getting my training details
@app.route("/test", methods=["GET"])
def test():
    return render_template("test.html")
        
@app.route("/mymembership")
def mymembership():
        # Check if user is loggedin
    if 'loggedin' in session and (session['role'] == 'Member'):
        userid=session['id']
        connection = getCursor()  
        connection.execute("""SELECT date FROM membership WHERE user_id=%s;""",(userid,))
        date = connection.fetchone()
        dueDate = date[0] + timedelta(days=30)
        return render_template("membership.html", duedate = dueDate) 
    
    return redirect(url_for('login'))    

# Route for updating membership  
@app.route("/updatemembership",methods=["POST"])
def updatemembership():
        # Check if user is loggedin
    if 'loggedin' in session and (session['role'] == 'Member'):
        userid=session['id']
        print (userid)
 
        today = datetime.today()
        today = datetime.date(today)
        connection = getCursor()  
        connection.execute("""SELECT date FROM membership WHERE user_id=%s;""",(userid,))
        date = connection.fetchone()
        duedate = date[0].date()+ timedelta(days=30)
        
        #compate today's date with duedate
        if(today >= duedate):
            newdate = today
        else:
            newdate = duedate

        connection = getCursor()  
        #update date in membership table
        connection.execute("""UPDATE membership SET date=%s WHERE user_id=%s;""",(newdate,userid,))
        #update duedate
        connection.execute("""SELECT date FROM membership WHERE user_id=%s;""",(userid,))
        date = connection.fetchone()
        dueDate = date[0] + timedelta(days=30)
        
        #add payment details to payment table
        paymentcategory = 1
        paymenttype = 2
        paymentstatus = 2
        description = "Membership payment"
        paymentamount = 100
        session_id = 0
        connection.execute("""INSERT INTO payment (member_id, payment_category_id, payment_type_id, payment_status_id, amount, description,session_id) 
                           VALUES(%s, %s, %s, %s, %s,%s,%s);""", (userid, paymentcategory, paymenttype, paymentstatus, paymentamount, description,session_id,))
        flash('You successfully renew the membership')
        return render_template("membership.html", duedate = dueDate) 
        
      # User is not loggedin redirect to login page
    return redirect(url_for('membership'))     


# Rount for Manager to add a new class
@app.route("/addclass", methods=["GET", "POST"])
def addclass():
    # NOTE: No need to Check if user is admin or manager here
    # Already done it in class.html
    if request.method == 'GET':
        return render_template("addclass.html")
    elif request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        date = request.form.get('date')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        connection = getCursor()
        try:
            connection.execute("""INSERT INTO class
                                (name, description,
                                date, time_start, time_end)
                                VALUES(%s,%s,%s,%s,%s);""",
                               (name, description,
                                date, time_start, time_end))
            flash('You were successfully added a new class')
            return redirect(url_for('classdetails'))
        except:
            flash('Something went wrong')
            return redirect(url_for('classdetails'))


# Route for get list class details
@app.route("/viewclassdetails", methods=["GET", "POST"])
def viewclassdetails():
    if request.method == 'GET':
        return render_template("class.html")
    elif request.method == 'POST':
        classid = request.form.get('classid')
        connection = getCursor()
        connection.execute("""SELECT name,
                            description,
                            date,
                            time_start,
                            time_end,
                            id
                        FROM class
                        WHERE id = %s;""",
                           (classid, ))
        classinfo = connection.fetchone()
        return render_template("editclass.html", classinfo=classinfo)


# Route for update class details
@app.route("/editclass", methods=["GET", "POST"])
def editclass():
    if request.method == 'GET':
        return render_template("editclass.html")
    elif request.method == 'POST':
        classid = request.form.get('classid')
        name = request.form.get('name')
        description = request.form.get('description')
        date = request.form.get('date')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        connection = getCursor()
        connection.execute("""UPDATE class SET
                            name=%s, description=%s,
                            date=%s, time_start=%s, time_end=%s
                            WHERE id = %s;""",
                           (name, description,
                            date, time_start, time_end, classid))

        flash('You were successfully updated class')
        return redirect(url_for('classdetails'))


# For Manager to add a new training program
@app.route("/addtraining", methods=["GET", "POST"])
def addtraining():
    if request.method == 'GET':
        connection = getCursor()
        connection.execute("""SELECT u.id, CONCAT(u.first_name, ', ', u.last_name) as name FROM user_role AS ur
                                LEFT JOIN user AS u ON u.id = ur.user_id
                                WHERE ur.is_active = 1 AND ur.role_id = 3""" )
        trainersinfo = connection.fetchall()
        return render_template("addtraining.html", trainers=trainersinfo)
    elif request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        trainer_id = request.form.get('trainer_id')
        date = request.form.get('date')
        amount = request.form.get('amount')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        connection = getCursor()
        try:
            connection.execute("""INSERT INTO training
                                (name, description, trainer_id,
                                date, amount, time_start, time_end)
                                VALUES(%s,%s,%s,%s,%s,%s,%s);""",
                               (name, description, trainer_id,
                                date, amount, time_start, time_end))
            flash('You were successfully added a new trainning program')
            return redirect(url_for('training'))
        except:
            flash('Something went wrong')
            return redirect(url_for('training'))


 # List training details
@app.route("/viewtrainingdetails", methods=["GET", "POST"])
def viewtrainingdetails():
    if request.method == 'GET':
        return render_template("training.html")
    elif request.method == 'POST':
        programid = request.form.get('programid')
        connection = getCursor()
        connection.execute("""SELECT name, description, trainer_id,
                            date, amount, time_start, time_end,
                            id
                            FROM training
                            WHERE id = %s;""",
                           (programid, ))
        traininginfo = connection.fetchone()
        
        # Get trainer details
        connection = getCursor()
        connection.execute("""SELECT u.id, CONCAT(u.first_name, ', ', u.last_name) as name FROM user_role AS ur
                                LEFT JOIN user AS u ON u.id = ur.user_id
                                WHERE ur.is_active = 1 AND ur.role_id = 3""" )
        trainersinfo = connection.fetchall()
        
        return render_template("edittraining.html", training=traininginfo, trainers=trainersinfo)


# update training details
@app.route("/edittraining", methods=["GET", "POST"])
def edittraining():
    if request.method == 'GET':
        return render_template("edittraining.html")
    elif request.method == 'POST':
        programid = request.form.get('programid')
        name = request.form.get('name')
        description = request.form.get('description')
        trainer_id = request.form.get('trainer_id')
        date = request.form.get('date')
        amount = request.form.get('amount')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        connection = getCursor()
        connection.execute("""UPDATE training SET
                            name=%s, description=%s, 
                            trainer_id=%s, 
                            date=%s,amount=%s, time_start=%s, time_end=%s
                            WHERE id = %s;""",
                           (name, description, trainer_id,
                            date, amount, time_start, time_end, programid))
        flash('You were successfully updated training')
        return redirect(url_for('training'))

#view booked training details as trainer
@app.route("/managetraining")
def managetraining():
    #username = session['username']
    userid = session['id']
    connection = getCursor()
    connection.execute("""SELECT t.id,
                        t.name, CONCAT(u.first_name, ' ', u.last_name) AS trainee,
                        t.date, 
                        Time(t.time_start), 
                        Time(t.time_end), 
                        t.amount
                        FROM training_session AS ts
                        LEFT JOIN training AS t ON ts.training_id = t.id
                        LEFT JOIN user AS u ON u.id = ts.member_id
                        WHERE ts.training_id IN (SELECT training.id FROM training WHERE training.trainer_id = %s);""", (userid,))
    myTrainingList = connection.fetchall()
    return render_template("managetraining.html", mytraininglist = myTrainingList)


#add new training session as trainer
@app.route("/addtrainingsession", methods=["GET", "POST"])
def addtrainingsession():
    trainer_id = session['id']
    if request.method == 'GET':
        return render_template("addtrainingsession.html",trainerid = trainer_id)
    elif request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        #trainer_id = request.form.get('trainer_id')
        date = request.form.get('date')
        amount = request.form.get('amount')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        connection = getCursor()
        try:
            connection.execute("""INSERT INTO training
                                (name, description, trainer_id,
                                date, amount, time_start, time_end)
                                VALUES(%s,%s,%s,%s,%s,%s,%s);""",
                               (name, description, trainer_id,
                                date, amount, time_start, time_end))
            flash('You were successfully added a new trainning program')
            return redirect(url_for('managetraining'))
        except:
            flash('Something went wrong')
            return redirect(url_for('managetraining'))

#cancel training as trainer
@app.route("/canceltrainingsession", methods=["GET","POST"])
def canceltrainingsession():

    if request.method == 'GET':
        return render_template("managetraining.html")
    elif request.method == 'POST':
        training_id = request.form.get('trainingid')
        connection = getCursor()
        #delete training session
        connection.execute("""DELETE FROM training_session WHERE training_id = %s;""", (training_id,))
        connection.execute("""DELETE FROM training WHERE id = %s;""", (training_id,))
        #update payment status to refund
        connection.execute("""UPDATE payment SET payment_status_id = '4' WHERE session_id = %s;""",(training_id,))
        flash('You successfully cancelled the training, refund will be paid to trainee')
        return render_template("managetraining.html")


# Route for handlng membership status
@app.route("/Inactive")
def Inactive():
    user_name = request.args.get('memberid')
    try:
        connection = getCursor()
        connection.execute("""SELECT membership_status_id FROM membership WHERE membership.user_id=(SELECT id FROM user WHERE user_name='%s')
"""% user_name)
        status = connection.fetchone()
        if status[0] == 1:
            connection.execute("""UPDATE membership SET membership_status_id=2 WHERE membership.user_id=(SELECT id FROM user WHERE user_name='%s')"""%user_name)
            connection.execute("""UPDATE user_role SET user_role.is_active=0 WHERE user_role.user_id=(SELECT id FROM user WHERE user_name='%s')"""%user_name)
        else:
            connection.execute("""UPDATE membership SET membership_status_id=1 WHERE membership.user_id=(SELECT id FROM user WHERE user_name='%s')"""%user_name)
            connection.execute("""UPDATE user_role SET user_role.is_active=1 WHERE user_role.user_id=(SELECT id FROM user WHERE user_name='%s')"""%user_name)
        return redirect("/member")
    except Exception as e:
        return flash('Something went wrong')
    
# Route for notification config
@app.route("/notificationconfig", methods=["GET"])
def notificationconfig():
    if 'loggedin' in session and (session['role'] == 'Admin' or session['role'] == 'Manager'):
        connection = getCursor()
        # Get all notification config
        connection.execute("""SELECT
                                nt.id,
                                nt.name AS notification_type,
                                rt.name AS recipient_type,
                                st.name AS schedule_type,
                                nch.name AS notification_channel,
                                nc.is_active,
                                nc.subject,
                                nc.body,
                                nc.days
                            FROM notification_config AS nc
                            LEFT JOIN notification_type AS nt ON nt.id = nc.notification_type_id
                            LEFT JOIN recipient_type AS rt ON rt.id = nc.recipient_type_id
                            LEFT JOIN schedule_type AS st ON st.id = nc.schedule_type_id
                            LEFT JOIN notification_channel AS nch ON nch.id = nc.notification_channel_id""")
        notificationConfigList = connection.fetchall()
        
        # Get notification log
        connection.execute("""
                           SELECT 
                                nl.notification_type,
                                nl.recipient_email,
                                nl.notification_channel,
                                nl.status,
                                nl.date
                            FROM notification_log AS nl
                           """)
        notificationLogList = connection.fetchall()
        
        return render_template("notificationconfig.html", 
                               notificationconfiglist = notificationConfigList,
                               notificationloglist = notificationLogList)
        
    return render_template("index.html")

# Route for edit notification config
@app.route("/editnotificationconfig", methods=["POST"])
def editnotificationconfig():
    configid = request.form.get('configid')
    recipienttypeid = request.form.get('recipient-type')
    scheduletypeid = request.form.get('schedule-type')
    channeltypeid = request.form.get('channel-type')
    subjecttext = request.form.get('subject-text')
    bodytext = request.form.get('body-text')
    daysvalue = request.form.get('days-value')
    status = request.form.get('status')
    # Convert status to int
    if (status == '1'):
        status = 1
    else:
        status = 0
        
    # UPDATE notification config
    connection = getCursor()
    connection.execute("""UPDATE notification_config 
                            SET recipient_type_id = %s, 
                            schedule_type_id = %s, 
                            notification_channel_id = %s, 
                            subject = %s, 
                            body = %s,
                            days = %s,
                            is_active = %s
                            WHERE id = %s;""", (recipienttypeid, 
                                                scheduletypeid, 
                                                channeltypeid, 
                                                subjecttext, 
                                                bodytext,
                                                daysvalue,
                                                status, 
                                                configid))
    flash('You were successfully updated notification config')
    return redirect(url_for('notificationconfig'))

# Check given notification type for given user id is active.
def IsNotificationTypeActive(notification_type_id, recipient_id):
    connection = getCursor()
    connection.execute("""SELECT nc.is_active
                            FROM notification_config AS nc
                            LEFT JOIN notification_type AS nt ON nt.id = nc.notification_type_id
                            LEFT JOIN recipient_type AS rt ON rt.id = nc.recipient_type_id
                            WHERE nc.notification_type_id = %s AND nc.recipient_type_id = %s AND nc.is_active = 1;""", (notification_type_id, recipient_id,))
    notificationConfigList = connection.fetchall()
    if (len(notificationConfigList) > 0):
        return True
    else:
        return False
    
# Get notification channel for given notification type for given recipient type.
def GetNotificationConfig(notification_type_id, recipient_id):
    connection = getCursor()
    connection.execute("""SELECT nc.notification_channel_id, nc.schedule_type_id, nc.days, nc.subject, nc.body
                            FROM notification_config AS nc
                            LEFT JOIN notification_type AS nt ON nt.id = nc.notification_type_id
                            LEFT JOIN recipient_type AS rt ON rt.id = nc.recipient_type_id
                            WHERE nc.notification_type_id = %s AND nc.recipient_type_id = %s AND nc.is_active = 1;""", (notification_type_id, recipient_id,))
    notificationConfigList = connection.fetchall()
    if (len(notificationConfigList) > 0):
        return notificationConfigList[0]
    else:
        return 0


# Create notification
def createNotification(notification_type, recipient_type, recipient_id, notificaton_status_id):
    is_active = IsNotificationTypeActive(notification_type, recipient_type)
    if (is_active):
        config = GetNotificationConfig(notification_type, recipient_type)
        if (len(config) > 0):
            notification_channel_id = config[0]
            scheduler_type = config[1]
            days = config[2]
            subject = config[3]
            body = config[4]
            # On event
            if (scheduler_type == 1): 
                schedule_date = datetime.now()
            elif(scheduler_type == 2):
                schedule_date = datetime.now() - timedelta(days=days)
            elif(scheduler_type == 3):
                schedule_date = datetime.now() + timedelta(days=days)
                
            connection = getCursor()
            # Add notification
            connection.execute("""INSERT INTO notification (notification_type_id, recipient_id, notification_status_id, notification_channel_id, schedule_date, subject, body) 
                       values (%s, %s, %s, %s, %s, %s, %s);""", (notification_type, recipient_id, notificaton_status_id, notification_channel_id, schedule_date, subject, body))
    return True

# Trigger pending notification
def triggerNotification():
    # Get all pending notification to be sent
    pendingNorificationList = getPendingNotification()
    for x in pendingNorificationList:
        if x[3] == 1:
            # Email
            sendEmail(x[5], x[4], x[8], x[6], x[7])
        elif x[3] == 2:
            # SMS
            # sendSMS(x[2], x[4], x[5])
            print("SMS")
        elif x[3] == 3:
            # Site Notification
            sendSiteNotification(x[2], x[1])
        # Update notification status
        connection = getCursor()
        connection.execute("""UPDATE notification SET notification_status_id = 2 
                           WHERE id = %s;""", (x[0],))
    
# Send email
def sendEmail(recipient_name, recipient_email, notification_type, subject, body):
    try:
        recipients = [recipient_email]
        with app.app_context():
            msg = Message(subject, sender=MAIL_DEFAULT_SENDER, recipients=recipients)
            # TODO: Need to add email template
            formated_boby = "Hello "+ recipient_name + ",\n\n" + body + "\n\nThanks,\nFM Team"
            msg.body = formated_boby
            # TODO: Fix email template
            # msg.html = render_template("mails\cancelation.html", username=recipient_name)
            mail.send(msg)
            # create notification log entry
            logNotification(notification_type, recipient_email, "Success", "Email", "Email sent successfully")
    except Exception as e:
            logNotification(notification_type, recipient_email, "Error", "Email", e)
    
    return True

# TODO: Backend for send site notification is redy, need to implement front end.
def sendSiteNotification(recipient_id, notification_id):
    connection = getCursor()
    connection.execute("""INSERT INTO site_notification (recipient_id, notification_id) 
                       values (%s, %s);""", (recipient_id, notification_id))
    return True

# Get all pending notification to be sent
def getPendingNotification():
    connection = getCursor()
    connection.execute("""
                       SELECT
                        n.id,
                        n.notification_type_id,
                        n.recipient_id,
                        n.notification_channel_id,
                        u.email,
                        u.first_name as recipient_name,
                        n.subject,
                        n.body,
                        nt.name AS notification_type
                    FROM notification AS n 
                    LEFT JOIN user AS u ON u.id = n.recipient_id
                    LEFT JOIN notification_type AS nt ON nt.id = n.notification_type_id
                    WHERE notification_status_id = 1 AND schedule_date < %s;""", (datetime.now(),))
    pendingNotificationList = connection.fetchall()
    return pendingNotificationList

# Log notification
def logNotification(notification_type,recipient_email, status, notification_channel, description):
    connection = getCursor()
    connection.execute("""
                       INSERT INTO notification_log(notification_type, recipient_email, status, notification_channel, description)
                       values (%s, %s, %s, %s, %s);""", (notification_type,recipient_email, status, notification_channel, description))
    return True

# Scheduler job to check payment status
# Check payment transaction
def checkPayment():
    try:
        # Get all pending payment
        connection = getCursor()
        connection.execute("""SELECT session_id FROM payment WHERE payment_status_id = 1;""")
        pendingPaymentList = connection.fetchall()
        for x in pendingPaymentList:
            # Update payment status
            connection = getCursor()
            connection.execute("""UPDATE payment SET payment_status_id = 2 WHERE session_id = %s;""", (x[0],))
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))

# NOTE: Scheduler job are not working on Pythonanywhere. Need to find a solution.
# Create the background scheduler
# scheduler = BackgroundScheduler()
# Create the job
# scheduler.add_job(func=checkPayment, trigger="interval", seconds=50)
# Trigger Notification
# scheduler.add_job(func=triggerNotification, trigger="interval", seconds=15)
# Start the scheduler
# scheduler.start()

# /!\ IMPORTANT /!\ : Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())

# Scheduler workaround for Pythonanywhere
@app.route("/refresh", methods=['GET'])
def refresh():
    checkPayment()
    triggerNotification()
    print("Refreshed")
    return redirect(url_for('notificationconfig'))

# Route for report info
@app.route("/reportInfo")
def reportInfo():
    list_left = []
    list_right = []
    list_left = []
    list_right = []
    connection = getCursor()
    connection.execute("""select t2.name,t1.`人数`FROM (select membership_type_id, COUNT(*) as '人数', date FROM membership GROUP BY  membership_type_id, date) AS t1 INNER JOIN membership_type as t2 on t1.membership_type_id = t2.id""")
    res = connection.fetchall()

    for name,value in res:
        list_left.append({'value':value,'name':name})

    connection.execute("select * from (select payment_category_id,SUM(amount) as '费用' FROM payment WHERE payment_status_id <> 4 GROUP BY payment_category_id )AS T1 INNER JOIN payment_category as T2 ON T1.payment_category_id = T2.id")
    res1=connection.fetchall()

    for item in res1:
        list_right.append({'value': item[1], 'name': item[3]})
    print(list_right)

    return jsonify({'left':list_left, 'right':list_right})

# Route for report veiw
@app.route("/report")
def report():
    return render_template("financialReport.html")

# Route for popular class info
@app.route("/popularclassinfo")
def popularclassinfo():
    list_class1=[]
    list_class2=[]

    connection = getCursor()
    connection.execute("SELECT  class.name,COUNT(class_id) as selected from booking LEFT JOIN class on class.id=booking.class_id group by class_id ORDER BY COUNT(class_id) desc limit 5")
    res3 = connection.fetchall()
    for item in res3:
        list_class1.append(item[0])
        list_class2.append(item[1])

    connection.execute("SELECT  class.name,COUNT(class_id) as selected from booking LEFT JOIN class on class.id=booking.class_id group by class_id ORDER BY COUNT(class_id)  limit 5")
    list_class_unpopular1 = []
    list_class2_unpopular2 = []
    res4=connection.fetchall()
    for item in res4:
        list_class_unpopular1.append(item[0])
        list_class2_unpopular2.append(item[1])

    return jsonify({'left1': list_class1,'left2': list_class2,'right1':list_class_unpopular1,'right2':list_class2_unpopular2})

# Route for popular class view
@app.route("/popularclass")
def popularclass():
    return render_template("popularclass.html")

# Get payments
@app.route("/payment")
def payments():
    connection = getCursor()
    connection.execute("""
                       SELECT 
                        CONCAT(u.first_name, ' ', u.last_name) AS user_name,
                        pt.name AS payment_type,
                        pc.name AS payment_category,
                        p.description,
                        ps.name AS payment_status,
                        p.date
                    FROM payment AS p
                    LEFT JOIN payment_type AS pt ON pt.id = p.payment_type_id
                    LEFT JOIN user AS u ON u.id = p.member_id
                    LEFT JOIN payment_category AS pc ON pc.id = p.payment_category_id
                    LEFT JOIN payment_status AS ps ON ps.id = p.payment_status_id
                       """)
    payments = connection.fetchall()
    return render_template("payment.html", payments=payments)

# Route for visitor request.
@app.route('/contact', methods=["GET", "POST"])
def contact():
    # Get form data
    name = request.form['qa_name']
    email = request.form['qa_email']
    subject = request.form['qa_subject']
    message = request.form['qa_message']

    # Create email message
    msg = Message(subject, recipients=['fmsreadonly@gmail.com'] )
    msg.body = f"Name: {name}\nEmail: {email}\n\n{message}"
    print(msg.body)

    try:
        # Send email
        mail.send(msg)
        flash('Thank you for your message. We will get back to you soon!')
    except Exception as e:
        # Show error message
        flash('An error occurred while sending your message. Please try again later.')

    return render_template('index.html')

# Route for delete group class
@app.route("/deletegroupclass", methods=["GET", "POST"])
def deletegroupclass():
    if request.method == 'GET':
        return redirect(url_for('classdetails'))
    else:
        classid = request.form.get('classid')
        print(classid)
        try:
            connection = getCursor()
            connection.execute("""DELETE FROM class 
                            WHERE id = %s;""",
                           (classid, ))
            flash('You were successfully deleted the group class')
            return redirect(url_for('classdetails'))
        except Exception as e:
            return flash('Something went wrong')

# Route for delete personal training
@app.route("/deletepersonaltraining", methods=["GET", "POST"])
def deletepersonaltraining():
    if request.method == 'GET':
        return redirect(url_for('training'))
    else:
        programid = request.form.get('programid')
        try:
            connection = getCursor()
            connection.execute("""DELETE FROM training 
                            WHERE id = %s;""",
                           (programid, ))
            flash('You were successfully deleted the personal training')
            return redirect(url_for('training'))
        except Exception as e:
            return flash('Something went wrong')

# NOTE: Local debuging only
if __name__ == "__main__":
    app.run(debug=True)