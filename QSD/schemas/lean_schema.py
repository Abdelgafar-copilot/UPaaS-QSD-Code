from dataclasses import dataclass
from typing import List

# Lean WaferMetadata
@dataclass
class LeanLotInfo:
    BatchId: str
    LotId: str
    WaferId: str

# Lean WaferElectricalTesting
@dataclass
class LeanDieResult:
    DieId: str
    Pass: str
    DieLocation: str


@dataclass
class LeanWaferTestResult:
    TestResultId: int
    TestTypeId: str
    YieldPassed: float
    YieldFab: float
    DieResults: List[LeanDieResult]


@dataclass
class LeanTestRun:
    TestRunId: str
    TestTypeId: str
    YieldLimit: float
    YieldPassed: float
    YieldFab: float


@dataclass
class LeanWaferElectricalTesting:
    WaferTestId: int
    TestFlowId: str
    FacilityId: str
    TestRun: LeanTestRun
    WaferTestResult: LeanWaferTestResult


@dataclass
class LeanQSD:
    meta: LeanLotInfo
    electrical_test: LeanWaferElectricalTesting
