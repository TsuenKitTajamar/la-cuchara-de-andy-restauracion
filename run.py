from flask import Flask, render_template
from app import create_app
import webbrowser
from threading import Timer

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

def open_browser():
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    try:
        app = create_app()
        print("Aplicación Flask creada exitosamente")
        Timer(1.5, open_browser).start()
        print("Iniciando servidor Flask...")
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Error al iniciar la aplicación: {str(e)}")
