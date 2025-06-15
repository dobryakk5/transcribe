CREATE OR REPLACE FUNCTION update_category(
    p_user_id BIGINT,
    old_name TEXT,
    new_name TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    -- Обновляем категорию в справочнике
    UPDATE categories 
    SET name = new_name 
    WHERE user_id = p_user_id AND name = old_name;
    
    -- Если обновление прошло (хоть одна строка затронута)
    IF FOUND THEN
        -- Обновляем связанные покупки
        UPDATE purchases
        SET category = new_name
        WHERE user_id = p_user_id AND category = old_name;
        
        RETURN TRUE;
    END IF;
    
    -- Если категория не найдена
    RETURN FALSE;
EXCEPTION
    WHEN unique_violation THEN
        -- Объединяем дубликаты: переносим покупки и удаляем старую категорию
        UPDATE purchases
        SET category = new_name
        WHERE user_id = p_user_id AND category = old_name;
        
        DELETE FROM categories
        WHERE user_id = p_user_id AND name = old_name;
        
        RETURN TRUE;
END;

CREATE OR REPLACE FUNCTION update_subcategory(
    p_user_id BIGINT,
    p_category_name TEXT,
    old_name TEXT,
    new_name TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    v_category_id INT;
BEGIN
    -- Получаем ID категории
    SELECT id INTO v_category_id 
    FROM categories 
    WHERE user_id = p_user_id AND name = p_category_name;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Обновляем подкатегорию
    UPDATE subcategories 
    SET name = new_name 
    WHERE user_id = p_user_id 
      AND category_id = v_category_id 
      AND name = old_name;
    
    IF FOUND THEN
        -- Обновляем связанные покупки
        UPDATE purchases
        SET subcategory = new_name
        WHERE user_id = p_user_id 
          AND category = p_category_name 
          AND subcategory = old_name;
        
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
EXCEPTION
    WHEN unique_violation THEN
        -- Объединение дубликатов
        UPDATE purchases
        SET subcategory = new_name
        WHERE user_id = p_user_id 
          AND category = p_category_name 
          AND subcategory = old_name;
        
        DELETE FROM subcategories
        WHERE user_id = p_user_id 
          AND category_id = v_category_id 
          AND name = old_name;
        
        RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_last_purchase(p_user_id BIGINT) 
RETURNS BOOLEAN AS $$
BEGIN
    DELETE FROM purchases
    WHERE id = (
        SELECT id
        FROM purchases
        WHERE user_id = p_user_id
        ORDER BY ts DESC
        LIMIT 1
    );
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_last_purchase(p_user_id BIGINT)
RETURNS TABLE (category TEXT, subcategory TEXT, price NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT p.category, p.subcategory, p.price
    FROM purchases p
    WHERE p.user_id = p_user_id
    ORDER BY p.ts DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;