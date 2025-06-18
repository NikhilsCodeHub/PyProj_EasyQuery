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
SELECT CHANNEL, \n       COUNT(CASE WHEN strftime('%Y-%m', FILL_DT) BETWEEN '2023-01' AND '2023-03' THEN 1 END) AS Q1, \n       COUNT(CASE WHEN strftime('%Y-%m', FILL_DT) BETWEEN '2023-04' AND '2023-06' THEN 1 END) AS Q2, \n       COUNT(CASE WHEN strftime('%Y-%m', FILL_DT) BETWEEN '2023-07' AND '2023-09' THEN 1 END) AS Q3, \n       COUNT(CASE WHEN strftime('%Y-%m', FILL_DT) BETWEEN '2023-10' AND '2023-12' THEN 1 END) AS Q4 \nFROM RX_CLAIM \nWHERE FILL_DT LIKE '2023%' \nGROUP BY CHANNEL \nLIMIT 100;
