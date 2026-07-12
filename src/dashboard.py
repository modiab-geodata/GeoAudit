import pandas as pd
from quality_score import calculate_quality_score
from quality_results import get_quality_results

def get_dashboard_metrics():
    summary = calculate_quality_score()
    details = get_quality_results()
    metrics = {
        "nb_layers":
            summary["table_name"].nunique(),
        "average_score":
            round(
                summary["score_quality"].mean(),
                2
            ),
        "total_controls":
            len(details),
        "total_errors":
            len(
                details[
                    details["status"]=="ERROR"
                ]
            )

    }

    return metrics
