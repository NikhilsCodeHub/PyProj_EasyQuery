-- SQLite
SELECT strftime('%Y-%m', FILL_DT) AS month, 
SUM(CASE WHEN CATEGORY_NAME = 'MIGRAINE' THEN 1 ELSE 0 END) AS MIGRAINE, 
SUM(CASE WHEN CATEGORY_NAME = 'HYPERTENSION' THEN 1 ELSE 0 END) AS HYPERTENSION 
FROM RX_CLAIM 
WHERE FILL_DT BETWEEN '2022-01-01' AND '2022-12-31' 
GROUP BY month ORDER BY month LIMIT 100;
-- This query retrieves the count of migraine and hypertension prescriptions filled each month in 2022.
-- It groups the results by month and orders them chronologically, limiting the output to 100 rows.


Generate a pivot tabular dataset for number of claims for each month in 2022 for the category  MIGRAINE, HYPERTENSION and VACCINATION. partition by category as columns.
{'query': "SELECT strftime('%Y-%m', FILL_DT) AS month, \n       SUM(CASE WHEN CATEGORY_NAME = 'MIGRAINE' THEN 1 ELSE 0 END) AS MIGRAINE,\n       SUM(CASE WHEN CATEGORY_NAME = 'HYPERTENSION' THEN 1 ELSE 0 END) AS HYPERTENSION,\n       SUM(CASE WHEN CATEGORY_NAME = 'VACCINATION' THEN 1 ELSE 0 END) AS VACCINATION\nFROM RX_CLAIM \nWHERE strftime('%Y', FILL_DT) = '2022' \nAND CATEGORY_NAME IN ('MIGRAINE', 'HYPERTENSION', 'VACCINATION')\nGROUP BY month\nORDER BY month\nLIMIT 100;"}

Create a pivot dataset showing claim counts by CHANNEL as headers. Split where the category names are in ALLERGIES, DEPRESSION and  GLAUCOMA
{'query': "SELECT CHANNEL, \n       COUNT(CASE WHEN CATEGORY_NAME = 'ALLERGIES' THEN 1 END) AS Allergies_Claim_Count, \n       COUNT(CASE WHEN CATEGORY_NAME = 'DEPRESSION' THEN 1 END) AS Depression_Claim_Count, \n       COUNT(CASE WHEN CATEGORY_NAME = 'GLAUCOMA' THEN 1 END) AS Glaucoma_Claim_Count \nFROM RX_CLAIM \nWHERE CATEGORY_NAME IN ('ALLERGIES', 'DEPRESSION', 'GLAUCOMA') \nGROUP BY CHANNEL \nLIMIT 100;"}

SELECT strftime('%Y-%m', FILL_DT) AS month, CHANNEL, COUNT(*) AS claim_count FROM RX_CLAIM WHERE CATEGORY_NAME = 'HORMONE THERAPY' AND strftime('%Y', FILL_DT) = '2023' GROUP BY month, CHANNEL ORDER BY month, CHANNEL LIMIT 100;

Calculate claim counts by Channel for each quarter in 2023. Show Quarters as column headers.
SELECT CHANNEL, COUNT(CASE WHEN strftime('%Y-%m', FILL_DT) BETWEEN '2023-01' AND '2023-03' THEN 1 END) AS Q1,        COUNT(CASE WHEN strftime('%Y-%m', FILL_DT) BETWEEN '2023-04' AND '2023-06' THEN 1 END) AS Q2,        COUNT(CASE WHEN strftime('%Y-%m', FILL_DT) BETWEEN '2023-07' AND '2023-09' THEN 1 END) AS Q3,        COUNT(CASE WHEN strftime('%Y-%m', FILL_DT) BETWEEN '2023-10' AND '2023-12' THEN 1 END) AS Q4 FROM RX_CLAIM WHERE FILL_DT LIKE '2023%' GROUP BY CHANNEL LIMIT 100;

SELECT CHANNEL, COUNT(RX_CLAIM_NBR) AS claim_count FROM RX_CLAIM WHERE CATEGORY_NAME IN ('allergies', 'depression', 'glaucoma') GROUP BY CHANNEL LIMIT 100;


Create a pivot dataset showing claim counts by CHANNEL as headers. Split where the category names are in ALLERGIES, DEPRESSION and  GLAUCOMA

SELECT CHANNEL, CATEGORY_NAME, COUNT(*) AS CLAIM_COUNT \nFROM RX_CLAIM \nWHERE LOWER(CATEGORY_NAME) IN ('allergies', 'depression', 'glaucoma') \nGROUP BY CHANNEL, CATEGORY_NAME \nORDER BY CHANNEL, CATEGORY_NAME \nLIMIT 100;


