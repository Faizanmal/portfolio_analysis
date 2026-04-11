"""
Document Analyzer with LLM Integration

Advanced document analysis using large language models for:
- Document summarization
- Question answering
- Key information extraction
- Investment due diligence automation

Features:
- PDF/DOCX document processing
- Multi-document analysis
- LLM-powered insights
- Structured data extraction
"""

import PyPDF2
from docx import Document
from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime
from loguru import logger
import sys
import re

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from api.integrations import OpenAIClient


class DocumentAnalyzer:
    """
    AI-powered document analysis system.
    
    Processes financial documents and extracts insights using
    large language models and natural language processing.
    """
    
    def __init__(self, output_dir: str = "data/processed"):
        """
        Initialize document analyzer.
        
        Args:
            output_dir: Directory for processed documents
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.llm_client = OpenAIClient()
        self.analysis_cache = {}
        
        logger.info("Document Analyzer initialized")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Extracting text from PDF: {pdf_path.name}")
        
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                
            logger.info(f"Extracted {len(text)} characters from {num_pages} pages")
            
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise
        
        return text
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            Extracted text
        """
        docx_path = Path(docx_path)
        
        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX not found: {docx_path}")
        
        logger.info(f"Extracting text from DOCX: {docx_path.name}")
        
        try:
            doc = Document(docx_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
            logger.info(f"Extracted {len(text)} characters")
            
        except Exception as e:
            logger.error(f"Error extracting DOCX: {str(e)}")
            raise
        
        return text
    
    def load_document(self, file_path: str) -> str:
        """
        Load document and extract text.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Extracted text
        """
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif file_path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def summarize_document(self, document_text: str, max_length: int = 500) -> str:
        """
        Generate comprehensive document summary.
        
        Args:
            document_text: Document text
            max_length: Maximum summary length in words
            
        Returns:
            Document summary
        """
        logger.info("Generating document summary...")
        
        # Use LLM for summarization
        summary = self.llm_client.summarize_document(document_text, max_length)
        
        logger.info(f"Summary generated ({len(summary)} characters)")
        
        return summary
    
    def extract_financial_metrics(self, document_text: str) -> Dict:
        """
        Extract financial metrics from document.
        
        Args:
            document_text: Document text
            
        Returns:
            Dictionary of extracted metrics
        """
        logger.info("Extracting financial metrics...")
        
        prompt = f"""
        Extract all financial metrics and key numbers from the following document.
        Present the information in a structured JSON format with these categories:
        - revenue
        - profit_margin
        - growth_rate
        - debt_levels
        - cash_flow
        - valuation_metrics
        - other_metrics
        
        For each metric, provide the value and unit if available.
        
        Document:
        {document_text[:4000]}
        
        JSON Output:
        """
        
        response = self.llm_client.generate_completion(prompt, max_tokens=1000)
        
        try:
            # Try to parse JSON from response
            # Extract JSON if it's embedded in markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object in response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                json_str = json_match.group(0) if json_match else '{}'
            
            metrics = json.loads(json_str)
            logger.info(f"Extracted {len(metrics)} metric categories")
            
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON metrics, returning raw response")
            metrics = {'raw_response': response}
        
        return metrics
    
    def answer_question(self, document_text: str, question: str) -> str:
        """
        Answer questions about the document.
        
        Args:
            document_text: Document text
            question: Question to answer
            
        Returns:
            Answer text
        """
        logger.info(f"Answering question: {question}")
        
        prompt = f"""
        Based on the following document, answer this question:
        
        Question: {question}
        
        Document:
        {document_text[:4000]}
        
        Answer (be specific and cite information from the document):
        """
        
        answer = self.llm_client.generate_completion(prompt, max_tokens=500)
        
        return answer
    
    def perform_due_diligence(self, document_text: str) -> Dict:
        """
        Perform automated due diligence analysis.
        
        Args:
            document_text: Document text
            
        Returns:
            Due diligence report
        """
        logger.info("Performing due diligence analysis...")
        
        prompt = f"""
        Perform a comprehensive due diligence analysis of the following company document.
        
        Provide analysis for these areas:
        1. Business Model & Strategy
        2. Financial Health
        3. Market Position & Competition
        4. Growth Potential
        5. Risk Factors
        6. Management & Governance
        7. Overall Assessment
        8. Investment Recommendation
        
        For each area, provide:
        - Summary (2-3 sentences)
        - Key findings
        - Risk level (Low/Medium/High)
        
        Document:
        {document_text[:5000]}
        
        Analysis:
        """
        
        analysis = self.llm_client.generate_completion(prompt, max_tokens=2000)
        
        # Structure the response
        due_diligence = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'document_length': len(document_text),
            'status': 'completed'
        }
        
        return due_diligence
    
    def extract_key_entities(self, document_text: str) -> Dict:
        """
        Extract key entities and their relationships.
        
        Args:
            document_text: Document text
            
        Returns:
            Dictionary of entities
        """
        logger.info("Extracting key entities...")
        
        prompt = f"""
        Extract and categorize all important entities from this financial document:
        
        Categories:
        - Companies (name, role, relationship)
        - People (name, title, organization)
        - Financial Figures (amount, context, time period)
        - Dates (date, associated event)
        - Locations (place, relevance)
        - Products/Services (name, description)
        
        Document:
        {document_text[:4000]}
        
        Entities (in JSON format):
        """
        
        response = self.llm_client.generate_completion(prompt, max_tokens=1000)
        
        try:
            # Extract JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                json_str = json_match.group(0) if json_match else '{}'
            
            entities = json.loads(json_str)
            
        except json.JSONDecodeError:
            entities = {'raw_response': response}
        
        return entities
    
    def generate_investment_memo(self, document_text: str, company_name: str) -> str:
        """
        Generate investment memorandum.
        
        Args:
            document_text: Source document text
            company_name: Company name
            
        Returns:
            Investment memo
        """
        logger.info(f"Generating investment memo for {company_name}...")
        
        prompt = f"""
        Create a professional investment memorandum for {company_name} based on the provided information.
        
        Structure:
        1. Executive Summary
        2. Company Overview
        3. Investment Thesis
        4. Financial Analysis
        5. Market Opportunity
        6. Risks and Mitigations
        7. Valuation
        8. Recommendation
        
        Use professional language suitable for investment committee presentation.
        
        Source Document:
        {document_text[:6000]}
        
        Investment Memorandum:
        """
        
        memo = self.llm_client.generate_completion(prompt, max_tokens=2000)
        
        return memo
    
    def analyze_document_complete(self, file_path: str) -> Dict:
        """
        Perform complete document analysis.
        
        Args:
            file_path: Path to document
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Performing complete analysis of: {file_path}")
        
        # Load document
        document_text = self.load_document(file_path)
        
        # Perform all analyses
        results = {
            'file_path': str(file_path),
            'file_name': Path(file_path).name,
            'timestamp': datetime.now().isoformat(),
            'document_length': len(document_text),
            'summary': self.summarize_document(document_text),
            'financial_metrics': self.extract_financial_metrics(document_text),
            'key_entities': self.extract_key_entities(document_text),
            'due_diligence': self.perform_due_diligence(document_text)
        }
        
        # Save results
        output_file = self.output_dir / f"analysis_{Path(file_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Analysis complete. Results saved to {output_file}")
        
        return results
    
    def batch_analyze_documents(self, file_paths: List[str]) -> List[Dict]:
        """
        Analyze multiple documents.
        
        Args:
            file_paths: List of document paths
            
        Returns:
            List of analysis results
        """
        logger.info(f"Batch analyzing {len(file_paths)} documents...")
        
        results = []
        
        for file_path in file_paths:
            try:
                analysis = self.analyze_document_complete(file_path)
                results.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {str(e)}")
                results.append({
                    'file_path': file_path,
                    'error': str(e),
                    'status': 'failed'
                })
        
        logger.info(f"Batch analysis complete. {len(results)} documents processed.")
        
        return results


def create_sample_document():
    """Create a sample document for testing."""
    
    sample_text = """
    COMPANY QUARTERLY REPORT
    Q4 2024 Financial Results
    
    Executive Summary:
    TechCorp Inc. delivered exceptional performance in Q4 2024, with revenue reaching $250 million,
    representing a 35% year-over-year growth. The company's innovative product line and strategic
    market expansion have positioned us well for continued growth in 2025.
    
    Financial Highlights:
    - Total Revenue: $250 million (↑35% YoY)
    - Gross Profit Margin: 68%
    - Operating Income: $75 million
    - Net Income: $55 million
    - EBITDA: $85 million
    - Free Cash Flow: $45 million
    
    Key Metrics:
    - Customer Acquisition Cost (CAC): $1,200
    - Lifetime Value (LTV): $8,500
    - LTV/CAC Ratio: 7.1x
    - Monthly Recurring Revenue (MRR): $18 million
    - Annual Recurring Revenue (ARR): $216 million
    
    Business Highlights:
    - Launched three new AI-powered products
    - Expanded operations to 15 new markets
    - Acquired Strategic AI Company for $50 million
    - Grew customer base to 125,000 (↑45% YoY)
    - Increased team size to 850 employees
    
    Market Position:
    TechCorp maintains a strong competitive position in the enterprise AI software market,
    with an estimated 15% market share. Our proprietary technology and customer-centric
    approach have resulted in a 95% customer retention rate and net promoter score of 72.
    
    Risk Factors:
    - Increasing competition in AI software market
    - Dependence on key cloud infrastructure providers
    - Regulatory uncertainty in data privacy regulations
    - Foreign exchange fluctuations affecting international revenue
    
    2025 Outlook:
    Management expects continued strong performance with projected revenue growth of 30-35%
    for full year 2025. We plan to invest $100 million in R&D and expand our sales team by 40%.
    """
    
    # Save to file
    output_path = Path("data/raw/sample_company_report.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(sample_text)
    
    logger.info(f"Sample document created: {output_path}")
    
    return output_path


if __name__ == "__main__":
    # Configure logging
    logger.add("logs/document_analyzer.log", rotation="10 MB")
    
    # Create sample document
    sample_doc = create_sample_document()
    
    # Initialize analyzer
    analyzer = DocumentAnalyzer()
    
    # Perform analysis
    logger.info("Starting document analysis...")
    
    # Load document
    text = analyzer.load_document(sample_doc)
    logger.info(f"Loaded document: {len(text)} characters")
    
    # Generate summary
    summary = analyzer.summarize_document(text)
    logger.info("\n" + "="*50)
    logger.info("DOCUMENT SUMMARY:")
    logger.info("="*50)
    logger.info(summary)
    
    # Extract metrics
    metrics = analyzer.extract_financial_metrics(text)
    logger.info("\n" + "="*50)
    logger.info("FINANCIAL METRICS:")
    logger.info("="*50)
    logger.info(json.dumps(metrics, indent=2))
    
    # Answer a question
    question = "What was the company's revenue growth rate?"
    answer = analyzer.answer_question(text, question)
    logger.info("\n" + "="*50)
    logger.info(f"Q: {question}")
    logger.info(f"A: {answer}")
    logger.info("="*50)
    
    # Perform complete analysis (if OpenAI key is configured)
    if analyzer.llm_client.api_key:
        logger.info("\nPerforming complete analysis...")
        complete_analysis = analyzer.analyze_document_complete(sample_doc)
        logger.info("Complete analysis saved")
    
    logger.info("\nDocument analysis demonstration complete!")
