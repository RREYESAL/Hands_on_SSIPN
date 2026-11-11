# Mes 1: Fundamentos y CMS Open Data

Al final del mes 1 reconstruyes tú solo el espectro de masa invariante μ⁺μ⁻ con CMS Open Data, identificas las resonancias y comparas datos con simulación. Todo corre en una laptop con conda o en Google Colab, sin cuentas de CERN.

## Resumen del mes

El mes tiene 5 semanas (0 a 4) de unas 20 h cada una. Cada ejercicio trae una **verificación**: una condición numérica que compruebas con un `assert` antes de abrir el PR. Las celdas de verificación ya están escritas en los notebooks: no las borres ni las relajes. Si una verificación falla, primero intenta corregirlo tú; pregunta al supervisor solo si sigue fallando después de anotarlo en la bitácora.

| Semana | Tema | Entregable |
| --- | --- | --- |
| 0 | Entorno y repositorio | Entorno que instala sin errores y `00_entorno_y_contexto.ipynb` (parte E0) |
| 1 | Contexto físico y git | `bitacora.md` con resumen de lecturas, `docs/contexto.md` y primer PR |
| 2 | Leer NanoAOD con uproot y awkward | `notebooks/mes1/01_intro_uproot.ipynb` |
| 3 | Masa invariante | `notebooks/mes1/02_masa_invariante.ipynb` |
| 4 | Selecciones y datos vs MC | `notebooks/mes1/03_seleccion.ipynb` + presentación de 10 min |

**Reglas fijas del mes**

- Ritmo: lunes PR + bitácora, martes revisión asíncrona, miércoles reunión de 30 min.
- Una rama por semana (`semana-02-uproot`) y un PR por entregable. Notebooks con salidas limpias; nunca subir archivos `.root`.
- Toda función usada en dos notebooks se mueve a `src/hepss/`.
- La bitácora tiene siempre tres apartados: *qué hice*, *qué no entendí*, *qué sigue*. Una duda sin anotar en la bitácora no se responde en la reunión.

**Datos (sin cuentas de CERN)**

- Semanas 2 y 3: archivo educativo de CMS Open Data *DoubleMuParked 2012 en NanoAOD reducido* (`Run2012BC_DoubleMuParked_Muons.root`, unos 61 millones de eventos, ramas `nMuon`, `Muon_pt`, `Muon_eta`, `Muon_phi`, `Muon_mass`, `Muon_charge`). Se lee por streaming HTTPS desde `https://opendata.cern.ch/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/` (en laptop también sirve XRootD); para desarrollar basta con `entry_stop=2_000_000`.
- Semana 4: un archivo de datos `DoubleMuon` 2016 y uno de MC Drell–Yan (`DYJetsToLL_M-50`) en NanoAOD completo de Open Data, que sí traen identificación, aislamiento y *truth information*. Las rutas van en `configs/datos.yaml`.
- Si no hay red estable: `hepss.io.abrir_events` genera automáticamente datos sintéticos con las mismas ramas (`src/hepss/sintetico.py`) y avisa con un warning. Las gráficas hechas con ellos llevan la etiqueta *Simulación sintética*. Para forzarlo, define la variable de entorno `HEPSS_SINTETICO=1`.

## Semanas 0 y 1: entorno, git y contexto físico

Al cerrar la semana 1 tienes un repositorio que cualquiera puede instalar desde cero y entiendes qué se mide en el análisis de Bs.

**Semana 0: entorno y repositorio**

Hay dos rutas equivalentes: **A, laptop con conda** y **B, Google Colab** (si no tienes computadora propia). Elige una en la semana 0 y anótala en el README; los ejercicios y las verificaciones son los mismos en ambas. Las dos usan GitHub.

