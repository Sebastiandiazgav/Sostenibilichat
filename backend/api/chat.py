import os
from fastapi import APIRouter, HTTPException
from models.chat import ChatRequest, ChatResponse
from services.llm_service import llm_service
from services.rag_service import rag_service
from core.config import settings

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint for chat interactions with the sustainability assistant."""
    try:
        result = llm_service.generate_response(
            question=request.message,
            conversation_id=request.conversation_id
        )

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            sources=result["sources"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@router.post("/ingest")
async def ingest_documents():
    """Endpoint to ingest documents into the vector database."""
    try:
        print("Starting direct document ingestion...")

        # Direct approach - scan project directory
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        docs_paths = [
            os.path.join(project_root, "documentos"),
            os.path.join(project_root, "docs"),
            project_root
        ]

        all_texts = []
        all_metadatas = []

        for docs_path in docs_paths:
            if os.path.exists(docs_path):
                print(f"Scanning directory: {docs_path}")
                for root, dirs, files in os.walk(docs_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_ext = os.path.splitext(file)[1].lower()

                        # Process supported file types
                        if file_ext in ['.txt', '.pdf', '.xlsx', '.xls', '.csv', '.docx', '.pptx']:
                            try:
                                print(f"Processing file: {file_path}")
                                content = _extract_content_simple(file_path, file_ext)

                                # Special debug for the specific Excel file
                                if 'Dany- Huella de Carbono.xlsx' in file_path:
                                    print("🔍 DEBUG: Analyzing Dany Excel file")
                                    print(f"Content preview (first 500 chars): {content[:500]}")
                                    print(f"Content contains 't_h9iy_energy_distribution_pct': {'t_h9iy_energy_distribution_pct' in content}")
                                    print(f"Content contains 'energy_distribution': {'energy_distribution' in content.lower()}")

                                if content.strip():
                                    print(f"Content length: {len(content)} chars")
                                    # Split content into chunks to avoid token limits
                                    chunks = _split_text_for_ingestion(content, max_chunk_size=3000)
                                    for i, chunk in enumerate(chunks):
                                        all_texts.append(chunk)
                                        all_metadatas.append({
                                            "source": file_path,
                                            "file_type": file_ext,
                                            "chunk": i,
                                            "total_chunks": len(chunks)
                                        })
                                    print(f"Processed: {os.path.basename(file_path)} → {len(chunks)} chunks ({len(content)} chars)")
                                else:
                                    print(f"No content extracted from: {file_path}")
                            except Exception as e:
                                print(f"Error processing {file_path}: {e}")

        print(f"Total texts prepared: {len(all_texts)}")

        if not all_texts:
            raise HTTPException(status_code=500, detail="No documents found to ingest")

        # Add to vector store
        from core.vector_store import vector_store
        vector_store.add_texts(all_texts, all_metadatas)
        print("Successfully added texts to vector store")

        # Create detailed summary
        file_summary = {}
        for metadata in all_metadatas:
            source = metadata["source"]
            if source not in file_summary:
                file_summary[source] = {
                    "chunks": 0,
                    "file_type": metadata["file_type"]
                }
            file_summary[source]["chunks"] += 1

        return {
            "status": "success",
            "message": f"Successfully ingested {len(all_texts)} document chunks from {len(file_summary)} files",
            "chunks_count": len(all_texts),
            "files_count": len(file_summary),
            "files_processed": [
                {
                    "filename": os.path.basename(source),
                    "path": source,
                    "chunks": info["chunks"],
                    "file_type": info["file_type"]
                }
                for source, info in file_summary.items()
            ]
        }

    except Exception as e:
        print(f"Error in ingest endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error ingesting documents: {str(e)}")

def _split_text_for_ingestion(text: str, max_chunk_size: int = 3000) -> list[str]:
    """Split text into chunks for ingestion, ensuring each chunk is under token limit."""
    if len(text) <= max_chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_size
        if end < len(text):
            # Find a good break point (sentence, paragraph, or word boundary)
            break_point = text.rfind('\n\n', start, end)  # Paragraph break
            if break_point == -1:
                break_point = text.rfind('\n', start, end)  # Line break
            if break_point == -1:
                break_point = text.rfind('. ', start, end)  # Sentence break
            if break_point == -1:
                break_point = text.rfind(' ', start, end)  # Word break
            if break_point == -1:
                break_point = end  # Hard break

            chunk = text[start:break_point].strip()
            if chunk:
                chunks.append(chunk)
            start = break_point + 1
        else:
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            start = len(text)

    return chunks

def _extract_content_simple(file_path: str, file_ext: str) -> str:
    """Simple content extraction for supported file types."""
    try:
        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif file_ext == '.pdf':
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                content = ""
                for page in reader.pages:
                    content += page.extract_text() + "\n"
                return content
            except:
                return f"PDF content extraction failed for: {os.path.basename(file_path)}"

        elif file_ext in ['.xlsx', '.xls']:
            try:
                import pandas as pd
                print(f"DEBUG: Attempting to read Excel file: {file_path}")

                # Try to read all sheets
                excel_data = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
                print(f"DEBUG: Successfully read {len(excel_data)} sheets from Excel")

                content = ""
                for sheet_name, df in excel_data.items():
                    print(f"DEBUG: Processing sheet '{sheet_name}' with shape {df.shape}")
                    content += f"Sheet: {sheet_name}\n"

                    # Convert DataFrame to string, handling NaN values
                    df_str = df.fillna('').astype(str)
                    content += df_str.to_string(index=False) + "\n\n"

                print(f"DEBUG: Excel extraction completed, content length: {len(content)}")
                return content

            except Exception as e:
                print(f"DEBUG: Excel extraction failed with error: {e}")
                # Try alternative approach with xlrd for .xls files
                try:
                    if file_ext == '.xls':
                        excel_data = pd.read_excel(file_path, sheet_name=None, engine='xlrd')
                        content = ""
                        for sheet_name, df in excel_data.items():
                            content += f"Sheet: {sheet_name}\n"
                            df_str = df.fillna('').astype(str)
                            content += df_str.to_string(index=False) + "\n\n"
                        return content
                except Exception as e2:
                    print(f"DEBUG: Alternative Excel extraction also failed: {e2}")

                return f"Excel content extraction failed for: {os.path.basename(file_path)} - Error: {str(e)}"

        elif file_ext == '.csv':
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                return df.to_string()
            except:
                return f"CSV content extraction failed for: {os.path.basename(file_path)}"

        elif file_ext == '.docx':
            try:
                from docx import Document as DocxDocument
                doc = DocxDocument(file_path)
                content = ""
                for paragraph in doc.paragraphs:
                    content += paragraph.text + "\n"
                return content
            except:
                return f"Word content extraction failed for: {os.path.basename(file_path)}"

        elif file_ext in ['.pptx', '.ppt']:
            try:
                from unstructured.partition.auto import partition
                elements = partition(file_path)
                return "\n".join([str(element) for element in elements])
            except:
                return f"PowerPoint content extraction failed for: {os.path.basename(file_path)}"

        else:
            return ""

    except Exception as e:
        return f"Error extracting content from {file_path}: {str(e)}"

@router.get("/debug/excel")
async def debug_excel_extraction():
    """Debug endpoint to check Excel extraction content."""
    try:
        # Try with a different Excel file that's likely available
        excel_files_to_try = [
            r"docs/anexos/t_sustainability_kpi_param.xlsx",
            r"docs/anexos/Universo de tablas - Sostenibilidad.xlsx",
            r"docs/Huella Carbono Launchpad-20251125T144346Z-1-001/Huella Carbono Launchpad/Dany- Huella de Carbono.xlsx"
        ]

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        for excel_path in excel_files_to_try:
            full_path = os.path.join(project_root, excel_path)
            print(f"DEBUG: Trying file: {full_path}")

            if os.path.exists(full_path):
                print(f"DEBUG: File exists, attempting extraction: {full_path}")

                # Extract content using the same function as ingestion
                content = _extract_content_simple(full_path, '.xlsx')

                # Check for specific table
                has_table = 't_h9iy_energy_distribution_pct' in content
                has_energy_dist = 'energy_distribution' in content.lower()

                print(f"DEBUG: Content length: {len(content)}")
                print(f"DEBUG: Has table: {has_table}, Has energy_dist: {has_energy_dist}")

                return {
                    "file_tested": os.path.basename(excel_path),
                    "file_path": full_path,
                    "content_length": len(content),
                    "has_t_h9iy_energy_distribution_pct": has_table,
                    "has_energy_distribution": has_energy_dist,
                    "extraction_success": len(content) > 100,  # Consider successful if we got meaningful content
                    "content_preview": content[:1000] if content else "No content extracted",
                    "full_content": content if len(content) < 2000 else f"{content[:2000]}... [truncated]"
                }

        return {"error": "No Excel files found to test"}

    except Exception as e:
        return {"error": str(e)}

@router.get("/health")
async def health_check():
    """Detailed health check for all services."""
    try:
        from core.vector_store import vector_store
        from services.llm_service import llm_service

        health_status = {
            "status": "healthy",
            "services": {}
        }

        # Check Pinecone
        try:
            index_stats = vector_store.index.describe_index_stats()
            health_status["services"]["pinecone"] = {
                "status": "connected",
                "index_name": settings.PINECONE_INDEX_NAME,
                "total_vectors": index_stats.total_vector_count
            }
        except Exception as e:
            health_status["services"]["pinecone"] = {
                "status": "error",
                "error": str(e)
            }

        # Check AWS Bedrock
        try:
            # Simple test call to validate connection
            test_response = llm_service._call_bedrock("Hola, esta es una prueba de conexión.")
            health_status["services"]["bedrock"] = {
                "status": "connected",
                "model": settings.BEDROCK_MODEL_ID,
                "test_response_length": len(test_response)
            }
        except Exception as e:
            health_status["services"]["bedrock"] = {
                "status": "error",
                "error": str(e)
            }

        # Overall status
        all_services_ok = all(
            service.get("status") == "connected"
            for service in health_status["services"].values()
        )

        if not all_services_ok:
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "services": {}
        }