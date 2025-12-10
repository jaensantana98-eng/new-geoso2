import os
import json
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import shutil

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, "templates")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    env = Environment(loader=FileSystemLoader(templates_dir))

    with open(os.path.join(base_dir, "datos.json"), "r", encoding="utf-8") as f:
        datos = json.load(f)

    datos['fecha'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    datos['imagenes'] = [
        "img/foto1.jpg",
        "img/foto2.png",
        "img/foto3.png",
        "img/foto4.jpg",
        "img/foto5.jpg",
        "img/foto6.jpg"
    ]

    templates_a_generar = [
        
        ("index.html", "index.html"),
        ("carrusel.html", "carrusel.html"),
        ("quienes-somos.html", "quienes-somos.html"),
        ("publicaciones.html", "publicaciones.html"),
        ("contacto.html", "contacto.html"),
        ("geocoopera.html", "geocoopera.html"),
        ("navbar.html", "navbar.html"),
        ("rafagas.html", "rafagas.html"),
        ("rafaga_publicacion.html", "rafaga_publicacion.html"),
        ("proyectos.html", "proyectos.html"),
    ]

    for tpl_name, salida in templates_a_generar:
        template = env.get_template(tpl_name)
        html_generado = template.render(datos)
        with open(os.path.join(output_dir, salida), "w", encoding="utf-8") as f:
            f.write(html_generado)
        print(f"✓ Página generada correctamente: {salida}")

    css_file = os.path.join(templates_dir, "styles.css")
    if os.path.exists(css_file):
        shutil.copy(css_file, output_dir)
        print("✓ CSS actualizado en output: styles.css")

if __name__ == '__main__':
    main()
