import pymysql

# DB Utils
db_name = 'store_itc'
connection = None


def create_cursor():
    host = 'localhost'
    user = 'root'
    password = 'zaq1zaq'
    autocommit = True
    global connection
    connection = pymysql.connect(host=host, user=user, password=password, autocommit=autocommit)
    return connection.cursor()


## Selects
def select_from_table(table, key=None, value=None):
    curs = create_cursor()
    with connection:
        try:
            if key is None:
                statement = 'SELECT * FROM {}.{};'.format(db_name, table)
            else:
                statement = 'SELECT * FROM {}.{} where {}=\'{}\';'.format(db_name, table, key, value)
            print(statement)
            curs.execute(statement)
            result = curs.fetchall()
        except pymysql.err.ProgrammingError:
            print('error selecting from select_from_table')
        return result


def check_if_value_exists_in_table(table, field, value):
    curs = create_cursor()
    with connection:
        try:
            statement = 'SELECT * FROM {}.{} WHERE {}=\'{}\';'.format(db_name, table, field, value)
            print(statement)
            curs.execute(statement)
            result = curs.fetchone()
            print('select result: {}'.format(result))
            if result is None:
                return False
            else:
                return True
        except pymysql.err.ProgrammingError:
            print('DATABASE store_itc exists, dropping and creating')
        return statement


## Inserts
def insert_into_table(table, **kwargs):
    curs = create_cursor()
    with connection:
        try:
            print('in insert_into_table, table: {}, kwargs: {}'.format(table, kwargs))
            statement = 'INSERT INTO store_itc.{} ({}) VALUES ({});'.format(table, ",".join([k for k in kwargs.keys()]),
                                                                            ",".join(
                                                                                ["'" + v + "'" for v in
                                                                                 kwargs.values()]))
            print('statement: {}'.format(statement))
            curs.execute(statement)
            print('after curs.execute(statement)')
            last_row_id = curs.lastrowid
            print('last_row_id: ' + str(last_row_id))
            return last_row_id
        except pymysql.err.ProgrammingError:
            print('Oh shoot, something\'s wrong... ')


## Update
def insert_into_table_or_update(table, **kwargs):
    print('in insert_into_table_or_update, table: {}, kwargs: {}'.format(table, kwargs))
    curs = create_cursor()
    with connection:
        try:
            print('id:{}, type of id: {}'.format(kwargs['id'], type(kwargs['id'])))
            if kwargs['id'] is None:
                print("kwargs['id'] is None")
                # insert
                my_keys = ",".join([str(k) for k in kwargs.keys() if k != 'id'])
                print('my_keys: ' + my_keys)
                my_values = ",".join(["'" + str(v) + "'" for v in kwargs.values() if v is not None])
                print('my_values: ' + my_values)
                statement = 'INSERT INTO store_itc.{table} ({keys}) VALUES ({values});'.format(
                    table=table, keys=my_keys,
                    values=my_values)
                print('statement: {}'.format(statement))
            else:
                print('else')
                kv = []
                ##### Errors - need to fix
                for k, v in kwargs.items():
                    print(k)
                    print(v)
                    if k == 'id' or k == 'category' or k == 'price':
                        item = k + '=' + v
                        print(item)
                        kv.append(item)
                    else:
                        item = k + '="' + v + '"'
                        print(item)
                        kv.append(item)
                print('kv')
                print(kv)
                # update
                statement = 'UPDATE store_itc.{table} SET {kv} WHERE \'id\'={id};'.format(table=table, id=kwargs['id'],
                                                                                          kv=kv)
                print('statement: {}'.format(statement))
            print('after statement setting')
            with connection:
                curs.execute(statement)
                print('after curs.execute(statement)')
                last_row_id = curs.lastrowid
                print('last_row_id: ' + str(last_row_id))
                return last_row_id
        except pymysql.err.ProgrammingError:
            print('Oh shoot, something\'s wrong... ')


## Creates

def create_database():
    curs = create_cursor()
    with connection:
        try:
            curs.execute('CREATE DATABASE store_itc;')
            print('Creating DATABASE store_itc')
        except pymysql.err.ProgrammingError:
            curs.execute('DROP DATABASE store_itc;')
            curs.execute('CREATE DATABASE store_itc;')
            print('DATABASE store_itc exists, dropping and creating')
        finally:
            curs.execute('USE store_itc;')


def create_tables():
    curs = create_cursor()
    with connection:
        try:
            curs.execute('USE store_itc;')
            for statement in table_create_statements:
                curs.execute(statement)
        except pymysql.err.ProgrammingError:
            print('error creating table using statement: {}'.format(statement))


