-- Tabla 1: outages
-- Registros diarios de capacidad nuclear fuera de servicio.
-- PK: period (cada día es único en el dataset de EIA)
CREATE TABLE IF NOT EXISTS outages (
    period          DATE           NOT NULL COMMENT 'Fecha del registro (PK natural)',
    capacity        DECIMAL(10,2)  NOT NULL COMMENT 'Capacidad total instalada (MW)',
    outage          DECIMAL(10,2)  NOT NULL COMMENT 'Capacidad fuera de servicio (MW)',
    percent_outage  DECIMAL(6,4)   NOT NULL COMMENT '% de capacidad fuera de servicio',
    ingested_at     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (period),
    INDEX idx_percent (percent_outage)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Tabla 2: outage_stats
-- Estadísticas anuales precalculadas desde la tabla outages.
-- Responde: ¿cuánta capacidad estuvo fuera de servicio cada año?
CREATE TABLE IF NOT EXISTS outage_stats (
    year               SMALLINT      NOT NULL COMMENT 'Año (PK)',
    avg_outage_mw      DECIMAL(10,2) NOT NULL,
    avg_percent_outage DECIMAL(6,4)  NOT NULL,
    max_outage_mw      DECIMAL(10,2) NOT NULL,
    min_outage_mw      DECIMAL(10,2) NOT NULL,
    total_records      INT           NOT NULL,

    PRIMARY KEY (year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;