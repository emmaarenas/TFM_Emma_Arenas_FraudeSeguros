# AGENTE IA PREDICTIVO PARA LA DETECCIÓN DE FRAUDE EN RECLAMOS DE SEGUROS DE VEHÍCULOS


Puedes probar la solución en línea a través del siguiente enlace:

[Accede a la solución de detección de fraudes](https://carclaim.streamlit.app/)

## Descripción
Este repositorio contiene el desarrollo de un agente inteligente basado en Inteligencia Artificial (IA) para la detección de fraudes en los reclamos de seguros de vehículos. El proyecto utiliza técnicas de Machine Learning para predecir la probabilidad de fraude en las reclamaciones y optimiza los procesos dentro de las aseguradoras.

![Pipeline Diagram](Assets/diagram.png)

## Contexto y justificación

La industria de los seguros de vehículos enfrenta un desafío creciente con el fraude en las reclamaciones. Estos fraudes representan un alto costo para las aseguradoras, y los métodos tradicionales de detección basados en reglas están quedando obsoletos. Este proyecto propone una solución basada en IA y Machine Learning para detectar fraudes en reclamos de seguros de vehículos, optimizando los procesos operativos y mejorando la precisión de la detección.

## Objetivos

El objetivo principal es desarrollar una herramienta inteligente capaz de detectar fraudes en reclamos de seguros de vehículos de forma rápida, eficaz y comprensible. Los objetivos específicos incluyen:

- Diseño de una arquitectura modular que integre componentes de análisis predictivo, lógica explicativa y presentación visual.
- Desarrollo de un modelo predictivo supervisado para asignar un score de fraude a cada reclamo.
- Implementación de un sistema de clasificación de riesgo para cada caso (bajo, medio, alto).
- Generación de recomendaciones prácticas basadas en reglas de negocio.
- Creación de una interfaz de usuario amigable utilizando Streamlit.
- Despliegue de la solución en la nube para su accesibilidad.

## Metodología
El desarrollo del proyecto se ha seguido con una metodología iterativa y modular, centrada en la integración de datos históricos de reclamaciones, la construcción de un pipeline de procesamiento de datos y la implementación de modelos predictivos avanzados para la clasificación de fraudes. La solución fue validada a través de pruebas con datos simulados para asegurar su robustez y eficiencia.

## Desarrollo de la solución

### Selección y análisis descriptivo de los datos

El conjunto de datos utilizado es el archivo `carclaims.csv`, que contiene 15.420 registros de reclamaciones con 33 variables. Se realizó un análisis exploratorio para identificar inconsistencias y prepararlo para el modelado.

### Preprocesamiento

El preprocesamiento incluye la eliminación de datos erróneos y la transformación de variables. Además, se aplicaron técnicas de balanceo para tratar el desbalance de clases en la variable objetivo (fraude/no fraude).

### Mapeo semántico de variables

Se diseñó un esquema de entrada para la aplicación que traduce las variables del dataset a un formato comprensible para los usuarios, facilitando la interacción a través de un formulario.

### Modelos predictivos

Se probaron diversos algoritmos de Machine Learning, como Random Forest, Logistic Regression, XGBoost y LightGBM, para predecir el fraude en los reclamos. Después de evaluar el rendimiento de cada modelo, se optó por un modelo ensemble para mejorar la precisión y el recall en la detección de fraudes.

### Backend inteligente

El backend gestiona las predicciones y recomendaciones a través de un pipeline de ingeniería de características. También se desarrolló un clasificador de riesgo que evalúa el nivel de riesgo de cada reclamación y genera recomendaciones basadas en reglas de negocio.

### Interfaz de usuario y frontend

La interfaz de usuario fue desarrollada utilizando Streamlit, permitiendo la visualización clara de los resultados y facilitando la interacción con la herramienta. Los usuarios pueden ingresar datos de reclamaciones, recibir predicciones de fraude, ver el nivel de riesgo, obtener recomendaciones, y una explicación en lenguaje natural.

## Despliegue en producción

La solución fue desplegada en la nube utilizando Streamlit Cloud, asegurando su accesibilidad desde cualquier dispositivo sin necesidad de instalación local. 

## Evaluación del sistema

Se realizaron pruebas exhaustivas para evaluar la precisión del modelo, su capacidad para manejar errores y la eficiencia de la interfaz. El sistema muestra un rendimiento destacado en la clasificación de fraudes, con un buen balance entre precisión y recall.

## Conclusiones

La implementación de IA para la detección de fraudes en reclamos de seguros de vehículos muestra un gran potencial para mejorar la eficiencia operativa de las aseguradoras. El modelo desarrollado permite detectar fraudes con alta precisión y proporcionar recomendaciones útiles para la toma de decisiones.

## Fuente de los datos

- [Kaggle: Car Claims Dataset](https://www.kaggle.com/datasets/khusheekapoor/vehicle-insurance-fraud-detection)

## Instalación

1. Clona este repositorio en tu máquina local:
    ```bash
    git clone https://github.com/emmaarenas/TFM_FraudeSeguros.git
    ```

2. Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```

3. Ejecuta la aplicación:
    ```bash
    streamlit run app.py
    ```

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
