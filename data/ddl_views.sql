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
    fill_date COLLATE NOCASE AS fill_date,
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


DROP VIEW IF EXISTS vw_all_drug_claims_data;

CREATE VIEW vw_all_drug_claims_data AS
--CREATE TABLE all_drug_claims_data_t AS
SELECT
    c.claim_id,
    c.claim_nbr,
    c.member_id,
    c.fill_date,
    --c.claim_type_cd,
    ct.claim_type_description,
    --c.channel_id,
    ch.channel_name,
    c.specialty_indicator_flag AS claim_specialty_indicator_flag,
    --c.brand_generic_cd AS claim_brand_generic_cd,
    bg.brand_generic_description,
    c.NDC,
    --d.drug_id,
    --d.drug_name_id,
    dn.drug_name,
    --dn.specialty_indicator_flag AS drug_specialty_indicator_flag,
    --dn.drug_source_cd,
    dst.drug_source_description,
    --d.drug_category_id,
    dc.drug_category_description,
    d.brand_generic_cd AS drug_brand_generic_cd,
    d.mfg_name,
    d.strength,
    d.dosage_form_description,
    c.net_money,
    c.copay_money,
    c.admin_money,
    c.third_party_money,
    --c.provider_id,
    p.provider_name,
    p.provider_location_city,
    p.provider_Location_state,
    p.is_pharmacy_or_clinic,
    --p.created_dt AS provider_created_dt,
    --p.updated_dt AS provider_updated_dt,
    --c.place_of_svc_id,
    pos.place_of_service_description,
    c.quantity,
    c.days_supply,
    c.asp AS average_sales_price,
    c.awp as average_wholesale_price,
    c.dispense_fee,
    c.ingredient_cost,
    c.days_supply_claim_count
FROM vw_claim_t c
LEFT JOIN vw_providers_t p ON c.provider_id = p.provider_id
LEFT JOIN vw_drug_t d ON c.NDC = d.NDC and length(c.NDC) = 11
LEFT JOIN vw_drug_name_t dn ON c.drug_name_id = dn.drug_name_id
LEFT JOIN vw_drug_category_t dc ON c.drug_category_id = dc.drug_category_id
INNER JOIN vw_channel_t ch ON c.channel_id = ch.channel_id
LEFT JOIN vw_claim_type_t ct ON c.claim_type_cd = ct.claim_type_id
INNER JOIN vw_brand_generic_t bg ON c.brand_generic_cd = bg.brand_generic_cd
LEFT JOIN vw_drug_source_type_t dst ON dn.drug_source_cd = dst.drug_source_type_cd
INNER JOIN vw_place_of_service_t pos ON c.place_of_svc_id = pos.place_of_service_id;


--------------



DROP VIEW IF EXISTS vw_all_drug_claims_data;
CREATE VIEW vw_all_drug_claims_data AS
SELECT
    c.claim_id,
    c.claim_nbr,
    c.member_id,
    c.fill_date,
    c.specialty_indicator_flag AS claim_specialty_indicator_flag,
    c.NDC,
    (SELECT claim_type_description from claim_type_t where claim_type_id = c.claim_type_cd) as claim_type_description,
    (SELECT channel_name FROM channel_t WHERE channel_id = c.channel_id) AS channel_name,    
    (SELECT brand_generic_description from brand_generic_t where brand_generic_cd = d.brand_generic_cd) as brand_generic_description,
    dn.drug_name,
    (SELECT drug_category_description FROM drug_category_t WHERE drug_category_id = c.drug_category_id) AS drug_category_description,
    (SELECT place_of_service_description FROM vw_place_of_service_t WHERE place_of_service_id = c.place_of_svc_id) AS place_of_service_description,
    d.brand_generic_cd AS drug_brand_generic_cd,
    d.mfg_name,
    d.strength,
    d.dosage_form_description,
    c.net_money,
    c.copay_money,
    c.admin_money,
    c.third_party_money,
    p.provider_name,
    p.provider_location_city,
    p.provider_Location_state,
    p.is_pharmacy_or_clinic,
    c.quantity,
    c.days_supply,
    c.asp AS average_sales_price,
    c.awp as average_wholesale_price,
    c.dispense_fee,
    c.ingredient_cost,
    c.days_supply_claim_count
FROM claim_t c
LEFT JOIN providers_t p ON c.provider_id = p.provider_id
LEFT JOIN drug_t d ON c.NDC = d.NDC and length(c.NDC) = 11
LEFT JOIN drug_name_t dn ON c.drug_name_id = dn.drug_name_id
LEFT JOIN drug_source_type_t dst ON dn.drug_source_cd = dst.drug_source_type_cd;
