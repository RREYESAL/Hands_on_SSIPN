"""Lectura de CMS Open Data con respaldo automático a datos sintéticos.

Uso típico::

    from hepss.io import abrir_events
    arbol, origen = abrir_events("dimuon2012")
    eventos = arbol.arrays(["nMuon", "Muon_pt"], entry_stop=100_000)

``origen`` vale ``"opendata"`` o ``"sintetico"``. Se usa el respaldo sintético
cuando:

1. la variable de entorno ``HEPSS_SINTETICO=1`` está definida (forzarlo),
2. no hay red o el servidor de Open Data no responde en ``timeout`` segundos,
3. la ruta del archivo no está configurada (por ejemplo las de 2016 en el YAML).

En esos casos se escribe una vez un archivo en ``data/`` y se reutiliza.
"""

from __future__ import annotations

import os
import warnings
from pathlib import Path

import awkward as ak
import uproot

from . import sintetico

URL_DIMUON_2012 = [
    "https://opendata.cern.ch/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root",
    "root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root",
]

RAMAS_MUON = ["nMuon", "Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass", "Muon_charge"]


def raiz_repo() -> Path:
    """Busca la carpeta del repositorio (la que contiene configs/ o environment.yml)."""
    aqui = Path.cwd().resolve()
    for p in [aqui, *aqui.parents]:
        if (p / "configs").is_dir() or (p / "environment.yml").exists():
            return p
    return aqui


def carpeta_datos() -> Path:
    d = raiz_repo() / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _respaldo(nombre: str, **kw):
    """Devuelve (ruta, función generadora) del archivo sintético para cada muestra."""
    d = carpeta_datos()
    if nombre == "dimuon2012":
        n = kw.get("n_eventos_sinteticos", 2_000_000)
        ruta = d / f"sintetico_dimuon2012_{n}.root"
        return ruta, lambda: sintetico.generar_dimuon_2012(ruta, n_eventos=n)
    if nombre in ("datos2016", "mc2016"):
        n = kw.get("n_eventos_sinteticos", 400_000)
        es_mc = nombre == "mc2016"
        ruta = d / f"sintetico_{nombre}_{n}.root"
        return ruta, lambda: sintetico.generar_nanoaod_2016(ruta, es_mc=es_mc, n_eventos=n)
    raise ValueError(f"No hay respaldo sintético para '{nombre}'")


def abrir_events(nombre="dimuon2012", urls=None, timeout=30, **kw):
    """Abre el árbol Events de una muestra; si falla, usa (y si hace falta genera) la sintética.

    nombre: "dimuon2012", "datos2016" o "mc2016".
    urls: lista de rutas a intentar en orden (HTTPS, XRootD o archivo local).
    Devuelve (arbol, origen).
    """
    if urls is None:
        urls = URL_DIMUON_2012 if nombre == "dimuon2012" else []
    if isinstance(urls, (str, Path)):
        urls = [urls]
    urls = [str(u) for u in urls if u]

    motivos = [] if urls else ["no hay ruta configurada"]
    if os.environ.get("HEPSS_SINTETICO", "0") == "1":
        motivos = ["HEPSS_SINTETICO=1"]
        urls = []
    for url in urls:
        if url.startswith("root://"):
            try:
                import fsspec_xrootd  # noqa: F401
            except ImportError:
                motivos.append("XRootD no instalado (pip install fsspec-xrootd)")
                continue
        try:
            arbol = uproot.open(url, timeout=timeout)["Events"]
            _ = arbol.num_entries  # fuerza la lectura de la cabecera
            print(f"[hepss] Leyendo CMS Open Data: {url}")
            return arbol, "opendata"
        except Exception as e:  # sin red, 403, timeout, etc.
            motivos.append(f"{url.split(':')[0]}: {type(e).__name__}: {str(e)[:120]}")

    ruta, generar = _respaldo(nombre, **kw)
    if not ruta.exists():
        print(f"[hepss] Generando datos sintéticos en {ruta} (tarda ~1 min, solo la primera vez)...")
        generar()
    warnings.warn(
        f"[hepss] USANDO DATOS SINTÉTICOS para '{nombre}' ({'; '.join(motivos)}). "
        "Las gráficas NO son CMS Open Data.",
        stacklevel=2,
    )
    return uproot.open(ruta)["Events"], "sintetico"


def leer_muones(ruta="dimuon2012", n_eventos=2_000_000, ramas=None, urls=None, **kw):
    """Lee las ramas de muones de los primeros ``n_eventos`` en un ``ak.Array``.

    TODO (semana 2, E2.7): mueve aquí el código de lectura de tu notebook ``01_intro_uproot``.

    Especificación (los notebooks 02 y 03 la usan así):

    * ``ruta``: un nombre de muestra conocido (``"dimuon2012"``, ``"datos2016"``, ``"mc2016"``)
      o una URL/ruta a un archivo NanoAOD.
    * ``ramas``: lista de ramas a leer; por defecto ``RAMAS_MUON``.
    * Abre el árbol con ``abrir_events`` (así hereda el respaldo sintético) y lee con
      ``arbol.arrays(ramas, entry_stop=n_eventos)``.
    * Devuelve la tupla ``(eventos, origen)``, con ``origen`` igual a ``"opendata"`` o ``"sintetico"``.
    """
    raise NotImplementedError("E2.7: implementa hepss.io.leer_muones")


def zip_muones(eventos, prefijo="Muon"):
    """Agrupa las ramas Muon_* en un registro: eventos.Muon_pt -> muones.pt."""
    campos = {c[len(prefijo) + 1:]: eventos[c] for c in eventos.fields if c.startswith(prefijo + "_")}
    return ak.zip(campos)
