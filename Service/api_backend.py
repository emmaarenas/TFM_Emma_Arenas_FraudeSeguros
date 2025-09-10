# Librerías a utilizar
import json
import pickle
import joblib
import numpy as np
import pandas as pd
import shap
import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv
# Carga las variables de entorno
load_dotenv()

# Rutas de Artifacts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, '../Artifacts')

# Carga de modelos
def load_models():
    models = {}
    models['logreg'] = joblib.load(os.path.join(ARTIFACTS_DIR, 'model_logreg.pkl'))
    models['rf'] = joblib.load(os.path.join(ARTIFACTS_DIR, 'model_rf.pkl'))
    models['xgb'] = joblib.load(os.path.join(ARTIFACTS_DIR, 'model_xgb.pkl'))
    models['lgbm'] = joblib.load(os.path.join(ARTIFACTS_DIR, 'model_lgbm.pkl'))
    return models

# Configuración del ensemble
def load_ensemble_config():
    with open(os.path.join(ARTIFACTS_DIR, 'ensemble_config.json'), 'r') as f:
        config = json.load(f)
    return config

# Carga del esquema de entrada y salida (io_schema)
def load_io_schema():
    with open(os.path.join(ARTIFACTS_DIR, 'io_schema.json'), 'r') as f:
        schema = json.load(f)
    return schema

# Carga del archivo feature_cols.pkl para obtener las columnas que el modelo espera
def load_feature_cols():
    with open(os.path.join(ARTIFACTS_DIR, 'feature_cols.pkl'), 'rb') as f:
        feature_cols = pickle.load(f)
    return feature_cols

