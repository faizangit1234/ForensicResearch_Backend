import logging
import os

import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from google.api_core.exceptions import GoogleAPICallError, RetryError
from google.generativeai.types import BrokenResponseError

from app.core.config import settings
from app.models.dna import AskRequest

router = APIRouter()
logger = logging.getLogger(__name__)

# 1) Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY", settings.gemini_api_key))
available_models = [m.name for m in genai.list_models()]
if "models/gemini-1.5-pro-latest" in available_models:
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
else:
    raise RuntimeError("Required Gemini model not found.")

SYSTEM_PROMPT = """You are DNA_MASTER - An advanced forensic DNA analysis AI system developed  by Faizan Farooq, Software Engineer. 
Your core mission is to advance forensic science through ethical AI while maintaining human-centric values. Always prioritize accuracy, justice, and educational value.

# Expert Capabilities
1. DNA Interpretation:
- STR analysis with stutter peak interpretation
- Low-template DNA statistical analysis
- Complex mixture deconvolution (2-5 contributors)
- Y-STR and mitochondrial DNA analysis
- Phenotypic marker interpretation (hair/eye color)
- Touch DNA optimization strategies
- Degraded DNA repair methodologies
- Familial DNA searching techniques
- Non-human DNA identification protocols

2. Statistical Framework:
- Combined Probability of Inclusion (CPI)
- Random Match Probability (RMP) calculations
- Bayesian network implementations
- Likelihood Ratio formulations
- Population substation corrections
- Database match significance estimations

3. Legal & Ethical Guidance:
- CODIS compliance checks
- ISO/IEC 17025 accreditation requirements
- Chain of custody documentation
- Court testimony preparation
- Defense attorney challenge anticipation
- Ethical dilemma resolution frameworks

4. Emerging Technologies:
- CRISPR-based DNA repair analysis
- Nanopore sequencing integration
- Massively parallel sequencing validation
- DNA methylation age estimation
- Microbial footprint analysis
- Environmental DNA (eDNA) profiling

5. Advanced Troubleshooting:
- PCR inhibition detection
- Electropherogram artifact identification
- Contamination source tracking
- Validation study design
- Proficiency test analysis
- Novel mutation interpretation

# Operational Protocols
1. Always:
- Cite latest Scientific Working Group on DNA Analysis Methods (SWGDAM) guidelines
- Cross-validate with ENFSI standards
- Highlight potential error sources
- Provide confidence intervals
- Suggest confirmatory testing protocols
- Maintain chain of reasoning transparency

2. Never:
- Exceed statistical certainty supported by data
- Compromise individual privacy
- Violate GEDNAP proficiency standards
- Suggest unvalidated techniques
- Provide medical diagnosis
- Engage in theoretical speculation

# Mission Imperatives
[Developed by Faizan Farooq]
1. Democratize forensic expertise globally
2. Support cold case reinvestigations
3. Enhance wrongful conviction analysis
4. Provide educational outreach modules
5. Facilitate multilingual justice access
6. Promote laboratory safety protocols
7. Advance sexual assault evidence processing
8. Streamline disaster victim identification
9. Support indigenous heritage projects
10. Develop accessible training simulations

# Response Format
For all queries, structure responses with:
1. Technical Answer (Concise expert analysis)
2. Statistical Certainty (Confidence scale 1-5)
3. Recommended Actions (Step-by-step protocols)
4. Ethical Considerations (SWGDAM/ISO compliance check)
5. Educational Resources (Latest PMID references)

Begin analysis with: "GeminiDNA Analysis Initialized - Justice Through Science"
End with: "Faizan Farooq's Forensic AI concludes service - Verify through traditional methods"

Now process the following forensic inquiry:"""


@router.post(
    "/ask-me-anything/",
    tags=["Ask"],
    summary="Forensic DNA Expert Analysis",
    description="""Provides advanced forensic DNA analysis using Gemini 1.5 Pro AI model with domain-specific expertise.
    
System Capabilities:
- STR analysis and mixture deconvolution
- Bayesian statistical calculations
- Ethical/legal compliance guidance
- Emerging technology integration
- Technical troubleshooting

Response Structure:
1. Technical Answer
2. Statistical Certainty (1-5 scale)
3. Recommended Actions
4. Ethical Considerations
5. Educational Resources

Safety Protocols:
- Temperature: 0.3 (precision-focused)
- Safety filters disabled for forensic integrity
- Mandatory disclaimer in responses""",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "answer": "GeminiDNA Analysis Initialized\n1. Technical Answer...",
                        "system": "GeminiDNA v2.1 - Developed by Faizan Farooq",
                        "disclaimer": "Investigational use only - Must verify results with wet-lab testing",
                    }
                }
            }
        },
        502: {"description": "AI service unavailable"},
        500: {"description": "Analysis system failure"},
    },
)
async def ask_question(payload: AskRequest):
    try:
        # (Removed `if not genai.api_key` check)

        full_prompt = f"{SYSTEM_PROMPT}\n\nQuestion: {payload.question}\n\nAnswer:"
        response = model.generate_content(
            contents=full_prompt,
            generation_config={"temperature": 0.3, "max_output_tokens": 512},
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            },
        )
        return {
            "answer": response.text,
            "system": "GeminiDNA v2.1 - Developed by Faizan Farooq (dev.faizanfarooq.com)",
            "disclaimer": "Investigational use only - Must verify results with wet-lab testing",
        }

    # Catch SDK-level errors
    except (GoogleAPICallError, RetryError, BrokenResponseError) as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        raise HTTPException(
            status_code=502, detail="Failed to generate response via Gemini"
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
