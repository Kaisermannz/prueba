class Enfermedad:
    def __init__(self, nombre, probabilidad_contagio, duracion):
        self.__nombre = nombre
        self.__probabilidad_contagio = probabilidad_contagio
        self.__duracion = duracion

    def get_nombre(self):
        return self.__nombre

    def get_probabilidad_contagio(self):
        return self.__probabilidad_contagio

    def get_duracion(self):
        return self.__duracion
