from datetime import datetime
from typing import Dict, Any, List
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from logger import logger
from dateutil import parser as date_parser

class VectorStoreService:
    """Service for vector database operations using ChromaDB"""
    
    def __init__(self):
        self.client = chromadb.Client(Settings(anonymized_telemetry=False))
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        try:
            self.collection = self.client.get_collection("invoice_reimbursements")
        except Exception:
            self.collection = self.client.create_collection(
                name="invoice_reimbursements",
                metadata={"description": "Invoice reimbursement analysis storage"}
            )
    
    def store_invoice_analysis(self, 
                             invoice_id: str,
                             invoice_text: str,
                             analysis_result: Dict[str, Any],
                             employee_name: str) -> bool:
        """Store invoice analysis in vector database"""
        
        try:
            # Prepare text for embedding
            text_for_embedding = f"""
            Employee: {employee_name}
            Status: {analysis_result['status']}
            Reason: {analysis_result['reason']}
            Invoice Content: {invoice_text}
            """
            
            # Generate embedding
            embedding = self.embedding_model.encode(text_for_embedding).tolist()
            # Prepare metadata
            metadata = {
                "employee_name": employee_name,
                "status": analysis_result['status'],
                "approved_amount": analysis_result.get('approved_amount', 0.0),
                "total_amount": analysis_result.get('total_amount', 0.0),
                "date": datetime.now().isoformat(),
                "invoice_id": invoice_id
            }
            
            # Store in vector database
            self.collection.add(
                documents=[text_for_embedding],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[invoice_id]
            )
            logger.info(f"Metadata for invoice {invoice_id}: {metadata}")
            logger.info(f"Stored invoice analysis for {invoice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing invoice analysis: {str(e)}")
            return False
    
    def search_invoices(self, query: str, filters: Dict = None, limit: int = 10) -> List[Dict]:
        """Search invoices using vector similarity and metadata filters"""
        
        try:
            query_embedding = self.embedding_model.encode(query).tolist()

            where_clause = {}
            amount_fuzzy = None
            date_fuzzy = None

            if filters:
                for key, value in filters.items():
                    if not value:
                        continue

                    if key == "amount":
                        amount_fuzzy = float(value)  # handle fuzzy later
                    elif key == "date":
                        try:
                            if isinstance(value, str) and len(value.split()) == 2:
                                # e.g., "May 2024"
                                parsed_date = date_parser.parse(value)
                                date_fuzzy = parsed_date
                            else:
                                # exact format
                                date_fuzzy = date_parser.parse(value)
                        except Exception as e:
                            logger.warning(f"Invalid date format in filter: {value}")
                    else:
                        where_clause[key] = value

            # Vector search with basic where_clause (employee, status, etc.)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                where=where_clause if where_clause else None,
                n_results=limit
            )

            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}

                    # Fuzzy amount filtering
                    if amount_fuzzy is not None:
                        db_amount = float(metadata.get('total_amount', 0.0))
                        if not (amount_fuzzy - 20 <= db_amount <= amount_fuzzy + 20):
                            continue  # skip if outside fuzzy range

                    # Fuzzy date filtering
                    if date_fuzzy:
                        try:
                            db_date = date_parser.parse(metadata.get('date'))
                            if isinstance(date_fuzzy, datetime):
                                # Check if same month and year
                                if (db_date.year != date_fuzzy.year or db_date.month != date_fuzzy.month):
                                    continue
                            else:
                                # strict match
                                if db_date.date() != date_fuzzy.date():
                                    continue
                        except Exception:
                            continue  # Skip if date parsing fails

                    formatted_results.append({
                        "document": doc,
                        "metadata": metadata,
                        "distance": results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            logger.info(f"Found {len(formatted_results)} results for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching invoices: {str(e)}")
            return []