import sqlite3
import random
import os

DATABASE_NAME = 'ship_database.db'

def create_tables(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weapons (
        weapon TEXT PRIMARY KEY,
        "reload speed" INTEGER,
        "rotational speed" INTEGER,
        diameter INTEGER,
        "power volley" INTEGER,
        count INTEGER
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hulls (
        hull TEXT PRIMARY KEY,
        armor INTEGER,
        type INTEGER,
        capacity INTEGER
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS engines (
        engine TEXT PRIMARY KEY,
        power INTEGER,
        type INTEGER
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ships (
        ship TEXT PRIMARY KEY,
        weapon TEXT,
        hull TEXT,
        engine TEXT,
        FOREIGN KEY (weapon) REFERENCES weapons(weapon),
        FOREIGN KEY (hull) REFERENCES hulls(hull),
        FOREIGN KEY (engine) REFERENCES engines(engine)
    )''')
    print("Tables created successfully.")

def populate_weapons(cursor, count=20):
    weapons_data = []
    for i in range(1, count + 1):
        weapons_data.append((
            f'Weapon-{i}',
            random.randint(1, 20), # reload speed
            random.randint(1, 20), # rotational speed
            random.randint(1, 20), # diameter
            random.randint(1, 20), # power volley
            random.randint(1, 20)  # count
        ))
    cursor.executemany('INSERT INTO weapons VALUES (?, ?, ?, ?, ?, ?)', weapons_data)
    print(f"Inserted {count} records into 'weapons' table.")
    return [w[0] for w in weapons_data]

def populate_hulls(cursor, count=5):
    hulls_data = []
    for i in range(1, count + 1):
        hulls_data.append((
            f'Hull-{i}',
            random.randint(1, 20), # armor
            random.randint(1, 20), # type
            random.randint(1, 20)  # capacity
        ))
    cursor.executemany('INSERT INTO hulls VALUES (?, ?, ?, ?)', hulls_data)
    print(f"Inserted {count} records into 'hulls' table.")
    return [h[0] for h in hulls_data]

def populate_engines(cursor, count=6):
    engines_data = []
    for i in range(1, count + 1):
        engines_data.append((
            f'Engine-{i}',
            random.randint(1, 20), # power
            random.randint(1, 20)  # type
        ))
    cursor.executemany('INSERT INTO engines VALUES (?, ?, ?)', engines_data)
    print(f"Inserted {count} records into 'engines' table.")
    return [e[0] for e in engines_data]

def populate_ships(cursor, count=200, weapon_ids=None, hull_ids=None, engine_ids=None):
    if not all([weapon_ids, hull_ids, engine_ids]):
        print("Error: Component IDs must be provided to populate ships.")
        return

    ships_data = []
    for i in range(1, count + 1):
        ships_data.append((
            f'Ship-{i}',
            random.choice(weapon_ids),
            random.choice(hull_ids),
            random.choice(engine_ids)
        ))
    cursor.executemany('INSERT INTO ships VALUES (?, ?, ?, ?)', ships_data)
    print(f"Inserted {count} records into 'ships' table.")

def main():
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
        print(f"Removed existing database: {DATABASE_NAME}")

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    create_tables(cursor)

    weapon_ids = populate_weapons(cursor)
    hull_ids = populate_hulls(cursor)
    engine_ids = populate_engines(cursor)

    populate_ships(cursor, weapon_ids=weapon_ids, hull_ids=hull_ids, engine_ids=engine_ids)

    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_NAME}' created and populated successfully.")

if __name__ == '__main__':
    main()