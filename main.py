from flask import Flask, request, jsonify, render_template, redirect
import mysql.connector
import stripe
app = Flask(__name__)
stripe.api_key = 'sk_test_51NdGfwSH8lu44vb8Ss5VsJy58ncGFku2eHqRKh2Ehte5XrYND2dvCC6c6QDgTqUFzSghq2n0fWSPI9EUQ313tN6f00n6ym3MuC'


# MySQL configs
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="stripe"
)

# Plans data
plans = [
  {'name':'Basic', 'monthly':100, 'yearly':1000, 'quality':'Good', 'resolution':'480p', 'devices':'Phone', 'screens':1},
  {'name':'Standard', 'monthly':200, 'yearly':2000, 'quality':'Good', 'resolution':'720p', 'devices':'Phone+Tablet', 'screens':3},
  {'name':'Premium', 'monthly':500, 'yearly':5000, 'quality':'Better', 'resolution':'1080p', 'devices':'Phone+Tablet+Computer', 'screens':5},
  {'name':'Regular', 'monthly':700, 'yearly':7000, 'quality':'Best', 'resolution':'4K+HDR', 'devices':'Phone+Tablet+TV', 'screens':10}
]
@app.route('/')
@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    # Get form data
    name = request.form['name']
    email = request.form['email']  
    password = request.form['password']
    
    # Save user to database
    cursor = mydb.cursor()
    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
    values = (name, email, password)
    cursor.execute(query, values)
    mydb.commit()
    cursor.close()
    
    return render_template('login.html')
  
  return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])  
def login():
  if request.method == 'POST':
    # Get form data
    email = request.form['email']
    password = request.form['password']

    # Verify user credentials
    
    cursor = mydb.cursor()
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    values = (email, password)
    cursor.execute(query, values)
    user = cursor.fetchone()
    cursor.close()
    
    
    if user:
      return render_template('plans.html', plans=plans, email=email, name=user[1])
    else:
      return render_template('login.html', error='Invalid email or password')

  return render_template('login.html')
@app.route('/subscribe', methods=['POST'])
def subscribe():
  email = request.form['email']
  name = request.form['name']

  customer = stripe.Customer.create(email=email, name=name)
  customer_id = customer['id']

  cursor = mydb.cursor()
  query = "INSERT INTO customers (id, email, name) VALUES (%s, %s, %s)"
  values = (customer_id, email, name)
  
  cursor.execute(query, values)
  mydb.commit()
  cursor.close()

  plan = request.form['plan']

  cursor = mydb.cursor()
  user_query = "SELECT id FROM users WHERE email = %s"
  cursor.execute(user_query, (email,))
  
  results = cursor.fetchall()
  user_id = results[0]

  sub = stripe.Subscription.create(customer=customer_id, items=[{'plan': plan}])
  
  sub_id = sub['id']

  cursor = mydb.cursor()
  sub_query = "INSERT INTO subscriptions (user_id, stripe_sub) VALUES (%s, %s)"
  sub_values = (user_id, sub_id)
  
  cursor.execute(sub_query, sub_values)
  mydb.commit()
  cursor.close()

  return render_template('subscribe_success.html')
@app.route('/cancel/<string:sub_id>', methods=['GET'])
def cancel(sub_id):
    # Cancel subscription in Stripe
    stripe.Subscription.delete(sub_id)

    # Update database
    cursor = mydb.cursor()
    query = "UPDATE subscriptions SET active=0 WHERE stripe_sub=%s"
    values = (sub_id,)
    cursor.execute(query, values)
    mydb.commit()
    cursor.close()
   

    return render_template('unsubscribe_success.html')

if __name__ == '__main__':
    app.run(debug=True)
