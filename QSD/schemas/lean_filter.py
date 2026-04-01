from schemas.full_schema import QualifiedSyntheticData
from schemas.lean_schema import (
    LeanLotInfo,
    LeanDieResult,
    LeanWaferTestResult,
    LeanTestRun,
    LeanWaferElectricalTesting,
    LeanQSD,
)


def convert_qsd_to_lean(full_qsd: QualifiedSyntheticData):
    """
    Convert a full QualifiedSyntheticData object into a LeanQSD object.
    """

    # Meta
    meta = full_qsd.meta
    lean_meta = LeanLotInfo(
        BatchId=meta.BatchId,
        LotId=meta.LotId,
        WaferId=meta.WaferId
    )

    # Electrical
    et = full_qsd.electrical_test
    tr = et.TestRun
    wr = et.WaferTestResult

    # DieResults
    lean_die_results = [
        LeanDieResult(
            DieId=d.DieId,
            Pass=d.Pass,
            DieLocation=d.DieLocation
        )
        for d in wr.DieResults
    ]

    # WaferTestResults
    lean_wr = LeanWaferTestResult(
        TestResultId=wr.TestResultId,
        TestTypeId=wr.TestTypeId,
        YieldPassed=wr.YieldPassed,
        YieldFab=wr.YieldFab,
        DieResults=lean_die_results
    )

    # TestRun
    lean_tr = LeanTestRun(
        TestRunId=tr.TestRunId,
        TestTypeId=tr.TestTypeId,
        YieldLimit=tr.YieldLimit,
        YieldPassed=tr.YieldPassed,
        YieldFab=tr.YieldFab
    )

    # Electrical wrapper
    lean_et = LeanWaferElectricalTesting(
        WaferTestId=et.WaferTestId,
        TestFlowId=et.TestFlowId,
        FacilityId=et.FacilityId,
        TestRun=lean_tr,
        WaferTestResult=lean_wr
    )

    # Wrapper
    lean_qsd = LeanQSD(
        meta=lean_meta,
        electrical_test=lean_et
    )

    return lean_qsd
