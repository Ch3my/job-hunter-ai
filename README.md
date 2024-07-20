# Job Hunter #
Utilizando la API de rapidapi obtiene una lista de trabajos segun la descripcion en `config.json`

## Funcionamiento ##
Utilizamos OpenAI, por lo tanto debes tener la `OPENAI_API_KEY` definida en el entorno.

Por medio de RapidAPI se obtiene un listado de 25 trabajos, cada trabajo se evalua con AI para saber si es `relevante` o `no-relevante`

Luego, todos los trabajos `relevantes` se guardan en una base de datos Sqlite donde puedes marcarlos para saber cuales ya aplicaste y cuales no.

La clave de los registros es el cargo y la empresa, si encuentra el mismo trabajo en una busqueda futura no lo guarda (no lo duplica)

## Configurar la AI para que determine si es relevante o no ##
La AI identifica si la oferta de trabajo es relevante para ti basado en tus calificaciones y experiencia, para que revises las ofertas que esten mas acorde a tu perfil.

Esto se hace por medio del archivo `prompt.txt` (debes crearlo) que puede tener algo como lo siguiente:

```
Soy un contador en busca de trabajo, debes evaluar si el trabajo se ajusta a mis habilidades y requerimientos.

Mis habilidades son: contabilidad general, auditoría, análisis financiero, preparación de impuestos, contabilidad de costos, contabilidad de gestión, manejo de software contable (como QuickBooks y SAP), conciliaciones bancarias, gestión de presupuestos, informes financieros, cumplimiento normativo y asesoría fiscal.
```

## Entorno virtual ##

Crear entorno

`python -m venv .venv`

Activar entorno

`.venv\Script\Activate`

Luego instalar paquetes dentro del entorno

## Instalar dependencias ##
`pip install pyinstaller langchain-openai langchain langchain-core`

## Compilar a ejecutable ##
```
pyinstaller -n "Job Hunter" --collect-all langchain --noconfirm --windowed --icon=assets/favicon.ico main.py
```
