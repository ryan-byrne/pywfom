from flask import Flask

app = Flask(__name__)

@app.route('/list_ports')
def say_hello():
    return {"ports":control.list_ports()}

# View mouse information
@app.route('/view/<mouse_id>')
def view_mouse(mouse_id):
    return ""

# View the mouse runs
@app.route('/view/<mouse_id>/<run_id>')
def view_run(mouse_id, run_id):
    return ""

# View the mouse runs
@app.route('/get/<category>')
def get_settings(category):
    if category == 'cameras':
        return {}
    elif category == 'arduino':
        return {}
    else:
        return {}