| Ejercicio | Ruta A: laptop con conda | Ruta B: Google Colab | Verificación |
| --- | --- | --- | --- |
| E0.1 Repositorio | Clonar este repositorio (o tu fork, según acuerdes con tu supervisor) y revisar que tenga la estructura del programa | Lo mismo desde la web de GitHub; poner la URL en `REPO_URL` de la primera celda de cada notebook | La celda de E0.1 pasa |
| E0.2 Entorno | Instalar Miniforge y `conda env create -f environment.yml` | Primera celda de cada notebook: instala las librerías con pip; reiniciar la sesión si Colab lo pide | `import uproot, awkward, vector, hist, mplhep, zfit, xgboost` sin errores |
| E0.3 Paquete `hepss` | `pip install -e .` dentro del entorno (ya incluido en `environment.yml`) | La celda de configuración clona el repo y añade `src/` a `sys.path` | `import hepss` funciona en una sesión nueva |
| E0.4 Notebooks limpios | `nbstripout --install` en el repo, commit y push desde terminal | *Editar → Borrar todas las salidas* y *Archivo → Guardar una copia en GitHub* en una rama nueva | El commit aparece en la rama, sin salidas |
| E0.5 Resultados intermedios | Guardar histogramas (`.pkl` o `.npz`) en `data/` | Montar Google Drive y guardarlos ahí | Recuperas un histograma guardado sin volver a leer datos |
| E0.6 Bitácora | Primera entrada de `bitacora.md` | Igual, editando en la web de GitHub | Tiene los tres apartados fijos |

Notas para la ruta B: la sesión de Colab se borra tras un rato inactiva o tras varias horas, así que todo lo que importe vive en GitHub o en Drive. Si hace falta un token de GitHub, va en *Secretos* de Colab (ícono de llave), nunca en el notebook. Los archivos de `src/hepss/` se editan en la web de GitHub o con `!git` desde el notebook.

El repositorio incluye `environment.yml` y `requirements.txt` con la misma lista de librerías, para que el código de una ruta corra en la otra.

**Semana 1: git y contexto físico**

Lecturas (unas 8 h en total):

