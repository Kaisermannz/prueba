import numpy as np
import random

class Ciudadano:
    def __init__(self, id, nombre, apellido, comunidad, enfermedad=None):
        self.__id = id
        self.__nombre = nombre
        self.__apellido = apellido
        self.__comunidad = comunidad
        self.__enfermedad = enfermedad
        self.__estado = "susceptible"
        self.__dias_enfermo = 0
        self.__conexiones = set()

    def get_id(self):
        return self.__id

    def get_nombre(self):
        return self.__nombre

    def get_apellido(self):
        return self.__apellido

    def get_comunidad(self):
        return self.__comunidad

    def get_enfermedad(self):
        return self.__enfermedad

    def get_estado(self):
        return self.__estado

    def set_estado(self, estado):
        if estado in ["susceptible", "infectado", "recuperado"]:
            if estado == "infectado" and self.__estado == "susceptible":
                self.__estado = estado
            elif estado == "recuperado" and self.__estado == "infectado":
                self.__estado = estado
                self.__enfermedad = None
            elif estado == "susceptible" and self.__estado != "recuperado":
                self.__estado = estado
                self.__enfermedad = None
                self.__dias_enfermo = 0

    def get_enfermo(self):
        return self.__estado == "infectado"

    def set_enfermo(self, estado):
        if estado:
            self.set_estado("infectado")
        else:
            self.set_estado("recuperado")

    def get_dias_enfermo(self):
        return self.__dias_enfermo

    def incrementar_dias_enfermo(self):
        if self.__estado == "infectado":
            self.__dias_enfermo += 1

    def agregar_conexion(self, otro_ciudadano):
        self.__conexiones.add(otro_ciudadano)
        otro_ciudadano.__conexiones.add(self)

    def get_conexiones(self):
        return self.__conexiones

    def infectar(self, enfermedad):
        if self.__estado == "susceptible":
            self.__enfermedad = enfermedad
            self.set_estado("infectado")

    def simular_contagio(self):
        if self.__estado == "infectado" and self.__enfermedad:
            # Filtrar las conexiones susceptibles
            conexiones_susceptibles = []
            for conexion in self.__conexiones:
                if conexion.get_estado() == "susceptible":
                    conexiones_susceptibles.append(conexion)
            
            num_susceptibles = len(conexiones_susceptibles)

            # Proceder solo si hay conexiones susceptibles
            if num_susceptibles > 0:
                # Obtener la probabilidad de contagio de la enfermedad
                prob_contagio = self.__enfermedad.get_probabilidad_contagio()

                # Calcular el número de nuevos contagios usando distribución binomial
                num_contagios = np.random.binomial(num_susceptibles, prob_contagio)

                # Seleccionar aleatoriamente a los ciudadanos que serán contagiados
                nuevos_contagiados = np.random.choice(conexiones_susceptibles, num_contagios, replace=False)

                # Infectar a los ciudadanos seleccionados
                for ciudadano in nuevos_contagiados:
                    ciudadano.infectar(self.__enfermedad)

    def actualizar_estado(self):
        if self.__estado == "infectado":
            self.incrementar_dias_enfermo()
            if self.__dias_enfermo >= self.__enfermedad.get_duracion():
                if random.random() < 0.3:  #  de probabilidad de recuperarse cada día después de la duración
                    self.set_estado("recuperado")

    def __str__(self):
        return f"Ciudadano(id={self.__id}, nombre={self.__nombre}, apellido={self.__apellido}, estado={self.__estado}, dias_enfermo={self.__dias_enfermo})"

    def remove_conexion(self, otro_ciudadano):
        if otro_ciudadano in self.__conexiones:
            self.__conexiones.remove(otro_ciudadano)
        if self in otro_ciudadano.get_conexiones():
            otro_ciudadano.get_conexiones().remove(self)
