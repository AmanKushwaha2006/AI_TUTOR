import os
import sys
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from pypdf import PdfReader
from typing import List, Dict, Tuple, Union, Optional
import logging

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

try:
    from rapidocr_onnxruntime import RapidOCR
    ocr_engine = RapidOCR()
except Exception:
    ocr_engine = None

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> List[Tuple[str, Dict]]:
    """
    Extracts text from a given PDF file with metadata.
    Supports digital text and automatic OCR fallback for scanned certificates, stamp papers, and images.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of tuples containing (text, metadata)
    """
    logger.info(f"Extracting text from {os.path.basename(pdf_path)}")
    texts_with_metadata = []

    # 1. First choice: Use PyMuPDF (fitz) with automatic OCR fallback
    if fitz is not None:
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            for page_idx, page in enumerate(doc):
                text = page.get_text().strip()

                # If text is empty or very short, this is likely a scanned image/certificate -> run OCR
                if len(text) < 30 and ocr_engine is not None:
                    try:
                        logger.info(f"Page {page_idx+1} has no digital text. Running OCR...")
                        pix = page.get_pixmap(dpi=150)
                        res, _ = ocr_engine(pix.tobytes("png"))
                        if res:
                            ocr_text = "\n".join([line[1] for line in res]).strip()
                            if ocr_text:
                                text = ocr_text
                                logger.info(f"Page {page_idx+1}: Extracted {len(text)} chars via OCR")
                    except Exception as ocr_err:
                        logger.warning(f"OCR failed for page {page_idx}: {ocr_err}")

                if text and text.strip():
                    metadata = {
                        "file_name": os.path.basename(pdf_path),
                        "file_path": pdf_path,
                        "page_index": page_idx,
                        "total_pages": total_pages
                    }
                    texts_with_metadata.append((text, metadata))

            if texts_with_metadata:
                logger.info(f"Extracted {len(texts_with_metadata)} pages with text from {os.path.basename(pdf_path)} using PyMuPDF+OCR")
                return texts_with_metadata
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed for {pdf_path}: {e}. Trying pypdf fallback...")

    # 2. Fallback: Use pypdf with image OCR fallback
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        for page_idx, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()

            if len(text) < 30 and ocr_engine is not None and hasattr(page, 'images') and len(page.images) > 0:
                try:
                    logger.info(f"pypdf: Page {page_idx+1} has {len(page.images)} images. Running OCR...")
                    ocr_lines = []
                    for img in page.images:
                        res, _ = ocr_engine(img.data)
                        if res:
                            ocr_lines.extend([line[1] for line in res])
                    if ocr_lines:
                        text = "\n".join(ocr_lines).strip()
                        logger.info(f"pypdf: Extracted {len(text)} chars via image OCR")
                except Exception as ocr_err:
                    logger.warning(f"pypdf image OCR failed on page {page_idx}: {ocr_err}")

            if text and text.strip():
                metadata = {
                    "file_name": os.path.basename(pdf_path),
                    "file_path": pdf_path,
                    "page_index": page_idx,
                    "total_pages": total_pages
                }
                texts_with_metadata.append((text, metadata))

        logger.info(f"Extracted {len(texts_with_metadata)} pages with text from {os.path.basename(pdf_path)}")
        return texts_with_metadata
        
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
        return []

def index_pdfs(pdf_inputs: Union[str, List[str]], chunk_size: int = 1000, chunk_overlap: int = 200, 
               model: str = "mxbai-embed-large:latest") -> Optional[FAISS]:
    """
    Unified function to index PDFs from various input types (single PDF, list of PDFs, or folder)
    
    Args:
        pdf_inputs: Can be a single PDF path, a list of PDF paths, or a folder path
        chunk_size: Size of text chunks for splitting
        chunk_overlap: Overlap between chunks
        model: Embedding model to use
        
    Returns:
        FAISS vector store or None if indexing failed
    """
    all_texts_with_metadata = []
    
    # Process different input types
    if isinstance(pdf_inputs, str):
        if os.path.isdir(pdf_inputs):
            # It's a folder path
            logger.info(f"Indexing all PDFs in folder: {pdf_inputs}")
            pdf_files = [os.path.join(pdf_inputs, f) for f in os.listdir(pdf_inputs) 
                         if f.lower().endswith(".pdf")]
            
            if not pdf_files:
                logger.warning(f"No PDF files found in folder: {pdf_inputs}")
                return None
                
            for pdf in pdf_files:
                all_texts_with_metadata.extend(extract_text_from_pdf(pdf))
        
        elif os.path.isfile(pdf_inputs) and pdf_inputs.lower().endswith(".pdf"):
            # It's a single PDF file
            logger.info(f"Indexing single PDF: {pdf_inputs}")
            all_texts_with_metadata = extract_text_from_pdf(pdf_inputs)
        
        else:
            logger.error(f"Invalid input: {pdf_inputs} is not a PDF file or folder")
            return None
    
    elif isinstance(pdf_inputs, list):
        # It's a list of PDF paths
        logger.info(f"Indexing {len(pdf_inputs)} PDF files")
        for pdf in pdf_inputs:
            if os.path.isfile(pdf) and pdf.lower().endswith(".pdf"):
                all_texts_with_metadata.extend(extract_text_from_pdf(pdf))
            else:
                logger.warning(f"Skipping invalid file: {pdf}")
    
    else:
        logger.error("Invalid input type. Expected a string path or list of paths")
        return None
    
    # Check if we have any texts to index
    if not all_texts_with_metadata:
        logger.warning("No text content extracted from any PDFs")
        return None
    
    # Create the index
    logger.info(f"Creating FAISS index with {len(all_texts_with_metadata)} text segments")
    return create_faiss_index(all_texts_with_metadata, chunk_size, chunk_overlap, model)

