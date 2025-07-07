-- This file contains SQL queries to import data into the database.
-- It'll copy data from the source database to the destination database.
--ATTACH DATABASE 'data/sample_data.db' AS destinationDB;
ATTACH DATABASE 'data/example.db' AS sourceDB;

Insert INTO destinationDB.channel_t
(channel_id, channel_name)
Values (1, 'Retail'),
(2, 'Mail Order'),
(3, 'Specialty'),
(4, 'Institutional'),
(5, 'Long Term Care'),
(6, 'Home Infusion'),
(7, 'Other');

INSERT INTO destinationDB.claim_type_t
(claim_type_id, claim_type_description)
Values ('M', 'Medical'),
('P', 'Pharmacy');

INSERT INTO destinationDB.brand_generic_t
(brand_generic_cd, brand_generic_description)
Values ('B', 'Brand'),
('G', 'Generic'),
('U', 'Unknown');

INSERT INTO destinationDB.place_of_service_t
(place_of_service_id, place_of_service_description)
Values (11, 'Office'),
(22, 'Home'),
(12, 'Hospital'),
(1, 'Pharmacy'),
(21, 'Clinic'),
(99, 'Other');

Insert into destinationDB.drug_source_type_t
(drug_source_type_cd, drug_source_description)
Values ('UNK', 'Unknown'),
('SSB','Single Source Brand'),
('GNC','Generic'),
('MSB','Multi Source Brand');


-- Copy data for Providers_T from Source to Destination DB
INSERT INTO destinationDB.providers_t
(provider_id, provider_name, provider_location_city, provider_Location_state, is_pharmacy_or_clinic, created_dt, updated_dt)
SELECT provider_id, provider_name, city, state, is_pharmacy, date(), date()
FROM sourceDB.providers;

-- Copy data for drug_name_T from Source to Destination DB
INSERT INTO destinationDB.drug_name_t
(drug_name_id, drug_name, specialty_indicator_flag, drug_source_cd)
SELECT drug_name_id, drug_name, specialty_ind, drug_status
FROM sourceDB.drug_name;

INSERT INTO destinationDB.drug_category_t
(drug_category_id, drug_category_description)
SELECT drug_cat_id, drug_cat_name
FROM sourceDB.drug_category;

INSERT INTO destinationDB.drug_t
(NDC, drug_name_id, drug_category_id, brand_generic_cd,mfg_name, strength, dosage_form_description)
SELECT cd, drug_name_id, drug_cat_id,brand_generic,mfg, strength, dsg_frm_desc
FROM sourceDB.drug;

INSERT INTO destinationDB.claim_t
(claim_id, claim_nbr, member_id, fill_dt, claim_type_cd, channel_id, specialty_indicator_flag, brand_generic_cd, NDC, drug_name_id, drug_category_id, net_money, copay_money, admin_money, third_party_money, provider_id, place_of_svc_id, quantity, days_supply, asp, awp, dispense_fee, ingredient_cost, days_supply_claim_count)
SELECT claim_id, claim_nbr, member_id, prim_dt, benefit_type, channel_id, specialty_ind, brand_generic, cd, drug_name_id, drug_cat_id, net_mony, copay_mony, admin_mony, third_party_mony, provider_id, place_of_svc, quantity, days_supply, asp, awp, disp_fee, ingred_cost, days_supply_claim_count
FROM sourceDB.claim;



select * from vw_all_drug_claims_data limit 10000;