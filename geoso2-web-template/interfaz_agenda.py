import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import datetime
import webbrowser
from PIL import Image
import base64
from jinja2 import Environment, FileSystemLoader


# -----------------------------
# Ventana del editor con pestañas
# -----------------------------
class AgendaWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Agenda")
        self.geometry("980x640")

        # Estado del documento: ahora múltiples eventos en "agenda"
        self.state = {
            "portada": "",
            "titulo": "",
            "fecha del evento": "",
            "hora": "",
            "lugar": "",
            "descripcion": "",
            "enlace": {
                "texto": "",
                "url": "",
                "usar_en_titulo": True,
                "usar_en_portada": True
            },
        }

        # Asegurar carpeta de imágenes
        os.makedirs("data/img", exist_ok=True)

        # Si es edición, cargar datos desde JSON
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                # Nuevo formato: ya trae lista de agenda
                if isinstance(datos.get("agenda"), list):
                    self.state["agenda"] = datos["agenda"]
                else:
                    # Formato antiguo: una sola entrada en la raíz
                    evento_unico = {
                        "portada": datos.get("portada", ""),
                        "portada_base64": datos.get("portada_base64", ""),
                        "titulo": datos.get("titulo", ""),
                        "fecha del evento": datos.get("fecha del evento", ""),
                        "hora": datos.get("hora", ""),
                        "lugar": datos.get("lugar", ""),
                        "cuerpo": datos.get("cuerpo", ""),
                        "enlace": datos.get("enlace", {
                            "texto": "",
                            "url": "",
                            "usar_en_titulo": True,
                            "usar_en_portada": True
                        })
                    }
                    if evento_unico["titulo"] or evento_unico["cuerpo"]:
                        self.state["agenda"].append(evento_unico)
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
# Pestaña: Datos (múltiples eventos)
# -----------------------------
class DatosTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Para guardar temporalmente la portada_base64 del evento en edición
        self.portada_base64_actual = ""

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Campos superiores ---

        ttk.Label(frm, text="Portada:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_portada = ttk.Entry(frm)
        self.entry_portada.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_portada).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Título del documento:").grid(row=1, column=0, sticky="w", pady=6)
        self.text_titulo = tk.Text(frm, wrap="word", height=2)
        self.text_titulo.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Fecha del evento:").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_fecha_evento = ttk.Entry(frm)
        self.entry_fecha_evento.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Lugar:").grid(row=5, column=0, sticky="w", pady=6)
        self.entry_lugar = ttk.Entry(frm)
        self.entry_lugar.grid(row=4, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Descripción:").grid(row=6, column=0, sticky="nw", pady=6)
        cuerpo_frame = ttk.Frame(frm)
        cuerpo_frame.grid(row=5, column=1, sticky="nsew", pady=6)
        self.text_cuerpo = tk.Text(cuerpo_frame, wrap="word", height=15)
        self.text_cuerpo.pack(side="left", fill="both", expand=True)
        scroll_cuerpo = ttk.Scrollbar(cuerpo_frame, orient="vertical", command=self.text_cuerpo.yview)
        scroll_cuerpo.pack(side="right", fill="y")
        self.text_cuerpo.config(yscrollcommand=scroll_cuerpo.set)

        # Enlace
        ttk.Label(frm, text="Texto del enlace:").grid(row=6, column=0, sticky="w", pady=6)
        self.entry_enlace_texto = ttk.Entry(frm)
        self.entry_enlace_texto.grid(row=6, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="URL del enlace:").grid(row=7, column=0, sticky="w", pady=6)
        self.entry_enlace_url = ttk.Entry(frm)
        self.entry_enlace_url.grid(row=7, column=1, sticky="ew", pady=6)

        ttk.Button(
            frm,
            text="Probar enlace",
            command=self.probar_enlace
        ).grid(row=7, column=2, padx=8)

        # Checkbuttons para usar enlace en título/portada
        self.var_link_titulo = tk.BooleanVar(value=True)
        self.var_link_portada = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            frm,
            text="Usar este enlace en el título",
            variable=self.var_link_titulo
        ).grid(row=8, column=0, sticky="w", pady=(6, 0))

        ttk.Checkbutton(
            frm,
            text="Usar este enlace en la portada",
            variable=self.var_link_portada
        ).grid(row=8, column=1, sticky="w")

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(5, weight=1)

        # Actualizar estado al escribir
        self.entry_portada.bind("<KeyRelease>", self.update_state)
        self.text_titulo.bind("<KeyRelease>", self.update_state)
        self.entry_fecha.bind("<KeyRelease>", self.update_state)
        self.entry_lugar.bind("<KeyRelease>", self.update_state)
        self.text_cuerpo.bind("<KeyRelease>", self.update_state)
        self.entry_enlace_texto.bind("<KeyRelease>", self.update_state)
        self.entry_enlace_url.bind("<KeyRelease>", self.update_state)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        # --- Tabla de eventos ---

        self.tree = ttk.Treeview(
            frm,
            columns=("Imagen", "Título", "Fecha", "Lugar", "Enlace"),
            show="headings",
            height=10
        )
        self.tree.grid(row=10, column=0, columnspan=3, sticky="nsew")
        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Fecha", text="Fecha evento")
        self.tree.heading("Lugar", text="Lugar")
        self.tree.heading("Enlace", text="Enlace")

        frm.rowconfigure(10, weight=1)

    # ---------- Gestión de imagen de portada ----------
    def select_portada(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )

        if not ruta:
            return

        try:
            nombre = os.path.basename(ruta)
            destino = os.path.join("", nombre)

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

        if not url.startswith(("http://", "https://")):
            messagebox.showerror("Error", "La URL debe empezar por http:// o https://")
            return

        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")

    # ---------- CRUD de eventos ----------

    def update_state(self, event=None):
        self.controller.state["titulo"] = self.text_titulo.get("1.0", tk.END).strip()
        self.controller.state["fecha del evento"] = self.entry_fecha.get().strip()
        self.controller.state["lugar"] = self.entry_lugar.get().strip()
        self.controller.state["portada"] = self.entry_portada.get().strip()
        self.controller.state["descripcion"] = self.text_cuerpo.get("1.0", tk.END).strip()
        self.controller.state["enlace"]["texto"] = self.entry_enlace_texto.get().strip()
        self.controller.state["enlace"]["url"] = self.entry_enlace_url.get().strip()
        self.controller.state["enlace"]["usar_en_titulo"] = self.var_link_titulo.get()
        self.controller.state["enlace"]["usar_en_portada"] = self.var_link_portada.get()

        if not titulo:
            messagebox.showwarning("Aviso", "Debes introducir al menos un título para el evento.")
            return

        evento = {
            "portada": portada,
            "portada_base64": self.portada_base64_actual,
            "titulo": titulo,
            "fecha del evento": fecha_evento,
            "hora": hora,
            "lugar": lugar,
            "cuerpo": cuerpo,
            "enlace": {
                "texto": enlace_texto,
                "url": enlace_url,
                "usar_en_titulo": usar_en_titulo,
                "usar_en_portada": usar_en_portada
            }
        }

        self.controller.state["agenda"].append(evento)
        self.refresh_table()

        # Limpiar campos
        self.entry_portada.delete(0, tk.END)
        self.text_titulo.delete("1.0", tk.END)
        self.entry_fecha_evento.delete(0, tk.END)
        self.entry_hora.delete(0, tk.END)
        self.entry_lugar.delete(0, tk.END)
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
        del self.controller.state["agenda"][index]
        self.refresh_table()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        item = self.controller.state["agenda"][index]

        self.entry_portada.delete(0, tk.END)
        self.entry_portada.insert(0, item.get("portada", ""))

        self.text_titulo.delete("1.0", tk.END)
        self.text_titulo.insert("1.0", item.get("titulo", ""))

        self.entry_fecha_evento.delete(0, tk.END)
        self.entry_fecha_evento.insert(0, item.get("fecha del evento", ""))

        self.entry_hora.delete(0, tk.END)
        self.entry_hora.insert(0, item.get("hora", ""))

        self.entry_lugar.delete(0, tk.END)
        self.entry_lugar.insert(0, item.get("lugar", ""))

        self.text_cuerpo.delete("1.0", tk.END)
        self.text_cuerpo.insert("1.0", datos.get("descripcion", ""))

        enlace = item.get("enlace", {})
        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_texto.insert(0, enlace.get("texto", ""))

        self.entry_enlace_url.delete(0, tk.END)
        self.entry_enlace_url.insert(0, enlace.get("url", ""))

        self.var_link_titulo.set(enlace.get("usar_en_titulo", True))
        self.var_link_portada.set(enlace.get("usar_en_portada", True))

        self.portada_base64_actual = item.get("portada_base64", "")

        del self.controller.state["agenda"][index]
        self.refresh_table()

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

    def refresh_table(self):
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        for ev in self.controller.state["agenda"]:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    ev.get("portada", ""),
                    ev.get("titulo", ""),
                    ev.get("fecha del evento", ""),
                    ev.get("lugar", ""),
                    ev.get("enlace", {}).get("url", "")
                )
            )

    def set_data(self, datos):
        self.controller.state["agenda"] = datos.get("agenda", [])
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
        ttk.Button(toolbar, text="Generar HTML", command=self.generate_html).pack(side="right", padx=8)

        info = ttk.Label(toolbar, text="Revisa el JSON antes de guardar.")
        info.pack(side="left", padx=16)

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    def update_preview(self):
        datos = {
            "agenda": [],
            "fecha": datetime.datetime.now().strftime("%d-%m-%Y")
        }

        for ev in self.controller.state.get("agenda", []):
            copia = ev.copy()
            copia.pop("portada_base64", None)
            datos["agenda"].append(copia)

        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    def save_json(self):
        datos = self.controller.state.copy()

        index_json = "geoso2-web-template/json/index.json"
        try:
            if os.path.exists(index_json):
                with open(index_json, "r", encoding="utf-8") as f:
                    agenda = json.load(f)
            else:
                agenda = {}
            
            agenda.setdefault("index_page", {})
            agenda["index_page"].setdefault("agenda", [])

            nuevo_id = f"evento{len(agenda['index_page']['agenda']) + 1}"
            nuevo_evento = {
                "id": nuevo_id,
                "titulo": datos.get("titulo", ""),
                "descripcion": datos.get("descripcion", ""),
                "fecha": f"Fecha: {datos.get('fecha del evento', '')} Hora: {datos.get('hora', '')}",
                "lugar": f"Lugar: {datos.get('lugar', '')}",
                "imagen": datos.get("portada", ""),
                "link": datos.get("enlace", {}).get("url", ""),
                "texto_link": datos.get("enlace", {}).get("texto", "")
            }

            agenda["index_page"]["agenda"].append(nuevo_evento)
            with open(index_json, "w", encoding="utf-8") as f:
                json.dump(agenda, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Éxito", "El JSON de la agenda se ha guardado correctamente.")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")
