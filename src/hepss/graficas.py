"""Gráficas con estilo CMS (mplhep).

Regla del grupo: toda gráfica hecha con Open Data lleva la etiqueta "CMS Open Data";
las hechas con el generador sintético llevan "Simulación sintética" para que
nunca se confundan con datos reales. Usa siempre ``etiqueta_cms(ax, ORIGEN)``.
"""

from __future__ import annotations

import matplotlib.pyplot as plt  # noqa: F401
import mplhep as hep

hep.style.use("CMS")


def etiqueta_cms(ax, origen="opendata", anio=2012, com=8, **kw):
    """Pone la etiqueta CMS en ``ax`` según el origen de los datos ("opendata" o "sintetico")."""
    if origen == "sintetico":
        ax.text(0.0, 1.01, "Simulación sintética (no son datos de CMS)", transform=ax.transAxes,
                fontsize=16, fontweight="bold", va="bottom")
        ax.text(1.0, 1.01, f"({com} TeV)", transform=ax.transAxes, fontsize=16, va="bottom", ha="right")
        return
    hep.cms.label(ax=ax, year=anio, com=com, label="Open Data", data=True, **kw)


def hist_cms(h, ax=None, origen="opendata", anio=2012, com=8, logy=False, logx=False,
             etiqueta=None, densidad=False, **kw):
    """Dibuja un histograma de ``hist`` (o una lista de histogramas) con estilo CMS.

    TODO (semana 2, E2.7): mueve aquí el código de gráficas que repetiste en ``01_intro_uproot``.

    Especificación (los notebooks 02 y 03 la usan así):

    * Si ``ax`` es None, crea una figura nueva.
    * Dibuja con ``mplhep.histplot`` (los ``**kw`` extra van ahí); ``etiqueta`` es la leyenda
      y ``densidad=True`` normaliza a área 1.
    * ``logy`` / ``logx`` ponen escala logarítmica en el eje correspondiente.
    * Siempre llama a ``etiqueta_cms(ax, origen=origen, anio=anio, com=com)``.
    * Devuelve el eje ``ax``.
    """
    raise NotImplementedError("E2.7: implementa hepss.graficas.hist_cms")
