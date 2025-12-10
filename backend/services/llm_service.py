import boto3
from botocore.exceptions import BotoCoreError, ClientError
from core.config import settings
from core.vector_store import vector_store
import json
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        try:
            # Initialize Bedrock client
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            logger.info("Bedrock client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise

    def generate_response(self, question: str, conversation_id: str = None) -> dict:
        """Generate a response using RAG with AWS Bedrock."""
        try:
            # Get relevant documents from vector store
            logger.info(f"Searching for relevant documents for question: {question}")
            docs = vector_store.similarity_search(question, k=3)
            logger.info(f"Found {len(docs)} relevant documents")

            sources = [doc.get("metadata", {}).get("source", "Unknown") for doc in docs]

            # Prepare context from retrieved documents
            context_parts = []
            for i, doc in enumerate(docs, 1):
                content = doc.get("page_content", "")
                source = doc.get("metadata", {}).get("source", "Unknown")
                context_parts.append(f"Documento {i} ({source}):\n{content}")

            context = "\n\n".join(context_parts)
            logger.info(f"Prepared context with {len(context)} characters")

            # Create prompt for Claude with structured formatting
            prompt = f"""Eres un Asistente Técnico Experto con enfoque en UX (Experiencia de Usuario) especializado en sostenibilidad financiera de BBVA.
Tu objetivo es responder preguntas técnicas basándote en los documentos proporcionados, asegurando que la lectura sea escaneable, clara y visualmente estructurada.

Pregunta del usuario: {question}

Información relevante de los documentos:
{context}

REGLAS DE FORMATO Y ESTILO (ESTRICTO):

1. ESTRUCTURA VISUAL DEL TEXTO:
   - NO generes bloques de texto plano o párrafos infinitos
   - Usa listas con viñetas (- o *) para enumerar características, pasos o requisitos
   - Usa negritas (**texto**) para resaltar conceptos clave, nombres de librerías o términos importantes
   - Usa encabezados (### Título) para separar secciones lógicas

2. MANEJO DE ENLACES:
   - Si la información contiene una URL, formatearla como enlace Markdown clickeable
   - Formato: [Texto descriptivo](URL)

3. REFERENCIA A DOCUMENTOS:
   - Cuando menciones fuentes, resáltalas visualmente
   - Usa formato distintivo como: *Fuente: **[Nombre del documento.pdf]***

4. CONTENIDO Y ESTILO:
   - Responde en español
   - Sé específico y preciso con los datos
   - Mantén un tono profesional y experto
   - Si no encuentras información relevante, indica claramente que no tienes datos suficientes

EJEMPLO DE ESTRUCTURA ESPERADA:
### Definición del Concepto
Explicación clara y concisa del tema principal.

### Características Principales
- **Característica 1:** Descripción detallada
- **Característica 2:** Información adicional
- **Característica 3:** Detalles técnicos

### Pasos para Implementación
1. Primer paso con instrucciones claras
2. Segundo paso con requisitos específicos
3. Tercer paso con consideraciones importantes

*Fuente: **[Documento de referencia.pdf]***

Respuesta:"""

            # Call Bedrock
            logger.info("Calling AWS Bedrock for response generation")
            response = self._call_bedrock(prompt)
            logger.info("Successfully generated response from Bedrock")

            return {
                "response": response,
                "conversation_id": conversation_id or "default",
                "sources": sources
            }

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response when everything fails
            return {
                "response": f"Lo siento, ocurrió un error al procesar tu pregunta. Error: {str(e)}",
                "conversation_id": conversation_id or "default",
                "sources": []
            }

    def _call_bedrock(self, prompt: str) -> str:
        """Call AWS Bedrock Claude model."""
        try:
            # Prepare the request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,  # Low temperature for more consistent responses
                "top_p": 0.9
            }

            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']

        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS Bedrock error: {e}")
            raise Exception(f"Error calling Bedrock: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error calling Bedrock: {e}")
            raise

# Global instance
llm_service = LLMService()