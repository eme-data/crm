"""
Routes API pour l'import de données
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import tempfile

from app.database import get_db
from app.services.excel_import import ExcelImportService
from app.api.dependencies import get_current_active_admin
from app.models.user import User


router = APIRouter()


@router.post("/excel/detect-structure")
async def detect_excel_structure(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Analyser la structure d'un fichier Excel
    
    Retourne les noms de feuilles et leurs colonnes.
    
    Requiert: Admin seulement
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être au format Excel (.xlsx ou .xls)"
        )
    
    try:
        # Sauvegarder temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        #Analyser la structure
        structure = ExcelImportService.detect_excel_structure(tmp_path)
        
        # Nettoyer
        os.unlink(tmp_path)
        
        return {
            "filename": file.filename,
            "sheets": structure
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse du fichier: {str(e)}"
        )


@router.post("/excel/materials")
async def import_materials_from_excel(
    file: UploadFile = File(...),
    sheet_name: str = "Matériaux",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Importer des matériaux depuis un fichier Excel
    
    Format attendu :
    - Code | Nom FR | Nom RO | Unité | Prix EUR | Prix LEI | Fournisseur
    
    Requiert: Admin seulement
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être au format Excel (.xlsx ou .xls)"
        )
    
    try:
        # Sauvegarder temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Importer
        result = ExcelImportService.import_materials_from_excel(
            tmp_path,
            db,
            sheet_name=sheet_name
        )
        
        # Nettoyer
        os.unlink(tmp_path)
        
        return {
            "message": "Import réussi",
            "statistics": result,
            "file": file.filename,
            "sheet": sheet_name
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import: {str(e)}"
        )


@router.post("/excel/services")
async def import_services_from_excel(
    file: UploadFile = File(...),
    sheet_name: str = "Services",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Importer des services depuis un fichier Excel
    
    Format attendu :
    - Code | Nom | Unité | Prix Net | Prix Brut
    
    Requiert: Admin seulement
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être au format Excel (.xlsx ou .xls)"
        )
    
    try:
        # Sauvegarder temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Importer
        result = ExcelImportService.import_services_from_excel(
            tmp_path,
            db,
            sheet_name=sheet_name
        )
        
        # Nettoyer
        os.unlink(tmp_path)
        
        return {
            "message": "Import réussi",
            "statistics": result,
            "file": file.filename,
            "sheet": sheet_name
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import: {str(e)}"
        )
