import pytest
import sqlite3
import random
import shutil
import os

ORIGINAL_DB_NAME = 'ship_database.db'
RANDOMIZED_DB_NAME = 'randomized_ship_database.db'

WEAPON_PARAMS = ["reload speed", "rotational speed", "diameter", "power volley", "count"]
HULL_PARAMS = ["armor", "type", "capacity"]
ENGINE_PARAMS = ["power", "type"]

@pytest.fixture(scope="session")
def db_cursors():
    if not os.path.exists(ORIGINAL_DB_NAME):
        pytest.exit(f"{ORIGINAL_DB_NAME} not found. Run create_db.py to generate it.")

    shutil.copyfile(ORIGINAL_DB_NAME, RANDOMIZED_DB_NAME)

    conn_orig = sqlite3.connect(ORIGINAL_DB_NAME)
    cursor_orig = conn_orig.cursor()

    conn_rand = sqlite3.connect(RANDOMIZED_DB_NAME)
    cursor_rand = conn_rand.cursor()
    print(f"Connected to original database: {ORIGINAL_DB_NAME} and randomized database: {RANDOMIZED_DB_NAME}")
    strategy_A_component_swap = random.choice([True, False])
    print(f"\nApplying randomization strategy: {'Component Swap (A)' if strategy_A_component_swap else 'Parameter Change (B)'}")

    if strategy_A_component_swap:
        cursor_rand.execute("SELECT ship FROM ships")
        ship_ids = [row[0] for row in cursor_rand.fetchall()]

        for ship_id in ship_ids:
            component_to_change = random.choice(['weapon', 'hull', 'engine'])
            
            current_component_id_query = f"SELECT {component_to_change} FROM ships WHERE ship = ?"
            cursor_rand.execute(current_component_id_query, (ship_id,))
            current_component_id = cursor_rand.fetchone()[0]

            if component_to_change == 'weapon':
                cursor_rand.execute("SELECT weapon FROM weapons")
                all_components = [row[0] for row in cursor_rand.fetchall()]
            elif component_to_change == 'hull':
                cursor_rand.execute("SELECT hull FROM hulls")
                all_components = [row[0] for row in cursor_rand.fetchall()]
            else:
                cursor_rand.execute("SELECT engine FROM engines")
                all_components = [row[0] for row in cursor_rand.fetchall()]
            
            available_components = [c for c in all_components if c != current_component_id]
            
            if available_components:
                new_component_id = random.choice(available_components)
                update_query = f"UPDATE ships SET {component_to_change} = ? WHERE ship = ?"
                cursor_rand.execute(update_query, (new_component_id, ship_id))
    else:
        cursor_rand.execute("SELECT weapon FROM weapons")
        weapon_ids = [row[0] for row in cursor_rand.fetchall()]

        num_weapons_to_change = random.randint(1, max(1, min(3, len(weapon_ids))))
        weapons_to_modify = random.sample(weapon_ids, num_weapons_to_change)
        for weapon_id in weapons_to_modify:
            param_to_change = random.choice(WEAPON_PARAMS)
            new_value = random.randint(1, 20)

            cursor_rand.execute(f'UPDATE weapons SET "{param_to_change}" = ? WHERE weapon = ?', (new_value, weapon_id))

        cursor_rand.execute("SELECT hull FROM hulls")
        hull_ids = [row[0] for row in cursor_rand.fetchall()]
        num_hulls_to_change = random.randint(1, max(1, min(2, len(hull_ids))))
        hulls_to_modify = random.sample(hull_ids, num_hulls_to_change)
        for hull_id in hulls_to_modify:
            param_to_change = random.choice(HULL_PARAMS)
            new_value = random.randint(1, 20)
            cursor_rand.execute(f'UPDATE hulls SET "{param_to_change}" = ? WHERE hull = ?', (new_value, hull_id))

        cursor_rand.execute("SELECT engine FROM engines")
        engine_ids = [row[0] for row in cursor_rand.fetchall()]
        num_engines_to_change = random.randint(1, max(1, min(2, len(engine_ids))))
        engines_to_modify = random.sample(engine_ids, num_engines_to_change)
        for engine_id in engines_to_modify:
            param_to_change = random.choice(ENGINE_PARAMS)
            new_value = random.randint(1, 20)
            cursor_rand.execute(f'UPDATE engines SET "{param_to_change}" = ? WHERE engine = ?', (new_value, engine_id))

    conn_rand.commit()

    yield cursor_orig, cursor_rand
    print(f"\nRandomization complete. Changes applied to {RANDOMIZED_DB_NAME}.")

    conn_orig.close()
    conn_rand.close()
    if os.path.exists(RANDOMIZED_DB_NAME):
        os.remove(RANDOMIZED_DB_NAME)
    print(f"\nCleaned up {RANDOMIZED_DB_NAME}.")

def pytest_generate_tests(metafunc):
    if "ship_id" in metafunc.fixturenames and "component_type" in metafunc.fixturenames:
        conn = sqlite3.connect(ORIGINAL_DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT ship FROM ships")
        ship_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        component_types = ['weapon', 'hull', 'engine']
        
        test_params = []
        for ship_id in ship_ids:
            for comp_type in component_types:
                test_params.append((ship_id, comp_type))
        
        metafunc.parametrize("ship_id,component_type", test_params)