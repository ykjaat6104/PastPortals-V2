"""
CRAG (Correction + Retrieval-Augmented Generation) Implementation
Provides fact-checking and hallucination correction for AI-generated responses
"""
import re
from typing import Optional, Dict, List, Tuple
from .ai_utils import generate_content, get_embeddings_model
from .vector_utils import search_vector_db
from .wikipedia_utils import search_and_summarize


class CRAGValidator:
    """
    CRAG Pipeline Implementation
    - Stage 1: Retrieval (get relevant context)
    - Stage 2: Generation (generate response)
    - Stage 3: Validation (check facts)
    - Stage 4: Correction (fix hallucinations)
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize CRAG Validator
        
        Args:
            confidence_threshold: Score threshold for fact validation (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.validation_attempts = 0
        self.max_validation_attempts = 2
        
    def retrieve(self, query: str, index=None, text_map=None, k: int = 5) -> List[str]:
        """
        Stage 1: Retrieve relevant context from knowledge base
        
        Args:
            query: User query/question
            index: FAISS vector database index
            text_map: Mapping of index to text
            k: Number of top results to retrieve
            
        Returns:
            List of relevant context documents
        """
        try:
            # Try vector search first
            if index and text_map:
                results = search_vector_db(query, index, text_map, k=k)
                if results:
                    return results
        except Exception as e:
            print(f"Vector search error: {str(e)}")
        
        # Fallback to Wikipedia search
        try:
            wiki_result = search_and_summarize(query)
            if isinstance(wiki_result, dict) and wiki_result.get('extract'):
                return [wiki_result.get('extract', '')]
        except Exception:
            pass
        
        return []
    
    def generate(self, query: str, context: List[str], temperature: float = 0.6) -> Tuple[str, str]:
        """
        Stage 2: Generate response using retrieved context
        
        Args:
            query: User query/question
            context: List of retrieved context documents
            temperature: Model temperature (0.0-1.0)
            
        Returns:
            Tuple of (generated_response, formatted_prompt)
        """
        # Build context string
        context_str = "\n\n".join([f"Context {i+1}: {ctx[:500]}" for i, ctx in enumerate(context)])
        
        prompt = f"""You are an expert museum guide and historian. Answer the following question based ONLY on the provided context.
        
IMPORTANT RULES:
1. Base your answer ONLY on the provided context
2. If the context doesn't contain the answer, say "I don't have enough information"
3. Be specific and cite which context you're using
4. Provide accurate historical and cultural information
5. Maintain professional and engaging tone

CONTEXT:
{context_str}

QUESTION: {query}

ANSWER:"""
        
        try:
            response = generate_content(prompt, temperature=temperature, max_tokens=1500)
            return response or "", prompt
        except Exception as e:
            print(f"Generation error: {str(e)}")
            return "", prompt
    
    def validate_facts(self, response: str, context: List[str], query: str) -> Tuple[float, List[str]]:
        """
        Stage 3: Validate facts in generated response
        
        Args:
            response: Generated response text
            context: Retrieved context documents
            query: Original query
            
        Returns:
            Tuple of (confidence_score, list_of_issues)
        """
        issues = []
        context_text = " ".join(context).lower()
        response_lower = response.lower()
        
        # Check 1: Extract key claims from response
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        unverified_claims = []
        
        for sentence in sentences:
            # Check if sentence contains factual claim indicators
            if any(indicator in sentence for indicator in ['is', 'was', 'invented', 'discovered', 'created', 'built', 'founded']):
                # Check if claim is supported by context
                if not self._claim_in_context(sentence, context_text):
                    unverified_claims.append(sentence)
        
        # Check 2: Detect unsupported statistics or numbers
        numbers = re.findall(r'\d+(?:\.\d+)?', response)
        for number in set(numbers):
            if number not in " ".join(context):
                issues.append(f"Number '{number}' not found in source context")
        
        # Check 3: Detect "I don't know" or uncertainty phrases (should not be corrected)
        uncertainty_phrases = ["i don't", "i cannot", "i'm not sure", "there is no information", "not available"]
        has_uncertainty = any(phrase in response_lower for phrase in uncertainty_phrases)
        
        # Calculate confidence score
        confidence = 1.0
        if unverified_claims:
            confidence -= len(unverified_claims) * 0.15
        if issues:
            confidence -= len(issues) * 0.1
        
        confidence = max(0.0, min(1.0, confidence))  # Clamp between 0 and 1
        
        if unverified_claims:
            issues.append(f"{len(unverified_claims)} claims lack source verification")
        
        return confidence, issues
    
    def correct(self, response: str, issues: List[str], context: List[str], query: str) -> str:
        """
        Stage 4: Correct hallucinations and rewrite response
        
        Args:
            response: Original response
            issues: List of validation issues
            context: Retrieved context
            query: Original query
            
        Returns:
            Corrected response
        """
        if not issues:
            return response
        
        # Build correction prompt
        context_str = "\n".join([f"• {ctx[:300]}" for ctx in context])
        
        correction_prompt = f"""You are a fact-checking expert. Review the following response for inaccuracies.

