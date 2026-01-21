import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
import webbrowser
from PIL import Image


class EditorProyectosWindow(tk.Toplevel):
    def __init__(self, filepath=None):
        super().__init__()
        self.title("Editor de Proyectos")
        self.geometry("1100x700")

        self.filepath = filepath
        self.editing_index = None

        # Estado inicial
        self.state = {
            "proyectos": {
                "encurso": [],
                "anteriores": [],
                "trabajosacademicos": []
            }
        }

        if filepath and os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                datos = json.load(f)

            # Cargar proyectos desde la ruta correcta
            self.state["proyectos"] = datos.get("web", {}) \
                                        .get("proyectos", {
                                            "encurso": [],
                                            "anteriores": [],
                                            "trabajosacademicos": []
                                        })


        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_lista = ListaTab(self.notebook, self)
        self.tab_form = FormTab(self.notebook, self)

        self.notebook.add(self.tab_lista, text="Lista")
        self.notebook.add(self.tab_form, text="Formulario")

        save_frame = ttk.Frame(self)
        save_frame.pack(fill="x", pady=15)
        ttk.Button(save_frame, text="Guardar cambios", command=self.save_json).pack(anchor="center")

        self.tab_lista.refresh_table()

    # Guardar JSON automáticamente
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

            # Guardar proyectos en la ruta correcta
            datos_completos["web"]["index_page"]["proyectos"] = self.state["proyectos"]

            # Guardar JSON completo
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", f"Archivo JSON actualizado:\n{ruta}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")



class ListaTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Categoría:").pack(anchor="w", padx=10, pady=5)

        self.categoria_var = tk.StringVar(value="encurso")
        self.combo = ttk.Combobox(
            self,
            textvariable=self.categoria_var,
            values=["encurso", "anteriores", "trabajosacademicos"],
            state="readonly"
        )
        self.combo.pack(anchor="w", padx=10)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=10)

        ttk.Button(toolbar, text="Añadir", command=self.add).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Editar", command=self.edit).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Eliminar", command=self.delete).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Subir", command=self.up).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Bajar", command=self.down).pack(side="left", padx=5)

        self.tree = ttk.Treeview(
            self,
            columns=("Imagen", "Título", "Link"),
            show="headings",
            height=20
        )
        self.tree.pack(fill="both", expand=True)

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Link", text="Link")

    def refresh_table(self):
        categoria = self.categoria_var.get()
        proyectos = self.controller.state["proyectos"][categoria]

        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in proyectos:
            self.tree.insert(
                "",
                tk.END,
                values=(p.get("imagen", ""), p.get("titulo", ""), p.get("link", ""))
            )

    def add(self):
        self.controller.editing_index = None
        categoria = self.categoria_var.get()
        self.controller.tab_form.load_data({}, categoria)
        self.controller.notebook.select(self.controller.tab_form)

    def edit(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        categoria = self.categoria_var.get()
        self.controller.editing_index = index

        data = self.controller.state["proyectos"][categoria][index]
        self.controller.tab_form.load_data(data, categoria)
        self.controller.notebook.select(self.controller.tab_form)

    def delete(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        categoria = self.categoria_var.get()

        del self.controller.state["proyectos"][categoria][index]
        self.refresh_table()

    def up(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        categoria = self.categoria_var.get()
        arr = self.controller.state["proyectos"][categoria]

        if index == 0:
            return

        arr[index - 1], arr[index] = arr[index], arr[index - 1]
        self.refresh_table()

    def down(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        categoria = self.categoria_var.get()
        arr = self.controller.state["proyectos"][categoria]

        if index == len(arr) - 1:
            return

        arr[index + 1], arr[index] = arr[index], arr[index + 1]
        self.refresh_table()


class FormTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.categoria_actual = None

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w")
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew")
        ttk.Button(frm, text="Seleccionar", command=self.select_image).grid(row=0, column=2, padx=5)

        ttk.Label(frm, text="Título:").grid(row=1, column=0, sticky="nw")
        self.text_titulo = tk.Text(frm, height=3)
        self.text_titulo.grid(row=1, column=1, sticky="ew")

        ttk.Label(frm, text="Link:").grid(row=2, column=0, sticky="w")

        link_frame = ttk.Frame(frm)
        link_frame.grid(row=2, column=1, sticky="ew")

        self.entry_link = ttk.Entry(link_frame)
        self.entry_link.pack(side="left", fill="x", expand=True)

        ttk.Button(link_frame, text="Probar", command=self.probar_link).pack(side="left", padx=5)
        ttk.Button(frm, text="Buscar archivo", command=self.select_file).grid(row=2, column=2, padx=8)

        ttk.Label(frm, text="Descripción:").grid(row=3, column=0, sticky="nw")
        self.text_desc = tk.Text(frm, height=8)
        self.text_desc.grid(row=3, column=1, sticky="ew")

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=3, pady=20)

        ttk.Button(btns, text="Guardar", command=self.save).pack(side="left", padx=10)
        ttk.Button(btns, text="Cancelar", command=self.cancel).pack(side="left", padx=10)

        frm.columnconfigure(1, weight=1)

    def select_file(self):
        ruta = filedialog.askopenfilename(
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
            destino_dir = "geoso2-web-template/imput/docs/proyectos"
            os.makedirs(destino_dir, exist_ok=True)

            nombre = os.path.basename(ruta)
            destino = os.path.join(destino_dir, nombre)

            with open(ruta, "rb") as f_src, open(destino, "wb") as f_dst:
                f_dst.write(f_src.read())

            self.entry_link.delete(0, tk.END)
            self.entry_link.insert(0, f"../imput/docs/proyectos/{nombre}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar el archivo:\n{e}")

    def load_data(self, data, categoria):
        self.categoria_actual = categoria

        self.entry_imagen.delete(0, tk.END)
        self.text_titulo.delete("1.0", tk.END)
        self.entry_link.delete(0, tk.END)
        self.text_desc.delete("1.0", tk.END)

        self.entry_imagen.insert(0, data.get("imagen", ""))
        self.text_titulo.insert("1.0", data.get("titulo", ""))
        self.entry_link.insert(0, data.get("link", ""))
        self.text_desc.insert("1.0", data.get("descripcion", ""))

    def select_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if not ruta:
            return

        try:
            nombre = os.path.basename(ruta)
            destino_dir = "geoso2-web-template/imput/img/proyectos"
            os.makedirs(destino_dir, exist_ok=True)

            destino = os.path.join(destino_dir, nombre)

            # Miniatura 300x300
            with Image.open(ruta) as img:
                img = img.convert("RGB")
                img.thumbnail((300, 300), Image.LANCZOS)

                canvas = Image.new("RGB", (300, 300), "white")
                x = (300 - img.width) // 2
                y = (300 - img.height) // 2
                canvas.paste(img, (x, y))
                canvas.save(destino, quality=90)

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, f"../imput/img/proyectos/{nombre}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def probar_link(self):
        url = self.entry_link.get().strip()

        if not url:
            messagebox.showwarning("Aviso", "No hay ningún enlace para probar.")
            return

        try:
            if url.startswith(("http://", "https://")):
                webbrowser.open_new_tab(url)
            else:
                ruta = os.path.abspath(url)
                if os.path.exists(ruta):
                    webbrowser.open_new_tab(f"file:///{ruta}")
                else:
                    messagebox.showerror("Error", f"No se encontró el archivo:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")

    def save(self):
        data = {
            "imagen": self.entry_imagen.get().strip(),
            "titulo": self.text_titulo.get("1.0", tk.END).strip(),
            "link": self.entry_link.get().strip(),
            "descripcion": self.text_desc.get("1.0", tk.END).strip()
        }

        categoria = self.categoria_actual or self.controller.tab_lista.categoria_var.get()

        if self.controller.editing_index is None:
            self.controller.state["proyectos"][categoria].append(data)
        else:
            self.controller.state["proyectos"][categoria][self.controller.editing_index] = data
            self.controller.editing_index = None

        self.controller.tab_lista.refresh_table()
        self.controller.notebook.select(self.controller.tab_lista)

    def cancel(self):
        self.controller.notebook.select(self.controller.tab_lista)
