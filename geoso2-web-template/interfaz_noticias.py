import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from PIL import Image
import copy
import webbrowser


class NoticiasWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Noticias")
        self.geometry("980x640")

        # Estado
        self.state = {
            "noticias": []
        }

        # Carpeta correcta
        os.makedirs("geoso2-web-template/imput/img/noticias", exist_ok=True)

        # Cargar JSON si estamos editando
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                if isinstance(datos, dict) and "noticias" in datos:
                    self.state["noticias"] = datos["noticias"]
                elif isinstance(datos, list):
                    self.state["noticias"] = datos
                else:
                    self.state["noticias"] = []

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        # Solo una pestaña: Datos
        self.tab_datos = DatosTab(self, self)
        self.tab_datos.pack(fill="both", expand=True)

        # Si estamos editando, refrescar tabla
        if mode == "edit":
            self.tab_datos.refresh_table()


class DatosTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.editing_index = None

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_imagen).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Título:").grid(row=1, column=0, sticky="w")
        self.entry_titulo = ttk.Entry(frm)
        self.entry_titulo.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Descripción:").grid(row=2, column=0, sticky="nw")
        self.text_descripcion = tk.Text(frm, height=5)
        self.text_descripcion.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Texto del enlace:").grid(row=3, column=0, sticky="w", pady=6)
        self.entry_enlace_texto = ttk.Entry(frm)
        self.entry_enlace_texto.grid(row=3, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="URL del enlace (URL o HTML):").grid(row=4, column=0, sticky="w", pady=6)
        self.entry_enlace_url = ttk.Entry(frm)
        self.entry_enlace_url.grid(row=4, column=1, sticky="ew", pady=6)

        btn_enlace_frame = ttk.Frame(frm)
        btn_enlace_frame.grid(row=5, column=1, sticky="ew", padx=8)

        ttk.Button(btn_enlace_frame, text="Buscar archivo", command=self.select_file).pack(side="left", padx=4)
        ttk.Button(btn_enlace_frame, text="Probar enlace", command=lambda: webbrowser.open_new_tab(self.entry_enlace_url.get().strip())).pack(side="left", padx=4)

        self.var_link_titulo = tk.BooleanVar(value=True)
        self.var_link_portada = tk.BooleanVar(value=True)

        checkbox_frame = ttk.Frame(frm)
        checkbox_frame.grid(row=6, column=1, sticky="w", pady=4)

        ttk.Checkbutton(checkbox_frame, text="Usar enlace en título",
                        variable=self.var_link_titulo).pack(side="left", padx=(0, 20))

        ttk.Checkbutton(checkbox_frame, text="Usar enlace en portada",
                        variable=self.var_link_portada).pack(side="left")

        # Botones principales
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)

        # Tabla
        self.tree = ttk.Treeview(frm, columns=("Imagen", "Título"), show="headings", height=12)
        self.tree.grid(row=8, column=0, columnspan=3, sticky="nsew")

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(8, weight=1)

        ttk.Button(frm, text="Guardar cambios", command=self.save_json).grid(row=9, column=1, sticky="s", pady=10)

    def select_file(self):
        ruta = filedialog.askopenfilename(
            initialdir="geoso2-web-template/output",
            title="Seleccionar archivo",
            filetypes=[
                ("Documentos", "*.pdf *.html *.htm"),
                ("PDF", "*.pdf"),
                ("HTML", "*.html *.htm"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not ruta:
            return

        try:
            nombre = os.path.basename(ruta)
            extension = nombre.lower().split(".")[-1]

            if extension == "pdf":
                destino_dir = "geoso2-web-template/imput/docs/noticias"
                os.makedirs(destino_dir, exist_ok=True)

                destino = os.path.join(destino_dir, nombre)

                with open(ruta, "rb") as f_src:
                    with open(destino, "wb") as f_dst:
                        f_dst.write(f_src.read())

                ruta_relativa = f"../imput/docs/noticias/{nombre}"

            else:
                ruta_relativa = nombre

            self.entry_enlace_url.delete(0, tk.END)
            self.entry_enlace_url.insert(0, ruta_relativa)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el archivo:\n{e}")

    def select_imagen(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")])
        if not ruta:
            return
        try:
            nombre = os.path.basename(ruta)
            destino = os.path.join("geoso2-web-template/imput/img/noticias", nombre)

            with Image.open(ruta) as img:
                img = img.convert("RGB")
                img.save(destino)

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, destino)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def add_item(self):
        imagen = self.entry_imagen.get().strip()
        titulo = self.entry_titulo.get().strip()
        descripcion = self.text_descripcion.get("1.0", tk.END).strip()
        enlace_texto = self.entry_enlace_texto.get().strip()
        enlace_url = self.entry_enlace_url.get().strip()
        usar_en_titulo = self.var_link_titulo.get()
        usar_en_portada = self.var_link_portada.get()

        if not imagen or not titulo or not descripcion:
            messagebox.showwarning("Aviso", "Imagen, título y descripción son obligatorios.")
            return

        nuevo = {
            "imagen": imagen,
            "titulo": titulo,
            "descripcion": descripcion,
            "enlace": {
                "texto": enlace_texto,
                "url": enlace_url,
                "usar_en_titulo": usar_en_titulo,
                "usar_en_portada": usar_en_portada
            }
        }

        if self.editing_index is not None:
            self.controller.state["noticias"][self.editing_index] = nuevo
            self.editing_index = None
        else:
            self.controller.state["noticias"].append(nuevo)

        self.refresh_table()
        self.clear_fields()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecciona una noticia para editar.")
            return

        index = self.tree.index(selected[0])
        noticia = self.controller.state["noticias"][index]
        self.editing_index = index

        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, noticia["imagen"])

        self.entry_titulo.delete(0, tk.END)
        self.entry_titulo.insert(0, noticia["titulo"])

        self.text_descripcion.delete("1.0", tk.END)
        self.text_descripcion.insert("1.0", noticia["descripcion"])

        enlace = noticia.get("enlace", {})

        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_texto.insert(0, enlace.get("texto", ""))

        self.entry_enlace_url.delete(0, tk.END)
        self.entry_enlace_url.insert(0, enlace.get("url", ""))

        self.var_link_titulo.set(enlace.get("usar_en_titulo", True))
        self.var_link_portada.set(enlace.get("usar_en_portada", True))

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state["noticias"][index]
        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for elem in self.controller.state["noticias"]:
            self.tree.insert("", tk.END, values=(elem["imagen"], elem["titulo"]))

    def save_json(self):
        datos = self.controller.state.copy()

        # Ruta fija
        ruta = "geoso2-web-template/json/noticias.json"

        # Asegurar que la carpeta existe
        os.makedirs(os.path.dirname(ruta), exist_ok=True)

        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", f"Archivo JSON guardado en:\n{ruta}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

