# Technical POC Requirements — Tourism & Event Impact (Knowledge Graph + Geospatial Anomaly Detection)

## 1) Purpose & Scope

- **Goal:** Build a geospatial, geotemporal **POC** that models raw observations of movement and event participation for **tourists, locals, staff, and police**, linked to **POIs** (attractions, hotels, restaurants, venues).
- **Primary outcomes:**
  - (a) Ingest and store raw **lat/lon** observations with ticket-entry and auxiliary event data.
  - (b) Enable queries for raw co-occurrence and movement patterns.
  - (c) Prepare data foundation for later higher-level feature extraction and anomaly detection.
- **Out-of-scope:** Abstractions like derived groups, itineraries, or embeddings. The POC will **retain raw events and raw links only**.

---

## 2) Core Functional Requirements

1. **Entity & Event Modeling**

   - Represent only **Persons**, **POIs**, and **Events** (PositionPing, TicketEntry).
   - Store raw spatiotemporal attributes: `lat`, `lon`, `timestamp`, `accuracy?`.
   - Minimal sociographic attributes (sex, age, wealth) stored as optional properties.

2. **Data Ingestion**

   - Ingest raw events from multiple sources:
     - **Positions of individual objects** (GPS pings).
     - **Ticket Entry Information** (scans at venues).
   - Store as-is, without preprocessing beyond schema validation.

3. **Geospatial Handling**

   - Coordinate system: WGS84 (EPSG:4326).
   - Raw positions linked to POIs by optional nearest-neighbor association, but preserve raw lat/lon always.
   - No staypoint detection or trajectory segmentation at this stage.

---

## 3) Data Model (Knowledge Graph)

### 3.1 Node Types

- **Person**: {`person_id`, `role`: tourist|local|staff|police, optional sociographic info}.
- **POI**: {`poi_id`, `category`, `name`, `geom` (lat/lon or polygon)}.
- **Event**: minimal container for raw events with timestamps and source.
  - **PositionPing**: {`event_id`, `person_id`, `lat`, `lon`, `ts`, `accuracy?`}.
  - **TicketEntry**: {`event_id`, `person_id`, `poi_id`, `ts`, `ticket_class?`}.

### 3.2 Relationships

- `(Person)-[:EMITTED]->(PositionPing)`
- `(Person)-[:ENTERED]->(POI)` via TicketEntry

**Note:** Higher-level abstractions (Group, ItinerarySession, derived edges like FOLLOWED or MEMBER\_OF) are **excluded** in this POC.

---

## 4) Data Sources & Synthetic Data Generators

### 4.1 Real/Ingested Sources

- **Positions of individuals**: raw lat/lon/time logs.
- **Ticket Entry**: gate logs with timestamps and person references.
- **POI Catalog**: raw list of attractions, hotels, restaurants.

### 4.2 Synthetic Generators

- **Position Generator**: emits raw GPS tracks with noise/jitter.
- **Ticketing Generator**: emits entry events based on schedules.
- **Anomaly Injector**: introduces irregularities in raw data (e.g., sudden gaps, unusual surges) but leaves raw format unchanged.
- **POI Catalog**: ingestion of basic POI data/polygons for selected city/area

---

## 5) Processing & Storage

- **Landing Zone:** Object storage of JSON/CSV with raw event data.
- **Graph DB:** Load raw events as nodes and edges with minimal transformations.
- **Lakehouse/TS Store:** Store raw events in tabular form for direct query.

---

## 6) Interfaces & Queries

- Queries should expose raw relationships:
  - Retrieve all `PositionPings` for a person in a time window.
  - Retrieve all `TicketEntries` for a POI in a time window.
  - Retrieve raw co-occurrence of persons at the same POI within Δt.

---

