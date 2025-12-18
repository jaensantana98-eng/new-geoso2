import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import datetime
import webbrowser
from PIL import Image

# -----------------------------
# Ventana del editor con pestañas
# -----------------------------
class EditorWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de JSON")
        self.geometry("980x640")

        # Estado del documento
        self.state = {
            "portada": "",
            "titulo": "", 
            "cuerpo": "",
            "enlace": {
                "texto": "",
                "url": "",
                "usar_en_titulo": True,
                "usar_en_portada": True
            },
            "fecha": "",     
        }

        # Asegurar carpeta de imágenes
        os.makedirs("data/img", exist_ok=True)

        # Si es edición, cargar datos desde JSON
        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                # Merge sin perder claves
                for k in self.state.keys():
                    if k in datos:
                        self.state[k] = datos[k]
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
# Pestaña: Datos
# -----------------------------
class DatosTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frm, text="Portada:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_portada = ttk.Entry(frm)
        self.entry_portada.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_portada).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Título del documento:").grid(row=2, column=0, sticky="w", pady=6)
        self.text_titulo = tk.Text(frm, wrap="word", height=2)
        self.text_titulo.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Cuerpo:").grid(row=4, column=0, sticky="nw", pady=6)
        cuerpo_frame = ttk.Frame(frm)
        cuerpo_frame.grid(row=4, column=1, sticky="nsew", pady=6)
        self.text_cuerpo = tk.Text(cuerpo_frame, wrap="word")
        self.text_cuerpo.pack(side="left", fill="both", expand=True)
        scroll_cuerpo = ttk.Scrollbar(cuerpo_frame, orient="vertical", command=self.text_cuerpo.yview)
        scroll_cuerpo.pack(side="right", fill="y")
        self.text_cuerpo.config(yscrollcommand=scroll_cuerpo.set)

        # Enlace
        ttk.Label(frm, text="Texto del enlace:").grid(row=5, column=0, sticky="w", pady=6)
        self.entry_enlace_texto = ttk.Entry(frm)
        self.entry_enlace_texto.grid(row=5, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="URL del enlace:").grid(row=6, column=0, sticky="w", pady=6)
        self.entry_enlace_url = ttk.Entry(frm)
        self.entry_enlace_url.grid(row=6, column=1, sticky="ew", pady=6)
        
        ttk.Button(
            frm,
            text="Probar enlace",
            command=self.probar_enlace
        ).grid(row=6, column=2, padx=8)

        # Checkbuttons para usar enlace en título/portada
        self.var_link_titulo = tk.BooleanVar(value=True)
        self.var_link_portada = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            frm,
            text="Usar este enlace en el título",
            variable=self.var_link_titulo,
            command=self.update_state
        ).grid(row=7, column=0, sticky="w", pady=(6, 0))

        ttk.Checkbutton(
            frm,
            text="Usar este enlace en la portada",
            variable=self.var_link_portada,
            command=self.update_state
        ).grid(row=7, column=1, sticky="w")

        frm.columnconfigure(1, weight=1)

        # Actualizar estado al escribir
        self.entry_portada.bind("<KeyRelease>", self.update_state)
        self.text_titulo.bind("<KeyRelease>", self.update_state)
        self.text_cuerpo.bind("<KeyRelease>", self.update_state)
        self.entry_enlace_texto.bind("<KeyRelease>", self.update_state)
        self.entry_enlace_url.bind("<KeyRelease>", self.update_state)

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
            self.controller.state["portada"] = destino

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo procesar la imagen de portada:\n{e}"
            )

    def probar_enlace(self):
        url = self.entry_enlace.get().strip()

        if not url:
            messagebox.showwarning("Aviso", "No hay ninguna URL para probar.")
            return

        try:
            # Si es un archivo HTML dentro del proyecto
            if url.endswith(".html"):
                # Si la ruta es relativa, convertirla a absoluta
                ruta_absoluta = os.path.abspath(url)
                if os.path.exists(ruta_absoluta):
                    webbrowser.open_new_tab(f"file:///{ruta_absoluta}")
                else:
                    messagebox.showerror("Error", f"No se encontró el archivo HTML:\n{ruta_absoluta}")
            # Si es un enlace web normal
            elif url.startswith(("http://", "https://")):
                webbrowser.open_new_tab(url)
            else:
                messagebox.showerror("Error", "El enlace debe ser una URL válida o un archivo .html del proyecto.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")




    def update_state(self, event=None):
        self.controller.state["titulo"] = self.text_titulo.get("1.0", tk.END).strip()
        self.controller.state["portada"] = self.entry_portada.get().strip()
        self.controller.state["cuerpo"] = self.text_cuerpo.get("1.0", tk.END).strip()
        self.controller.state["enlace"]["texto"] = self.entry_enlace_texto.get().strip()
        self.controller.state["enlace"]["url"] = self.entry_enlace_url.get().strip()
        self.controller.state["enlace"]["usar_en_titulo"] = self.var_link_titulo.get()
        self.controller.state["enlace"]["usar_en_portada"] = self.var_link_portada.get()

    def set_data(self, datos):

        self.entry_portada.delete(0, tk.END)
        self.entry_portada.insert(0, datos.get("portada", ""))

        self.text_titulo.delete("1.0", tk.END)
        self.text_titulo.insert("1.0", datos.get("titulo", ""))

        self.text_cuerpo.delete("1.0", tk.END)
        self.text_cuerpo.insert("1.0", datos.get("cuerpo", ""))

        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_texto.insert(0, datos.get("enlace", {}).get("texto", ""))

        self.entry_enlace_url.delete(0, tk.END)
        self.entry_enlace_url.insert(0, datos.get("enlace", {}).get("url", ""))

        enlace = datos.get("enlace", {})

        self.var_link_titulo.set(enlace.get("usar_en_titulo", True))
        self.var_link_portada.set(enlace.get("usar_en_portada", True))



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

        info = ttk.Label(toolbar, text="Revisa el JSON antes de guardar.")
        info.pack(side="left", padx=16)

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    def update_preview(self):
        datos = self.controller.state.copy()
        datos["fecha"] = datetime.datetime.now().strftime("%d-%m-%Y")


        # Opcional: eliminar claves vacías para el preview más limpio
        compact = {k: v for k, v in datos.items() if v not in ("", [], None)}
        preview = json.dumps(compact, indent=4, ensure_ascii=False)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, preview)

    def save_json(self):
        datos = self.controller.state.copy()
        datos["fecha"] = datetime.datetime.now().strftime("%d-%m-%Y")
        ruta = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], initialdir="data")
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Guardado", f"Archivo JSON guardado en {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")
