import random
import pandas as pd
import os
import matplotlib.pyplot as plt
from ciudadano import Ciudadano

class Comunidad:
    def __init__(self):
        self.__ciudadanos = {}
        self.__grupos = []
        self.__historial = []
        self.__dias_simulados = 0
        self.__output_dir = "resultados_simulacion"
        self.__total_infectados_acumulados = 0
        self.__infectados_anteriores = 0 
        self.__infectados_diarios = []

        if not os.path.exists(self.__output_dir):
            os.makedirs(self.__output_dir)

    def agregar_ciudadano(self, ciudadano):
        self.__ciudadanos[ciudadano.get_id()] = ciudadano

    def get_ciudadanos(self):
        return self.__ciudadanos

    def crear_grupos(self, promedio_grupos_por_persona, min_personas_por_grupo, max_personas_por_grupo):
        ciudadanos_lista = list(self.__ciudadanos.values())
        num_ciudadanos = len(ciudadanos_lista)
        
        total_slots = num_ciudadanos * promedio_grupos_por_persona
        num_grupos = total_slots // ((min_personas_por_grupo + max_personas_por_grupo) // 2)
        
        self.__grupos = [[] for _ in range(num_grupos)]
        
        for ciudadano in ciudadanos_lista:
            num_grupos_ciudadano = max(1, int(random.gauss(promedio_grupos_por_persona, 1)))
            grupos_asignados = random.sample(range(num_grupos), num_grupos_ciudadano)
            for grupo_index in grupos_asignados:
                self.__grupos[grupo_index].append(ciudadano)
        
        for grupo in self.__grupos:
            while len(grupo) < min_personas_por_grupo:
                ciudadano = random.choice(ciudadanos_lista)
                if ciudadano not in grupo:
                    grupo.append(ciudadano)
        
        for grupo in self.__grupos:
            for ciudadano in grupo:
                for otro_ciudadano in grupo:
                    if otro_ciudadano != ciudadano:
                        ciudadano.agregar_conexion(otro_ciudadano)
        
        max_conexiones = 50
        for ciudadano in ciudadanos_lista:
            if len(ciudadano.get_conexiones()) > max_conexiones:
                conexiones = list(ciudadano.get_conexiones())
                random.shuffle(conexiones)
                for conexion in conexiones[max_conexiones:]:
                    ciudadano.remove_conexion(conexion)

    def infectar_aleatoriamente(self, num_infectados, enfermedad):
        ciudadanos_lista = list(self.__ciudadanos.values())
        infectados = random.sample(ciudadanos_lista, num_infectados)
        for ciudadano in infectados:
            ciudadano.infectar(enfermedad)
        self.__total_infectados_acumulados += num_infectados  

    def simular_contagio(self):
        for ciudadano in self.__ciudadanos.values():
            ciudadano.simular_contagio()
        for ciudadano in self.__ciudadanos.values():
            ciudadano.actualizar_estado()

        self.__generar_informe()
        self.__exportar_a_csv()
        self.__dias_simulados += 1

    def obtener_estadisticas(self):
        total_ciudadanos = len(self.__ciudadanos)
        infectados = sum(1 for c in self.__ciudadanos.values() if c.get_estado() == "infectado")
        recuperados = sum(1 for c in self.__ciudadanos.values() if c.get_estado() == "recuperado")
        susceptibles = total_ciudadanos - infectados - recuperados
        return {
            "total_ciudadanos": total_ciudadanos,
            "susceptibles": susceptibles,
            "infectados": infectados,
            "recuperados": recuperados
        }

    def __generar_informe(self):
        stats = self.obtener_estadisticas()
        infectados_actuales = stats["infectados"]
        infectados_hoy = max(0, infectados_actuales - self.__infectados_anteriores)
        self.__infectados_diarios.append(infectados_hoy)
        self.__infectados_anteriores = infectados_actuales

        informe = {
            "dia": self.__dias_simulados,
            "susceptibles": stats["susceptibles"],
            "infectados": infectados_actuales,
            "recuperados": stats["recuperados"],
            "infectados_diarios": infectados_hoy
        }
        self.__historial.append(informe)
        print(
            f"Día {self.__dias_simulados}: Susceptibles: {informe['susceptibles']}, "
            f"Infectados: {informe['infectados']}, Recuperados: {informe['recuperados']}, "
            f"Infectados hoy: {infectados_hoy}"
        )

    def __exportar_a_csv(self):
        nombre_archivo = os.path.join(self.__output_dir, f"simulacion_dia_{self.__dias_simulados}.csv")
        datos = []
        for ciudadano in self.__ciudadanos.values():
            dato = {
                "id": ciudadano.get_id(),
                "nombre": ciudadano.get_nombre(),
                "apellido": ciudadano.get_apellido(),
                "estado": ciudadano.get_estado(),
                "dias_enfermo": ciudadano.get_dias_enfermo(),
            }
            datos.append(dato)
            
        df = pd.DataFrame(datos)
        df.to_csv(nombre_archivo, index=False)

    def imprimir_estadisticas(self):
        stats = self.obtener_estadisticas()
        print(f"Total de ciudadanos: {stats['total_ciudadanos']}")
        print(f"Ciudadanos susceptibles: {stats['susceptibles']}")
        print(f"Ciudadanos infectados: {stats['infectados']}")
        print(f"Ciudadanos recuperados: {stats['recuperados']}")

    def imprimir_grupos(self):
        for i, grupo in enumerate(self.__grupos):
            print(f"Grupo {i + 1}: {[c.get_id() for c in grupo]}")

    def generar_grafica(self):
        dias = [informe['dia'] for informe in self.__historial]
        susceptibles = [informe['susceptibles'] for informe in self.__historial]
        infectados = [informe['infectados'] for informe in self.__historial]
        recuperados = [informe['recuperados'] for informe in self.__historial]
        infectados_diarios = self.__infectados_diarios

        plt.figure(figsize=(10, 6))
        plt.plot(dias, susceptibles, label='Susceptibles', color='blue')
        plt.plot(dias, infectados, label='Infectados (actuales)', color='red')
        plt.plot(dias, recuperados, label='Recuperados', color='green')

        plt.title('Modelo SIR - Evolución de la epidemia')
        plt.xlabel('Días')
        plt.ylabel('Número de individuos')
        plt.legend()
        plt.grid(True)

        plt.savefig(os.path.join(self.__output_dir, 'grafica_SIR.png'))
        plt.close()