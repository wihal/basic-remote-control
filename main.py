from flask import Flask, render_template, Response, request, redirect, url_for
from PIL import ImageGrab
import time
from io import BytesIO
import pyautogui
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pyotp

# ------------------------------------------------------------------------------
#   Tunnel for hosting on localhost 
#
#   docs: https://localhost.run/docs/
#
#   ssh -R 80:127.0.0.1:5000 localhost.run
# ------------------------------------------------------------------------------

app = Flask(__name__)

app.config['SECRET_KEY'] = 'YKRTE3MO4AIH2QH5YKRTE3MO4AIH2QH5'
login_manager = LoginManager(app)

# Simulierte Benutzerdaten
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Simulierte Benutzerdatenbank
users = {1: User(1)}

# Geheimschlüssel für TOTP
secret_keys = {1: 'LXN6C66YJHH4BPBEMXOPYUL7RMHXATH7ODC2ZH7UH4R5PFUF6WJ2ZKBBPTZRZGHCMWKONZTY6IC7JPZHLRWN2JQ42C24EAWC5RGSB2I'}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def login():
    error_message = ''
    if request.method == 'POST':
        user_id = 1
        if user_id in secret_keys.keys():
            totp = pyotp.TOTP(secret_keys[user_id])

            # Lädt alle nummern aus dem Formular und kombiniert sie
            totp_code = ''.join([request.form[f'code{i+1}'] for i in range(6)]) 
            if totp.verify(totp_code):
                user = load_user(user_id)
                login_user(user)
                return home() # Lädt die home Seite
            else:
                error_message = 'Falscher TOTP-Code'
        else:
            error_message = 'Ungültige Benutzer-ID'
    return error_message

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

def generate():
    while True:
        screenshot = ImageGrab.grab()
        img_bytes = BytesIO()
        screenshot.save(img_bytes, format='JPEG')
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_bytes.getvalue() + b'\r\n')

        time.sleep(0.04347)

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Events
@app.route('/mouse_event', methods=['POST'])
def mouse_event():
    x = int(request.form['x'])
    y = int(request.form['y'])

    pyautogui.mouseDown(y=y, x=x)
    time.sleep(0.1)
    pyautogui.mouseUp()

    return '', 204  # Leerer Response mit Statuscode 204 (No Content)

@app.route('/keydown_event', methods=['POST'])
def keyboard_down():

    key = request.form['key']
    pyautogui.keyDown(key)

    return '', 204 

@app.route('/keyup_event', methods=['POST'])
def keyboard_up():
    key = request.form['key']
    print(f"key up: {key}")
    pyautogui.keyUp(key)

    return '', 204

if __name__ == '__main__':
    app.run()