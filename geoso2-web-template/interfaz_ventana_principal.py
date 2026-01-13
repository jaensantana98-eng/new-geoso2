import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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

# -----------------------------
# Ventana principal
# -----------------------------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Geoso2")
        self.geometry("500x250")

        ttk.Label(
            self,
            text="Selecciona una opción:",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=20)

        btns = ttk.Frame(self)
        btns.pack(pady=10)

        ttk.Button(
            btns,
            text="Crear JSON",
            width=18,
            command=lambda: self.open_section_menu("create")
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            btns,
            text="Editar JSON",
            width=18,
            command=lambda: self.open_section_menu("edit")
        ).grid(row=0, column=1, padx=10)

        firma = ttk.Label(self, text="© Creado por Jesús Jaén Santana v.1.0/2025", font=("Segoe UI", 10, "italic"))
        firma.pack(side="bottom", pady=10)

    # -----------------------------
    # Ventana de selección
    # -----------------------------
    def open_section_menu(self, mode):
        win = tk.Toplevel(self)
        win.title("Selecciona la sección")
        win.geometry("400x600")

        text = (
            "Selecciona la sección a crear:"
            if mode == "create"
            else "Selecciona el JSON a editar:"
        )

        ttk.Label(
            win,
            text=text,
            font=("Segoe UI", 12, "bold")
        ).pack(pady=15)

        frm = ttk.Frame(win)
        frm.pack(pady=10)

        # ---------- BOTONES DIRECTOS ----------
        
        ttk.Label(frm, text="Gestionar imagenes de:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(
            frm,
            text="Carrusel",
            width=20,
            command=lambda: self.abrir_carrusel(mode, win)
        ).pack(pady=4)

        ttk.Button(
            frm,
            text="Entidades Colaboradoras",
            width=20,
            command=lambda: self.abrir_entidades_colaboradoras(mode, win)
        ).pack(pady=4)

        ttk.Separator(frm).pack(fill="x", pady=8)

        ttk.Label(frm, text="Secciones de la página principal:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(
            frm,
            text="Noticias",
            width=20,
            command=lambda: self.abrir_noticias(mode, win)
        ).pack(pady=4)

        ttk.Button(
                frm,
                text="Agenda",
                width=20,
                command=lambda: self.abrir_agenda(mode, win)
            ).pack(pady=4)

        ttk.Separator(frm).pack(fill="x", pady=8)

        ttk.Label(frm, text="Otras secciones:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(
            frm,
            text="Ráfagas",
            width=20,
            command=lambda: self.abrir_rafagas(mode, win)
        ).pack(pady=4)

        ttk.Button(
            frm,
            text="Proyectos",
            width=20,
            command=lambda: self.abrir_proyectos(mode, win)
        ).pack(pady=4)

        ttk.Button(
            frm,
            text="Quienes Somos",
            width=20,
            command=lambda: self.abrir_quienes_somos(mode, win)
        ).pack(pady=4)
        ttk.Button(
            frm,
            text="Publicaciones",
            width=20,
            command=lambda: self.abrir_publicaciones(mode, win)
        ).pack(pady=4)

        ttk.Separator(frm).pack(fill="x", pady=8)

        ttk.Label(frm, text="Gestión de Página Web:", font=("Segoe UI", 11)).pack(pady=8)
        ttk.Button(
            frm,
            text="Página Web",
            width=20,
            command=lambda: self.abrir_pagina_web(mode, win)
        ).pack(pady=4)


    # -----------------------------
    # BOTONES -> ARCHIVOS
    # -----------------------------
    
    def abrir_noticias(self, mode, parent_win):
        parent_win.destroy()
        filepath = self.seleccionar_json(mode, "Noticias")
        if mode == "edit" and not filepath:
            return
        interfaz_noticias.EditorWindow(mode=mode, filepath=filepath)

    def abrir_rafagas(self, mode, parent_win):
        parent_win.destroy()
        filepath = self.seleccionar_json(mode, "Ráfagas")
        if mode == "edit" and not filepath:
            return
        interfaz_rafagas.EditorWindow(mode=mode, filepath=filepath)

    def abrir_proyectos(self, mode, parent_win):
        parent_win.destroy()
        filepath = self.seleccionar_json(mode, "Proyectos")
        if mode == "edit" and not filepath:
            return
        interfaz_proyectos.ProyectosWindow(mode=mode, filepath=filepath)

    def abrir_quienes_somos(self, mode, parent_win):
        parent_win.destroy()
        filepath = self.seleccionar_json(mode, "Quienes Somos")
        if mode == "edit" and not filepath:
            return
        interfaz_quienessomos.EditorWindow(mode=mode, filepath=filepath)
    
    def abrir_publicaciones(self, mode, parent_win):
        parent_win.destroy()
        filepath = self.seleccionar_json(mode, "Publicaciones")
        if mode == "edit" and not filepath:
            return
        interfaz_publicaciones.EditorWindow(mode=mode, filepath=filepath)
    
    def abrir_agenda(self, mode, parent_win):
        parent_win.destroy()
        filepath = self.seleccionar_json(mode, "Agenda")
        if mode == "edit" and not filepath:
            return
        interfaz_agenda.EditorWindow(mode=mode, filepath=filepath)

            
    def abrir_carrusel(self, mode, parent_win):
        parent_win.destroy()

        filepath = None
        if mode == "edit":
            filepath = filedialog.askopenfilename(
                title="Selecciona el JSON de Carrusel",
                filetypes=[("JSON files", "*.json")],
                initialdir="data"
            )

            if not filepath or not os.path.exists(filepath):
                messagebox.showwarning(
                    "Aviso",
                    "No se seleccionó ningún archivo válido."
                )
                return
        interfaz_carrusel.CarruselWindow(mode=mode, filepath=filepath)


    def abrir_entidades_colaboradoras(self, mode, parent_win):
        parent_win.destroy()

        filepath = None
        if mode == "edit":
            filepath = filedialog.askopenfilename(
                title="Selecciona el JSON de Entidades Colaboradoras",
                filetypes=[("JSON files", "*.json")],
                initialdir="data"
            )

            if not filepath or not os.path.exists(filepath):
                messagebox.showwarning(
                    "Aviso",
                    "No se seleccionó ningún archivo válido."
                )
                return
        interfaz_entidades_colaboradoras.EntidadesWindow(mode=mode, filepath=filepath)

    def abrir_pagina_web(self, mode, parent_win):
        parent_win.destroy()

        filepath = self.seleccionar_json(mode, "Página Web")
        if mode == "edit" and not filepath:
            return
        interfaz_pagina_web.paginaWindow(mode=mode, filepath=filepath)

    # -----------------------------
    # Selector de JSON (reutilizable)
    # -----------------------------
    def seleccionar_json(self, mode, section_name):
        if mode != "edit":
            return None

        filepath = filedialog.askopenfilename(
            title=f"Selecciona el JSON de {section_name}",
            filetypes=[("JSON files", "*.json")],
            initialdir="geoso2-web-template/json"
        )

        if not filepath or not os.path.exists(filepath):
            messagebox.showwarning(
                "Aviso",
                "No se seleccionó ningún archivo válido."
            )
            return None

        return filepath


# -----------------------------
# Ejecutar app
# -----------------------------
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
