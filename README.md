# ALEPH

Superposición transparente de guías de composición en la pantalla. Útil
para el análisis y estudio de la fotografía cinematográfica viendo
películas, series y anime.

![Captura de la app](docs/screenshot.png)

## CARACTERÍSTICAS

- Pool con 11 guías preestablecidas: regla de tercios, triángulos áureos,
  espirales de Fibonacci, centro, diagonales y rejilla áurea (Phi Grid).
  Incluye un espacio vacío para trabajar solo con las reglas propias.

- Definición de reglas personalizadas por el usuario.

- Modo pasivo (click-through): la ventana deja de capturar el ratón y
  los clics pasan al contenido de abajo.

- Ventana redimensionable, para ajustar los marcos a diferentes
  resoluciones.

- Captura de pantalla limpia con las guías y reglas superpuestas.

- Acceso directo en el Escritorio y registro en el menú de aplicaciones
  en la primera ejecución.

## GALERÍA

Las guías de Aleph sobre una película, en modo pasivo: la overlay no
intercepta el ratón ni las teclas, así que la película sigue siendo lo
que estás mirando.

<table>
  <tr>
    <td width="50%"><a href="docs/aleph-01.jpg"><img src="docs/aleph-01.jpg" alt="Aleph sobre una película, muestra 1"></a></td>
    <td width="50%"><a href="docs/aleph-02.jpg"><img src="docs/aleph-02.jpg" alt="Aleph sobre una película, muestra 2"></a></td>
  </tr>
  <tr>
    <td width="50%"><a href="docs/aleph-03.jpg"><img src="docs/aleph-03.jpg" alt="Aleph sobre una película, muestra 3"></a></td>
    <td width="50%"><a href="docs/aleph-04.jpg"><img src="docs/aleph-04.jpg" alt="Aleph sobre una película, muestra 4"></a></td>
  </tr>
  <tr>
    <td width="50%"><a href="docs/aleph-05.jpg"><img src="docs/aleph-05.jpg" alt="Aleph sobre una película, muestra 5"></a></td>
    <td width="50%"><a href="docs/aleph-06.jpg"><img src="docs/aleph-06.jpg" alt="Aleph sobre una película, muestra 6"></a></td>
  </tr>
  <tr>
    <td width="50%"><a href="docs/aleph-07.jpg"><img src="docs/aleph-07.jpg" alt="Aleph sobre una película, muestra 7"></a></td>
    <td width="50%"><a href="docs/aleph-08.jpg"><img src="docs/aleph-08.jpg" alt="Aleph sobre una película, muestra 8"></a></td>
  </tr>
  <tr>
    <td width="50%"><a href="docs/aleph-09.jpg"><img src="docs/aleph-09.jpg" alt="Aleph sobre una película, muestra 9"></a></td>
    <td width="50%"><a href="docs/aleph-10.jpg"><img src="docs/aleph-10.jpg" alt="Aleph sobre una película, muestra 10"></a></td>
  </tr>
</table>

## INSTALACIÓN

### Binarios (sin Python)

Descargá el binario de tu sistema desde la pestaña Releases del
repositorio:

<https://github.com/LucasLassa/aleph/releases>

- Linux x86_64
- Windows x86_64
- macOS arm64

En Linux, dale permisos de ejecución con `chmod +x`.
En macOS sin firmar, hacé clic derecho → Abrir (Gatekeeper).
En Windows, "Ejecutar de todas formas" (SmartScreen).

### Desde el código

Requisitos:

- Python ≥ 3.11
- PySide6 ≥ 6.5

