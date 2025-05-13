from datetime import datetime
import spacy
import dateparser
from typing import Optional, Dict, List, Tuple
import logging

nlp = spacy.load("en_core_web_sm")

def parse_query(query: str) -> Dict[str, List[Tuple[datetime, datetime]]]:
    """
    Returns structured date ranges and keywords from query.
    Handles both absolute and relative dates.
    """
    doc = nlp(query)
    results = {
        "date_ranges": [],
        "actions": [],
        "topics": []
    }

    # Extract date expressions and parse to date ranges
    date_expressions = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    
    # Fallback to full query parsing if no dates found
    if not date_expressions:
        date_expressions = [query]
        
    for expr in date_expressions:
        try:
            # Get date range (start/end) for expression
            parsed = dateparser.parse(
                expr,
                settings={
                    'PREFER_DATES_FROM': 'future',
                    'RETURN_AS_TIMEZONE_AWARE': False
                }
            )
            
            if parsed:
                # Handle single date vs date ranges
                if " to " in expr or "-" in expr:
                    start_end = [dateparser.parse(p) for p in expr.split(" to ")]
                    if len(start_end) == 2 and all(start_end):
                        results["date_ranges"].append((start_end[0], start_end[1]))
                else:
                    results["date_ranges"].append((parsed, parsed))
        except Exception as e:
            logging.error(f"Date parsing error: {e}")

    # Extract other entities
    results["actions"] = [tok.lemma_ for tok in doc if tok.pos_ == "VERB"]
    results["topics"] = [
        ent.text for ent in doc.ents 
        if ent.label_ in {"ORG", "PRODUCT", "GPE", "EVENT"}
    ]

    return results