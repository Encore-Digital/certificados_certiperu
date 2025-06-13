import csv
import random
import string
import os
import qrcode

# Configuración
CARPETA_SITIO = "."
CARPETA_QRS = "qrs"
PLANTILLA_HTML = "plantilla.html"
CSV_ENTRADA = "certificados.csv"
CSV_SALIDA = "codigos.csv"
EXTENSION_URL = ".html"

# Crear carpetas necesarias
os.makedirs(CARPETA_SITIO, exist_ok=True)
os.makedirs(CARPETA_QRS, exist_ok=True)

# Generar código único de 6 dígitos
def generar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Leer certificados
certificados = []
with open(CSV_ENTRADA, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        certificados.append(row)

# Escribir resultados
with open(CSV_SALIDA, 'w', newline='', encoding='utf-8') as csvfile_out:
    fieldnames = ['nombre', 'curso', 'codigo', 'url']
    writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
    writer.writeheader()

    # Generar página por certificado
    for cert in certificados:
        nombre = cert['nombre']
        curso = cert['curso']
        codigo = generar_codigo()
        filename = f"{codigo}{EXTENSION_URL}"
        filepath = os.path.join(CARPETA_SITIO, filename)

        # Reemplazar variables en la plantilla
        with open(PLANTILLA_HTML, 'r', encoding='utf-8') as plantilla_file:
            contenido = plantilla_file.read()
            contenido = contenido.replace("[NOMBRE]", nombre)
            contenido = contenido.replace("[CURSO]", curso)
            contenido = contenido.replace("[CODIGO]", codigo)
            contenido = contenido.replace("[PDF]", f"pdfs/{codigo}.pdf")

        # Guardar página
        with open(filepath, 'w', encoding='utf-8') as salida_file:
            salida_file.write(contenido)

        # Generar QR
        url_final = f"https://certiperu.com/certificados/{codigo}" 
        qr = qrcode.make(url_final)
        qr.save(os.path.join(CARPETA_QRS, f"{codigo}_{nombre}.png"))

        # Guardar en CSV
        writer.writerow({
            'nombre': nombre,
            'curso': curso,
            'codigo': codigo,
            'url': url_final
        })

        print(f"{nombre} -> {codigo}")

print("Páginas generadas correctamente.")