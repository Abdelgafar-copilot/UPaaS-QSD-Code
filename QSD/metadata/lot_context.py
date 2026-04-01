from dataclasses import dataclass
from datetime import datetime

@dataclass
class LotContext:
    Manufacturer: str
    WaferSupplier: str
    ProductionSite: str
    Location: str
    LocationId: str
    Facility: str
    FacilityId: str

    BaseMaterial: str
    ThicknessRaw: float
    ThicknessFinished: float
    Dopant: str
    IngotPulling: str
    ResistivityClass: float

    Technology: str
    ProductNumber: str
    BasicType: str

    workRouteId: str
    operationId: str
    equipId: str
    globalRouteId: str
    LastUpdate: datetime

    Diameter: float
    DieWidth: float
    DieHeight: float
