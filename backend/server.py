from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import json
from openai import AsyncOpenAI


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Text Analysis Models
class Sugerencia(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original: str
    problema: str
    sugerencia: str

class AnalysisRequest(BaseModel):
    text: str
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('El texto no puede estar vacío')
        if len(v) > 4000:
            raise ValueError('El texto excede el límite de 4000 caracteres')
        return v.strip()

class AnalysisResponse(BaseModel):
    sugerencias: List[Sugerencia]

# System prompt for OpenAI
SYSTEM_PROMPT = """Eres un asistente especializado en textos administrativos en español.
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

Criterios de la Guía panhispánica que debes aplicar:
1. Evitar párrafos largos, densos y con demasiadas subordinadas.
2. Sustituir formulismos, arcaísmos, latinismos, y clichés administrativos.
3. Usar léxico común y preciso; eliminar palabras baúl y verbos comodín.
4. Eliminar redundancias, ambigüedades y vaguedades semánticas.
5. Mantener la precisión jurídica sin reducir contenido.
6. Reordenar la información para que siga un orden lógico y fácil de leer.
7. Sustituir gerundios indebidos, pasivas innecesarias y construcciones impersonales excesivas.
8. Explicar términos técnicos cuando su comprensión no sea obvia.
9. Extraer incisos o explicaciones laterales que interrumpan la línea argumental.
10. Garantizar buena puntuación y acentuación para mejorar la claridad.
11. Detectar y corregir errores ortográficos (faltas de ortografía, tildes incorrectas o faltantes, uso incorrecto de mayúsculas y minúsculas).

Qué debes detectar:
- frases extensas o con demasiadas subordinadas
- nominalizaciones y tecnicismos innecesarios
- voz pasiva innecesaria
- expresiones burocráticas ("en relación a", "a los efectos oportunos"…)
- gerundios de posterioridad o dudosos
- conectores confusos o redundantes
- formulismos, arcaísmos y latinismos
- palabras baúl y verbos comodín
- redundancias y ambigüedades
- orden no lógico de la información
- construcciones impersonales excesivas
- incisos que interrumpan la línea argumental
- problemas de puntuación y acentuación
- errores ortográficos (faltas de ortografía, palabras mal escritas)
- tildes incorrectas o faltantes
- uso incorrecto de mayúsculas y minúsculas

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
- No cambies definiciones legales, plazos, porcentajes, nombres de órganos, procedimientos ni competencias."""

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

@api_router.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest):
    try:
        # Get API key from environment
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")
        
        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=api_key)
        
        # Send message and get response
        logger.info(f"Sending text for analysis: {len(request.text)} characters")
        try:
            completion = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": request.text}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            response = completion.choices[0].message.content
            logger.info(f"Received response from OpenAI: {response[:200]}...")
            
        except Exception as llm_error:
            logger.error(f"OpenAI API Error: {str(llm_error)}")
            error_str = str(llm_error).lower()
            if "insufficient_quota" in error_str or "quota" in error_str:
                raise HTTPException(
                    status_code=503,
                    detail="Balance de créditos insuficiente en OpenAI. Por favor, recarga tu balance."
                )
            elif "rate_limit" in error_str:
                raise HTTPException(
                    status_code=429,
                    detail="Límite de uso excedido. Por favor, intenta en unos minutos."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al conectar con OpenAI: {str(llm_error)}"
                )
        
        # Parse JSON response
        try:
            # Try to parse the response as JSON
            response_data = json.loads(response)
            
            # Validate response structure
            if "sugerencias" not in response_data:
                raise ValueError("Response missing 'sugerencias' field")
            
            # Add IDs to suggestions if not present
            sugerencias = []
            for sug in response_data["sugerencias"]:
                if "id" not in sug:
                    sug["id"] = str(uuid.uuid4())
                sugerencias.append(Sugerencia(**sug))
            
            return AnalysisResponse(sugerencias=sugerencias)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response was: {response}")
            # Check if response indicates API key issue
            if "insufficient_quota" in response.lower() or "rate_limit" in response.lower():
                raise HTTPException(
                    status_code=503,
                    detail="Servicio temporalmente no disponible. Por favor, intenta más tarde."
                )
            raise HTTPException(
                status_code=500, 
                detail="Error al procesar la respuesta del análisis. Por favor, intenta de nuevo."
            )
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            error_msg = str(e)
            if "insufficient_quota" in error_msg.lower() or "rate_limit" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail="Servicio temporalmente no disponible. Por favor, intenta más tarde."
                )
            raise HTTPException(
                status_code=500,
                detail="Error al procesar las sugerencias. Por favor, intenta de nuevo."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al analizar el texto. Por favor, intenta de nuevo."
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()