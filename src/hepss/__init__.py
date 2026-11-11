"""hepss: funciones reutilizables del servicio social (lectura, cinemática, selección, gráficas).

Regla del repositorio: cuando una función se usa en dos notebooks, se mueve aquí.
"""

__version__ = "0.1.0"

from . import cinematica, constantes, graficas, io, seleccion, sintetico  # noqa: F401
