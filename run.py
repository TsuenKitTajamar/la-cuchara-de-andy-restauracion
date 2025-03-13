from flask import Flask, render_template, request
from app import create_app
import webbrowser
from threading import Timer

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    # Obtener la lista de archivos PDF de los restaurantes
    restaurant_pdfs = list_pdf_files()
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total = len(restaurant_pdfs)
    start = (page - 1) * per_page
    end = start + per_page
    pdf_files_paginated = restaurant_pdfs[start:end]
    
    return render_template('index.html', restaurant_pdfs=pdf_files_paginated, total=total, page=page, per_page=per_page)

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
