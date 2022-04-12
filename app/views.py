"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
from audioop import avg
import os
from app import app, db
from app.models import Guarantor, SignUpProfile, GraphicalAnalytics, LoanPrioritization, LoanApplication, Payment, Img
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory, Response
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.forms import *
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import uuid as uuid



# ##
# Routing for your application.
# ##
# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     passwd="",
#     db="dev_techzen_db"
# )

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD']= ''
# app.config['MYSQL_DB'] = 'dev_techzen_db'

# mysql = MySQL(app)

mysql = MySQL(app)


@app.route('/home')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="TechZen")

@app.route('/payment', methods=['POST', 'GET'])
def payment():
    """Render the website's payment."""
    paymentform =PaymentForm()
    # Validate file upload on submit
    if request.method == 'POST' and paymentform.validate_on_submit():
        
        payment = Payment( 
            sid = paymentform.sid.data,
            loanid = paymentform.loanid.data,
            payment_amount= paymentform.paymentamount.data,
            payment_date= paymentform.paymentdate.data,
            paymentid= paymentform.paymentid.data
        )
        
        db.session.add(payment)

        db.session.commit()
        flash('added payment')
       
        flash('File Saved', 'success')
        return redirect(url_for('home'))
    
    return render_template('payment.html', form=paymentform)

def average(lst):
    return sum(lst) / len(lst)

@app.route('/dashboard')
def dashboard():
    
    #this works
    currentsid = '12345'
    # grabs the payment data
    paymentlist = []
    foundvalue = Payment.query.all()
    loandetails = GraphicalAnalytics.query.all()
    #iterates through the list and appends payment number
    for x in foundvalue:
        if x.sid == currentsid:
            paymentlist.append(x.payment_amount)
    
    # Averages payment so we can tell how much paid monthly
    avgpayment = average(paymentlist)
    print("avg pay =", int(avgpayment))
    
    # if avgpayment is below the minimum payback, the minimum payback value is used
    # This is because, if the value is below the interest, then there will be no progress made
    # towards paying off the loan. The minimum value in this case, is the interest accrued, + 5000 for good measure.
    overallloan= loandetails[0].loanamount
    minimumpayback = (overallloan * 0.06) + 5000
    print("minimum payback is: ", minimumpayback)

    if avgpayment < minimumpayback:
        avgpayment = minimumpayback
        
    print(paymentlist)
    
    print(loandetails[0].interestrate / 100)
    # user = SignUpProfile.query.filter_by(username=username).first()
    
    # avgpay is equal to the average payment made.
    avgpay = avgpayment
    temploanamount = overallloan
    loanpay = []
    days = []
    i = 0
    interestrate = loandetails[0].interestrate / 100
    interest = 0
    interestprojection = []

    while (temploanamount-avgpay) > 0:
        i += 1
        loanpay.append(temploanamount-avgpay)
        days.append("Day " + str(i))
        temploanamount = temploanamount-avgpay
        interest = temploanamount * interestrate
        temploanamount = temploanamount + interest
        interestprojection.append(interest) 
        
        
    if (temploanamount-avgpay) < 0:
            temploanamount = temploanamount - temploanamount
            loanpay.append(0)
            days.append("Day " + str(i+1))     
            
    chartvalue = [0, 5000,6000, 7000]
    
    return render_template('dashboard.html', paymentval=foundvalue, paymentlst=json.dumps(paymentlist), values = json.dumps(chartvalue), overall=json.dumps(overallloan), loanpay=json.dumps(loanpay), days=json.dumps(days), interest=json.dumps(interestprojection))
    