Instalación recomendada (venv):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
aleph
```

En entornos con PEP 668, si preferís instalar en el usuario:

```bash
pip install --user --break-system-packages -e .[dev]
aleph
```

También podés correrlo sin instalar:

```bash
python -m src.main
```

## USO RÁPIDO

La ventana se abre a pantalla completa, adaptada al monitor, con el
marco activo.

### Atajos

| Tecla | Acción |
|---|---|
| `←` / `→` | Guía anterior / siguiente |
| `↑` / `↓` | Subir / bajar opacidad (pasos de 0.05) |
| `Shift + M` | Alternar modo marco (edición ↔ pasivo) |
| `Shift + D` | Borrar las reglas propias |
| `Shift + S` | Captura de pantalla con las líneas |
| `Shift + C` | Alternar color de las líneas (blanco / negro) |
| `Esc` | Cerrar la aplicación |
| `Tab` | Abrir / cerrar el panel |
| `Shift + clic izq.` | Colocar / mover una regla propia |

Las teclas se configuran en `src/core/keymap.py`.

### Panel lateral

Con el marco activo, se muestra un panel a la derecha que se despliega,
organizado en secciones:

- **Reglas**: guía anterior/posterior, opacidad y color de las líneas.
- **Dibujo**: botones para crear reglas propias (rectas, diagonales
  y vértices).
- **Listo para ver**: modo visualización (pasivo) y borrar las líneas
  propias.
- **Opciones**: captura de pantalla, carpeta de guardado y manual de uso.
- **Apoya nuestra app**: link de donación, CVU y alias (al portapapeles).

### Modo pasivo

Con `Shift + M` (o el botón "Modo visualización") la overlay quita todo el
cromo y deja solo las guías. Abajo a la derecha aparece un botón "Volver
al modo edición".

Los atajos con Shift siguen funcionando con el marco OFF. El teclado
también responde sin botones visibles: `←` `→`, `↑` `↓`, `Shift + M`,
`Shift + C` y `Esc`.

## REGLAS PROPIAS

Además de las guías preestablecidas, podés crear líneas de composición a
medida. Los botones del panel se agrupan en rectas (horizontal y
vertical), diagonales (ascendente y descendente), vértices (cuatro
esquinas) y el punto de fuga.

### Punto de fuga (◇ Fuga)

El botón "◇ Fuga" crea un punto de fuga de perspectiva: 16 líneas que
van de 5 anclajes por cara de la pantalla (puntas, mitad y medios entre
mitad y punta) hasta el vértice elegido, más un punto marcador en el
vértice. Se coloca igual que las demás reglas: botón → `Shift` + clic y
arrastrar → soltar `Shift`.

### Cómo se colocan

1. Pulsá el botón del tipo de regla que quieras.
2. Mantené `Shift` y arrastrá con clic izquierdo hasta donde quieras el
   vértice.
3. Al soltar `Shift`, la regla queda fija.

### Cómo se borran

`Shift + D` (o el botón "Borrar mis líneas dibujadas" del panel)
borra todas las reglas propias.

### Espacio vacío

La guía "Espacio vacío" no dibuja ninguna línea preestablecida: queda
el lienzo limpio. Es útil para usar solo tus reglas.

## CAPTURAS DE PANTALLA

`Shift + S` (o el botón "Capturar") guarda una foto con la guía activa y
las reglas superpuestas.

- Se guarda en Descargas, o en la carpeta elegida con "Guardar en".
- Nombres: `aleph-AAAAMMDD-HHMMSS.png`.

## REDIMENSIONAR LA VENTANA

La app arranca siempre en pantalla completa. El redimensionamiento manual
con tiradores en las esquinas queda reservado para futuras versiones; por
ahora la ventana cubre el monitor completo.

## CONFIGURACIÓN

La configuración se guarda en
`~/.config/aleph/config.json` al cerrar la app: opacidad,
color de líneas y carpeta de capturas.

No se persisten el modo marco, la guía activa, el modo fullscreen ni las
reglas. La app arranca siempre con marco ON, en la regla de tercios y a
pantalla completa.

## DESARROLLO

```bash
pip install -e .[dev]
python -m pytest
ruff check src tests
```

Para generar los binarios:

```bash
pip install -e .[dev]
pyinstaller aleph.spec
# Linux/Windows: dist/aleph(.exe)    [onefile]
# macOS:         dist/aleph.app       [onedir + bundle]
```

Estructura:

```
src/
├── main.py              # punto de entrada
├── app.py               # config + estado + plataforma + ventana
├── ui/                  # ventana, paintEvent, íconos
├── core/                # estado, guías, reglas, captura, keymap
├── platform/            # backends por SO (Qt genérico, Wayland)
├── config/              # defaults + load/save
└── utils/               # logger, geometría (Fibonacci, perpendicular)
```

