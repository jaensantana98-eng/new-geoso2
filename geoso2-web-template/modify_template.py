#!/usr/bin/env python3
import json
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, "templates")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    print("Usando templates dir:", templates_dir)

    # Inicializar Jinja2 con la ruta correcta
    env = Environment(loader=FileSystemLoader(templates_dir))

    # --- Carrusel ---
    imagenes = [
        "img/foto1.jpg",
        "img/foto2.png",
        "img/foto3.png",
        "img/foto4.jpg",
        "img/foto5.jpg",
        "img/foto6.jpg"
    ]
    template_carrusel = env.get_template("carrusel.html")
    html_carrusel = template_carrusel.render(imagenes=imagenes)
    with open(os.path.join(output_dir, "carrusel.html"), "w", encoding="utf-8") as f:
        f.write(html_carrusel)
    print("✓ Carrusel generado: output/carrusel.html")

    # --- Template con JSON ---
    template_datos = env.get_template("template.html")
    with open(os.path.join(base_dir, "datos.json"), "r", encoding="utf-8") as file:
        datos = json.load(file)
    datos['fecha'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    html_generado = template_datos.render(datos)
    with open(os.path.join(output_dir, "output.html"), "w", encoding="utf-8") as file:
        file.write(html_generado)

    print("✓ Template procesado exitosamente: output/output.html")

if __name__ == '__main__':
    main()
