import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
from jinja2 import Environment, FileSystemLoader




# ============================================================
#   PESTAÑA 2 — SECCIONES
# ============================================================
class SeccionesTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        self.entries = {}

        for i in range(1, 6):
            ttk.Label(frm, text=f"Pregunta {i}:").grid(row=(i - 1) * 2, column=0, sticky="w", pady=4)
            e_p = ttk.Entry(frm)
            e_p.grid(row=(i - 1) * 2, column=1, sticky="ew", pady=4)

            ttk.Label(frm, text=f"Respuesta {i}:").grid(row=(i - 1) * 2 + 1, column=0, sticky="w", pady=4)
            e_r = ttk.Entry(frm)
            e_r.grid(row=(i - 1) * 2 + 1, column=1, sticky="ew", pady=4)

            self.entries[f"pregunta{i}"] = e_p
            self.entries[f"respuesta{i}"] = e_r

        frm.columnconfigure(1, weight=1)
        ttk.Button(frm, text="Guardar secciones", command=self.save).grid(row=20, column=0, columnspan=2, pady=20)

        self.load_data()

    def load_data(self):
        secciones = self.controller.state["quienes_somos"]["secciones"][0]
        for key, widget in self.entries.items():
            widget.insert(0, secciones.get(key, ""))

    def save(self):
        secciones = self.controller.state["quienes_somos"]["secciones"][0]
        for key, widget in self.entries.items():
            secciones[key] = widget.get().strip()


# ============================================================
#   PESTAÑA 3 — INVESTIGADORES
# ============================================================
class InvestigadoresTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        form = ttk.Frame(main)
        form.grid(row=0, column=0, sticky="nsew")

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_nombre = ttk.Entry(form)
        self.entry_nombre.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Imagen (ruta):").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_imagen = ttk.Entry(form)
        self.entry_imagen.grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Button(form, text="Seleccionar", command=self.select_image).grid(row=1, column=2, padx=5)

        ttk.Label(form, text="Bio:").grid(row=2, column=0, sticky="nw", pady=4)
        self.text_bio = tk.Text(form, height=6, wrap="word")
        self.text_bio.grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)

        ttk.Label(form, text="Link:").grid(row=3, column=0, sticky="w", pady=4)
        self.entry_link = ttk.Entry(form)
        self.entry_link.grid(row=3, column=1, sticky="ew", pady=4)
        ttk.Button(form, text="Probar enlace", command=self.probar_enlace).grid(row=3, column=2, padx=5)

        ttk.Label(form, text="Texto del enlace:").grid(row=4, column=0, sticky="w", pady=4)
        self.entry_link_text = ttk.Entry(form)
        self.entry_link_text.grid(row=4, column=1, sticky="ew", pady=4)

        form.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=1, column=0, sticky="w", pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        self.tree = ttk.Treeview(
            main,
            columns=("Nombre", "Imagen", "Link", "LinkText"),
            show="headings",
            height=10
        )
        self.tree.grid(row=2, column=0, sticky="nsew", pady=10)

        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Link", text="Link")
        self.tree.heading("LinkText", text="Texto enlace")

        main.rowconfigure(2, weight=1)
        main.columnconfigure(0, weight=1)

        self.refresh_table()

    def select_image(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if ruta:
            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, ruta)

    def probar_enlace(self):
        url = self.entry_link.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "No hay URL para probar.")
            return
        if url.startswith(("http://", "https://")):
            webbrowser.open_new_tab(url)
        else:
            messagebox.showerror("Error", "El enlace debe ser una URL válida.")

    def clear_fields(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_imagen.delete(0, tk.END)
        self.text_bio.delete("1.0", tk.END)
        self.entry_link.delete(0, tk.END)
        self.entry_link_text.delete(0, tk.END)

    def add_item(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Aviso", "El nombre es obligatorio.")
            return

        investigador = {
            "nombre": nombre,
            "imagen": self.entry_imagen.get().strip(),
            "bio": self.text_bio.get("1.0", tk.END).strip(),
            "link": self.entry_link.get().strip(),
            "link_text": self.entry_link_text.get().strip()
        }

        self.controller.state["quienes_somos"]["investigadores"].append(investigador)
        self.refresh_table()
        self.clear_fields()

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])

        lista = self.controller.state["quienes_somos"]["investigadores"]
        if 0 <= index < len(lista):
            if messagebox.askyesno("Confirmar", "¿Eliminar este investigador?"):
                del lista[index]
                self.refresh_table()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])

        lista = self.controller.state["quienes_somos"]["investigadores"]
        if 0 <= index < len(lista):
            item = lista[index]

            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, item.get("nombre", ""))

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, item.get("imagen", ""))

            self.text_bio.delete("1.0", tk.END)
            self.text_bio.insert("1.0", item.get("bio", ""))

            self.entry_link.delete(0, tk.END)
            self.entry_link.insert(0, item.get("link", ""))

            self.entry_link_text.delete(0, tk.END)
            self.entry_link_text.insert(0, item.get("link_text", ""))

            del lista[index]
            self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        lista = self.controller.state["quienes_somos"]["investigadores"]

        if index > 0:
            lista[index - 1], lista[index] = lista[index], lista[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        lista = self.controller.state["quienes_somos"]["investigadores"]

        if index < len(lista) - 1:
            lista[index + 1], lista[index] = lista[index], lista[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for inv in self.controller.state["quienes_somos"]["investigadores"]:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    inv.get("nombre", ""),
                    inv.get("imagen", ""),
                    inv.get("link", ""),
                    inv.get("link_text", "")
                )
            )


