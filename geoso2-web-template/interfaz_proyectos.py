import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import datetime
import webbrowser
from PIL import Image
import base64
from jinja2 import Environment, FileSystemLoader


class ProyectosTab(tk.Frame):
    def __init__(self, parent, controller, lista_clave, titulo_tabla):
        super().__init__(parent)
        self.controller = controller
        self.lista_clave = lista_clave  # ej: "en_curso"
        self.titulo_tabla = titulo_tabla

        self.portada_base64_actual = ""


        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

    
        # -------------------------
        # CAMPOS SUPERIORES
        # -------------------------

        ttk.Label(frm, text="Portada:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_portada = ttk.Entry(frm)
        self.entry_portada.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_portada).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Título:").grid(row=1, column=0, sticky="w", pady=6)
        self.text_titulo = tk.Text(frm, wrap="word", height=2)
        self.text_titulo.grid(row=1, column=1, sticky="ew", pady=6)

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

        self.var_link_titulo = tk.BooleanVar(value=True)
        self.var_link_portada = tk.BooleanVar(value=True)

        ttk.Checkbutton(frm, text="Usar enlace en título", variable=self.var_link_titulo).grid(row=5, column=0, sticky="w")
        ttk.Checkbutton(frm, text="Usar enlace en portada", variable=self.var_link_portada).grid(row=5, column=1, sticky="w")

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(2, weight=0)

        # -------------------------
        # BOTONES CRUD
        # -------------------------

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        # -------------------------
        # TABLA
        # -------------------------

        self.tree = ttk.Treeview(
            frm,
            columns=("Imagen", "Título", "Enlace"),
            show="headings",
            height=10
        )
        self.tree.grid(row=7, column=0, columnspan=3, sticky="nsew")
        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Enlace", text="Enlace")

        frm.rowconfigure(7, weight=1)

    def set_data(self):
        self.refresh_table()


    # ============================================================
    #   FUNCIONES DE IMAGEN
    # ============================================================
    def select_portada(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")])
        if not ruta:
            return

        try:
            nombre = os.path.basename(ruta)
            destino = os.path.join("data/img", nombre)

            with Image.open(ruta) as img:
                img = img.convert("RGB")
                img.thumbnail((300, 300), Image.LANCZOS)

                canvas = Image.new("RGB", (300, 300), "white")
                x = (300 - img.width) // 2
                y = (300 - img.height) // 2
                canvas.paste(img, (x, y))
                canvas.save(destino, quality=90)

            self.entry_portada.delete(0, tk.END)
            self.entry_portada.insert(0, destino)

            with open(destino, "rb") as f:
                self.portada_base64_actual = base64.b64encode(f.read()).decode("utf-8")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    # ============================================================
    #   CRUD
    # ============================================================
    def add_item(self):
        titulo = self.text_titulo.get("1.0", tk.END).strip()
        if not titulo:
            messagebox.showwarning("Aviso", "Debes introducir un título.")
            return

        item = {
            "portada": self.entry_portada.get().strip(),
            "portada_base64": self.portada_base64_actual,
            "titulo": titulo,
            "cuerpo": self.text_cuerpo.get("1.0", tk.END).strip(),
            "enlace": {
                "texto": self.entry_enlace_texto.get().strip(),
                "url": self.entry_enlace_url.get().strip(),
                "usar_en_titulo": self.var_link_titulo.get(),
                "usar_en_portada": self.var_link_portada.get()
            }
        }

        self.controller.state[self.lista_clave].append(item)
        self.refresh_table()
        self.clear_fields()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        item = self.controller.state[self.lista_clave][index]

        self.entry_portada.delete(0, tk.END)
        self.entry_portada.insert(0, item["portada"])

        self.text_titulo.delete("1.0", tk.END)
        self.text_titulo.insert("1.0", item["titulo"])

        self.text_cuerpo.delete("1.0", tk.END)
        self.text_cuerpo.insert("1.0", item["cuerpo"])

        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_texto.insert(0, item["enlace"]["texto"])

        self.entry_enlace_url.delete(0, tk.END)
        self.entry_enlace_url.insert(0, item["enlace"]["url"])

        self.var_link_titulo.set(item["enlace"]["usar_en_titulo"])
        self.var_link_portada.set(item["enlace"]["usar_en_portada"])

        self.portada_base64_actual = item["portada_base64"]

        del self.controller.state[self.lista_clave][index]
        self.refresh_table()

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state[self.lista_clave][index]
        self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index > 0:
            arr = self.controller.state[self.lista_clave]
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.controller.state[self.lista_clave]
        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    # ============================================================
    #   UTILIDADES
    # ============================================================
    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in self.controller.state[self.lista_clave]:
            self.tree.insert("", tk.END, values=(p["portada"], p["titulo"], p["enlace"]["url"]))

    def clear_fields(self):
        self.entry_portada.delete(0, tk.END)
        self.text_titulo.delete("1.0", tk.END)
        self.text_cuerpo.delete("1.0", tk.END)
        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_url.delete(0, tk.END)
        self.var_link_titulo.set(True)
        self.var_link_portada.set(True)
        self.portada_base64_actual = ""

    def probar_enlace(self):
        url = self.entry_enlace_url.get().strip()
        if url.startswith(("http://", "https://")):
            webbrowser.open_new_tab(url)
        else:
            messagebox.showerror("Error", "URL inválida")


# ============================================================
#   VENTANA PRINCIPAL DE PROYECTOS
# ============================================================
class ProyectosWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Proyectos")
        self.geometry("980x640")

        self.state = {
            "en_curso": [],
            "trabajos_academicos": [],
            "anteriores": []
        }

        os.makedirs("data/img", exist_ok=True)

        # Si es edición, cargar JSON
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                self.state["en_curso"] = datos.get("en_curso", [])
                self.state["trabajos_academicos"] = datos.get("trabajos_academicos", [])
                self.state["anteriores"] = datos.get("anteriores", [])

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        # Notebook principal
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Crear pestañas
        self.tab_en_curso = ProyectosTab(self.notebook, self, "en_curso", "En curso")
        self.tab_academicos = ProyectosTab(self.notebook, self, "trabajos_academicos", "Trabajos académicos")
        self.tab_anteriores = ProyectosTab(self.notebook, self, "anteriores", "Anteriores")

        self.notebook.add(self.tab_en_curso, text="En curso")
        self.notebook.add(self.tab_academicos, text="Trabajos académicos")
        self.notebook.add(self.tab_anteriores, text="Anteriores")

        # Pestaña Preview
        self.tab_preview = PreviewTab(self.notebook, self)
        self.notebook.add(self.tab_preview, text="Preview y Generar")

        # Rellenar tablas si es edición
        self.tab_en_curso.set_data()
        self.tab_academicos.set_data()
        self.tab_anteriores.set_data()



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

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    def update_preview(self):
        datos = {
            "en_curso": [],
            "trabajos_academicos": [],
            "anteriores": [],
            "fecha": datetime.datetime.now().strftime("%d-%m-%Y")
        }

        # Quitar base64 en preview
        for lista, clave in [
            (datos["en_curso"], "en_curso"),
            (datos["trabajos_academicos"], "trabajos_academicos"),
            (datos["anteriores"], "anteriores")
        ]:
            for ev in self.controller.state[clave]:
                copia = ev.copy()
                copia.pop("portada_base64", None)
                lista.append(copia)

        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    def save_json(self):
        datos = {
            "en_curso": self.controller.state["en_curso"],
            "trabajos_academicos": self.controller.state["trabajos_academicos"],
            "anteriores": self.controller.state["anteriores"],
            "fecha": datetime.datetime.now().strftime("%d-%m-%Y")
        }

        ruta = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Guardado", "JSON guardado correctamente")

    def preview_web(self):
        datos = {
            "en_curso": self.controller.state["en_curso"],
            "trabajos_academicos": self.controller.state["trabajos_academicos"],
            "anteriores": self.controller.state["anteriores"],
            "fecha": datetime.datetime.now().strftime("%d-%m-%Y")
        }

        bloques = ""

        def render_lista(lista, titulo):
            nonlocal bloques
            bloques += f"<h2>{titulo}</h2>"
            for ev in lista:
                cuerpo_html = ev.get("cuerpo", "").replace("\n", "<br>")

                portada_src = ""
                if ev.get("portada_base64"):
                    portada_src = f"data:image/jpeg;base64,{ev['portada_base64']}"

                enlace = ev.get("enlace", {})
                enlace_url = enlace.get("url", "")
                enlace_texto = enlace.get("texto", "")
                usar_titulo = enlace.get("usar_en_titulo", True)
                usar_portada = enlace.get("usar_en_portada", True)

                titulo_html = ev["titulo"]
                if enlace_url and usar_titulo:
                    titulo_html = f'<a href="{enlace_url}" target="_blank">{titulo_html}</a>'

                portada_html = ""
                if portada_src:
                    img_tag = f'<img src="{portada_src}" alt="Portada">'
                    if enlace_url and usar_portada:
                        img_tag = f'<a href="{enlace_url}" target="_blank">{img_tag}</a>'
                    portada_html = img_tag

                enlace_inferior = ""
                if enlace_url and enlace_texto:
                    enlace_inferior = f'<p><a href="{enlace_url}" target="_blank">{enlace_texto}</a></p>'

                bloques += f"""
                <div class="proyecto">
                    <div class="contenedor">
                        <div class="portada">{portada_html}</div>
                        <div class="contenido">
                            <h3>{titulo_html}</h3>
                            <div>{cuerpo_html}</div>
                            {enlace_inferior}
                        </div>
                    </div>
                    <hr>
                </div>
                """

        render_lista(datos["en_curso"], "En curso")
        render_lista(datos["trabajos_academicos"], "Trabajos académicos")
        render_lista(datos["anteriores"], "Anteriores")

        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Proyectos</title>
            <style>
                body {{
                    font-family: Segoe UI, sans-serif;
                    margin: 40px auto;
                    max-width: 900px;
                }}
                .contenedor {{
                    display: flex;
                    gap: 20px;
                }}
                img {{
                    width: 250px;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <h1>Proyectos</h1>
            {bloques}
        </body>
        </html>
        """

        temp_html = "data/preview_temp_proyectos.html"
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open_new_tab(f"file:///{os.path.abspath(temp_html)}")

    def generate_html(self):
        # Datos para la plantilla
        datos = {
            "en curso": self.controller.state.get("en_curso", []),
            "trabajos academicos": self.controller.state.get("trabajos_academicos", []),
            "anteriores": self.controller.state.get("anteriores", []),
            "fecha": datetime.datetime.now().strftime("%d-%m-%Y")
        }

        # Ruta de plantillas
        env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))

        # Plantilla de proyectos (debes adaptarla para usar datos.proyectos)
        template = env.get_template("proyectos.html")

        # Renderizar HTML
        html_output = template.render(datos=datos)

        output_dir = "geoso2-web-template/output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "proyectos.html")

        # Guardar archivo automáticamente
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_output)
            messagebox.showinfo("Éxito", f"Archivo HTML generado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el archivo:\n{e}")
