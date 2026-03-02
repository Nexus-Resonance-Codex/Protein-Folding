"""
BOINC Distributed Computing Integrators.
========================================
Scripts and wrappers for generating computational shards and work-units
capable of running seamlessly on the BOINC network.
"""
from typing import Any, Dict, List


def generate_boinc_workunits(sequence_data: List[float], shard_count: int = 100) -> List[Dict[str, Any]]:
    """
    Splits long protein target sequences into parallel
    computation shards for distributed BOINC processing.

    Args:
        sequence_data: Target array/tensor layout.
        shard_count: Number of chunks to split the workload.

    Returns:
        A list of JSON-serializable dictionaries formatted as BOINC WUs.
    """
    chunk_size = max(1, len(sequence_data) // shard_count)
    work_units = []

    for i in range(shard_count):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < shard_count - 1 else len(sequence_data)

        chunk = sequence_data[start_idx:end_idx]
        if not chunk:
            continue

        wu = {
            "boinc_wu_name": f"nrc_target_phi_shard_{i}",
            "start_index": start_idx,
            "end_index": end_idx,
            "job_data": chunk
        }
        work_units.append(wu)

    return work_units
