import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
from PIL import Image
from jinja2 import Environment, FileSystemLoader


# -----------------------------
# Ventana del editor de Agenda
# -----------------------------
class EditorWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Agenda")
        self.geometry("1080x840")

        # Estado del documento: múltiples eventos de agenda
        self.state = {
            "agenda": []  # lista de eventos
        }

        # Carpeta de imágenes para la agenda
        os.makedirs("data/img", exist_ok=True)

        # Carga en modo edición
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                # Puede venir como {"agenda": [...]} o directamente como lista
                if isinstance(datos, dict) and isinstance(datos.get("agenda"), list):
                    eventos_raw = datos["agenda"]
                elif isinstance(datos, list):
                    eventos_raw = datos
                else:
                    eventos_raw = []

                # Normalizar eventos
                self.state["agenda"] = [self.normalize_event(ev) for ev in eventos_raw]

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON de agenda:\n{e}")

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

    # Normalización de un evento de agenda (para legacy)
    def normalize_event(self, ev):
        nuevo = {
            "titulo": ev.get("titulo") or ev.get("titulo1") or "",
            "descripcion": ev.get("descripcion") or ev.get("descripcion1") or "",
            "fecha": ev.get("fecha", ""),
            "hora": ev.get("hora", ""),
            "lugar": ev.get("lugar", ""),
            "imagen": ev.get("imagen", ""),
            "alt": ev.get("alt", ""),
            "link": ev.get("link", ""),
            "texto_link": ev.get("texto_link", "")
        }
        return nuevo


