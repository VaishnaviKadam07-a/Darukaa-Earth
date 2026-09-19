-- ============================================================
-- DARUKAA.EARTH POSTGRESQL + POSTGIS DATABASE SCHEMA
-- ============================================================

CREATE EXTENSION IF NOT EXISTS postgis;


-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,

    name VARCHAR(120) NOT NULL,

    email VARCHAR(255) UNIQUE NOT NULL,

    password_hash TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- PROJECTS
-- ============================================================

CREATE TABLE projects (
    project_id BIGSERIAL PRIMARY KEY,

    name VARCHAR(200) NOT NULL,

    description TEXT,

    project_type VARCHAR(80),

    status VARCHAR(40)
        DEFAULT 'Active',

    created_by BIGINT
        REFERENCES users(user_id),

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- SITES
-- ============================================================

CREATE TABLE sites (
    site_id BIGSERIAL PRIMARY KEY,

    project_id BIGINT NOT NULL
        REFERENCES projects(project_id)
        ON DELETE CASCADE,

    name VARCHAR(200) NOT NULL,

    state VARCHAR(100),

    district VARCHAR(100),

    area_hectares NUMERIC(12,2),

    latitude NUMERIC(10,7),

    longitude NUMERIC(10,7),

    geometry GEOMETRY(
        POLYGON,
        4326
    ) NOT NULL,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- BIODIVERSITY OCCURRENCES
-- ============================================================

CREATE TABLE biodiversity_occurrences (

    id BIGSERIAL PRIMARY KEY,

    gbif_id VARCHAR(100),

    site_id BIGINT
        REFERENCES sites(site_id)
        ON DELETE SET NULL,

    species VARCHAR(255),

    accepted_scientific_name VARCHAR(255),

    kingdom VARCHAR(100),

    phylum VARCHAR(100),

    class VARCHAR(100),

    order_name VARCHAR(100),

    family VARCHAR(100),

    genus VARCHAR(100),

    latitude NUMERIC(10,7),

    longitude NUMERIC(10,7),

    event_date DATE,

    year INTEGER,

    month INTEGER,

    basis_of_record VARCHAR(100),

    dataset_key VARCHAR(100),

    geometry GEOMETRY(
        POINT,
        4326
    ) NOT NULL
);


-- ============================================================
-- CARBON METRICS
-- ============================================================

CREATE TABLE carbon_metrics (

    id BIGSERIAL PRIMARY KEY,

    site_id BIGINT NOT NULL
        REFERENCES sites(site_id)
        ON DELETE CASCADE,

    year INTEGER NOT NULL,

    carbon_emissions_tco2e NUMERIC(14,2),

    above_ground_biomass_t NUMERIC(14,2),

    tree_cover_percent NUMERIC(6,2),

    forest_loss_hectares NUMERIC(12,2),

    estimated_net_carbon_tco2e NUMERIC(14,2),

    UNIQUE(site_id, year)
);


-- ============================================================
-- BIODIVERSITY METRICS
-- ============================================================

CREATE TABLE biodiversity_metrics (

    id BIGSERIAL PRIMARY KEY,

    site_id BIGINT NOT NULL
        REFERENCES sites(site_id)
        ON DELETE CASCADE,

    year INTEGER NOT NULL,

    species_count INTEGER,

    observation_count INTEGER,

    bird_species INTEGER,

    mammal_species INTEGER,

    amphibian_species INTEGER,

    reptile_species INTEGER,

    plant_species INTEGER,

    UNIQUE(site_id, year)
);


-- ============================================================
-- SPATIAL INDEXES
-- ============================================================

CREATE INDEX idx_sites_geometry
ON sites
USING GIST(geometry);


CREATE INDEX idx_occurrences_geometry
ON biodiversity_occurrences
USING GIST(geometry);


-- ============================================================
-- OTHER INDEXES
-- ============================================================

CREATE INDEX idx_occurrences_site
ON biodiversity_occurrences(site_id);


CREATE INDEX idx_carbon_site_year
ON carbon_metrics(site_id, year);


CREATE INDEX idx_biodiversity_site_year
ON biodiversity_metrics(site_id, year);


-- ============================================================
-- END OF SCHEMA
-- ============================================================