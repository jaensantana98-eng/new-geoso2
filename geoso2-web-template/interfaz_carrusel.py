import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
from PIL import Image, ImageTk
from collections import OrderedDict
import copy
import base64
from jinja2 import Environment, FileSystemLoader


class CarruselWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Carrusel JSON")
        self.geometry("980x640")

        # Estado: lista de elementos del carrusel
        self.state = {
            "carrusel": []
        }

        os.makedirs("data/img", exist_ok=True)

        # Si es edición, cargar datos desde JSON
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                if "carrusel" in datos:
                    self.state["carrusel"] = datos["carrusel"]
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Pestañas
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

        # --- Campos de entrada ---
        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_imagen).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Enlace:").grid(row=1, column=0, sticky="w")
        self.entry_enlace = ttk.Entry(frm)
        self.entry_enlace.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frm, text="Probar enlace", command=self.probar_enlace).grid(row=1, column=2, padx=8)

        frm.columnconfigure(1, weight=1)

        # --- Botones de gestión ---
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        # --- Tabla Treeview ---
        self.tree = ttk.Treeview(frm, columns=("Imagen", "Enlace"), show="headings", height=12)
        self.tree.grid(row=3, column=0, columnspan=3, sticky="nsew")

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Enlace", text="Enlace")

        frm.rowconfigure(3, weight=1)

    def select_imagen(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")])
        if not ruta:
            return
        try:
            nombre = os.path.basename(ruta)
            destino = os.path.join("data/img", nombre)
            with Image.open(ruta) as img:
                img = img.convert("RGB")
                img.save(destino, quality=90) # guardar tal cual, sin redimensionar 
                self.entry_imagen.delete(0, tk.END)
                self.entry_imagen.insert(0, destino)
        except Exception as e:
                messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def probar_enlace(self):
        url = self.entry_enlace.get().strip()

        if not url:
            messagebox.showwarning("Aviso", "No hay ninguna URL para probar.")
            return

        try:
            # Si es un archivo HTML dentro del proyecto
            if url.endswith(".html") and os.path.exists(url):
                ruta_absoluta = os.path.abspath(url)
                webbrowser.open_new_tab(f"file:///{ruta_absoluta}")
            # Si es un enlace web normal
            elif url.startswith(("http://", "https://")):
                webbrowser.open_new_tab(url)
            else:
                messagebox.showerror("Error", "El enlace debe ser una URL válida o un archivo .html del proyecto.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")


    def add_item(self):
        imagen = self.entry_imagen.get().strip()
        enlace = self.entry_enlace.get().strip()

        if not imagen or not enlace:
            messagebox.showwarning("Aviso", "Debes seleccionar una imagen y escribir un enlace.")
            return

        # Convertir imagen a base64
        try:
            with open(imagen, "rb") as img_file:
                b64 = base64.b64encode(img_file.read()).decode("utf-8")
        except:
            b64 = ""

        self.controller.state["carrusel"].append({
            "imagen": imagen,
            "imagen_base64": b64,
            "enlace": enlace
        })

        self.refresh_table()
        self.entry_imagen.delete(0, tk.END)
        self.entry_enlace.delete(0, tk.END)


    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state["carrusel"][index]
        self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index > 0:
            self.controller.state["carrusel"][index - 1], self.controller.state["carrusel"][index] = \
                self.controller.state["carrusel"][index], self.controller.state["carrusel"][index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index < len(self.controller.state["carrusel"]) - 1:
            self.controller.state["carrusel"][index + 1], self.controller.state["carrusel"][index] = \
                self.controller.state["carrusel"][index], self.controller.state["carrusel"][index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for elem in self.controller.state["carrusel"]:
            self.tree.insert("", tk.END, values=(elem["imagen"], elem["enlace"]))


class PreviewTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=16, pady=10)

        ttk.Button(toolbar, text="Actualizar preview", command=self.update_preview).pack(side="left")
        ttk.Button(toolbar, text="Guardar JSON", command=self.save_json).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Previsualizar en web", command=self.preview_web).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Generar archivo HTML", command=self.generate_html).pack(side="right", padx=8)

        info = ttk.Label(toolbar, text="Revisa el JSON antes de guardar.")
        info.pack(side="left", padx=16)

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)


    def update_preview(self):
        datos = copy.deepcopy(self.controller.state)

        # Eliminar base64 del preview
        for item in datos.get("carrusel", []):
            item.pop("imagen_base64", None)

        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)


    def save_json(self):
        datos = self.controller.state.copy()

        index_json = "geoso2-web-template/json/index.json"

        try:
            if os.path.exists(index_json):
                with open(index_json, "r", encoding="utf-8") as f:
                    maestro = json.load(f, object_pairs_hook=OrderedDict)
            else:
                maestro = OrderedDict()

            maestro.setdefault("index_page", OrderedDict())
            maestro["index_page"].setdefault("carousel", [])

            for item in datos["carrusel"]:
                maestro["index_page"]["carousel"].append({
                    "src": item["imagen"],
                    "alt": f"Imagen {len(maestro['index_page']['carousel']) + 1}",
                    "link": item["enlace"]
                })
                
            with open(index_json, "w", encoding="utf-8") as f:
                json.dump(maestro, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Éxito", "El carrusel se ha actualizado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el carrusel:\n{e}")
