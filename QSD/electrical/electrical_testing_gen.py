import random
from typing import Tuple
import pandas as pd
from utils.utils import (
    generate_wafer_test_id, generate_test_flow_id, generate_facility_and_location,
    generate_test_timestamps, generate_test_run_info, generate_test_equipment
)
from electrical.test_result_gen import WaferSummary, generate_wafer_test_result
from schemas.full_schema import (
    WaferElectricalTesting,
    TestRun,
    WaferTestResult
)

def generate_wafer_electrical_testing(
        df_blank: pd.DataFrame,
        usable_radius_mm: float,
        base_yield: float = 0.95
) -> Tuple[WaferElectricalTesting, pd.DataFrame, WaferSummary]:
    wafer_test_id = generate_wafer_test_id()
    test_flow_id = generate_test_flow_id()

    facility_id, location_id = generate_facility_and_location()
    timestamp_start, timestamp_end = generate_test_timestamps()

    wafer_result, df_filled, summary = generate_wafer_test_result(
        df_blank=df_blank, 
        usable_radius_mm=usable_radius_mm,
        base_yield=base_yield
    )
    
    test_run_id, test_type_id, run_start, run_end = generate_test_run_info()
    probe_card, tester, test_program = generate_test_equipment()

    yield_limit = round(random.uniform(0.95, 0.99), 4)

    test_run = TestRun(
        TestRunId=test_run_id,
        TestTypeId=test_type_id,
        TimestampStart=run_start,
        TimestampEnd=run_end,
        TestEquipment=f"{tester} / {probe_card}",
        ProbeCard=probe_card,
        Tester=tester,
        TestProgram=test_program,
        YieldLimit=yield_limit,
        Passed=int(summary["yield_passed"] >= yield_limit),
        YieldPassed=round(summary["yield_passed"] * 100, 2),
        YieldFab=round(summary["yield_fab"] * 100, 2)
    )

    wafer_test_result = WaferTestResult(
        TestResultId=random.randint(1, 99999),
        TestTypeId=test_type_id,
        Pass=summary["quantity_out"],
        YieldPassed=round(summary["yield_passed"], 4),
        YieldFab=round(summary["yield_fab"], 4),
        DieResults=wafer_result["die_results"]
    )

    wafer_electrical_testing = WaferElectricalTesting(
        WaferTestId=wafer_test_id,
        TestFlowId=test_flow_id,
        TimestampStart=timestamp_start,
        TimestampEnd=timestamp_end,
        QuantityIn=summary["quantity_in"],
        QuantityOut=summary["quantity_out"],
        FacilityId=facility_id,
        LocationId=location_id,
        TestRun=test_run,
        WaferTestResult=wafer_test_result
    )

    return wafer_electrical_testing, df_filled, summary