@app.route('/register', methods=['POST', 'GET'])
def register():
    # if not session.get('logged_in'):
    #     abort(401)

    # Instantiate your form class
    registerform=SignUpForm()
    # Validate file upload on submit
    if request.method == 'POST' and registerform.validate_on_submit():
        # my_cursor = mysql.connection.cursor()
        
        # fname = request.form['fname']
        # lname = request.form['lname']
        # username = request.form['username']
        # email = request.form['email']
        # password = request.form['password']
        # print(fname)
        # print(email)
        
        signup = SignUpProfile( 
            first_name = registerform.fname.data,
            last_name = registerform.lname.data,
            username = registerform.username.data,
            email = registerform.email.data,
            password = registerform.password.data
        )
        
        db.session.add(signup)
        print(signup)
        db.session.commit()
        flash('added')
        # my_cursor.execute('''INSERT INTO studentssignup VALUES(%s,%s,%s,%s,%s)''', (fname,lname,username,email,password))
        # mysql.connection.commmit()
        # my_cursor.close()        
        # Get file data and save to your uploads folder
        # filename=secure_filename(photo.filename)
        # photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('File Saved', 'success')
        return redirect(url_for('home'))

    return render_template('signup.html', form=registerform)

@app.route('/apply', methods=['POST', 'GET'])
def loanApplication():
    # if not session.get('logged_in'):
    #     abort(401)

    # Instantiate your form class
    applicationform=LoanApplicationForm()
    # Validate file upload on submit
    if request.method == 'POST' :
        # Get file data and save to your uploads folder
        photo = applicationform.photo.data
        photo2 = applicationform.selfie.data
        sid = applicationform.sid.data
        root_dir = os.getcwd()

        filename = str(sid) + "_A_" + secure_filename(photo.filename)
        photo.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename
        ))
        print(filename)
        
        filename2 = str(sid) + "_B_" + secure_filename(photo2.filename)
        photo2.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename2
        ))
        
        loanapplication = LoanApplication( 
            first_name = applicationform.fname.data,
            last_name = applicationform.lname.data,
            sex = applicationform.sex.data,
            phonenumber= applicationform.phone.data,
            sid = applicationform.sid.data,
            trn = applicationform.trn.data,
            address = applicationform.address.data,
            email = applicationform.email.data,
            photo= filename

        )
        
        
        # API Call


        # url = "https://face-verification2.p.rapidapi.com/FaceVerification"

        # payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"{os.path.join(root_dir, './uploads/') + filename}\"\r\n\r\n\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"{os.path.join(root_dir, './uploads/') + filename}\"\r\n\r\n\r\n-----011000010111000001101001--\r\n\r\n"
        # headers = {
        #     "content-type": "multipart/form-data; boundary=---011000010111000001101001",
        #     "X-RapidAPI-Host": "face-verification2.p.rapidapi.com",
        #     "X-RapidAPI-Key": "198bff86e4msh4cfe80801440c7ep1c1779jsn9a870a2e8dbe"
        # }

        # response = requests.request("POST", url, data=payload, headers=headers)

        # print(response.text)
        
        
        
        # api_url = 'https://face-verification2.p.rapidapi.com/FaceVerification'
        # api_key = '198bff86e4msh4cfe80801440c7ep1c1779jsn9a870a2e8dbe'
        
        # root_dir = os.getcwd()
        # image1_path =  os.path.join(root_dir, './uploads/')
        # image1_name = filename
        # image2_path = os.path.join(root_dir, './uploads/')
        # image2_name = filename2

        # files = {'Photo1': (image1_name, open(image1_path + image1_name, 'rb'), 'multipart/form-data'), 
        #         'Photo2': (image2_name, open(image2_path + image2_name, 'rb'), 'multipart/form-data')}
        # header = {
        #     "x-rapidapi-host": "face-recognition4.p.rapidapi.com",
        #     "x-rapidapi-key": api_key
        # }
        # response = requests.post(api_url, files=files, headers=header)
        # print(response.text)
                
        
        db.session.add(loanapplication)
        db.session.commit()
        flash('added loan application')

        flash('File Saved', 'success')
        return redirect(url_for('home'))

    return render_template('loanapplication.html', form=applicationform)


    
    
