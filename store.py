from bottle import route, run, template, static_file, get, post, delete, request, response, abort, redirect
from sys import argv
import json
import db_utils


@get("/admin")
def admin_portal():
    return template("pages/admin.html")


@get("/")
def index():
    return template("index.html")


# Main pages

# Creating a Category
# URL: /category
# Method: POST
# Parameters:
# name: The name of the category
# Result (JSON):
# STATUS:
# “SUCCESS” – The category was created successfully
# “ERROR” – The category was not created due to an error
# MSG (in case of an error):
# Category already exists
# Name parameter is missing
# Internal error
# CAT_ID
# The id of the new category (read about cursor.lastrowid)
# CODE
# 201 - category created successfully
# 200 - category already exists
# 400 - bad request
# 500 - internal error
@post('/category')
def create_a_category():
    try:
        try:
            category = request.forms.get('name')
            if len(category) == 0:
                print('Name parameter is empty')
                raise ValueError
            elif not category.isalnum():
                print('Name parameter is not alphanumeric')
                result = {
                    'STATUS': 'ERROR',
                    'MSG': 'Internal error',
                    'CODE': 500
                }
                return result
            else:
                # category is valid, process
                if db_utils.check_if_value_exists_in_table('categories', 'name', category):
                    print('category already exists')
                    result = {
                        'STATUS': 'ERROR',
                        'MSG': 'category already exists',
                        'CODE': 200
                    }
                    return result
                else:
                    # create category
                    db_utils.insert_into_table('categories', name=category)
                    result = {
                        'STATUS': 'SUCCESS',
                        'MSG': 'The category was created successfully',
                        'CODE': 200
                    }
                    return result
        except:
            print('try except - get name parameter')
            raise ValueError
    except ValueError:
        print('oh shoot - raising value error')
        result = {
            'STATUS': 'ERROR',
            'MSG': 'Name parameter is missing',
            'CODE': 400
        }
        return result


# Deleting a Category
# URL: /category/<id>
# Method: DELETE
# Parameters:
# id: The category id – (read about Bottle path parameters)
# Result (JSON):
# STATUS:
# “SUCCESS” – The category was deleted successfully
# “ERROR” – The category was not deleted due to an error
# MSG (in case of an error):
# Category not found
# Internal error
# CODE
# 201 - category deleted successfully
# 404 - category not found
# 500 - internal error
@delete('/category/<id>')
def delete_a_category(id):
    print('in delete_a_category, category id: {}'.format(id))
    # check if category exists
    if db_utils.check_if_value_exists_in_table('categories', 'id', id):
        print('category {} exists'.format(id))
        try:
            # delete from table
            db_utils.delete_value_from_table('products', 'category', id)
            result = {
                "STATUS": "SUCCESS",
                "PRODUCTS": 'category deleted successfully',
                "CODE": 201
            }
            print('category deleted successfully')
            return result
        except:
            result = {
                "STATUS": "ERROR",
                "MSG": "Internal error",
                "CODE": 500
            }
            print('category delete error')
            return result
    else:
        # category does not exist
        result = {
            "STATUS": "ERROR",
            "MSG": "category not found",
            "CODE": 404
        }
        print('category not found')
        return result


#################################################
# List Categories
# URL: /categories
# Method: GET
# Result (JSON):
# STATUS:
# “SUCCESS” – Categories fetched
# “ERROR” – internal error
# MSG (in case of an error):
# Internal error
# CATEGORIES
# [{id:<cat_id>,name:<cat_name>},{id:<cat_id>,name:<cat_name>},...]
# CODE
# 200 - Success
# 500 - internal error
@get('/categories')
def list_categories():
    print('in list_categories')
    try:
        available_categories = db_utils.select_from_table('categories')
        result_categories = [{'id': item[0], 'name': item[1]} for item in available_categories]
        # print('categories: {}'.format(result_categories))
        result = {
            'STATUS': 'SUCCESS',
            'CATEGORIES': result_categories,
            'CODE': 200
        }
        return result
    except:
        result = {
            'STATUS': 'ERROR',
            'MSG': 'internal error',
            'CODE': 500
        }
        return result


# Add/Edit a Product
# URL: /product
# Method: POST
# Parameters:
# Id (optional): if exists the handler will update an existing product, if not a new product will be created
# title: the product’s title
# desc: the product’s description
# price: the product’s price
# img_url: the product’s image url
# category: the product’s category id (must be a valid category)
# favorite: 0/1 if favorite
# Result (JSON):
# STATUS:
# “SUCCESS” – The product was added/updated successfully
# “ERROR” – The product was not created/updated due to an error
# MSG (in case of an error):
# Category not found
# missing parameters
# Internal error
# PRODUCT_ID
# The created/edited product
# CODE
# 201 - product created/updated successfully
# 404 - category not found
# 400 - bad request
# 500 - internal error
@post('/product')
def add_or_edit_a_product():
    print('in add_or_edit_a_product')
    try:
        try:
            category_id = request.forms.get('category') or None
            title = request.forms.get('title')
            desc = request.forms.get('desc')
            favorite = request.forms.get('favorite')
            price = request.forms.get('price')
            img_url = request.forms.get('img_url')
            id = request.forms.get('id') or None

            print(
                'got product values: category: {}, title: {}, desc: {}, favorite: {}, price: {}, img_url: {}, id: {}'.format(
                    category_id, title, desc, favorite, price, img_url, id))
            if not category_id.isalnum():
                print('Category not found')
                result = {
                    'STATUS': 'ERROR',
                    'MSG': 'Category not found',
                    'CODE': 404
                }
                return result
            else:
                if db_utils.check_if_value_exists_in_table('categories', 'id', category_id):
                    print('category id ({}) exists'.format(category_id))
                    product_id = db_utils.insert_into_table_or_update('products', id=id, category=category_id,
                                                                      title=title, description=desc, price=float(price),
                                                                      img_url=img_url)

                    result = {
                        'STATUS': 'SUCCESS',
                        'PRODUCT_ID': product_id,
                        'CODE': 201
                    }
                    return result
                else:
                    print('category does not exist, return an error')
                    result = {
                        'STATUS': 'ERROR',
                        'MSG': 'category not found',
                        'CODE': 404
                    }
                    return result
        except:
            print('try except - get name parameter')
            raise ValueError
    except ValueError:
        print('oh shoot - raising value error')
        result = {
            'STATUS': 'ERROR',
            'MSG': 'category not found',
            'CODE': 404
        }
        return result


