CREATE OR REPLACE FUNCTION check_minor_safety()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT age FROM Characters WHERE id = NEW.person_id) < 18 THEN
        IF (SELECT safety FROM Location WHERE id = NEW.location_id) = FALSE THEN
            RAISE EXCEPTION 'Underage characters can not be in unsafe location';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER scene_safety_check
BEFORE INSERT OR UPDATE ON Scene
FOR EACH ROW
EXECUTE FUNCTION check_minor_safety();