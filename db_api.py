from sqlalchemy import true
import settings
import math
import pandas


def get_asset_child(parent_id):
    conn = settings.conn
    query = """
    SELECT
        *
    FROM
        (SELECT 
            to_id   
        FROM
            relation
        WHERE 
            from_id = %s
            AND relation_type = 'Belong' ) root_a
    LEFT JOIN asset a ON (root_a.to_id = a.id);
    """
    df = pandas.read_sql_query(
        sql=query, con=conn, params=(parent_id,))
    data = [
        {
            "id": i["id"],
            "name": i["name"].split("-")[0],
            "type": i["type"],
            "children": []
        } for i in df.to_dict("records")
    ]
    return data


def get_asset_parent(tenant_id, page_size, page):
    conn = settings.conn
    query = """
    SELECT
        count(*)
    FROM
        Asset
    WHERE tenant_id = %s
        AND id NOT IN (SELECT 
            to_id   
        FROM
            relation
        WHERE  relation_type = 'Belong' ) 
    """
    df = pandas.read_sql_query(
        sql=query, con=conn, params=(tenant_id,))
    total_elements = int(df["count"][0])
    total_pages = math.ceil(total_elements/page_size)
    has_next = True if total_pages > (page + 1) else False
    if total_elements == 0:
        return {
            "total_elements": total_elements,
            "total_pages": total_pages,
            "has_next": has_next,
            "data": []
        }
    query = """
    SELECT
        *
    FROM
        Asset
    WHERE tenant_id = %s
        AND id NOT IN (SELECT 
            to_id   
        FROM
            relation
        WHERE  relation_type = 'Belong' )
    LIMIT %s
    OFFSET %s;
    """
    df = pandas.read_sql_query(
        sql=query, con=conn, params=(tenant_id, page_size, page,))
    data = [
        {
            "id": i["id"],
            "name": i["name"].split("-")[0],
            "type": i["type"],
            "children": []
        } for i in df.to_dict("records")
    ]
    new_list = []
    for key in data:
        if(key["type"] != "Post"):
            new_list.append({
                "id": key["id"],
                "name": key["name"],
                "type": key["type"],
                "children": None
            })
        else:
            new_list.append({
                "id": key["id"],
                "name": key["name"],
                "type": key["type"],
                "children": get_asset_child(key["id"],)
            })
    return {
        "total_elements": total_elements,
        "total_pages": total_pages,
        "has_next": has_next,
        "data": new_list
    }


def get_test(tenant_id, page_size, page):
    conn = settings.conn
    query = """
    SELECT
        *
    FROM
        Asset
    WHERE tenant_id = %s
        AND id NOT IN (SELECT 
            to_id   
        FROM
            relation
        WHERE  relation_type = 'Belong' )
        AND UPPER(name) ~ %s;
    LIMIT %s
    OFFSET %s;
    """
    df = pandas.read_sql_query(
        sql=query, con=conn, params=(tenant_id, page_size, page))
    print(df)
    return true
