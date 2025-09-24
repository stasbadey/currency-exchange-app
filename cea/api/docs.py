"""Reusable Swagger/OpenAPI documentation bits for the API (English).

This module defines common error responses and route-specific descriptions
and examples to keep route files clean and consistent.
"""

from typing import Dict, Any


# Generic error response payload produced by cea.main.handle_service_error
_DETAIL_EXAMPLE = {'detail': 'Error message'}


common_error_responses: Dict[int, Dict[str, Any]] = {
    400: {
        'description': 'Validation error',
        'content': {'application/json': {'example': _DETAIL_EXAMPLE}},
    },
    404: {
        'description': 'Not found',
        'content': {'application/json': {'example': _DETAIL_EXAMPLE}},
    },
    409: {
        'description': 'Conflict',
        'content': {"application/json": {'example': _DETAIL_EXAMPLE}},
    },
    502: {
        'description': 'Upstream dependency error',
        'content': {'application/json': {'example': _DETAIL_EXAMPLE}},
    },
    503: {
        'description': "Internal dependency error",
        "content": {"application/json": {"example": _DETAIL_EXAMPLE}},
    },
}


# Currency rates docs

currencies_description = (
    'Returns a list of currency rates for the selected date. '
    'If the date is not provided, the current date is used.'
)

currencies_responses: Dict[int, Dict[str, Any]] = {
    200: {
        'description': 'Successful response',
        'content': {
            'application/json': {
                'examples': {
                    'sample': {
                        'summary': 'Sample rates list',
                        'value': [
                            {
                                'id': 1,
                                'abbreviation': 'USD',
                                'scale': 1,
                                'rate': 3.2571,
                                'rate_date': '2024-09-24',
                            },
                            {
                                'id': 2,
                                'abbreviation': 'EUR',
                                'scale': 1,
                                'rate': 3.4552,
                                'rate_date': '2024-09-24',
                            },
                        ],
                    }
                }
            }
        },
    },
} | common_error_responses


# Deals docs

preview_description = (
    'Exchange preview: creates a draft deal in PENDING status and '
    'calculates the amount to receive based on current rates.'
)

preview_request_example = {
    'amount_from': 100.0,
    'currency_from': 'USD',
    'currency_to': 'EUR',
}

preview_responses: Dict[int, Dict[str, Any]] = {
    200: {
        'description': 'Successful calculation and draft creation',
        'content': {
            'application/json': {
                'examples': {
                    'sample': {
                        'summary': 'Sample response',
                        'value': {
                            'deal_id': '9eac6a0d-9a7e-4a3e-9f3a-210b5f5b1c40',
                            'amount_to': 92.5311,
                            'rate_from': 3.2571,
                            'scale_from': 1,
                            'rate_to': 3.5234,
                            'scale_to': 1,
                            'status': 'pending',
                        },
                    }
                }
            }
        },
    },
} | common_error_responses


confirm_description = (
    'Confirms or rejects a previously created draft deal. '
    'Possible errors: not found (404), already finalized (409).'
)

confirm_request_example = {
    'deal_id': '9eac6a0d-9a7e-4a3e-9f3a-210b5f5b1c40',
    'result': 'confirm',
}

confirm_responses: Dict[int, Dict[str, Any]] = {
    200: {
        'description': 'Deal status after confirmation/rejection',
        'content': {
            'application/json': {
                'examples': {
                    'confirmed': {
                        'summary': 'Confirmed',
                        'value': {
                            'id': '9eac6a0d-9a7e-4a3e-9f3a-210b5f5b1c40',
                            'status': 'confirmed',
                        },
                    },
                    'rejected': {
                        'summary': 'Rejected',
                        'value': {
                            'id': '9eac6a0d-9a7e-4a3e-9f3a-210b5f5b1c40',
                            'status': 'rejected',
                        },
                    },
                }
            }
        },
    },
} | common_error_responses


pending_description = 'List of pending (PENDING) deals awaiting confirmation.'

pending_responses: Dict[int, Dict[str, Any]] = {
    200: {
        'description': 'Successful response',
        'content': {
            'application/json': {
                'example': [
                    {
                        'id': '8e1c0cfe-bb3d-4b6a-bb3d-8f4b9e5a4a00',
                        'created_at': '2024-09-24T12:00:00Z',
                        'amount_from': 100.0,
                        'amount_to': 92.5311,
                        'currency_from': 'USD',
                        'currency_to': 'EUR',
                        'rate_from': 3.2571,
                        'scale_from': 1,
                        'rate_to': 3.5234,
                        'scale_to': 1,
                    }
                ]
            }
        },
    },
} | common_error_responses


report_description = (
    'Aggregated report for deals over a period. Returns incoming/outgoing '
    'amounts and count per currency.'
)

report_responses: Dict[int, Dict[str, Any]] = {
    200: {
        'description': 'Successful response',
        'content': {
            'application/json': {
                'example': [
                    {
                        'currency': 'USD', 
                        'in_amount': 500.0, 
                        'out_amount': 0.0, 
                        'count': 2,
                    },
                    {
                        'currency': 'EUR', 
                        'in_amount': 0.0, 
                        'out_amount': 750.0, 
                        'count': 1,
                    },
                ]
            }
        },
    },
} | common_error_responses


# OpenAPI tags metadata

openapi_tags = [
    {
        'name': 'Currency Rates',
        'description': 'Operations for retrieving currency rates by date.',
    },
    {
        'name': 'Deal',
        'description': 'Preview, confirm, and report on exchange deals.',
    },
]
