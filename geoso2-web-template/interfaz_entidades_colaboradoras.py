import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
from PIL import Image
import copy
from jinja2 import Environment, FileSystemLoader

class EntidadesWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Entidades Colaboradoras")
        self.geometry("980x640")

        # Estado
        self.state = {
            "entidades": []
        }

        # Carpeta correcta
        os.makedirs("geoso2-web-template/imput/img/colaboradores", exist_ok=True)

        # Cargar JSON si estamos editando
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                # Cargar entidades desde la ruta correcta
                self.state["entidades"] = datos.get("web", {}) \
                                            .get("Entidades", {}) \
                                            .get("entidades", [])

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

        ttk.Label(frm, text="Enlace:").grid(row=1, column=0, sticky="w")
        self.entry_enlace = ttk.Entry(frm)
        self.entry_enlace.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frm, text="Probar enlace", command=self.probar_enlace).grid(row=1, column=2, padx=8)
        ttk.Button(frm, text="Buscar archivo", command=self.select_file).grid(row=2, column=2, padx=8)

        frm.columnconfigure(1, weight=1)

        # Botones
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)

        # Tabla
        self.tree = ttk.Treeview(frm, columns=("Imagen", "Enlace"), show="headings", height=12)
        self.tree.grid(row=3, column=0, columnspan=3, sticky="nsew")

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Enlace", text="Enlace")

        frm.rowconfigure(3, weight=1)
    
    def select_file(self):

        # Carpeta Descargas del usuario
        descargas = os.path.join(os.path.expanduser("~"), "Downloads")

        if not os.path.isdir(descargas):
            descargas = os.path.expanduser("~")

        ruta = filedialog.askopenfilename(
            initialdir=descargas,
            initialfile="",   # ← ESTO OBLIGA A USAR initialdir
            title="Seleccionar archivo",
            filetypes=[
                ("Documentos", "*.pdf;*.html;*.htm"),
                ("PDF", "*.pdf"),
                ("HTML", "*.html;*.htm"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not ruta:
            return

        try:
            destino_dir = "geoso2-web-template/imput/docs/colaboradores"
            os.makedirs(destino_dir, exist_ok=True)

            nombre = os.path.basename(ruta)
            destino = os.path.join(destino_dir, nombre)

            with open(ruta, "rb") as f_src:
                with open(destino, "wb") as f_dst:
                    f_dst.write(f_src.read())

            ruta_relativa = f"../imput/docs/colaboradores/{nombre}"
            self.entry_enlace.delete(0, tk.END)
            self.entry_enlace.insert(0, ruta_relativa)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar el archivo:\n{e}")


    def select_imagen(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")])
        if not ruta:
            return
        try:
            nombre = os.path.basename(ruta)
            destino = os.path.join("geoso2-web-template/imput/img/colaboradores", nombre)

            with Image.open(ruta) as img:
                img = img.convert("RGBA")
                img.save(destino)

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
        webbrowser.open_new_tab(enlace)

    def add_item(self):
        imagen = self.entry_imagen.get().strip()
        enlace = self.entry_enlace.get().strip()

        if not imagen or not enlace:
            messagebox.showwarning("Aviso", "Debes seleccionar una imagen y escribir un enlace.")
            return

        self.controller.state["entidades"].append({
            "imagen": imagen,
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
        ttk.Button(toolbar, text="Abrir Geoso2.es", command=self.open_output_html).pack(side="right")

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    def update_preview(self):
        datos = copy.deepcopy(self.controller.state)
        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    def save_json(self):
        ruta = "geoso2-web-template/json/web.json"

        try:
            # Cargar JSON completo
            with open(ruta, "r", encoding="utf-8") as f:
                datos_completos = json.load(f)

            # Asegurar estructura
            if "web" not in datos_completos:
                datos_completos["web"] = {}

            if "index_page" not in datos_completos["web"]:
                datos_completos["web"]["index_page"] = {}

            # Guardar entidades en la ruta correcta
            datos_completos["web"]["index_page"]["entidades"] = self.controller.state["entidades"]

            # Guardar JSON completo
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", f"Archivo JSON actualizado:\n{ruta}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def preview_web(self):
        entidades = self.controller.state.get("entidades", [])

        entidades_ajustadas = []
        for e in entidades:
            nuevo = e.copy()
            imagen = nuevo["imagen"].replace("\\", "/")
            nombre_archivo = os.path.basename(imagen)
            nuevo["imagen"] = f"../imput/img/colaboradores/{nombre_archivo}"
            entidades_ajustadas.append(nuevo)

        try:
            env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
            template = env.get_template("entidades.html")
            html = template.render(entidades=entidades_ajustadas)

            ruta = "geoso2-web-template/data/preview_entidades.html"
            os.makedirs("geoso2-web-template/data", exist_ok=True)

            with open(ruta, "w", encoding="utf-8") as f:
                f.write(html)

            webbrowser.open_new_tab(f"file:///{os.path.abspath(ruta)}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el preview HTML:\n{e}")

    def generate_html(self):
        entidades = self.controller.state.get("entidades", [])

        env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
        template = env.get_template("entidades.html")

        html_output = template.render(entidades=entidades)

        output_dir = "geoso2-web-template/output"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "entidades.html")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_output)
            messagebox.showinfo("Éxito", f"Archivo HTML generado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el archivo:\n{e}")

    def open_output_html(self):
        output_path = "geoso2-web-template/output/index.html"
        ruta_absoluta = os.path.abspath(output_path)

        if not os.path.exists(ruta_absoluta):
            messagebox.showerror(
                "Error",
                f"No se encontró el archivo HTML final:\n{ruta_absoluta}\n\nGenera el HTML primero."
            )
            return

        try:
            webbrowser.open_new_tab(f"file:///{ruta_absoluta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el HTML:\n{e}")
