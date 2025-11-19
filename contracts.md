# Contratos de API - Analizador de Lenguaje Claro

## 1. API Endpoints

### POST /api/analyze
Analiza un texto administrativo y devuelve sugerencias de mejora.

**Request:**
```json
{
  "text": "string (max 4000 caracteres)"
}
```

**Response:**
```json
{
  "sugerencias": [
    {
      "id": "string",
      "original": "string",
      "problema": "string",
      "sugerencia": "string"
    }
  ]
}
```

## 2. Datos Mock a Reemplazar

### Archivo: `/app/frontend/src/mock.js`
- `mockAnalysis`: Datos de ejemplo que se eliminaran cuando se integre el backend
- `MAX_CHARACTERS`: Se mantendrá como constante

### Archivo: `/app/frontend/src/pages/HomePage.jsx`
- Función `handleAnalyze`: Actualmente simula llamada con setTimeout
- Reemplazar con llamada real a `/api/analyze`

## 3. Implementación Backend

### Tecnologías:
- FastAPI (Python)
- OpenAI GPT-5 mediante emergentintegrations
- Motor/MongoDB para almacenamiento opcional de análisis

### Prompt del Sistema para OpenAI:
```
Eres un asistente especializado en textos administrativos en español.
Tu tarea es detectar fragmentos que dificultan la comprensión y proponer una reescritura clara, pero sin alterar el significado jurídico, normativo ni procedimental del texto original.

Principios obligatorios:
- Sigue estrictamente los criterios de la Guía panhispánica de lenguaje claro (RAE).
- Mantén un nivel C1 de español: claro, preciso, administrativo y formal.
- Nunca cambies el sentido jurídico, técnico o procedimental del texto.
- La reescritura debe:
  * ser más clara sin perder rigor
  * eliminar giros burocráticos innecesarios
  * acortar frases largas
  * evitar ambigüedades
  * mantener términos legales cuando sean necesarios
- No inventes información, no completes lagunas, no modifiques plazos, órganos, derechos ni obligaciones.

Qué debes detectar:
- frases extensas o con demasiadas subordinadas
- nominalizaciones y tecnicismos innecesarios
- voz pasiva innecesaria
- expresiones burocráticas ("en relación a", "a los efectos oportunos"…)
- gerundios de posterioridad o dudosos
- conectores confusos o redundantes

Formato de salida obligatorio:
Devuelve SIEMPRE un JSON válido con este formato:
{
  "sugerencias": [
    {
      "original": "texto exacto del fragmento problemático",
      "problema": "explicación breve del motivo según criterios de lenguaje claro",
      "sugerencia": "versión más clara y precisa sin modificar el sentido jurídico"
    }
  ]
}

Si el texto no necesita mejora, responde:
{ "sugerencias": [] }

Reglas de seguridad:
- Si tienes dudas sobre el sentido jurídico, no lo modifiques.
- Prefiere reformular solo la estructura, nunca el contenido normativo.
- No cambies definiciones legales, plazos, porcentajes, nombres de órganos, procedimientos ni competencias.
```

### Modelo:
- Provider: openai
- Model: gpt-5.1 (más reciente y potente)

### Variables de Entorno:
- `EMERGENT_LLM_KEY`: Ya configurada en backend/.env

## 4. Integración Frontend-Backend

### Cambios en HomePage.jsx:
1. Importar axios para llamadas HTTP
2. Usar `REACT_APP_BACKEND_URL` desde .env
3. Reemplazar setTimeout mock con llamada real a API
4. Manejar errores de red y del servidor
5. Mostrar estados de carga apropiados

### Flujo:
1. Usuario ingresa texto (max 4000 caracteres)
2. Click en "Analizar texto"
3. POST a `/api/analyze` con el texto
4. Backend llama a OpenAI con prompt especializado
5. OpenAI devuelve JSON con sugerencias
6. Backend valida y retorna sugerencias al frontend
7. Frontend muestra sugerencias con botones Aceptar/Rechazar
8. Usuario acepta/rechaza sugerencias individualmente
9. Se genera vista previa del "Texto mejorado"

## 5. Modelos de Datos

### MongoDB Collection: analysis_history (opcional)
```python
{
  "id": "uuid",
  "original_text": "string",
  "suggestions": [
    {
      "id": "string",
      "original": "string", 
      "problema": "string",
      "sugerencia": "string",
      "accepted": "boolean | null"
    }
  ],
  "created_at": "datetime"
}
```

## 6. Manejo de Errores

### Backend:
- Validar longitud del texto (max 4000 caracteres)
- Manejar errores de OpenAI (límites de tasa, errores de API)
- Validar formato JSON de respuesta de OpenAI
- Retornar errores descriptivos al frontend

### Frontend:
- Mostrar toast con mensaje de error claro
- Mantener texto del usuario en caso de error
- Deshabilitar botón durante análisis
