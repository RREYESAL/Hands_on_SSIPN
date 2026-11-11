# Servicio social: análisis de datos y ML en física de altas energías

Repositorio de trabajo del servicio social (6 meses, unas 20 h/semana) en el grupo de física de altas energías experimental (CMS, análisis de decaimientos de mesones Bs). Todo el trabajo es en Python con el ecosistema [Scikit-HEP](https://scikit-hep.org) y corre con CMS Open Data o con datos sintéticos, sin cuentas de CERN.

| Mes | Tema | Programa |
| --- | --- | --- |
| 1 | Fundamentos y CMS Open Data: uproot, awkward, masa invariante, selecciones | [docs/programa_mes1.md](docs/programa_mes1.md) |
| 2 | Estadística y ajustes con zfit: χ² vs verosimilitud, ajustes extendidos, toys | por publicar |
| 3 | Machine learning: BDT con XGBoost, validación, corte óptimo | por publicar |
| 4–5 | Proyecto dentro del análisis del grupo | por definir con el supervisor |
| 6 | Cierre, documentación e informe final | por definir |

## Cómo instalar

Hay dos rutas equivalentes. Elige una en la semana 0 y anótala aquí abajo.

**Ruta A: laptop con conda**

```bash
# 1. Instalar Miniforge: https://github.com/conda-forge/miniforge
git clone https://github.com/RREYESAL/Hands_on_SSIPN.git
cd Hands_on_SSIPN
conda env create -f environment.yml     # crea el entorno hep-ss e instala hepss con pip install -e .
conda activate hep-ss
nbstripout --install                    # quita las salidas de los notebooks al hacer commit
jupyter lab
```

**Ruta B: Google Colab**

Abre un notebook de `notebooks/mes1/` en Colab (*Archivo → Abrir cuaderno → GitHub*) y corre la primera celda: instala las librerías, clona el repositorio y deja `hepss` importable. Si trabajas en un fork, cambia `REPO_URL` en esa celda por la URL de tu fork.

Ruta elegida: _(completar en la semana 0)_

## Cómo trabajar

1. Cada semana, crea una rama (`semana-02-uproot`) desde `main`.
2. Abre el notebook de la semana y completa las celdas marcadas con `# TODO`. Las celdas de **verificación** (con `assert`) ya están escritas: no las borres ni cambies las tolerancias.
3. Si una verificación falla, intenta corregirlo tú primero. Si sigue fallando, anótalo en `bitacora.md` en *qué no entendí*.
4. El lunes: commit con las salidas limpias, push y PR hacia `main`, y entrada nueva en `bitacora.md`.
5. Cuando una función se usa en dos notebooks, se mueve a `src/hepss/`. Algunas ya tienen un esqueleto con su especificación (`raise NotImplementedError`): impleméntalas cuando el programa lo pida.

## Datos

`hepss.io.abrir_events` intenta leer CMS Open Data por HTTPS (y por XRootD si `fsspec-xrootd` está instalado). Si no puede (sin red, servidor caído, rutas sin configurar), genera una vez un archivo sintético en `data/` con las mismas ramas, avisa con un warning y las gráficas llevan la etiqueta *Simulación sintética*. Para forzar los datos sintéticos: `HEPSS_SINTETICO=1`.

Las rutas de las muestras están en `configs/datos.yaml`. Nunca se suben datos ni archivos `.root` al repositorio.

## Estructura

```text
├── README.md            # este archivo
├── environment.yml      # ruta A (conda)
├── requirements.txt     # ruta B (Colab), mismas librerías
├── pyproject.toml       # hace instalable el paquete hepss
├── bitacora.md          # entrada semanal
├── docs/                # programa de cada mes y textos (contexto.md, ...)
├── notebooks/
│   ├── mes1/            # 00_entorno_y_contexto, 01_intro_uproot, 02_masa_invariante, 03_seleccion
│   ├── mes2/
│   └── mes3/
├── src/hepss/           # funciones reutilizables (lectura, cinemática, selección, gráficas)
├── configs/             # cortes y rutas en YAML, no en el código
├── data/                # ignorado por git
└── plots/               # ignorado por git
```

## Reglas de git

- Una rama por tarea semanal y un *pull request* para la revisión.
- Nunca subir datos ni archivos ROOT; sí subir notebooks con las salidas limpias.
- Nada de rutas absolutas de tu computadora en el código.
