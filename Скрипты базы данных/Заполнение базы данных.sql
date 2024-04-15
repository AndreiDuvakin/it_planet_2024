INSERT INTO region_types ("type") VALUES 
    ('Район'),
    ('Город'),
    ('Деревня'),
    ('Село'),
    ('Поселок'),
    ('Область'),
    ('Край'),
    ('Республика'),
   	('Страна');

   
INSERT INTO regions ("name", latitude, longitude, type_id)
VALUES 
    ('Россия', 60.0000, 90.0000, 9), -- Страна
    ('Беларусь', 49.0000, 32.0000, 9), -- Страна
    ('Казахстан', 53.0000, 28.0000, 9); -- Страна

    
INSERT INTO regions ("name", parent_region, latitude, longitude, type_id)
VALUES 
    ('Москва', 1, 55.7558, 37.6176, 2), -- Город
    ('Санкт-Петербург', 1, 59.9343, 30.3351, 2), -- Город
    ('Краснодарский край', 1, 45.0355, 38.9753, 6), -- Область
    ('Московская область', 1, 55.5043, 37.1229, 6), -- Область
    ('Ростовская область', 1, 47.2357, 39.7015, 6), -- Область
    ('Крым', 1, 45.3441, 35.3570, 8), -- Республика
    ('Воронежская область', 1, 51.6755, 39.2088, 6), -- Область
    ('Татарстан', 1, 55.7944, 49.1012, 8), -- Республика
    ('Башкортостан', 1, 54.2315, 55.3257, 8), -- Республика
    ('Самарская область', 1, 53.2020, 50.1405, 6), -- Область
    ('Астраханская область', 1, 46.3479, 48.0336, 6), -- Область
    ('Красноярский край', 1, 56.0106, 92.8526, 6), -- Край
    ('Приморский край', 1, 43.1735, 132.0114, 6), -- Край
    ('Свердловская область', 1, 56.8380, 60.5975, 6), -- Область
    ('Новосибирская область', 1, 55.0084, 82.9357, 6); -- Область
    
    
INSERT INTO weathers (temperature, humidity, wind_speed, weather_condition, precipitation_amount, measurement_date_time, region_id)
SELECT 
    ROUND((RANDOM() * 30 - 10)::numeric, 2) AS temperature,
    ROUND((RANDOM() * 100)::numeric, 2) AS humidity,
    ROUND((RANDOM() * 20)::numeric, 2) AS wind_speed,
    CASE 
        WHEN RANDOM() < 0.25 THEN 'CLEAR'
        WHEN RANDOM() < 0.5 THEN 'CLOUDY'
        WHEN RANDOM() < 0.75 THEN 'RAIN'
        ELSE 'SNOW'
    END AS weather_condition,
    ROUND((RANDOM() * 10)::numeric, 2) AS precipitation_amount,
    CURRENT_DATE - INTERVAL '3 days' * RANDOM() AS measurement_date_time,
    r.id
FROM regions r
CROSS JOIN generate_series(1, 30);



INSERT INTO public.forecasts (date_time, temperature, weather_condition, region_id)
SELECT 
    CURRENT_DATE + INTERVAL '3 days' + INTERVAL '1 day' * ROUND(RANDOM() * 7)::int AS date_time,
    ROUND((RANDOM() * 30 - 10)::numeric, 2) AS temperature,
    CASE 
        WHEN RANDOM() < 0.25 THEN 'CLEAR'
        WHEN RANDOM() < 0.5 THEN 'CLOUDY'
        WHEN RANDOM() < 0.75 THEN 'RAIN'
        ELSE 'SNOW'
    END AS weather_condition,
    r.id
FROM regions r
CROSS JOIN generate_series(1, 30);


INSERT INTO public.weather_forecasts (weather_id, forecast_id)
SELECT 
    w.id AS weather_id,
    f.id AS forecast_id
FROM 
    weathers w
JOIN 
    forecasts f ON w.region_id = f.region_id;
