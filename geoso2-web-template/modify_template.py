#!/usr/bin/env python3
"""
Script para modificar un template HTML usando Jinja2
"""
import os
import json
from jinja2 import Template, Environment, FileSystemLoader
from datetime import datetime

def main():

    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, "templates")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    env = Environment(loader=FileSystemLoader(templates_dir))

    with open(os.path.join(base_dir, "datos.json"), "r", encoding="utf-8") as f:
        datos = json.load (f)
    
    datos['fecha'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    imagenes = [
        "img/foto1.jpg",
        "img/foto2.png",
        "img/foto3.png",
        "img/foto4.jpg",
        "img/foto5.jpg",
        "img/foto6.jpg"
    ]
    datos['imagenes'] = imagenes


    templates_a_generar = [
         ("index.html", "index.html"),
        ("carrusel.html", "carrusel.html"),
        ("quienes-somos.html", "quienes-somos.html"),
        ("publicaciones.html", "publicaciones.html"),
        ("contacto.html", "contacto.html"),
        ("geocoopera.html", "geocoopera.html"),
         ("navbar.html", "navbar.html")
    ]

    for tpl_name, salida in templates_a_generar:
        template = env.get_template(tpl_name)
        html_generado = template.render(datos)
        with open(os.path.join(output_dir, salida), "w", encoding="utf-8") as f:
            f.write(html_generado)
    print(f"Pagina generada correctamente: {salida}")

    # Leer el template
    with open('template.html', 'r', encoding='utf-8') as file:
        template_content = file.read()

    # Crear el objeto Template de Jinja2
    template = Template(template_content)

    # Leer datos desde el archivo JSON
    with open('datos.json', 'r', encoding='utf-8') as file:
        datos = json.load(file)

    # Agregar la fecha actual (se genera dinámicamente)
    datos['fecha'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    # Renderizar el template con los datos
    html_generado = template.render(datos)

    # Guardar el resultado en output.html
    with open('output.html', 'w', encoding='utf-8') as file:
        file.write(html_generado)

    print('✓ Template procesado exitosamente')
    print('✓ Archivo generado: output.html')

if __name__ == '__main__':
    main()
