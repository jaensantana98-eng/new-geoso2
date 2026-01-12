import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import datetime
import webbrowser
from PIL import Image
import base64
from jinja2 import Environment, FileSystemLoader


# ============================================================
#   VENTANA PRINCIPAL DEL EDITOR DE AGENDA
# ============================================================
class AgendaWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Agenda")
        self.geometry("980x640")

        # JSON maestro
        self.json_path = "geoso2-web-template/json/index.json"

        # Estado interno (solo agenda)
        self.state = {
            "agenda": []
        }

        # Asegurar carpeta de imágenes
        os.makedirs("data/img", exist_ok=True)

        # Cargar JSON maestro
        self.load_master_json()

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Pestañas
        self.tab_datos = DatosTab(self.notebook, self)
        self.tab_preview = PreviewTab(self.notebook, self)

        self.notebook.add(self.tab_datos, text="Datos")
        self.notebook.add(self.tab_preview, text="Preview y Generar")

        # Inicializar preview
        self.tab_preview.update_preview()

    # --------------------------------------------------------
    # Cargar JSON maestro index.json
    # --------------------------------------------------------
    def load_master_json(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                datos = json.load(f)

            # Asegurar estructura
            datos.setdefault("index_page", {})
            datos["index_page"].setdefault("agenda", [])

            self.master_json = datos
            self.state["agenda"] = datos["index_page"]["agenda"].copy()

        else:
            # Crear estructura mínima
            self.master_json = {
                "index_page": {
                    "carousel": [],
                    "noticias": [],
                    "agenda": [],
                    "colaboradores": [],
                    "footer": {}
                }
            }
            self.state["agenda"] = []


# ============================================================
#   PESTAÑA DE DATOS
# ============================================================
class DatosTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.portada_base64_actual = ""

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # ----------------------------------------------------
        # CAMPOS
        # ----------------------------------------------------
        ttk.Label(frm, text="Imagen (portada):").grid(row=0, column=0, sticky="w")
        self.entry_portada = ttk.Entry(frm)
        self.entry_portada.grid(row=0, column=1, sticky="ew")
        ttk.Button(frm, text="Buscar", command=self.select_portada).grid(row=0, column=2, padx=6)

        ttk.Label(frm, text="Título:").grid(row=1, column=0, sticky="w")
        self.text_titulo = tk.Text(frm, wrap="word", height=2)
        self.text_titulo.grid(row=1, column=1, sticky="ew")

        ttk.Label(frm, text="Descripción:").grid(row=2, column=0, sticky="nw")
        self.text_descripcion = tk.Text(frm, wrap="word", height=5)
        self.text_descripcion.grid(row=2, column=1, sticky="ew")

        ttk.Label(frm, text="Fecha:").grid(row=3, column=0, sticky="w")
        self.entry_fecha = ttk.Entry(frm)
        self.entry_fecha.grid(row=3, column=1, sticky="ew")

        ttk.Label(frm, text="Lugar:").grid(row=4, column=0, sticky="w")
        self.entry_lugar = ttk.Entry(frm)
        self.entry_lugar.grid(row=4, column=1, sticky="ew")

        ttk.Label(frm, text="URL del enlace:").grid(row=5, column=0, sticky="w")
        self.entry_link = ttk.Entry(frm)
        self.entry_link.grid(row=5, column=1, sticky="ew")

        ttk.Label(frm, text="Texto del enlace:").grid(row=6, column=0, sticky="w")
        self.entry_texto_link = ttk.Entry(frm)
        self.entry_texto_link.grid(row=6, column=1, sticky="ew")

        ttk.Button(frm, text="Probar enlace", command=self.probar_enlace).grid(row=5, column=2, padx=6)

        frm.columnconfigure(1, weight=1)

        # ----------------------------------------------------
        # BOTONES CRUD
        # ----------------------------------------------------
        btns = ttk.Frame(frm)
        btns.grid(row=7, column=0, columnspan=3, pady=10)

        ttk.Button(btns, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btns, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btns, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btns, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btns, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        # ----------------------------------------------------
        # TABLA
        # ----------------------------------------------------
        self.tree = ttk.Treeview(
            frm,
            columns=("Imagen", "Título", "Fecha", "Lugar", "Link"),
            show="headings",
            height=10
        )
        self.tree.grid(row=8, column=0, columnspan=3, sticky="nsew")

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Lugar", text="Lugar")
        self.tree.heading("Link", text="Link")

        frm.rowconfigure(8, weight=1)

        self.refresh_table()

    # --------------------------------------------------------
    # Seleccionar imagen
    # --------------------------------------------------------
    def select_portada(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )
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

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    # --------------------------------------------------------
    # Probar enlace
    # --------------------------------------------------------
    def probar_enlace(self):
        url = self.entry_link.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "No hay URL para probar.")
            return
        if not url.startswith(("http://", "https://")):
            messagebox.showerror("Error", "La URL debe empezar por http:// o https://")
            return
        webbrowser.open_new_tab(url)

    # --------------------------------------------------------
    # Añadir evento
    # --------------------------------------------------------
    def add_item(self):
        titulo = self.text_titulo.get("1.0", tk.END).strip()
        if not titulo:
            messagebox.showwarning("Aviso", "El evento debe tener un título.")
            return

        evento = {
            "portada": self.entry_portada.get().strip(),
            "titulo": titulo,
            "descripcion": self.text_descripcion.get("1.0", tk.END).strip(),
            "fecha": self.entry_fecha.get().strip(),
            "lugar": self.entry_lugar.get().strip(),
            "link": self.entry_link.get().strip(),
            "texto_link": self.entry_texto_link.get().strip()
        }

        self.controller.state["agenda"].append(evento)
        self.refresh_table()
        self.clear_fields()

    # --------------------------------------------------------
    # Editar evento
    # --------------------------------------------------------
    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        item = self.controller.state["agenda"][index]

        # Cargar datos
        self.entry_portada.delete(0, tk.END)
        self.entry_portada.insert(0, item.get("portada", ""))

        self.text_titulo.delete("1.0", tk.END)
        self.text_titulo.insert("1.0", item.get("titulo", ""))

        self.text_descripcion.delete("1.0", tk.END)
        self.text_descripcion.insert("1.0", item.get("descripcion", ""))

        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, item.get("fecha", ""))

        self.entry_lugar.delete(0, tk.END)
        self.entry_lugar.insert(0, item.get("lugar", ""))

        self.entry_link.delete(0, tk.END)
        self.entry_link.insert(0, item.get("link", ""))

        self.entry_texto_link.delete(0, tk.END)
        self.entry_texto_link.insert(0, item.get("texto_link", ""))

        # Eliminar temporalmente
        del self.controller.state["agenda"][index]
        self.refresh_table()

    # --------------------------------------------------------
    # Eliminar evento
    # --------------------------------------------------------
    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state["agenda"][index]
        self.refresh_table()

    # --------------------------------------------------------
    # Subir / Bajar
    # --------------------------------------------------------
    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index > 0:
            arr = self.controller.state["agenda"]
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.controller.state["agenda"]
        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    # --------------------------------------------------------
    # Refrescar tabla
    # --------------------------------------------------------
    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for ev in self.controller.state["agenda"]:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    ev.get("portada", ""),
                    ev.get("titulo", ""),
                    ev.get("fecha", ""),
                    ev.get("lugar", ""),
                    ev.get("link", "")
                )
            )

    # --------------------------------------------------------
    # Limpiar campos
    # --------------------------------------------------------
    def clear_fields(self):
        self.entry_portada.delete(0, tk.END)
        self.text_titulo.delete("1.0", tk.END)
        self.text_descripcion.delete("1.0", tk.END)
        self.entry_fecha.delete(0, tk.END)
        self.entry_lugar.delete(0, tk.END)
        self.entry_link.delete(0, tk.END)
        self.entry_texto_link.delete(0, tk.END)


