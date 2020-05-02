# South Atlantic Conservation Blueprint Simple Viewer - API

## Overview

Use case: user uploads shapefile (AOI) representing a small area, this generates a custom PDF report including maps and summaries of overlap with Blueprint and indicators.

## API requests

To make custom report requests using HTTPie:

```
http -f POST :5000/api/reports/custom/ name="<area name>" token=="<token from .env>" file@<filename>.zip
```

This creates a background job and returns:

```
{
    "job": "<job_id>"
}
```

To query job status:

```
http :5000/reports/status/<job_id>
```

To download PDF from a successful job:

```
http :5000/reports/results/<job_id>
```

This sets the `Content-Type` header to attachment and uses the passed-in name
for the filename.
