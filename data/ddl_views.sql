--ATTACH DATABASE 'data/sample_data.db' AS destinationDB;

-- Create views for all the above tables
CREATE VIEW vw_providers_t AS 
SELECT 
    provider_id, 
    provider_name COLLATE NOCASE AS provider_name, 
    provider_location_city COLLATE NOCASE AS provider_location_city, 
    provider_Location_state COLLATE NOCASE AS provider_Location_state,
    is_pharmacy_or_clinic,
    created_dt,
    updated_dt
FROM providers_t;

CREATE VIEW vw_claim_t AS 
SELECT 
    claim_id,
    claim_nbr COLLATE NOCASE AS claim_nbr,
    member_id COLLATE NOCASE AS member_id,
    fill_dt COLLATE NOCASE AS fill_dt,
    claim_type_cd COLLATE NOCASE AS claim_type_cd,
    channel_id,
    specialty_indicator_flag COLLATE NOCASE AS specialty_indicator_flag,
    brand_generic_cd COLLATE NOCASE AS brand_generic_cd,
    NDC COLLATE NOCASE AS NDC,
    drug_name_id,
    drug_category_id,
    net_money,
    copay_money,
    admin_money,
    third_party_money,
    provider_id COLLATE NOCASE AS provider_id,
    place_of_svc_id,
    quantity,
    days_supply,
    asp,
    awp,
    dispense_fee,
    ingredient_cost,
    days_supply_claim_count
FROM claim_t;

CREATE VIEW vw_drug_name_t AS 
SELECT 
    drug_name_id,
    drug_name COLLATE NOCASE AS drug_name,
    specialty_indicator_flag COLLATE NOCASE AS specialty_indicator_flag,
    drug_source_cd COLLATE NOCASE AS drug_source_cd
FROM drug_name_t;

CREATE VIEW vw_drug_category_t AS
SELECT 
    drug_category_id,
    drug_category_description COLLATE NOCASE AS drug_category_description
FROM drug_category_t;

CREATE VIEW vw_drug_t AS 
SELECT 
    drug_id,
    NDC COLLATE NOCASE AS NDC,
    drug_name_id,
    drug_category_id,
    brand_generic_cd COLLATE NOCASE AS brand_generic_cd,
    mfg_name COLLATE NOCASE AS mfg_name,
    strength COLLATE NOCASE AS strength,
    dosage_form_description COLLATE NOCASE AS dosage_form_description
FROM drug_t;

CREATE VIEW vw_channel_t AS 
SELECT 
    channel_id,
    channel_name COLLATE NOCASE AS channel_name
FROM channel_t;

CREATE VIEW vw_claim_type_t AS
SELECT 
    claim_type_id COLLATE NOCASE AS claim_type_id,
    claim_type_description COLLATE NOCASE AS claim_type_description
FROM claim_type_t;

CREATE VIEW vw_brand_generic_t AS 
SELECT 
    brand_generic_cd COLLATE NOCASE AS brand_generic_cd,
    brand_generic_description COLLATE NOCASE AS brand_generic_description
FROM brand_generic_t;

CREATE VIEW vw_drug_source_type_t AS
SELECT 
    drug_source_type_cd COLLATE NOCASE AS drug_source_type_cd,
    drug_source_description COLLATE NOCASE AS drug_source_description
FROM drug_source_type_t;

CREATE VIEW vw_place_of_service_t AS 
SELECT 
    place_of_service_id,
    place_of_service_description COLLATE NOCASE AS place_of_service_description
FROM place_of_service_t;
