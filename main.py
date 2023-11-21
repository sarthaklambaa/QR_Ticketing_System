from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode, os, random, string
import reportlab
from reportlab.pdfgen import canvas
from PIL import Image
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_ticketing.db'
db = SQLAlchemy(app)

class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(10), unique=True, nullable=False)
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

        ticket_id = generate_ticket_id()

        form_data = FormData(ticket_id=ticket_id, f_name=f_name, l_name=l_name, dob=dob, phone_number=phone_number)

        db.session.add(form_data)
        db.session.commit()

        generate_qr_code(ticket_id, f_name, l_name, dob)
        # return redirect(url_for('get_data'))
        return render_template("success.html", ticket_id=ticket_id)
    return render_template("index.html")

def generate_ticket_id():
    random_id = ''.join(random.choices(string.digits, k=10))
    return random_id

def generate_qr_code(ticket_id, f_name, l_name, dob):
    data = f'Ticket ID: {ticket_id}\nName: {f_name} {l_name}\nDOB: {dob.strftime("%Y-%m-%d")}'
    img = qrcode.make(data)
    img.save(f"static/qrcodes/{ticket_id}.png")

@app.route("/get", methods=['GET'])
def get_data():
    data = FormData.query.all()
    return render_template("get_data.html", data=data)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/pdf/<ticket_id>")
def download_pdf(ticket_id):
    pdf_filename = f"ticket_{ticket_id}.pdf"
    pdf_path = generate_pdf(ticket_id, pdf_filename)
    return send_file(pdf_path, as_attachment=True)

def generate_pdf(ticket_id, filename):
    pdf_path = os.path.join(app.root_path, filename)
    c = canvas.Canvas(pdf_path)

    # Get form data for the specific ticket_id
    form_data = FormData.query.filter_by(ticket_id=ticket_id).first()

    if form_data:
        c.drawString(100, 750, f"Ticket ID: {form_data.ticket_id}")
        c.drawString(100, 730, f"Name: {form_data.f_name} {form_data.l_name}")
        c.drawString(100, 710, f"DOB: {form_data.dob.strftime('%Y-%m-%d')}")
        c.drawString(100, 690, f"Phone Number: {form_data.phone_number}")

        img_path = f"static/qrcodes/{form_data.ticket_id}.png"
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            img_width = 100
            img_height = img_width / aspect_ratio
            c.drawInlineImage(img_path, 100, 660 - img_height, width=img_width, height=img_height)

        c.showPage()
        c.save()

    return pdf_path

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
