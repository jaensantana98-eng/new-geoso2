import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
from PIL import Image, ImageTk
import base64
import copy
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

        os.makedirs("geoso2-web-template/imput/img/carrusel", exist_ok=True)

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
            destino = os.path.join("geoso2-web-template/imput/img", nombre)
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
        ruta = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json")],
                                            initialdir="geoso2-web-template/json",)
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Guardado", f"Archivo JSON guardado en {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")

    def preview_web(self):
        datos = self.controller.state.copy()

        # Construir slides
        slides = ""
        for item in datos["carrusel"]:
            img_src = ""
            if item.get("imagen_base64"):
                img_src = f"data:image/jpeg;base64,{item['imagen_base64']}"

            img_html = f'<img src="{img_src}" class="slide-img">' if img_src else ""

            # Imagen clicable
            if item.get("enlace"):
                img_html = f'<a href="{item["enlace"]}" target="_blank">{img_html}</a>'

            slides += f'<div class="slide">{img_html}</div>'
        
        # HTML del carrusel
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Carrusel</title>
            <style>
                body {{
                    font-family: Segoe UI, sans-serif;
                    margin: 40px auto;
                    max-width: 900px;
                    text-align: center;
                }}

                .carrusel {{
                    position: relative;
                    width: 100%;
                    height: 400px;
                    overflow: hidden;
                }}

                .slides {{
                    display: flex;
                    width: 100%;
                    height: 100%;
                    transition: transform 0.5s ease;
                }}

                .slide {{
                    min-width: 100%;
                    height: 100%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}

                .slide-img {{
                    max-width: 100%;
                    max-height: 100%;
                    object-fit: contain;
                }}

                .btn {{
                    position: absolute;
                    top: 50%;
                    transform: translateY(-50%);
                    background: rgba(0,0,0,0.5);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    cursor: pointer;
                    font-size: 20px;
                }}

                .prev {{ left: 10px; }}
                .next {{ right: 10px; }}
            </style>
        </head>
        <body>

            <h1>Carrusel</h1>

            <div class="carrusel">
                <div class="slides" id="slides">
                    {slides}
                </div>

                <button class="btn prev" onclick="move(-1)">❮</button>
                <button class="btn next" onclick="move(1)">❯</button>
            </div>

            <script>
                let index = 0;
                function move(dir) {{
                    const slides = document.getElementById("slides");
                    const total = slides.children.length;
                    index = (index + dir + total) % total;
                    slides.style.transform = "translateX(" + (-index * 100) + "%)";
                }}

                const intervalo = 2000;
                setInterval(() => move(1), intervalo);
            </script>

        </body>
        </html>
        """

        temp_html = "geoso2-web-template/data/preview_carrusel.html"
        os.makedirs("geoso2-web-template/data", exist_ok=True)
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open_new_tab(f"file:///{os.path.abspath(temp_html)}")

    def generate_html(self):
        # Datos para la plantilla
        datos = {
            "carrusel": self.controller.state.get("carrusel", []),
        }

        # Cargar plantilla desde /templates
        env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))

        # Plantilla del carrusel
        template = env.get_template("carrusel.html")

        # Renderizar HTML
        html_output = template.render(datos=datos)

        # Carpeta de salida
        output_dir = "geoso2-web-template/output"
        os.makedirs(output_dir, exist_ok=True)

        # Nombre fijo del archivo
        output_path = os.path.join(output_dir, "carrusel.html")

        # Guardar archivo automáticamente
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_output)
            messagebox.showinfo("Éxito", f"Archivo HTML generado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el archivo:\n{e}")