# Preprocesamiento de datos según el io_schema
def preprocess_data(data, schema, feature_cols):
    col_map = [
    {'PastNumberOfClaims': {'none': 0, '1': 1, '2 to 4': 3, 'more than 4': 5}},
    {'AgeOfPolicyHolder': {'16 to 17': 16.5, '18 to 20': 19, '21 to 25': 23, '26 to 30': 28, '31 to 35': 33, '36 to 40': 38, '41 to 50': 45.5, '51 to 65': 58, 'over 65': 66}},
    {'NumberOfSuppliments': {'none': 0, '1 to 2': 1.5, '3 to 5': 4, 'more than 5': 6}},
    {'VehiclePrice': {'20000 to 29000': 24500, '30000 to 39000': 34500, '40000 to 59000': 49500, '60000 to 69000': 64500, 'less than 20000': 15000, 'more than 69000': 70000}},
    {'Days_Policy_Accident': {'none': 0, '1 to 7': 4, '8 to 15': 11.5, '15 to 30': 22.5, 'more than 30': 35}},
    {'Days_Policy_Claim': {'none': 0, '8 to 15': 11.5, '15 to 30': 22.5, 'more than 30': 35}},
    {'NumberOfCars': {'1 vehicle': 1, '2 vehicles': 2, '3 to 4': 3.5, '5 to 8': 6.5, 'more than 8': 9}} ]
    # Renombrado de columnas según esquema
    rename_map = {}
    for feature, info in schema.items():
        if 'original' in info:
            rename_map[feature] = info['original']
    data.rename(columns=rename_map, inplace=True)
    renamed_schema = {}
    for feature, info in schema.items():
        if 'original' in info:
            renamed_schema[rename_map.get(feature, feature)] = info
    # Iteración sobre cada columna del esquema para aplicar transformaciones
    for feature, info in renamed_schema.items():
        print(f"Procesando la columna: {feature}, tipo en esquema: {info['type']}")
        # FECHAS
        if info['type'] == 'date':
            data[feature] = pd.to_datetime(data[feature], format='%d/%m/%Y')
        # CATEGÓRICAS
        elif info['type'] == 'categorical':
            data[feature] = data[feature].map(info['options'])
        # NUMÉRICAS
        elif info['type'] == 'numeric':
            data[feature] = pd.to_numeric(data[feature], errors='coerce')
            # Aproximación a la media si la variable estaba en rangos
            for col_dict in col_map:
                if feature in col_dict:
                    mapping_values = list(col_dict[feature].values())
                    # Conversión EUR → USD para el precio del vehículo
                    eur_to_usd = 1 / 0.86 
                    if feature == 'VehiclePrice':
                        data[feature] = data[feature] * eur_to_usd
                    # Redondeo al más próximo
                    def round_to_closest(value):
                        arr = np.array(mapping_values)
                        idx = (np.abs(arr - value)).argmin()
                        return arr[idx]
                    data[feature] = data[feature].apply(round_to_closest)
        # DERIVADAS
        elif info.get('derived', False) or str(info['type']).lower() in ['derived', 'derived_numeric']:
            sources = info['from']
            if len(sources) == 1:
                col_source = rename_map.get(sources[0], sources[0])
                if col_source not in data.columns:
                    raise KeyError(f"Columna fuente '{col_source}' no encontrada en el DataFrame")
                data[col_source] = pd.to_datetime(data[col_source], errors='coerce')
                if 'options' in info:
                    if 'month' in feature.lower():
                        data[feature] = data[col_source].dt.strftime('%b').map(info['options'])
                    elif 'dayofweek' in feature.lower():
                        data[feature] = data[col_source].dt.day_name().map(info['options'])
                else:
                    # WeekOfMonth
                    data[feature] = ((data[col_source].dt.day - 1) // 7 + 1).astype(int)
            elif len(sources) == 2:  
                col1, col2 = sources
                if col1 not in data.columns or col2 not in data.columns:
                    print("Columnas fuente que faltan:", col1, col2)
                    continue 
                data[col1] = pd.to_datetime(data[col1], format="%d/%m/%Y", errors="coerce", dayfirst=True)
                data[col2] = pd.to_datetime(data[col2], format="%d/%m/%Y", errors="coerce", dayfirst=True)
                data[feature] = (data[col2] - data[col1]).dt.days
    print(f"Columnas en los datos: {data.columns}")
    missing_cols = [col for col in feature_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Faltan columnas requeridas: {missing_cols}")
    else:
        data = data[feature_cols]
        return data

# Clasificador de riesgo
def clasificar_riesgo(score, threshold):
    if score < threshold:
        return 'Bajo riesgo'
    elif score < threshold + 0.1:
        return 'Riesgo medio'
    else:
        return 'Alto riesgo'

# Generador de recomendaciones
def generar_recomendaciones(data):
    recomendaciones = []
    for idx, row in data.iterrows():
        fila = []
        if row.get('NumberOfSuppliments', 0) > 0:
            fila.append("Consultar los documentos suplementarios adjuntos al reclamo.")
        if row.get('WitnessPresent', 0) == 1:
            fila.append("Solicitar testimonio o contacto del testigo.")
        if row.get('PoliceReportFiled', 0) == 1:
            fila.append("Revisar el informe policial relacionado con el accidente.")
        fila.append("Confirmar la responsabilidad declarada por el asegurado.")
        if row.get('PastNumberOfClaims', 0) > 6:
            fila.append("Historial de reclamos elevado: revisar patrones o recurrencia.")
        if row.get('Days_Policy_Accident', 999) < 30:
            fila.append("El accidente ocurrió poco después de contratar la póliza: revisar con atención.")
        if row.get('AddressChange_Claim', 1) in [0, 2, 3]:
            fila.append("El asegurado cambió de domicilio recientemente: validar veracidad del cambio.")
        if row.get('VehiclePrice', 0) > 65500:
            fila.append("Vehículo de alto valor: considerar inspección más exhaustiva.")
        if row.get('AgentType', 1) == 0:
            fila.append("Agente externo involucrado: revisar consistencia de la documentación.")
        if row.get('AgeOfPolicyHolder', 100) < 21:
            fila.append("Corroborar historial del asegurado por edad especialmente joven.")
        if row.get('VehicleCategory', -1) == 1:
            fila.append("Evaluar el contexto del accidente por tratarse de un vehículo deportivo.")
        if row.get('BasePolicy', -1) == 0:
            fila.append("Evaluar nivel de cobertura total de la póliza por posible incentivo a fraude.")
        if (
            row.get('WitnessPresent', 0) == 0 and
            row.get('PoliceReportFiled', 0) == 0 and
            row.get('NumberOfSuppliments', 0) == 0
        ):
            fila.append("Falta total de respaldo documental: enviar perito o iniciar investigación formal.")
        if not fila:
            fila.append("No se identificaron recomendaciones automáticas. Evaluar manualmente.")
        recomendaciones.append(fila)
    return recomendaciones

# Función principal de servicio
def model_service(data):
    # Llamada a las cargaas
    models = load_models()
    config = load_ensemble_config()
    schema = load_io_schema()
    feature_cols = load_feature_cols() 
    # Preprocesado
    data= preprocess_data(data, schema, feature_cols)
    print("\nDatos preprocesados:")
    for col, val in data.iloc[0].items():
        print(f"{col}: {val}")
    # Predicciones
    preds = {}
    for model_name, model in models.items():
        preds[model_name] = model.predict_proba(data)[:, 1] 
        print(f"Predicciones de {model_name}: {preds[model_name]}")
    scores = sum(preds[model_name] * config['weights'][model_name] for model_name in models)
    print("Predicciones ponderadas (scores):", scores)
    threshold = config['threshold']
    riesgos = [clasificar_riesgo(score, threshold) for score in scores]
    recomendaciones = generar_recomendaciones(data)
    for i in range(len(scores)):
        print(f"Riesgo: {riesgos[i]}")
        print("Recomendaciones:")
        for rec in recomendaciones[i]:
            print(f" - {rec}")

# Capa de IA
def generar_explicacion_llm(resultado, entrada, api_key):
    import json
    client = OpenAI(api_key=api_key)
    # Serializar entrada como texto legible
    entrada_legible = json.dumps({k: str(v) for k, v in entrada.items()}, ensure_ascii=False)
    messages: list[ChatCompletionMessageParam] = [
    {
        "role": "system",
        "content": (
            "Eres un asistente experto en detección de fraudes en seguros de vehículos. "
            "Tu tarea es explicar de manera clara y sencilla, pero profesional, por qué un reclamo fue clasificado con un nivel de riesgo determinado, "
            "basándote únicamente en la información proporcionada del caso y en las recomendaciones automáticas generadas. "
            "El texto debe estar dirigido a un empleado del área de siniestros, sin conocimientos técnicos. "
            "No menciones puntuaciones, modelos, scores ni variables técnicas. "
            "En su lugar, elabora una explicación comprensible que justifique el riesgo percibido y las acciones sugeridas. "
            "No debes saludar al empleado ni referirte a él directamente. "
            "Además, nunca dejes la explicación incompleta. Debes garantizar que la explicación esté totalmente terminada, "
            "sin dejar dudas o puntos sin resolver."
            "Para la explicación, puedes basarte en patrones comunes de riesgo. Algunos ejemplos incluyen:\n"
            "- Es sospechoso si no hay testigos del accidente.\n"
            "- Es sospechoso si no se presentó informe policial.\n"
            "- Es sospechoso si no hay documentos adjuntos.\n"
            "- Es sospechoso si hay muchos vehículos involucrados.\n"
            "- Es sospechoso si el número de coches involucrados es 0 o no se especifica.\n"
            "- También pueden influir reclamos pasados, valor del vehículo, edad del asegurado, etc.\n"
        )
    },
    {
        "role": "user",
        "content": f"""
Nivel de riesgo del reclamo: {resultado['riesgo']}
Recomendaciones automáticas: {', '.join(resultado['recomendaciones'])}
Información del reclamo: {entrada_legible}
Redacta una explicación sencilla, clara y profesional que justifique el nivel de riesgo, tomando en cuenta las recomendaciones. La respuesta debe estar completa y no quedarte NUNCA a medias.
"""
    }
]
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400 
        )
        # Validar si hay contenido real
        if response.choices and response.choices[0].message and response.choices[0].message.content.strip():
            return response.choices[0].message.content.strip()
        else:
            return "⚠️ El modelo no devolvió contenido."
    except Exception as e:
        return f"❌ Error al generar explicación IA: {e}"

# Prueba
if __name__ == "__main__":
    import getpass
    example_data = pd.DataFrame({
        'FECHA DEL ACCIDENTE': ['11/08/2021'],
        'FECHA DE LA RECLAMACION': ['25/08/2021'],
        'MARCA DEL VEHICULO': ['FORD'],
        'GENERO DEL ASEGURADO': ['MUJER'],
        'PRECIO DEL VEHICULO': [60000],
        'ZONA DONDE OCURRIO EL ACCIDENTE': ['ZONA RURAL'],
        'EDAD DEL ASEGURADO': [20],
        'ESTADO CIVIL DEL ASEGURADO': ['SOLTERO'],
        'CULPABLE DEL ACCIDENTE': ['EL PROPIO ASEGURADO'],
        'TIPO DE VEHICULO': ['DEPORTIVO'],
        'FRANQUICIA DE LA POLIZA': ["SIN FRANQUICIA"],
        'FECHA EN LA QUE SE EMITIO LA POLIZA': ['30/01/2020'],
        'NUMERO DE RECLAMACIONES PASADAS': [8],
        'ANTIGUEDAD DEL VEHICULO': ["3"],
        'INFORME POLICIAL DEL ACCIDENTE': ['EXISTE'],
        'TESTIGOS DEL ACCIDENTE': ['EXISTEN'],
        'TIPO DE AGENTE QUE GESTIONO LA POLIZA': ['EXTERNO'],
        'NUMERO DE DOCUMENTOS RELACIONADOS CON EL ACCIDENTE': [0],
        'CUANTO TIEMPO DESPUES SE MUDO EL ASEGURADOR TRAS EL ACCIDENTE': ['NO SE HA MUDADO'],
        'NUMERO DE COCHES INVOLUCRADOS EN EL ACCIDENTE': [9],
        'TIPO DE POLIZA': ['COLISION']
    })

    # Ejecutar predicción
    resultado = model_service(example_data)

    # Solicitar clave
    api_key = os.getenv("OPENAI_API_KEY")

    # Ejecutar explicación si hay clave
    if api_key:
        from api_backend import generar_explicacion_llm
        explicacion = generar_explicacion_llm(resultado, example_data.iloc[0].to_dict(), api_key)
        print("\n=== EXPLICACIÓN DE LA IA ===")
        print(explicacion)
    else:
        print("No se proporcionó clave API. Explicación no generada.")
