-- SQLite
-- Empty all tables in the database

/* 

DELETE FROM Drugs;
DELETE FROM Pharmacies;
DELETE FROM Diseases;
DELETE FROM Members;
DELETE FROM Diseases_By_Channel;
DELETE FROM Member_Costs;
DELETE FROM Cost_Of_Care; 

*/

-- Set mode to CSV
.mode csv

--- Load data
.import simple_db_QnA/data/Top_Drugs2.csv Drugs
.import simple_db_QnA/data/Top_Members2.csv Members
.import simple_db_QnA/data/Top_Diseases2.csv Diseases
.import simple_db_QnA/data/Top_Pharmacies2.csv Pharmacies
.import simple_db_QnA/data/New_High_Cost_Members2.csv Member_Costs
.import 'simple_db_QnA/data/Top_Diseases by Channel2.csv' Diseases_By_Channel
.import simple_db_QnA/data/Total_Cost_of_Care_Detail2.csv Cost_Of_Care



--- 