# Getting a Product
# URL: /product/<id>
# Method: GET
# Parameters:
# id: The product id
# Result (JSON):
# STATUS:
# “SUCCESS” – The product was fetched successfully
# “ERROR” – The product was not fetched due to an error
# MSG (in case of an error):
# Product not found
# Internal error
# PRODUCT
# {"category": 16, "description": "this is great", "price": 1000.0, "title": "honda2", "favorite": 0, "img_url":
# "https://images.honda.ca/nav.png", "id": 1}
# CODE
# 200 - product fetched successfully
# 404 - product not found
# 500 - internal error
@get('/product/<id>')
def get_a_product(id):
    print('in get_a_product, product id: {}'.format(id))
    return 'in get_a_product, product id: {}'.format(id)


# Deleting a Product
# URL: /product/<id>
# Method: DELETE
# Parameters:
# id: The product id
# Result (JSON):
# STATUS:
# “SUCCESS” – The product was deleted successfully
# “ERROR” – The product was not deleted due to an error
# MSG (in case of an error):
# Product not found
# Internal error
# CODE
# 201 - product deleted successfully
# 404 - product not found
# 500 - internal error
@delete('/product/<id>')
def delete_a_product(id):
    print('in delete_a_product, product id: {}'.format(id))
    return 'in delete_a_product, product id: {}'.format(id)


# List All Products
# URL: /products
# Method: GET
# Result (JSON):
# STATUS:
# “SUCCESS” – Products fetched
# “ERROR” – internal error
# MSG (in case of an error):
# Internal error
# PRODUCTS
# [{"category": 16, "description": "this is great", "price": 1000.0, "title": "honda2", "favorite": 0, "img_url":
# "https://images.honda.ca/v.png", "id": 1},…]
# CODE
# 200 - Success
# 500 - internal error
@get('/products')
def list_all_products():
    print('in list_all_products')
    try:
        products = db_utils.select_from_table('products')
        # print('products: {}, type products: {}'.format(products, type(products)))
        conv = []
        for product in products:
            conv.append(
                {"id": product[0], "category": product[1], "title": product[2], "description": product[3],
                 "price": product[4], "favorite": product[5],"img_url": product[6]})
        result = {
            "STATUS": "SUCCESS",
            "PRODUCTS": conv,
            "CODE": 200
        }
        return result
    except:
        print('error listing products')
        result = {
            "STATUS": "ERROR",
            "MSG": "Internal error",
            "CODE": 500
        }
        return result


# List Products by Category
# URL: /category/<id>/products
# Method: GET
# Parameters:
# Id: The requested category id
# Result (JSON):
# STATUS:
# “SUCCESS” – Products fetched
# “ERROR” – internal error
# MSG (in case of an error):
# Internal error
# PRODUCTS
# [{"category": 16, "description": "this is great", "price": 1000.0, "title": "honda2", "favorite": 0, "img_url":
# "https://images.honda.ca/v.png", "id": 1},…]
# CODE
# 200 – Success
# 404 - category not found
# 500 - internal error
@get('/category/<id>/products')
def list_product_by_category(id):
    print('in list_product_by_category, category id: {}'.format(id))
    # check if category exists
    if db_utils.check_if_value_exists_in_table('categories', 'id', id):
        try:
            results = db_utils.select_from_table('products', 'category', id)
            conv = []
            print('in list_product_by_category, results: {}, type: {}, length: {}'.format(results, type(results),
                                                                                          len(results)))
            for res in results:
                id = res[0]
                category_id = res[1]
                title = res[2]
                desc = res[3]
                price = res[4]
                favorite = res[5]
                img_url = res[6]
                conv.append(
                    {"id": id, "category": category_id, "title": title, "description": desc, "favorite": favorite,
                     "price": price, "img_url": img_url})

            print('conv')
            print(conv)
            result = {
                "STATUS": "SUCCESS",
                "PRODUCTS": conv,
                "CODE": 200
            }
            return result
        except:
            result = {
                "STATUS": "ERROR",
                "MSG": "Internal error",
                "CODE": 500
            }
            return result
    else:
        # category does not exist
        result = {
            "STATUS": "ERROR",
            "MSG": "category not found",
            "CODE": 404
        }
        return result


# Static routes

@get('/js/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='js')


@get('/css/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='css')


@get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='images')


# Runner

if __name__ == '__main__':
    # DB Setup
    # db_utils.setup_database()
    run(host='127.0.0.1', port=5555, debug=True, reloader=True)
else:
    run(host='0.0.0.0', port=argv[1])
