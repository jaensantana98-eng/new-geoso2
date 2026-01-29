import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
import webbrowser
from PIL import Image


# ============================================================
# VENTANA PRINCIPAL DEL EDITOR DE RÁFAGAS
# ============================================================
class EditorRafagasWindow(tk.Toplevel):
    def __init__(self, filepath=None):
        super().__init__()
        self.title("Editor de Ráfagas")
        self.geometry("1100x700")

        self.state = {"rafagas": []}
        self.filepath = filepath
        self.editing_index = None

        # Cargar JSON si existe
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                # Cargar ráfagas desde la ruta correcta
                self.state["rafagas"] = datos.get("web", {}).get("pagina1", {}).get("rafagas", [])
                self.contenido_original = json.loads(json.dumps(self.state["rafagas"]))


            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        # Notebook sin preview
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_lista = ListaTab(self.notebook, self)
        self.tab_form = FormTab(self.notebook, self)

        self.notebook.add(self.tab_lista, text="Lista")
        self.notebook.add(self.tab_form, text="Formulario")

        # Marco inferior para botones
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", pady=10)

        # Botón de instrucciones (abajo a la izquierda)
        ttk.Button(bottom_frame, text="Instrucciones", command=self.tab_lista.instrucciones).pack(side="left", padx=10)

        # Botón guardar cambios (centrado)
        ttk.Button(bottom_frame, text="Guardar cambios", command=self.save_json).pack(side="top", pady=5)


        self.tab_lista.refresh_table()

    def detectar_cambios(self, antes, despues):
        cambios = []
        if antes != despues:
            cambios.append("rafagas")
        return cambios


    # Guardar JSON automáticamente
    def save_json(self):
        ruta = "geoso2-web-template/json/web.json"

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos_completos = json.load(f)

            datos_completos.setdefault("web", {})
            datos_completos["web"].setdefault("pagina1", {})

            # Detectar cambios
            cambios = self.detectar_cambios(self.contenido_original, self.state["rafagas"])

            # Registrar historial
            if cambios:
                datos_completos["web"]["pagina1"].setdefault("history", [])
                datos_completos["web"]["pagina1"]["history"].append({
                    "timestamp": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                    "sections_changed": cambios,
                    "summary": "Actualización en ráfagas"
                })

            # Guardar ráfagas
            datos_completos["web"]["pagina1"]["rafagas"] = self.state["rafagas"]

            # Guardar archivo
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", f"Archivo JSON actualizado:\n{ruta}")

            # Actualizar contenido original
            self.contenido_original = json.loads(json.dumps(self.state["rafagas"]))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")



