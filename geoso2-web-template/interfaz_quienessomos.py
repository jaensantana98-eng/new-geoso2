import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
import webbrowser


# ============================================================
#   PESTAÑA 2 — INVESTIGADORES
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

    def select_file(self):
        descargas = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.isdir(descargas):
            descargas = os.path.expanduser("~")

        ruta = filedialog.askopenfilename(
            initialdir=descargas,
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
            destino_dir = "geoso2-web-template/imput/docs/quienes-somos"
            os.makedirs(destino_dir, exist_ok=True)

            nombre = os.path.basename(ruta)
            destino = os.path.join(destino_dir, nombre)

            with open(ruta, "rb") as f_src:
                with open(destino, "wb") as f_dst:
                    f_dst.write(f_src.read())

            ruta_relativa = f"../imput/docs/quienes-somos/{nombre}"
            self.entry_link.delete(0, tk.END)
            self.entry_link.insert(0, ruta_relativa)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar el archivo:\n{e}")

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
#   PESTAÑA 3 — COLABORADORES
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
#   CLASE PRINCIPAL — EDITORWINDOW
# ============================================================
class EditorWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor - Quiénes Somos")
        self.geometry("1100x700")

        # Estado inicial
        self.state = {
            "quienes_somos": {
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

        # Cargar JSON si estamos en modo edición
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    qs = datos.get("web", {}).get("quienes_somos", {})

                    self.state["quienes_somos"]["secciones"] = qs.get("secciones", [])
                    self.state["quienes_somos"]["investigadores"] = qs.get("investigadores", [])
                    self.state["quienes_somos"]["colaboradores"] = qs.get("colaboradores", [])

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Pestañas
        self.tab_investigadores = InvestigadoresTab(self.notebook, self)
        self.tab_colaboradores = ColaboradoresTab(self.notebook, self)

        self.notebook.add(self.tab_investigadores, text="Investigadores")
        self.notebook.add(self.tab_colaboradores, text="Colaboradores")

        # Botón guardar cambios
        ttk.Button(self, text="Guardar cambios", command=self.save_json).pack(pady=10)

        # Refrescar tablas si venimos de edición
        self.tab_investigadores.refresh_table()
        self.tab_colaboradores.refresh_table()

    def save_json(self):
        ruta = "geoso2-web-template/json/web.json"

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos_completos = json.load(f)

            if "web" not in datos_completos:
                datos_completos["web"] = {}

            datos_completos["web"]["quienes_somos"] = self.state["quienes_somos"]

            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", "Datos de 'Quiénes Somos' actualizados correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

