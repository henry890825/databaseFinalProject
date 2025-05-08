from flask import Flask, render_template, request, session
from PIL import Image
from io import BytesIO
import sqlite3
import base64

app = Flask(__name__)
app.secret_key = 'ambutukam'
# ------------------------------------------------ home page
@app.route("/")
@app.route("/guesthome")
def guest_home():
    session.get('user_id') == None
    return render_template("guest_home.html")

@app.route("/userhome")
def user_home():
    if session.get('user_id') == None or session.get('user_id') == 1:
        return render_template('guest_relogin.html')
    return render_template("user_home.html")

@app.route("/adminhome")
def admin_home():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    return render_template("admin_home.html")
# -------------------------------------------------- auth
@app.route("/guestlogin", methods = ['POST', 'GET'])
def guest_login():
    session['user_id'] = None
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("SELECT rowid, name, password FROM User WHERE name = '"+name+"' AND password = '"+password+"'")
            result = cur.fetchall()
        con.close()

        if len(result) == 0:
            return ('pls try again or sign up first')
        elif name == 'admin' and password == '123':
            session['user_id'] = 1
            return render_template('admin_home.html')
        else:
            session['user_id'] = result[0][0]
            return render_template('user_home.html')
    return render_template('guest_login.html')

@app.route("/guestsignup", methods = ['POST', 'GET'])
def guest_signup():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO User VALUES (?, ?)", (name, password))
            con.commit()
        con.close()

        return render_template('guest_signup_success.html')
    return render_template('guest_signup.html')

@app.route("/logout", methods = ['POST', 'GET'])
def logout():
    session['user_id'] = None
    return render_template('guest_home.html')
# --------------------------------------------------- add comment page
@app.route("/usercreate")
def user_create():
    if session.get('user_id') == None or session.get('user_id') == 1:
        return render_template('guest_relogin.html')

    return render_template("user_create.html", return_page = 'user_create')

@app.route("/admincreate")
def admin_create():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')

    return render_template("admin_create.html", return_page = 'admin_create')
# -------------------------------------------------------------- add comment
@app.route("/addrow", methods = ['POST', 'GET'])
def addrow(return_page = None):
    if session.get('user_id') == None:
        return render_template('guest_relogin.html')
    if request.method == 'POST':     
        try:
            return_page = request.form['return_page']

            uId = session.get('user_id')
            food_name = request.form['food_name']
            price = request.form['price']
            score = request.form['score']
            comment = request.form['comment']
            store_name = request.form['store_name']
            addr = request.form['addr']
            date = request.form['date']

            pic = request.files['pic'].read()
            if pic != b'':
                pic = Image.open(BytesIO(pic))
                pic_format = pic.format
                pic = pic.resize((200, 200))
                image_data = BytesIO()
                pic.save(image_data, format= pic_format)
                pic = image_data.getvalue()

            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
# ---------- store跟addr一樣就不插入新的store 反之則插入
                cur.execute("SELECT rowid FROM Store WHERE (name, addr) = (?,?)", (store_name, addr))

                items = cur.fetchall()
                if len(items) == 0:
                    cur.execute("INSERT INTO Store VALUES (?,?)", (store_name, addr))
                    cur.execute("SELECT rowid FROM Store WHERE (name, addr) = (?,?)", (store_name, addr))
                    items = cur.fetchall()
                    food_sId = items[0][0]
                else:
                    food_sId = items[0][0]  