ORIGINAL RESPONSE:
{response}

IDENTIFIED ISSUES:
{chr(10).join([f"- {issue}" for issue in issues])}

SOURCE CONTEXT:
{context_str}

TASK: Rewrite the response to:
1. Remove unverified claims
2. Keep only facts directly supported by the source context
3. If information is missing, explicitly state "Based on available information..."
4. Maintain professional tone
5. Preserve the overall structure and key points

CORRECTED RESPONSE:"""
        
        try:
            corrected = generate_content(correction_prompt, temperature=0.5, max_tokens=1500)
            return corrected or response
        except Exception as e:
            print(f"Correction error: {str(e)}")
            return response
    
    def execute_pipeline(self, query: str, index=None, text_map=None, extracted_text: str = "") -> Dict:
        """
        Execute full CRAG pipeline
        
        Args:
            query: User question
            index: FAISS vector database
            text_map: Vector database text mapping
            extracted_text: Extracted content from user upload
            
        Returns:
            Dictionary with full CRAG results
        """
        results = {
            'query': query,
            'stage_1_retrieval': [],
            'stage_2_generation': '',
            'stage_3_validation': {
                'confidence_score': 0.0,
                'issues': []
            },
            'stage_4_correction': '',
            'final_response': '',
            'crag_applied': False,
            'validation_passed': True
        }
        
        try:
            # Stage 1: Retrieval
            context = self.retrieve(query, index, text_map, k=5)
            if extracted_text:
                context.insert(0, extracted_text)
            
            results['stage_1_retrieval'] = context[:3]  # Keep top 3
            
            if not context:
                return {
                    **results,
                    'final_response': "I don't have sufficient context to answer this question accurately.",
                    'crag_applied': False
                }
            
            # Stage 2: Generation
            generated_response, _ = self.generate(query, context)
            results['stage_2_generation'] = generated_response
            
            if not generated_response:
                return {
                    **results,
                    'final_response': "Unable to generate response at this time.",
                    'crag_applied': False
                }
            
            # Stage 3: Validation
            confidence, issues = self.validate_facts(generated_response, context, query)
            results['stage_3_validation'] = {
                'confidence_score': round(confidence, 3),
                'issues': issues
            }
            
            # Stage 4: Correction (if needed)
            if confidence < self.confidence_threshold and self.validation_attempts < self.max_validation_attempts:
                self.validation_attempts += 1
                corrected_response = self.correct(generated_response, issues, context, query)
                results['stage_4_correction'] = corrected_response
                results['final_response'] = corrected_response
                results['crag_applied'] = True
                results['validation_passed'] = False
            else:
                results['final_response'] = generated_response
                results['crag_applied'] = confidence >= self.confidence_threshold
                results['validation_passed'] = confidence >= self.confidence_threshold
            
            return results
            
        except Exception as e:
            print(f"CRAG pipeline error: {str(e)}")
            return {
                **results,
                'final_response': "An error occurred during processing.",
                'crag_applied': False,
                'error': str(e)
            }
    
    def _claim_in_context(self, claim: str, context: str) -> bool:
        """
        Check if a claim is supported by context
        
        Args:
            claim: Statement to verify
            context: Source context text (lowercase)
            
        Returns:
            True if claim has support in context
        """
        # Extract key terms from claim
        words = claim.lower().split()
        
        # Filter out common words
        stop_words = {'is', 'was', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'of', 'to', 'for', 'by', 'at', 'be', 'has', 'have', 'are'}
        key_words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Check if at least 50% of key words are in context
        if not key_words:
            return True
        
        found = sum(1 for word in key_words if word in context)
        coverage = found / len(key_words)
        
        return coverage >= 0.5


# Global CRAG validator instance
_crag_validator = None


def get_crag_validator(confidence_threshold: float = 0.7) -> CRAGValidator:
    """
    Get or create global CRAG validator instance
    
    Args:
        confidence_threshold: Score threshold for validation
        
    Returns:
        CRAGValidator instance
    """
    global _crag_validator
    if _crag_validator is None:
        _crag_validator = CRAGValidator(confidence_threshold=confidence_threshold)
    return _crag_validator


def apply_crag(query: str, index=None, text_map=None, extracted_text: str = "") -> Dict:
    """
    Apply CRAG pipeline to query
    
    Args:
        query: User question
        index: FAISS vector database
        text_map: Vector database text mapping
        extracted_text: Extracted content from upload
        
    Returns:
        CRAG results dictionary
    """
    validator = get_crag_validator()
    return validator.execute_pipeline(query, index, text_map, extracted_text)
