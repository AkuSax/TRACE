import os
import subprocess
import pandas as pd
from celery import Celery
from .database import SessionLocal
from . import models

# Celery application setup remains the same
celery_app = Celery(
    'worker',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True)
def run_trace_pipeline(self, job_id: int, input_file_path: str, sample_id: str, data_type: str):
    """
    A Celery task to execute the TRACE Snakemake pipeline.
    
    Args:
        job_id: The ID of the analysis job in the database.
        input_file_path: The absolute path to the uploaded file inside the container.
        sample_id: The unique identifier for the sample.
        data_type: The type of data ('WGS' or 'WGBS').
    """
    db = SessionLocal()
    try:
        # 1. Update job status to 'running'
        job = db.query(models.AnalysisJob).filter(models.AnalysisJob.id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        job.status = "running"
        job.results = "Snakemake pipeline has started."
        db.commit()

        # 2. Define pipeline paths and create a sample sheet for this specific job
        pipeline_dir = "/app/pipeline" # Path inside the Docker container
        sample_sheet_path = os.path.join(pipeline_dir, f"samples_{sample_id}.tsv")
        final_output_file = f"/app/pipeline/results/TRACE_v1.0.0_{sample_id}_feature_matrix.tsv"
        
        # Create a simple TSV for the one sample
        sample_data = {'sample_id': [sample_id], 'data_type': [data_type], 'accession_id': [sample_id], 'source_url': [input_file_path]}
        pd.DataFrame(sample_data).to_csv(sample_sheet_path, sep='\t', index=False)
        
        # 3. Construct and run the Snakemake command
        # This command is executed inside the 'worker' container
        command = [
            "snakemake",
            "--cores", "4",  # Use a reasonable number of cores
            "--snakefile", os.path.join(pipeline_dir, "Snakefile"),
            "--configfile", os.path.join(pipeline_dir, "config.yaml"),
            # Override the sample sheet in the config with our job-specific one
            "--config", f"samples={sample_sheet_path}",
            "--reason",
            "--keep-going",
            final_output_file # Specify the final target file
        ]
        
        print(f"Executing command: {' '.join(command)}")
        
        # We use check=True to raise an exception if Snakemake fails
        subprocess.run(command, check=True, capture_output=True, text=True)

        # 4. Update job status to 'complete' on success
        job.status = "complete"
        job.results = f"Pipeline finished successfully. Results at: {final_output_file}"
        db.commit()
        return {"status": "Success", "output": final_output_file}

    except subprocess.CalledProcessError as e:
        # If Snakemake fails, update status to 'failed' and log the error
        job.status = "failed"
        error_message = f"Snakemake pipeline failed.\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
        job.results = error_message
        db.commit()
        raise Exception(error_message)
    except Exception as e:
        job.status = "failed"
        job.results = f"An unexpected error occurred: {str(e)}"
        db.commit()
        raise
    finally:
        # Clean up the temporary sample sheet
        if os.path.exists(sample_sheet_path):
            os.remove(sample_sheet_path)
        db.close()