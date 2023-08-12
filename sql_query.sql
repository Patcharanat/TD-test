WITH denormalized AS (
  SELECT
    *,
    (product.retail_price * sales.quantity) AS total
  FROM `dataset.Sales Transaction` AS sales
  LEFT JOIN `dataset.Product` AS product
  ON sales.product_id = product.product_id
),

product_sales AS (
  SELECT
    product_name,
    SUM(total) AS sales_value
  FROM denormalized
  GROUP BY 1
),

ranked_products AS (
  SELECT
    product_class.product_class_name,
    product_sales.product_name,
    product_sales.sales_value,
    RANK() OVER(PARTITION BY product_class_name ORDER BY sales_value DESC) AS rank
  FROM product_sales
  LEFT JOIN `dataset.Product Class` AS product_class
  ON product_sales.product_class_id = product_class.product_class_id
)
SELECT
  product_class_name,
  rank,
  product_name,
  sales_value
FROM ranked_products
WHERE rank <= 2
ORDER BY
  product_class_name,
  sales_value DESC;
