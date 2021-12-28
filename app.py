import datetime
import random

from flask import Flask, render_template, request, redirect, flash, g
from flask_wtf import CSRFProtect

from db import insert_into_many
from db_services import get_row, insert_many_update_dups, insert_table, delete_row, get_rows, get_data, \
    get_data_where_not_in

app = Flask(__name__, static_url_path='',
            static_folder='static',
            template_folder='templates')
csrf = CSRFProtect(app)

app.config['SECRET_KEY'] = "asdasdsadsd6262{QWEQ{WEW{E1d32as1d5sa1d2a4d"

DEADLINE = 13


@app.before_request
def before_request():
    not_auth_endpoints = ("start", "save_user")
    ip = request.remote_addr
    g.user = get_row("users", {"ip": ip})

    if request.endpoint not in not_auth_endpoints:
        if not g.user:
            flash("Register here, before accessing the page")
            return redirect("/")

        participant = get_row("participants", {"user_id": g.user["id"], "created": datetime.date.today()})

        if not participant:
            flash("Register here, before accessing the page")
            return redirect("/")


@app.route("/")
def start():
    return render_template("start.html", user=g.user)


@app.route("/save-user/", methods=['POST'])
def save_user():
    ip = request.remote_addr
    g.user = get_row("users", {"ip": ip})
    try:

        if not datetime.datetime.now().time().hour < DEADLINE:
            return render_template("info.html", info="You are late")

        ip = request.remote_addr
        insert_many_update_dups("users", [{"name": request.form["name"], "surname": request.form["surname"], "ip": ip}])
        user = get_row("users", {"ip": ip})

        insert_table("participants", {"user_id": user["id"], "created": datetime.datetime.now()})
    except:
        pass
    return redirect("/add-product-links/")


@app.route("/add-product-links/", methods=['GET'])
def participants():
    participant = get_row("participants", {"user_id": g.user["id"], "created": datetime.date.today()})

    if not participant:
        flash("Register here, before accessing the page")
        return redirect("/")
    sql = "SELECT * FROM users_products WHERE user_id = %(user_id)s AND created = %(created)s"
    links = get_rows(sql, {"user_id": g.user["id"], "created": datetime.date.today()}) or []
    return render_template("add-products.html", links=links)


@app.route("/save-product-links/", methods=['POST'])
def save_links():
    delete_row("users_products", "user_id", g.user['id'])

    links = request.form.getlist('link')
    price = request.form.getlist('price')

    if not any(links) or not any(price):
        flash("Enter links or price")
        return redirect("/add-product-links/")

    users_links = []
    for index, item in enumerate(links):
        users_links.append(
            {"user_id": g.user["id"],
             "link": item,
             "price": price[index],
             "created": datetime.datetime.now()
             }
        )
    insert_into_many("users_products", users_links)
    return redirect("/add-product-links/")


@app.route("/get-random-host/", methods=['GET'])
def get_random_host():
    host = get_row("host", {"created": datetime.date.today()})

    if host:
        host = get_row("users", {"id": host["user_id"]})
        return render_template("info.html", info=f"Today's host is {host['name']} {host['surname']}")

    if not datetime.datetime.now().time().hour >= DEADLINE:
        return render_template("info.html", info=f"Time should be >= {DEADLINE}:00")

    already_hosts = [user["user_id"] for user in get_rows("SELECT user_id FROM host", None) or []]

    participants = get_data_where_not_in("participants", "user_id", already_hosts)

    if not participants:
        # in case all have already ordered
        participants = get_data("participants", {"created": datetime.date.today()})

    if not participants:
        return render_template("info.html", info="We could not determine the host")

    random_num = random.randint(0, len(participants) - 1)

    host = get_row("users", {"id": participants[random_num]["user_id"]})
    if host:
        insert_table("host", {"user_id": host["id"], "created": datetime.datetime.now()})
    else:
        return render_template("info.html", info="Something went wrong, we couldn't find a host")

    return render_template("info.html", info=f"Today's host is {host['name']} {host['surname']}")


@app.route("/all-orders/", methods=['GET'])
def see_all_orders():
    today = datetime.date.today()

    ordered_users = f"""
        SELECT users.name, users.surname, users.id FROM users_products
        JOIN users ON users.id = users_products.user_id
        WHERE users_products.created = %(created)s
        GROUP BY users.id 
        ORDER BY users.name
    """

    links_sql = f"""
        SELECT * FROM users_products WHERE users_products.created = %(created)s
    """

    users = get_rows(ordered_users, {"created": today})
    links = get_rows(links_sql, {"created": today})

    data = []

    for user in users:
        user_data = {"user": user, "products": []}
        for link in links:
            if str(link["user_id"]) == str(user["id"]):
                user_data["products"].append(link)
        data.append(user_data)

    return render_template("all-products.html", data=data)