# ------food_name跟price同時一樣就不插入新的food 反之則插入
                cur.execute("SELECT rowid FROM Food WHERE (name, price) = (?,?)", (food_name, price))

                items = cur.fetchall()
                if len(items) == 0:
                    cur.execute("INSERT INTO Food VALUES (?,?,?)", (food_sId, food_name, price))

                    cur.execute("SELECT rowid FROM Food WHERE (name, price) = (?,?)", (food_name, price))

                    items = cur.fetchall()
                    fId = items[0][0]
                else:
                    fId = items[0][0]  

                cur.execute("INSERT INTO Rating VALUES (?,?,?,?,?,?)", (uId, fId, score, date, comment, pic))
                con.commit()
        except:
                con.rollback()

        finally:
                con.close()
                if return_page == 'admin_create':
                    return admin_search_own_comment()
                    # return admin_create()
                elif return_page == 'user_create':
                    return user_search_own_comment()   
                    # return user_create()
# ------------------------------------------------------------ list table
@app.route('/adminlistuser')
def admin_list_user():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    con = sqlite3.connect("database.db")

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM User")

    rows = cur.fetchall()
    con.close()
    return render_template("admin_list_user.html",rows = rows)

@app.route('/adminliststore')
def admin_list_store():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    con = sqlite3.connect("database.db")

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM Store")

    rows = cur.fetchall()
    con.close()
    return render_template("admin_list_store.html",rows = rows)

@app.route('/adminlistrating')
def admin_list_rating():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    con = sqlite3.connect("database.db")

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM Rating")

    rows = cur.fetchall()
    con.close()

    for i in range(len(rows)):
        pics = base64.b64encode(rows[i][6]).decode()
        rows[i] = rows[i][:6] + (pics,) + rows[i][7:]

    return render_template("admin_list_rating.html",rows = rows)

@app.route('/adminlistfood')
def admin_list_food():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    con = sqlite3.connect("database.db")

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM Food")

    rows = cur.fetchall()
    con.close()

    return render_template("admin_list_food.html", rows = rows)
# --------------------------------------------------------- delete row
@app.route("/deleteuser", methods=['POST','GET'])
def delete_user():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    if request.method == 'POST':
        try:
            rowid = request.form['id']
            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM User WHERE rowid = (?)", rowid)
                    con.commit()
        except:
            con.rollback()

        finally:
            con.close()
            return admin_list_user()
        
@app.route("/deletestore", methods=['POST','GET'])
def delete_store():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    if request.method == 'POST':
        try:
            rowid = request.form['id']
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("DELETE FROM Store WHERE rowid = (?)", rowid)
                con.commit()
        except:
            con.rollback()

        finally:
            con.close()
            return admin_list_store()
        
@app.route("/deleterating", methods=['POST','GET'])
def delete_rating():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    if request.method == 'POST':
        try:
            rowid = request.form['id']
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("DELETE FROM Rating WHERE rowid = (?)", rowid)
                con.commit()
        except:
            con.rollback()

        finally:
            con .close()
            return admin_list_rating()

@app.route("/deletefood", methods=['POST','GET'])
def delete_food():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    if request.method == 'POST':
        try:
            rowid = request.form['id']
            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM Food WHERE rowid = (?)", rowid)
                    con.commit()
        except:
            con.rollback()

        finally:
            con.close()
            return admin_list_food()
# ------------------------------------------------ search food 
@app.route("/guestsearchfood", methods=['POST','GET'])
def guest_search_food():
    if request.method == 'POST':
        food_name = request.form['food_name']   
    else:
        food_name = ''  

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM Food, Rating, Store WHERE Store.rowid = Food.food_sId AND Food.rowid = Rating.fId AND Food.name LIKE (?)", ('%' + food_name + '%',))
    rows = cur.fetchall()
    con.close()

    for i in range(len(rows)):
        pics = base64.b64encode(rows[i][8]).decode()
        rows[i] = rows[i][:8] + (pics,) + rows[i][9:]

    return render_template("guest_search_food.html", rows = rows)

