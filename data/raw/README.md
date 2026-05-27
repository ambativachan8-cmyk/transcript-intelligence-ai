Raw transcript files are not included in this public repository.

To run the pipeline, place an authorized local dataset at `data/raw/dataset/` with the expected transcript export structure, or pass a custom folder with:

```powershell
.\.venv\Scripts\python.exe run_pipeline.py --raw-dir "path\to\dataset"
```

Do not commit private transcripts, customer records, personal email data, credentials, or row-level generated outputs.
