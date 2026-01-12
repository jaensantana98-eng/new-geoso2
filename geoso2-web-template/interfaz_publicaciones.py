import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from collections import OrderedDict
import webbrowser


class PublicacionesWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Publicaciones")
        self.geometry("1100x700")

        # Estado inicial
        self.state = {
            "publicaciones": OrderedDict()
        }

        # Cargar JSON si estamos en modo edición
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f, object_pairs_hook=OrderedDict)
                if "publicaciones" in datos:
                    self.state["publicaciones"] = datos["publicaciones"]
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Pestañas
        self.tab_selector = SelectorTab(self.notebook, self)
        self.tab_lista = ListaTab(self.notebook, self)
        self.tab_form = FormularioTab(self.notebook, self)
        self.tab_preview = PreviewTab(self.notebook, self)

        self.notebook.add(self.tab_selector, text="Años")
        self.notebook.add(self.tab_lista, text="Publicaciones")
        self.notebook.add(self.tab_form, text="Formulario")
        self.notebook.add(self.tab_preview, text="Preview y Guardar")

        # Refrescar
        self.tab_selector.refresh_years()
        self.tab_lista.refresh_table()
        self.tab_preview.update_preview()


# ---------------------------------------------------------
# TAB 1 — Selector de año
# ---------------------------------------------------------

class SelectorTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frm, text="Año:").grid(row=0, column=0, sticky="w")
        self.combo_anio = ttk.Combobox(frm, state="readonly")
        self.combo_anio.grid(row=0, column=1, padx=10)

        ttk.Button(frm, text="Seleccionar", command=self.select_year).grid(row=0, column=2, padx=10)
        ttk.Button(frm, text="Añadir Año", command=self.add_year).grid(row=1, column=0, pady=10)
        ttk.Button(frm, text="Eliminar Año", command=self.delete_year).grid(row=1, column=1, pady=10)

    def refresh_years(self):
        years = list(self.controller.state["publicaciones"].keys())
        self.combo_anio["values"] = years
        if years:
            self.combo_anio.current(0)

    def select_year(self):
        year = self.combo_anio.get()
        if not year:
            return
        self.controller.current_year = year
        self.controller.tab_lista.refresh_table()

    def add_year(self):
        new_year = tk.simpledialog.askstring("Nuevo Año", "Introduce el año:")
        if not new_year:
            return
        if new_year in self.controller.state["publicaciones"]:
            messagebox.showwarning("Aviso", "Ese año ya existe.")
            return
        self.controller.state["publicaciones"][new_year] = []
        self.refresh_years()

    def delete_year(self):
        year = self.combo_anio.get()
        if not year:
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar el año {year}?"):
            del self.controller.state["publicaciones"][year]
            self.refresh_years()
            self.controller.tab_lista.refresh_table()


# ---------------------------------------------------------
# TAB 2 — Lista de publicaciones
# ---------------------------------------------------------

class ListaTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # Tabla
        self.tree = ttk.Treeview(frm, columns=("Autores", "Título", "Revista", "Link"), show="headings")
        self.tree.heading("Autores", text="Autores")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Revista", text="Revista")
        self.tree.heading("Link", text="Link")
        self.tree.pack(fill="both", expand=True)

        # Botones
        btns = ttk.Frame(frm)
        btns.pack(pady=10)

        ttk.Button(btns, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btns, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btns, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        year = getattr(self.controller, "current_year", None)
        if not year:
            return

        for pub in self.controller.state["publicaciones"].get(year, []):
            self.tree.insert("", tk.END, values=(
                pub["autores"],
                pub["titulo"],
                pub["revista"],
                pub["link"]
            ))

    def add_item(self):
        self.controller.tab_form.load_form(None)
        self.controller.notebook.select(self.controller.tab_form)

    def edit_item(self):
        year = getattr(self.controller, "current_year", None)
        if not year:
            return

        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        pub = self.controller.state["publicaciones"][year][index]

        self.controller.tab_form.load_form(pub, index)
        self.controller.notebook.select(self.controller.tab_form)

    def delete_item(self):
        year = getattr(self.controller, "current_year", None)
        if not year:
            return

        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        del self.controller.state["publicaciones"][year][index]
        self.refresh_table()


# ---------------------------------------------------------
# TAB 3 — Formulario
# ---------------------------------------------------------

class FormularioTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.edit_index = None

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        labels = ["Autores", "Título", "Tipo", "Revista", "Volumen", "Número", "Link"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(frm, text=label + ":").grid(row=i, column=0, sticky="w", pady=5)
            entry = ttk.Entry(frm, width=80)
            entry.grid(row=i, column=1, pady=5)
            self.entries[label.lower()] = entry

        ttk.Button(frm, text="Guardar", command=self.save_item).grid(row=len(labels), column=0, pady=20)
        ttk.Button(frm, text="Cancelar", command=self.cancel).grid(row=len(labels), column=1, pady=20)

    def load_form(self, pub, index=None):
        self.edit_index = index

        for key in self.entries:
            self.entries[key].delete(0, tk.END)

        if pub:
            self.entries["autores"].insert(0, pub["autores"])
            self.entries["título"].insert(0, pub["titulo"])
            self.entries["tipo"].insert(0, pub["tipo"])
            self.entries["revista"].insert(0, pub["revista"])
            self.entries["volumen"].insert(0, pub["volumen"])
            self.entries["número"].insert(0, pub["num"])
            self.entries["link"].insert(0, pub["link"])

    def save_item(self):
        year = getattr(self.controller, "current_year", None)
        if not year:
            messagebox.showwarning("Aviso", "Selecciona un año primero.")
            return

        pub = {
            "autores": self.entries["autores"].get(),
            "titulo": self.entries["título"].get(),
            "tipo": self.entries["tipo"].get(),
            "revista": self.entries["revista"].get(),
            "volumen": self.entries["volumen"].get(),
            "num": self.entries["número"].get(),
            "link": self.entries["link"].get()
        }

        if self.edit_index is None:
            self.controller.state["publicaciones"][year].append(pub)
        else:
            self.controller.state["publicaciones"][year][self.edit_index] = pub

        self.controller.tab_lista.refresh_table()
        self.controller.tab_preview.update_preview()
        self.controller.notebook.select(self.controller.tab_lista)

    def cancel(self):
        self.controller.notebook.select(self.controller.tab_lista)


# ---------------------------------------------------------
# TAB 4 — Preview y Guardado
# ---------------------------------------------------------

class PreviewTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=20, pady=10)

        ttk.Button(toolbar, text="Actualizar preview", command=self.update_preview).pack(side="left")
        ttk.Button(toolbar, text="Guardar JSON", command=self.save_json).pack(side="left", padx=10)

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=20, pady=10)

    def update_preview(self):
        preview = json.dumps(self.controller.state, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    def save_json(self):

        index_json = "geoso2-web-template/json/publicaciones.json"

        try:
            # 1. Cargar JSON maestro
            if os.path.exists(index_json):
                with open(index_json, "r", encoding="utf-8") as f:
                    maestro = json.load(f, object_pairs_hook=OrderedDict)
            else:
                maestro = OrderedDict()

            # 2. Asegurar estructura
            maestro.setdefault("index_page", OrderedDict())
            maestro.setdefault("publicaciones", OrderedDict())

            publicaciones_maestro = maestro["publicaciones"]
            publicaciones_editor = self.controller.state["publicaciones"]

            # 3. Fusionar año por año sin borrar nada
            for year, lista_editor in publicaciones_editor.items():

                # Asegurar que el año existe en el maestro
                publicaciones_maestro.setdefault(year, [])

                # Añadir cada publicación nueva sin borrar las anteriores
                for pub in lista_editor:
                    publicaciones_maestro[year].append(pub)

            # 4. Guardar archivo
            with open(index_json, "w", encoding="utf-8") as f:
                json.dump(maestro, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", "Publicaciones actualizadas correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar las publicaciones:\n{e}")
