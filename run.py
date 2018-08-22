from blog import app
import os

# Create random secret key
app.secret_key = os.urandom(24)

# Run app in production mode
#port = int(os.environ.get('PORT', 5000))
#app.run(host='0.0.0.0', port=port)

# Run app in debug mode
app.run(debug=True)
