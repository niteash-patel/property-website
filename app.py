from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user
)

import os

app = Flask(__name__)

app.secret_key = "dreamhome_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['UPLOAD_FOLDER'] = 'static/uploads'

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Upload folder create
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# ---------------- LOGIN SYSTEM ---------------- #

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


class User(UserMixin):
    id = 1


@login_manager.user_loader
def load_user(user_id):
    return User()


# ---------------- DATABASE ---------------- #

class Property(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))

    price = db.Column(db.String(100))

    location = db.Column(db.String(200))

    images = db.Column(db.Text)


# ---------------- HOME ---------------- #

@app.route('/')
def home():

    properties = Property.query.all()

    return render_template(
        'index.html',
        properties=properties,
        current_user=current_user
    )


# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        # CHANGE USERNAME & PASSWORD HERE
        if username == "Ravi" and password == "Ravi@1122":

            login_user(User())

            return redirect('/')

    return render_template('login.html')


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect('/')


# ---------------- ADD PROPERTY ---------------- #

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_property():

    if request.method == 'POST':

        title = request.form['title']

        price = request.form['price']

        location = request.form['location']

        files = request.files.getlist('image')

        # Maximum 10 Images
        if len(files) > 10:

            return "Maximum 10 images allowed"

        image_names = []

        for file in files:

            if file.filename != '':

                filename = secure_filename(file.filename)

                file.save(
                    os.path.join(
                        app.config['UPLOAD_FOLDER'],
                        filename
                    )
                )

                image_names.append(filename)

        new_property = Property(

            title=title,

            price=price,

            location=location,

            images=','.join(image_names)

        )

        db.session.add(new_property)

        db.session.commit()

        return redirect('/')

    return render_template('add_property.html')


# ---------------- DELETE PROPERTY ---------------- #

@app.route('/delete/<int:id>')
@login_required
def delete_property(id):

    property = Property.query.get_or_404(id)

    image_list = property.images.split(',')

    for img in image_list:

        image_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            img
        )

        if os.path.exists(image_path):

            os.remove(image_path)

    db.session.delete(property)

    db.session.commit()

    return redirect('/')


# ---------------- RUN ---------------- #

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5001)