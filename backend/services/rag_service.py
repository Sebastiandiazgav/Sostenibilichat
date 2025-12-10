from utils.document_loader import DocumentLoader
from core.vector_store import vector_store
from core.config import settings

class RAGService:
    def __init__(self):
        self.document_loader = DocumentLoader()

    def ingest_documents(self) -> dict:
        """Ingest all documents from the project into Pinecone."""
        try:
            print("Starting document ingestion with direct approach...")

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
                                    content = self._extract_content_simple(file_path, file_ext)
                                    if content.strip():
                                        all_texts.append(content)
                                        all_metadatas.append({
                                            "source": file_path,
                                            "file_type": file_ext
                                        })
                                        print(f"Processed: {file_path} ({len(content)} chars)")
                                except Exception as e:
                                    print(f"Error processing {file_path}: {e}")

            print(f"Total texts prepared: {len(all_texts)}")

            if not all_texts:
                return {"status": "error", "message": "No documents found to ingest"}

            # Add to vector store
            vector_store.add_texts(all_texts, all_metadatas)
            print("Successfully added texts to vector store")

            return {
                "status": "success",
                "message": f"Successfully ingested {len(all_texts)} document chunks",
                "chunks_count": len(all_texts)
            }

        except Exception as e:
            print(f"Error in ingest_documents: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": f"Error ingesting documents: {str(e)}"}

    def _extract_content_simple(self, file_path: str, file_ext: str) -> str:
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
                    excel_data = pd.read_excel(file_path, sheet_name=None)
                    content = ""
                    for sheet_name, df in excel_data.items():
                        content += f"Sheet: {sheet_name}\n"
                        content += df.to_string() + "\n\n"
                    return content
                except:
                    return f"Excel content extraction failed for: {os.path.basename(file_path)}"

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

# Global instance
rag_service = RAGService()