# ============================================================
# TABLA DE RÁFAGAS
# ============================================================
class ListaTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

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
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in self.controller.state["rafagas"]:
            self.tree.insert(
                "",
                tk.END,
                values=(r.get("imagen", ""), r.get("titulo", ""), r.get("link", ""))
            )

    def add(self):
        self.controller.editing_index = None
        self.controller.tab_form.load_data({})
        self.controller.notebook.select(self.controller.tab_form)

    def edit(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        self.controller.editing_index = index
        data = self.controller.state["rafagas"][index]

        self.controller.tab_form.load_data(data)
        self.controller.notebook.select(self.controller.tab_form)

    def delete(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state["rafagas"][index]
        self.refresh_table()

    def up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index == 0:
            return
        arr = self.controller.state["rafagas"]
        arr[index - 1], arr[index] = arr[index], arr[index - 1]
        self.refresh_table()

    def down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.controller.state["rafagas"]
        if index == len(arr) - 1:
            return
        arr[index + 1], arr[index] = arr[index], arr[index + 1]
        self.refresh_table()

    def instrucciones(self):
        instrucciones = (
            "Instrucciones para editar las Ráfagas:\n\n"
            "1. Imagen: Selecciona una imagen representativa para la ráfaga. "
            "La imagen se redimensionará automáticamente a 300x300 píxeles.\n\n"
            "2. Título: Escribe un título breve y descriptivo para la ráfaga.\n\n"
            "3. Descripción: Proporciona una descripción detallada de la ráfaga. "
            "Puedes incluir información relevante que quieras destacar.\n\n"
            "4. Link: Introduce un enlace relacionado con la ráfaga. "
            "Puedes seleccionar un archivo local o introducir una URL externa.\n\n"
            "5. Guardar: Una vez completados los campos, haz clic en 'Guardar' "
            "para añadir o actualizar la ráfaga en la lista.\n\n"
            "6. Cancelar: Si deseas descartar los cambios, haz clic en 'Cancelar'."
        )
        messagebox.showinfo("Instrucciones", instrucciones)

# ============================================================
# FORMULARIO DE EDICIÓN
# ============================================================
class FormTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # Imagen
        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w")
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew")
        ttk.Button(frm, text="Seleccionar", command=self.select_imagen).grid(row=0, column=2, padx=5)

        # Título
        ttk.Label(frm, text="Título:").grid(row=1, column=0, sticky="nw")
        self.text_titulo = tk.Text(frm, height=3)
        self.text_titulo.grid(row=1, column=1, sticky="ew")

        # Descripción
        ttk.Label(frm, text="Descripción:").grid(row=2, column=0, sticky="nw")
        self.text_desc = tk.Text(frm, height=8)
        self.text_desc.grid(row=2, column=1, sticky="ew")

        # Link
        ttk.Label(frm, text="Link:").grid(row=3, column=0, sticky="w")

        link_frame = ttk.Frame(frm)
        link_frame.grid(row=3, column=1, sticky="ew")

        self.entry_link = ttk.Entry(link_frame)
        self.entry_link.pack(side="left", fill="x", expand=True)

        ttk.Button(link_frame, text="Probar", command=self.probar_link).pack(side="left", padx=5)
        ttk.Button(frm, text="Buscar archivo", command=self.select_file).grid(row=3, column=2, padx=8)

        # Botones
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
            destino_dir = "geoso2-web-template/imput/docs/rafagas"
            os.makedirs(destino_dir, exist_ok=True)

            nombre = os.path.basename(ruta)
            destino = os.path.join(destino_dir, nombre)

            with open(ruta, "rb") as f_src, open(destino, "wb") as f_dst:
                f_dst.write(f_src.read())

            self.entry_link.delete(0, tk.END)
            self.entry_link.insert(0, f"../imput/docs/rafagas/{nombre}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar el archivo:\n{e}")

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

    def load_data(self, data):
        self.entry_imagen.delete(0, tk.END)
        self.text_titulo.delete("1.0", tk.END)
        self.text_desc.delete("1.0", tk.END)
        self.entry_link.delete(0, tk.END)

        self.entry_imagen.insert(0, data.get("imagen", ""))
        self.text_titulo.insert("1.0", data.get("titulo", ""))
        self.text_desc.insert("1.0", data.get("descripcion", ""))
        self.entry_link.insert(0, data.get("link", ""))

    def select_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if not ruta:
            return

        try:
            nombre = os.path.basename(ruta)
            destino_dir = "geoso2-web-template/imput/img/rafagas"
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
            self.entry_imagen.insert(0, f"../imput/img/rafagas/{nombre}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def save(self):
        data = {
            "imagen": self.entry_imagen.get().strip(),
            "titulo": self.text_titulo.get("1.0", tk.END).strip(),
            "descripcion": self.text_desc.get("1.0", tk.END).strip(),
            "link": self.entry_link.get().strip()
        }

        if self.controller.editing_index is None:
            self.controller.state["rafagas"].append(data)
        else:
            self.controller.state["rafagas"][self.controller.editing_index] = data
            self.controller.editing_index = None

        self.controller.tab_lista.refresh_table()
        self.controller.notebook.select(self.controller.tab_lista)

    def cancel(self):
        self.controller.notebook.select(self.controller.tab_lista)

