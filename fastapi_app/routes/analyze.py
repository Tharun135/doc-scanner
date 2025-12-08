# fastapi_app/routes/analyze.py
"""
Document analysis endpoints using rule engine.
"""
from fastapi import APIRouter, HTTPException
from fastapi_app.models import AnalyzeRequest, AnalyzeResponse, RuleFinding
from fastapi_app.config import settings
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["Analysis"])


@router.post("/", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze text using rule engine and optional AI suggestions.
    
    This endpoint integrates with your existing rule engine from Flask app.
    For now, it's a placeholder that you'll wire to your actual rules.
    """
    start_time = time.time()
    
    try:
        # Get text to analyze
        if request.text:
            text = request.text
        elif request.file_id:
            # TODO: Retrieve text from uploaded file by ID
            raise HTTPException(status_code=501, detail="File ID analysis not yet implemented")
        else:
            raise HTTPException(status_code=400, detail="Either text or file_id required")
        
        # Run rule checks (placeholder - integrate your existing rule engine)
        findings = []
        
        # Example findings (replace with actual rule engine integration)
        if "passive voice" in text.lower() or "was" in text.lower():
            findings.append(RuleFinding(
                rule_id="passive_voice",
                rule_name="Avoid Passive Voice",
                severity="warning",
                message="Passive voice detected",
                suggestion="Consider using active voice for clarity",
                matched_text="was configured"
            ))
        
        # Count by severity
        severity_counts = {
            "error": len([f for f in findings if f.severity == "error"]),
            "warning": len([f for f in findings if f.severity == "warning"]),
            "info": len([f for f in findings if f.severity == "info"])
        }
        
        # AI suggestions (if requested)
        ai_suggestions = None
        if request.use_ai:
            # TODO: Integrate with LLM service
            ai_suggestions = [
                "Consider making this sentence more concise",
                "You could improve clarity by restructuring this paragraph"
            ]
        
        processing_time = time.time() - start_time
        
        response = AnalyzeResponse(
            text_analyzed=text[:100] + "..." if len(text) > 100 else text,
            findings=findings,
            total_findings=len(findings),
            severity_counts=severity_counts,
            ai_suggestions=ai_suggestions,
            processing_time=round(processing_time, 3)
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules")
async def list_rules():
    """
    List all available writing rules.
    
    TODO: Integrate with your existing rule database.
    """
    # Placeholder - integrate with your actual rule storage
    rules = [
        {
            "id": "passive_voice",
            "name": "Avoid Passive Voice",
            "description": "Detects passive voice constructions",
            "severity": "warning",
            "category": "style",
            "enabled": True
        },
        {
            "id": "word_choice",
            "name": "Word Choice",
            "description": "Suggests better word alternatives",
            "severity": "info",
            "category": "vocabulary",
            "enabled": True
        },
        {
            "id": "sentence_length",
            "name": "Sentence Length",
            "description": "Warns about overly long sentences",
            "severity": "warning",
            "category": "readability",
            "enabled": True
        }
    ]
    
    return {
        "rules": rules,
        "total": len(rules)
    }


@router.post("/batch")
async def batch_analyze(texts: list[str]):
    """
    Analyze multiple texts in batch.
    Useful for processing entire documents.
    """
    try:
        results = []
        
        for i, text in enumerate(texts):
            request = AnalyzeRequest(text=text, use_ai=False)
            result = await analyze_text(request)
            results.append({
                "index": i,
                "analysis": result
            })
        
        return {
            "status": "success",
            "results": results,
            "total_processed": len(results)
        }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
