"""
Lightweight contract analysis that prepares structured output for Sara.

No external AI calls — this tool parses the document, identifies risk
categories, and organizes provisions into a prompt-ready format that
Sara processes with her own judgment.
"""

import re
from typing import Dict, Any, List, Optional

from core.reader import read_docx
from core.extractor import extract_structure, PROVISION_PATTERNS


# Risk categories by contract type (adapted from Ambrose)
RISK_CATEGORIES = {
    "purchase and sale agreement": [
        "Buyer Closing Escapes",
        "Deposit at Risk",
        "Title/Survey Cure Obligations",
        "Representation Exposure",
        "Indemnification Scope",
        "Closing Timeline Risk",
        "Financing Contingency",
        "Due Diligence Termination Rights",
        "Casualty/Condemnation Risk",
        "Default Remedies",
    ],
    "lease": [
        "Rent Escalation Exposure",
        "Landlord Control of Property",
        "Tenant Default Remedies",
        "Assignment/Subletting Restrictions",
        "Operating Expense Passthrough",
        "Renewal/Extension Options",
        "Early Termination Rights",
        "Maintenance and Repair Obligations",
        "Insurance Requirements",
        "Casualty/Condemnation",
        "Holdover Provisions",
        "Security Deposit",
    ],
    "development agreement": [
        "Performance Timeline Risk",
        "Cost Overrun Allocation",
        "Change Order Approval",
        "Completion Standards",
        "Warranty Scope",
        "Indemnification Obligations",
        "Default and Cure Rights",
        "Termination Triggers",
    ],
    "loan agreement": [
        "Default Triggers",
        "Cross-Default Provisions",
        "Prepayment Restrictions",
        "Financial Covenant Compliance",
        "Collateral Requirements",
        "Representation Exposure",
        "Acceleration Rights",
    ],
}

# Keywords that signal specific risk categories
CATEGORY_SIGNALS = {
    "Deposit at Risk": [r'\bdeposit\b', r'\bearnest\s+money\b'],
    "Title/Survey Cure Obligations": [r'\btitle\b', r'\bsurvey\b', r'\bencumbrance\b'],
    "Representation Exposure": [r'\brepresents?\b', r'\bwarrants?\b'],
    "Indemnification Scope": [r'\bindemnif\b', r'\bhold\s+harmless\b'],
    "Closing Timeline Risk": [r'\bclosing\s+date\b', r'\bextension\b', r'\btime\s+is\s+of\s+the\s+essence\b'],
    "Financing Contingency": [r'\bfinancing\b', r'\bloan\b', r'\bmortgage\b'],
    "Due Diligence Termination Rights": [r'\bdue\s+diligence\b', r'\binspection\b', r'\bfeasibility\b'],
    "Casualty/Condemnation Risk": [r'\bcasualty\b', r'\bcondemnation\b', r'\beminent\s+domain\b'],
    "Default Remedies": [r'\bdefault\b', r'\bbreach\b', r'\bliquidated\s+damages\b', r'\bspecific\s+performance\b'],
    "Buyer Closing Escapes": [r'\bcondition\s+(?:precedent|to\s+closing)\b', r'\btermination\s+right\b'],
    "Rent Escalation Exposure": [r'\brent\b.*\bincrease\b', r'\bescalat\b', r'\bCPI\b'],
    "Assignment/Subletting Restrictions": [r'\bassign\b', r'\bsublet\b', r'\btransfer\b'],
    "Operating Expense Passthrough": [r'\boperating\s+expense\b', r'\bCAM\b', r'\bcommon\s+area\b'],
    "Renewal/Extension Options": [r'\brenewal?\b', r'\bextension\b', r'\boption\s+to\s+renew\b'],
    "Early Termination Rights": [r'\bearly\s+termination\b', r'\bterminate\b.*\bprior\b'],
    "Holdover Provisions": [r'\bholdover\b'],
    "Security Deposit": [r'\bsecurity\s+deposit\b'],
    "Default Triggers": [r'\bevent\s+of\s+default\b', r'\bdefault\b'],
    "Cross-Default Provisions": [r'\bcross.?default\b'],
    "Prepayment Restrictions": [r'\bprepay\b', r'\bearly\s+repayment\b'],
    "Acceleration Rights": [r'\baccelerat\b'],
}