# -----------------------------
# Pestaña: Datos (múltiples eventos)
# -----------------------------
class DatosTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Campos superiores ---

        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_imagen).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Evento Nº:").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_alt = ttk.Entry(frm)
        self.entry_alt.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Título del evento:").grid(row=2, column=0, sticky="w", pady=6)
        self.text_titulo = tk.Text(frm, wrap="word", height=2)
        self.text_titulo.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Descripción:").grid(row=3, column=0, sticky="nw", pady=6)
        desc_frame = ttk.Frame(frm)
        desc_frame.grid(row=3, column=1, sticky="nsew", pady=6)
        self.text_descripcion = tk.Text(desc_frame, wrap="word")
        self.text_descripcion.pack(side="left", fill="both", expand=True)
        scroll_desc = ttk.Scrollbar(desc_frame, orient="vertical", command=self.text_descripcion.yview)
        scroll_desc.pack(side="right", fill="y")
        self.text_descripcion.config(yscrollcommand=scroll_desc.set)

        ttk.Label(frm, text="Fecha:").grid(row=4, column=0, sticky="w", pady=6)
        self.entry_fecha = ttk.Entry(frm)
        self.entry_fecha.grid(row=4, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Hora:").grid(row=5, column=0, sticky="w", pady=6)
        self.entry_hora = ttk.Entry(frm)
        self.entry_hora.grid(row=5, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Lugar:").grid(row=6, column=0, sticky="w", pady=6)
        self.entry_lugar = ttk.Entry(frm)
        self.entry_lugar.grid(row=6, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="URL del enlace:").grid(row=7, column=0, sticky="w", pady=6)
        self.entry_link = ttk.Entry(frm)
        self.entry_link.grid(row=7, column=1, sticky="ew", pady=6)
        ttk.Button(
            frm,
            text="Probar enlace",
            command=self.probar_enlace
        ).grid(row=7, column=2, padx=8)

        ttk.Label(frm, text="Texto del enlace:").grid(row=8, column=0, sticky="w", pady=6)
        self.entry_texto_link = ttk.Entry(frm)
        self.entry_texto_link.grid(row=8, column=1, sticky="ew", pady=6)

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(3, weight=1)

        # --- Botones de gestión de eventos ---

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
            columns=("Imagen", "Título", "Fecha", "Lugar", "Link"),
            show="headings",
            height=10
        )
        self.tree.grid(row=10, column=0, columnspan=3, sticky="nsew")

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Lugar", text="Lugar")
        self.tree.heading("Link", text="Link")

        frm.rowconfigure(10, weight=1)

    # ---------- Seleccionar imagen ----------
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
                img = img.convert("RGB")
                img.thumbnail((300, 300), Image.LANCZOS)

                canvas = Image.new("RGB", (300, 300), "white")
                x = (300 - img.width) // 2
                y = (300 - img.height) // 2
                canvas.paste(img, (x, y))

                canvas.save(destino, quality=90)

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, destino)

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo procesar la imagen:\n{e}"
            )

    # ---------- Probar enlace ----------
    def probar_enlace(self):
        url = self.entry_link.get().strip()

        if not url:
            messagebox.showwarning("Aviso", "No hay ninguna URL para probar.")
            return

        try:
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

    # ---------- CRUD de eventos ----------
    def add_item(self):
        imagen = self.entry_imagen.get().strip()
        alt = self.entry_alt.get().strip()
        titulo = self.text_titulo.get("1.0", tk.END).strip()
        descripcion = self.text_descripcion.get("1.0", tk.END).strip()
        fecha = self.entry_fecha.get().strip()
        hora = self.entry_hora.get().strip()
        lugar = self.entry_lugar.get().strip()
        link = self.entry_link.get().strip()
        texto_link = self.entry_texto_link.get().strip()

        if not titulo:
            messagebox.showwarning("Aviso", "Debes introducir al menos un título para el evento.")
            return

        evento = {
            "imagen": imagen,
            "alt": alt,
            "titulo": titulo,
            "descripcion": descripcion,
            "fecha": fecha,
            "hora": hora,
            "lugar": lugar,
            "link": link,
            "texto_link": texto_link
        }

        self.controller.state["agenda"].append(evento)
        self.refresh_table()
        self.clear_fields()

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

        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, item.get("imagen", ""))

        self.entry_alt.delete(0, tk.END)
        self.entry_alt.insert(0, item.get("alt", ""))

        self.text_titulo.delete("1.0", tk.END)
        self.text_titulo.insert("1.0", item.get("titulo", ""))

        self.text_descripcion.delete("1.0", tk.END)
        self.text_descripcion.insert("1.0", item.get("descripcion", ""))

        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, item.get("fecha", ""))

        self.entry_hora.delete(0, tk.END)
        self.entry_hora.insert(0, item.get("hora", ""))

        self.entry_lugar.delete(0, tk.END)
        self.entry_lugar.insert(0, item.get("lugar", ""))

        self.entry_link.delete(0, tk.END)
        self.entry_link.insert(0, item.get("link", ""))

        self.entry_texto_link.delete(0, tk.END)
        self.entry_texto_link.insert(0, item.get("texto_link", ""))

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

        for e in self.controller.state["agenda"]:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    e.get("imagen", ""),
                    e.get("titulo", ""),
                    e.get("fecha", ""),
                    e.get("lugar", ""),
                    e.get("link", "")
                )
            )

    def clear_fields(self):
        self.entry_imagen.delete(0, tk.END)
        self.entry_alt.delete(0, tk.END)
        self.text_titulo.delete("1.0", tk.END)
        self.text_descripcion.delete("1.0", tk.END)
        self.entry_fecha.delete(0, tk.END)
        self.entry_hora.delete(0, tk.END)
        self.entry_lugar.delete(0, tk.END)
        self.entry_link.delete(0, tk.END)
        self.entry_texto_link.delete(0, tk.END)

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
        ttk.Button(toolbar, text="Generar archivo HTML", command=self.generate_html).pack(side="right", padx=8)
        ttk.Button(toolbar, text="Abrir Geoso2.es", command=self.open_output_html).pack(side="right")

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    def update_preview(self):
        datos = {
            "agenda": self.controller.state.get("agenda", [])
        }
        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    def save_json(self):
        datos = {
            "agenda": self.controller.state.get("agenda", [])
        }
        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir="geoso2-web-template/json"
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Guardado", f"Archivo JSON guardado en {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")

    def preview_web(self):
        # Copiamos el estado actual
        datos = {
            "agenda": self.controller.state.get("agenda", [])
        }

        # Ajustar rutas de imagen para que funcionen desde /geoso2-web-template/data/
        agenda_ajustada = []
        for e in datos["agenda"]:
            nuevo = e.copy()
            imagen = nuevo.get("imagen", "").replace("\\", "/")

            # Si la imagen está en data/img/... convertimos a ruta relativa desde preview
            if "data/img" in imagen:
                # Queremos ../data/img/archivo.png
                nuevo["imagen"] = "../" + imagen.split("data/")[1]
            else:
                nuevo["imagen"] = imagen

            agenda_ajustada.append(nuevo)

        # Renderizar usando el template real
        try:
            env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
            template = env.get_template("agenda.html")
            html = template.render(agenda=agenda_ajustada)

            # Guardar preview
            ruta = "geoso2-web-template/data/preview_agenda.html"
            os.makedirs("geoso2-web-template/data", exist_ok=True)

            with open(ruta, "w", encoding="utf-8") as f:
                f.write(html)

            webbrowser.open_new_tab(f"file:///{os.path.abspath(ruta)}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el preview HTML:\n{e}")



    def generate_html(self):
        datos = {
            "agenda": self.controller.state.get("agenda", [])
        }

        try:
            env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
            template = env.get_template("agenda.html")
            html_output = template.render(agenda=datos["agenda"])

            output_dir = "geoso2-web-template/output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "agenda.html")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_output)

            messagebox.showinfo("Éxito", f"Archivo HTML generado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el archivo HTML de agenda:\n{e}")

    def open_output_html(self):
        output_path = "geoso2-web-template/output/agenda.html"
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
