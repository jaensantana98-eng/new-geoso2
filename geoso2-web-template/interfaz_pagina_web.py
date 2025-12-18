import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import datetime
import webbrowser
from PIL import Image

class paginaWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Página Web")
        self.geometry("1050x950")

        # Estado inicial
        self.state = {
            "portada": "",
            "titulo": "",
            "cuerpo": [],   # lista de bloques texto+imagen+enlace
            "autor": "",
            "fecha": "",
        }

        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                self.state.update(datos)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Pestañas
        self.tab_datos = DatosTab(self.notebook, self)
        self.tab_cuerpo = CuerpoTab(self.notebook, self)
        self.tab_preview = PreviewTab(self.notebook, self)

        self.notebook.add(self.tab_datos, text="Datos")
        self.notebook.add(self.tab_cuerpo, text="Cuerpo")
        self.notebook.add(self.tab_preview, text="Preview y Guardar")

        if mode == "edit":
            self.tab_datos.refresh_fields()
            self.tab_cuerpo.refresh_table()
            self.tab_preview.update_preview()


class DatosTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frm, text="Portada:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_portada = ttk.Entry(frm)
        self.entry_portada.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_portada).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Titulo:").grid(row=2, column=0, sticky="w", pady=6)
        self.texto = tk.Text(frm, height=8, wrap="word")
        self.texto.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Autor:").grid(row=3, column=0, sticky="w", pady=6)
        self.entry_autor = ttk.Entry(frm)
        self.entry_autor.grid(row=3, column=1, sticky="ew", pady=6)

        frm.columnconfigure(1, weight=1)

    def refresh_fields(self):
        self.entry_portada.delete(0, tk.END)
        self.entry_portada.insert(0, self.controller.state.get("portada", ""))

        self.texto.delete("1.0", tk.END)
        self.texto.insert("1.0", self.controller.state.get("titulo", ""))

        self.entry_autor.delete(0, tk.END)
        self.entry_autor.insert(0, self.controller.state.get("autor", ""))

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

    def update_state(self):
        self.controller.state["portada"] = self.entry_portada.get().strip()
        self.controller.state["titulo"] = self.texto.get("1.0", tk.END).strip()
        self.controller.state["autor"] = self.entry_autor.get().strip()

class CuerpoTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        # Campos para añadir bloques
        ttk.Label(frm, text="Texto:").grid(row=0, column=0, sticky="w", pady=6)
        self.texto = tk.Text(frm, height=16, wrap="word")
        self.texto.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Enlace:").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_enlace = ttk.Entry(frm)
        self.entry_enlace.grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Probar enlace", command=self.probar_enlace).grid(row=1, column=2, padx=8)

        ttk.Label(frm, text="Texto del enlace:").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_texto_del_enlace = ttk.Entry(frm)
        self.entry_texto_del_enlace.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frm, text="Imagen:").grid(row=3, column=0, sticky="w", pady=6)
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=3, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_imagen).grid(row=3, column=2, padx=8)

        ttk.Label(frm, text="Pie de imagen:").grid(row=4, column=0, sticky="w", pady=6)
        self.texto_Pie_de_imagen = tk.Text(frm, height=6, wrap="word")
        self.texto_Pie_de_imagen.grid(row=4, column=1, sticky="ew", pady=6)

        # Botones de gestión
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Añadir", command=self.add_block).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_block).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_block).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        # Tabla para mostrar bloques añadidos
        self.tree = ttk.Treeview(frm, columns=("Texto", "Imagen", "Pie de imagen", "Enlace", "Texto del enlace"), show="headings", height=8)
        self.tree.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.tree.heading("Texto", text="Texto")
        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Pie de imagen", text="Pie de Imagen")
        self.tree.heading("Enlace", text="Enlace")
        self.tree.heading("Texto del enlace", text="Texto del Enlace")

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(5, weight=1)

    def add_block(self):
        bloque = {
            "texto": self.texto.get("1.0", tk.END).strip(),
            "imagen": self.entry_imagen.get().strip(),
            "Pie de imagen": self.texto_Pie_de_imagen.get("1.0", tk.END).strip(),
            "enlace": self.entry_enlace.get().strip(),
            "texto del enlace": self.entry_texto_del_enlace.get().strip()
        }
        if not bloque["texto"] and not bloque["imagen"]:
            messagebox.showwarning("Aviso", "Debes añadir al menos texto o imagen.")
            return
        self.controller.state["cuerpo"].append(bloque)
        self.refresh_table()

        # limpiar campos
        self.texto.delete("1.0", tk.END)
        self.entry_imagen.delete(0, tk.END)
        self.entry_enlace.delete(0, tk.END)
        self.entry_texto_del_enlace.delete(0, tk.END)
        self.texto_Pie_de_imagen.delete("1.0", tk.END)

    def delete_block(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state["cuerpo"][index]
        self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index > 0:
            arr = self.controller.state["cuerpo"]
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.controller.state["cuerpo"]
        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def edit_block(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        bloque = self.controller.state["cuerpo"][index]

        # Cargar datos en los campos
        self.texto.delete("1.0", tk.END)
        self.texto.insert("1.0", bloque["texto"])
        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, bloque["imagen"])
        self.texto_Pie_de_imagen.delete("1.0", tk.END)
        self.texto_Pie_de_imagen.insert("1.0", bloque["Pie de imagen"])
        self.entry_enlace.delete(0, tk.END)
        self.entry_enlace.insert(0, bloque["enlace"])
        self.entry_texto_del_enlace.delete(0, tk.END)
        self.entry_texto_del_enlace.insert(0, bloque["texto del enlace"])

        # Eliminar el bloque actual para reemplazarlo al guardar
        del self.controller.state["cuerpo"][index]
        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for bloque in self.controller.state["cuerpo"]:
            self.tree.insert("", tk.END, values=(bloque["texto"], bloque["enlace"], bloque["texto del enlace"], bloque["imagen"], bloque["Pie de imagen"]))

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

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, destino)
            self.controller.state["imagen"] = destino

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo procesar la imagen:\n{e}"
            )

    def probar_enlace(self):
        url = self.entry_enlace.get().strip()

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

    def texto_del_enlace(self):
        return self.entry_texto_del_enlace.get().strip()
    

class PreviewTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=16, pady=10)

        ttk.Button(toolbar, text="Actualizar preview", command=self.update_preview).pack(side="left")
        ttk.Button(toolbar, text="Guardar JSON", command=self.save_json).pack(side="left", padx=8)

        self.text_area = tk.Text(self, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=16, pady=10)

    def update_preview(self):
        self.controller.tab_datos.update_state()
        datos = self.controller.state.copy()
        datos["fecha"] = datetime.datetime.now().strftime("%d-%m-%Y")
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, json.dumps(datos, indent=4, ensure_ascii=False))

    def save_json(self):
        self.controller.tab_datos.update_state()
        datos = self.controller.state.copy()
        datos["fecha"] = datetime.datetime.now().strftime("%d-%m-%Y")
        ruta = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], initialdir="data")
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Éxito", "El JSON se ha guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")
