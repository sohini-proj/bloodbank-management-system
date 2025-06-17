from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',     # replace with your MySQL username
        password='root', # replace with your MySQL password
        database='bloodbank'
    )

@app.route('/')
def index():
    return render_template('index.html')

# ------------------ Blood Types ------------------
@app.route('/blood_types')
def blood_types():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Blood_Type")
    blood_types = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('blood_types.html', blood_types=blood_types)

# ------------------ Donors ------------------
@app.route('/donors')
def donors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.donor_id, d.first_name, d.last_name, d.dob, d.gender, b.blood_type, d.contact_number, d.email, d.address, d.registration_date
        FROM Donors d
        LEFT JOIN Blood_Type b ON d.blood_type_id = b.blood_type_id
    """)
    donors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('donors.html', donors=donors)

@app.route('/add_donor', methods=['GET', 'POST'])
def add_donor():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT blood_type_id, blood_type FROM Blood_Type")
    blood_types = cursor.fetchall()

    if request.method == 'POST':
        data = (
            request.form['first_name'],
            request.form['last_name'],
            request.form['dob'],
            request.form['gender'],
            request.form['blood_type_id'],
            request.form['contact_number'],
            request.form['email'],
            request.form['address'],
            request.form['registration_date']
        )
        cursor.execute("""
            INSERT INTO Donors (first_name, last_name, dob, gender, blood_type_id, contact_number, email, address, registration_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('donors'))
    cursor.close()
    conn.close()
    return render_template('add_donor.html', blood_types=blood_types)

@app.route('/delete_donor/<int:donor_id>')
def delete_donor(donor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Donors WHERE donor_id=%s", (donor_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('donors'))

# ------------------ Blood Inventory ------------------
@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.blood_type, i.quantity
        FROM Blood_Inventory i
        JOIN Blood_Type b ON i.blood_type_id = b.blood_type_id
    """)
    inventory = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inventory.html', inventory=inventory)

# ------------------ Donations ------------------
@app.route('/donations')
def donations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.donation_id, d.donation_date, b.blood_type, dm.first_name, dm.last_name, d.quantity
        FROM Donations d
        JOIN Blood_Type b ON d.blood_type_id = b.blood_type_id
        JOIN Donors dm ON d.donor_id = dm.donor_id
    """)
    donations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('donations.html', donations=donations)

@app.route('/add_donation', methods=['GET', 'POST'])
def add_donation():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.donor_id, d.first_name, d.last_name, b.blood_type 
        FROM Donors d
        JOIN Blood_Type b ON d.blood_type_id = b.blood_type_id
    """)
    donors = cursor.fetchall()

    if request.method == 'POST':
        try:
            # Get the blood type ID from the donor
            cursor.execute("""
                SELECT blood_type_id FROM Donors 
                WHERE donor_id = %s
            """, (request.form['donor_id'],))
            donor_blood_type = cursor.fetchone()[0]
            
            data = (
                request.form['donor_id'],
                request.form['donation_date'],
                donor_blood_type,  # Use donor's blood type
                request.form['quantity']
            )
            
            # Insert donation
            cursor.execute("""
                INSERT INTO Donations (donor_id, donation_date, blood_type_id, quantity)
                VALUES (%s, %s, %s, %s)
            """, data)

            # Update Inventory
            try:
                cursor.execute("""
                    INSERT INTO Blood_Inventory (blood_type_id, quantity)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE quantity = quantity + %s
                """, (donor_blood_type, request.form['quantity'], request.form['quantity']))
            except Exception as e:
                print(f"Error updating inventory: {str(e)}")
            
            cursor.close()
            conn.commit()
            print(f"Successfully added donation and updated inventory for blood type ID: {donor_blood_type}")
            
            conn.close()
            return redirect(url_for('donations'))
            
        except Exception as e:
            print(f"Error processing donation: {str(e)}")
            cursor.close()
            conn.close()
            return f"Error processing donation: {str(e)}", 500

    cursor.close()
    conn.close()
    return render_template('add_donation.html', donors=donors)

# ------------------ Recipients ------------------
@app.route('/recipients')
def recipients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.recipient_id, r.first_name, r.last_name, r.dob, r.contact_number, r.email, r.address, b.blood_type, r.received_date
        FROM Recipients r
        LEFT JOIN Blood_Type b ON r.blood_type_id = b.blood_type_id
    """)
    recipients = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('recipients.html', recipients=recipients)

@app.route('/add_recipient', methods=['GET', 'POST'])
def add_recipient():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT blood_type_id, blood_type FROM Blood_Type")
    blood_types = cursor.fetchall()

    if request.method == 'POST':
        data = (
            request.form['first_name'],
            request.form['last_name'],
            request.form['dob'],
            request.form['contact_number'],
            request.form['email'],
            request.form['address'],
            request.form['blood_type_id'],
            request.form['received_date']
        )
        cursor.execute("""
            INSERT INTO Recipients (first_name, last_name, dob, contact_number, email, address, blood_type_id, received_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('recipients'))
    cursor.close()
    conn.close()
    return render_template('add_recipient.html', blood_types=blood_types)

# Add more routes as needed...

if __name__ == '__main__':
    print("✅ Flask app is starting...")

    app.run(debug=True)