# ============================================================
#   PESTAÑA 4 — COLABORADORES
# ============================================================
class ColaboradoresTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        form = ttk.Frame(main)
        form.grid(row=0, column=0, sticky="nsew")

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_nombre = ttk.Entry(form)
        self.entry_nombre.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Imagen (ruta):").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_imagen = ttk.Entry(form)
        self.entry_imagen.grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Button(form, text="Seleccionar", command=self.select_image).grid(row=1, column=2, padx=5)

        ttk.Label(form, text="Bio:").grid(row=2, column=0, sticky="nw", pady=4)
        self.text_bio = tk.Text(form, height=6, wrap="word")
        self.text_bio.grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)

        ttk.Label(form, text="Link:").grid(row=3, column=0, sticky="w", pady=4)
        self.entry_link = ttk.Entry(form)
        self.entry_link.grid(row=3, column=1, sticky="ew", pady=4)
        ttk.Button(form, text="Probar enlace", command=self.probar_enlace).grid(row=3, column=2, padx=5)

        ttk.Label(form, text="Texto del enlace:").grid(row=4, column=0, sticky="w", pady=4)
        self.entry_link_text = ttk.Entry(form)
        self.entry_link_text.grid(row=4, column=1, sticky="ew", pady=4)

        form.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=1, column=0, sticky="w", pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        self.tree = ttk.Treeview(
            main,
            columns=("Nombre", "Imagen", "Link", "LinkText"),
            show="headings",
            height=10
        )
        self.tree.grid(row=2, column=0, sticky="nsew", pady=10)

        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Link", text="Link")
        self.tree.heading("LinkText", text="Texto enlace")

        main.rowconfigure(2, weight=1)
        main.columnconfigure(0, weight=1)

        self.refresh_table()

    def select_image(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if ruta:
            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, ruta)

    def probar_enlace(self):
        url = self.entry_link.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "No hay URL para probar.")
            return
        if url.startswith(("http://", "https://")):
            webbrowser.open_new_tab(url)
        else:
            messagebox.showerror("Error", "El enlace debe ser una URL válida.")

    def clear_fields(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_imagen.delete(0, tk.END)
        self.text_bio.delete("1.0", tk.END)
        self.entry_link.delete(0, tk.END)
        self.entry_link_text.delete(0, tk.END)

    def add_item(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Aviso", "El nombre es obligatorio.")
            return

        colab = {
            "nombre": nombre,
            "imagen": self.entry_imagen.get().strip(),
            "bio": self.text_bio.get("1.0", tk.END).strip(),
            "link": self.entry_link.get().strip(),
            "link_text": self.entry_link_text.get().strip()
        }

        self.controller.state["quienes_somos"]["colaboradores"].append(colab)
        self.refresh_table()
        self.clear_fields()

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])

        lista = self.controller.state["quienes_somos"]["colaboradores"]
        if 0 <= index < len(lista):
            if messagebox.askyesno("Confirmar", "¿Eliminar este colaborador?"):
                del lista[index]
                self.refresh_table()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])

        lista = self.controller.state["quienes_somos"]["colaboradores"]
        if 0 <= index < len(lista):
            item = lista[index]

            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, item.get("nombre", ""))

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, item.get("imagen", ""))

            self.text_bio.delete("1.0", tk.END)
            self.text_bio.insert(0.0, item.get("bio", ""))

            self.entry_link.delete(0, tk.END)
            self.entry_link.insert(0, item.get("link", ""))

            self.entry_link_text.delete(0, tk.END)
            self.entry_link_text.insert(0, item.get("link_text", ""))

            del lista[index]
            self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        lista = self.controller.state["quienes_somos"]["colaboradores"]

        if index > 0:
            lista[index - 1], lista[index] = lista[index], lista[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        lista = self.controller.state["quienes_somos"]["colaboradores"]

        if index < len(lista) - 1:
            lista[index + 1], lista[index] = lista[index], lista[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for colab in self.controller.state["quienes_somos"]["colaboradores"]:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    colab.get("nombre", ""),
                    colab.get("imagen", ""),
                    colab.get("link", ""),
                    colab.get("link_text", "")
                )
            )