SELECT AVG(AWP) AS average_weighted_price FROM RX_CLAIM WHERE GN_NAME = 'prednisone' AND strftime('%Y', PAID_DT) = '2023' LIMIT 100;

Show top 10 claims where provider location in TX

SELECT claim_nbr, client_id, net_mony, copay_mony, provider_view.provider_id, provider_view.provider_name, provider_view.provider_location
FROM claim_view inner join provider_view on claim_view.provider_id = provider_view.provider_id
WHERE provider_view.provider_location like '%TX%'

select DISTINCT channel_id from pharmacy_claims_drug_provider_view


/*
uvicorn simple_db_QnA.api_main:app --host 0.0.0.0 --port 443 --ssl-keyfile=simple_db_QnA/cert/key.pem --ssl-certfile=simple_db_QnA/cert/cert.pem

*/

-- Start View Creation

Create VIEW claim_view AS
SELECT client_id, member_id, groupvar1, groupvar2, groupvar3, groupvar4, groupvar5, prim_dt as fill_dt, claim_nbr, benefit_type COLLATE NOCASE as benefit_type_Pharmacy_or_Medical, channel_id, specialty_ind COLLATE NOCASE as specialty_indicator, brand_generic COLLATE NOCASE as brand_or_generic, drug_name_id, drug_cat_id, net_mony, copay_mony, admin_mony, third_party_mony, provider_id, prescriber_id, nabp_id, place_of_svc as place_of_service, quantity, days_supply, asp, asp_use, awp, dxt_class COLLATE NOCASE, disp_fee as dispense_fee, ingred_cost as ingredient_cost, sales_tax, claim_id
FROM claim;


Create VIEW drug_view AS
SELECT cd, cd_type, drug_name_id, drug_cat_id, brand_generic, obsolete_date, strength COLLATE NOCASE, mfg COLLATE NOCASE, HIC3, dsg_frm_desc as dosage_from_description, cd_desc COLLATE NOCASE COLLATE NOCASE as code_description
FROM drug;

create VIEW drug_category_view AS
SELECT drug_cat_id, drug_cat_name COLLATE NOCASE, drug_cat_code COLLATE NOCASE
FROM drug_category;

Create VIEW drug_name_view AS
Select drug_name_id, drug_name COLLATE NOCASE
FROM drug_name;

Create VIEW provider_view AS
Select provider_id, provider_name COLLATE NOCASE, ltrim(rtrim(city)) COLLATE NOCASE as provider_location_city, ltrim(rtrim(state)) COLLATE NOCASE as provider_Location_state, is_pharmacy, provider_specialty_id
FROM Providers;

drop view if exists provider_view;

-- End View Creation

select * from claim_view where benefit_type_Pharmacy_or_Medical = 'p' limit 10;


-- Create a view to simplify the claim data for easier querying
drop view if exists pharmacy_claims_drug_provider_view;

CREATE VIEW pharmacy_claims_drug_provider_view AS
SELECT c.client_id, c.member_id, c.prim_dt as fill_dt, c.claim_nbr, c.benefit_type COLLATE NOCASE as benefit_type_Pharmacy_or_Medical, c.specialty_ind COLLATE NOCASE as specialty_indicator, c.brand_generic COLLATE NOCASE as brand_or_generic, dn.drug_name COLLATE NOCASE as drug_name, c.net_mony, c.copay_mony, c.admin_mony, c.third_party_mony, c.quantity, c.days_supply, c.asp, c.asp_use, c.awp, c.dxt_class COLLATE NOCASE, disp_fee as dispense_fee, c.ingred_cost as ingredient_cost, c.sales_tax, c.claim_id, 
       p.provider_name COLLATE NOCASE as provider_name, 
       p.provider_location_city COLLATE NOCASE as provider_location_city, 
       p.provider_location_state COLLATE NOCASE as provider_location_state, 
       p.is_pharmacy, 
       d.cd COLLATE NOCASE as NDC_CD, 
       d.cd_type COLLATE NOCASE as CD_Type,
       d.strength COLLATE NOCASE as strength,
       d.mfg COLLATE NOCASE as manufacturer, 
       d.dosage_from_description COLLATE NOCASE as dosage_form_description, 
       d.obsolete_date,
       d.code_description COLLATE NOCASE as code_description,
       dc.drug_cat_name COLLATE NOCASE as drug_category_name, 
       dc.drug_cat_code COLLATE NOCASE as drug_category_code,
        CASE 
           WHEN c.channel_id = '1' THEN 'Retail'
           WHEN c.channel_id = '2' THEN 'Mail Order'
           WHEN c.channel_id = '3' THEN 'Specialty'
           WHEN c.channel_id = '5' THEN 'Retail90'
           WHEN c.channel_id = '6' THEN 'Physician Office'
           WHEN c.channel_id = '7' THEN 'Home Infusion'
           ELSE 'Other'
       END COLLATE NOCASE AS channel_type
