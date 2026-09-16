from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.auth import require_roles
from app.schemas.kpi import (
    KPICatalogResponse,
    KPICreate,
    KPIResponse,
    KPIUpdate,
)
from app.services.kpi_service import (
    create_kpi,
    deactivate_kpi,
    get_kpi_by_id,
    get_kpi_catalog,
    get_kpi_catalog_by_category,
    get_patient_kpis,
    update_kpi,
)


router = APIRouter(
    prefix="/kpis",
    tags=["KPIs"],
)


@router.get(
    "/catalog",
    response_model=List[KPICatalogResponse],
)
def get_kpi_catalog_endpoint(
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_kpi_catalog()


@router.get(
    "/catalog/{category}",
    response_model=List[KPICatalogResponse],
)
def get_kpi_catalog_category_endpoint(
    category: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_kpi_catalog_by_category(category)


@router.post(
    "/",
    response_model=KPIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_kpi_endpoint(
    kpi: KPICreate,
    current_user: dict = Depends(require_roles("admin", "doctor", "researcher")),
):
    return create_kpi(kpi)


@router.get(
    "/patient/{patient_id}",
    response_model=List[KPIResponse],
    summary="Get patient KPIs by UUID or patient code",
)
def get_patient_kpis_endpoint(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_patient_kpis(patient_id)


@router.get(
    "/{kpi_id}",
    response_model=KPIResponse,
)
def get_kpi_endpoint(
    kpi_id: UUID,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_kpi_by_id(str(kpi_id))


@router.put(
    "/{kpi_id}",
    response_model=KPIResponse,
)
def update_kpi_endpoint(
    kpi_id: UUID,
    kpi: KPIUpdate,
    current_user: dict = Depends(require_roles("admin", "doctor", "researcher")),
):
    return update_kpi(str(kpi_id), kpi)


@router.delete(
    "/{kpi_id}",
)
def deactivate_kpi_endpoint(
    kpi_id: UUID,
    current_user: dict = Depends(require_roles("admin", "doctor", "researcher")),
):
    return deactivate_kpi(str(kpi_id))
