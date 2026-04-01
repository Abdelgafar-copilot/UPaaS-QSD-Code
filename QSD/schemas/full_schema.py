from dataclasses import dataclass
from datetime import datetime
from typing import List

# WaferMetaData
@dataclass
class WaferSpecifications:
    Diameter: float
    BaseMaterial: str
    thicknessRaw: float
    thicknessFinished: float
    Dopant: str
    IngotPulling: str
    ResistivityClass: float

@dataclass
class ProductInformation:
    ProductNumber: str
    Technology: str
    BasicType: str
    chipsPerWafer: int
    chipSize: str

@dataclass
class LotInfo:
    LotId: str
    BatchId: str
    WaferId: str
    LotPosition: str
    BatchPosition: str
    Manufacturer: str
    WaferSupplier: str
    ProductionSite: str
    Facility: str
    FacilityId: str
    Location: str
    LocationId: str
    workRouteId: str
    operationId: str
    equipId: str
    lastUpdate: datetime
    globalRouteId: str
    WaferSpecifications: WaferSpecifications
    ProductInformation: ProductInformation

# WaferElectricalTesting
@dataclass
class DieResult:
    DieId: str
    HBIN: str
    SBIN: str
    Pass: str
    DieLocation: str

@dataclass
class TestRun:
    TestRunId: str
    TestTypeId: str
    TimestampStart: datetime
    TimestampEnd: datetime
    TestEquipment: str
    ProbeCard: str
    Tester: str
    TestProgram: str
    YieldLimit: float
    Passed: int
    YieldPassed: float
    YieldFab: float

@dataclass
class WaferTestResult:
    TestResultId: int
    TestTypeId: str
    Pass: int
    YieldPassed: float
    YieldFab: float
    DieResults: List[DieResult]

@dataclass
class WaferElectricalTesting:
    WaferTestId: int
    TestFlowId: str
    TimestampStart: datetime
    TimestampEnd: datetime
    QuantityIn: int
    QuantityOut: int
    FacilityId: str
    LocationId: str
    TestRun: TestRun
    WaferTestResult: WaferTestResult 

# Full QSD wrapper
@dataclass
class QualifiedSyntheticData:
    meta: LotInfo
    electrical_test: WaferElectricalTesting