# ============================================================
#   PESTAÑA PREVIEW Y GENERAR
# ============================================================
class PreviewTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=16, pady=10)

        ttk.Button(toolbar, text="Actualizar preview", command=self.update_preview).pack(side="left")
        ttk.Button(toolbar, text="Guardar JSON", command=self.save_json).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Generar HTML", command=self.generate_html).pack(side="right", padx=8)

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    # --------------------------------------------------------
    # PREVIEW JSON
    # --------------------------------------------------------
    def update_preview(self):
        datos = {
            "agenda": self.controller.state["agenda"]
        }
        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    # --------------------------------------------------------
    # GUARDAR JSON MAESTRO
    # --------------------------------------------------------
    def save_json(self):
        try:
            # Cargar maestro
            maestro = self.controller.master_json

            # Asegurar estructura
            maestro.setdefault("index_page", {})
            maestro["index_page"].setdefault("agenda", [])

            # IDs automáticos
            existing_ids = [
                ev.get("id", "")
                for ev in maestro["index_page"]["agenda"]
                if ev.get("id", "").startswith("evento")
            ]

            next_id = 1
            if existing_ids:
                nums = [int(e.replace("evento", "")) for e in existing_ids if e.replace("evento", "").isdigit()]
                if nums:
                    next_id = max(nums) + 1

            # Convertir eventos internos → estructura final
            nuevos_eventos = []
            for ev in self.controller.state["agenda"]:
                evento_final = {
                    "id": f"evento{next_id}",
                    "titulo": ev.get("titulo", ""),
                    "descripcion": ev.get("descripcion", ""),
                    "fecha": ev.get("fecha", ""),
                    "lugar": ev.get("lugar", ""),
                    "imagen": ev.get("portada", ""),
                    "link": ev.get("link", ""),
                    "texto_link": ev.get("texto_link", "")
                }
                nuevos_eventos.append(evento_final)
                next_id += 1

            # Añadir sin borrar los existentes
            maestro["index_page"]["agenda"].extend(nuevos_eventos)

            # Guardar JSON maestro
            with open(self.controller.json_path, "w", encoding="utf-8") as f:
                json.dump(maestro, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", "Agenda guardada correctamente en index.json")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    # --------------------------------------------------------
    # GENERAR HTML FINAL
    # --------------------------------------------------------
    def generate_html(self):
        try:
            # Cargar JSON maestro actualizado
            with open(self.controller.json_path, "r", encoding="utf-8") as f:
                datos = json.load(f)

            env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
            template = env.get_template("index_page.html")

            html_output = template.render(index_page=datos["index_page"])

            output_path = "geoso2-web-template/output/index.html"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_output)

            messagebox.showinfo("Éxito", f"HTML generado en:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el HTML:\n{e}")
