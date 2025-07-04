
ATTACH DATABASE 'data/sample_data.db' AS destinationDB;

CREATE TABLE destinationDB.providers_t 
(
    provider_id integer PRIMARY KEY, 
    provider_name TEXT, 
    provider_location_city TEXT, 
    provider_Location_state TEXT,
    is_pharmacy_or_clinic boolean,
    created_dt DATETIME,
    updated_dt DATETIME
);

CREATE TABLE destinationDB.claim_t  
(
    claim_id INTEGER PRIMARY KEY,   --- maps to claim_id
    claim_nbr TEXT,  --- maps to claim_nbr
    member_id TEXT,
    fill_dt TEXT,  --- maps to prim_dt
    claim_type_cd TEXT,  -- maps to Benefit Type - Medical and Pharmacy
    channel_id INTEGER,  -- Retail, Mail Order, Etc.
    specialty_indicator_flag TEXT,  
    brand_generic_cd TEXT,
    NDC ,
    drug_name_id INTEGER,
    drug_category_id INTEGER,  -- maps to drug_cat_id
    net_money REAL,  -- maps to net_mony
    copay_money REAL,  -- maps to copay_mony
    admin_money REAL,  -- maps to admin_mony
    third_party_money REAL,  -- maps to third_party_mony
    provider_id TEXT,
    place_of_svc_id integer,
    quantity REAL,
    days_supply INTEGER,
    asp REAL,
    awp REAL,
    dispense_fee REAL,
    ingredient_cost REAL,
    days_supply_claim_count INTEGER,
    FOREIGN KEY (provider_id) REFERENCES providers_t(provider_id),
    FOREIGN KEY (drug_name_id) REFERENCES drug_name_t(drug_name_id),
    FOREIGN KEY (drug_category_id) REFERENCES drug_category_t(drug_category_id),
    FOREIGN KEY (channel_id) REFERENCES channel_t(channel_id)
    FOREIGN KEY (claim_type_cd) REFERENCES claim_type_t(claim_type_id)   
    ForeIGN KEY (brand_generic_cd) REFERENCES brand_generic_t(brand_generic_cd)
    FOREIGN KEY (place_of_svc_id) REFERENCES place_of_service_t(place_of_service_id) 
    FOREIGN KEY (NDC) REFERENCES drug_t(NDC)
);   

CREATE TABLE destinationDB.drug_name_t 
(
    drug_name_id INTEGER PRIMARY KEY,
    drug_name TEXT,
    specialty_indicator_flag TEXT,
    drug_source_cd TEXT,
    FOREIGN KEY (drug_source_cd) REFERENCES drug_source_type_t(drug_source_type_cd)
);

CREATE TABLE destinationDB.drug_category_t 
(
    drug_category_id INTEGER PRIMARY KEY,
    drug_category_description TEXT
);

CREATE TABLE destinationDB.drug_t 
(
    drug_id INTEGER PRIMARY KEY AUTOINCREMENT,
    NDC TEXT,
    drug_name_id INTEGER,
    drug_category_id INTEGER,
    brand_generic_cd TEXT,
    mfg_name TEXT,
    strength TEXT,
    dosage_form_description TEXT,
    FOREIGN KEY (drug_name_id) REFERENCES drug_name_t(drug_name_id),
    FOREIGN KEY (drug_category_id) REFERENCES drug_category_t(drug_category_id)
);
CREATE TABLE destinationDB.channel_t 
(
    channel_id INTEGER PRIMARY KEY,
    channel_name TEXT
);
CREATE TABLE destinationDB.claim_type_t 
(
    claim_type_id TEXT PRIMARY KEY,
    claim_type_description TEXT
);

CREATE TABLE destinationDB.brand_generic_t 
(
    brand_generic_cd TEXT PRIMARY KEY,   
    brand_generic_description TEXT
);

CREATE TABLE destinationDB.drug_source_type_t 
(
    drug_source_type_cd TEXT PRIMARY KEY,   
    drug_source_description TEXT
);

Create Table destinationDB.place_of_service_t
(
    place_of_service_id INTEGER PRIMARY KEY,
    place_of_service_description TEXT
);

