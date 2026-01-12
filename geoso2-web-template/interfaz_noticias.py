import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import datetime
import webbrowser
from PIL import Image
from collections import OrderedDict

# -----------------------------
# Ventana del editor con pestañas
# -----------------------------
class EditorWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Noticias")
        self.geometry("980x640")

        # Estado del documento: ahora múltiples noticias
        self.state = {
            "noticias": []  # lista de noticias
        }

        # Asegurar carpeta de imágenes
        os.makedirs("data/img", exist_ok=True)

        # Si es edición, cargar datos desde JSON
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                # Nuevo formato: ya trae lista de noticias
                if isinstance(datos.get("noticias"), list):
                    self.state["noticias"] = datos["noticias"]
                else:
                    # Formato antiguo: una sola noticia en la raíz
                    noticia_unica = {
                        "portada": datos.get("portada", ""),
                        "portada_base64": datos.get("portada_base64", ""),
                        "titulo": datos.get("titulo", ""),
                        "cuerpo": datos.get("cuerpo", ""),
                        "enlace": datos.get("enlace", {
                            "texto": "",
                            "url": "",
                            "usar_en_titulo": True,
                            "usar_en_portada": True
                        })
                    }
                    # Solo la añadimos si tiene algo mínimamente relleno
                    if noticia_unica["titulo"] or noticia_unica["cuerpo"]:
                        self.state["noticias"].append(noticia_unica)
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

        # Inicializar contenido si es edición
        if mode == "edit":
            self.tab_datos.set_data(self.state)
            self.tab_preview.update_preview()


