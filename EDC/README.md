# EDC Data Exchange Collection

This folder contains everything needed to run and document a complete EDC data exchange demo:

- A request collection that can be imported in Postman or Bruno.
- Result logs from a successful end-to-end exchange.

## Folder Contents

- `EDC data exchange collection.json`: request collection for the full flow.
- `data-offer-results.md`: captured responses for a successful run.

## Import the Collection

Import `EDC data exchange collection.json` into your preferred API client (for example Postman or Bruno), then set the required environment variables for your EDC setup before running the requests.

## Successful Run Logs

The file `data-offer-results.md` contains captured responses from a successful run, including:

- Asset/Policy/Contract Definition creation responses.
- Catalog response with available distributions.
- EDR retrieval responses.
- Data Address response used for the final data fetch.

Sensitive token values in logs are redacted where needed.