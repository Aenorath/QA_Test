import pytest
import sqlite3

COMPONENT_DETAILS = {
    'weapon': {'table': 'weapons', 'pk_col': 'weapon', 'params': ["reload speed", "rotational speed", "diameter", "power volley", "count"]},
    'hull': {'table': 'hulls', 'pk_col': 'hull', 'params': ["armor", "type", "capacity"]},
    'engine': {'table': 'engines', 'pk_col': 'engine', 'params': ["power", "type"]}
}

def fetch_ship_component_id(cursor, ship_id, component_type):
    query = f"SELECT \"{component_type}\" FROM ships WHERE ship = ?"
    cursor.execute(query, (ship_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def fetch_component_params(cursor, component_id, component_type):
    details = COMPONENT_DETAILS[component_type]
    table_name = details['table']
    pk_col_name = details['pk_col']
    param_names = details['params']
    
    select_cols_str = ", ".join([f'"{p}"' for p in param_names])
    
    query = f"SELECT {select_cols_str} FROM \"{table_name}\" WHERE \"{pk_col_name}\" = ?"
    cursor.execute(query, (component_id,))
    result = cursor.fetchone()
    return dict(zip(param_names, result)) if result else {}

def test_ship_component_changes(db_cursors, ship_id, component_type):
    cursor_orig, cursor_rand = db_cursors

    original_ship_comp_id = fetch_ship_component_id(cursor_orig, ship_id, component_type)
    randomized_ship_comp_id = fetch_ship_component_id(cursor_rand, ship_id, component_type)

    if original_ship_comp_id is None or randomized_ship_comp_id is None:
        pytest.fail(f"Could not find component IDs for {ship_id}, component {component_type}. "
                    f"Original: {original_ship_comp_id}, Randomized: {randomized_ship_comp_id}", 
                    pytrace=False)
        return 

    if original_ship_comp_id != randomized_ship_comp_id:
        message = (f"{ship_id}, {randomized_ship_comp_id}\n"
                   f"expected {original_ship_comp_id}, was {randomized_ship_comp_id}")
        pytest.fail(message, pytrace=False)
        return 

    original_params = fetch_component_params(cursor_orig, original_ship_comp_id, component_type)
    randomized_params = fetch_component_params(cursor_rand, original_ship_comp_id, component_type) 

    if not original_params: 
         pytest.fail(f"Could not fetch original parameters for component {original_ship_comp_id} ({component_type}).", 
                     pytrace=False)
         return
    if not randomized_params: 
         pytest.fail(f"Could not fetch randomized parameters for component {original_ship_comp_id} ({component_type}), "
                     f"even though original parameters were found. This might indicate a data integrity issue in the randomized DB.",
                     pytrace=False)
         return

    for param_name, original_value in original_params.items():
        if param_name not in randomized_params:
            pytest.fail(f"{ship_id}, {original_ship_comp_id}\n"
                        f"Parameter '{param_name}' missing in randomized data for component.", 
                        pytrace=False)
            return

        randomized_value = randomized_params[param_name]
        
        if original_value != randomized_value:
            message = (f"{ship_id}, {original_ship_comp_id}\n" 
                       f"{param_name}: expected {original_value}, was {randomized_value}")
            pytest.fail(message, pytrace=False)
            return