@app.route('/guarantor', methods=['POST', 'GET'])
def guarantorForm():
    # if not session.get('logged_in'):
    #     abort(401)

    # Instantiate your form class
    guarantorform= GuarantorForm()
    # Validate file upload on submit
    if request.method == 'POST' and guarantorform.validate_on_submit():
        guarantor = Guarantor( 
            first_name = guarantorform.gfname.data,
            last_name = guarantorform.glname.data,
            guarantor_occupation = guarantorform.goccupation.data, 
            guarantor_phonenumber = guarantorform.gphone.data,
            guarantor_salary = guarantorform.gsalary.data,
            guarantor_address = guarantorform.gaddress.data,
            loanid = guarantorform.loanid.data,
            sid = guarantorform.sid.data
        )
        
        db.session.add(guarantor)
        print(guarantor)
        db.session.commit()
        
        
        flash('Form Completed', 'success')
        return redirect(url_for('home'))

    return render_template('guarantorform.html', form=guarantorform)




@app.route('/graphicalanalyticsform', methods=['POST', 'GET'])
def graphicalAnalytics():
  
    # day 1 principal = 5000
    # day 2 principal = 2000
    

    # Instantiate your form class
    graphicalanalyticsform= GraphicalAnalyticsForm()

    if request.method == 'POST' and graphicalanalyticsform.validate_on_submit():
       
        graphicalanalytics = GraphicalAnalytics( 
            loanid = graphicalanalyticsform.loanid.data,
            loanamount = graphicalanalyticsform.loanamount.data,
            interestrate = graphicalanalyticsform.interestrate.data,
            sid = graphicalanalyticsform.sid.data
            
        )
        
        # Error here, new rows in database, need to migrate.
                
        db.session.add(graphicalanalytics)
        print(graphicalanalytics)
        db.session.commit()
        flash('added')
        
        flash('File Saved', 'success')
        return redirect(url_for('home'))

    return render_template('graphicalanalyticsform.html', form=graphicalanalyticsform)


@app.route('/loananalyticsprioritizerform', methods=['POST', 'GET'])
def loanAnalyticsPrioritizer():
  

    # Instantiate your form class
    loananalyticsprioritizerform=LoanAnalyticsPrioritizerForm()

    if request.method == 'POST' and loananalyticsprioritizerform.validate_on_submit():
       
        loananalyticsprioritizer = LoanPrioritization( 
            loanid = loananalyticsprioritizerform.loanid.data,
            priority_id = loananalyticsprioritizerform.priorityid.data,
            interest= loananalyticsprioritizerform.interest.data
        )
        
        # Error here, new rows in database, need to migrate.
        
        db.session.add(loananalyticsprioritizer)
        print(loananalyticsprioritizer)
        db.session.commit()
        flash('added')
        
        flash('File Saved', 'success')
        return redirect(url_for('home'))

    return render_template('loananalyticsprioritizerform.html', form=loananalyticsprioritizerform)





def get_uploaded_file():
    rootdir = os.getcwd()
    upload_files=[]
    for subdir, dirs, files in os.walk(rootdir + '/uploads'):    
        for file in files:
            upload_files.append(file)
    upload_files.pop(0)     
    return upload_files


@app.route('/uploads/<filename>')
def get_image(filename):
    root_dir = os.getcwd()
    return send_from_directory(os.path.join(root_dir, app.config['UPLOAD_FOLDER']), filename)


@app.route('/files')
def files():
    imgs=get_uploaded_file()
    return render_template('files.html', imgs=imgs)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None

    if request.method == 'POST':
        
        if request.form['username']:
            username = request.form['username']
            password = request.form['password']
            
            user = SignUpProfile.query.filter_by(username=username).first()
            if user is not None and check_password_hash(user.password, password):
                session['logged_in'] = True
                flash('Successfully logged in', 'success')
                return redirect(url_for('home'))
            
            
            else:
                error = 'Invalid username or password'
                flash(error)
                
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'success')
    return redirect(url_for('home'))


###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('home.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")