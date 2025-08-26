# Domain Ontologies

This directory contains domain-specific ontologies that represent core business entities and concepts in the tourism and event impact analysis domain.

## Overview

Domain ontologies define the fundamental entities and relationships that are specific to the business domain. These ontologies represent confirmed facts and core business concepts that are essential for understanding the domain.

## Ontologies

### **POI (Points of Interest)**
- **File**: `poi/poi_ontology.yaml`
- **Description**: Tourism attractions, venues, and locations with geospatial metadata
- **Entities**: POI, POI_TYPE
- **Relationships**: IS_OF_TYPE
- **Purpose**: Represents physical locations and venues in the tourism domain
- **Key Features**:
  - Geospatial location as WKT POINT geometry
  - Categorical classification with confidence scoring
  - Venue capacity and operational data (opening hours)
  - Rating and descriptive information
  - Address and location details
- **Relationship Semantics**: `IS_OF_TYPE` - POI is of a specific type with confidence scoring

### **People**
- **File**: `people/people_ontology.yaml`
- **Description**: Individual persons with demographic information and role classifications
- **Entities**: PERSON, PERSON_ROLE
- **Relationships**: HAS_ROLE
- **Purpose**: Represents people and their roles in the tourism and event context
- **Key Features**:
  - Demographic information (age, sex, wealth categories)
  - Role-based classification (tourist, local, staff, police)
  - Multi-role support with primary role designation
  - Context-aware role assignments with timestamps
  - Sociographic data for analysis
- **Relationship Semantics**: `HAS_ROLE` - Person has a specific role with assignment context

### **Location (Confirmed Facts)**
- **File**: `location/location_ontology.yaml` (planned)
- **Description**: Confirmed location facts and spatial relationships
- **Entities**: LOCATION, LOCATION_TYPE, LOCATION_FACT
- **Relationships**: LOCATED_IN, CONFIRMED_AT, VERIFIED_BY
- **Purpose**: Represents confirmed spatial facts and location hierarchies

## Characteristics

### **Domain-Specific**
- Focused on tourism and event impact analysis
- Represents real-world entities and relationships
- Based on confirmed facts and business requirements

### **Stable**
- These ontologies represent relatively stable domain concepts
- Changes should be infrequent and well-justified
- Backward compatibility should be maintained

### **Business-Critical**
- Essential for understanding the domain
- Used across multiple applications and use cases
- Core to the knowledge graph system

## Usage

Domain ontologies are used by:
- **Schema Generators**: To create database schemas
- **Data Ingestion**: To validate and structure incoming data
- **Query Interfaces**: To provide consistent data models
- **Analytics**: To understand domain relationships and patterns

## Adding New Domain Ontologies

When adding new domain ontologies:

1. **Validate Domain Relevance**: Ensure the ontology represents core domain concepts
2. **Confirm Facts**: Base the ontology on confirmed facts, not assumptions
3. **Maintain Consistency**: Follow the established ontology structure and naming conventions
4. **Document**: Provide clear descriptions and examples
5. **Test**: Validate with domain experts and stakeholders

## Relationships with Other Ontologies

Domain ontologies are referenced by:
- **System Ontologies**: For operational data and events
- **App Ontologies**: For application-specific features and analytics
- **Cross-Domain**: For integration with other business domains
