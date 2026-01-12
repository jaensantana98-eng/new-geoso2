import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
from PIL import Image, ImageTk
import base64
import copy
from jinja2 import Environment, FileSystemLoader

class EntidadesWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Entidades Colaboradoras")
        self.geometry("980x640")

        # Estado: lista de elementos de entidades colaboradoras
        self.state = {
            "entidades": []
        }

        os.makedirs("data/img", exist_ok=True)

        # Si es edición, cargar datos desde JSON
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                if "entidades" in datos:
                    self.state["entidades"] = datos["entidades"]
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
                img = img.convert("RGBA")
                img = img.resize((120, 120), Image.LANCZOS)
                img.save(destino, format="PNG")

                
                self.entry_imagen.delete(0, tk.END)
                self.entry_imagen.insert(0, destino)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def probar_enlace(self):
        enlace = self.entry_enlace.get().strip()
        if not enlace:
            messagebox.showwarning("Aviso", "No hay ningún enlace para probar.")
            return
        if not enlace.startswith(("http://", "https://")):
            messagebox.showerror("Error", "La URL debe empezar por http:// o https://")
            return
        try:
            webbrowser.open_new_tab(enlace)
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

        self.controller.state["entidades"].append({
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
        del self.controller.state["entidades"][index]
        self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index > 0:
            self.controller.state["entidades"][index - 1], self.controller.state["entidades"][index] = \
                self.controller.state["entidades"][index], self.controller.state["entidades"][index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index < len(self.controller.state["entidades"]) - 1:
            self.controller.state["entidades"][index + 1], self.controller.state["entidades"][index] = \
                self.controller.state["entidades"][index], self.controller.state["entidades"][index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for elem in self.controller.state["entidades"]:
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
        ttk.Button(toolbar, text="Generar HTML", command=self.generate_html).pack(side="right", padx=8)

        info = ttk.Label(toolbar, text="Revisa el JSON antes de guardar.")
        info.pack(side="left", padx=16)

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    def update_preview(self):
        datos = copy.deepcopy(self.controller.state)

        # Eliminar imagen_base64 del preview
        for entidad in datos.get("entidades", []):
            entidad.pop("imagen_base64", None)

        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)


    def save_json(self):
        datos = self.controller.state.copy()
        ruta = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json")],
                                            initialdir="data")
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Guardado", f"Archivo JSON guardado en {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")

    def preview_web(self):
        datos = self.controller.state.copy()

        # Construir HTML de entidades
        bloques = ""
        for e in datos["entidades"]:
            img_src = ""
            if e.get("imagen_base64"):
                img_src = f"data:image/jpeg;base64,{e['imagen_base64']}"

            img_html = f'<img src="{img_src}" alt="Entidad">' if img_src else ""

            # Imagen clicable
            if e.get("enlace"):
                img_html = f'<a href="{e["enlace"]}" target="_blank">{img_html}</a>'

            bloques += f"""
            <div class="entidad">
                {img_html}
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Entidades Colaboradoras</title>
            <style>
                body {{
                    font-family: Segoe UI, sans-serif;
                    margin: 40px auto;
                    max-width: 1000px;
                    text-align: center;
                }}
                .fila {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 20px;
                }}
                .entidad img {{
                    width: 120px;
                    height: 120px;
                    object-fit: contain;
                    border-radius: 6px;
                }}
            </style>
        </head>
        <body>
            <h1>Entidades Colaboradoras</h1>

            <div class="fila">
                {bloques}
            </div>
        </body>
        </html>
        """

        temp_html = "data/preview_entidades.html"
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open_new_tab(f"file:///{os.path.abspath(temp_html)}")

    def generate_html(self):
        datos = self.controller.state.copy()

        # Ruta de plantillas
        env = Environment(loader=FileSystemLoader("templates"))

        # Seleccionar plantilla según el editor
        # Puedes cambiar esto dinámicamente si quieres
        template = env.get_template("noticias.html")

        # Renderizar HTML
        html_output = template.render(datos=datos)

        # Guardar archivo final
        ruta = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")],
            initialdir="data/output"
        )

        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(html_output)
                messagebox.showinfo("Éxito", f"Archivo HTML generado en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar el archivo:\n{e}")
