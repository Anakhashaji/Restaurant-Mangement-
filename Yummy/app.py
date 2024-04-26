from flask import Flask,render_template,request,redirect,session,flash,url_for,jsonify,send_from_directory
from werkzeug.utils import secure_filename
import os

from functools import wraps
from flask_bcrypt import Bcrypt
# import mysql.connector
import pymysql


UPLOAD_FOLDER = os.path.join('static', 'images')
# # Define allowed files
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key_here'
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'restaurant',
}

#connection = pymysql.connect(**db_config)


# connection = mysql.connector.connect(**db_config)


os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def connect():
        """ Connect to the PostgreSQL database server """
        conn = None
        try:
            # connect to the PostgreSQL server
            #self.log.info('Connecting to the PostgreSQL database...')
            conn = pymysql.connect(**db_config)
        except (Exception) as error:
            #self.log.error(error)
            raise error
        return conn



def single_insert(insert_req):
        """ Execute a single INSERT request """
        conn = None
        cursor = None
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute(insert_req)
            conn.commit()
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            if conn is not None:
                conn.rollback()
            raise error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
def execute(req_query):
        """ Execute a single request """
        """ for Update/Delete request """
        conn = None
        cursor = None
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute(req_query)
            conn.commit()
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            if conn is not None:
                conn.rollback()
            raise error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
def executeAndReturnId( req_query):
        """ Execute a single request and return id"""
        """ for insert request """
        conn = None
        cursor = None
        try:
            conn =connect()
            cursor = conn.cursor()
            cursor.execute(req_query)
            conn.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            last_inserted_id = cursor.fetchone()[0]
            return last_inserted_id
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            if conn is not None:
                conn.rollback()
            raise error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
def fetchone( get_req):
        conn=None
        cur=None
        try:
            conn = connect()
            cur = conn.cursor()
            cur.execute(get_req)
            data = cur.fetchone()
            return data
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            raise error
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
def fetchall(get_req):
        conn = None
        cur = None
        try:
            conn = connect()
            cur = conn.cursor()
            cur.execute(get_req)
            data = cur.fetchall()
            return data
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            raise error
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/edit_resta/<int:uid>",methods=['POST','GET'])
def edit_resta(uid):
   
    query="SELECT * FROM restregister WHERE regre_id ='{}'"
    
    
    user_data =fetchall(query.format (uid))
   
    #cur.
   
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email'] 
        phno = request.form['phno']
        sdate = request.form['sdate']
        address = request.form['address']
        bio = request.form['bio']
        photo=request.files['photo']
       
        query="UPDATE restregister SET name='{}', email='{}', phone='{}', sdate='{}',  address='{}', bio='{}', photo='{}' WHERE regre_id='{}'"
        execute(query.format(name, email, phno, sdate,  address, bio, photo.filename, uid))
        #execute("UPDATE restregister SET name=%s, email=%s, phone=%s, sdate=%s,  address=%s, bio=%s, photo=%s WHERE regre_id=%s", (name, email, phno, sdate,  address, bio, photo.filename, uid))
     
       
       
        flash('User Updated','success')
        return redirect(url_for('admin_dashboard'))
    return render_template("admin/editrest.html",datau=user_data)


@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
       
        query="SELECT * FROM login WHERE username = '{}' AND password = '{}' AND status = 1"
        
        account = fetchone(query.format(username, password))
        if account:
            id,username , password, login_type,status = account
            session['id'] = id
            session['login_type'] = login_type
            if login_type == "user":
                query="SELECT * FROM register WHERE log_id='{}'"
                register =fetchone( query.format (id))
                
                reg_id=register[0]
                session['reg_id'] = reg_id
                return redirect(url_for('user_home'))
            
            elif login_type == "admin":     
                return redirect(url_for('admin_dashboard'))
            
            elif login_type == "restaurant":
                query="SELECT * FROM restregister WHERE log_id ='{}'"
                
                register = fetchone(query.format (id))
                
                reg_id=register[0]
                session['reg_id'] = reg_id
                return redirect(url_for('restaurant_home'))            
        else:
            flash("Username or password incorrect", 'error')

    return render_template('login.html')

@app.route('/enter_username', methods=['GET', 'POST'])
def enter_username():
    if request.method == 'POST':
        username = request.form['username']
        # Check if the username exists in the database
       
        query="SELECT username FROM login WHERE username='{}'"
        
        account = fetchone(query.format(username))
        if account:
            return redirect(url_for('new_password', username=username))
        else:
            flash('Username not found.', 'error')
    return render_template('admin/username.html')

