from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from app.database import SessionLocal


def calculate_average_risk_score_sync(db: Session, country: str) -> float:
    """
    Calculate average risk score for a country using all admin1 entries.
    Returns the score rounded to 2 decimal places.
    This is a synchronous helper function.
    """
    result = db.query(func.avg(models.ConflictData.score)).filter(
        models.ConflictData.country == country
    ).scalar()
    
    if result is None:
        raise ValueError(f"No data found for country: {country}")
    
    return round(float(result), 2)


def calculate_average_risk_score_background(country: str) -> float:
    """
    Background task to calculate average risk score for a country.
    This function creates its own database session and can be run as a background job.
    """
    db = SessionLocal()
    try:
        return calculate_average_risk_score_sync(db, country)
    finally:
        db.close()

