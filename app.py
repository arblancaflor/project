from flask import Flask, request, url_for, redirect, session, render_template
import sqlite3  # allows to connect and use a database

app = Flask(__name__)

# Configuration for app starts here
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "Thissithesecretkey!"
# Configuration ends here

def connect_db():
    conn = sqlite3.connect("users_db.db")
    return conn

def read_all_users():
    # Read all contents of user table

    #end of db transactionconn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    results = cur.fetchall()
    cur.close()

    return results

@app.route("/", defaults= {"name" : "User"})
@app.route("/<name>", methods=["POST", "GET"])
def home(name):
    session["name"] = name

    return render_template("home.html", name=session["name"], )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/form", methods=["POST", "GET"])
def form():
    if request.method == "GET":
        return render_template("form.html")
    elif request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        conn = connect_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (name,password) VALUES (?,?)', (name,password)) # ? to prevent sql injection
        conn.commit() # because sqlite is transactional
        cur.close()

        if name == '':
            return redirect(url_for('unsuccessful'))
        else:
            return redirect(url_for("home", name=name))

@app.route('/edit',methods=["POST","GET"])
def edit():
    if request.method == "GET":
        edit_id = request.args.get("edit")
        # Retrieve that record
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE id = ?',(edit_id))
        result = cur.fetchone()
        cur.close()
        #done

        return render_template('edit.html',result=result)
    elif request.method == 'POST':
        new_name = request.form["name"]
        new_password = request.form["password"]
        edit_id = request.form["id"]

        if request.form["edit"] == "update":
            #Update the record
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('UPDATE users SET name = ?, password = ? WHERE id = ?',(new_name,new_password,edit_id))
            conn.commit()
            cur.close()
            #end of DB transaction
        elif request.form["edit"] == "delete":
            #Delete the record
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('DELETE FROM users WHERE id = ?',(edit_id))
            conn.commit()
            cur.close()
            #end of DB transaction

        results = read_all_users()
        return render_template('showall.html',results=results)

@app.route('/unsuccessful')
def unsuccessful():
    return "<h1>Username not found</h1>"

@app.route('/showall')
def showall():
    # Read all contents of user table
    results = read_all_users()
    #end of db transaction

    return render_template('showall.html', results=results)

@app.route("/logout")
def logout():
    session.pop("name", None)
    return redirect(url_for(render_template("home.html")))

if __name__ == "__main__":
    app.run()
