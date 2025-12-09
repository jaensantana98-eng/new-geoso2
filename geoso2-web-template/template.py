#!/usr/bin/env python3
import json
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
import shutil

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, "templates")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    env = Environment(loader=FileSystemLoader(templates_dir))

    imagenes = [
        "img/foto1.jpg",
        "img/foto2.png",
        "img/foto3.png",
        "img/foto4.jpg",
        "img/foto5.jpg",
        "img/foto6.jpg"
    ]

    template_carrusel = env.get_template("carrusel.html")
    html_final = template_carrusel.render(imagenes=imagenes)

    output_html_path = os.path.join(output_dir, "carrusel.html")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_final)
    
    print("Pagina generada correctamente")

    shutil.copy(os.path.join(base_dir, "templates/styles.css"), output_dir)

    img_src = os.path.join(base_dir, "img")
    img_dst = os.path.join(output_dir, "img")
    if os.path.exists(img_dst):
        shutil.rmtree(img_dst)
    shutil.copytree(img_src, img_dst)

    logo_src = os.path.join(base_dir, "logo")
    logo_dst = os.path.join(output_dir, "logo")
    if os.path.exists(logo_dst):
        shutil.rmtree(logo_dst)
    shutil.copytree(logo_src, logo_dst)

if __name__ == '__main__':
    main()
