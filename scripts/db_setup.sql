CREATE FUNCTION determine_time_of_day (val TIME)
	RETURNS VARCHAR(20)
	LANGUAGE plpgsql
AS $BODY$
BEGIN
	IF (val < '06:00:00'::TIME AND val >= '00:00:00'::TIME) THEN
		RETURN 'Ночь';
	END IF;

	IF (val < '12:00:00'::TIME AND val >= '06:00:00'::TIME) THEN
		RETURN 'Утро';
	END IF;

	IF (val < '18:00:00'::TIME AND val >= '12:00:00'::TIME) THEN
		RETURN 'День';
	END IF;

	IF (val > '18:00:00'::TIME) THEN
		RETURN 'Вечер';
	END IF;

	RETURN '';
END
$BODY$

CREATE FUNCTION time_in_interval (
	begin_time TIME WITHOUT TIME ZONE,
	end_time TIME WITHOUT TIME ZONE,
	check_time TIME WITHOUT TIME ZONE
)
    RETURNS BOOL
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
	IF (begin_time < end_time) THEN
		RETURN (check_time >= begin_time AND check_time < end_time);
	END IF;

	--crosses midnight
	RETURN (check_time >= begin_time OR check_time < end_time);

END
$BODY$;

CREATE TABLE Categories (
	category_id BIGINT NOT NULL PRIMARY KEY,
	category_name VARCHAR(100) NOT NULL
);

CREATE TABLE Goods (
	goods_id BIGINT NOT NULL PRIMARY KEY,
	category_id BIGINT NOT NULL,
	goods_name VARCHAR(200) NOT NULL,
	description TEXT,
	price MONEY NOT NULL
);

ALTER TABLE Goods
ADD FOREIGN KEY (category_id)
	REFERENCES Categories (category_id)
	ON UPDATE CASCADE;


CREATE TABLE Users (
	user_id BIGINT NOT NULL PRIMARY KEY,
	user_name VARCHAR(100) NOT NULL,
	country VARCHAR(20) DEFAULT 'unknown',
	visits_count INT DEFAULT 0,
	carts_count INT DEFAULT 0,
	payments_count INT DEFAULT 0,
	last_ip INET NOT NULL
);

CREATE TABLE Transactions (
	transaction_id BIGINT NOT NULL PRIMARY KEY,
	user_id BIGINT NOT NULL,
	created_at_d DATE NOT NULL,
	created_at_t TIME WITHOUT TIME ZONE NOT NULL
);

ALTER TABLE Transactions
ADD FOREIGN KEY (user_id)
	REFERENCES Users (user_id)
	ON UPDATE CASCADE;

CREATE TABLE TransactionsGoods (
	transactions_goods_id BIGINT NOT NULL,
	transaction_id BIGINT NOT NULL,
	goods_id BIGINT NOT NULL,
	goods_count INT NOT NULL,
	total_price MONEY NOT NULL
);

ALTER TABLE TransactionsGoods
ADD FOREIGN KEY (transaction_id)
	REFERENCES Transactions (transaction_id)
	ON UPDATE CASCADE,
ADD FOREIGN KEY (goods_id)
	REFERENCES Goods (goods_id)
	ON UPDATE CASCADE;

CREATE TABLE CategoriesVisits (
	categories_visits BIGSERIAL,
	category_id BIGINT NOT NULL,
	visitor_ip INET NOT NULL,
	visitor_country VARCHAR(20) DEFAULT 'unknown',
	visited_at_d DATE NOT NULL,
	visited_at_t TIME WITHOUT TIME ZONE NOT NULL
);

ALTER TABLE CategoriesVisits
ADD FOREIGN KEY (category_id)
	REFERENCES Categories (category_id)
	ON UPDATE CASCADE;

CREATE TABLE Queries (
	query_id BIGSERIAL,
	query_ip INET NOT NULL,
	query_text VARCHAR(200) NOT NULL,
	queried_at_d DATE NOT NULL,
	queried_at_t TIME WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE UnusedCarts (
	cart_id BIGINT PRIMARY KEY
);

CREATE VIEW TimeOfDaySplittedVisits (
	category_id,
	visitor_country,
	time_of_day
)
AS SELECT category_id,
	visitor_country,
	determine_time_of_day(visited_at_t)
FROM CategoriesVisits;