# -----------------------------
# Pestaña: Datos (múltiples noticias)
# -----------------------------
class DatosTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Para guardar temporalmente la portada_base64 de la noticia en edición
        self.portada_base64_actual = ""

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Campos superiores ---

        ttk.Label(frm, text="Portada:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_portada = ttk.Entry(frm)
        self.entry_portada.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_portada).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Título de la noticia:").grid(row=1, column=0, sticky="w", pady=6)
        self.text_titulo = tk.Text(frm, wrap="word", height=2)
        self.text_titulo.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Cuerpo:").grid(row=2, column=0, sticky="nw", pady=6)
        cuerpo_frame = ttk.Frame(frm)
        cuerpo_frame.grid(row=2, column=1, sticky="nsew", pady=6)
        self.text_cuerpo = tk.Text(cuerpo_frame, wrap="word")
        self.text_cuerpo.pack(side="left", fill="both", expand=True)
        scroll_cuerpo = ttk.Scrollbar(cuerpo_frame, orient="vertical", command=self.text_cuerpo.yview)
        scroll_cuerpo.pack(side="right", fill="y")
        self.text_cuerpo.config(yscrollcommand=scroll_cuerpo.set)

        # Enlace
        ttk.Label(frm, text="Texto del enlace:").grid(row=3, column=0, sticky="w", pady=6)
        self.entry_enlace_texto = ttk.Entry(frm)
        self.entry_enlace_texto.grid(row=3, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="URL del enlace:").grid(row=4, column=0, sticky="w", pady=6)
        self.entry_enlace_url = ttk.Entry(frm)
        self.entry_enlace_url.grid(row=4, column=1, sticky="ew", pady=6)
        
        ttk.Button(
            frm,
            text="Probar enlace",
            command=self.probar_enlace
        ).grid(row=4, column=2, padx=8)

        # Checkbuttons para usar enlace en título/portada
        self.var_link_titulo = tk.BooleanVar(value=True)
        self.var_link_portada = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            frm,
            text="Usar este enlace en el título",
            variable=self.var_link_titulo
        ).grid(row=5, column=0, sticky="w", pady=(6, 0))

        ttk.Checkbutton(
            frm,
            text="Usar este enlace en la portada",
            variable=self.var_link_portada
        ).grid(row=5, column=1, sticky="w")

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(2, weight=1)

        # --- Botones de gestión de noticias ---

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        # --- Tabla de noticias ---

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

    # ---------- Gestión de imagen de portada ----------
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

            self.entry_portada.delete(0, tk.END)
            self.entry_portada.insert(0, destino)

            # Guardar base64 solo para la noticia actual (no en el estado global directamente)
            with open(destino, "rb") as img_file:
                b64 = base64.b64encode(img_file.read()).decode("utf-8")
                self.portada_base64_actual = b64

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo procesar la imagen de portada:\n{e}"
            )

    # ---------- Probar enlace ----------
    def probar_enlace(self):
        url = self.entry_enlace_url.get().strip()

        if not url:
            messagebox.showwarning("Aviso", "No hay ninguna URL para probar.")
            return

        try:
            # Si es un archivo HTML dentro del proyecto
            if url.endswith(".html"):
                ruta_absoluta = os.path.abspath(url)
                if os.path.exists(ruta_absoluta):
                    webbrowser.open_new_tab(f"file:///{ruta_absoluta}")
                else:
                    messagebox.showerror("Error", f"No se encontró el archivo HTML:\n{ruta_absoluta}")
            elif url.startswith(("http://", "https://")):
                webbrowser.open_new_tab(url)
            else:
                messagebox.showerror("Error", "El enlace debe ser una URL válida o un archivo .html del proyecto.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")

    # ---------- CRUD de noticias ----------

    def add_item(self):
        portada = self.entry_portada.get().strip()
        titulo = self.text_titulo.get("1.0", tk.END).strip()
        cuerpo = self.text_cuerpo.get("1.0", tk.END).strip()
        enlace_texto = self.entry_enlace_texto.get().strip()
        enlace_url = self.entry_enlace_url.get().strip()
        usar_en_titulo = self.var_link_titulo.get()
        usar_en_portada = self.var_link_portada.get()

        if not titulo:
            messagebox.showwarning("Aviso", "Debes introducir al menos un título para la noticia.")
            return

        noticia = {
            "portada": portada,
            "portada_base64": self.portada_base64_actual,
            "titulo": titulo,
            "cuerpo": cuerpo,
            "enlace": {
                "texto": enlace_texto,
                "url": enlace_url,
                "usar_en_titulo": usar_en_titulo,
                "usar_en_portada": usar_en_portada
            }
        }

        self.controller.state["noticias"].append(noticia)
        self.refresh_table()

        # Limpiar campos para siguiente noticia
        self.entry_portada.delete(0, tk.END)
        self.text_titulo.delete("1.0", tk.END)
        self.text_cuerpo.delete("1.0", tk.END)
        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_url.delete(0, tk.END)
        self.var_link_titulo.set(True)
        self.var_link_portada.set(True)
        self.portada_base64_actual = ""

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state["noticias"][index]
        self.refresh_table()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        item = self.controller.state["noticias"][index]

        # Rellenar campos con la noticia seleccionada
        self.entry_portada.delete(0, tk.END)
        self.entry_portada.insert(0, item.get("portada", ""))

        self.text_titulo.delete("1.0", tk.END)
        self.text_titulo.insert("1.0", item.get("titulo", ""))

        self.text_cuerpo.delete("1.0", tk.END)
        self.text_cuerpo.insert("1.0", item.get("cuerpo", ""))

        enlace = item.get("enlace", {})
        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_texto.insert(0, enlace.get("texto", ""))

        self.entry_enlace_url.delete(0, tk.END)
        self.entry_enlace_url.insert(0, enlace.get("url", ""))

        self.var_link_titulo.set(enlace.get("usar_en_titulo", True))
        self.var_link_portada.set(enlace.get("usar_en_portada", True))

        self.portada_base64_actual = item.get("portada_base64", "")

        # Eliminar la noticia de la lista; se volverá a guardar al pulsar "Añadir"
        del self.controller.state["noticias"][index]
        self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index > 0:
            arr = self.controller.state["noticias"]
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.controller.state["noticias"]
        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def refresh_table(self):
        # Vaciar tabla
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        # Rellenar
        for n in self.controller.state["noticias"]:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    n.get("portada", ""),
                    n.get("titulo", ""),
                    n.get("enlace", {}).get("url", "")
                )
            )

    def set_data(self, datos):
        # Cargar lista de noticias al abrir en modo edición
        self.controller.state["noticias"] = datos.get("noticias", [])
        self.refresh_table()


# -----------------------------
# Pestaña: Preview y Generar
# -----------------------------
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

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    def update_preview(self):
        # Construir datos para preview
        datos = {
            "noticias": [],
            "fecha": datetime.datetime.now().strftime("%d-%m-%Y")
        }

        for n in self.controller.state.get("noticias", []):
            copia = n.copy()
            # Quitar la clave base64 para el JSON de preview
            copia.pop("portada_base64", None)
            datos["noticias"].append(copia)

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
            maestro["index_page"].setdefault("noticias", [])

            nueva = OrderedDict()
            nueva["titulo"] = datos.get("titulo", "")
            nueva["imagen"] = datos.get("portada", "")
            nueva["descripcion"] = datos.get("cuerpo", "")
            nueva["link"] = datos.get("enlace", {}).get("url", "")
            nueva["link_text"] = datos.get("enlace", {}).get("texto", "")

            maestro["index_page"]["noticias"].append(nueva)

            with open(index_json, "w", encoding="utf-8") as f:
                json.dump(maestro, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", "Noticia añadida correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la noticia:\n{e}")