# Route to handle setting a new password
@app.route('/new_password/<username>', methods=['GET', 'POST'])
def new_password(username):
    if request.method == 'POST':
        new_password = request.form['new_pass']
        confirm_password = request.form['new_pass_c']
        if new_password == confirm_password:
            # Update the password in the database
           
            query="UPDATE login SET password='{}' WHERE username='{}'"
            execute(query.format(new_password, username))
           
            flash('Password updated successfully.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match.', 'error')
    return render_template('admin/newpassword.html', username=username)



@app.route('/logoutu')
def logoutu():
   
    session.clear()   
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/logoutr')
def logoutr():
  
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/logouta')
def logouta():
    # Clear the session data
    session.clear()
    
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/user_home')
def user_home():
    # Add your logic for user home here
   log_id = session.get('id') 
   query="SELECT * FROM restregister "
   datar =fetchall(query.format(log_id))
   
   log_id = session.get('id') 
   query="select  * from register WHERE log_id = '{}'"
   dataur=fetchall(query.format(log_id))
   print(dataur)
   
   
   
   return render_template('admin/indexuser1.html',datare=datar,datau=dataur)


@app.route('/display_dishes')
def display_dishes():
    log_id = session.get('id')  # Retrieve the logged-in user's ID from the session
    query="select  * from register WHERE log_id = '{}'"
        
    dataur=fetchall(query.format(log_id))
    
    rest_id = request.args.get('rest_id') 
    print('rest_id',rest_id)
    query = "SELECT * FROM dishes WHERE rest_id = '{}'"
    dishes_data = fetchall(query.format(rest_id))
    print("dishes_data",dishes_data)
    return render_template('admin/display_dishes.html', dishes_data=dishes_data,datau=dataur)





@app.route('/restaurant_home')
def restaurant_home():
    log_id = session.get('id') 
   
    
    query="SELECT * FROM dishes d INNER JOIN restregister r ON d.rest_id = r.regre_id inner join dish_category dc on dc.id=d.cusine where r.log_id='{}'"
    
    datar =fetchall(query.format(log_id))

    query="select * from restregister WHERE log_id ='{}'" 
    dataur=fetchall(query.format(log_id))
   
    return render_template('admin/indexrestau.html',datare=datar,datau=dataur)


@app.route('/admin_dashboard')
def admin_dashboard():
   
   query="SELECT * FROM restregister "
   datar =fetchall(query.format())
   
   return render_template('admin/index.html', datare=datar)

@app.route('/add_dish', methods=['POST','GET'])
def add_dish():
    log_id = session.get('id')
    
    query="select  * from restregister WHERE log_id ='{}'" 
    dataur=fetchall(query.format(log_id))
    print(dataur)
   
    query="SELECT * FROM dish_category"
    data =fetchall(query.format())
    
    if request.method == 'POST':
        cuisine = request.form['cuisine']
        dishname = request.form['dishname']
        dishphoto = request.files['dishphoto']
        price=request.form['price']
        filename = secure_filename(dishphoto.filename)
        dishphoto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        query="INSERT INTO dishes (rest_id, cusine, dishe, dishe_photo,price) VALUES ('{}', '{}', '{}', '{}','{}')"
        datain=single_insert(query.format(dataur[0][0], cuisine, dishname, filename,price))
        #execute("INSERT INTO dishes (rest_id, cusine, dishe, dishe_photo,price) VALUES (%s, %s, %s, %s,%s)",
                    #(dataur[0][0], cuisine, dishname, filename,price))
        flash('Review submitted successfully', 'success')
        return redirect(url_for('restaurant_home'))
    
    return render_template('admin/adddish.html',datau=dataur,datas=data)



@app.route('/add_seats', methods=['POST','GET'])
def add_seats():
    log_id = session.get('id')
    
    query="select  * from restregister WHERE log_id ='{}'" 
    dataur=fetchall(query.format(log_id))
    print(dataur)
   
    
    
    if request.method == 'POST':
        seatnumber = request.form['seatnumber']
        
        
        query="INSERT INTO seats (rest_id, table_name,status) VALUES ('{}', '{}', '{}')"
        datain=single_insert(query.format(dataur[0][0],seatnumber,'0'))
        
     
        return redirect(url_for('restaurant_home'))
    
    return render_template('admin/addseat.html',datau=dataur)







@app.route('/dish_category', methods=['POST','GET'])
def dish_category():
    log_id = session.get('id')
    query="select  * from restregister WHERE log_id ='{}'"
    dataur=fetchall(query.format(log_id))
    
    print(dataur)
    if request.method == 'POST':
        cuisine = request.form['category']
        query="INSERT INTO dish_category (dish_category) VALUES ('{}')"
        datain=single_insert(query.format(cuisine))
        #execute("INSERT INTO dish_category (dish_category) VALUES (%s)",(cuisine,))
        return redirect(url_for('restaurant_home'))
    
    return render_template('admin/dish_category.html',datau=dataur)

