"""Generador de datos sintéticos con el mismo formato que CMS Open Data (NanoAOD).

Se usa cuando no se puede leer CMS Open Data (sin red, red lenta o un servidor
que bloquea el acceso). Los archivos que escribe tienen un árbol ``Events``
con las mismas ramas que los archivos reales, así que el código de análisis es
idéntico en ambos casos.

**No son datos de CMS.** Es una simulación de juguete:

* Resonancias con su masa y anchura del PDG, decaimiento isótropo a dos muones
  y un espectro de pT del padre de forma ``pT / (1 + (pT/p0)^2)^n``.
* Continuo tipo Drell–Yan (ley de potencias en masa) y combinatorio con cargas
  aleatorias (da pares de igual carga).
* Detector simplificado: aceptancia |η| < 2.4, umbral de pT del trigger,
  eficiencia de reconstrucción del 97 % por muon y resolución en pT que empeora
  con |η| y con pT.
* Para 2016: variables de calidad (``tightId``, ``pfRelIso04_all``, ``dxy``,
  ``dz``), vértices primarios con *pile-up* distinto en datos y MC, y en el MC
  la *truth information* (``GenPart_*`` y ``Muon_genPartIdx``).

Los números (fracciones, resoluciones, eficiencias) están elegidos para que las
verificaciones del programa salgan con la misma lógica que con datos reales,
no para reproducir CMS con precisión.

Nota para el estudiante: este archivo es infraestructura. No hace falta leerlo ni
modificarlo para resolver los ejercicios; lo que se pide es descubrir las
propiedades de la muestra en los datos, como se haría con datos reales.
"""

from __future__ import annotations

from pathlib import Path

import awkward as ak
import numpy as np

# Tablas internas del generador (masas y anchuras del PDG 2024, GeV). Son solo para
# generar datos de juguete: en los ejercicios busca tú los valores en https://pdg.lbl.gov.
M_MU = 0.1056583755
RESONANCIAS = {
    r"$\eta$": 0.547862,
    r"$\rho/\omega$": 0.77526,
    r"$\phi$": 1.019461,
    r"$J/\psi$": 3.096900,
    r"$\psi(2S)$": 3.686097,
    r"$\Upsilon(1S)$": 9.46040,
    r"$\Upsilon(2S)$": 10.02326,
    r"$\Upsilon(3S)$": 10.3552,
    r"$Z$": 91.1880,
}
ANCHURAS = {
    r"$\eta$": 1.31e-6,
    r"$\rho/\omega$": 0.1474,
    r"$\phi$": 0.004249,
    r"$J/\psi$": 9.26e-5,
    r"$\psi(2S)$": 2.94e-4,
    r"$\Upsilon(1S)$": 5.40e-5,
    r"$\Upsilon(2S)$": 3.19e-5,
    r"$\Upsilon(3S)$": 2.03e-5,
    r"$Z$": 2.4955,
}

# ---------------------------------------------------------------------------
# Herramientas de muestreo
# ---------------------------------------------------------------------------


def _muestrear_pt(n, p0, expo, rng, pt_max=300.0):
    """Muestra pT con densidad pT / (1 + (pT/p0)^2)^expo por CDF inversa numérica."""
    x = np.linspace(0.0, pt_max, 20001)
    pdf = x / (1.0 + (x / p0) ** 2) ** expo
    cdf = np.cumsum(pdf)
    cdf /= cdf[-1]
    return np.interp(rng.uniform(size=n), cdf, x)


def _muestrear_bw(n, m0, gamma, rng, m_min, m_max):
    """Breit–Wigner no relativista (Cauchy) truncada a [m_min, m_max]."""
    out = np.empty(0)
    while out.size < n:
        m = m0 + 0.5 * gamma * np.tan(np.pi * (rng.uniform(size=2 * n) - 0.5))
        out = np.concatenate([out, m[(m > m_min) & (m < m_max)]])
    return out[:n]


def _muestrear_potencia(n, alfa, m_min, m_max, rng):
    """Masa con densidad proporcional a m^-alfa entre m_min y m_max."""
    a = 1.0 - alfa
    u = rng.uniform(size=n)
    return (m_min**a + u * (m_max**a - m_min**a)) ** (1.0 / a)


