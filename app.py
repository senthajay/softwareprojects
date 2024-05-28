#import required modules(libraries) for the application
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 

####################################
import random

############
import pandas as pd
import numpy as np 
##################
import os
import secrets
from PIL import Image
        
from flask import url_for, current_app
from flask import session
from werkzeug.utils import secure_filename

############################################
import smtplib
from email.mime.text import MIMEText
#######################################
import plotly.graph_objs as chart
from plotly.subplots import make_subplots
import plotly.express as plotex
from datetime import datetime
###################################################
import stripe


#creation of flask app
app = Flask(__name__)
stripe.api_key = "sk_test_51N15rvFxgziGaiKJd6UxvlxXWcS9C3mXsoLx65LGUqcx0UYCoVJQtogwKsEBZHQDs8o3WsmBWUuWeiFkbMVQcxpt00wnXXKOWo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newhome.db'
db = SQLAlchemy(app)
app.secret_key = 'my_secret_key'#enterr your secret key


#############################################

PROFILE_FOLDER = 'C:/Users/SENTHA.JAY/Desktop/newhomes_choices_extras_mangmt/static/images/profile_pics'
PROPERTY_FOLDER ='C:/Users/SENTHA.JAY/Desktop/newhomes_choices_extras_mangmt/static/images/property_pics'
PRODUCTS_FOLDER ='C:/Users/SENTHA.JAY/Desktop/newhomes_choices_extras_mangmt/static/images/products_pics'
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}

#function to check the whether the file extensions allowed.
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
#################################################
def save_user_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images/profile_pics', picture_fn)

    output_size = (512,512)
    i = Image.open(form_picture)
    i.resize(output_size)
    i.save(picture_path)

    return picture_fn

def save_house_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)

    output_size = (512,512)
    i = Image.open(form_picture)
    i.resize(output_size)
    i.save(picture_path)

    return picture_fn

