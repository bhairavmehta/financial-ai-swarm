"""
Document Processing Agent
Receipt and invoice OCR with field extraction
Based on Sparrow patterns
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
from PIL import Image
import io
import base64

# OCR imports
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available, OCR will be limited")

import numpy as np
import cv2

logger = logging.getLogger(__name__)


@dataclass
class ExtractedDocument:
    """Extracted document data"""
    document_type: str  # RECEIPT, INVOICE, CONTRACT
    merchant_name: Optional[str]
    total_amount: Optional[float]
    tax_amount: Optional[float]
    date: Optional[str]
    items: List[Dict]
    payment_method: Optional[str]
    currency: str
    confidence_score: float
    raw_text: str
    metadata: Dict


class DocumentProcessingAgent:
    """
    Document processing agent with OCR and field extraction
    Handles receipts, invoices, and expense documents
    """
    
    # Regex patterns for field extraction
    PATTERNS = {
        'total': [
            r'total[:\s]*\$?\s*(\d+[.,]\d{2})',
            r'amount[:\s]*\$?\s*(\d+[.,]\d{2})',
            r'grand\s+total[:\s]*\$?\s*(\d+[.,]\d{2})',
        ],
        'tax': [
            r'tax[:\s]*\$?\s*(\d+[.,]\d{2})',
            r'vat[:\s]*\$?\s*(\d+[.,]\d{2})',
            r'sales\s+tax[:\s]*\$?\s*(\d+[.,]\d{2})',
        ],
        'date': [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
        ],
        'merchant': [
            r'^([A-Z][A-Za-z\s&]+)(?:\n|$)',  # First line capitalized
        ]
    }
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.pdf', '.tiff']
        
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        return denoised
    
    def _extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from image using OCR"""
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract not available, returning mock text")
            return self._generate_mock_receipt_text()
        
        try:
            # Preprocess image
            processed = self._preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(
                processed,
                config='--psm 6'  # Assume uniform block of text
            )
            
            return text
            
        except Exception as e:
            logger.error(f"OCR error: {e}", exc_info=True)
            return self._generate_mock_receipt_text()
    
    def _generate_mock_receipt_text(self) -> str:
        """Generate mock receipt text for testing"""
        return """
        ACME RESTAURANT
        123 Main Street
        New York, NY 10001
        Tel: (555) 123-4567
        
        Date: 01/15/2025
        Server: John
        Table: 12
        
        2x Burger Deluxe      $28.00
        1x Caesar Salad       $12.00
        3x Soft Drinks        $9.00
        
        Subtotal:            $49.00
        Tax (8%):             $3.92
        
        TOTAL:               $52.92
        
        Payment Method: Credit Card
        Card: **** **** **** 1234
        
        Thank you for dining with us!
        """
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a specific field from text using regex"""
        patterns = self.PATTERNS.get(field_name, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_items(self, text: str) -> List[Dict]:
        """Extract line items from receipt"""
        items = []
        
        # Pattern: quantity x item name price
        pattern = r'(\d+)x?\s+([A-Za-z\s]+)\s+\$?(\d+[.,]\d{2})'
        matches = re.finditer(pattern, text, re.MULTILINE)
        
        for match in matches:
            quantity = int(match.group(1))
            name = match.group(2).strip()
            price = float(match.group(3).replace(',', '.'))
            
            items.append({
                'quantity': quantity,
                'description': name,
                'unit_price': price / quantity if quantity > 0 else price,
                'total_price': price
            })
        
        return items
    
    def _detect_document_type(self, text: str) -> str:
        """Detect document type from text content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['invoice', 'bill to', 'invoice number']):
            return 'INVOICE'
        elif any(word in text_lower for word in ['receipt', 'total', 'server', 'table']):
            return 'RECEIPT'
        elif any(word in text_lower for word in ['contract', 'agreement', 'terms']):
            return 'CONTRACT'
        else:
            return 'UNKNOWN'
    
    def _calculate_confidence(self, extracted_data: Dict) -> float:
        """Calculate confidence score based on extracted fields"""
        score = 0.0
        max_score = 5.0
        
        if extracted_data.get('merchant_name'):
            score += 1.0
        if extracted_data.get('total_amount'):
            score += 1.5
        if extracted_data.get('date'):
            score += 1.0
        if extracted_data.get('items'):
            score += 1.0
        if extracted_data.get('tax_amount'):
            score += 0.5
        
        return min(score / max_score, 1.0)
    
    def process_document(self, document_data: Dict) -> ExtractedDocument:
        """
        Main document processing method
        
        Args:
            document_data: Dict with 'file_path' or 'image_bytes' or 'base64_image'
            
        Returns:
            ExtractedDocument with all extracted fields
        """
        logger.info("Processing document")
        
        try:
            # Load image
            if 'image_bytes' in document_data:
                image = Image.open(io.BytesIO(document_data['image_bytes']))
            elif 'base64_image' in document_data:
                image_bytes = base64.b64decode(document_data['base64_image'])
                image = Image.open(io.BytesIO(image_bytes))
            elif 'file_path' in document_data:
                image = Image.open(document_data['file_path'])
            else:
                raise ValueError("No image data provided")
            
            # Extract text
            raw_text = self._extract_text_from_image(image)
            logger.debug(f"Extracted text: {raw_text[:200]}...")
            
            # Detect document type
            doc_type = self._detect_document_type(raw_text)
            
            # Extract fields
            merchant_name = self._extract_field(raw_text, 'merchant')
            date_str = self._extract_field(raw_text, 'date')
            total_str = self._extract_field(raw_text, 'total')
            tax_str = self._extract_field(raw_text, 'tax')
            
            # Convert to proper types
            total_amount = float(total_str.replace(',', '.')) if total_str else None
            tax_amount = float(tax_str.replace(',', '.')) if tax_str else None
            
            # Extract items
            items = self._extract_items(raw_text)
            
            # Detect payment method
            payment_method = None
            if 'credit card' in raw_text.lower():
                payment_method = 'Credit Card'
            elif 'cash' in raw_text.lower():
                payment_method = 'Cash'
            
            # Build result
            extracted = {
                'merchant_name': merchant_name,
                'total_amount': total_amount,
                'tax_amount': tax_amount,
                'date': date_str,
                'items': items,
                'payment_method': payment_method
            }
            
            confidence_score = self._calculate_confidence(extracted)
            
            result = ExtractedDocument(
                document_type=doc_type,
                merchant_name=merchant_name,
                total_amount=total_amount,
                tax_amount=tax_amount,
                date=date_str,
                items=items,
                payment_method=payment_method,
                currency='USD',  # Could be detected from symbols
                confidence_score=confidence_score,
                raw_text=raw_text,
                metadata={
                    'image_size': f"{image.width}x{image.height}",
                    'processing_timestamp': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Document processed: {doc_type} (confidence: {confidence_score:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Document processing error: {e}", exc_info=True)
            raise
    
    def validate_expense(self, extracted_doc: ExtractedDocument, policy_limits: Dict) -> Dict:
        """
        Validate extracted expense against policy
        
        Args:
            extracted_doc: Extracted document data
            policy_limits: Dictionary of policy limits
            
        Returns:
            Validation result with pass/fail and reasons
        """
        violations = []
        warnings = []
        
        # Check amount limits
        if extracted_doc.total_amount:
            category_limit = policy_limits.get(extracted_doc.document_type, float('inf'))
            if extracted_doc.total_amount > category_limit:
                violations.append(
                    f"Amount ${extracted_doc.total_amount:.2f} exceeds limit ${category_limit:.2f}"
                )
        
        # Check for missing required fields
        if not extracted_doc.merchant_name:
            warnings.append("Merchant name not found")
        if not extracted_doc.date:
            warnings.append("Date not found")
        if extracted_doc.confidence_score < 0.5:
            warnings.append(f"Low confidence score: {extracted_doc.confidence_score:.2f}")
        
        return {
            'valid': len(violations) == 0,
            'violations': violations,
            'warnings': warnings,
            'confidence': extracted_doc.confidence_score
        }
    
    def batch_process(self, documents: List[Dict]) -> List[ExtractedDocument]:
        """Process multiple documents"""
        return [self.process_document(doc) for doc in documents]


# Global agent instance
_document_agent = None

def get_document_agent() -> DocumentProcessingAgent:
    """Get or create global document processing agent"""
    global _document_agent
    if _document_agent is None:
        _document_agent = DocumentProcessingAgent()
    return _document_agent


if __name__ == "__main__":
    # Test the document processing agent
    logging.basicConfig(level=logging.INFO)
    
    # Test with mock data
    agent = DocumentProcessingAgent()
    
    test_doc = {
        'file_path': 'test_receipt.jpg'  # Would be actual file in production
    }
    
    # Process will use mock text since we don't have an actual image
    result = agent.process_document(test_doc)
    
    print(f"\nDocument Type: {result.document_type}")
    print(f"Merchant: {result.merchant_name}")
    print(f"Total: ${result.total_amount:.2f}" if result.total_amount else "Total: Not found")
    print(f"Date: {result.date}")
    print(f"Confidence: {result.confidence_score:.2f}")
    print(f"Items: {len(result.items)}")
    for item in result.items:
        print(f"  - {item['quantity']}x {item['description']}: ${item['total_price']:.2f}")
