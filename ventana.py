import gi
import csv
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject

ID_APLICACION = "com.Cristobal.Araya.liststore"

class Row(GObject.Object):
    def __init__(self, id, nombre, apellido, estado, dias_enfermo):
        super().__init__()
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.estado = estado
        self.dias_enfermo = int(dias_enfermo)

    def __lt__(self, otro):
        # Ordenar primero los infectados, luego por días de enfermedad
        if self.estado == "infectado" and otro.estado == "infectado":
            return self.dias_enfermo > otro.dias_enfermo
        elif self.estado == "infectado":
            return True
        elif otro.estado == "infectado":
            return False
        else:
            return self.dias_enfermo > otro.dias_enfermo

class SimulacionCovidWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Simulación COVID")
        self.set_default_size(800, 600)
        self.dia_actual = 1
        self.modelo = Gio.ListStore()
        
        # Armando la estructura de la ventana
        caja_vertical_principal = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
        self.set_child(caja_vertical_principal)

        caja_horizontal = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        caja_vertical_principal.append(caja_horizontal)

        # Configuración de la barra de título
        barra_titulo = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=barra_titulo)
        self.set_title(f"Simulación - Día {self.dia_actual}")

        # Creación del menú
        menu = Gio.Menu.new()
        self.popover = Gtk.PopoverMenu()
        self.popover.set_menu_model(menu)
        self.boton_menu = Gtk.MenuButton()
        self.boton_menu.set_popover(self.popover)
        self.boton_menu.set_icon_name("open-menu-symbolic")
        barra_titulo.pack_end(self.boton_menu)

        # Botones para navegar entre días
        boton_retroceder_10 = Gtk.Button.new_with_label("<<")
        boton_retroceder_10.connect("clicked", self.on_back_10_button_clicked)
        barra_titulo.pack_start(boton_retroceder_10)

        boton_retroceder = Gtk.Button.new_with_label("<")
        boton_retroceder.connect("clicked", self.on_back_button_clicked)
        barra_titulo.pack_start(boton_retroceder)

        boton_avanzar = Gtk.Button.new_with_label(">")
        boton_avanzar.connect("clicked", self.on_forward_button_clicked)
        barra_titulo.pack_start(boton_avanzar)

        boton_avanzar_10 = Gtk.Button.new_with_label(">>")
        boton_avanzar_10.connect("clicked", self.on_forward_10_button_clicked)
        barra_titulo.pack_start(boton_avanzar_10)

        boton_grafico = Gtk.Button.new_with_label("Grafico")
        boton_grafico.connect("clicked", self.on_grafico)
        barra_titulo.pack_start(boton_grafico)

        # Configuración del menú "Acerca de"
        accion_acerca_de = Gio.SimpleAction.new("about", None)
        accion_acerca_de.connect("activate", self.show_about_dialog)
        self.add_action(accion_acerca_de)
        menu.append("Acerca de", "win.about")

        # Configuración de la vista de columnas
        modelo_seleccion = Gtk.SingleSelection(model=self.modelo)
        modelo_seleccion.connect("selection-changed", self.on_selected_items_changed)

        ventana_desplazable = Gtk.ScrolledWindow()
        ventana_desplazable.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        ventana_desplazable.set_vexpand(True)

        vista_columnas = Gtk.ColumnView()
        vista_columnas.set_model(modelo_seleccion)

        # Definición de las columnas
        fabricas = [
            ("ID", self.on_list_item_bind, 1),
            ("Nombre", self.on_list_item_bind, 2),
            ("Apellido", self.on_list_item_bind, 3),
            ("Estado", self.on_list_item_bind, 4),
            ("Días Enfermo", self.on_list_item_bind, 5)
        ]

        for titulo, func_vinculacion, num_columna in fabricas:
            fabrica = Gtk.SignalListItemFactory()
            fabrica.connect("setup", self.on_list_item_setup)
            fabrica.connect("bind", func_vinculacion, num_columna)
            columna = Gtk.ColumnViewColumn(title=titulo, factory=fabrica)
            columna.set_resizable(True)
            columna.set_expand(True)
            vista_columnas.append_column(columna)

        ventana_desplazable.set_child(vista_columnas)
        caja_vertical_principal.append(ventana_desplazable)

        self.load_csv_data()

    def on_grafico(self, button):
        image_path = "resultados_simulacion/grafica_SIR.png"
        if not os.path.exists(image_path):
            print(f"Error: La imagen {image_path} no existe.")
            return

        dialog = Gtk.Window(title="Gráfico SIR")
        dialog.set_default_size(1000, 600)
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        
        image = Gtk.Picture.new_for_filename(image_path)
        image.set_can_shrink(False)
            
        scrolled_window.set_child(image)
        dialog.set_child(scrolled_window)
            
        dialog.present()

    def load_csv_data(self):
        self.modelo.remove_all()
        ruta_archivo = f"resultados_simulacion/simulacion_dia_{self.dia_actual}.csv"
        if os.path.exists(ruta_archivo):
            filas = []
            with open(ruta_archivo, 'r') as archivo_csv:
                lector_csv = csv.reader(archivo_csv)
                next(lector_csv)  # Saltamos la cabecera
                for fila in lector_csv:
                    filas.append(Row(*fila))
            
            # Ordenamos las filas
            filas.sort()
            
            # Agregamos las filas ordenadas al modelo
            for fila in filas:
                self.modelo.append(fila)
            
            self.set_title(f"Simulación - Día {self.dia_actual}")
        else:
            print(f"No se encontró el archivo: {ruta_archivo}")

    def change_day(self, delta):
        nuevo_dia = max(0, self.dia_actual + delta)
        ruta_archivo = f"resultados_simulacion/simulacion_dia_{nuevo_dia}.csv"
        if os.path.exists(ruta_archivo):
            self.dia_actual = nuevo_dia
            self.load_csv_data()
        else:
            print(f"No hay datos para el día {nuevo_dia}")

    def on_back_button_clicked(self, boton):
        self.change_day(-1)

    def on_forward_button_clicked(self, boton):
        self.change_day(1)

    def on_back_10_button_clicked(self, boton):
        self.change_day(-10)

    def on_forward_10_button_clicked(self, boton):
        self.change_day(10)

    def show_about_dialog(self, accion, param):
        self.about = Gtk.AboutDialog()
        self.about.set_transient_for(self)
        self.about.set_modal(self)
        self.about.set_authors(["Cristobal Araya"])
        self.about.set_copyright("Copyright 2024")
        self.about.set_license_type(Gtk.License.GPL_3_0)
        self.about.set_website("https://github.com/Kaisermannz/Proyecto")
        self.about.set_website_label("Github Del Proyecto")
        self.about.set_version("1.0")
        self.about.set_logo_icon_name("org.example.example")
        self.about.set_visible(True)

    def on_selected_items_changed(self, seleccion, posicion, n_elementos):
        elemento_seleccionado = seleccion.get_selected_item()
        if elemento_seleccionado is not None:
            print(f"ID: {elemento_seleccionado.id}, Nombre: {elemento_seleccionado.nombre} {elemento_seleccionado.apellido}, Estado: {elemento_seleccionado.estado}, Días enfermo: {elemento_seleccionado.dias_enfermo}")

    def on_list_item_setup(self, fabrica, elemento):
        etiqueta = Gtk.Inscription()
        elemento.set_child(etiqueta)

    def on_list_item_bind(self, fabrica, elemento, num_columna):
        fila = elemento.get_item()
        texto = ""
        if num_columna == 1:
            texto = str(fila.id)
        elif num_columna == 2:
            texto = fila.nombre
        elif num_columna == 3:
            texto = fila.apellido
        elif num_columna == 4:
            texto = fila.estado
        elif num_columna == 5:
            texto = str(fila.dias_enfermo)
        elemento.get_child().set_text(texto)

class SimulacionCovidApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=ID_APLICACION, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        ventana = SimulacionCovidWindow(self)
        ventana.present()

def create_simulacion_covid_app():
    return SimulacionCovidApp()

if __name__ == "__main__":
    app = create_simulacion_covid_app()
    app.run(None)