1. [HSF Training](https://hsf-training.org): módulos de *Unix shell* y *Version control with git* (ramas, PR, conflictos).
2. [PDG](https://pdg.lbl.gov): ficha del Bs⁰ (masa, vida media, modos J/ψφ y μ⁺μ⁻) y ficha del J/ψ.
3. Descripción del detector CMS en la página pública de CMS: tracker, calorímetros, imán de 3.8 T, cámaras de muones, sistema de trigger.
4. [Scikit-HEP](https://scikit-hep.org): *getting started* de uproot y awkward.

| Ejercicio | Qué hacer | Verificación |
| --- | --- | --- |
| E1.1 | Crear la rama `semana-01-contexto`, modificar el README (ruta elegida, cómo instalar) y abrir un PR | El PR existe y tiene descripción |
| E1.2 | Provocar y resolver a propósito un conflicto de merge en una rama de prueba | Lo describes en la bitácora con los comandos usados |
| E1.3 | Escribir en `docs/contexto.md` (máximo una página): qué es un mesón Bs, por qué se estudian Bs→J/ψφ y Bs→μ⁺μ⁻, y por qué el J/ψ se reconstruye con dos muones | Contiene masa y vida media del Bs con fuente (PDG) |
| E1.4 | Dibujar a mano o en texto la secuencia detector → trigger → reconstrucción → NanoAOD → notebook | Cada paso tiene una frase sobre qué información se pierde o se gana |
| E1.5 | Calcular la distancia media de vuelo de un Bs con pT = 10 GeV (usar cτ del PDG y βγ = p/m) | Resultado del orden de 1 mm; explicas por qué eso permite separar señal de fondo |

## Semana 2: leer NanoAOD con uproot y awkward

El entregable es `01_intro_uproot.ipynb` con las distribuciones de pT, η, φ y número de muones del archivo DoubleMuParked 2012, con estilo CMS de `mplhep`.

Lecturas: tutorial de uproot (abrir archivos, `arrays`, `iterate`) y de awkward (arreglos irregulares, máscaras, `ak.num`, `ak.flatten`).

| Ejercicio | Qué hacer | Verificación |
| --- | --- | --- |
| E2.1 | Abrir el archivo, listar ramas y tipos con `tree.show()` | Encuentras las 6 ramas de muones; con Open Data, `tree.num_entries` cerca de 61.5 millones |
| E2.2 | Leer las ramas de muones en un `ak.Array` con `entry_stop=2_000_000` | `ak.all(ak.num(events.Muon_pt) == events.nMuon)` es `True` |
| E2.3 | Histograma de `nMuon` con `hist` | La mayoría de los eventos tiene 2 o más muones; explicas por qué aun así hay eventos con 1 muon si el dataset viene de un trigger de doble muon |
| E2.4 | Histogramas de pT (escala log en y), η y φ de todos los muones con `ak.flatten` | El número de entradas es el número total de muones |
| E2.5 | Lo mismo pero solo para el muon de mayor pT de cada evento (`ak.argmax` con `keepdims=True`) | Con ambas distribuciones normalizadas a 1, la del muon líder está por encima en pT alto |
| E2.6 | Medir cuánto tarda y cuánta memoria usa leer 2 M eventos; leer por bloques con `uproot.iterate` llenando el mismo histograma | El histograma por bloques tiene el mismo contenido que uno hecho de golpe sobre los mismos eventos |
| E2.7 | Mover a `src/hepss/io.py` la función `leer_muones(ruta, n_eventos)` y a `src/hepss/graficas.py` la función `hist_cms` de histograma con estilo CMS | El notebook importa ambas funciones desde `hepss` |

Pregunta para la bitácora: ¿por qué la distribución en η no es plana y la de φ sí?

## Semana 3: masa invariante de dimuones

El entregable es `02_masa_invariante.ipynb`: el espectro μ⁺μ⁻ de 0.25 a 150 GeV en escala log-log, con las resonancias marcadas y sus picos medidos.

Lecturas: capítulo de cinemática del PDG (masa invariante, rapidez, pseudorrapidez) y documentación de `vector` para awkward.

La masa invariante de dos muones es:

```latex
m_{\mu\mu}^2 = (E_1 + E_2)^2 - |\vec p_1 + \vec p_2|^2 \approx 2\, p_{T1}\, p_{T2}\, [\cosh(\eta_1 - \eta_2) - \cos(\phi_1 - \phi_2)]
```

La aproximación de la derecha desprecia la masa del muon.

| Ejercicio | Qué hacer | Verificación |
| --- | --- | --- |
| E3.1 | Seleccionar eventos con exactamente 2 muones de carga opuesta | La fracción de eventos que pasan está anotada; ningún par seleccionado tiene `Muon_charge` con suma ≠ 0 |
| E3.2 | Calcular mμμ a mano con la fórmula sin masa (en `hepss.cinematica.masa_sin_masa`) | Para un evento de prueba con pT = (10, 10) GeV, Δη = 0, Δφ = π el resultado es 20 GeV |
| E3.3 | Calcular mμμ con `vector` (`pt`, `eta`, `phi`, `mass`) sumando los cuadrivectores | Coincide con E3.2 a mejor que 0.1 % en al menos el 99 % de los pares con mμμ > 5 GeV; explicas en la bitácora por qué no en todos |
| E3.4 | Graficar la diferencia relativa entre E3.2 y E3.3 en función de mμμ | Explicas por qué la diferencia crece cerca de 2mμ = 0.211 GeV |
| E3.5 | Histograma de mμμ con bins logarítmicos (`hist.axis.Regular(..., transform=hist.axis.transform.log)`) y escala log en ambos ejes | Se ven al menos 7 picos |
| E3.6 | Marcar η, ρ/ω, φ, J/ψ, ψ(2S), Υ(1S,2S,3S) y Z con sus masas del PDG | Cada etiqueta cae sobre un pico |
| E3.7 | Medir la posición del pico de J/ψ, Υ(1S) y Z como el bin máximo en una ventana fina | J/ψ en 3.097 ± 0.01 GeV, Υ(1S) en 9.46 ± 0.05 GeV, Z en 91.2 ± 0.5 GeV |
| E3.8 | Repetir el espectro de J/ψ (2.8 a 3.4 GeV) separando pares con ambos muones en el barril (\|η\| < 0.9) y ambos en el endcap (\|η\| > 1.2); estimar la anchura de cada pico | La anchura en el endcap es mayor que en el barril |

Preguntas para la bitácora: ¿por qué el fondo cae con la masa? ¿Por qué el Υ(1S), Υ(2S) y Υ(3S) se ven como picos separados y no un solo bulto?

## Semana 4: selecciones y datos vs MC

El entregable es `03_seleccion.ipynb` con una tabla de cortes (*cutflow*), la comparación normalizada datos/MC en el pico del Z y una presentación de 10 min al supervisor.

Se usa NanoAOD completo de 2016 porque el archivo de 2012 no trae variables de calidad ni información de verdad. Los cortes van en `configs/seleccion_z.yaml`, no en el código.

| Ejercicio | Qué hacer | Verificación |
| --- | --- | --- |
| E4.1 | Leer de datos y de MC solo las ramas necesarias: `Muon_pt`, `eta`, `phi`, `mass`, `charge`, `tightId`, `pfRelIso04_all`, `dxy`, `dz` y `PV_npvsGood` | La lista de ramas vive en el YAML |
| E4.2 | Aplicar en orden: pT > 25 GeV, \|η\| < 2.4, `tightId`, aislamiento relativo `pfRelIso04_all` < 0.15, \|dxy\| < 0.2 cm, \|dz\| < 0.5 cm; después exactamente 2 muones de carga opuesta y 70 < mμμ < 110 GeV. Implementar `hepss.seleccion.aplicar_seleccion` | El *cutflow* es reproducible desde el YAML y el número de eventos nunca aumenta |
| E4.3 | Graficar mμμ, pT y η del muon líder antes y después de cada corte | Explicas cuál corte quita más fondo y cuál quita más señal |
| E4.4 | Comparar datos y MC normalizados al mismo área, con panel de cociente datos/MC (`mplhep.histplot` + subplot) | Barras de error estadístico en datos y en el cociente; el cociente en el pico es compatible con 1 dentro de unos pocos % |
| E4.5 | Comparar `PV_npvsGood` en datos y MC | Encuentras la diferencia y la anotas como efecto de *pile-up* no corregido |
| E4.6 | En MC, asociar cada muon reconstruido con su partícula generada (`Muon_genPartIdx`, `GenPart_pdgId` = ±13) | Fracción de muones seleccionados con un muon generado asociado mayor que 95 % |
| E4.7 | En MC, histograma de m(reco) − m(gen) para pares en barril (\|η\| < 0.9) y en endcap (\|η\| > 1.2) | La resolución en el endcap es peor que en el barril |
| E4.8 | Preparar 4 o 5 diapositivas: datos usados, cortes, cutflow, comparación datos/MC, una conclusión | Presentas en 10 min sin leer las diapositivas |

Antes de empezar la semana 4 el supervisor elige un archivo de cada muestra en [CMS Open Data](https://opendata.cern.ch) (búsqueda: `DoubleMuon Run2016` y `DYJetsToLL_M-50 NanoAODv9`) y pone las rutas en `configs/datos.yaml`. Leer uno solo con `entry_stop` es suficiente. Mientras no estén, el notebook usa el respaldo sintético.

## Punto de control y preguntas del mes

Pasas al mes 2 si el espectro μμ de E3.5 a E3.7 es correcto, el cutflow de E4.2 es reproducible desde el YAML y respondes bien al menos 6 de estas 8 preguntas en la reunión de la semana 4. Si no, se toma una semana de refuerzo.

1. ¿Por qué se usa escala logarítmica en el espectro μμ?
2. ¿Qué diferencia hay entre datos y MC, y qué es la *truth information*?
3. ¿Por qué la resolución de masa depende de la región de η?
4. ¿Qué es la pseudorrapidez y por qué se usa en lugar del ángulo polar?
5. ¿Por qué se piden muones de carga opuesta? ¿Para qué sirven los pares de la misma carga?
6. ¿Qué sesgo introduce el trigger en el espectro de masa a bajo pT?
7. ¿Por qué se normalizan datos y MC al mismo área y qué información se pierde al hacerlo?
8. ¿Qué es el *pile-up* y por qué hace falta repesar el MC?
