from flask import Flask, render_template, request, send_from_directory
import subprocess
import csv
import os
import sys
import io
import zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET', 'POST'])
def cargar_csv():
    datos = []
    if request.method == 'POST':
        archivo = request.files['archivo']
        if not archivo or archivo.filename == '':
            return "❌ No se seleccionó ningún archivo", 400

        ruta_csv = 'certificados.csv'
        archivo.save(ruta_csv)

        with open(ruta_csv, newline='', encoding='utf-8') as csvfile:
            lector = csv.DictReader(csvfile)
            for fila in lector:
                datos.append(fila)

        return render_template('index.html', datos=datos)

    return render_template('index.html', datos=datos)


@app.route('/generar', methods=['POST'])
def ejecutar_generar():
    try:
        resultado = subprocess.run(
            [sys.executable, 'generar.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        # Crear ZIP automáticamente
        zip_path = os.path.join(BASE_DIR, 'certificados_generados.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Agregar QR
            qrs_dir = os.path.join(BASE_DIR, 'qrs')
            for archivo in os.listdir(qrs_dir):
                zf.write(os.path.join(qrs_dir, archivo), os.path.join('qrs', archivo))

            # Agregar PDFs y HTML
            for archivo in os.listdir(BASE_DIR):
                if archivo.endswith('.pdf') or archivo.endswith('.html') or archivo == 'codigos.csv':
                    zf.write(os.path.join(BASE_DIR, archivo), archivo)

        salida = "✅ Certificados generados. Puedes <a href='/descargar_zip' target='_blank'>descargar el ZIP aquí</a>."
    except subprocess.CalledProcessError as e:
        salida = (
            "❌ Error al generar certificados:<br>"
            f"STDOUT:<br>{e.stdout.decode('utf-8', errors='replace')}<br>"
            f"STDERR:<br>{e.stderr.decode('utf-8', errors='replace')}"
        )
    except Exception as e:
        salida = f"❌ Error inesperado: {str(e).encode('utf-8', errors='replace').decode('utf-8', errors='replace')}"
    return render_template('index.html', datos=[], resultado=salida)

@app.route('/descargar_zip')
def descargar_zip():
    return send_from_directory(BASE_DIR, 'certificados_generados.zip', as_attachment=True)

if __name__ == '__main__':
    import webbrowser
    webbrowser.open("http://localhost:5000")
    app.run(debug=True)