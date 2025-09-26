# Industry API Documentation

## Overview

The Industry API provides comprehensive data collection and analysis for EVE Online industrial jobs. It offers detailed insights into character industrial activities, job prioritization, location security analysis, and performance metrics.

## Base URL

```
/api/industry
```

## Authentication

All endpoints require EVE SSO authentication. The character must have the `esi-industry.read_character_jobs.v1` scope.

## Endpoints

### 1. Character Industry Summary

**GET** `/api/industry/characters/{character_id}/summary`

Get comprehensive industry summary for a character.

**Response:**

```json
{
  "character_id": 123456789,
  "total_jobs": 25,
  "active_jobs": 15,
  "completed_jobs": 8,
  "paused_jobs": 2,
  "jobs_by_activity": {
    "Manufacturing": 12,
    "Researching Technology": 5,
    "Copying": 3,
    "Invention": 5
  },
  "jobs_by_location": {
    "Jita IV - Moon 4 - Caldari Navy Assembly Plant": 8,
    "Amarr VIII (Oris) - Emperor Family Academy": 5,
    "Dodixie IX - Moon 20 - Federation Navy Assembly Plant": 7,
    "Rens VI - Moon 8 - Brutor Tribe Treasury": 5
  },
  "jobs_by_priority": {
    "high": 3,
    "medium": 8,
    "low": 4
  },
  "total_cost": 15000000,
  "efficiency_rating": 87.5,
  "risk_distribution": {
    "high": 2,
    "medium": 8,
    "low": 5
  },
  "upcoming_completions": [
    {
      "job_id": 12345,
      "product_name": "Tritanium",
      "time_remaining_hours": 0.5,
      "location_name": "Jita IV - Moon 4 - Caldari Navy Assembly Plant"
    }
  ],
  "needs_attention": [
    {
      "job_id": 12346,
      "product_name": "Plex",
      "time_remaining_hours": 0.2,
      "priority": "high",
      "attention_reasons": [
        "Завершается менее чем через час",
        "Высокий приоритет"
      ]
    }
  ]
}
```

### 2. Jobs by Activity

**GET** `/api/industry/characters/{character_id}/jobs/by-activity?activity_id={activity_id}`

Get jobs filtered by activity type.

**Parameters:**

- `activity_id` (optional): Filter by specific activity ID

**Activity IDs:**

- 1: Manufacturing
- 3: Researching Technology
- 4: Researching Time Efficiency
- 5: Researching Material Efficiency
- 6: Copying
- 7: Duplicating
- 8: Reverse Engineering
- 9: Invention
- 11: Reaction

**Response:**

```json
{
  "character_id": 123456789,
  "activity_id": 1,
  "jobs_by_activity": {
    "Manufacturing": [
      {
        "job_id": 12345,
        "product_name": "Tritanium",
        "activity_name": "Manufacturing",
        "start_date": "2024-01-01T10:00:00Z",
        "end_date": "2024-01-01T12:00:00Z",
        "status": "active",
        "progress_percentage": 75.0,
        "time_remaining_hours": 1.5,
        "location_name": "Jita IV - Moon 4 - Caldari Navy Assembly Plant",
        "system_security": 0.9,
        "priority": "medium",
        "risk_level": "low",
        "efficiency": 95.0,
        "cost": 1000000,
        "runs": 1
      }
    ]
  },
  "total_jobs": 12
}
```

### 3. Jobs by Location

**GET** `/api/industry/characters/{character_id}/jobs/by-location`

Get jobs grouped by location with security analysis.

**Response:**

```json
{
  "character_id": 123456789,
  "jobs_by_location": {
    "Jita IV - Moon 4 - Caldari Navy Assembly Plant": [
      {
        "job_id": 12345,
        "product_name": "Tritanium",
        "location_name": "Jita IV - Moon 4 - Caldari Navy Assembly Plant",
        "system_name": "Jita",
        "system_security": 0.9,
        "location_type": "station",
        "priority": "medium",
        "risk_level": "low"
      }
    ]
  },
  "location_security": {
    "Jita IV - Moon 4 - Caldari Navy Assembly Plant": 0.9
  },
  "security_analysis": {
    "high_sec_locations": 3,
    "low_sec_locations": 1,
    "null_sec_locations": 0,
    "total_jobs_in_high_sec": 15,
    "total_jobs_in_low_sec": 5,
    "total_jobs_in_null_sec": 0,
    "risky_locations": []
  },
  "total_locations": 4
}
```