def _decaer_dos_cuerpos(m, pt, y, phi, rng):
    """Decaimiento isótropo padre -> mu mu y boost al laboratorio.

    Devuelve dos tuplas (pt, eta, phi) de los muones.
    """
    mt = np.sqrt(m**2 + pt**2)
    E = mt * np.cosh(y)
    px, py, pz = pt * np.cos(phi), pt * np.sin(phi), mt * np.sinh(y)

    pstar = np.sqrt(np.clip(m**2 / 4.0 - M_MU**2, 0.0, None))
    estar = m / 2.0
    cos_t = rng.uniform(-1, 1, m.size)
    sin_t = np.sqrt(1 - cos_t**2)
    ang = rng.uniform(0, 2 * np.pi, m.size)
    d = np.stack([pstar * sin_t * np.cos(ang), pstar * sin_t * np.sin(ang), pstar * cos_t])

    b = np.stack([px, py, pz]) / E
    b2 = np.sum(b**2, axis=0)
    gam = E / m
    bp = np.sum(b * d, axis=0)
    g2 = np.where(b2 > 0, (gam - 1.0) / np.where(b2 > 0, b2, 1.0), 0.0)

    hijos = []
    for signo in (+1, -1):
        p = signo * d + g2 * (signo * bp) * b + gam * b * estar
        pt_h = np.hypot(p[0], p[1])
        eta_h = np.arcsinh(p[2] / np.maximum(pt_h, 1e-9))
        phi_h = np.arctan2(p[1], p[0])
        hijos.append((pt_h, eta_h, phi_h))
    return hijos


def _resolucion_relativa(pt, eta, factor=1.0):
    """sigma(pT)/pT: ~0.8 % en el barril, ~2 % en los endcaps, crece con pT."""
    a = 0.008 + 0.012 * (np.abs(eta) / 2.4) ** 2
    b = 1.0e-4 * pt
    return factor * np.hypot(a, b)


def _empaquetar(columnas, valido):
    """Convierte columnas (N, k) con máscara en listas irregulares ordenadas por pT."""
    pt = np.where(valido, columnas["pt"], -np.inf)
    orden = np.argsort(-pt, axis=1, kind="stable")
    valido = np.take_along_axis(valido, orden, axis=1)
    cuentas = valido.sum(axis=1)
    salida = {}
    for nombre, col in columnas.items():
        col = np.take_along_axis(col, orden, axis=1)
        salida[nombre] = ak.unflatten(col[valido], cuentas)
    return salida, cuentas


