from simtools.core.benchmarking import build_benchmark_result, normalize_task_metrics


def test_task_metrics_defaults_to_unscored_result():
    metrics = normalize_task_metrics({})

    assert metrics == {
        "schema_version": "simtools.task_metrics.v1",
        "success": None,
        "score": None,
        "steps_completed": None,
        "collisions": None,
        "custom": {},
    }


def test_benchmark_result_defaults_to_not_scored_task_metrics():
    result = build_benchmark_result()

    assert result == {
        "schema_version": "simtools.benchmark_result.v1",
        "status": "not_scored",
        "task_metrics": {
            "schema_version": "simtools.task_metrics.v1",
            "success": None,
            "score": None,
            "steps_completed": None,
            "collisions": None,
            "custom": {},
        },
    }
