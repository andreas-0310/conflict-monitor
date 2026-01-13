from typing import List
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from math import ceil
from datetime import datetime
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, get_current_admin_user
from app.background_tasks import calculate_average_risk_score_background

router = APIRouter(prefix="/conflictdata", tags=["Conflict Data"])


@router.get("", response_model=schemas.ConflictDataListResponse)
def get_conflict_data(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    List conflict data for each country with pagination.
    Returns 20 countries per page by default.
    Note: Each country can have multiple admin1 entries.
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20

    all_countries_query = db.query(
        models.ConflictData.country
    ).distinct().order_by(models.ConflictData.country)
    
    total_countries = all_countries_query.count()
    offset = (page - 1) * page_size
    countries_page = all_countries_query.offset(offset).limit(page_size).all()
    countries_list = [country[0] for country in countries_page]
    
    if not countries_list:
        return {
            "items": [],
            "total": total_countries,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total_countries / page_size) if total_countries > 0 else 0
        }
    
    conflict_data = db.query(models.ConflictData).filter(
        models.ConflictData.country.in_(countries_list)
    ).order_by(models.ConflictData.country, models.ConflictData.admin1).all()
    
    country_dict = {}
    for data in conflict_data:
        if data.country not in country_dict:
            country_dict[data.country] = []
        country_dict[data.country].append(
            schemas.CountryAdmin1Response(
                admin1=data.admin1,
                score=data.score,
                population=data.population,
                events=data.events
            )
        )
    
    items = [
        schemas.CountryDetailResponse(
            country=country_name,
            admin1_details=country_dict.get(country_name, [])
        )
        for country_name in countries_list
    ]
    
    total_pages = ceil(total_countries / page_size) if total_countries > 0 else 0
    
    return {
        "items": items,
        "total": total_countries,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{country}", response_model=List[schemas.CountryDetailResponse])
def get_conflict_data_by_country(
    country: str,
    db: Session = Depends(get_db)
):
    """
    Get conflict data by country name.
    Supports multiple countries (comma-separated).
    Returns admin1 details including names, conflict risk scores, population, and events.
    """
    countries = [c.strip() for c in country.split(",")]
    conflict_data = db.query(models.ConflictData).filter(
        models.ConflictData.country.in_(countries)
    ).all()
    
    if not conflict_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for country/countries: {country}"
        )

    country_dict = {}
    for data in conflict_data:
        if data.country not in country_dict:
            country_dict[data.country] = []
        country_dict[data.country].append(
            schemas.CountryAdmin1Response(
                admin1=data.admin1,
                score=data.score,
                population=data.population,
                events=data.events
            )
        )
    result = [
        schemas.CountryDetailResponse(
            country=country_name,
            admin1_details=details
        )
        for country_name, details in country_dict.items()
    ]
    
    return result


@router.get("/{country}/riskscore", response_model=schemas.RiskScoreResponse)
async def get_country_risk_score(
    country: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Get the average risk score for a country.
    Uses a background job to calculate the average risk scores across admin1's.
    """
    country_data = db.query(models.ConflictData).filter(
        models.ConflictData.country == country
    ).first()
    
    if not country_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for country: {country}"
        )

    loop = asyncio.get_event_loop()
    average_score = await loop.run_in_executor(
        None, 
        calculate_average_risk_score_background, 
        country
    )
    
    return schemas.RiskScoreResponse(
        country=country,
        average_risk_score=average_score,
        calculated_at=datetime.now()
    )


@router.post("/{admin1}/userfeedback", response_model=schemas.UserFeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_user_feedback(
    admin1: str,
    feedback: schemas.UserFeedbackCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add user feedback about an admin1 region.
    Authentication required.
    Feedback text must be between 10 and 500 characters.
    """
    try:
        conflict_data = db.query(models.ConflictData).filter(
            models.ConflictData.admin1 == admin1
        ).first()
        
        if not conflict_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for admin1: {admin1}"
            )
        
        db_feedback = models.UserFeedback(
            user_id=current_user.id,
            admin1=admin1,
            country=conflict_data.country,
            feedback_text=feedback.feedback_text
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        return db_feedback
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_conflict_data(
    delete_request: schemas.ConflictDataDelete,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete conflict data entry by country and admin1 combination.
    Admin only endpoint.
    """
    try:
        conflict_data = db.query(models.ConflictData).filter(
            and_(
                models.ConflictData.country == delete_request.country,
                models.ConflictData.admin1 == delete_request.admin1
            )
        ).first()
        
        if not conflict_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for country: {delete_request.country}, admin1: {delete_request.admin1}"
            )
        
        db.delete(conflict_data)
        db.commit()
        
        return None
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

