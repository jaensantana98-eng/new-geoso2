import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import datetime
import webbrowser
from PIL import Image
import base64
import copy
from jinja2 import Environment, FileSystemLoader

class EditorWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor Investigadores/Colaboradores")
        self.geometry("980x640")

        # Estado inicial
        self.state = {
            "investigadores": [],
            "colaboradores": []
        }

        os.makedirs("data/img", exist_ok=True)

        # Si es edición, cargar datos desde JSON
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                for k in self.state.keys():
                    if k in datos and isinstance(datos[k], list):
                        self.state[k] = datos[k]
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Pestañas
        self.tab_investigadores = PersonasTab(self.notebook, self, "investigadores")
        self.tab_colaboradores = PersonasTab(self.notebook, self, "colaboradores")
        self.tab_preview = PreviewTab(self.notebook, self)

        self.notebook.add(self.tab_investigadores, text="Investigadores")
        self.notebook.add(self.tab_colaboradores, text="Colaboradores")
        self.notebook.add(self.tab_preview, text="Preview y Guardar")

        # Refrescar si venimos de edición
        self.tab_investigadores.refresh_table()
        self.tab_colaboradores.refresh_table()
        self.tab_preview.update_preview()


class PersonasTab(ttk.Frame):
    def __init__(self, parent, controller, key):
        super().__init__(parent)
        self.controller = controller
        self.key = key  # "investigadores" o "colaboradores"

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        # Campos de entrada
        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_imagen).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Nombre:").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_nombre = ttk.Entry(frm)
        self.entry_nombre.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Cuerpo:").grid(row=2, column=0, sticky="nw", pady=6)
        cuerpo_frame = ttk.Frame(frm)
        cuerpo_frame.grid(row=2, column=1, sticky="nsew", pady=6)
        self.text_cuerpo = tk.Text(cuerpo_frame, wrap="word", height=6)
        self.text_cuerpo.pack(side="left", fill="both", expand=True)
        scroll_cuerpo = ttk.Scrollbar(cuerpo_frame, orient="vertical", command=self.text_cuerpo.yview)
        scroll_cuerpo.pack(side="right", fill="y")
        self.text_cuerpo.config(yscrollcommand=scroll_cuerpo.set)

        ttk.Label(frm, text="Texto del enlace:").grid(row=3, column=0, sticky="w", pady=6)
        self.entry_enlace_texto = ttk.Entry(frm)
        self.entry_enlace_texto.grid(row=3, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="URL del enlace:").grid(row=4, column=0, sticky="w", pady=6)
        self.entry_enlace_url = ttk.Entry(frm)
        self.entry_enlace_url.grid(row=4, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Probar enlace", command=self.probar_enlace).grid(row=4, column=2, padx=8)

        self.var_link_nombre = tk.BooleanVar(value=True)
        self.var_link_imagen = tk.BooleanVar(value=True)

        ttk.Checkbutton(frm, text="Usar enlace en nombre", variable=self.var_link_nombre).grid(row=5, column=0, sticky="w")
        ttk.Checkbutton(frm, text="Usar enlace en imagen", variable=self.var_link_imagen).grid(row=5, column=1, sticky="w")

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(2, weight=1)

        # Botones de gestión
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_block).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        # Tabla
        self.tree = ttk.Treeview(frm, columns=("Imagen", "Nombre", "Enlace"), show="headings", height=10)
        self.tree.grid(row=7, column=0, columnspan=3, sticky="nsew")
        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Enlace", text="Enlace")
        frm.rowconfigure(7, weight=1)

    def edit_block(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        item = self.controller.state[self.key][index]

        # Rellenar campos
        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, item.get("imagen", ""))
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, item.get("nombre", ""))
        self.text_cuerpo.delete("1.0", tk.END)
        self.text_cuerpo.insert("1.0", item.get("cuerpo", ""))
        enlace = item.get("enlace", {})
        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_texto.insert(0, enlace.get("texto", ""))
        self.entry_enlace_url.delete(0, tk.END)
        self.entry_enlace_url.insert(0, enlace.get("url", ""))
        self.var_link_nombre.set(enlace.get("usar_en_nombre", True))
        self.var_link_imagen.set(enlace.get("usar_en_imagen", True))

        # Eliminar el item para reemplazarlo al guardar
        del self.controller.state[self.key][index]
        self.refresh_table()

    def select_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )

        if not ruta:
            return

        try:
            nombre = os.path.basename(ruta)
            destino = os.path.join("data/img", nombre)

            with Image.open(ruta) as img:
                # Convertir a RGB para evitar problemas de formato
                img = img.convert("RGB")

                # Mantener proporción dentro de 300x300
                img.thumbnail((300, 300), Image.LANCZOS)

                # Crear lienzo 300x300 con fondo blanco
                canvas = Image.new("RGB", (300, 300), "white")
                x = (300 - img.width) // 2
                y = (300 - img.height) // 2
                canvas.paste(img, (x, y))

                # La imagen final es el canvas
                canvas.save(destino, quality=90)

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, destino)
            self.controller.state["imagen"] = destino

            with open(destino, "rb") as img_file:
                b64 = base64.b64encode(img_file.read()).decode("utf-8")
                self.controller.state["imagen_base64"] = b64

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo procesar la imagen de portada:\n{e}"
            )

    def probar_enlace(self):
        url = self.entry_enlace_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "No hay ninguna URL para probar.")
            return
        if not url.startswith(("http://", "https://")):
            messagebox.showerror("Error", "La URL debe empezar por http:// o https://")
            return
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")

    def add_item(self):
        imagen = self.entry_imagen.get().strip()
        nombre = self.entry_nombre.get().strip()
        cuerpo = self.text_cuerpo.get("1.0", tk.END).strip()
        enlace_texto = self.entry_enlace_texto.get().strip()
        enlace_url = self.entry_enlace_url.get().strip()
        usar_nombre = self.var_link_nombre.get()
        usar_imagen = self.var_link_imagen.get()

        if not imagen or not nombre:
            messagebox.showwarning("Aviso", "Debes completar al menos imagen y nombre.")
            return

        item = {
            "imagen": imagen,
            "imagen_base64": self.controller.state.get("imagen_base64", ""),
            "nombre": nombre,
            "cuerpo": cuerpo,
            "enlace": {
                "texto": enlace_texto,
                "url": enlace_url,
                "usar_en_nombre": usar_nombre,
                "usar_en_imagen": usar_imagen
            }
        }
        self.controller.state[self.key].append(item)
        self.refresh_table()

        # Limpiar entradas
        self.entry_imagen.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.text_cuerpo.delete("1.0", tk.END)
        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_url.delete(0, tk.END)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state[self.key][index]
        self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index > 0:
            arr = self.controller.state[self.key]
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.controller.state[self.key]
        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def refresh_table(self):
        # Vaciar tabla
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        # Rellenar
        for elem in self.controller.state[self.key]:
            self.tree.insert("", tk.END, values=(
                elem.get("imagen", ""),
                elem.get("nombre", ""),
                elem.get("enlace", {}).get("url", "")
            ))


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
        # Copia profunda para no modificar el estado real
        datos = copy.deepcopy(self.controller.state)
        datos["fecha"] = datetime.datetime.now().strftime("%d-%m-%Y")

        # Eliminar claves internas que no deben aparecer en el preview
        for persona in datos.get("investigadores", []):
            persona.pop("imagen_base64", None)

        for persona in datos.get("colaboradores", []):
            persona.pop("imagen_base64", None)

        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)



    def save_json(self):
        datos = {
            "investigadores": self.controller.state.get("investigadores", []),
            "colaboradores": self.controller.state.get("colaboradores", []),
        }

        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir="geoso2-web-template/json"
        )
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Guardado", "JSON guardado correctamente")

    def preview_web(self):
        datos = self.controller.state.copy()
        datos["fecha"] = datetime.datetime.now().strftime("%d-%m-%Y")

        # Construir HTML de personas
        def render_personas(lista):
            bloques = ""
            for p in lista:
                img_src = ""
                if p.get("imagen_base64"):
                    img_src = f"data:image/jpeg;base64,{p['imagen_base64']}"

                # Imagen con o sin enlace
                img_html = f'<img src="{img_src}" alt="{p["nombre"]}">' if img_src else ""

                if p.get("enlace", {}).get("url") and p["enlace"].get("usar_en_imagen"):
                    img_html = f'<a href="{p["enlace"]["url"]}" target="_blank">{img_html}</a>'

                # Nombre con o sin enlace
                nombre_html = p["nombre"]
                if p.get("enlace", {}).get("url") and p["enlace"].get("usar_en_nombre"):
                    nombre_html = f'<a href="{p["enlace"]["url"]}" target="_blank">{nombre_html}</a>'

                cuerpo_html = p["cuerpo"].replace("\n", "<br>")

                # Texto del enlace
                enlace_html = ""
                if p.get("enlace", {}).get("texto") and p["enlace"].get("url"):
                    enlace_html = f'<p><a href="{p["enlace"]["url"]}" target="_blank">{p["enlace"]["texto"]}</a></p>'

                bloques += f"""
                <div class="persona">
                    <div class="foto">{img_html}</div>
                    <div class="info">
                        <h3>{nombre_html}</h3>
                        <p>{cuerpo_html}</p>
                        {enlace_html}
                    </div>
                </div>
                """
            return bloques


        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Investigadores y Colaboradores</title>
            <style>
                body {{
                    font-family: Segoe UI, sans-serif;
                    margin: 40px auto;
                    max-width: 900px;
                    line-height: 1.6;
                }}
                .persona {{
                    display: flex;
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .persona img {{
                    width: 150px;
                    height: auto;
                    border-radius: 6px;
                }}
                .info {{
                    flex-grow: 1;
                }}
            </style>
        </head>
        <body>
            <h1>Investigadores</h1>
            {render_personas(datos["investigadores"])}

            <h1>Colaboradores</h1>
            {render_personas(datos["colaboradores"])}

            <p><small>Fecha: {datos['fecha']}</small></p>
        </body>
        </html>
        """

        temp_html = "data/preview_personas.html"
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open_new_tab(f"file:///{os.path.abspath(temp_html)}")

    def generate_html(self):
        datos = self.controller.state.copy()

        # Ruta de plantillas
        env = Environment(loader=FileSystemLoader("templates"))

        # Seleccionar plantilla según el editor
        # Puedes cambiar esto dinámicamente si quieres
        template = env.get_template("quienes-somos.html")

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
