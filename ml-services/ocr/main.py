from fastapi import FastAPI
from services.row_grouper import (
    RowGrouper
)
row_grouper = RowGrouper()
from services.table_reconstructor import (
    TableReconstructor
)
table_reconstructor = (
    TableReconstructor()
)

from services.transaction_merger import (
    TransactionMerger
)

transaction_merger = (
    TransactionMerger()
)

from pydantic import BaseModel
# from standardize.services.standardization_service import (
#     StandardizationService
# )

# standardizer = StandardizationService()
from services.extraction_service import (
    ExtractionService
)

import ssl
import certifi

_original = ssl.create_default_context

def fixed_context(*args, **kwargs):
    return _original(cafile=certifi.where())

ssl.create_default_context = fixed_context

import aiohttp

print("aiohttp imported successfully")

app = FastAPI()

extractor = ExtractionService()


class ExtractRequest(BaseModel):
    file_path: str


@app.get("/health")
def health():

    return {
        "service": "ocr",
        "status": "healthy"
    }


@app.post("/extract")
def extract(
    request: ExtractRequest
):

    try:

        print(
            f"\nReceived file path:\n{request.file_path}"
        )

        result = extractor.extract(
            request.file_path
        )

        print(
            "\nExtraction completed successfully"
        )

        return result

    except Exception as e:

        print(
            f"\nOCR ERROR:\n{str(e)}"
        )

        import traceback

        traceback.print_exc()

        return {
            "status": "error",
            "message": str(e)
        }
    
from services.statement_understanding import (
    StatementUnderstandingEngine
)

engine = StatementUnderstandingEngine()


@app.post("/extract-and-understand")
def extract_and_understand(
    request: ExtractRequest
):

    extracted = extractor.extract(
        request.file_path
    )

    rows = extracted["rows"]

    structured = engine.process(
        rows
    )

    return {
        "raw_row_count": len(rows),
        "structured_count": len(structured),
        "structured_rows": structured
    }

@app.post("/full-pipeline")
def full_pipeline(
    request: ExtractRequest
):
    extracted = extractor.extract(
        request.file_path
    )

    structured = engine.process(
        extracted["rows"]
    )

    standardized = (
        standardizer.process(
            structured
        )
    )

    return {
        "structured_rows": structured,
        "standardized": [
            row.model_dump()
            for row in standardized
        ]
    }

@app.post("/debug-table")
def debug_table(
    request: ExtractRequest
):

    extracted = extractor.extract(
        request.file_path
    )

    rows = extracted["rows"]

    for idx, row in enumerate(rows):
        print(idx, row)

    return rows

@app.post("/debug-reconstruction")
def debug_reconstruction(
    request: ExtractRequest
):

    extracted = extractor.extract(
        request.file_path
    )

    rows = extracted["rows"]

    result = (
        engine.process(rows)
    )

    return result

@app.post("/debug-table-reconstruction-full")
def debug_table_reconstruction_full(
    request: ExtractRequest
):

    extracted = extractor.extract(
        request.file_path
    )

    ocr_rows = extracted["rows"]

    grouped_rows = (
        row_grouper.group_rows(
            ocr_rows
        )
    )

    reconstructed_table = (
        table_reconstructor
        .reconstruct(
            grouped_rows
        )
    )

    return {
        "ocr_boxes": len(
            ocr_rows
        ),
        "grouped_rows": grouped_rows,
        "reconstructed_table":
            reconstructed_table
    }

@app.post("/debug-merged-transactions")
def debug_merged_transactions(
    request: ExtractRequest
):

    extracted = extractor.extract(
        request.file_path
    )

    grouped = (
        row_grouper.group_rows(
            extracted["rows"]
        )
    )

    table = (
        table_reconstructor
        .reconstruct(grouped)
    )

    merged = (
        transaction_merger.merge(
            table
        )
    )

    return {
        "transaction_count":
            len(merged),
        "transactions":
            merged[:20]
    }

from services.transaction_normalizer import (
    TransactionNormalizer
)

normalizer = (
    TransactionNormalizer()
)

@app.post("/debug-normalized")
def debug_normalized(
    request: ExtractRequest
):

    extracted = extractor.extract(
        request.file_path
    )

    grouped = (
        row_grouper.group_rows(
            extracted["rows"]
        )
    )

    table = (
        table_reconstructor.reconstruct(
            grouped
        )
    )

    merged = (
        transaction_merger.merge(
            table
        )
    )

    normalized = []

    for transaction in merged:

        normalized.append(
            normalizer.normalize(
                transaction
            )
        )

    return {
        "count":
            len(normalized),
        "transactions":
            normalized[:20]
    }