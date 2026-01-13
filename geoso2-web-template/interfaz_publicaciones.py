import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
from jinja2 import Environment, FileSystemLoader


# -----------------------------
# Ventana del editor de Publicaciones
# -----------------------------
class EditorWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Publicaciones")
        self.geometry("980x640")

        # Estado del documento: diccionario de años → lista de publicaciones
        self.state = {
            "publicaciones": {}
        }

        # Cargar JSON en modo edición
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                if isinstance(datos, dict) and isinstance(datos.get("publicaciones"), dict):
                    self.state["publicaciones"] = datos["publicaciones"]
                else:
                    self.state["publicaciones"] = {}

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
            self.tab_datos.set_data(self.state)
            self.tab_preview.update_preview()


# -----------------------------
# Pestaña: Datos
# -----------------------------
class DatosTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # -------------------------
        # Selector de año
        # -------------------------
        ttk.Label(frm, text="Año:").grid(row=0, column=0, sticky="w", pady=6)

        self.combo_year = ttk.Combobox(frm, state="readonly")
        self.combo_year.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Button(frm, text="Añadir año", command=self.add_year).grid(row=0, column=2, padx=6)
        ttk.Button(frm, text="Eliminar año", command=self.delete_year).grid(row=0, column=3, padx=6)

        frm.columnconfigure(1, weight=1)

        # -------------------------
        # Campos de publicación
        # -------------------------
        ttk.Label(frm, text="Autores:").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_autores = ttk.Entry(frm)
        self.entry_autores.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Título:").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_titulo = ttk.Entry(frm)
        self.entry_titulo.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Tipo:").grid(row=3, column=0, sticky="w", pady=6)
        self.entry_tipo = ttk.Entry(frm)
        self.entry_tipo.grid(row=3, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Revista:").grid(row=4, column=0, sticky="w", pady=6)
        self.entry_revista = ttk.Entry(frm)
        self.entry_revista.grid(row=4, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Volumen:").grid(row=5, column=0, sticky="w", pady=6)
        self.entry_volumen = ttk.Entry(frm)
        self.entry_volumen.grid(row=5, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Número:").grid(row=6, column=0, sticky="w", pady=6)
        self.entry_num = ttk.Entry(frm)
        self.entry_num.grid(row=6, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="URL:").grid(row=7, column=0, sticky="w", pady=6)
        self.entry_link = ttk.Entry(frm)
        self.entry_link.grid(row=7, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Probar enlace", command=self.probar_enlace).grid(row=7, column=2, padx=6)

        # -------------------------
        # Botones CRUD
        # -------------------------
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=8, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)
        ttk.Button(frm, text="Actualizar", command=self.refresh_table).grid(row=0, column=4, padx=6)


        # -------------------------
        # Tabla
        # -------------------------
        self.tree = ttk.Treeview(
            frm,
            columns=("Autores", "Título", "Tipo", "Revista", "Volumen", "Num", "Link"),
            show="headings",
            height=10
        )
        self.tree.grid(row=9, column=0, columnspan=4, sticky="nsew")

        for col in ("Autores", "Título", "Tipo", "Revista", "Volumen", "Num", "Link"):
            self.tree.heading(col, text=col)

        frm.rowconfigure(9, weight=1)

    # -------------------------
    # Gestión de años
    # -------------------------
    def add_year(self):
        year = tk.simpledialog.askstring("Nuevo año", "Introduce el año (ej: 2025):")
        if not year:
            return

        if year in self.controller.state["publicaciones"]:
            messagebox.showwarning("Aviso", "Ese año ya existe.")
            return

        self.controller.state["publicaciones"][year] = []
        self.refresh_years()
        self.combo_year.set(year)
        self.refresh_table()

    def delete_year(self):
        year = self.combo_year.get()
        if not year:
            return

        # Confirmación antes de borrar
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que quieres eliminar el año {year}?\nEsta acción no se puede deshacer."
        )

        if not confirmar:
            return

        del self.controller.state["publicaciones"][year]
        self.refresh_years()
        self.refresh_table()


    def refresh_years(self):
        years = sorted(self.controller.state["publicaciones"].keys(), reverse=True)
        self.combo_year["values"] = years
        if years:
            self.combo_year.set(years[0])

    # -------------------------
    # CRUD
    # -------------------------
    def add_item(self):
        year = self.combo_year.get()
        if not year:
            messagebox.showwarning("Aviso", "Debes seleccionar un año.")
            return

        pub = {
            "autores": self.entry_autores.get().strip(),
            "titulo": self.entry_titulo.get().strip(),
            "tipo": self.entry_tipo.get().strip(),
            "revista": self.entry_revista.get().strip(),
            "volumen": self.entry_volumen.get().strip(),
            "num": self.entry_num.get().strip(),
            "link": self.entry_link.get().strip()
        }

        if not pub["titulo"]:
            messagebox.showwarning("Aviso", "Debes introducir un título.")
            return

        self.controller.state["publicaciones"][year].append(pub)
        self.refresh_table()
        self.clear_fields()

    def delete_item(self):
        year = self.combo_year.get()
        if not year:
            return

        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        del self.controller.state["publicaciones"][year][index]
        self.refresh_table()

    def edit_item(self):
        year = self.combo_year.get()
        if not year:
            return

        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        item = self.controller.state["publicaciones"][year][index]

        self.entry_autores.delete(0, tk.END)
        self.entry_autores.insert(0, item["autores"])

        self.entry_titulo.delete(0, tk.END)
        self.entry_titulo.insert(0, item["titulo"])

        self.entry_tipo.delete(0, tk.END)
        self.entry_tipo.insert(0, item["tipo"])

        self.entry_revista.delete(0, tk.END)
        self.entry_revista.insert(0, item["revista"])

        self.entry_volumen.delete(0, tk.END)
        self.entry_volumen.insert(0, item["volumen"])

        self.entry_num.delete(0, tk.END)
        self.entry_num.insert(0, item["num"])

        self.entry_link.delete(0, tk.END)
        self.entry_link.insert(0, item["link"])

        del self.controller.state["publicaciones"][year][index]
        self.refresh_table()

    def move_up(self):
        year = self.combo_year.get()
        if not year:
            return

        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        arr = self.controller.state["publicaciones"][year]

        if index > 0:
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        year = self.combo_year.get()
        if not year:
            return

        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        arr = self.controller.state["publicaciones"][year]

        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    # -------------------------
    # Utilidades
    # -------------------------
    def probar_enlace(self):
        url = self.entry_link.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "No hay URL para probar.")
            return

        try:
            if url.startswith(("http://", "https://")):
                webbrowser.open_new_tab(url)
            else:
                messagebox.showerror("Error", "El enlace debe ser una URL válida.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        year = self.combo_year.get()
        if not year:
            return

        for p in self.controller.state["publicaciones"].get(year, []):
            self.tree.insert(
                "",
                tk.END,
                values=(
                    p["autores"],
                    p["titulo"],
                    p["tipo"],
                    p["revista"],
                    p["volumen"],
                    p["num"],
                    p["link"]
                )
            )

    def clear_fields(self):
        self.entry_autores.delete(0, tk.END)
        self.entry_titulo.delete(0, tk.END)
        self.entry_tipo.delete(0, tk.END)
        self.entry_revista.delete(0, tk.END)
        self.entry_volumen.delete(0, tk.END)
        self.entry_num.delete(0, tk.END)
        self.entry_link.delete(0, tk.END)

    def set_data(self, datos):
        self.controller.state["publicaciones"] = datos.get("publicaciones", {})
        self.refresh_years()
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
        datos = {
            "publicaciones": self.controller.state.get("publicaciones", {})
        }
        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    def save_json(self):
        datos = {
            "publicaciones": self.controller.state.get("publicaciones", {})
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
        datos = self.controller.state.get("publicaciones", {})

        bloques = ""

        for year in sorted(datos.keys(), reverse=True):
            bloques += f"""
            <hr>
            <h4><strong>{year}</strong></h4>
            <br>
            <div class="references csl-bib-body hanging-indent" role="list">
            """

            for p in datos[year]:
                autores = p.get("autores", "")
                titulo = p.get("titulo", "")
                tipo = p.get("tipo", "")
                revista = p.get("revista", "")
                volumen = p.get("volumen", "")
                num = p.get("num", "")
                link = p.get("link", "")

                bloques += f"""
                <div class="csl-entry" role="listitem">
                    {autores} ({year}). {titulo} [{tipo}].
                    <i>{revista}</i>{", " + volumen if volumen else ""}{", " + num if num else ""}.
                    {"<a href='" + link + "' target='_blank'>" + link + "</a>" if link else ""}
                    <br>
                </div>
                """

            bloques += "</div><br>"


            html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Publicaciones</title>
            <style>
                body {{
                    font-family: Segoe UI, sans-serif;
                    margin: 40px auto;
                    max-width: 900px;
                    line-height: 1.6;
                }}
                .csl-entry {{
                    margin-bottom: 10px;
                }}
                i {{
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <h1>Publicaciones</h1>
            {bloques}
        </body>
        </html>
        """

        temp_html = "data/publicaciones_preview.html"
        os.makedirs("data", exist_ok=True)
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open_new_tab(f"file:///{os.path.abspath(temp_html)}")

    def generate_html(self):
        datos = self.controller.state.get("publicaciones", {})

        try:
            env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
            template = env.get_template("publicaciones.html")
            html_output = template.render(publicaciones=datos)

            output_dir = "geoso2-web-template/output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "publicaciones.html")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_output)

            messagebox.showinfo("Éxito", f"Archivo HTML generado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el archivo HTML:\n{e}")
