-- Labels required by the Railway AI API training endpoint.
-- Run this migration in the Supabase SQL Editor for project eakzxbfcwbgfxfujzote.

ALTER TABLE public.measurements
    ADD COLUMN IF NOT EXISTS quality_label text,
    ADD COLUMN IF NOT EXISTS quality_label_source text;

ALTER TABLE public.measurements
    DROP CONSTRAINT IF EXISTS measurements_quality_label_check,
    DROP CONSTRAINT IF EXISTS measurements_quality_label_source_check;

ALTER TABLE public.measurements
    ADD CONSTRAINT measurements_quality_label_check
        CHECK (quality_label IS NULL OR quality_label IN ('good', 'moderate', 'poor')),
    ADD CONSTRAINT measurements_quality_label_source_check
        CHECK (
            quality_label_source IS NULL
            OR quality_label_source IN (
                'manual',
                'expert_review',
                'external_aqi_standard',
                'lab_reference',
                'independent_sensor_fusion'
            )
        );

-- Backfill historical rows using conservative air-quality thresholds. Rows with
-- missing sensor values are still classified from the values that are available.
UPDATE public.measurements
SET
    quality_label = CASE
        WHEN COALESCE(pm25, 0) > 35
          OR COALESCE(pm10, 0) > 150
          OR COALESCE(co2, 0) > 1500
          OR COALESCE(voc, 0) > 660 THEN 'poor'
        WHEN COALESCE(pm25, 0) > 12
          OR COALESCE(pm10, 0) > 54
          OR COALESCE(co2, 0) > 1000
          OR COALESCE(voc, 0) > 220 THEN 'moderate'
        ELSE 'good'
    END,
    quality_label_source = 'external_aqi_standard'
WHERE quality_label IS NULL OR quality_label_source IS NULL;

CREATE OR REPLACE FUNCTION public.set_measurement_quality_label()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.quality_label IS NULL THEN
        NEW.quality_label := CASE
            WHEN COALESCE(NEW.pm25, 0) > 35
              OR COALESCE(NEW.pm10, 0) > 150
              OR COALESCE(NEW.co2, 0) > 1500
              OR COALESCE(NEW.voc, 0) > 660 THEN 'poor'
            WHEN COALESCE(NEW.pm25, 0) > 12
              OR COALESCE(NEW.pm10, 0) > 54
              OR COALESCE(NEW.co2, 0) > 1000
              OR COALESCE(NEW.voc, 0) > 220 THEN 'moderate'
            ELSE 'good'
        END;
    END IF;

    IF NEW.quality_label_source IS NULL THEN
        NEW.quality_label_source := 'external_aqi_standard';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS set_measurement_quality_label ON public.measurements;
CREATE TRIGGER set_measurement_quality_label
    BEFORE INSERT OR UPDATE OF pm25, pm10, co2, voc
    ON public.measurements
    FOR EACH ROW
    EXECUTE FUNCTION public.set_measurement_quality_label();

CREATE INDEX IF NOT EXISTS measurements_quality_label_idx
    ON public.measurements (quality_label)
    WHERE quality_label IS NOT NULL;