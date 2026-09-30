-- ============================================================
-- Task 3: Active Customers by Country
--
-- Requirements:
-- 1. Only count customers whose status is 'active'.
-- 2. Group the results by country.
-- 3. Name the count column active_count.
-- 4. Sort from the highest customer count to the lowest.
-- ============================================================

SELECT
    country,
    COUNT(*) AS active_count
FROM customers
WHERE status = 'active'
GROUP BY country
ORDER BY active_count DESC;