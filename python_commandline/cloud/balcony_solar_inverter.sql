-- Create telemetry table
CREATE TABLE IF NOT EXISTS inverter_telemetry (
    id                   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recorded_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    device_id            VARCHAR(64) NOT NULL,
    
    -- Inverter state & health
    is_active            BOOLEAN NOT NULL,
    fault_code           INTEGER NOT NULL DEFAULT 0,
    
    -- AC Grid side (Scaled)
    ac_voltage_v         NUMERIC(5, 1) NOT NULL,   -- DPS 20 / 10.0
    ac_current_a         NUMERIC(6, 3) NOT NULL,   -- DPS 22 / 1000.0
    power_reported_w     NUMERIC(6, 1) NOT NULL,   -- DPS 25 / 100.0
    apparent_power_va    NUMERIC(7, 1) NOT NULL,
    power_factor         NUMERIC(4, 2) NOT NULL,
    power_calculated_w   NUMERIC(6, 1) GENERATED ALWAYS AS (ROUND(ac_voltage_v * ac_current_a, 1)) STORED,
       
    -- Accumulation & Cumulative Energy
    raw_cumulative_wh    BIGINT NOT NULL,          -- Energy generated since the prior reading
    net_produced_wh      BIGINT NOT NULL,          -- Cumulative energy generated
    
    -- Raw payload backup for debugging/unmapped attributes
    raw_dps              JSONB
);

ALTER TABLE inverter_telemetry
    ADD COLUMN IF NOT EXISTS apparent_power_va NUMERIC(7, 1),
    ADD COLUMN IF NOT EXISTS power_factor NUMERIC(4, 2),
    DROP COLUMN IF EXISTS net_produced_kwh,
    DROP COLUMN IF EXISTS heatsink_temp_c,
    DROP COLUMN IF EXISTS grid_freq_hz,
    DROP COLUMN IF EXISTS dc_bus_voltage_v;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_attribute
        WHERE attrelid = 'inverter_telemetry'::regclass
          AND attname = 'net_produced_wh'
          AND attgenerated <> ''
    ) THEN
        ALTER TABLE inverter_telemetry
            ALTER COLUMN net_produced_wh DROP EXPRESSION;
    END IF;
END $$;

WITH readings AS (
    SELECT
        id,
        device_id,
        recorded_at,
        power_reported_w,
        LAG(recorded_at) OVER (
            PARTITION BY device_id, recorded_at::date ORDER BY recorded_at, id
        ) AS previous_at,
        LAG(power_reported_w) OVER (
            PARTITION BY device_id, recorded_at::date ORDER BY recorded_at, id
        ) AS previous_power_w
    FROM inverter_telemetry
), intervals AS (
    SELECT
        id,
        device_id,
        recorded_at,
        GREATEST(
            0,
            ROUND(
                ((power_reported_w + COALESCE(previous_power_w, 0)) / 2.0)
                * COALESCE(EXTRACT(EPOCH FROM recorded_at - previous_at) / 3600.0, 1.0)
            )
        )::BIGINT AS interval_wh
    FROM readings
), cumulative AS (
    SELECT
        id,
        interval_wh,
        SUM(interval_wh) OVER (
            PARTITION BY device_id ORDER BY recorded_at, id
        ) AS total_wh
    FROM intervals
)
UPDATE inverter_telemetry AS telemetry
SET raw_cumulative_wh = cumulative.interval_wh,
    net_produced_wh = cumulative.total_wh
FROM cumulative
WHERE telemetry.id = cumulative.id;

-- Index for time-series range queries and dashboard charting
CREATE INDEX IF NOT EXISTS idx_inverter_telemetry_time 
    ON inverter_telemetry (recorded_at DESC);

-- Optional: TimescaleDB hypertables may reject the id-only primary key because
-- unique indexes must include the partitioning time column.
-- SELECT create_hypertable('inverter_telemetry', 'recorded_at', if_not_exists => TRUE);