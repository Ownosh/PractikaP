-- Единица измерения
CREATE TABLE edinica_izmereniya (
    id_edinicy   SERIAL      PRIMARY KEY,
    oboznachenie VARCHAR(20) NOT NULL UNIQUE
);
 
-- Контрагент (заказчики и поставщики)
CREATE TABLE kontragent (
    id_kontragenta    VARCHAR(9)   PRIMARY KEY,
    naimenovanie      VARCHAR(255) NOT NULL,
    inn               VARCHAR(20),
    adres             VARCHAR(255),
    telefon           VARCHAR(20),
    yavl_postavshikom BOOLEAN      NOT NULL DEFAULT FALSE,
    yavl_pokupatel    BOOLEAN      NOT NULL DEFAULT FALSE
);
 
-- Номенклатура (продукция и материалы)
CREATE TABLE nomenklatura (
    id_nomenklatury  SERIAL       PRIMARY KEY,
    kod              VARCHAR(20)  UNIQUE,
    naimenovanie     VARCHAR(255) NOT NULL,
    id_edinicy       INTEGER      NOT NULL REFERENCES edinica_izmereniya(id_edinicy)
);
 
-- Цена
CREATE TABLE cena (
    id_ceny          SERIAL         PRIMARY KEY,
    id_nomenklatury  INTEGER        NOT NULL REFERENCES nomenklatura(id_nomenklatury),
    cena             NUMERIC(10, 2) NOT NULL,
    data_ustanovki   DATE           NOT NULL DEFAULT CURRENT_DATE
);
 
-- Спецификация
CREATE TABLE specifikaciya (
    id_specifikacii  SERIAL         PRIMARY KEY,
    naimenovanie     VARCHAR(255)   NOT NULL,
    id_produkcii     INTEGER        NOT NULL REFERENCES nomenklatura(id_nomenklatury),
    kol_vo_produkcii NUMERIC(10, 3) NOT NULL DEFAULT 1,
    id_izgotovitelya VARCHAR(9)     NOT NULL REFERENCES kontragent(id_kontragenta)
);
 
-- Состав спецификации
CREATE TABLE sostav_specifikacii (
    id_stroki       SERIAL         PRIMARY KEY,
    id_specifikacii INTEGER        NOT NULL REFERENCES specifikaciya(id_specifikacii),
    id_materiala    INTEGER        NOT NULL REFERENCES nomenklatura(id_nomenklatury),
    kolichestvo     NUMERIC(10, 4) NOT NULL
);
 
-- Заказ покупателя
CREATE TABLE zakaz_pokupatelya (
    id_zakaza     SERIAL     PRIMARY KEY,
    nomer         INTEGER    NOT NULL,
    data          DATE       NOT NULL,
    id_zakazchika VARCHAR(9) NOT NULL REFERENCES kontragent(id_kontragenta)
);
 
-- Строка заказа
CREATE TABLE stroka_zakaza (
    id_stroki       SERIAL         PRIMARY KEY,
    id_zakaza       INTEGER        NOT NULL REFERENCES zakaz_pokupatelya(id_zakaza),
    id_nomenklatury INTEGER        NOT NULL REFERENCES nomenklatura(id_nomenklatury),
    kolichestvo     NUMERIC(10, 3) NOT NULL,
    cena            NUMERIC(10, 2) NOT NULL
);
 
-- Производство
CREATE TABLE proizvodstvo (
    id_proizvodstva SERIAL  PRIMARY KEY,
    nomer           INTEGER NOT NULL,
    data            DATE    NOT NULL
);
 
-- Продукция производства
CREATE TABLE produkciya_proizvodstva (
    id_stroki       SERIAL         PRIMARY KEY,
    id_proizvodstva INTEGER        NOT NULL REFERENCES proizvodstvo(id_proizvodstva),
    id_nomenklatury INTEGER        NOT NULL REFERENCES nomenklatura(id_nomenklatury),
    kolichestvo     NUMERIC(10, 3) NOT NULL
);
 
-- Материалы производства
CREATE TABLE materialy_proizvodstva (
    id_stroki       SERIAL         PRIMARY KEY,
    id_proizvodstva INTEGER        NOT NULL REFERENCES proizvodstvo(id_proizvodstva),
    id_materiala    INTEGER        NOT NULL REFERENCES nomenklatura(id_nomenklatury),
    kolichestvo     NUMERIC(10, 4) NOT NULL
);
 
-- Расчёт себестоимости
CREATE TABLE raschet_sebestoimosti (
    id_rascheta         SERIAL         PRIMARY KEY,
    data                DATE           NOT NULL DEFAULT CURRENT_DATE,
    id_produkcii        INTEGER        NOT NULL REFERENCES nomenklatura(id_nomenklatury),
    id_specifikacii     INTEGER        NOT NULL REFERENCES specifikaciya(id_specifikacii),
    itogo_sebestoimost  NUMERIC(10, 2) NOT NULL
);
 
-- Строка расчёта
CREATE TABLE stroka_rascheta (
    id_stroki   SERIAL         PRIMARY KEY,
    id_rascheta INTEGER        NOT NULL REFERENCES raschet_sebestoimosti(id_rascheta),
    id_materiala INTEGER       NOT NULL REFERENCES nomenklatura(id_nomenklatury),
    kolichestvo NUMERIC(10, 4) NOT NULL,
    cena        NUMERIC(10, 2) NOT NULL
);