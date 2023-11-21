from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_ticket.db'
db = SQLAlchemy(app)

class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(50), nullable=False)
    l_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        phone_number = request.form['phone_number']

        form_data = FormData(f_name=f_name, l_name=l_name, dob=dob, phone_number=phone_number)

        db.session.add(form_data)
        db.session.commit()

        return redirect(url_for('get_data'))

    return render_template("index.html")

@app.route("/get", methods=['GET'])
def get_data():
    data = FormData.query.all()
    return render_template("get_data.html", data=data)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
