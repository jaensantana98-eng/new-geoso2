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
        ruta = self.abrir_json_directo(mode, parent_win, "noticias")
        if ruta:
            interfaz_noticias.NoticiasWindow(mode=mode, filepath=ruta)

    def abrir_agenda(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "agenda")
        if ruta:
            interfaz_agenda.EditorWindow(mode=mode, filepath=ruta)

    def abrir_rafagas(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "rafagas")
        if ruta:
            interfaz_rafagas.EditorRafagasWindow(filepath=ruta)

    def abrir_proyectos(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "proyectos")
        if ruta:
            interfaz_proyectos.EditorProyectosWindow(filepath=ruta)

    def abrir_quienes_somos(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "quienes_somos")
        if ruta:
            interfaz_quienessomos.EditorWindow(mode=mode, filepath=ruta)

    def abrir_publicaciones(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "publicaciones")
        if ruta:
            interfaz_publicaciones.EditorWindow(mode=mode, filepath=ruta)

    def abrir_carrusel(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "carrusel")
        if ruta:
            interfaz_carrusel.CarruselWindow(mode=mode, filepath=ruta)

    def abrir_entidades_colaboradoras(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "entidades_colaboradoras")
        if ruta:
            interfaz_entidades_colaboradoras.EntidadesWindow(mode=mode, filepath=ruta)

    def abrir_pagina_web(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_pagina_web.paginaWindow(mode=mode, filepath=ruta)

    # -----------------------------
    # Generar sitio web
    # -----------------------------
    def generar_sitio_web(self):
        try:
            with open("geoso2-web-template/json/web.json", "r", encoding="utf-8") as f:
                datos = json.load(f)

            env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))

            paginas = {
                "carrusel.html": "carrusel.html",
                "entidades_colaboradoras.html": "entidades_colaboradoras.html",
                "noticias.html": "noticias.html",
                "agenda.html": "agenda.html",
                "rafagas.html": "rafagas.html",
                "proyectos.html": "proyectos.html",
                "quienes_somos.html": "quienes_somos.html",
                "publicaciones.html": "publicaciones.html",
            }

            output_dir = "geoso2-web-template/output"
            os.makedirs(output_dir, exist_ok=True)

            for plantilla, salida in paginas.items():
                template = env.get_template(plantilla)
                html = template.render(**datos)

                with open(os.path.join(output_dir, salida), "w", encoding="utf-8") as f:
                    f.write(html)

            webbrowser.open_new_tab(f"file:///{os.path.abspath(output_dir + '/index.html')}")

            messagebox.showinfo("Éxito", "Sitio web generado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el sitio web:\n{e}")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
