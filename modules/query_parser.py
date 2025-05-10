import spacy
import dateparser
from datetime import datetime

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def parse_date(query):
    """
    Parse dates from the query using dateparser.
    """
    parsed_date = dateparser.parse(query)
    return parsed_date if parsed_date else None

def extract_keywords(query):
    """
    Extract keywords like date references, topics, and actions from the query.
    """
    # Process the query with spaCy
    doc = nlp(query)

    # Extract dates
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    actions = [token.text for token in doc if token.pos_ == "VERB"]
    topics = [ent.text for ent in doc.ents if ent.label_ == "ORG" or ent.label_ == "PRODUCT"]  # You can also add other entity types like "GPE" for locations

    # Use dateparser to find any implicit date references in the query
    parsed_date = parse_date(query)
    
    return {
        "dates": dates if dates else [parsed_date],  # Default to parsed date if none are found
        "actions": actions,
        "topics": topics
    }

