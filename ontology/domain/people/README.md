# Tourism & Event Impact People Ontology

This ontology defines the data structure for tourism and event impact analysis, focusing on raw observations of movement and event participation for tourists, locals, staff, and police.

## Overview

The Tourism & Event Impact People Ontology provides a focused framework for modeling:
- **Persons** with sociographic information
- **Roles** as separate entities (tourist, local, staff, police)
- **Role assignments** with context and metadata

## Domain Context

This ontology is specifically designed for:
- **Tourism & Event Impact Analysis**: Understanding movement patterns and event participation
- **Geospatial Anomaly Detection**: Foundation for detecting unusual patterns in tourist/local behavior
- **Raw Data Retention**: Preserving unprocessed observations for later analysis
- **Multi-role Analysis**: Supporting tourists, locals, staff, and police data

## Entity Types (Vertices)

### PERSON
Core entity representing individuals in tourism/event context:
- **Required fields**: `person_id`
- **Optional fields**: Sociographic info (sex, age, wealth)
- **Metadata**: Creation timestamp

### ROLE
Role classification for persons in tourism/event context:
- **Required fields**: `role_id`, `name` (tourist, local, staff, police)
- **Optional fields**: Description, category (visitor, resident, service, security)



## Relationship Types (Edges)

### Role Relationships
- **HAS_ROLE**: Person → Role (person has a specific role in tourism/event context)

### Role Relationships
- **HAS_ROLE**: Person → Role (person has a specific role in tourism/event context)

## Key Design Principles

### Role Management Focus
- **Flexible role assignment**: People can have multiple roles with context
- **Role categorization**: Roles are categorized (visitor, resident, service, security)
- **Assignment tracking**: Track when and why roles are assigned

### Multi-role Support
- **Tourist**: Visitors to the area
- **Local**: Residents of the area
- **Staff**: Event/venue staff members
- **Police**: Law enforcement personnel

## Usage Examples

### Person Creation
```yaml
person_id: "p001"
sex: "female"
age: 35
wealth: "high"
```

### Role Assignment
```yaml
source: "p001"  # person_id
target: "role001"  # role_id
relationship: "HAS_ROLE"
properties:
  assigned_date: "2024-08-26T00:00:00Z"
  is_primary: true
  context: "Event registration"
```



## Data Types

The ontology supports the following data types:
- **string**: Text data (IDs, roles, descriptions)
- **int**: Integer values (age)
- **bool**: Boolean values (is_primary flag)
- **timestamp**: Date and time values (assignment timestamps)

## Indexes

Performance indexes are defined for:
- Role names (for role-based queries)

## Query Patterns

This ontology supports the following query patterns:
- Retrieve all roles for a person
- Retrieve all persons with a specific role
- Analyze role distribution across the population
- Track role assignments over time

## Version History

- **v1.0**: Initial version focused on people and role management
- Separate role entities for flexible role management
- Role assignment tracking with context and metadata
- Note: Position and location information is handled by separate people_locations ontology

