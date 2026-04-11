import mlflow
import datetime

def log_request(endpoint: str, input_length: int, output_length: int):
    """Log API request metrics to MLflow."""
    with mlflow.start_run(run_name=f"request_{endpoint.replace('/', '_')}"):
        mlflow.log_param("endpoint", endpoint)
        mlflow.log_param("timestamp", datetime.datetime.now().isoformat())
        mlflow.log_metric("input_length", input_length)
        mlflow.log_metric("output_length", output_length)
        mlflow.log_metric("compression_ratio", 
                         round(output_length / input_length, 3) if input_length > 0 else 0)