table_create_statements = [
    """CREATE TABLE `store_itc`.`categories` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `name` VARCHAR(200) NOT NULL,
      PRIMARY KEY (`id`));""",

    """CREATE TABLE `products` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `category` int(11) NOT NULL,
      `title` varchar(200) NOT NULL,
      `description` varchar(200) DEFAULT NULL,
      `price` float DEFAULT NULL,
      `favorite` tinyint(4) DEFAULT NULL,
      `img_url` varchar(95) DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `id_UNIQUE` (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
]

other_products = ["""CREATE TABLE `store_itc`.`products` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `category` INT NOT NULL,
      `title` VARCHAR(200) NOT NULL,
      `description` VARCHAR(200) NULL,
      `price` FLOAT NULL,
      `favorite` TINYINT NULL,
      `img_url` VARCHAR(95) NULL,
      FOREIGN KEY `category`(`category`)
      REFERENCES `categories`(`id`)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
      PRIMARY KEY (`id`),
      UNIQUE INDEX `category_UNIQUE` (`category` ASC) VISIBLE,
      UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);
    """]

categories_inserts = ["INSERT INTO `store_itc`.`categories` (`id`, `name`) VALUES ('1', 'Cameras');",
                      "INSERT INTO `store_itc`.`categories` (`id`, `name`) VALUES ('2', 'Tablets');",
                      "INSERT INTO `store_itc`.`categories` (`id`, `name`) VALUES ('3', 'Books');"]

cameras_inserts = [
    "INSERT INTO `store_itc`.`products` (`id`, `category`, `title`, `description`, `price`, `img_url`) VALUES ('1', '1', 'Canon EOS Rebel T7', 'Canon EOS Rebel T7 DSLR Camera with 18-55mm Lens Kit', '519.99', 'https://multimedia.bbycastatic.ca/multimedia/products/500x500/123/12383/12383478.jpg');",
    "INSERT INTO `store_itc`.`products` (`id`, `category`, `title`, `description`, `price`, `img_url`) VALUES ('2', '1', 'Fujifilm Instax Mini 9', 'Fujifilm Instax Mini 9 Instant Camera - Ice Blue','49.99','https://images-na.ssl-images-amazon.com/images/I/41WfBNBSq1L._SY300_QL70_.jpg');",
    "INSERT INTO `store_itc`.`products` (`id`, `category`, `title`, `description`, `price`, `img_url`) VALUES ('3', '1', 'GoPro HERO 7 Silver', 'GoPro HERO 7 Silver', '239.90','https://images-na.ssl-images-amazon.com/images/I/31aJyUiHKtL._SL500_AC_SS350_.jpg');",
    "INSERT INTO `store_itc`.`products` (`id`,`category`,`title`,`description`,`price`,`favorite`,`img_url`) VALUES (4,2,'Fire HD 8 Tablet','Fire HD 8 Tablet (8in HD Display, 16 GB) - Black',79.99,NULL,'https://images-na.ssl-images-amazon.com/images/I/51hGfH1RMKL._SY300_.jpg');",
    "INSERT INTO `store_itc`.`products` (`id`,`category`,`title`,`description`,`price`,`favorite`,`img_url`) VALUES (5,3,'Directorate S','Directorate S: The C.I.A. and America\'s Secret Wars in Afghanistan and Pakistan Paperback – February 5, 2019',11.24,NULL,'https://images-na.ssl-images-amazon.com/images/I/41BcqkoALqL._SX324_BO1,204,203,200_.jpg');"]


## Deletes


def delete_value_from_table(table, key, value):
    curs = create_cursor()
    with connection:
        try:
            statement = 'DELETE FROM {}.{} WHERE {}=\'{}\''.format(db_name, table, key, value)
            curs.execute(statement)
        except pymysql.err.ProgrammingError:
            print('error deleting from table {}.{}, key {}, value {}'.format(db_name, table, key, value))


def delete_old_tables(tables):
    curs = create_cursor()
    with connection:
        try:
            curs.execute('USE store_itc;')
            for table in tables:
                curs.execute('DROP TABLE IF EXISTS {}'.format(table))
        except pymysql.err.ProgrammingError:
            print('error removing old tables')


def insert_data_into_tables():
    curs = create_cursor()
    with connection:
        try:
            # Categories
            for category_statement in categories_inserts:
                curs.execute(category_statement)
            # Products
            for product_statement in cameras_inserts:
                curs.execute(product_statement)
        except:
            print("error setting up tables")


## Setup

def setup_database():
    create_database()
    delete_old_tables(['`store_itc`.`categories`', '`store_itc`.`products`'])
    create_tables()
    insert_data_into_tables()
