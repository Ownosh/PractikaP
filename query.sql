SELECT
    zp.nomer AS nomer_zakaza,
    k.naimenovanie AS zakazchik,
    n.naimenovanie AS produkt,
    sz.kolichestvo AS kolichestvo,
    ROUND(SUM(ss.kolichestvo * c.cena), 2) AS sebestoimost_edinicy,
    ROUND(sz.kolichestvo * SUM(ss.kolichestvo * c.cena), 2) AS polnaya_stoimost
FROM zakaz_pokupatelya zp
JOIN kontragent k ON k.id_kontragenta = zp.id_zakazchika
JOIN stroka_zakaza sz ON sz.id_zakaza = zp.id_zakaza
JOIN nomenklatura n ON n.id_nomenklatury = sz.id_nomenklatury
JOIN specifikaciya sp ON sp.id_produkcii = n.id_nomenklatury
JOIN sostav_specifikacii ss ON ss.id_specifikacii = sp.id_specifikacii
JOIN cena c ON c.id_nomenklatury = ss.id_materiala
GROUP BY zp.nomer, k.naimenovanie, n.naimenovanie, sz.kolichestvo;