# ============================================================
#   PESTAÑA 5 — PREVIEW Y GENERAR
# ============================================================
class PreviewTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=16, pady=10)

        ttk.Button(toolbar, text="Actualizar JSON", command=self.update_json_preview).pack(side="left")
        ttk.Button(toolbar, text="Guardar JSON", command=self.save_json).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Previsualizar en web", command=self.preview_web).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Generar archivo HTML", command=self.generate_html).pack(side="right", padx=8)

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

        self.update_json_preview()

    def sync_state(self):
        self.controller.tab_secciones.save()
        # Investigadores y colaboradores ya trabajan directo sobre state

    def update_json_preview(self):
        self.sync_state()
        datos = {
            "quienes_somos": self.controller.state.get("quienes_somos", {})
        }
        preview = json.dumps(datos, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    def save_json(self):
        self.sync_state()
        datos = {
            "quienes_somos": self.controller.state.get("quienes_somos", {})
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
        self.sync_state()
        qs = self.controller.state.get("quienes_somos", {})

        descripcion = qs.get("descripcion", "")
        imagen_principal = qs.get("imagen_principal", "")
        secciones = qs.get("secciones", [{}])[0]

        investigadores = qs.get("investigadores", [])
        colaboradores = qs.get("colaboradores", [])

        secciones_html = '<div class="marco2">\n'
        for i in range(1, 6):
            p = secciones.get(f"pregunta{i}", "")
            r = secciones.get(f"respuesta{i}", "")
            if p or r:
                secciones_html += f'  <p class="texto-justificado">{p} {r}</p>\n'
        secciones_html += "</div>\n"

        investigadores_html = """
  <hr style="height: 4px; background: #ccc; margin: 16px 0;">
  <div class="marco2"><h3><strong>Investigadores</strong></h3></div>
  <br><br>
    """
        for inv in investigadores:
            investigadores_html += f"""
  <div class="container my-4">
    <div class="row align-items-center">
      <div class="col-md-4 text-center imagenizq-texto">
        <a href="{inv.get('link','')}"><img src="{inv.get('imagen','')}" style="width:300px"></a>
      </div>
      <div class="col-md-8">
        <p><a style="color:#003366; font-weight:700; text-decoration:none;" href="{inv.get('link','')}"><h4>{inv.get('nombre','')}</h4></a></p>
        <p>{inv.get('bio','')}</p>
        <p><a style="color: #003366;" href="{inv.get('link','')}">{inv.get('link_text','')}</a></p>
      </div>
    </div>
  </div>
    """

        colaboradores_html = """
  <hr>
  <div class="marco2"><h3><strong>Colaboradores</strong></h3></div>
    """
        for colab in colaboradores:
            colaboradores_html += f"""
  <div class="container my-4">
    <div class="row align-items-center">
      <div class="col-md-4 text-center imagenizq-texto">
        <a href="{colab.get('link','')}"><img src="{colab.get('imagen','')}" style="width:300px"></a>
      </div>
      <div class="col-md-8">
        <p><a style="color:#003366; font-weight:700; text-decoration:none;" href="{colab.get('link','')}"><h4>{colab.get('nombre','')}</h4></a></p>
        <p>{colab.get('bio','')}</p>
        <p><a style="color: #003366;" href="{colab.get('link','')}">{colab.get('link_text','')}</a></p>
      </div>
    </div>
  </div>
    """

            html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>¿Quiénes somos?</title>
    </head>
    <body>
    <br>
    <div class="marco2">
    <h3>{descripcion}</h3>
    </div>

    <br>
    <div class="text-center">
    <img src="{imagen_principal}" width="350" height="350">
    </div>

    {secciones_html}

    <div class="mx-3">
    {investigadores_html}
    {colaboradores_html}
    </div>
    </body>
    </html>
    """

        temp_html = "geoso2-web-template/data/quienes_somos_preview.html"
        os.makedirs("geoso2-web-template/data", exist_ok=True)
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open_new_tab(f"file:///{os.path.abspath(temp_html)}")

    def generate_html(self):
        self.sync_state()
        qs = self.controller.state.get("quienes_somos", {})

        try:
            env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
            template = env.get_template("quienes-somos.html")
            html_output = template.render(quienes_somos=qs)

            output_dir = "geoso2-web-template/output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "quienes-somos.html")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_output)

            messagebox.showinfo("Éxito", f"Archivo HTML generado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el archivo HTML:\n{e}")


# ============================================================
#   CLASE PRINCIPAL — EDITORWINDOW
# ============================================================
class EditorWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor - Quiénes Somos")
        self.geometry("1100x700")

        self.state = {
            "quienes_somos": {
                "descripcion": "",
                "imagen_principal": "",
                "secciones": [
                    {
                        "pregunta1": "",
                        "respuesta1": "",
                        "pregunta2": "",
                        "respuesta2": "",
                        "pregunta3": "",
                        "respuesta3": "",
                        "pregunta4": "",
                        "respuesta4": "",
                        "pregunta5": "",
                        "respuesta5": ""
                    }
                ],
                "investigadores": [],
                "colaboradores": []
            }
        }

        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                if "quienes_somos" in datos:
                    self.state["quienes_somos"] = datos["quienes_somos"]
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_secciones = SeccionesTab(self.notebook, self)
        self.tab_investigadores = InvestigadoresTab(self.notebook, self)
        self.tab_colaboradores = ColaboradoresTab(self.notebook, self)
        self.tab_preview = PreviewTab(self.notebook, self)

        self.notebook.add(self.tab_secciones, text="Secciones")
        self.notebook.add(self.tab_investigadores, text="Investigadores")
        self.notebook.add(self.tab_colaboradores, text="Colaboradores")
        self.notebook.add(self.tab_preview, text="Preview y Generar")