@app.route("/usersearchfood", methods=['POST','GET'])
def user_search_food():
    if session.get('user_id') == None or session.get('user_id') == 1:
        return render_template('guest_relogin.html')
    
    if request.method == 'POST':
        food_name = request.form['food_name']   
    else:
        food_name = ''   

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM Food, Rating, Store WHERE Store.rowid = Food.food_sId AND Food.rowid = Rating.fId AND Food.name LIKE (?)", ('%' + food_name + '%',))
    rows = cur.fetchall()
    con.close()

    for i in range(len(rows)):
        pics = base64.b64encode(rows[i][8]).decode()
        rows[i] = rows[i][:8] + (pics,) + rows[i][9:]

    return render_template("user_search_food.html", rows = rows)

@app.route("/adminsearchfood", methods=['POST','GET'])
def admin_search_food():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    
    if request.method == 'POST':
        food_name = request.form['food_name']   
    else:
        food_name = ''  

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM Food, Rating, Store WHERE Store.rowid = Food.food_sId AND Food.rowid = Rating.fId AND Food.name LIKE (?)", ('%' + food_name + '%',))
    rows = cur.fetchall()
    con.close()

    for i in range(len(rows)):
        pics = base64.b64encode(rows[i][8]).decode()
        rows[i] = rows[i][:8] + (pics,) + rows[i][9:]

    return render_template("admin_search_food.html", rows = rows)
# ----------------------------------------------- search user 
@app.route("/guestsearchuser", methods=['POST','GET'])
def guest_search_user():
    if request.method == 'POST':
        user_name = request.form['user_name']   
    else:
        user_name = ''

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM Food, Rating, User WHERE User.rowid = Rating.uId AND Food.rowid = Rating.fId AND User.name LIKE (?)", ('%' + user_name + '%',))

    rows = cur.fetchall()
    con.close()

    for i in range(len(rows)):
        pics = base64.b64encode(rows[i][8]).decode()
        rows[i] = rows[i][:8] + (pics,) + rows[i][9:]

    return render_template("guest_search_user.html",rows = rows)

@app.route("/usersearchuser", methods=['POST','GET'])
def user_search_user():
    if session.get('user_id') == None or session.get('user_id') == 1:
        return render_template('guest_relogin.html')

    if request.method == 'POST':
        user_name = request.form['user_name']   
    else:
        user_name = ''

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM Food, Rating, User WHERE User.rowid = Rating.uId AND Food.rowid = Rating.fId AND User.name LIKE (?)", ('%' + user_name + '%',))

    rows = cur.fetchall()
    con.close()

    for i in range(len(rows)):
        pics = base64.b64encode(rows[i][8]).decode()
        rows[i] = rows[i][:8] + (pics,) + rows[i][9:]

    return render_template("user_search_user.html",rows = rows)

@app.route("/adminsearchuser", methods=['POST','GET'])
def admin_search_user():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    
    if request.method == 'POST':
        user_name = request.form['user_name']   
    else:
        user_name = ''

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM Food, Rating, User WHERE User.rowid = Rating.uId AND Food.rowid = Rating.fId AND User.name LIKE (?)", ('%' + user_name + '%',))
    rows = cur.fetchall()
    con.close()

    for i in range(len(rows)):
        pics = base64.b64encode(rows[i][8]).decode()
        rows[i] = rows[i][:8] + (pics,) + rows[i][9:]

    return render_template("admin_search_user.html", rows = rows)
# ------------------------------------------- search own comment
@app.route("/usersearchowncomment", methods=['POST','GET'])
def user_search_own_comment(return_page = None):
    if session.get('user_id') == None or session.get('user_id') == 1:
        return render_template('guest_relogin.html')

    if request.method == 'POST':
        if return_page != None:
            food_name = ''  
        else:
            food_name = request.form['food_name']   
    else:
        food_name = '' 
  
    uId = session.get('user_id')

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT Rating.rowid, * FROM Food, Rating, User WHERE User.rowid = (?) AND User.rowid = Rating.uId AND Food.rowid = Rating.fId AND Food.name LIKE (?)", (uId, '%' + food_name + '%'))
    rows = cur.fetchall()
    con.close()


    # user_id
    # Rating.rowid, * => 4

    for i in range(len(rows)):
        pics = base64.b64encode(rows[i][9]).decode()
        rows[i] = rows[i][:9] + (pics,) + rows[i][10:]

    return render_template("user_search_own_comment.html", rows = rows)