def create_faiss_index(texts_with_metadata: List[Tuple[str, Dict]], 
                      chunk_size: int = 1000, 
                      chunk_overlap: int = 200,
                      model: str = "mxbai-embed-large:latest") -> FAISS:
    """
    Creates a FAISS index from extracted text using embeddings and stores metadata.
    
    Args:
        texts_with_metadata: List of tuples containing (text, metadata)
        chunk_size: Size of text chunks for splitting
        chunk_overlap: Overlap between chunks
        model: Embedding model to use
        
    Returns:
        FAISS vector store
    """
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    
    # Process text chunks with metadata
    documents = []
    metadata_list = []
    
    for text, metadata in texts_with_metadata:
        chunks = text_splitter.split_text(text)
        documents.extend(chunks)
        metadata_list.extend([metadata] * len(chunks))
    
    logger.info(f"Created {len(documents)} text chunks after splitting")
    
    # Initialize embedding model (Ollama with local HuggingFace fallback)
    embeddings = None
    try:
        embeddings = OllamaEmbeddings(model=model)
        embedding_dim = len(embeddings.embed_query("test"))
        logger.info(f"Using Ollama embedding model {model} with dimension {embedding_dim}")
    except Exception as e:
        logger.warning(f"Ollama embedding unavailable ({e}). Falling back to local HuggingFace embeddings.")
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            embedding_dim = len(embeddings.embed_query("test"))
            logger.info(f"Using local HuggingFace all-MiniLM-L6-v2 embeddings with dimension {embedding_dim}")
        except Exception as inner_e:
            logger.error(f"Failed to initialize any embedding model: {inner_e}")
            raise

    # Create FAISS index
    index = faiss.IndexFlatL2(embedding_dim)
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    
    # Add documents to vector store
    vector_store.add_texts(documents, metadatas=metadata_list)
    logger.info(f"Successfully indexed {len(documents)} text chunks")
    
    return vector_store

def retrieve_answer(query: str, vector_store: FAISS, k: int = 3) -> str:
    """
    Retrieves the most relevant documents based on the query, with metadata.
    
    Args:
        query: The search query
        vector_store: FAISS vector store to search in
        k: Number of results to return
        
    Returns:
        Formatted string with search results
    """
    logger.info(f"Searching for: '{query}'")
    docs = vector_store.similarity_search_with_score(query, k=k)
    
    if not docs:
        return "No relevant information found."
    
    results = []
    for i, (doc, score) in enumerate(docs):
        metadata = doc.metadata
        results.append(
            f"Result {i+1} (Similarity: {1 - score:.4f}):\n"
            f"File: {metadata['file_name']}, Page: {metadata['page_index'] + 1}/{metadata['total_pages']}\n"
            f"Content: {doc.page_content.strip()}\n"
        )
    
    return "\n".join(results)

def save_index(vector_store: FAISS, path: str) -> None:
    """Save the FAISS index to disk"""
    vector_store.save_local(path)
    logger.info(f"Index saved to {path}")

def load_index(path: str, model: str = "mxbai-embed-large:latest") -> FAISS:
    """Load a FAISS index from disk"""
    try:
        embeddings = OllamaEmbeddings(model=model)
    except Exception:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    logger.info(f"Index loaded from {path}")
    return vector_store

def main():
    # Example usage
    pdf_path = "C:/Projects/AI-Tutor/data/docs/DL1.pdf"
    vector_store = index_pdfs(pdf_path)
    
    if vector_store:
        # Save index for future use
        save_index(vector_store, "C:/Projects/AI-Tutor/data/index/rag_index")
        
        # Interactive query loop
        while True:
            query = input("\nEnter your query (or 'quit' to exit):\n")
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            answer = retrieve_answer(query, vector_store)
            print("\nRelevant information:\n", answer)

if __name__ == "__main__":
    main()