def _escribir(ruta, ramas):
    """Escribe un TTree 'Events' estilo NanoAOD (ramas nMuon, Muon_pt, ...)."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    import uproot

    with uproot.recreate(ruta) as f:
        f.mktree("Events", {k: v.type if isinstance(v, ak.Array) else v.dtype for k, v in ramas.items()})
        f["Events"].extend(ramas)
    return ruta


# ---------------------------------------------------------------------------
# Dimuones 2012 (formato del archivo educativo Run2012BC_DoubleMuParked_Muons)
# ---------------------------------------------------------------------------

# nombre: (fracción antes del trigger, p0 [GeV], exponente del espectro de pT)
_CATEGORIAS_2012 = {
    "continuo": (0.30, 4.0, 2.2),
    "combinatorio": (0.07, None, None),
    r"$\eta$": (0.010, 5.0, 2.2),
    r"$\rho/\omega$": (0.030, 5.0, 2.2),
    r"$\phi$": (0.022, 5.0, 2.2),
    r"$J/\psi$": (0.36, 5.0, 2.6),
    r"$\psi(2S)$": (0.018, 5.5, 2.6),
    r"$\Upsilon(1S)$": (0.040, 8.0, 2.4),
    r"$\Upsilon(2S)$": (0.012, 8.0, 2.4),
    r"$\Upsilon(3S)$": (0.008, 8.0, 2.4),
    r"$Z$": (0.009, 10.0, 1.6),
}


def _bloque_2012(n, rng):
    nombres = list(_CATEGORIAS_2012)
    frac = np.array([_CATEGORIAS_2012[k][0] for k in nombres])
    cat = rng.choice(len(nombres), size=n, p=frac / frac.sum())

    pt1 = np.empty(n); eta1 = np.empty(n); phi1 = np.empty(n)
    pt2 = np.empty(n); eta2 = np.empty(n); phi2 = np.empty(n)
    q1 = -np.ones(n, dtype=np.int32)
    q2 = np.ones(n, dtype=np.int32)

    for i, nombre in enumerate(nombres):
        sel = cat == i
        k = int(sel.sum())
        if k == 0:
            continue
        if nombre == "combinatorio":
            # dos muones independientes (por ejemplo de decaimientos de hadrones b/c y pi/K)
            pt1[sel] = 3.0 + rng.exponential(2.5, k)
            pt2[sel] = 3.0 + rng.exponential(2.5, k)
            eta1[sel] = rng.uniform(-2.6, 2.6, k)
            eta2[sel] = rng.uniform(-2.6, 2.6, k)
            phi1[sel] = rng.uniform(-np.pi, np.pi, k)
            phi2[sel] = rng.uniform(-np.pi, np.pi, k)
            q1[sel] = rng.choice([-1, 1], k)
            q2[sel] = rng.choice([-1, 1], k)
            continue
        _, p0, expo = _CATEGORIAS_2012[nombre]
        if nombre == "continuo":
            m = _muestrear_potencia(k, 2.0, 0.22, 160.0, rng)
        else:
            m0, g = RESONANCIAS[nombre], ANCHURAS[nombre]
            m = _muestrear_bw(k, m0, g, rng, max(2 * M_MU + 1e-3, m0 - 10 * g - 0.05), m0 + 10 * g + 0.05)
        pt = _muestrear_pt(k, p0, expo, rng)
        y = rng.uniform(-2.8, 2.8, k)
        phi = rng.uniform(-np.pi, np.pi, k)
        (a, b) = _decaer_dos_cuerpos(m, pt, y, phi, rng)
        pt1[sel], eta1[sel], phi1[sel] = a
        pt2[sel], eta2[sel], phi2[sel] = b

    # extras: muones blandos de otros procesos en el mismo evento
    n_extra = rng.poisson(0.12, n)
    kmax = 2 + max(int(n_extra.max()), 1)
    cols = {c: np.zeros((n, kmax)) for c in ("pt", "eta", "phi")}
    carga = np.zeros((n, kmax), dtype=np.int32)
    cols["pt"][:, 0], cols["pt"][:, 1] = pt1, pt2
    cols["eta"][:, 0], cols["eta"][:, 1] = eta1, eta2
    cols["phi"][:, 0], cols["phi"][:, 1] = phi1, phi2
    carga[:, 0], carga[:, 1] = q1, q2
    hay = np.zeros((n, kmax), dtype=bool)
    hay[:, :2] = True
    for j in range(kmax - 2):
        s = n_extra > j
        m = int(s.sum())
        cols["pt"][s, 2 + j] = 2.5 + rng.exponential(2.5, m)
        cols["eta"][s, 2 + j] = rng.uniform(-2.6, 2.6, m)
        cols["phi"][s, 2 + j] = rng.uniform(-np.pi, np.pi, m)
        carga[s, 2 + j] = rng.choice([-1, 1], m)
        hay[s, 2 + j] = True

    # trigger de doble muon (sobre los dos muones "duros", en nivel generador):
    # ambos con pT > 3.5 GeV y |eta| < 2.4
    trig = (pt1 > 3.5) & (pt2 > 3.5) & (np.abs(eta1) < 2.4) & (np.abs(eta2) < 2.4)

    # reconstrucción: aceptancia, umbral para llegar a las cámaras de muones y eficiencia
    p = cols["pt"] * np.cosh(cols["eta"])
    llega = np.where(np.abs(cols["eta"]) < 1.2, cols["pt"] > 3.0, p > 3.0)
    reco = hay & (np.abs(cols["eta"]) < 2.4) & llega & (rng.uniform(size=hay.shape) < 0.97)
    cols["pt"] = cols["pt"] * (1.0 + _resolucion_relativa(cols["pt"], cols["eta"]) * rng.normal(size=hay.shape))

    reco &= trig[:, None]
    cols["mass"] = np.full((n, kmax), M_MU)
    cols["charge"] = carga
    muones, cuentas = _empaquetar(cols, reco)
    guardar = cuentas >= 1  # el NanoAOD de un dataset de trigger no tiene eventos sin muones
    return {k: v[guardar] for k, v in muones.items()}


def generar_dimuon_2012(ruta, n_eventos=2_000_000, semilla=2012):
    """Escribe un archivo con el formato de Run2012BC_DoubleMuParked_Muons.root.

    Ramas: nMuon, Muon_pt, Muon_eta, Muon_phi, Muon_mass, Muon_charge.
    """
    rng = np.random.default_rng(semilla)
    bloques = []
    total = 0
    while total < n_eventos:
        b = _bloque_2012(600_000, rng)
        bloques.append(b)
        total += len(b["pt"])
    muones = {k: ak.concatenate([b[k] for b in bloques])[:n_eventos] for k in bloques[0]}
    tipos = {"pt": np.float32, "eta": np.float32, "phi": np.float32, "mass": np.float32, "charge": np.int32}
    rec = ak.zip({k: ak.values_astype(muones[k], tipos[k]) for k in tipos})
    return _escribir(ruta, {"Muon": rec})


# ---------------------------------------------------------------------------
# Datos y MC 2016 (formato NanoAODv9 reducido) para la semana 4
# ---------------------------------------------------------------------------


def _bloque_2016(n, rng, es_mc, frac_fondo):
    # --- proceso duro ---
    fondo = (rng.uniform(size=n) < frac_fondo) if not es_mc else np.zeros(n, dtype=bool)
    dy = ~fondo
    k = int(dy.sum())
    m = np.where(
        rng.uniform(size=k) < 0.88,
        _muestrear_bw(k, RESONANCIAS[r"$Z$"], ANCHURAS[r"$Z$"], rng, 50.0, 200.0),
        _muestrear_potencia(k, 2.5, 50.0, 200.0, rng),
    )
    pt_z = _muestrear_pt(k, 8.0, 1.6, rng)
    y = rng.normal(0.0, 1.6, k)
    phi = rng.uniform(-np.pi, np.pi, k)
    a, b = _decaer_dos_cuerpos(m, pt_z, y, phi, rng)

    gpt = np.zeros((n, 2)); geta = np.zeros((n, 2)); gphi = np.zeros((n, 2))
    gpt[dy, 0], geta[dy, 0], gphi[dy, 0] = a
    gpt[dy, 1], geta[dy, 1], gphi[dy, 1] = b
    q = np.zeros((n, 2), dtype=np.int32)
    q[:, 0], q[:, 1] = -1, 1

    # fondo en datos: muones no aislados y desplazados (ttbar, QCD con hadrones b/c)
    kf = int(fondo.sum())
    gpt[fondo] = 12.0 + rng.exponential(14.0, (kf, 2))
    geta[fondo] = rng.uniform(-2.5, 2.5, (kf, 2))
    gphi[fondo] = rng.uniform(-np.pi, np.pi, (kf, 2))
    q[fondo] = np.where(rng.uniform(size=(kf, 1)) < 0.65, np.array([[-1, 1]]), rng.choice([-1, 1], (kf, 2)))

    # pile-up: el MC se generó con un perfil distinto al de los datos
    if es_mc:
        lam = np.clip(rng.normal(21.0, 9.0, n), 1.0, None)
    else:
        lam = np.clip(rng.normal(16.0, 5.0, n), 1.0, None)
    npv = rng.poisson(lam).astype(np.int32)
    npv = np.maximum(npv, 1)

    # --- extras: muones falsos o de decaimientos en vuelo (pi/K) ---
    n_extra = rng.poisson(0.25, n)
    kmax = 2 + max(int(n_extra.max()), 1)
    pt = np.zeros((n, kmax)); eta = np.zeros((n, kmax)); ph = np.zeros((n, kmax))
    carga = np.zeros((n, kmax), dtype=np.int32)
    pt[:, :2], eta[:, :2], ph[:, :2], carga[:, :2] = gpt, geta, gphi, q
    hay = np.zeros((n, kmax), dtype=bool)
    hay[:, :2] = True
    tipo = np.zeros((n, kmax), dtype=np.int8)  # 0 = prompt de DY, 1 = fondo no aislado, 2 = extra/falso
    tipo[fondo, :2] = 1
    for j in range(kmax - 2):
        s = n_extra > j
        mm = int(s.sum())
        pt[s, 2 + j] = 4.0 + rng.exponential(6.0, mm)
        eta[s, 2 + j] = rng.uniform(-2.5, 2.5, mm)
        ph[s, 2 + j] = rng.uniform(-np.pi, np.pi, mm)
        carga[s, 2 + j] = rng.choice([-1, 1], mm)
        hay[s, 2 + j] = True
        tipo[s, 2 + j] = 2
    gen_pt, gen_eta, gen_phi = pt.copy(), eta.copy(), ph.copy()

    # --- detector ---
    factor = 1.0 if es_mc else 1.12          # los datos tienen algo peor resolución
    escala = 1.0 if es_mc else 0.9990        # y una pequeña desviación de escala
    pt = escala * pt * (1.0 + _resolucion_relativa(pt, eta, factor) * rng.normal(size=pt.shape))
    reco = hay & (np.abs(eta) < 2.4) & (pt > 3.0) & (rng.uniform(size=hay.shape) < 0.97)

    u = rng.uniform(size=pt.shape)
    eff_tight = 0.980 if es_mc else 0.965
    tight = np.where(tipo == 0, u < eff_tight, np.where(tipo == 1, u < 0.92, u < 0.35))
    iso = np.where(
        tipo == 0,
        rng.exponential(0.020, pt.shape),
        np.where(tipo == 1, rng.exponential(0.45, pt.shape), rng.exponential(0.6, pt.shape)),
    )
    iso = iso + 0.0012 * npv[:, None] * rng.exponential(1.0, pt.shape)  # el pile-up añade energía en el cono
    dxy = np.where(tipo == 0, rng.normal(0, 0.0015, pt.shape), rng.normal(0, 0.04, pt.shape))
    dz = np.where(tipo == 0, rng.normal(0, 0.004, pt.shape), rng.normal(0, 0.08, pt.shape))

    # trigger de doble muon tipo Mu17_Mu8 sobre muones reconstruidos
    pt_trig = np.sort(np.where(reco, pt, 0.0), axis=1)[:, ::-1]
    trig = (pt_trig[:, 0] > 17.0) & (pt_trig[:, 1] > 8.0)
    reco &= trig[:, None]

    cols = {
        "pt": pt, "eta": eta, "phi": ph, "mass": np.full(pt.shape, M_MU), "charge": carga,
        "tightId": tight, "pfRelIso04_all": iso, "dxy": dxy, "dz": dz,
    }

    salida = {"PV_npvsGood": npv}
    if es_mc:
        # GenPart: [0] = Z/gamma*, [1] = mu-, [2] = mu+, después piones del evento subyacente
        n_pi = rng.poisson(3.0, n)
        gp_cols = {}
        npi_max = int(n_pi.max())
        ng = 3 + npi_max
        gp_cols["pt"] = np.zeros((n, ng)); gp_cols["eta"] = np.zeros((n, ng)); gp_cols["phi"] = np.zeros((n, ng))
        gp_cols["mass"] = np.zeros((n, ng)); gp_cols["pdgId"] = np.zeros((n, ng), dtype=np.int32)
        gp_cols["pt"][dy, 0] = pt_z
        gp_cols["eta"][dy, 0] = y  # aproximación: se guarda la rapidez como eta del bosón
        gp_cols["phi"][dy, 0] = phi
        gp_cols["mass"][dy, 0] = m
        gp_cols["pdgId"][:, 0] = 23
        for j in (0, 1):
            gp_cols["pt"][:, 1 + j] = gen_pt[:, j]
            gp_cols["eta"][:, 1 + j] = gen_eta[:, j]
            gp_cols["phi"][:, 1 + j] = gen_phi[:, j]
            gp_cols["mass"][:, 1 + j] = M_MU
            gp_cols["pdgId"][:, 1 + j] = -13 * carga[:, j]  # mu- tiene pdgId = +13
        hay_gp = np.zeros((n, ng), dtype=bool)
        hay_gp[:, :3] = True
        for j in range(npi_max):
            s = n_pi > j
            mm = int(s.sum())
            gp_cols["pt"][s, 3 + j] = rng.exponential(3.0, mm)
            gp_cols["eta"][s, 3 + j] = rng.uniform(-4, 4, mm)
            gp_cols["phi"][s, 3 + j] = rng.uniform(-np.pi, np.pi, mm)
            gp_cols["mass"][s, 3 + j] = 0.13957
            gp_cols["pdgId"][s, 3 + j] = rng.choice([-211, 211], mm)
            hay_gp[s, 3 + j] = True
        # Muon_genPartIdx: los muones duros apuntan a GenPart[1] y [2];
        # los extras (decaimientos en vuelo) a un pion si hay, o -1
        idx = np.full((n, kmax), -1, dtype=np.int32)
        idx[:, 0], idx[:, 1] = 1, 2
        for j in range(kmax - 2):
            idx[:, 2 + j] = np.where(n_pi > j, 3 + j, -1)
        cols["genPartIdx"] = idx
        # GenPart no se reordena: los índices se mantienen
        cuentas_gp = hay_gp.sum(axis=1)
        gen = {c: ak.unflatten(v[hay_gp], cuentas_gp) for c, v in gp_cols.items()}
        salida["GenPart"] = gen
        # pesos de generador estilo NLO: una fracción negativa
        salida["genWeight"] = np.where(rng.uniform(size=n) < 0.16, -1.0, 1.0).astype(np.float32)

    muones, cuentas = _empaquetar(cols, reco)
    guardar = cuentas >= 1
    salida["Muon"] = muones
    out = {}
    for clave, val in salida.items():
        if isinstance(val, dict):
            out[clave] = {c: v[guardar] for c, v in val.items()}
        else:
            out[clave] = val[guardar]
    return out


def generar_nanoaod_2016(ruta, es_mc, n_eventos=400_000, semilla=None, frac_fondo=0.35):
    """Escribe datos (DoubleMuon) o MC (Drell–Yan) 2016 sintéticos en formato NanoAOD."""
    rng = np.random.default_rng(semilla if semilla is not None else (2016 + int(es_mc)))
    bloques = []
    total = 0
    while total < n_eventos:
        b = _bloque_2016(300_000, rng, es_mc, frac_fondo)
        bloques.append(b)
        total += len(b["PV_npvsGood"])

    def unir(clave, sub=None):
        if sub is None:
            return ak.concatenate([ak.Array(b[clave]) for b in bloques])[:n_eventos]
        return ak.concatenate([b[clave][sub] for b in bloques])[:n_eventos]

    tipos_mu = {
        "pt": np.float32, "eta": np.float32, "phi": np.float32, "mass": np.float32,
        "charge": np.int32, "tightId": np.bool_, "pfRelIso04_all": np.float32,
        "dxy": np.float32, "dz": np.float32,
    }
    if es_mc:
        tipos_mu["genPartIdx"] = np.int32
    ramas = {
        "Muon": ak.zip({k: ak.values_astype(unir("Muon", k), t) for k, t in tipos_mu.items()}),
        "PV_npvsGood": ak.to_numpy(unir("PV_npvsGood")).astype(np.int32),
    }
    if es_mc:
        tipos_gp = {"pt": np.float32, "eta": np.float32, "phi": np.float32, "mass": np.float32, "pdgId": np.int32}
        ramas["GenPart"] = ak.zip({k: ak.values_astype(unir("GenPart", k), t) for k, t in tipos_gp.items()})
        ramas["genWeight"] = ak.to_numpy(unir("genWeight")).astype(np.float32)
    return _escribir(ruta, ramas)
