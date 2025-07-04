select count(*) 
from pharmacy_claims_drug_provider_view
where date(fill_dt) >= date('2021-01-01') 
    and date(fill_dt) < date('2021-03-01')

Select count(*)
from claim
where date(prim_dt) >= date('2021-03-01') 

select * from claim limit 20;

----------------

ATTACH DATABASE 'data/sample_data.db' AS destinationDB;




SELECT sql
FROM sqlite_master
WHERE type = 'table' AND name = 'claim';

select DISTINCT place_of_svc, count(*)
from claim
group by place_of_svc
;

select * from channel_t limit 10;


Drop table channel_t;
Truncate channel_T;
where claim_id = 1;

DELETE FROM channel_t
WHERE channel_id = 1;

Select * from sqlite_master
where type = 'table';-- and name = 'channel_t';

