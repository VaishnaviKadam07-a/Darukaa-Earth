# Darukaa.Earth Demo Dataset

## Overview

This package contains a ready-to-use demonstration dataset
for the Darukaa.Earth application.

The dataset is designed for:

- PostgreSQL
- PostGIS
- Mapbox
- React dashboards
- Environmental analytics
- Carbon monitoring
- Biodiversity monitoring
- Spatial queries
- Time-series visualization

------------------------------------------------------------

## IMPORTANT

The environmental metrics and biodiversity occurrence records
in this package are SYNTHETIC DEMO DATA.

They are created for application development, testing,
visualization and hackathon demonstration.

They are NOT direct measurements downloaded from:

- GBIF
- Global Forest Watch
- Hansen/UMD
- NASA
- ISRO
- Any government environmental database

The site locations are representative demonstration
locations.

The polygons are generated for PostGIS and Mapbox testing.

------------------------------------------------------------

## FILES

users.csv

Demo user account metadata.

------------------------------------------------------------

projects.csv

Contains environmental projects.

Columns:

project_id
name
description
project_type
status
created_by
created_at

------------------------------------------------------------

sites.csv

Contains monitoring sites.

Columns:

site_id
project_id
name
state
district
area_hectares
latitude
longitude
srid

------------------------------------------------------------

sites.geojson

GeoJSON polygons for displaying sites
on Mapbox or other GIS applications.

Coordinate system:

EPSG:4326

------------------------------------------------------------

carbon_metrics.csv

Contains yearly carbon metrics from 2021 to 2025.

Columns:

site_id
year
carbon_emissions_tco2e
above_ground_biomass_t
tree_cover_percent
forest_loss_hectares
estimated_net_carbon_tco2e

------------------------------------------------------------

biodiversity_metrics.csv

Contains yearly biodiversity metrics from 2021 to 2025.

Columns:

site_id
year
species_count
observation_count
bird_species
mammal_species
amphibian_species
reptile_species
plant_species

------------------------------------------------------------

biodiversity_occurrences.csv

Contains sample biodiversity observations.

Columns:

id
gbif_id
site_id
species
accepted_scientific_name
kingdom
phylum
class
order_name
family
genus
latitude
longitude
event_date
year
month
basis_of_record
dataset_key

------------------------------------------------------------

schema.sql

PostgreSQL + PostGIS database schema.

------------------------------------------------------------

## RECOMMENDED IMPORT ORDER

1. users.csv

2. projects.csv

3. sites.csv

4. biodiversity_occurrences.csv

5. carbon_metrics.csv

6. biodiversity_metrics.csv

------------------------------------------------------------

## POSTGIS GEOMETRY

Sites:

POLYGON
EPSG:4326

Biodiversity occurrences:

POINT
EPSG:4326

------------------------------------------------------------

## DASHBOARD USE

Use sites.geojson or sites.geometry
for Mapbox site boundaries.

Use biodiversity_occurrences.geometry
for spatial biodiversity queries.

Use carbon_metrics for:

- Carbon trend charts
- Tree cover charts
- Biomass charts
- Forest loss charts
- Net carbon charts

Use biodiversity_metrics for:

- Species trend charts
- Bird species charts
- Mammal species charts
- Amphibian charts
- Reptile charts
- Plant species charts

------------------------------------------------------------

## SAMPLE SPATIAL QUERY

Count biodiversity observations inside
each monitoring site:

SELECT
    s.site_id,
    s.name,
    COUNT(o.id) AS observation_count

FROM sites s

LEFT JOIN biodiversity_occurrences o

ON ST_Within(
    o.geometry,
    s.geometry
)

GROUP BY
    s.site_id,
    s.name;

------------------------------------------------------------

## SAMPLE CARBON QUERY

Latest carbon data:

SELECT *
FROM carbon_metrics
WHERE year = (
    SELECT MAX(year)
    FROM carbon_metrics
);

------------------------------------------------------------

## SAMPLE BIODIVERSITY QUERY

Latest biodiversity data:

SELECT *
FROM biodiversity_metrics
WHERE year = (
    SELECT MAX(year)
    FROM biodiversity_metrics
);

------------------------------------------------------------

## DATASET LOCATION

D:\JupyterNB\darukaa_dataset

ZIP:

D:\JupyterNB\Darukaa_Earth_Dataset.zip

------------------------------------------------------------