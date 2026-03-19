-- Единицы измерения
INSERT INTO edinica_izmereniya (oboznachenie) VALUES
('шт'),
('кг');
 
-- Комбинат (исполнитель) — нужен для спецификации
INSERT INTO kontragent (id_kontragenta, naimenovanie, inn, adres, telefon, yavl_postavshikom, yavl_pokupatel) VALUES
('000000000', 'ООО Молочный комбинат "Полесье"', '', '', '', FALSE, FALSE);
 
-- Номенклатура (из Цены.xlsx + Производство.xlsx)
INSERT INTO nomenklatura (kod, naimenovanie, id_edinicy) VALUES
('НФ-00000001', 'Кефир 2,5% 900г.',               1),
('НФ-00000002', 'Кефир 3,2% 900г.',               1),
('НФ-00000003', 'Молоко 2,5% 900г.',              1),
('НФ-00000004', 'Молоко нормализованное',          2),
('НФ-00000005', 'Закваска сметанная',              2),
('НФ-00000006', 'Сметана классическая 15% 540г.', 1),
('НФ-00000007', 'Молоко 3,2% 900г.',              1),
('НФ-00000008', 'Сметана классическая 20% 540г.', 1);
 
-- Цены (из Цены.xlsx)
INSERT INTO cena (id_nomenklatury, cena, data_ustanovki) VALUES
(5,  45.00, '2025-01-01'),  -- Закваска сметанная
(1,  80.00, '2025-01-01'),  -- Кефир 2,5% 900г.
(2,  82.00, '2025-01-01'),  -- Кефир 3,2% 900г.
(3,  70.00, '2025-01-01'),  -- Молоко 2,5% 900г.
(7,  76.00, '2025-01-01'),  -- Молоко 3,2% 900г.
(4,  34.00, '2025-01-01'),  -- Молоко нормализованное
(6,  89.00, '2025-01-01'),  -- Сметана классическая 15% 540г.
(8,  92.00, '2025-01-01');  -- Сметана классическая 20% 540г.
 
-- Спецификация (из Спецификация.xlsx)
INSERT INTO specifikaciya (naimenovanie, id_produkcii, kol_vo_produkcii, id_izgotovitelya) VALUES
('Основная Сметана 15%', 6, 1, '000000000');
 
-- Состав спецификации (из Спецификация.xlsx)
INSERT INTO sostav_specifikacii (id_specifikacii, id_materiala, kolichestvo) VALUES
(1, 4, 0.90),   -- Молоко нормализованное 0.9 кг
(1, 5, 0.07);   -- Закваска сметанная 0.07 кг
 
-- Заказ покупателя № 2 от 06.06.2025 (из Заказ_покупателя.xlsx)
-- Заказчик: ООО "Ассоль" = id 000000010
INSERT INTO zakaz_pokupatelya (nomer, data, id_zakazchika) VALUES
(2, '2025-06-06', '000000010');
 
-- Строки заказа (из Заказ_покупателя.xlsx)
INSERT INTO stroka_zakaza (id_zakaza, id_nomenklatury, kolichestvo, cena) VALUES
(1, 1, 12, 80.00),  -- Кефир 2,5% 900г. × 12 шт
(1, 2,  9, 82.00),  -- Кефир 3,2% 900г. × 9 шт
(1, 3, 10, 79.00);  -- Молоко 2,5% 900г. × 10 шт
 
-- Производство № 1 от 09.06.2025 (из Производство.xlsx)
INSERT INTO proizvodstvo (nomer, data) VALUES
(1, '2025-06-09');
 
-- Продукция производства
INSERT INTO produkciya_proizvodstva (id_proizvodstva, id_nomenklatury, kolichestvo) VALUES
(1, 6, 1);  -- Сметана классическая 15% 540г. × 1 шт
 
-- Материалы производства
INSERT INTO materialy_proizvodstva (id_proizvodstva, id_materiala, kolichestvo) VALUES
(1, 4, 0.90),  -- Молоко нормализованное 0.9 кг
(1, 5, 0.07);  -- Закваска сметанная 0.07 кг