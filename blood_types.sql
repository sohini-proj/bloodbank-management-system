-- Update A Positive to A+
UPDATE Blood_Type SET blood_type = 'A+' WHERE blood_type = 'A Positive';

-- First, update all references to use the first occurrence of each blood type
UPDATE Donors SET blood_type_id = 1 WHERE blood_type_id IN (9, 17);  -- A+
UPDATE Recipients SET blood_type_id = 1 WHERE blood_type_id IN (9, 17);
UPDATE Blood_Inventory SET blood_type_id = 1 WHERE blood_type_id IN (9, 17);
UPDATE Donations SET blood_type_id = 1 WHERE blood_type_id IN (9, 17);

UPDATE Donors SET blood_type_id = 2 WHERE blood_type_id IN (10, 18);  -- A-
UPDATE Recipients SET blood_type_id = 2 WHERE blood_type_id IN (10, 18);
UPDATE Blood_Inventory SET blood_type_id = 2 WHERE blood_type_id IN (10, 18);
UPDATE Donations SET blood_type_id = 2 WHERE blood_type_id IN (10, 18);

UPDATE Donors SET blood_type_id = 3 WHERE blood_type_id IN (11, 19);  -- B+
UPDATE Recipients SET blood_type_id = 3 WHERE blood_type_id IN (11, 19);
UPDATE Blood_Inventory SET blood_type_id = 3 WHERE blood_type_id IN (11, 19);
UPDATE Donations SET blood_type_id = 3 WHERE blood_type_id IN (11, 19);

UPDATE Donors SET blood_type_id = 4 WHERE blood_type_id IN (12, 20);  -- B-
UPDATE Recipients SET blood_type_id = 4 WHERE blood_type_id IN (12, 20);
UPDATE Blood_Inventory SET blood_type_id = 4 WHERE blood_type_id IN (12, 20);
UPDATE Donations SET blood_type_id = 4 WHERE blood_type_id IN (12, 20);

UPDATE Donors SET blood_type_id = 5 WHERE blood_type_id IN (13, 21);  -- AB+
UPDATE Recipients SET blood_type_id = 5 WHERE blood_type_id IN (13, 21);
UPDATE Blood_Inventory SET blood_type_id = 5 WHERE blood_type_id IN (13, 21);
UPDATE Donations SET blood_type_id = 5 WHERE blood_type_id IN (13, 21);

UPDATE Donors SET blood_type_id = 6 WHERE blood_type_id IN (14, 22);  -- AB-
UPDATE Recipients SET blood_type_id = 6 WHERE blood_type_id IN (14, 22);
UPDATE Blood_Inventory SET blood_type_id = 6 WHERE blood_type_id IN (14, 22);
UPDATE Donations SET blood_type_id = 6 WHERE blood_type_id IN (14, 22);

UPDATE Donors SET blood_type_id = 7 WHERE blood_type_id IN (15, 23);  -- O+
UPDATE Recipients SET blood_type_id = 7 WHERE blood_type_id IN (15, 23);
UPDATE Blood_Inventory SET blood_type_id = 7 WHERE blood_type_id IN (15, 23);
UPDATE Donations SET blood_type_id = 7 WHERE blood_type_id IN (15, 23);

UPDATE Donors SET blood_type_id = 8 WHERE blood_type_id = 16;  -- O-
UPDATE Recipients SET blood_type_id = 8 WHERE blood_type_id = 16;
UPDATE Blood_Inventory SET blood_type_id = 8 WHERE blood_type_id = 16;
UPDATE Donations SET blood_type_id = 8 WHERE blood_type_id = 16;

-- Deduplicate Blood_Inventory: keep one row per blood_type_id with the total quantity
CREATE TEMPORARY TABLE temp_inventory AS
SELECT blood_type_id, SUM(quantity) AS quantity
FROM Blood_Inventory
GROUP BY blood_type_id;

DELETE FROM Blood_Inventory;

INSERT INTO Blood_Inventory (blood_type_id, quantity)
SELECT blood_type_id, quantity FROM temp_inventory;

DROP TABLE temp_inventory;

-- Delete all duplicate blood types
DELETE FROM Blood_Type WHERE blood_type_id > 8;

-- Ensure all blood types have inventory entries
INSERT IGNORE INTO Blood_Inventory (blood_type_id, quantity)
SELECT blood_type_id, 0 FROM Blood_Type; 