def analyze_contract(
    docx_path: str,
    representation: str,
    focus_areas: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Analyze a contract and return structured, prompt-ready output.

    Args:
        docx_path: Path to the .docx file.
        representation: Who the client is (e.g., "buyer", "seller", "tenant").
        focus_areas: Optional list of specific areas to focus on.

    Returns:
        Dict with risk_categories, provisions_by_concept, representation, and structure.
    """
    structure = extract_structure(docx_path)
    parsed = read_docx(docx_path)
    paragraphs = [p for p in parsed["content"] if p["type"] == "paragraph"]

    contract_type = _detect_contract_type(paragraphs)
    categories = RISK_CATEGORIES.get(contract_type, RISK_CATEGORIES["purchase and sale agreement"])

    if focus_areas:
        categories = [c for c in categories if any(f.lower() in c.lower() for f in focus_areas)] or categories

    risk_analysis = _map_risk_categories(paragraphs, categories)

    provisions_by_concept = {}
    for prov in structure["provisions"]:
        ptype = prov["type"]
        if ptype not in provisions_by_concept:
            provisions_by_concept[ptype] = []
        provisions_by_concept[ptype].append(prov)

    return {
        "contract_type": contract_type,
        "representation": representation,
        "risk_categories": risk_analysis,
        "provisions_by_concept": provisions_by_concept,
        "defined_terms": structure["defined_terms"],
        "sections": structure["sections"],
        "summary": {
            "total_paragraphs": len(paragraphs),
            "categories_identified": len([r for r in risk_analysis if r["paragraphs"]]),
            "total_provisions_classified": len(structure["provisions"]),
        },
    }


def _detect_contract_type(paragraphs: List[Dict]) -> str:
    """Detect contract type from document content."""
    full_text = " ".join(p["text"] for p in paragraphs[:10]).lower()
    type_signals = {
        "purchase and sale agreement": [r'purchase\s+and\s+sale', r'purchase\s+agreement'],
        "lease": [r'\blease\b', r'\blandlord\b', r'\btenant\b', r'\brent\b'],
        "development agreement": [r'development\s+agreement', r'\bdeveloper\b'],
        "loan agreement": [r'loan\s+agreement', r'\blender\b', r'\bborrower\b', r'\bpromissory\b'],
    }
    for ctype, patterns in type_signals.items():
        for pattern in patterns:
            if re.search(pattern, full_text):
                return ctype
    return "purchase and sale agreement"


def _map_risk_categories(paragraphs: List[Dict], categories: List[str]) -> List[Dict]:
    """Map risk categories to paragraphs where they appear."""
    results = []
    for category in categories:
        signals = CATEGORY_SIGNALS.get(category, [])
        matching_paras = []
        for para in paragraphs:
            text = para["text"]
            if not text or len(text) < 20:
                continue
            for signal in signals:
                if re.search(signal, text, re.IGNORECASE):
                    matching_paras.append({
                        "para_id": para["id"],
                        "section_ref": para.get("section_ref"),
                        "text_preview": text[:150],
                    })
                    break
        results.append({
            "category": category,
            "paragraphs": matching_paras,
            "count": len(matching_paras),
        })
    return results


def format_for_display(result: Dict[str, Any]) -> str:
    """Format analysis result as readable text for Sara."""
    lines = []
    lines.append(f"Contract Analysis: {result['contract_type'].title()}")
    lines.append(f"Representation: {result['representation']}")
    s = result["summary"]
    lines.append(f"Paragraphs: {s['total_paragraphs']} | Categories found: {s['categories_identified']} | Provisions classified: {s['total_provisions_classified']}")
    lines.append("")

    lines.append("--- Risk Categories ---")
    for rc in result["risk_categories"]:
        if rc["paragraphs"]:
            lines.append(f"  {rc['category']} ({rc['count']} paragraphs)")
            for p in rc["paragraphs"][:3]:
                lines.append(f"    [{p['para_id']}] {p['text_preview'][:100]}...")
            if rc["count"] > 3:
                lines.append(f"    ... and {rc['count'] - 3} more")
    lines.append("")

    lines.append("--- Provisions by Concept ---")
    for concept, provisions in result["provisions_by_concept"].items():
        lines.append(f"  {concept}: {len(provisions)}")
    lines.append("")

    lines.append(f"--- Defined Terms ({len(result['defined_terms'])}) ---")
    for term in result["defined_terms"][:10]:
        lines.append(f"  \"{term['term']}\"")
    if len(result["defined_terms"]) > 10:
        lines.append(f"  ... and {len(result['defined_terms']) - 10} more")

    return "\n".join(lines)