### 4. Priority Jobs

**GET** `/api/industry/characters/{character_id}/jobs/priority?priority={priority}`

Get jobs by priority level.

**Parameters:**

- `priority`: "high", "medium", or "low" (default: "high")

**Response:**

```json
{
  "character_id": 123456789,
  "priority": "high",
  "jobs": [
    {
      "job_id": 12346,
      "product_name": "Plex",
      "time_remaining_hours": 0.2,
      "priority": "high",
      "attention_reasons": [
        "Завершается менее чем через час",
        "Высокий приоритет"
      ],
      "location_name": "Amarr VIII (Oris) - Emperor Family Academy",
      "system_security": 0.9,
      "risk_level": "low"
    }
  ],
  "count": 1
}
```

### 5. Jobs Needing Attention

**GET** `/api/industry/characters/{character_id}/jobs/attention`

Get jobs that need immediate attention.

**Response:**

```json
{
  "character_id": 123456789,
  "jobs_needing_attention": [
    {
      "job_id": 12346,
      "product_name": "Plex",
      "time_remaining_hours": 0.2,
      "priority": "high",
      "attention_reasons": [
        "Завершается менее чем через час",
        "Высокий приоритет"
      ],
      "location_name": "Amarr VIII (Oris) - Emperor Family Academy",
      "system_security": 0.9,
      "risk_level": "low",
      "progress_percentage": 95.0
    }
  ],
  "count": 1
}
```

### 6. Detailed Jobs Data

**GET** `/api/industry/characters/{character_id}/jobs/detailed`

Get detailed jobs data with all enriched information.

**Response:**

```json
{
  "character_id": 123456789,
  "jobs": [
    {
      "job_id": 12345,
      "character_id": 123456789,
      "product_type_id": 34,
      "product_name": "Tritanium",
      "product_volume": 0.01,
      "product_category": 4,
      "product_group": 18,
      "activity_id": 1,
      "activity_name": "Manufacturing",
      "start_date": "2024-01-01T10:00:00Z",
      "end_date": "2024-01-01T12:00:00Z",
      "location_id": 60003760,
      "location_name": "Jita IV - Moon 4 - Caldari Navy Assembly Plant",
      "location_type": "station",
      "location_security": 0.9,
      "station_id": 60003760,
      "station_name": "Caldari Navy Assembly Plant",
      "station_type": "station",
      "system_id": 30000142,
      "system_name": "Jita",
      "system_security": 0.9,
      "corporation_id": 1000001,
      "corporation_name": "Caldari Navy",
      "status": "active",
      "runs": 1,
      "cost": 1000000,
      "duration_hours": 2.0,
      "time_remaining_hours": 1.5,
      "is_completed": false,
      "is_paused": false,
      "progress_percentage": 75.0,
      "efficiency": 95.0,
      "priority": "medium",
      "risk_level": "low"
    }
  ],
  "total_jobs": 25,
  "active_jobs": 15,
  "completed_jobs": 8
}
```

## Data Enrichment

The API automatically enriches job data with:

### Product Information

- Product name, volume, category, and group
- Market data integration

### Location Information

- Station/structure names and types
- Solar system names and security status
- Corporation information

### Calculated Fields

- Job duration in hours
- Time remaining in hours
- Progress percentage
- Job efficiency rating
- Priority level (high/medium/low)
- Risk level (high/medium/low)

### Attention Detection

Jobs are flagged for attention if they:

- Complete within 1 hour
- Have high priority
- Are in high-risk (low/null sec) systems
- Are paused
- Have high cost (>1M ISK)

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (authentication failed)
- `404`: Character not found
- `500`: Internal server error

Error response format:

```json
{
  "error": "Error message description"
}
```

## Rate Limiting

The API respects EVE ESI rate limits and implements caching:

- Jobs data: 5 minutes cache
- Type/location data: 24 hours cache
- Station/corporation data: 24 hours cache

## Usage Examples

### Get all high-priority jobs for a character

```bash
curl -X GET "https://api.example.com/api/industry/characters/123456789/jobs/priority?priority=high" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get manufacturing jobs only

```bash
curl -X GET "https://api.example.com/api/industry/characters/123456789/jobs/by-activity?activity_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get jobs needing immediate attention

```bash
curl -X GET "https://api.example.com/api/industry/characters/123456789/jobs/attention" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