@app.route("/adminsearchowncomment", methods=['POST','GET'])
def admin_search_own_comment(return_page = None):
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html') 

    if request.method == 'POST':
        if return_page != None:
            food_name = ''  
        else:
            food_name = request.form['food_name']   
    else:
        food_name = '' 

    uId = session.get('user_id')

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT Rating.rowid, * FROM Food, Rating, User WHERE User.rowid = (?) AND User.rowid = Rating.uId AND Food.rowid = Rating.fId AND Food.name LIKE (?)", (uId, '%' + food_name + '%'))
    rows = cur.fetchall()
    con.close()

    # user_id
    # Rating.rowid, * => 4
    for i in range(len(rows)):
        pics = base64.b64encode(rows[i][9]).decode()
        rows[i] = rows[i][:9] + (pics,) + rows[i][10:]   

    return render_template("admin_search_own_comment.html", rows = rows)
# -------------------------------------------- delete own comment
@app.route("/admindeleteowncomment", methods=['POST','GET'])
def admin_delete_own_comment():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    if request.method == 'POST':
        try:
            rId = request.form['rId']

            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM Rating WHERE rowid = (?)", (rId,))
                    con.commit()
        except:
            con.rollback()
        finally:
            con.close()
            return_page = 'admin_delete_own_comment' 
            return admin_search_own_comment(return_page)

@app.route("/userdeleteowncomment", methods=['POST','GET'])
def user_delete_own_comment():
    if session.get('user_id') == None or session.get('user_id') == 1:
        return render_template('guest_relogin.html')
    if request.method == 'POST':
        try:
            rId = request.form['rId']
            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM Rating WHERE rowid = (?)", (rId,))
                    con.commit()
        except:
            con.rollback()
        finally:
            con.close()
            return_page = 'user_delete_own_comment'
            return user_search_own_comment(return_page)
# ------------------------------------------------------------ edit row
@app.route("/admineditowncomment", methods=['POST','GET'])
def admin_edit_own_comment():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')
    if request.method == 'POST':
        rId = request.form['rId']

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM Rating WHERE rowid=(?)", (rId,))
            rows = cur.fetchall()
            con.commit()
        con.close()

        for i in range(len(rows)):
            pics = base64.b64encode(rows[i][6]).decode()
            rows[i] = rows[i][:6] + (pics,) + rows[i][7:]

    return_page = 'admin_edit_own_comment' 
    return render_template("admin_edit_own_comment.html", rows = rows, return_page = return_page)

@app.route("/usereditowncomment", methods=['POST','GET'])
def user_edit_own_comment():
    if session.get('user_id') == None or session.get('user_id') == 1:
        return render_template('guest_relogin.html')
    if request.method == 'POST':
        rId = request.form['rId']

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM Rating WHERE rowid=(?)", (rId,))
            rows = cur.fetchall()
            con.commit()
        con.close()

        for i in range(len(rows)):
            pics = base64.b64encode(rows[i][6]).decode()
            rows[i] = rows[i][:6] + (pics,) + rows[i][7:]

    return_page = 'user_edit_own_comment'
    return render_template("user_edit_own_comment.html", rows = rows, return_page = return_page)

