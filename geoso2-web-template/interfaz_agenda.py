import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
from PIL import Image
from jinja2 import Environment, FileSystemLoader


# ============================================================
#   EDITOR DE AGENDA
# ============================================================
class AgendaWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Editor de Agenda")
        self.geometry("980x640")

        # Rutas
        self.json_path = "geoso2-web-template/json/agenda.json"
        self.template_path = "geoso2-web-template/templates"
        self.output_html = "geoso2-web-template/output/agenda.html"
        self.preview_html = "data/agenda_preview.html"

        # Estado interno
        self.state = {"agenda": []}

        # Cargar JSON maestro
        self.load_json()

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_datos = DatosTab(self.notebook, self)
        self.tab_preview = PreviewTab(self.notebook, self)

        self.notebook.add(self.tab_datos, text="Datos")
        self.notebook.add(self.tab_preview, text="Preview y Generar")

        self.tab_preview.update_preview()

    # --------------------------------------------------------
    # Cargar agenda.json
    # --------------------------------------------------------
    def load_json(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                datos = json.load(f)

            datos.setdefault("agenda", [])

            # Normalizar eventos
            self.state["agenda"] = [self.normalize_event(ev) for ev in datos["agenda"]]

        else:
            self.state["agenda"] = []

    # --------------------------------------------------------
    # Normalizar un evento
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # Guardar JSON maestro
    # --------------------------------------------------------
    def save_json(self):
        try:
            datos = {"agenda": self.state["agenda"]}

            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", "agenda.json actualizado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar agenda.json:\n{e}")

    # --------------------------------------------------------
    # Generar HTML final
    # --------------------------------------------------------
    def generate_html(self):
        try:
            env = Environment(loader=FileSystemLoader(self.template_path))
            template = env.get_template("agenda.html")

            html = template.render(agenda=self.state["agenda"])

            with open(self.output_html, "w", encoding="utf-8") as f:
                f.write(html)

            messagebox.showinfo("Éxito", f"HTML generado en:\n{self.output_html}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar agenda.html:\n{e}")

    # --------------------------------------------------------
    # Previsualizar HTML temporal
    # --------------------------------------------------------
    def preview_html_file(self):
        try:
            env = Environment(loader=FileSystemLoader(self.template_path))
            template = env.get_template("agenda.html")

            html = template.render(agenda=self.state["agenda"])

            with open(self.preview_html, "w", encoding="utf-8") as f:
                f.write(html)

            webbrowser.open_new_tab(f"file:///{os.path.abspath(self.preview_html)}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la previsualización:\n{e}")


# ============================================================
#   PESTAÑA DE DATOS
# ============================================================
class DatosTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # Campos
        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w")
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew")
        ttk.Button(frm, text="Buscar", command=self.select_image).grid(row=0, column=2, padx=6)

        ttk.Label(frm, text="ALT:").grid(row=1, column=0, sticky="w")
        self.entry_alt = ttk.Entry(frm)
        self.entry_alt.grid(row=1, column=1, sticky="ew")

        ttk.Label(frm, text="Título:").grid(row=2, column=0, sticky="w")
        self.text_titulo = tk.Text(frm, height=2)
        self.text_titulo.grid(row=2, column=1, sticky="ew")

        ttk.Label(frm, text="Descripción:").grid(row=3, column=0, sticky="nw")
        self.text_descripcion = tk.Text(frm, height=5)
        self.text_descripcion.grid(row=3, column=1, sticky="ew")

        ttk.Label(frm, text="Fecha:").grid(row=4, column=0, sticky="w")
        self.entry_fecha = ttk.Entry(frm)
        self.entry_fecha.grid(row=4, column=1, sticky="ew")

        ttk.Label(frm, text="Hora:").grid(row=5, column=0, sticky="w")
        self.entry_hora = ttk.Entry(frm)
        self.entry_hora.grid(row=5, column=1, sticky="ew")

        ttk.Label(frm, text="Lugar:").grid(row=6, column=0, sticky="w")
        self.entry_lugar = ttk.Entry(frm)
        self.entry_lugar.grid(row=6, column=1, sticky="ew")

        ttk.Label(frm, text="Link:").grid(row=7, column=0, sticky="w")
        self.entry_link = ttk.Entry(frm)
        self.entry_link.grid(row=7, column=1, sticky="ew")

        ttk.Label(frm, text="Texto del enlace:").grid(row=8, column=0, sticky="w")
        self.entry_texto_link = ttk.Entry(frm)
        self.entry_texto_link.grid(row=8, column=1, sticky="ew")

        # Botones CRUD
        btns = ttk.Frame(frm)
        btns.grid(row=9, column=0, columnspan=3, pady=10)

        ttk.Button(btns, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btns, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btns, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btns, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btns, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        # Tabla
        self.tree = ttk.Treeview(
            frm,
            columns=("Imagen", "Título", "Fecha", "Lugar", "Link"),
            show="headings",
            height=10
        )
        self.tree.grid(row=10, column=0, columnspan=3, sticky="nsew")

        for col in ("Imagen", "Título", "Fecha", "Lugar", "Link"):
            self.tree.heading(col, text=col)

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(10, weight=1)

        self.refresh_table()

    # --------------------------------------------------------
    def select_image(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if ruta:
            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, ruta)

    # --------------------------------------------------------
    def add_item(self):
        evento = {
            "imagen": self.entry_imagen.get().strip(),
            "alt": self.entry_alt.get().strip(),
            "titulo": self.text_titulo.get("1.0", tk.END).strip(),
            "descripcion": self.text_descripcion.get("1.0", tk.END).strip(),
            "fecha": self.entry_fecha.get().strip(),
            "hora": self.entry_hora.get().strip(),
            "lugar": self.entry_lugar.get().strip(),
            "link": self.entry_link.get().strip(),
            "texto_link": self.entry_texto_link.get().strip()
        }

        self.controller.state["agenda"].append(evento)
        self.refresh_table()
        self.clear_fields()

    # --------------------------------------------------------
    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        ev = self.controller.state["agenda"][index]

        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, ev["imagen"])

        self.entry_alt.delete(0, tk.END)
        self.entry_alt.insert(0, ev["alt"])

        self.text_titulo.delete("1.0", tk.END)
        self.text_titulo.insert("1.0", ev["titulo"])

        self.text_descripcion.delete("1.0", tk.END)
        self.text_descripcion.insert("1.0", ev["descripcion"])

        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, ev["fecha"])

        self.entry_hora.delete(0, tk.END)
        self.entry_hora.insert(0, ev["hora"])

        self.entry_lugar.delete(0, tk.END)
        self.entry_lugar.insert(0, ev["lugar"])

        self.entry_link.delete(0, tk.END)
        self.entry_link.insert(0, ev["link"])

        self.entry_texto_link.delete(0, tk.END)
        self.entry_texto_link.insert(0, ev["texto_link"])

        del self.controller.state["agenda"][index]
        self.refresh_table()

    # --------------------------------------------------------
    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state["agenda"][index]
        self.refresh_table()

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
    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for ev in self.controller.state["agenda"]:
            self.tree.insert(
                "",
                tk.END,
                values=(ev["imagen"], ev["titulo"], ev["fecha"], ev["lugar"], ev["link"])
            )

    # --------------------------------------------------------
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
        ttk.Button(toolbar, text="Previsualizar en navegador", command=self.preview_web).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Guardar JSON", command=self.save_json).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Generar HTML final", command=self.generate_html).pack(side="right", padx=8)

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    # --------------------------------------------------------
    def update_preview(self):
        preview = json.dumps({"agenda": self.controller.state["agenda"]}, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    # --------------------------------------------------------
    def save_json(self):
        self.controller.save_json()

    # --------------------------------------------------------
    def generate_html(self):
        self.controller.generate_html()

    # --------------------------------------------------------
    def preview_web(self):
        self.controller.preview_html_file()
