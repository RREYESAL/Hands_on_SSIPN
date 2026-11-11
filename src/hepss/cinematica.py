"""Cinemática de dimuones (semana 3)."""

from __future__ import annotations

import awkward as ak  # noqa: F401
import numpy as np  # noqa: F401
import vector

vector.register_awkward()


def masa_sin_masa(pt1, eta1, phi1, pt2, eta2, phi2):
    """Masa invariante de dos partículas despreciando su masa, en GeV.

    TODO (semana 3, E3.2): implementa la fórmula del programa sin bucles: debe funcionar
    igual con números, arreglos de numpy y arreglos de awkward.
    """
    raise NotImplementedError("E3.2: implementa hepss.cinematica.masa_sin_masa")


def cuadrivectores(muones):
    """Convierte un registro con campos ``pt, eta, phi, mass`` en cuadrivectores de ``vector``.

    TODO (semana 3, E3.3): usa ``ak.zip(..., with_name="Momentum4D")``. Así ``(v1 + v2).mass``
    da la masa invariante del par.
    """
    raise NotImplementedError("E3.3: implementa hepss.cinematica.cuadrivectores")
