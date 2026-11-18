"""Selecciones configuradas en YAML y tabla de cortes (cutflow), semana 4."""

from __future__ import annotations

import operator

import yaml

# Operadores permitidos en el YAML: "op": ">"  ->  operator.gt, etc.
OPERADORES = {">": operator.gt, ">=": operator.ge, "<": operator.lt, "<=": operator.le, "==": operator.eq}


def cargar_config(ruta):
    """Lee un archivo YAML y devuelve un diccionario."""
    with open(ruta) as f:
        return yaml.safe_load(f)


def masa_par(mu):
    """Masa invariante de los dos primeros muones de cada evento (GeV).

    TODO (semana 4, E4.2): reutiliza ``hepss.cinematica.cuadrivectores``.
    Supone que todos los eventos de ``mu`` tienen al menos 2 muones.
    """
    raise NotImplementedError("E4.2: implementa hepss.seleccion.masa_par")


def aplicar_seleccion(muones, config, pesos=None):
    """Aplica EN ORDEN los cortes del YAML y devuelve ``(muones_sel, mascara_eventos, cutflow, etapas)``.

    TODO (semana 4, E4.2). Especificación (el notebook 03 la usa así):

    * ``muones``: registro de awkward con campos ``pt, eta, phi, mass, charge, tightId, ...``
      (sale de ``hepss.io.zip_muones``).
    * ``config``: el diccionario de ``configs/seleccion_z.yaml``.
    * ``pesos``: pesos por evento (MC) o None (datos: todos valen 1).
    * Cortes por muon (``config["cortes_muon"]``): se quitan los muones que fallan; un evento
      sigue vivo mientras le queden al menos 2 muones.
    * Cortes por evento (``config["cortes_evento"]``): exactamente 2 muones, carga opuesta y
      ventana de masa, en ese orden.
    * ``muones_sel``: los muones que quedan en los eventos que pasan todo.
    * ``mascara_eventos``: arreglo booleano de numpy de longitud ``len(muones)``.
    * ``cutflow``: ``pandas.DataFrame`` con una fila por etapa ("Inicial", un corte por muon,
      y una por cada corte de evento) y columnas ``"Corte"``, ``"Eventos"``, ``"Suma de pesos"``,
      ``"Eficiencia relativa"`` y ``"Eficiencia acumulada"``.
    * ``etapas``: lista de ``(nombre, muones de los eventos vivos)`` tras cada corte, para graficar.

    La misma función, con el mismo YAML, se aplica a datos y a MC.
    """
    raise NotImplementedError("E4.2: implementa hepss.seleccion.aplicar_seleccion")
