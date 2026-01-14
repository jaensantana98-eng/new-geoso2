import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
from PIL import Image
from jinja2 import Environment, FileSystemLoader


# ============================================================
# VENTANA PRINCIPAL DEL EDITOR DE PROYECTOS
# ============================================================
class EditorProyectosWindow(tk.Toplevel):
    def __init__(self, filepath=None):
        super().__init__()
        self.title("Editor de Proyectos")
        self.geometry("1100x700")

        self.filepath = filepath
        self.editing_index = None


        self.state = {
            "proyectos": {
                "encurso": [],
                "anteriores": [],
                "trabajosacademicos": []
            }
        }

        # Cargar JSON si existe
        if filepath and os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                datos = json.load(f)
                self.state = datos

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_lista = ListaTab(self.notebook, self)
        self.tab_form = FormTab(self.notebook, self)
        self.tab_preview = PreviewTab(self.notebook, self)

        self.notebook.add(self.tab_lista, text="Lista")
        self.notebook.add(self.tab_form, text="Formulario")
        self.notebook.add(self.tab_preview, text="Preview y Generar")

        self.tab_lista.refresh_table()


# ============================================================
# TABLA DE PROYECTOS
# ============================================================
class ListaTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Selector de categoría
        ttk.Label(self, text="Categoría:").pack(anchor="w", padx=10, pady=5)

        self.categoria_var = tk.StringVar(value="encurso")
        self.combo = ttk.Combobox(
            self,
            textvariable=self.categoria_var,
            values=["encurso", "anteriores", "trabajosacademicos"],
            state="readonly"
        )
        self.combo.pack(anchor="w", padx=10)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        # Botones
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=10)

        ttk.Button(toolbar, text="Añadir", command=self.add).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Editar", command=self.edit).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Eliminar", command=self.delete).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Subir", command=self.up).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Bajar", command=self.down).pack(side="left", padx=5)

        # Tabla
        self.tree = ttk.Treeview(
            self,
            columns=("Imagen", "Título", "Link"),
            show="headings",
            height=20
        )
        self.tree.pack(fill="both", expand=True)

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Link", text="Link")

    def refresh_table(self):
        categoria = self.categoria_var.get()
        proyectos = self.controller.state["proyectos"][categoria]

        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in proyectos:
            self.tree.insert(
                "",
                tk.END,
                values=(p.get("imagen", ""), p.get("titulo", ""), p.get("link", ""))
            )

    def add(self):
        self.controller.editing_index = None
        categoria = self.categoria_var.get()
        self.controller.tab_form.load_data({}, categoria)
        self.controller.notebook.select(self.controller.tab_form)



    def edit(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        categoria = self.categoria_var.get()
        self.controller.editing_index = index

        data = self.controller.state["proyectos"][categoria][index]
        self.controller.tab_form.load_data(data, categoria)
        self.controller.notebook.select(self.controller.tab_form)



    def delete(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        categoria = self.categoria_var.get()

        del self.controller.state["proyectos"][categoria][index]
        self.refresh_table()

    def up(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        categoria = self.categoria_var.get()
        arr = self.controller.state["proyectos"][categoria]

        if index == 0:
            return

        arr[index - 1], arr[index] = arr[index], arr[index - 1]
        self.refresh_table()

    def down(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        categoria = self.categoria_var.get()
        arr = self.controller.state["proyectos"][categoria]

        if index == len(arr) - 1:
            return

        arr[index + 1], arr[index] = arr[index], arr[index + 1]
        self.refresh_table()


# ============================================================
# FORMULARIO DE PROYECTO
# ============================================================
class FormTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.categoria_actual = None

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # Imagen
        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w")
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew")
        ttk.Button(frm, text="Seleccionar", command=self.select_image).grid(row=0, column=2, padx=5)

        # Título
        ttk.Label(frm, text="Título:").grid(row=1, column=0, sticky="nw")
        self.text_titulo = tk.Text(frm, height=3)
        self.text_titulo.grid(row=1, column=1, sticky="ew")

        # Link + botón probar
        ttk.Label(frm, text="Link:").grid(row=2, column=0, sticky="w")

        link_frame = ttk.Frame(frm)
        link_frame.grid(row=2, column=1, sticky="ew")

        self.entry_link = ttk.Entry(link_frame)
        self.entry_link.pack(side="left", fill="x", expand=True)

        ttk.Button(link_frame, text="Probar", command=self.probar_link).pack(side="left", padx=5)

        # Descripción
        ttk.Label(frm, text="Descripción:").grid(row=3, column=0, sticky="nw")
        self.text_desc = tk.Text(frm, height=8)
        self.text_desc.grid(row=3, column=1, sticky="ew")

        # Botones
        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=3, pady=20)

        ttk.Button(btns, text="Guardar", command=self.save).pack(side="left", padx=10)
        ttk.Button(btns, text="Cancelar", command=self.cancel).pack(side="left", padx=10)

        frm.columnconfigure(1, weight=1)

    def load_data(self, data, categoria):
        self.categoria_actual = categoria   # ← ESTA LÍNEA ES CRÍTICA

        self.entry_imagen.delete(0, tk.END)
        self.text_titulo.delete("1.0", tk.END)
        self.entry_link.delete(0, tk.END)
        self.text_desc.delete("1.0", tk.END)

        self.entry_imagen.insert(0, data.get("imagen", ""))
        self.text_titulo.insert("1.0", data.get("titulo", ""))
        self.entry_link.insert(0, data.get("link", ""))
        self.text_desc.insert("1.0", data.get("descripcion", ""))

    def select_image(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png;*.gif")]
        )
        if ruta:
            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, ruta)

    def probar_link(self):
        url = self.entry_link.get().strip()

        if not url:
            messagebox.showwarning("Aviso", "No hay ningún enlace para probar.")
            return

        try:
            if url.endswith(".html") and os.path.exists(url):
                ruta = os.path.abspath(url)
                webbrowser.open_new_tab(f"file:///{ruta}")
                return

            if url.startswith("http://") or url.startswith("https://"):
                webbrowser.open_new_tab(url)
                return

            messagebox.showerror("Error", "El enlace no es válido.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")

    def save(self):
        data = {
            "imagen": self.entry_imagen.get().strip(),
            "titulo": self.text_titulo.get("1.0", tk.END).strip(),
            "link": self.entry_link.get().strip(),
            "descripcion": self.text_desc.get("1.0", tk.END).strip()
        }

        # Intentar usar la categoría del formulario;
        # si está vacía, usamos el combo de la pestaña Lista
        categoria = self.categoria_actual or self.controller.tab_lista.categoria_var.get()

        if not categoria:
            messagebox.showerror(
                "Error",
                "No se ha podido determinar la categoría.\n"
                "Abre este formulario siempre desde 'Añadir' o 'Editar'."
            )
            return

        # Asegurarnos de que la clave existe en el diccionario
        if "proyectos" not in self.controller.state:
            self.controller.state["proyectos"] = {}
        if categoria not in self.controller.state["proyectos"]:
            self.controller.state["proyectos"][categoria] = []

        if self.controller.editing_index is None:
            self.controller.state["proyectos"][categoria].append(data)
        else:
            self.controller.state["proyectos"][categoria][self.controller.editing_index] = data
            self.controller.editing_index = None

        self.controller.tab_lista.refresh_table()
        self.controller.notebook.select(self.controller.tab_lista)


    def cancel(self):
        self.controller.notebook.select(self.controller.tab_lista)


# ============================================================
# PREVIEW Y GENERAR
# ============================================================
class PreviewTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=10)

        ttk.Button(toolbar, text="Preview JSON", command=self.preview_json).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Preview HTML", command=self.preview_html).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Generar HTML", command=self.generate_html).pack(side="left", padx=5)

        self.text = tk.Text(self, wrap="word")
        self.text.pack(fill="both", expand=True)

    def preview_json(self):
        self.text.delete("1.0", tk.END)
        self.text.insert(
            tk.END,
            json.dumps(self.controller.state, indent=4, ensure_ascii=False)
        )

    def preview_html(self):
        env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
        template = env.get_template("proyectos.html")

        html = template.render(proyectos=self.controller.state["proyectos"])

        ruta = "data/preview_proyectos.html"
        os.makedirs("data", exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open_new_tab(f"file:///{os.path.abspath(ruta)}")

    def generate_html(self):
        env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
        template = env.get_template("proyectos.html")

        html = template.render(proyectos=self.controller.state["proyectos"])

        ruta = "geoso2-web-template/output/proyectos.html"
        os.makedirs("geoso2-web-template/output", exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(html)

        messagebox.showinfo("OK", f"Archivo generado:\n{ruta}")
