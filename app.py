from flask import Flask, render_template, redirect, url_for, request, session, flash
import mysql.connector

def get_db_connection():
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "131102",
        database = "hotel_db"
    )
    return db

app = Flask(__name__)

app.secret_key = 'tranductam'



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/check-availability', methods=['GET', 'POST'])
def check_availability():
    if request.method == 'POST' :
        session['check_in_date'] = request.form.get('check_in_date')
        session['check_out_date'] = request.form.get('check_out_date')

        if session.get('loggedin') :
            return redirect(url_for('rooms_checked'))
        else:
            return redirect(url_for('login'))
    return render_template('home.html')


@app.route('/rooms-checked')
def rooms_checked():
    db = get_db_connection()
    check_in_date = session.get('check_in_date')
    check_out_date = session.get('check_out_date')

    cursor = db.cursor(dictionary=True)
    cursor.execute('''SELECT * FROM rooms r WHERE r.room_number NOT IN (
                   SELECT room_number FROM reservations res WHERE res.check_in_date <= %s AND res.check_out_date >= %s
                   );
                   ''', (check_out_date, check_in_date))
    rooms_checked = cursor.fetchall()

    return render_template('rooms_checked.html', rooms_checked = rooms_checked)

    


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    db = get_db_connection()
    if request.method == 'POST':
        userEmail = request.form.get('email')
        userPassword = request.form.get('password')
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_email = %s AND user_password = %s", (userEmail, userPassword))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['user_name'] = user['user_name']
            session['user_id'] = user['user_id']
            session['user_email'] = user['user_email']
            cursor.close()
            db.close()
            if session.get('check_in_date') and session.get('check_out_date') :
                return redirect(url_for('rooms_checked'))
            else:
                return redirect(url_for('home'))
        else:
            message = 'Please enter correct Account/Password!'
    return render_template('login.html', message = message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    db = get_db_connection()
    if request.method == 'POST':
        userName = request.form.get('name')
        userPhone = request.form.get('phone')
        userEmail = request.form.get('email')
        userPassword = request.form.get('password')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE user_email = %s OR user_phone = %s', (userEmail, userPhone))
        user = cursor.fetchone()
        if user:
            message = 'Account already registered!'
        else:
            cursor.execute("INSERT INTO users(user_name, user_email, user_phone, user_password)  VALUES(%s, %s, %s, %s)", (userName, userEmail, userPhone, userPassword))
            db.commit()
            cursor.close()
            db.close()
            message = 'Account created successfully!'
    return render_template('register.html', message = message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('email', None)
    session.pop('check_in_date', None)
    session.pop('check_out_date', None)
    session.pop('made_a_reservation', None)
    return redirect(url_for('home'))



@app.route('/rooms')
def rooms():
    return render_template('rooms.html')





@app.route('/booking-history')
def booking_history():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT us')
    return render_template('history_booking.html')



@app.route('/online-payment')
def online_payment():
    return render_template('online_payment.html')

@app.route('/make-a-reservation', methods = ['GET', 'POST'])
def make_a_reservation():
    db = get_db_connection()
    if request.method == 'POST' :
        roomNumber = request.form.get('room_number')
        cursor = db.cursor()
        cursor.execute('INSERT INTO reservations (user_name, room_number, check_in_date, check_out_date) VALUES (%s, %s, %s, %s)', 
                       (session.get('user_name'), roomNumber, session.get('check_in_date'), session.get('check_out_date')))
        db.commit()
        cursor.close()
        db.close()
        flash ('You have successfully booked your room!')
    return redirect(url_for('online_payment'))


@app.route('/history-booking')
def history_booking():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('''SELECT r.room_type, r.room_number, res.check_in_date, res.check_out_date FROM reservations res 
                   INNER JOIN rooms r ON r.room_number = res.room_number WHERE res.user_name = %s''', (session.get('user_name'),))
    history_booking = cursor.fetchall()
    return render_template('history_booking.html', history_booking = history_booking)



@app.route('/cancel-room', methods = ['GET', 'POST'])
def cancel_room():
    db = get_db_connection()
    if request.method == 'POST':
        roomNumber = request.form.get('room_number')
        cursor = db.cursor()
        cursor.execute('DELETE FROM reservations WHERE room_number = %s AND user_name = %s', (roomNumber, session.get('user_name')))
        db.commit()
        cursor.close()
        db.close()
        flash('You have successfully canceled the room!')
        return redirect(url_for('home'))
    

if __name__ == '__main__':
    app.run(debug=True)