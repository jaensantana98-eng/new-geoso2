import tkinter as tk
from tkinter import ttk, messagebox
import interfaz_noticias
import interfaz_agenda
import interfaz_carrusel
import interfaz_entidades_colaboradoras
import interfaz_quienessomos
import interfaz_pagina_web
import interfaz_publicaciones
import interfaz_rafagas
import interfaz_proyectos
import os
import json
import webbrowser
from jinja2 import Environment, FileSystemLoader


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Geoso2")
        self.geometry("500x250")

        ttk.Label(self, text="Selecciona una opción:", font=("Segoe UI", 14, "bold")).pack(pady=20)

        btns = ttk.Frame(self)
        btns.pack(pady=10)

        ttk.Button(btns, text="Editar sitio web", width=18,
                   command=lambda: self.open_section_menu("edit")).grid(row=0, column=0, padx=10)

        ttk.Button(btns, text="Generar sitio web", width=18,
                   command=self.generar_sitio_web).grid(row=2, column=0, padx=10, pady=20)

        ttk.Label(self, text="© Creado por Jesús Jaén Santana v.1.0/2025",
                  font=("Segoe UI", 10, "italic")).pack(side="bottom", pady=10)

    # -----------------------------
    # Ventana de selección
    # -----------------------------
    def open_section_menu(self, mode):
        win = tk.Toplevel(self)
        win.title("Selecciona la sección")
        win.geometry("400x600")

        ttk.Label(win,
                  text="Selecciona el JSON a editar:",
                  font=("Segoe UI", 12, "bold")).pack(pady=15)

        frm = ttk.Frame(win)
        frm.pack(pady=10)

        ttk.Label(frm, text="Gestionar imágenes de:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(frm, text="Carrusel", width=20,
                   command=lambda: self.abrir_carrusel(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Entidades Colaboradoras", width=20,
                   command=lambda: self.abrir_entidades_colaboradoras(mode, win)).pack(pady=4)

        ttk.Separator(frm).pack(fill="x", pady=8)

        ttk.Label(frm, text="Secciones de la página principal:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(frm, text="Noticias", width=20,
                   command=lambda: self.abrir_noticias(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Agenda", width=20,
                   command=lambda: self.abrir_agenda(mode, win)).pack(pady=4)

        ttk.Separator(frm).pack(fill="x", pady=8)

        ttk.Label(frm, text="Otras secciones:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(frm, text="Ráfagas", width=20,
                   command=lambda: self.abrir_rafagas(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Proyectos", width=20,
                   command=lambda: self.abrir_proyectos(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Quienes Somos", width=20,
                   command=lambda: self.abrir_quienes_somos(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Publicaciones", width=20,
                   command=lambda: self.abrir_publicaciones(mode, win)).pack(pady=4)

        ttk.Separator(frm).pack(fill="x", pady=8)

        ttk.Label(frm, text="Gestión de Página Web:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(frm, text="Página Web", width=20,
                   command=lambda: self.abrir_pagina_web(mode, win)).pack(pady=4)

    # -----------------------------
    # Métodos abre-directo
    # -----------------------------
    def abrir_json_directo(self, mode, parent_win, filename):
        parent_win.destroy()

        ruta = f"geoso2-web-template/json/{filename}.json"

        if mode == "edit" and not os.path.exists(ruta):
            messagebox.showerror("Error", f"No se encontró el archivo:\n{ruta}")
            return None

        return ruta

    def abrir_noticias(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_noticias.NoticiasWindow(mode=mode, filepath=ruta)

    def abrir_agenda(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_agenda.EditorWindow(mode=mode, filepath=ruta)

    def abrir_rafagas(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_rafagas.EditorRafagasWindow(filepath=ruta)

    def abrir_proyectos(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_proyectos.EditorProyectosWindow(filepath=ruta)

    def abrir_quienes_somos(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_quienessomos.EditorWindow(mode=mode, filepath=ruta)

    def abrir_publicaciones(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_publicaciones.EditorWindow(mode=mode, filepath=ruta)

    def abrir_carrusel(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_carrusel.CarruselWindow(mode=mode, filepath=ruta)

    def abrir_entidades_colaboradoras(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_entidades_colaboradoras.EntidadesWindow(mode=mode, filepath=ruta)

    def abrir_pagina_web(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_pagina_web.paginaWindow(mode=mode, filepath=ruta)

    # Generar sitio web
    # -----------------------------
    def generar_sitio_web(self):
        try:
            # ============================
            # CARGAR JSON PRINCIPAL
            # ============================
            with open("geoso2-web-template/json/web.json", "r", encoding="utf-8") as f:
                datos = json.load(f)

            web = datos["web"]

            # ============================
            # ENTORNO JINJA
            # ============================
            env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))

            # ============================
            # CARPETA DE SALIDA
            # ============================
            output_dir = "geoso2-web-template/output"
            os.makedirs(output_dir, exist_ok=True)

            # ============================================================
            # INDEX (PÁGINA PRINCIPAL)
            # ============================================================
            template_index = env.get_template("index_page.html")

            html_index = template_index.render(
                index_page={
                    "carousel": web["index_page"].get("carrusel", []),
                    "noticias": web["index_page"].get("noticias", []),
                    "agenda": web["index_page"].get("agenda", []),
                    "colaboradores": web["index_page"].get("entidades", [])
                }
            )

            with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(html_index)

            # ============================================================
            # CARRUSEL
            # ============================================================
            if os.path.exists("geoso2-web-template/templates/carrusel.html"):
                template_carrusel = env.get_template("carrusel.html")
                html_carrusel = template_carrusel.render(
                    carrusel=web["index_page"].get("carrusel", [])
                )
                with open(os.path.join(output_dir, "carrusel.html"), "w", encoding="utf-8") as f:
                    f.write(html_carrusel)

            # ============================================================
            # NOTICIAS (PÁGINA PROPIA)
            # ============================================================
            if os.path.exists("geoso2-web-template/templates/noticias.html"):
                template_noticias = env.get_template("noticias.html")
                html_noticias = template_noticias.render(
                    noticias = web["index_page"].get("noticias", [])
                )
                with open(os.path.join(output_dir, "noticias.html"), "w", encoding="utf-8") as f:
                    f.write(html_noticias)


            # ============================================================
            # PROYECTOS
            # ============================================================
            if os.path.exists("geoso2-web-template/templates/proyectos.html"):
                template_proyectos = env.get_template("proyectos.html")
                html_proyectos = template_proyectos.render(
                    proyectos=web.get("proyectos", {})
                )
                with open(os.path.join(output_dir, "proyectos.html"), "w", encoding="utf-8") as f:
                    f.write(html_proyectos)

            # ============================================================
            # PUBLICACIONES
            # ============================================================
            if os.path.exists("geoso2-web-template/templates/publicaciones.html"):
                template_publicaciones = env.get_template("publicaciones.html")
                html_publicaciones = template_publicaciones.render(
                    publicaciones=web.get("publicaciones", {})
                )
                with open(os.path.join(output_dir, "publicaciones.html"), "w", encoding="utf-8") as f:
                    f.write(html_publicaciones)

            # ============================================================
            # QUIÉNES SOMOS
            # ============================================================
            if os.path.exists("geoso2-web-template/templates/quienes_somos.html"):
                template_qs = env.get_template("quienes_somos.html")
                html_qs = template_qs.render(
                    quienes_somos=web.get("quienes_somos", {})
                )
                with open(os.path.join(output_dir, "quienes_somos.html"), "w", encoding="utf-8") as f:
                    f.write(html_qs)

            # ============================================================
            # RÁFAGAS
            # ============================================================
            if os.path.exists("geoso2-web-template/templates/rafagas.html"):
                template_rafagas = env.get_template("rafagas.html")
                html_rafagas = template_rafagas.render(
                    rafagas=web.get("pagina1", {}).get("rafagas", [])
                )
                with open(os.path.join(output_dir, "rafagas.html"), "w", encoding="utf-8") as f:
                    f.write(html_rafagas)

            # ============================================================
            # ENTIDADES COLABORADORAS (PÁGINA PROPIA)
            # ============================================================
            if os.path.exists("geoso2-web-template/templates/entidades.html"):
                template_entidades = env.get_template("entidades.html")
                html_entidades = template_entidades.render(
                    entidades=web["index_page"].get("entidades", [])
                )
                with open(os.path.join(output_dir, "entidades.html"), "w", encoding="utf-8") as f:
                    f.write(html_entidades)

            # ============================================================
            # PÁGINAS WEB (cada página individual)
            # ============================================================
            if os.path.exists("geoso2-web-template/templates/pagina.html"):
                template_pagina = env.get_template("pagina.html")

                paginas = web.get("paginas", [])

                for pagina in paginas:
                    # Renderizar HTML de la página
                    html_pagina = template_pagina.render(pagina=pagina)

                    # Nombre del archivo basado en el ID
                    nombre_archivo = f"{pagina['id']}.html"

                    with open(os.path.join(output_dir, nombre_archivo), "w", encoding="utf-8") as f:
                        f.write(html_pagina)

            # ============================================================
            # LIMPIAR PÁGINAS ANTIGUAS DEL OUTPUT
            # ============================================================
            paginas_json = {p["id"] + ".html" for p in web.get("paginas", [])}

            for archivo in os.listdir(output_dir):
                if archivo.startswith("pagina_") and archivo.endswith(".html"):
                    if archivo not in paginas_json:
                        os.remove(os.path.join(output_dir, archivo))

            # ============================================================
            # FIN
            # ============================================================
            messagebox.showinfo("Éxito", "Sitio web generado correctamente.")

            index_path = os.path.abspath(os.path.join(output_dir, "index.html"))
            webbrowser.open(f"file:///{index_path}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el sitio web:\n{e}")




if __name__ == "__main__":
        app = MainApp()
        app.mainloop()
