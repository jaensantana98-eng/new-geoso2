import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
from PIL import Image
import copy
from jinja2 import Environment, FileSystemLoader


class NoticiasWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Noticias")
        self.geometry("980x640")

        # Estado
        self.state = {
            "noticias": []
        }

        # Carpeta correcta
        os.makedirs("geoso2-web-template/imput/img/noticias", exist_ok=True)

        # Cargar JSON si estamos editando
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                if isinstance(datos, dict) and "noticias" in datos:
                    self.state["noticias"] = datos["noticias"]
                elif isinstance(datos, list):
                    self.state["noticias"] = datos
                else:
                    self.state["noticias"] = []

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_datos = DatosTab(self.notebook, self)
        self.tab_preview = PreviewTab(self.notebook, self)

        self.notebook.add(self.tab_datos, text="Datos")
        self.notebook.add(self.tab_preview, text="Preview y Generar")

        if mode == "edit":
            self.tab_datos.refresh_table()
            self.tab_preview.update_preview()


class DatosTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        # Campos
        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_imagen).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Título:").grid(row=1, column=0, sticky="w")
        self.entry_titulo = ttk.Entry(frm)
        self.entry_titulo.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Descripción:").grid(row=2, column=0, sticky="nw")
        self.text_descripcion = tk.Text(frm, height=5)
        self.text_descripcion.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Enlace (opcional):").grid(row=3, column=0, sticky="w")
        self.entry_enlace = ttk.Entry(frm)
        self.entry_enlace.grid(row=3, column=1, sticky="ew", pady=6)

        frm.columnconfigure(1, weight=1)

        # Botones
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)

        # Tabla
        self.tree = ttk.Treeview(frm, columns=("Imagen", "Título"), show="headings", height=12)
        self.tree.grid(row=5, column=0, columnspan=3, sticky="nsew")

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")

        frm.rowconfigure(5, weight=1)
    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecciona una noticia para editar.")
            return
        index = self.tree.index(selected[0])
        noticia = self.controller.state["noticias"][index]

        # Cargar datos en los campos
        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, noticia["imagen"])

        self.entry_titulo.delete(0, tk.END)
        self.entry_titulo.insert(0, noticia["titulo"])

        self.text_descripcion.delete("1.0", tk.END)
        self.text_descripcion.insert("1.0", noticia["descripcion"])

        self.entry_enlace.delete(0, tk.END)
        self.entry_enlace.insert(0, noticia["enlace"])

        # Guardar índice para saber qué elemento editar
        self.editing_index = index


    def select_imagen(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")])
        if not ruta:
            return
        try:
            nombre = os.path.basename(ruta)
            destino = os.path.join("geoso2-web-template/imput/img/noticias", nombre)

            with Image.open(ruta) as img:
                img = img.convert("RGBA")
                img.save(destino)

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, destino)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def add_item(self):
        imagen = self.entry_imagen.get().strip()
        titulo = self.entry_titulo.get().strip()
        descripcion = self.text_descripcion.get("1.0", tk.END).strip()
        enlace = self.entry_enlace.get().strip()

        if not imagen or not titulo or not descripcion:
            messagebox.showwarning("Aviso", "Imagen, título y descripción son obligatorios.")
            return

        self.controller.state["noticias"].append({
            "imagen": imagen,
            "titulo": titulo,
            "descripcion": descripcion,
            "enlace": enlace
        })

        self.refresh_table()

        self.entry_imagen.delete(0, tk.END)
        self.entry_titulo.delete(0, tk.END)
        self.text_descripcion.delete("1.0", tk.END)
        self.entry_enlace.delete(0, tk.END)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state["noticias"][index]
        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for elem in self.controller.state["noticias"]:
            self.tree.insert("", tk.END, values=(elem["imagen"], elem["titulo"]))


class PreviewTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=16, pady=10)

        ttk.Button(toolbar, text="Actualizar preview", command=self.update_preview).pack(side="left")
        ttk.Button(toolbar, text="Guardar JSON", command=self.save_json).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Previsualizar en web", command=self.preview_web).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Generar HTML", command=self.generate_html).pack(side="right", padx=8)

        info = ttk.Label(toolbar, text="Revisa el JSON antes de guardar.")
        info.pack(side="left", padx=16)

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    def update_preview(self):
        datos = copy.deepcopy(self.controller.state)
        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    def save_json(self):
        datos = self.controller.state.copy()
        ruta = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json")],
                                            initialdir="geoso2-web-template/json")
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Guardado", f"Archivo JSON guardado en {ruta}")

    def preview_web(self):
        noticias = self.controller.state.get("noticias", [])

        noticias_ajustadas = []
        for n in noticias:
            nuevo = n.copy()
            imagen = nuevo["imagen"].replace("\\", "/")
            nombre_archivo = os.path.basename(imagen)
            nuevo["imagen"] = f"../imput/img/noticias/{nombre_archivo}"
            noticias_ajustadas.append(nuevo)

        try:
            env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
            template = env.get_template("noticias.html")
            html = template.render(noticias=noticias_ajustadas)

            ruta = "geoso2-web-template/data/preview_noticias.html"
            os.makedirs("geoso2-web-template/data", exist_ok=True)

            with open(ruta, "w", encoding="utf-8") as f:
                f.write(html)

            webbrowser.open_new_tab(f"file:///{os.path.abspath(ruta)}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el preview HTML:\n{e}")

    def generate_html(self):
        noticias = self.controller.state.get("noticias", [])

        env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
        template = env.get_template("noticias.html")

        html_output = template.render(noticias=noticias)

        output_dir = "geoso2-web-template/output"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "noticias.html")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_output)
            messagebox.showinfo("Éxito", f"Archivo HTML generado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el archivo:\n{e}")