from claim c
inner join provider_view p on c.provider_id = p.provider_id
INNER JOIN drug_view d ON c.drug_name_id = d.drug_name_id
INNER JOIN drug_category_view dc ON c.drug_cat_id = dc.drug_cat_id
INNER JOIN drug_name_view dn ON c.drug_name_id = dn.drug_name_id


select * from pharmacy_claims_Provider_view 
Order By Random()
Limit 10;


Query 1: Total Net Money by Drug Category of Nausea and Year

--sql 1
SELECT
    STRFTIME('%Y', fill_dt) AS fill_year,
    drug_category_name,
    SUM(net_mony) AS total_net_money
FROM
    pharmacy_claims_Provider_view
WHERE
    drug_category_name like '%Nausea%'
GROUP BY
    fill_year,
    drug_category_name
ORDER BY
    fill_year,
    total_net_money DESC;

Query 2: Top 5 Prescribers by Quantity Dispensed for a Specific Drug Type

--sql 2

SELECT
    prescriber_id,
    SUM(quantity) AS total_quantity_dispensed,
    COUNT(DISTINCT claim_id) AS total_claims
FROM
    pharmacy_claims_Provider_view
WHERE
    drug_name like  '%SYNTHROID%' -- Replace with any specific drug name
GROUP BY
    prescriber_id
ORDER BY
    total_quantity_dispensed DESC
LIMIT 5;

Query 3: Average Copay and Admin Fee per Claim for Pharmacy vs. Medical Benefits

--sql 3
SELECT
    benefit_type_Pharmacy_or_Medical,
    AVG(copay_mony) AS average_copay,
    AVG(admin_mony) AS average_admin_fee,
    COUNT(claim_id) AS number_of_claims
FROM
    pharmacy_claims_Provider_view
GROUP BY
    benefit_type_Pharmacy_or_Medical;


Query 4: Count of Unique Members and Claims by Provider State location in New York, Texas and Kentucky

--sql 4
SELECT
    provider_location_state,
    provider_location_city,
    COUNT(DISTINCT member_id) AS unique_members,
    COUNT(DISTINCT claim_id) AS unique_claims
FROM
    pharmacy_claims_Provider_view
WHERE
    provider_location_state in ('TX','NY', 'KY') AND provider_location_city IS NOT NULL
GROUP BY
    provider_location_state,
    provider_location_city
ORDER BY
    provider_location_state,
    provider_location_city;


Query 5: Provide Brand vs. Generic Drug Dispensing by Specialty Indicator (with Percentage)
--sql 5
SELECT
    specialty_indicator,
    brand_or_generic,
    COUNT(claim_id) AS total_claims,
    SUM(quantity) AS total_quantity,
    CAST(COUNT(claim_id) * 100.0 / SUM(COUNT(claim_id)) OVER (PARTITION BY specialty_indicator) AS REAL) AS percentage_of_claims_in_group
FROM
    pharmacy_claims_Provider_view
GROUP BY
    specialty_indicator,
    brand_or_generic
ORDER BY
    specialty_indicator,
    brand_or_generic;

Query 6: Total Claims and Net Money by Channel Type for a Specific Year 
-- Show total number of claims and total net money for each channel type in 2021.
Select channel_type, count(claim_id) as total_claims, sum(net_mony) as total_net_money
FROM pharmacy_claims_drug_provider_view
WHERE fill_dt BETWEEN '2021-01-01' AND '2021-12-31'
GROUP BY channel_type
ORDER BY channel_type;

Query 7: Top 10 Drugs by Total Net Money in 2022
SELECT
    drug_name,
    SUM(net_mony) AS total_net_money
FROM
    pharmacy_claims_drug_provider_view
WHERE
    STRFTIME('%Y', fill_dt) = '2021'
GROUP BY
    drug_name
ORDER BY
    total_net_money DESC
LIMIT 10;

Query 8: Average Days Supply by Drug Category in 2021
SELECT
    drug_category_name,
    AVG(days_supply) AS average_days_supply
FROM
    pharmacy_claims_drug_provider_view
WHERE
    STRFTIME('%Y', fill_dt) = '2021'
GROUP BY
    drug_category_name
ORDER BY
    average_days_supply DESC
LIMIT 10;