@app.route("/editcomment", methods=['POST','GET'])
def edit_comment(return_page = None):
    if session.get('user_id') == None:
        return render_template('guest_relogin.html')
    if request.method == 'POST':
        try:
            return_page = request.form['return_page']
            rId = request.form['rId']
            score = request.form['score']
            comment = request.form['comment']
            date = request.form['date']

            pic = request.files['pic'].read()
            if pic != b'':
                pic = Image.open(BytesIO(pic))
                pic_format = pic.format
                pic = pic.resize((200, 200))
                image_data = BytesIO()
                pic.save(image_data, format= pic_format)
                pic = image_data.getvalue()

            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("SELECT rowid, * FROM Rating WHERE rowid=(?)", (rId,))
                rows = cur.fetchall()

                if pic == b'':
                    pic = rows[0][6]

                cur.execute("UPDATE Rating SET score=?, comment=?, date=?, pic=? WHERE rowid=?", (score, comment, date, pic, rId))
                con.commit()
        except:
            con.rollback()

        finally:
            con.close()
            if return_page == 'admin_edit_own_comment':
                return admin_search_own_comment(return_page)
            elif return_page == 'user_edit_own_comment':
                return user_search_own_comment(return_page)
# ------------------------------------------ search top rated
@app.route("/adminsearchtoprated", methods=['POST','GET'])
def admin_search_top_rated():
    if session.get('user_id') != 1:
        return render_template('guest_relogin.html')

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT *,COUNT(Rating.rowid), SUM(Rating.score) FROM Food, Rating, Store WHERE Store.rowid = Food.food_sId AND Food.rowid = Rating.fId GROUP BY Food.rowid")
    rows = cur.fetchall()
    con.close()

    rows1 = []
    for row in rows:
        temp_list = list(row)    
        temp_list[5] = round(temp_list[12] / temp_list[11], 1)
        rows1.append(tuple(temp_list))

    for i in range(len(rows1)-1):
        for j in range(len(rows1) - 1 - i):
            if rows1[j][5] < rows1[j+1][5]:
                temp_list = list(rows1)    
                temp_list[j], temp_list[j+1] = temp_list[j+1], temp_list[j]
                rows1 = tuple(temp_list)
    return render_template("admin_search_top_rated.html", rows1 = rows1)

@app.route("/guestsearchtoprated", methods=['POST','GET'])
def guest_search_top_rated():

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT *,COUNT(Rating.rowid), SUM(Rating.score) FROM Food, Rating, Store WHERE Store.rowid = Food.food_sId AND Food.rowid = Rating.fId GROUP BY Food.rowid")
    rows = cur.fetchall()
    con.close()

    rows1 = []
    for row in rows:
        temp_list = list(row)    
        temp_list[5] = round(temp_list[12] / temp_list[11], 1)
        rows1.append(tuple(temp_list))

    for i in range(len(rows1)-1):
        for j in range(len(rows1) - 1 - i):
            if rows1[j][5] < rows1[j+1][5]:
                temp_list = list(rows1)    
                temp_list[j], temp_list[j+1] = temp_list[j+1], temp_list[j]
                rows1 = tuple(temp_list)
    return render_template("guest_search_top_rated.html", rows1 = rows1)

@app.route("/usersearchtoprated", methods=['POST','GET'])
def user_search_top_rated():
    if session.get('user_id') == None or session.get('user_id') == 1:
        return render_template('guest_relogin.html')

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT *,COUNT(Rating.rowid), SUM(Rating.score) FROM Food, Rating, Store WHERE Store.rowid = Food.food_sId AND Food.rowid = Rating.fId GROUP BY Food.rowid")
    rows = cur.fetchall()
    con.close()

    rows1 = []
    for row in rows:
        temp_list = list(row)    
        temp_list[5] = round(temp_list[12] / temp_list[11], 1)
        rows1.append(tuple(temp_list))

    for i in range(len(rows1)-1):
        for j in range(len(rows1) - 1 - i):
            if rows1[j][5] < rows1[j+1][5]:
                temp_list = list(rows1)    
                temp_list[j], temp_list[j+1] = temp_list[j+1], temp_list[j]
                rows1 = tuple(temp_list)
    return render_template("user_search_top_rated.html", rows1 = rows1)

# --------------------------------------------
if __name__ == '__main__':
    app.run(debug = True, port = 200)