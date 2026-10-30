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
    raw_cumulative_wh    BIGINT NOT NULL,          -- DPS 23 raw integer
    net_produced_wh      BIGINT GENERATED ALWAYS AS (GREATEST(0, raw_cumulative_wh - 28083)) STORED,
    net_produced_kwh     NUMERIC(10, 3) GENERATED ALWAYS AS (ROUND(GREATEST(0, raw_cumulative_wh - 28083) / 1000.0, 3)) STORED,
    
    -- Raw payload backup for debugging/unmapped attributes
    raw_dps              JSONB
);

ALTER TABLE inverter_telemetry
    ADD COLUMN IF NOT EXISTS apparent_power_va NUMERIC(7, 1),
    ADD COLUMN IF NOT EXISTS power_factor NUMERIC(4, 2),
    DROP COLUMN IF EXISTS heatsink_temp_c,
    DROP COLUMN IF EXISTS grid_freq_hz,
    DROP COLUMN IF EXISTS dc_bus_voltage_v;

-- Index for time-series range queries and dashboard charting
CREATE INDEX IF NOT EXISTS idx_inverter_telemetry_time 
    ON inverter_telemetry (recorded_at DESC);

-- Optional: TimescaleDB hypertables may reject the id-only primary key because
-- unique indexes must include the partitioning time column.
-- SELECT create_hypertable('inverter_telemetry', 'recorded_at', if_not_exists => TRUE);