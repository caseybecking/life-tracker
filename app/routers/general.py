from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/track", tags=["tracking"])

@router.get("/nouns", response_model=List[schemas.Noun])
def get_all_nouns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all nouns in the system"""
    return crud.get_nouns(db, skip, limit)

@router.post("/nouns", response_model=schemas.Noun)
def create_noun(noun: schemas.NounCreate, db: Session = Depends(get_db)):
    """Create a new noun"""
    try:
        return crud.create_noun(db, noun)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create noun: {str(e)}"
        )

@router.get("/{noun}", response_model=Dict[str, Any])
def get_noun_data(noun: str, db: Session = Depends(get_db)):
    """Get all data for a specific noun (e.g., Banking, Person, Home)"""
    result = crud.get_noun_with_attributes(db, noun)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for noun: {noun}"
        )
    return result

@router.post("/{noun}")
def add_noun_data(
    noun: str,
    attribute: str,
    value: str,
    data: str,
    data_type: str = "string",
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Add data for a specific noun using the EAV model"""
    try:
        result = crud.track_data(db, noun, attribute, value, data, data_type, notes)
        return {"message": "Data tracked successfully", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track data: {str(e)}"
        )

@router.get("/{noun}/{attribute}", response_model=Dict[str, Any])
def get_attribute_data(noun: str, attribute: str, db: Session = Depends(get_db)):
    """Get all data for a specific attribute of a noun"""
    noun_data = crud.get_noun_with_attributes(db, noun)
    if not noun_data or attribute not in noun_data["attributes"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for {noun}.{attribute}"
        )
    return noun_data["attributes"][attribute]

# Example data endpoints for quick setup
@router.post("/setup/example-data")
def setup_example_tracking_data(db: Session = Depends(get_db)):
    """Set up example tracking data for testing"""
    try:
        # Banking examples
        crud.track_data(db, "Banking", "Schools First", "Name", "Schools First", "string")
        crud.track_data(db, "Banking", "SF_Checking", "Balance", "11818.71", "number")
        crud.track_data(db, "Banking", "Cuna", "Balance", "5000.00", "number")
        
        # Home examples
        crud.track_data(db, "Home", "Purifier", "Clean", "1", "boolean")
        crud.track_data(db, "Home", "Pool", "Chlorine", "0.5", "number")
        crud.track_data(db, "Home", "BBQ", "Clean", "1", "boolean")
        
        # Person examples
        crud.track_data(db, "Person", "Casey", "Weight", "165", "number")
        crud.track_data(db, "Person", "Casey", "Height", "5'10\"", "string")
        
        # Vehicle examples
        crud.track_data(db, "Vehicle", "4-Runner", "Fuel_Gallons", "16.516", "number")
        crud.track_data(db, "Vehicle", "4-Runner", "Miles", "125000", "number")
        
        # Hockey examples
        crud.track_data(db, "Hockey", "Main Squeeze", "Score", "5-4", "string")
        crud.track_data(db, "Hockey", "Main Squeeze", "Game", "2022-11-28", "date")
        
        return {"message": "Example tracking data created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create example data: {str(e)}"
        )

@router.post("/{noun}/{attribute}")
def add_attribute_data(
    noun: str,
    attribute: str,
    value: str,
    data: str,
    data_type: str = "string",
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Add data for a specific attribute of a noun"""
    try:
        result = crud.track_data(db, noun, attribute, value, data, data_type, notes)
        return {"message": "Attribute data tracked successfully", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track attribute data: {str(e)}"
        ) 