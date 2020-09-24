from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import psycopg2


def create_connection():
    conn = psycopg2.connect("dbname='yo_yo_pizza_chat_bot' user='' host='127.0.0.1' password=''")
    conn.autocommit = True
    return conn


@method_decorator(csrf_exempt)
def ordersubmition(request):
    conn = create_connection()
    cur = conn.cursor()
    order = request.POST.get('order')
    for details in order.split("!"):
        if "BASE" in details.upper():
            base = details[5:]
        if "TOPPINGS" in details.upper():
            topping = details[9:]
        if "SIZE" in details.upper():
            size = details[5:]
        if "EXTRACHEESE" in details.upper():
            cheese = bool(details[12:])
    cur.execute("SELECT id FROM user_details ORDER BY id DESC LIMIT 1")
    u_id = cur.fetchone()
    cur.execute("INSERT INTO order_details(base, topping, size, extra_cheese, uid) VALUES (%s, %s, %s, %s, %s) RETURNING id", (base, topping, size, cheese, u_id))
    o_id = cur.fetchone()
    cur.execute("INSERT INTO tracking_details(order_id, pizza_status) VALUES (%s, %s) RETURNING id",
                (o_id, 'Processing'))
    message = {
        "base": base,
        "toppings": topping,
        "size": size,
        "extracheese": cheese,
        "order_id": o_id
    }
    return JsonResponse(message)

@method_decorator(csrf_exempt)
def saveuserdetails(request):
    conn = create_connection()
    cur = conn.cursor()
    order = request.POST.get('userdetails')
    for details in order.split("!"):
        if "FIRSTNAME" in details.upper():
            f_name = details[10:]
        if "LASTNAME" in details.upper():
            l_name = details[9:]
        if "EMAILID" in details.upper():
            email = details[8:]
        if "MOBILENUMBER" in details.upper():
            number = details[13:]
        if "ADDRESS" in details.upper():
            address = details[8:]

    cur.execute("INSERT INTO user_details(first_name, last_name, phone_number, email_id, address) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id", (f_name, l_name, email, number, address))

    message = {
        "address": address,
        "f_name": f_name,
        "l_name": l_name,
        "email": email,
        "number": number
    }
    return JsonResponse(message)


@method_decorator(csrf_exempt)
def trackorder(request):
    conn = create_connection()
    cur = conn.cursor()
    tracking = request.POST.get('tracking')
    for details in tracking.split("!"):
        if "ORDERID" in details.upper():
            try:
                o_id = int(details[8:])
            except Exception as e:
                o_id = 0
                message = {
                    "status": "wrong id"
                }
                return JsonResponse(message)

    cur.execute("SELECT pizza_status FROM tracking_details where order_id = %s", [o_id])
    status = cur.fetchone()

    if "Processing" in status:
        new_status = "Order confirmed"
    elif "Order confirmed" in status:
        new_status = "Cooking"
    elif "Cooking" in status:
        new_status = "Ready for pickup"
    else:
        new_status = "Out for delivery"

    cur.execute("UPDATE tracking_details SET pizza_status = %s WHERE order_id = %s", (new_status, o_id))

    message = {"status": status,
               "order_id": o_id}
    return JsonResponse(message)


def chatbot(request, template="chatbot.html"):
    return render(request, template)