############################################
# Creating database models
class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    paymentstatus = db.Column(db.Integer, nullable=True)
    property_alloc = db.relationship('Property', backref='buyer', lazy=True)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    property_pic = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Integer, nullable=True)
    estimated=db.Column(db.Integer,nullable=True)
    property_add_date = db.Column(db.Date,nullable=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id'), nullable=False)


class product_builder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50), nullable=False)
    category_home = db.Column(db.String(50), nullable=False)
    category_sub_home = db.Column(db.String(50), nullable=False)
    category_choice_extra = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    product_pic = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class product_buyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50), nullable=False)
    category_home = db.Column(db.String(50), nullable=False)
    category_sub_home = db.Column(db.String(50), nullable=False)
    category_choice_extra = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    product_pic = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    messagecustom = db.Column(db.String(250), nullable=True)
    product_add_date = db.Column(db.Date,nullable=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id'), nullable=False)
    
@app.route('/create_db')
def create_db():
    with app.app_context():
        db.create_all()
    return 'database tables created !'

#setting routes for web
#home route
@app.route('/')
def home():
    return redirect(url_for('login'))
    return render_template('home.html')   
#############################################
#login route
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        buyer = Buyer.query.filter_by(email=email, password=password).first()
        if buyer:
            print(buyer,"if buyer loop")
            #return redirect(url_for('dashboard', buyer_id=buyer.id))
            #otp Generated to the buyer email:
            global otp
            otp = random.randint(100000,999999)
            #sendemail
            fromaddr="info@booknewhome.co.uk"
            smtp_server="smtp.hostinger.com"
            port=465
            m=f'Your OTP for Login is {otp}.'
            msg = MIMEText(m)
            msg['Subject'] = "ONE TIME PASSWORD(OTP Login)"
            msg['From'] = fromaddr
            msg['To'] = buyer.email
            session=smtplib.SMTP_SSL(smtp_server,port)
            session.login("info@booknewhome.co.uk","Qwer123$")
            session.sendmail(fromaddr,buyer.email,msg.as_string())
            session.quit()
            # redirect 
            return render_template('verify_otp.html',id=buyer.id,email=buyer.email)
       
            
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')
    
##################################Verify OTP ###################
@app.route('/verify_otp',methods=['POST'])
def verify_otp():
    buyerid=request.form['buyerid']
    email = request.form['email']
    otpb = int(request.form['otp'])
    print(otpb,otp)
    buyer = Buyer.query.filter_by(email=email).first()
    if request.method =='POST':
        if int(otpb) == otp:
            #to verify seddion log in buyer
            session['logged_in'] = True
            session['email'] = email

            #redirect to dashboard
            return redirect(url_for('dashboard', buyer_id=buyerid))
        else:
            return redirect(url_for('verify_otp', error='Invalid OTP' ))
    else:
        return render_template('verify_otp.html')
################################VERIFY OTP ENDS#################


##################################
#set logout route
@app.route('/logout')
def logout():
    session.clear()

    return redirect(url_for('login'))
################################################################################
#set register route
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        
        if 'profile_picture' not in request.files:
            return 'No file Part'

        profile_picture = request.files['profile_picture']

     ###############################
        # profile pic logic ###
        if profile_picture.filename =='':
            return 'No selected file'

        if profile_picture and allowed_file(profile_picture.filename):
            filename = profile_picture.filename
            profile_pic="images/profile_pics/"+filename
            profile_picture.save(os.path.join(PROFILE_FOLDER, filename))
        
        buyer = Buyer(fname=fname, lname=lname, email=email, password=password, profile_pic=profile_pic, phone=phone, address=address)
        db.session.add(buyer)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

###########################
#####################################BUYERS DASHBOARD STARTS###################################################
# buyers dashboard
@app.route('/dashboard/<int:buyer_id>')
def dashboard(buyer_id):

    choices = []
    extras = []
    buyer = Buyer.query.get(buyer_id)
    properties = Property.query.filter_by(buyer_id=buyer_id).all()
    products_buyer = product_buyer.query.filter_by(buyer_id=buyer_id).all()
    
    
    type_home = None
    for propertyy in properties:
        type_home=propertyy.category
    print("home type",type_home)
   

    products = product_builder.query.all()
    #products = product_builder.query.filter_by().all()
    for product in products:
        if product.category_choice_extra =="choice":
            choices.append(product)
        else:
            extras.append(product)

    for choice in choices:

        print(choice.id, choice.product_name, choice.category_home, choice.category_sub_home, choice.category_choice_extra, choice.price, choice.product_pic, choice.stock)
    return render_template('dashboard.html', buyer=buyer, properties=properties,products=products,choices=choices, extras=extras,type_home=type_home,products_buyer=products_buyer )


    
    return render_template('dashboard.html',buyer_id=buyer.id)

#########################################################BUYERS DASHBOARD ENDS####################################

##################################custom message 
@app.route('/custome_message/<int:buyerid>', methods=['GET','POST'])
def custome_message(buyerid):
    buyer = Buyer.query.get(buyerid)
    productbuyer = product_buyer.query.filter_by(buyer_id=buyerid).first()
    if request.method=='POST':
        message = request.form['message']


        productbuyer.messagecustom=message
        print(productbuyer.messagecustom)

        db.session.commit()
    
        return redirect(url_for('dashboard', buyer_id=buyerid))
    return render_template('dashboard.html',buyer_id=buyer.id,buyer=buyer)
#############################################CUSTOMIZED MESSAGE BOX(ENDS)############   
    
###########################################SMART TOOLS STARTS ################################################
#set route for smart tools
@app.route('/smart_tools/<int:buyerid>', methods=['GET','POST'])
def smart_tools(buyerid):
    buyer = Buyer.query.get(buyerid)
    print(buyerid)
    properties = Property.query.filter_by(buyer_id=buyerid).first()
    print(properties.price)
    print(properties.category)
    #print(properties)    
    #print(properties.estimated)     

    return render_template('smart_tools.html',properties=properties)

#############################Smart TOOL 1  COST PLANNER ####################
#Cost planner route 
@app.route('/costplan', methods=['GET','POST'])
def costplan():
    total_cost=0
    if request.method=='POST':
        deposit = int(request.form['deposit'])
        moving_expense = int(request.form['moving_expense'])
        stamp_duty = int(request.form['stamp_duty'])
        council_tax = int(request.form['council_tax'])
        solicitor_fee = int(request.form['solicitor_fee'])
        validation_fee = int(request.form['validation_fee'])
        surveyor_fee = int(request.form['surveyor_fee'])
       
         # int conversion
        total_cost = int(deposit) + int(moving_expense)  + int(stamp_duty) + int(council_tax) + int(solicitor_fee)+ int(validation_fee) + int(surveyor_fee)
    
        return render_template('costplan.html', total_cost=total_cost)
    return render_template('costplan.html', total_cost=total_cost)

##################################################
#############MORTGAGE CALCULATOR########
@app.route('/mortgage_cal', methods=['GET','POST'])
def mortgage_cal():
    mortgage_payment=0
    maxafford = 0
    chart_html=''
    if request.method == 'POST':
        price = float(request.form['price'])
        initialamt = float(request.form['initialamt'])
        salary = float(request.form['salary'])
        loan = price - initialamt
        interest_rate = float(request.form['interest_rate']) / 100 / 12
        years = int(request.form['years']) * 12
        mortgage_payment = (loan * interest_rate * (1 + interest_rate) ** years) / ((1 + interest_rate) ** years - 1)
        #pie chart
        
        display = chart.Figure(data=[chart.Pie(labels=['price','salary','interest_rate','mortgage_payment'],values=[price,salary,mortgage_payment*years - price, mortgage_payment],hole=.6)])
        #display = chart.Figure(data=[chart.Scatter(x=['price','salary','interest_rate','mortgage_payment','maxafford'],y=[price,salary,mortgage_payment*years - price, mortgage_payment,salary*0.28])])
        
        #chart to html
        chart_html = display.to_html(full_html=False, include_plotlyjs='cdn')

        maxafford = salary*0.28
        if mortgage_payment <= maxafford:
            print("afforadble")
        else:
            print("not affordable")
        
    
        return render_template('mortgage_cal.html', mortgage_payment=mortgage_payment,maxafford=maxafford, chart_html=chart_html )
    return render_template('mortgage_cal.html', mortgage_payment=mortgage_payment,maxafford=maxafford, chart_html=chart_html)
##################################  MORTGAGE CALCULATOR ENDS ##############################
   
############################################   EDIT MY INFO ( BUYERS DASHBORAD ) STARTS #####################################
#set route edit_my_info
@app.route('/edit_my_info', methods=['GET','POST'])
def edit_my_info():
    
    email = None
    if request.method =='POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        if 'profile_picture' not in request.files:
            return 'No such file Part exist'

        profile_picture = request.files['profile_picture']

     ###############################
        # profile pic logic ###
        if profile_picture.filename =='':
            return 'No profile pic selected, please choose one to continue !'

        if profile_picture and allowed_file(profile_picture.filename):
            filename = profile_picture.filename
            profile_pic="images/profile_pics/"+filename
            profile_picture.save(os.path.join(PROFILE_FOLDER, filename))

        # info udpate logic 
        
        buyer = Buyer.query.filter_by(email=email).first()
        if buyer:
            buyer.fname = fname
            buyer.lname = lname
            buyer.phone = phone
            buyer.address = address
            buyer.profile_pic = profile_pic
        db.session.commit()
        
        return redirect(url_for('dashboard', buyer_id=buyer.id))
    else:
        buyer = Buyer.query.filter_by(email=email).first()
        return render_template('edit_my_info.html')
    
        
    return render_template('edit_my_info.html')
######################################################### EDIT MY INFO (BUYERS DASHBOARD ENDS ) ##############################


####################################################### CHANGE PASSWORD STARTS ######################################
#set route for change password 
@app.route('/change_password', methods=['GET','POST'])
def change_password():
    password = "current_password"
    if request.method =='POST':
        email = request.form['email']
        password= request.form['password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if  password == password and new_password == confirm_password:
            

            buyer = Buyer.query.filter_by(email = email).first()
            if buyer:
                buyer.password = new_password
                db.session.commit()

                return redirect(url_for('dashboard',buyer_id=buyer.id))
        else:
            buyer = Buyer.query.filter_by(email = email).first()
            return render_template('change_password.html')
    return render_template('change_password.html')
##################################################### CHANGE PASSWORD ENDS ###########################################

##################################################### BUILDER'S LOGIN STARTS#################################################
#set route for builder login
@app.route('/builder_login', methods=['GET','POST'])
def builder_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'builder' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('builder_dashboard'))
        else:
            return render_template('builder_login.html', error='invalid username or password')
    return render_template('builder_login.html')

##################################################################BUILDER'S LOGIN ENDS###########################################


###########################################################BUILDERS DASHBOARD STARTS #########################################
#builder dashboard route
@app.route('/builder_dashboard', methods=['GET','POST'])
def builder_dashboard():
    buyers = Buyer.query.all()
    cproperties = Property.query.all()
    properties = Property.query.all()
    if not session.get('logged_in'):
        return redirect(url_for('builder_login'))
    if request.method == 'POST':
        buyer_id =1
        #buyer_id = request.form['buyer_id']
        category=request.form['category']
        buyer = Buyer.query.get(buyer_id)
        buyer1 = db.session.query(Buyer).filter_by(id=buyer_id).first()
        property_of_buyer = Property.query.filter_by(buyer_id=buyer_id).all()
        buyer_products = product_buyer.query.filter_by(buyer_id=buyer_id).all()
        propertiesby_category = Property.query.filter_by(category=category).all()
        return render_template('builder_dashboard.html',username=buyer1.fname, properties=property_of_buyer,buyers=buyers, buyer_products=buyer_products,propertiesby_category=propertiesby_category)
    return render_template('builder_dashboard.html', buyers=buyers,cproperties=cproperties)
##################################################################BUILDER DASHBOARD ENDS #############################


######################################################BUILDERS USER DASHBOARD STARTS ########################
#builder User dashboard route
@app.route('/builder_user_dashboard', methods=['GET','POST'])
def builder_user_dashboard():
    buyer=''

    buyers = Buyer.query.all()
    print(buyers)
    properties = Property.query.all()
    if not session.get('logged_in'):
        return redirect(url_for('builder_login'))
    if request.method == 'POST':
        buyer_id = request.form['buyer_id']
        buyer = Buyer.query.get(buyer_id)
        buyer1 = db.session.query(Buyer).filter_by(id=buyer_id).first()
        property_of_buyer = Property.query.filter_by(buyer_id=buyer_id).all()
        buyer_products = product_buyer.query.filter_by(buyer_id=buyer_id).all()
        buyer_products_m = product_buyer.query.filter_by(buyer_id=buyer_id).first()
        return render_template('builder_user_dashboard.html',username=buyer1.fname,lname=buyer1.lname,email=buyer1.email,phone=buyer1.phone,address=buyer1.address,profile_pics=buyer1.profile_pic,properties=property_of_buyer,buyers=buyers, buyer_products=buyer_products,buyer_invoice=buyer1.id,buyer_payment=buyer1.id, buyer_products_mes=buyer_products_m.messagecustom )
    return render_template('builder_user_dashboard.html', buyers=buyers)
    #########################################      BUILDERS USER DASHBOARD ENDS     ######################################


##############################################BUILDERS PROPERTY DASHBOARD (View & Assign) STARTS #########################################
#builder property dashboard route
@app.route('/builder_property_dashboard', methods=['GET','POST'])
def builder_property_dashboard():
    
    buyers = Buyer.query.all()    
    cproperties = Property.query.all()
    properties = Property.query.all()
    if not session.get('logged_in'):
        return redirect(url_for('builder_login'))
    if request.method == 'POST':
        category=request.form['category']
        propertiesby_category = Property.query.filter_by(category=category).all()
        print(propertiesby_category)
        
        return render_template('builder_property_dashboard.html',propertiesby_category=propertiesby_category,buyers=buyers)
    return render_template('builder_property_dashboard.html',buyers=buyers,cproperties=cproperties)
######################################################## Builder Property dasboard end########################################


###########################################BUILDERS PRODUCT DASHBOARD STARTS (VIEW & ASSIGN ) ##############################
#builder product dashboard route
@app.route('/builder_product_dashboard', methods=['GET','POST'])
def builder_product_dashboard():
    category_choice_extra='None'
    #buyers = Buyer.query.all()    
    cproperties = Property.query.all()
    products_category = product_builder.query.all()
    if not session.get('logged_in'):
        return redirect(url_for('builder_login'))
    if request.method == 'POST':
        #buyer_id =1
        #buyer_id = request.form['buyer_id']
        category_choice_extra=request.form['category_choice_extra']
        print(category_choice_extra)
        #buyer = Buyer.query.get(buyer_id)
        #buyer1 = db.session.query(Buyer).filter_by(id=buyer_id).first()
        #property_of_buyer = Property.query.filter_by(buyer_id=buyer_id).all()
        #buyer_products = product_buyer.query.filter_by(buyer_id=buyer_id).all()
        products_category = product_builder.query.filter_by(category_choice_extra=category_choice_extra).all()
        print(products_category)
        #productby_category = Property.query.filter_by(category_choice_extra=category_choice_extra).all()
        
    return render_template('builder_product_dashboard.html',products_category=products_category,type=category_choice_extra)
###############################################Builder Product dasboard (View & assign) end############################################

#####################################EDIT PRODUCT (for price edit) STARTS########
@app.route('/edit_product', methods=['GET', 'POST'])
def edit_product():
    id="None"
    if request.method == 'POST':
        product_name = request.form['product_name']
        price = request.form['price']
        id = request.form['id']
        #edit product price logic 
        edit_prod = product_builder.query.filter_by(id=id).first()
        if edit_prod:
            edit_prod.price = price
            edit_prod.product_name = product_name
            
        db.session.commit()

        return redirect(url_for('builder_product_dashboard'))
    else:
        up_stock = product_builder.query.filter_by(id=id).first()
        return render_template('edit_product.html')
###################################################################

###################################################builder product stock starts #####################################333
#builder product stock route
@app.route('/builder_stock_dashboard', methods=['GET','POST'])
def builder_stock_dashboard():
    category_choice_extra='None'
    stocks = product_builder.query.all()
    if not session.get('logged_in'):
        return redirect(url_for('builder_login'))
    if request.method == 'POST':
        category_choice_extra=request.form['category_choice_extra']
        stocks = product_builder.query.filter_by(category_choice_extra=category_choice_extra).all()
    return render_template('builder_stock_dashboard.html',stocks=stocks,type=category_choice_extra)
###################################################builder product stock ends  #####################################333

#####################################UPDATE STOCK STARTS########
@app.route('/update_stock', methods=['GET', 'POST'])
def update_stock():
    id="None"
    if request.method == 'POST':
        product_name = request.form['product_name']
        category_choice_extra = request.form['category_choice_extra']
        stock = request.form['stock']
        id = request.form['id']
        #update stock logic 
        up_stock = product_builder.query.filter_by(id=id).first()
        if up_stock:
            up_stock.product_name = product_name
            up_stock.category_choice_extra = category_choice_extra
            up_stock.stock = stock
        db.session.commit()

        return redirect(url_for('builder_stock_dashboard'))
    else:
        up_stock = product_builder.query.filter_by(id=id).first()
        return render_template('update_stock.html')

#####################################UPDATE STOCK ENDS########################


#######################################################BUILDER ADD NEW PROPERTIES##################################
#builder_add property route decor
@app.route('/builder_add_property', methods=['GET','POST'])
def builder_add_property():
    if not session.get('logged_in'):
        return redirect(url_for('builder_login'))
    
    if request.method =='POST':
        category = request.form['category']
        price = request.form['price']
        #buyer_id = request.form['buyer_id']
        if 'property_pic' not in request.files:
            return 'Please add property picture'

        property_pic = request.files['property_pic']

        # if  haven't selected file, browser also submits an empty part without filename 
        if property_pic.filename == '':
            return 'no files selected'
        
        if property_pic and allowed_file(property_pic.filename):
            filename = property_pic.filename
            property_pic_name="images/property_pics/"+filename
            output_size = (365,365)
            property_path = os.path.join(PROPERTY_FOLDER,filename)
            i = Image.open(property_pic)
            i.resize(output_size)
            i.save(property_path)
        property = Property(category=category, price=price, property_pic=property_pic_name)
        #property = Property(category=category, price=price, property_pic=property_pic_name, buyer_id=buyer_id)
        db.session.add(property)
        db.session.commit()
        
        return redirect(url_for('builder_dashboard'))
    buyers = Buyer.query.all()
    return render_template('builder_add_property.html', buyers=buyers)
##################################################### BUILDER ADD NEW PROPERTIES ENDS ######################################

#################################################BUILDER ADD NEW PRODUCTS ####################################
#route for builder_add_products 
@app.route('/bulider_add_products',methods=['GET','POST'])
def builder_add_products():
    #to check whether the builder is logged in
    if not session.get('logged_in'):
        return redirect(url_for('builer_login'))

    #POST request handling 
    if request.method == 'POST':
        #getting form data from .form request object
        product_name = request.form['product_name']
        #category_home = request.form['category_home']
        category_sub_home = request.form['category_sub_home']
        category_choice_extra = request.form['category_choice_extra']
        price = request.form['price'] 
        stock = request.form['stock']

        # to check if a product_pic file  uploaded
        if 'product_pic' not in request.files:
            return 'No product picture added'

        product_pic = request.files['product_pic']

        #to check if the product pic is from a valid file 
        if product_pic.filename =='':
            return 'No product picture selected'

        if product_pic and allowed_file(product_pic.filename):
            filename = product_pic.filename
            product_pic_name = "images/products_pics/"+filename
            output_size = (365,365)
            product_path = os.path.join(PRODUCTS_FOLDER, filename)
            i = Image.open(product_pic)
            i.resize(output_size)
            i.save(product_path)

        product = product_builder(product_name=product_name,
                                 category_sub_home=category_sub_home,category_choice_extra=category_choice_extra,
                                 price=price, product_pic=product_pic_name, stock=stock)
        db.session.add(product)
        db.session.commit()

        return redirect(url_for('builder_dashboard'))

    return render_template('builder_add_product.html')
####################################################### BUILDER ADD NEW PRODUCTS ENDS  #############################

######################################################BUYERS ADD OPTION (choices and extras)##########################3
#route for Add operation 
@app.route('/add/<int:id>/<int:buyerid>')
def add(id, buyerid):
    product_to_copy = product_builder.query.get_or_404(id)
    add_product_buyer = product_buyer()
    add_product_buyer.product_name = product_to_copy.product_name
    add_product_buyer.category_home = product_to_copy.category_home
    add_product_buyer.category_sub_home = product_to_copy.category_sub_home
    add_product_buyer.category_choice_extra = product_to_copy.category_choice_extra
    add_product_buyer.price = product_to_copy.price
    add_product_buyer.product_pic = product_to_copy.product_pic
    add_product_buyer.stock = product_to_copy.stock
    add_product_buyer.buyer_id = buyerid
    product_to_copy.stock-=1
    if(product_to_copy.stock<10):
        fromaddr="info@booknewhome.co.uk"
        smtp_server="smtp.hostinger.com"
        port=465
        m=add_product_buyer.product_name +" "+add_product_buyer.category_choice_extra+" "+"low Stock alert!!!  Refil Stock"
        msg = MIMEText(m)
        msg['Subject'] = "STOCK ALERT"
        msg['From'] = fromaddr
        msg['To'] = "newhomebuilders5@gmail.com"
        session=smtplib.SMTP_SSL(smtp_server,port)
        session.login("info@booknewhome.co.uk","Qwer123$")
        session.sendmail(fromaddr,"newhomebuilders5@gmail.com",msg.as_string())
        session.quit()
        print( "Email sent to  newhomebuilders5@gmail.com")

    db.session.add(add_product_buyer)
    add_product_buyer.product_add_date = datetime.now() ####add the current date ####
    db.session.commit()
    return redirect(url_for('dashboard', buyer_id=buyerid))
###################################################################################################

################################################# RESERVE PROPERTY TO BUYER (BUILDERS) STARTS #######################################
@app.route('/add_property/<int:id>/',methods=['GET','POST'])
def add_property(id):
    buyers=Buyer.query.all()
    cproperties = Property.query.all()
    for buyer in buyers:
        print(buyer.fname)
    print(id)
    if request.method == 'POST':
        #getting form data from .form request object
        buyerid = request.form['buyer_id'] 
    print(buyerid)
    property=Property.query.filter_by(id=id).first()
    
    property.buyer_id=buyerid
    property.property_add_date = datetime.now()
    db.session.commit()
    return render_template('builder_property_dashboard.html',buyers=buyers,cproperties=cproperties)
    
########################################################### RESERVE PROPERTY TO BUYER (BUILDERS) ENDS ########

###################################################### UPDATE PROGRESS BAR (BUILDERS) STARTS ###########################   
@app.route('/update_status/<int:buyerid>/',methods=['GET','POST'])
def update_status(buyerid):
    buyers=Buyer.query.all()
    cproperties = Property.query.all()
    for buyer in buyers:
        print(buyer.fname)
    
    if request.method == 'POST':
        #getting form data from .form request object
        status1 = request.form['status']
        estimated1 = request.form['estimated']
        
    property=Property.query.filter_by(buyer_id=buyerid).first()
    #property = Property(category=category, price=price, property_pic=property_pic_name)
    property.status=status1
    property.estimated=estimated1
    db.session.commit()     
    return render_template('builder_property_dashboard.html',buyers=buyers,cproperties=cproperties)
        
#############################################UPDATE PROGRESS BAR (BUILDERS) ENDS ###########################

#################################################ADD PRODUCTS to property type operation (BUILDERS) ###########################
@app.route('/add_product/<int:id>/',methods=['GET','POST'])
def add_product(id):
    cproperties = Property.query.all()
    cname=""
    if request.method == 'POST':
        #getting form data from .form request object
        categories = request.form.getlist('category[]')
        #category = request.form ['category'] 
    if '1bhk'or'2bhk'or'3bhk'  in categories:
        for category in categories:
            cname=cname+category
    product= product_builder.query.filter_by(id=id).first()
    product.category_home= cname
    
    db.session.commit()

    return redirect(url_for('builder_product_dashboard'))
    
    
###################################################### Add products to property type ends###########################  

#route for Remove operation####BUYERS OPERATION ########
@app.route('/remove/<int:id>/<int:buyerid>')
def remove(id, buyerid):
    product_to_remove = product_buyer.query.get_or_404(id)
    db.session.delete(product_to_remove)
    db.session.commit()
    return redirect(url_for('dashboard', buyer_id=buyerid))
    ##################################

###########REMOVE PRODUCTS BUILDERS OPERATION##########
@app.route('/remove_product/<int:id>')
def remove_product(id):
    product_to_remove = product_builder.query.get_or_404(id)
    db.session.delete(product_to_remove)
    db.session.commit()
    return redirect(url_for('builder_product_dashboard'))
    #################################
###### REMOVE PROPERTY BUILDERS OPEARTION ##############
@app.route('/remove_property/<int:id>')
def remove_property(id):
    property_to_remove = Property.query.get_or_404(id)
    db.session.delete(property_to_remove)
    db.session.commit()
    return redirect(url_for('builder_property_dashboard'))
    ##################################

########### INVOICE ROUTE ##############
@app.route('/invoice/<int:buyer_id>')
def invoice(buyer_id):
    total=0
    choices=[]
    extras=[]
    buyer = Buyer.query.get(buyer_id)
    properties = Property.query.filter_by(buyer_id=buyer_id).all()
    products_buyer = product_buyer.query.filter_by(buyer_id=buyer_id).all()
    for propertyy in properties:
        type_home=propertyy.category
    print("home type",type_home)

    products = product_builder.query.all()
    for product in products_buyer:
        if product.category_choice_extra == "choice":
            choices.append(product)
        else:
            extras.append(product)

    for choice in choices:
        print(choice.id, choice.product_name, choice.category_home,choice.category_sub_home, choice.category_choice_extra, choice.price, choice.product_pic, choice.stock)
    for extra in extras:
        total=total+extra.price
        session['total'] = total

        print(total)
        print(extra.id, extra.product_name, extra.category_home,choice.category_sub_home, extra.category_choice_extra, extra.price, extra.product_pic, extra.stock)
    return render_template('invoice.html', buyer=buyer, properties=properties, products=products, choices=choices, extras=extras, total=total)

#############################################################INVOICE ENDS #############################################

@app.route('/build')
def build():
    return render_template('builderbase.html')
###########################################################EMAIL ROUTE ##################
@app.route('/sendEmail/<senderEmailid>/<subject>/<textmsg>')
def sendEmail(senderEmailid,subject,textmsg):
    fromaddr="info@booknewhome.co.uk"
    smtp_server="smtp.hostinger.com"
    port=465
    msg = MIMEText(textmsg)
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = senderEmailid
    session=smtplib.SMTP_SSL(smtp_server,port)
    session.login("info@booknewhome.co.uk","Qwer123$")
    session.sendmail(fromaddr,[senderEmailid],msg.as_string())
    session.quit()
    return "Email sent to " + senderEmailid  +" "+ "successfully !"

################################## PAYMENT GATEWAY (BUYER) STARTS ##########################
@app.route('/payment/<int:id>', methods=['GET', 'POST'])
def payment(id):
    error_flash = None
    #using the invoice route logic to show the amount in the payment gateway ###
    total = 0
    choices=[]
    extras=[]
    buyer = Buyer.query.get(id)
    products_buyer = product_buyer.query.filter_by(buyer_id=id).all()
    products = product_builder.query.all()
    for product in products_buyer:
        if product.category_choice_extra == "choice":
            choices.append(product)
        else:
            extras.append(product)

    for choice in choices:
        print(choice.id, choice.product_name, choice.category_home,choice.category_sub_home, choice.category_choice_extra, choice.price, choice.product_pic, choice.stock)
    for extra in extras:
        total=total+extra.price
        print(extra.id, extra.product_name, extra.category_home,choice.category_sub_home, extra.category_choice_extra, extra.price, extra.product_pic, extra.stock)
        session['total'] = total
    total = session.get('total')
    ##################################################

    ######### Actual payment gateway code ######
    if request.method == 'POST':
        # Retrieve the payment details from the form
        amount = request.form['amount']
        description = request.form['description']
        token = request.form['stripeToken']

        #### verify enetered amount matches the total amount to pay ###################
        if float(amount) != total:
            error_flash = 'Amount entered does not match the total amount to be paid !'
            return render_template('error.html',error_flash=error_flash)
        try:
            # Process the payment using Stripe
            charge = stripe.Charge.create(
                amount=int(float(amount) * 100),
                currency='GBP',
                description=description,
                source=token
            )
            buyer=Buyer.query.filter_by(id=id).first()
            buyer.paymentstatus=1
            db.session.commit()
            
            return render_template('success.html')
    
        except stripe.error.CardError as e:
            # The card has been declined
            return render_template('error.html', error=str(e))
    else:
        # Rendering some variables from invoice route####
        return render_template('payment.html',buyer = buyer, products=products, choices=choices, extras=extras,total=total,error_flash=error_flash)
################################## PAYMENT GATEWAY (BUYER) ENDS ##########################
    
########################Payment Status (BUILDER)############
@app.route('/pay_status/<int:id>',methods=['GET','POST'])
def pay_status(id):
    #using the invoice route logic to show the amount in the payment gateway ###
    total = 0
    choices=[]
    extras=[]
    buyer = Buyer.query.get(id)
    products_buyer = product_buyer.query.filter_by(buyer_id=id).all()
    products = product_builder.query.all()
    for product in products_buyer:
        if product.category_choice_extra == "choice":
            choices.append(product)
        else:
            extras.append(product)

    for choice in choices:
        print(choice.id, choice.product_name, choice.category_home,choice.category_sub_home, choice.category_choice_extra, choice.price, choice.product_pic, choice.stock)
    for extra in extras:
        total=total+extra.price
        print(extra.id, extra.product_name, extra.category_home,choice.category_sub_home, extra.category_choice_extra, extra.price, extra.product_pic, extra.stock)
        session['total'] = total
    total = session.get('total')
    ##################################################
    #############################pay-status logic#############
    if request.method =='POST':
        buyer=Buyer.query.filter_by(id=id).first()
        
        return render_template('pay_status.html', buyer = buyer,products=products, choices=choices, extras=extras,total=total)
    return render_template('pay_status.html', buyer = buyer,products=products, choices=choices, extras=extras,total=total)
############################## Payment Status (BUILDER) ENDS ###################

###################PROPERTY SALES REPORT #####################
@app.route('/property_sale_report')
def property_sale_report():
    #retrives property info from table
    properties = Property.query.all()
    data_of_properties = pd.DataFrame([(property.id,property.price,property.property_add_date,property.category,property.buyer_id) for property in properties],columns = ['id','price','property_add_date','category','BUYER ID'])
    total_properties = len(data_of_properties) # to find total property length
    category1bhk = len(data_of_properties[data_of_properties['category'] =='1bhk'])#length based on category(1bhk,2bhk,3bhk)
    category2bhk = len(data_of_properties[data_of_properties['category']=='2bhk'])
    category3bhk = len(data_of_properties[data_of_properties['category']=='3bhk'])
    # Find  Sold Properties By BUYERID #############
    data_of_sold_properties = data_of_properties[data_of_properties['BUYER ID'].notnull()]
    
    #VALUES IN THE SALES REPORT###############
    sold_property = len(data_of_sold_properties)
    mean_price_vale = np.mean(data_of_sold_properties['price'])
    property_revenue = np.sum(data_of_sold_properties['price'])

    available_properties = total_properties - sold_property # to find available property length
    sold_category1bhk = len(data_of_sold_properties[data_of_sold_properties['category'] =='1bhk'])
    sold_category2bhk = len(data_of_sold_properties[data_of_sold_properties['category']=='2bhk'])
    sold_category3bhk = len(data_of_sold_properties[data_of_sold_properties['category']=='3bhk'])
    #chart to display results of report###########
    data_of_properties['Month'] = pd.to_datetime(data_of_properties['property_add_date']).dt.strftime('%b %Y')
    sales_per_month = data_of_properties.groupby('Month').size().reset_index(name = 'Sold Property')
    fig1 = plotex.bar(sales_per_month, x='Month',y = 'Sold Property', title = ' Monthly Property Sales Report', color_discrete_sequence=[  'SteelBlue'])   
    # chart based on category type##############
    category_home_sales = data_of_sold_properties.groupby('category').count()['id'].reset_index(name='Sold Property')
    fig2 = plotex.bar(category_home_sales, x ='category', y = 'Sold Property', title = 'Properties sold based on Category',color_discrete_sequence=[  'SteelBlue'])

    #html
    chart_html1 = fig1.to_html(full_html=False)
    chart_html2 = fig2.to_html(full_html=False)

    return render_template('property_sale_report.html',salesreport=[sold_property,mean_price_vale,property_revenue],chart_html1 = chart_html1,chart_html2=chart_html2,total_properties = total_properties,available_properties = available_properties,category1bhk =category1bhk,sold_category1bhk=sold_category1bhk,
    category2bhk = category2bhk,sold_category2bhk=sold_category2bhk,category3bhk=category3bhk,sold_category3bhk=sold_category3bhk)
##################################################PROPERTY SALES REPORT ENDS ###########################

############PRODUCT SALES REPORT STARTS ###########################
@app.route('/products_sale_report')
def products_sale_report():
    #retrieve choices and extras from the prod_buildertable 
    choicesextras = product_builder.query.all()
    data_of_prod_choicesextra = pd.DataFrame([(choicesextras1.id,choicesextras1.price,choicesextras1.category_choice_extra) for choicesextras1 in choicesextras],columns = ['id','price','category_choice_extra'])

    #retrieve choices and extras from the prod_buyer table 
    products = product_buyer.query.all()
    data_of_choice_extra = pd.DataFrame([(product.id,product.price,product.product_add_date,product.category_choice_extra,product.buyer_id) for product in products],columns = ['id','price','product_add_date','category_choice_extra','BUYER ID'])

    total_choice_extra = len(data_of_prod_choicesextra) # to find total products length
    category_choice = len(data_of_prod_choicesextra[data_of_prod_choicesextra['category_choice_extra'] =='choice'])#length based on category(choice, extra)
    category_extra = len(data_of_prod_choicesextra[data_of_prod_choicesextra['category_choice_extra']=='extra'])

    ###find sold choices and extras product by Buyer_id ###
    data_of_sold_products = data_of_choice_extra[data_of_choice_extra['BUYER ID'].notnull()]

    ###VALUE IN SALES REPORT #####
    sold_choice_extra = len(data_of_sold_products)
    mean_price_vale = np.mean(data_of_sold_products['price'])
    product_revenue = np.sum(data_of_sold_products['price'])

    available_choice_extra = total_choice_extra - sold_choice_extra  # to find available product length
    sold_category_choice = len(data_of_sold_products[data_of_sold_products['category_choice_extra'] =='choice'])
    sold_category_extra = len(data_of_sold_products[data_of_sold_products['category_choice_extra']=='extra'])

    #graph to display results #######
    data_of_choice_extra['Month'] = pd.to_datetime(data_of_choice_extra['product_add_date']).dt.strftime('%b %Y')
    sales_per_month = data_of_choice_extra.groupby('Month').size().reset_index(name = 'Sold products')
    fig1 = plotex.bar(sales_per_month, x='Month',y = 'Sold products', title = ' Monthly Products Sales Report', color_discrete_sequence=[  'SteelBlue'])   
    # chart based on category type##############
    category_products_sales = data_of_sold_products.groupby('category_choice_extra').count()['id'].reset_index(name='Sold Products')
    fig2 = plotex.bar(category_products_sales, x ='category_choice_extra', y = 'Sold Products', title = 'Products sold based on Category',color_discrete_sequence=[  'SteelBlue'])
    


    #html
    chart_html1 = fig1.to_html(full_html=False)
    chart_html2 = fig2.to_html(full_html=False)

    return render_template('products_sale_report.html',salesreport=[sold_choice_extra,mean_price_vale,product_revenue],total_choice_extra = total_choice_extra,available_choice_extra = available_choice_extra,category_choice =category_choice,sold_category_choice=sold_category_choice,
    category_extra = category_extra,sold_category_extra=sold_category_extra,chart_html1=chart_html1, chart_html2=chart_html2)

#############################################################
if __name__ == '__main__':
    app.run(debug=True)