@app.route('/add_restatype', methods=['POST','GET'])
def add_restatype():   
    if request.method == 'POST':
        rest_type = request.form['rest_type']
        query="INSERT INTO type_restaurent (restaurent_type) VALUES ('{}')"
        datain=single_insert(query.format(rest_type))
        #execute("INSERT INTO type_restaurent (restaurent_type) VALUES (%s)",(rest_type,))
        flash(' submitted successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_restatype.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        phno = request.form['phno']
        age = request.form['age']
        gender = request.form['gender']
        address = request.form['address']
        #bio = request.form['bio']
        photo = request.files['photo']

        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        query="""INSERT INTO login(username, password, login_type, status) VALUES ('{}', '{}', '{}', '{}')"""
        result=executeAndReturnId(query.format(username, password, 'user', 1))
        
        #single_insert("""INSERT INTO login(username, password, login_type, status) VALUES (%s, %s, %s, %s) RETURNING id""", (username, password, 'user', 1))
        # query1="SELECT LAST_INSERT_ID()"
        # result = fetchone( query.format ())
        print("ree",result)

        if result is not None:
            user_id = result

            if user_id:
                query="INSERT INTO register(log_id, name, email, phno, age, gender, address, bio, photo) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
                datain=single_insert(query.format(user_id, name, email, phno, age, gender, address, 'aa', filename))
                print(datain)
                #execute("""INSERT INTO register(log_id, name, email, phno, age, gender, address, bio, photo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            #(user_id, name, email, phno, age, gender, address, bio, filename))
                            
                return_value = 'Registeration Suceesful'  # Set the return value to 'success'
                return render_template('index.html', return_value=return_value)
            else:
                flash('Error in registration. Please try again.')
               

    return render_template('admin/adduserr.html', registration_success=False)




@app.route("/usermyprofile",methods=['POST','GET'])
def usermyprofile():
    log_id = session.get('id') 
    
    query="SELECT * FROM register WHERE log_id ='{}'"
   
    # user_data =fetchone()
    user_data =fetchall(query.format (log_id))
   
    
    
    print(user_data)
    
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        phno = request.form['phno']
        age = request.form['age']
        gender = request.form['gender']
        address = request.form['address']
        bio = request.form['bio']
        photo=request.files['photo']
        
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        query="UPDATE register SET name='{}', email='{}', phno='{}', age='{}', gender='{}', address='{}', bio='{}',photo='{}' WHERE log_id='{}'"
        execute(query.format(name, email, phno, age, gender, address, bio, filename, log_id))
        #execute("UPDATE register SET name=%s, email=%s, phno=%s, age=%s, gender=%s, address=%s, bio=%s WHERE log_id=%s", (name, email, phno, age, gender, address, bio, log_id))

        flash('User Updated','success')
        return redirect(url_for('user_home'))
    return render_template('admin/updateuser.html',datau=user_data)


@app.route("/restmyprofile",methods=['POST','GET'])
def restmyprofile():
    log_id = session.get('id') 
    
    query="SELECT * FROM restregister WHERE log_id ='{}'"
    
    user_data = fetchone(query.format(log_id))
    #user_data =fetchall()
    print(user_data)
    
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        phno = request.form['phno']
        sdate = request.form['sdate']
        address = request.form['address']
        bio = request.form['bio']
        photo=request.files['photo']
        
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        query="UPDATE restregister SET name='{}', email='{}', phone='{}', sdate='{}', address='{}', bio='{}', photo='{}' WHERE log_id='{}'"
        execute(query.format(name, email, phno, sdate, address, bio, filename, log_id))
        #execute("UPDATE restregister SET name=%s, email=%s, phone=%s, sdate=%s, address=%s, bio=%s, photo=%s WHERE log_id=%s", (name, email, phno, sdate, address, bio, photo.filename, log_id))
        
       
       
        flash('Resturent Updated','success')
        return redirect(url_for('restaurant_home'))
    return render_template('admin/updaterest.html',datau=user_data)

@app.route('/show_orders')
def show_orders():
    log_id = session.get('id')
    reg_id=session.get('reg_id')
    print("reg_id",reg_id)
    print(log_id)
    if log_id:
       
       
        query="SELECT od.*, re.*, l.*, r.name as uname, r.address as uaddress, r.phno as uphno, r.email as uemail ,d.dishe as dishname FROM dish_order od INNER JOIN dishes d ON d.dish_id = od.dish_id INNER JOIN login l ON l.id = od.user_id INNER JOIN register r ON r.log_id = l.id INNER JOIN restregister re ON re.regre_id = d.rest_id WHERE re.regre_id = '{}' AND od.status = 1"

        #query="SELECT od.*, re.*, l.*, r.name as uname, r.address as uaddress, r.phno as uphno, r.email as uemail FROM dish_order od INNER JOIN dishes d ON d.dish_id = od.dish_id INNER JOIN login l ON l.id = od.user_id INNER JOIN register r ON r.log_id = l.id INNER JOIN restregister re ON re.regre_id = d.rest_id WHERE re.regre_id = '{}' AND od.status = 1 AND DATE(od.date) = CURDATE();"
       
        data =fetchall(query.format(reg_id))
       
        query="select  * from restregister WHERE log_id = '{}'"
        
        dataur=fetchall(query.format(log_id))
       
       
        return render_template('admin/order_user.html', datas=data,datau=dataur) 

@app.route('/mark_delivered', methods=['POST'])
def mark_delivered():
    if request.method == 'POST':
        order_id = request.form['order_id']
        print("order_id",order_id)
        # Update the status of the order in the database
        update_query = "UPDATE dish_order SET status ='{}' WHERE id = '{}'"
        execute(update_query.format('2',order_id))
        return redirect('/show_orders')
    
    
@app.route('/show_booktable')
def show_booktable():
    log_id = session.get('id')
    reg_id=session.get('reg_id')
    print("reg_id",reg_id)
    print(log_id)
    if log_id:
       
        #query="SELECT bo.*, re.*, l.*, r.name as uname, r.address as uaddress, r.phno as uphno, r.email as uemail FROM book_table bo INNER JOIN restregister re ON re.regre_id = bo.rest_id INNER JOIN login l ON l.id = bo.user_id INNER JOIN register r ON r.log_id = l.id WHERE re.regre_id ='{}'"
        query="SELECT bo.*, re.*, l.*, r.name AS uname, r.address AS uaddress, r.phno AS uphno, r.email AS uemail, TIME_FORMAT(bo.time, '%h:%i %p') AS formatted_time FROM book_table bo INNER JOIN restregister re ON re.regre_id = bo.rest_id INNER JOIN login l ON l.id = bo.user_id INNER JOIN register r ON r.log_id = l.id WHERE re.regre_id ='{}' AND bo.status='{}'"
        data =fetchall(query.format(reg_id,'1'))
       
        query="select  * from restregister WHERE log_id ='{}'"
        
        dataur=fetchall(query.format(log_id))
       
       
        return render_template('admin/booktable_show.html', datas=data,datau=dataur) 
    
    
@app.route('/update_seats', methods=['POST'])
def update_seats():
    if request.method == 'POST':
        rest_id = request.form['rest_id']
        seat_id=request.form['seat_id']
        query="UPDATE seats set status='{}' where rest_id='{}' and id='{}'"
        execute(query.format('0',rest_id,seat_id))
        
        query="UPDATE book_table set status='{}' where rest_id='{}' and seat_id='{}'"
        execute(query.format('0',rest_id,seat_id))
       
        return redirect('/show_booktable')
    
    
@app.route('/display_review')
def display_review():
     log_id = session.get('id') 

     if log_id:
       
        query="SELECT re.review_content as review,r.name as resturant FROM review re INNER JOIN restregister r ON r.regre_id = re.re_id"
        data =fetchall(query.format()) 
        
        query = "SELECT regre_id, name FROM restregister"
        restaurants = fetchall(query.format())
        print("restlist",restaurants)
       
          
        return render_template('admin/admin_showreview1.html', datas=data,restaurants=restaurants)

@app.route('/displayrest_review')
def displayrest_review():
     log_id = session.get('id')  # Retrieve the logged-in user's ID from the session
     print("log_id",log_id)
     reg_id=session.get('reg_id')
     print("reg_id",reg_id)
     if log_id:
       
        #query="SELECT * FROM review r INNER JOIN login l ON l.id = r.u_id inner join restregister re on re.regre_id=r.rest_id where re.log_id=log_id"
        #query="SELECT * FROM review r INNER JOIN restregister re on re.regre_id=r.rest_id INNER JOIN login l ON l.id =re.log_id where re.log_id=log_id"
        query="SELECT * FROM review r INNER JOIN restregister re on re.regre_id=r.rest_id where re.regre_id='{}' "
        data =fetchall(query.format(reg_id))
        print("datareviewrest",data)
        
        query="select  * from restregister WHERE log_id = '{}'"
       
        dataur=fetchall(query.format(log_id)) 
       
         
        return render_template('admin/show_review.html', datas=data,datau=dataur)
    
# @app.route('/showuser_review')
# def showuser_review():
#     log_id = session.get('id')  # Retrieve the logged-in user's ID from the session

#     if log_id:
       
#         query="SELECT re.name as name,re.review_content as review,r.name as resturant FROM review re INNER JOIN restregister r ON r.regre_id = re.rest_id WHERE re.u_id = '{}'"
        
#         data =fetchall(query.format(log_id))
#         print("data",data) 
       
        
#         query="select  * from register WHERE log_id = '{}'"
        
#         dataur=fetchall(query.format(log_id))
       
       
#         return render_template('admin/displayreview.html', datas=data,datau=dataur)


@app.route('/showuser_review')
def showuser_review():
    log_id = session.get('id')  # Retrieve the logged-in user's ID from the session
    query="select  * from register WHERE log_id = '{}'"
        
    dataur=fetchall(query.format(log_id))

    if log_id:
        # Fetch restaurant names and IDs
        query = "SELECT regre_id, name FROM restregister"
        restaurants = fetchall(query.format())
        print("restlist",restaurants)
   

        return render_template('admin/displayreview.html', restaurants=restaurants,datau=dataur)

@app.route('/get_reviewsad')
def get_reviewsad():
    restaurant_id = request.args.get('restaurant_id')

    if restaurant_id:
        query = "SELECT re.review_content as review, r.name as restaurant FROM review re INNER JOIN restregister r ON r.regre_id = re.rest_id WHERE re.rest_id = '{}'"
        reviews = fetchall(query.format(restaurant_id))
        return {'reviews': reviews}
    else:
        return {'reviews': []}
    
@app.route('/get_reviews')
def get_reviews():
    restaurant_id = request.args.get('restaurant_id')
    log_id = session.get('id') 

    if restaurant_id:
        query = "SELECT re.review_content as review, r.name as restaurant FROM review re INNER JOIN restregister r ON r.regre_id = re.rest_id inner join login l on l.id=re.u_id WHERE l.id= '{}' and re.rest_id = '{}'"
        reviews = fetchall(query.format(log_id,restaurant_id))
        return {'reviews': reviews}
    else:
        return {'reviews': []}



    
@app.route('/his_booktable')
def his_booktable():
    log_id = session.get('id')  # Retrieve the logged-in user's ID from the session

    if log_id:
       
        #query="SELECT bt.*, re.name AS restname, re.email AS reemail, re.phone AS rephone, re.address AS readdress, l.* FROM book_table bt INNER JOIN restregister re ON re.regre_id = bt.rest_id INNER JOIN login l ON l.id = bt.user_id WHERE bt.user_id = '{}'"
        
        query="SELECT bt.*, re.name AS restname, re.email AS reemail, re.phone AS rephone, re.address AS readdress, l.*, TIME_FORMAT(bt.time, '%h:%i %p') AS formatted_time  FROM book_table bt INNER JOIN restregister re ON re.regre_id = bt.rest_id INNER JOIN login l ON l.id = bt.user_id WHERE bt.user_id = '{}'"
        
        
        
        data =fetchall(query.format (log_id)) 
       
         
        query="select  * from register WHERE log_id = '{}'"
        
        dataur=fetchall(query.format(log_id))
       
       
        return render_template('admin/histroy_booktable.html', datas=data,datau=dataur)



@app.route('/his_order')
def his_order():
    log_id = session.get('id')  # Retrieve the logged-in user's ID from the session

    if log_id:
       
        query="SELECT do.*, d.*, re.name AS restname, re.email AS reemail, re.phone AS rephone, re.address AS readdress, l.* FROM dish_order do INNER JOIN dishes d ON d.dish_id = do.dish_id INNER JOIN restregister re ON re.regre_id = d.rest_id INNER JOIN login l ON l.id = do.user_id WHERE do.user_id = '{}' AND do.status='{}'"
        
        data =fetchall(query.format(log_id,'1'))
       
        
        
        query="select  * from register WHERE log_id = '{}'"
        
        dataur=fetchall(query.format(log_id))
       
       
        return render_template('admin/history_order.html', datas=data,datau=dataur)

@app.route('/cancel_order/<order_id>', methods=['POST'])
def cancel_order(order_id):
    if request.method == 'POST':
        dish_id = request.form['dish_id']
    # Update the status of the dish_order table field to 0 for the given order_id
    query = "UPDATE dish_order SET status = '0' WHERE id = '{}' AND dish_id='{}'"
    execute(query.format(order_id,dish_id))
    
    return redirect('/his_order')




@app.route("/delete_restaurant/<string:uid>",methods=['GET'])
def delete_restaurant(uid):
   
    query="SELECT * FROM restregister WHERE regre_id = '{}'",
    
    data = fetchone(query.format(uid))

    if data:
        #login_id = data['login_id']
        login_id = data[1]

        # Delete from register table
        #query="DELETE FROM restregister WHERE regre_id ='{}'"
        #deleter=(query.format(uid))
        
        execute("DELETE FROM restregister WHERE regre_id = %s", (uid,))

        # Delete from login table
        #query1="DELETE FROM login WHERE id = '{}'"
        #deletel =(query.format(login_id))
        execute("DELETE FROM login WHERE id = %s", (login_id,))

       
       
        flash('User Deleted', 'warning')
    else:
        flash('User not found', 'danger')

    return redirect(url_for("admin_dashboard"))


@app.route('/submit_review', methods=['POST','GET'])
def submit_review():
   
    log_id = session.get('id') 
   
    query="select  * from register WHERE log_id = '{}'"
   
    dataur=fetchall(query.format(log_id))
   
    #cur.

    log_id = session.get('id', None)  # Retrieve the logged-in user's ID from the session
    if log_id:
        rest_id = request.args.get('id') 
        print('rest_id',rest_id)
       
        query="SELECT * FROM restregister where regre_id = '{}'"
        data =fetchall(query.format(rest_id))
       
        #cur.
       
        
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        cuisine=request.form['cuisine']
        review = request.form['review']
        query="INSERT INTO review (u_id,rest_id, name, email, review_content) VALUES ('{}','{}', '{}','{}', '{}')"
        datain=single_insert(query.format(log_id,cuisine, name, email, review))
        #execute("INSERT INTO review (u_id,rest_id, name, email, review_content) VALUES (%s,%s, %s, %s, %s)",
                    #(log_id,cuisine, name, email, review))
       
        #cur.
        flash('Review submitted successfully', 'success')
        return redirect(url_for('user_home'))
    
    reg_id=session.get('reg_id')
    if log_id:
        id=request.args.get('id')
        #print("urlid",id)
       
        query="SELECT * FROM review WHERE rest_id = '{}'"
        
        datare =fetchall(query.format (id))
       
        #cur.
        
        
       
    
    return render_template('admin/review.html',datas=data,datau=dataur,review=datare)


# Add a new route to handle AJAX request for getting dishes based on the selected restaurant
@app.route('/get_dishes', methods=['POST'])
def get_dishes():
    if request.method=='POST':
        print("ezasdfghj")
        restaurant_id = request.form.get('restaurant_id')
       
        query="SELECT dish_id, dishe FROM dishes WHERE rest_id ={}"
        
        dishes =fetchall(query.format(restaurant_id))
       
       
        return jsonify(dishes)
@app.route('/get_dish_price', methods=['POST'])
def get_dish_price():
    dish_id = request.form.get('dish_id')

    # Query the database to fetch the price of the selected dish
    query = "SELECT price FROM dishes WHERE dish_id ='{}'"
    result = fetchone(query.format (dish_id))

    # Check if the dish price was found
    if result:
        price = result[0]  # Extracting the price from the result
        return jsonify(price)
    else:
        # If the dish price is not found, return an error response
        return jsonify({'error': 'Dish price not found'}), 404


@app.route('/get_rating', methods=['POST'])
def get_rating():
    if request.method=='POST':
        print("ezasdfghj")
        restaurant_id = request.form.get('restaurant_id')
       
        query="SELECT dish_id, dishe,dishe_photo FROM dishes WHERE rest_id='{}'"
        
        dishes =fetchall(query.format(restaurant_id))
       
       
        return jsonify(dishes)

@app.route('/get_cousine', methods=['POST'])
def get_cousine():
    if request.method=='POST':
        print("ezasdfghj")
        cousine_id = request.form.get('cousine_id')
       
        query="SELECT *,ROUND(AVG(rating)) AS average_rating,COUNT(rating) AS rating_count FROM rating r INNER JOIN dishes d ON r.dish_id = d.dish_id INNER JOIN restregister res ON d.rest_id = res.regre_id WHERE cusine = '{}' GROUP BY r.dish_id ORDER BY average_rating DESC"
        cousine =fetchall(query.format(cousine_id))
       
       
        return jsonify(cousine)

@app.route('/order_submit',methods=['POST','GET'])
def order_submit():
    log_id = session.get('id') 
   
    query="select  * from register WHERE log_id ='{}'"
    
    dataur=fetchall(query.format(log_id))
   
    
    query="SELECT * FROM restregister"
    data =fetchall(query.format())
   
    #cur.
    print("hellowwwwwwwwwwww")
    
    
    if request.method=='POST':
        print("hello11111")
        log_id = session.get('id')
        perunit=request.form.get('perunit')
        dish_id = request.form.get('dish')
        date=request.form.get('date')
        query="INSERT INTO dish_order (dish_id,user_id,perunit,status,date) VALUES ('{}','{}','{}','{}','{}')"
        datain=single_insert(query.format(dish_id,log_id,perunit,'0',date))
        #execute("INSERT INTO dish_order (dish_id,user_id,perunit,status,date) VALUES (%s,%s,%s,%s,%s)",(dish_id,log_id,perunit,'0',date))
        
    return render_template('admin/order1.html',datau=dataur,datas=data)
    
    
@app.route('/submit_rating',methods=['POST','GET'])
def submit_rating():
    log_id = session.get('id') 
   
    query="select  * from register WHERE log_id='{}'"
   
    dataur=fetchall(query.format(log_id))
    #
    
    query="SELECT * FROM restregister"
    data =fetchall(query.format())
    print("hellowwwwwwwwwwww")
    
    if request.method == 'POST':
        log_id = session.get('id')
        print("log_id:", log_id)
        dish_id = request.form.get('dish_id')
        print("dish_id:", dish_id)
        dish_name = request.form.get('dish_name')
        print("dish_name:", dish_name)
        rating_name = 'rating-' + str(dish_id)
        rating = request.form.get(rating_name)
        print("rating_name:", rating_name)
        print("rating:", rating)
        query = "INSERT INTO rating (dish_id, dish_name, rating) VALUES ('{}', '{}', '{}')"
        datain = single_insert(query.format(dish_id, dish_name, rating))
        print("datain:", datain)
    
        return render_template('admin/rating.html', datau=dataur, datas=data)


        
        
        
    
    return render_template('admin/rating.html',datau=dataur,datas=data)
        
    
@app.route('/suggetion',methods=['POST','GET'])
def suggetion():
    log_id = session.get('id') 
   
    query="select  * from register WHERE log_id='{}'"
   
    dataur=fetchall(query.format(log_id))
    #
    
    
    query="SELECT * FROM dish_category"
    data =fetchall(query.format())
    print("hellowwwwwwwwwwww")
   
    
    
    # if request.method=='POST':
    #     print("hello11111")
    #     log_id = session.get('id')
       
    #     dish_id = request.form.get('dish_id')
    #     dish_name=request.form.get('dish_name')
    #     rating=request.form.get('rating')
    #     query="INSERT INTO rating (dish_id,dish_name,rating) VALUES ('{}','{}','{}')"
    #     #execute(query.format(dish_id,dish_name,rating))
    #     datain=single_insert(query.format(dish_id,dish_name,rating))
       
       
    #     return render_template('admin/rating.html',datau=dataur,datas=data)
        
        
        
    
    return render_template('admin/suggetion.html',datau=dataur,datas=data)
        
  
  
@app.route('/cart',methods=['POST','GET'])
def cart():
    log_id = session.get('id') 
   
    query="select  * from register WHERE log_id = '{}'"
    dataur=fetchall(query.format(log_id))
    query="SELECT * FROM dish_order o INNER JOIN dishes d ON d.dish_id = o.dish_id INNER JOIN dish_category dc ON dc.id = d.cusine inner join login l on l.id=o.user_id where o.user_id='{}' AND o.status = 0 "
    
    data =fetchall(query.format(log_id))
    print('order',data)
   
    #cur.
    i=0
    for order_item in data:
        i=i+int(order_item[11])
    if request.method == 'POST':
         #log_id = session.get('id') 
        
         query="UPDATE dish_order SET status='{}'"
         execute(query.format('1'))
         #execute("UPDATE dish_order SET status=%s", ('1',))
        
        
       
         return render_template('admin/paymentgate.html',price=i)
    
    
    return render_template('admin/cart1.html',datau=dataur,datas=data,price=i)


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    
    # dish_id = request.form['dish_id']
    id = request.form['id']
   
    query = "DELETE FROM dish_order WHERE  id= '{}'"
    execute(query.format(id))
      
    # Return success response
    return jsonify({'success': True})
    
    #return redirect(url_for('cart'))
    
  
@app.route('/paymentgate',methods=['POST','GET'])
def paymentgate():
    return render_template('admin/paymentgate.html')
    
  
  
    
@app.route('/book_table',methods=['POST','GET'])
def book_table():
    log_id = session.get('id') 
   
    query="select  * from register WHERE log_id ={}" 
    
    dataur=fetchall(query.format(log_id))
   
   
    
    query="SELECT * FROM restregister"
    data =fetchall(query.format())
   
   
    
    if request.method == 'POST':
        log_id = session.get('id')
        restaurant_id = request.form.get('restaurant')
        #dish_id = request.form.get('dish')
        date=request.form.get('date')
        time=request.form.get('time')
         # Check if the selected date and time for the restaurant are already booked
        query = "SELECT * FROM book_table WHERE rest_id = '{}' AND date = '{}' AND time = '{}'"
        existing_booking = fetchall(query.format(restaurant_id, date, time))
        
        if existing_booking:
            # If booking exists, show alert
            return render_template('admin/book_table.html', datau=dataur, datas=data, error="This time slot is already booked for the selected restaurant.")
        else:
            people=request.form.get('people')
            message=request.form.get('message')
            seat_number=request.form.get('seat_number')
            
            query="INSERT INTO book_table (user_id,rest_id,date,time,people,message,status,seat_id) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')"
            datain=single_insert(query.format(log_id,restaurant_id,date,time,people,message,'1',seat_number))
            
            query="UPDATE seats set status='{}' where id='{}'"
            execute(query.format('1',seat_number))
            
            #execute("INSERT INTO book_table (user_id,rest_id,date,time,people,message,status) VALUES (%s,%s,%s,%s,%s,%s,%s)",(log_id,restaurant_id,date,time,people,message,'0'))
            
            # Show JavaScript alert after successful booking
            return render_template('admin/book_table.html', datau=dataur, datas=data, success="Table booked successfully.")

        
            return redirect(url_for('user_home'))
    
    return render_template('admin/book_table.html',datau=dataur,datas=data)
        
@app.route('/get_seats/<restaurant_id>')
def get_seats(restaurant_id):
    # query = "SELECT * FROM seats WHERE rest_id = '{}'"
    query = "SELECT * FROM seats s left join book_table b on s.id=b.seat_id AND (b.status <> 0) where s.rest_id= '1' AND s.status<>'1'"
    seats = fetchall(query.format(restaurant_id))
    
    return jsonify(seats) 
    
    
@app.route('/restregister', methods=['POST', 'GET'])
def restregister():
    
    query="SELECT * FROM type_restaurent"
    data =fetchall(query.format())
   
   
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        rest_type=request.form['rest_type']
        username = request.form['username']
        password = request.form['password']
        phno = request.form['phno']
        sdate = request.form['sdate']  
        address = request.form['address']
        #bio = request.form['bio']
        photo=request.files['photo']
        
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

      
            # Insert into login table and get last insert ID
        query="""INSERT INTO login(username, password, login_type, status) VALUES ('{}', '{}', '{}', '{}')"""
        result=executeAndReturnId(query.format(username, password, 'restaurant', 1))   
        #single_insert("""INSERT INTO login(username, password, login_type, status)VALUES (%s, %s, %s, %s) RETURNING id""", (username, password,'restaurant', 1))

       
        #result = fetchone("SELECT LAST_INSERT_ID()")
        if result is not None:
            user_id = result
                
           
            if user_id:
                    # Insert into register table
                query="INSERT INTO restregister(log_id,rest_type, name, email, phone,sdate, address, bio,photo)VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}','{}','{}') "
                datain=single_insert(query.format(user_id,rest_type, name, email, phno, sdate, address, 'aa',filename))
                #execute("""INSERT INTO restregister(log_id,rest_type, name, email, phone,sdate, address, bio,photo)VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s) """, (user_id,rest_type, name, email, phno, sdate, address, bio,filename))

               
               
                
                return_value = 'Registration Successful'
                
                flash('Registration successful', 'success')
                return render_template('index.html', return_value=return_value)
            else:
                flash('Error in registration. Please try again.', 'error')
                
    return render_template('admin/addrestaurent.html',datas=data,registration_success=False)
    
    

@app.route('/displayallresturent')   
def displayallresturent():
   
    query="SELECT * FROM restregister "
    datar =fetchall(query.format())
   
    
    #print(data1) 
    log_id = session.get('id')
    query="select  * from restregister WHERE log_id = '{}'"
    
    dataur=fetchall(query.format(log_id))
   
   
    
    return render_template('admin/show_resta.html', datare=datar,datau=dataur)
    #return render_template('displayallrest.html', datare=datar)
    
@app.route('/edit_user/<string:uid>',methods=['POST','GET'])
def edit_user(uid):
   
    query="SELECT * FROM register WHERE reg_id = {}"
    
    user_data = fetchone(query.format (uid))
    #print(user_data)
    
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        phno = request.form['phno']
        age = request.form['age']
        gender = request.form['gender']
        address = request.form['address']
        bio = request.form['bio']
       
        query="UPDATE register SET name='{}', email='{}', phno='{}', age='{}', gender='{}', address='{}', bio='{}' WHERE reg_id='{}'"
        execute=(query.format(name, email, phno, age, gender, address, bio, uid))
        #execute("UPDATE register SET name=%s, email=%s, phno=%s, age=%s, gender=%s, address=%s, bio=%s WHERE reg_id=%s", (name, email, phno, age, gender, address, bio, uid))

        print(cur)
       
       
        
        flash('User Updated','success')
        return redirect(url_for('displayu'))
    return render_template('upregister.html',datau=user_data)

@app.route("/delete_user/<string:uid>", methods=['GET'])
def delete_user(uid):
   

    query="SELECT * FROM register WHERE reg_id = '{}'"
    
    data = fetchone(query.format (uid))

    if data:
        #login_id = data['login_id']
        login_id = data[1]
        #query="DELETE FROM register WHERE reg_id = '{}'"
        #query1="DELETE FROM login WHERE id ='{}'"
        execute("DELETE FROM register WHERE reg_id = %s", (uid,))
        execute("DELETE FROM login WHERE id = %s", (login_id,))

       
       
        flash('User Deleted', 'warning')
    else:
        flash('User not found', 'danger')

    return redirect(url_for("displayall"))


if __name__ == '__main__':
     
  
    app.run(debug=True)