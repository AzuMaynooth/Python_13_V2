from flask import Flask, render_template, request, redirect, url_for, flash
import datetime
import json
import os


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to flash sms

#  Global variable to storage balance (real scenario must be a DB)
balance = 1000

# Global variables for operations history
operation_history = []
inventory = []


# Ruta del archivo donde se guarda el historial
history_file = 'history.json'


# Función para leer el historial desde el archivo
def read_history_from_file():
    if os.path.exists(history_file):
        with open(history_file, 'r') as file:
            return json.load(file)
    else:
        return []


# Función para escribir el historial en el archivo
def write_history_to_file(history_data):
    with open(history_file, 'w') as file:
        json.dump(history_data, file, indent=4)


# Inicializa el historial de operaciones leyendo desde el archivo
operation_history = read_history_from_file()


@app.route('/')
def index():
    global balance, inventory, operation_history
    return render_template('index.html', balance=balance, inventory=inventory, operation_history=operation_history)


@app.route('/purchase-form', methods=["GET", "POST"])
def purchase_form():
    global inventory, balance, operation_history

    if request.method == "POST":
        # Record data from form
        product_name = request.form['product_name']
        unit_price = request.form['unit_price']
        number_of_pieces = request.form['number_of_pieces']

        # Field validation
        if not product_name or not unit_price or not number_of_pieces:
            flash('Please complete all fields.', 'error')
            return redirect(url_for('purchase_form'))

        # Try to convert prices and quantity to numerical values
        try:
            unit_price = round(float(unit_price), 2)
            number_of_pieces = int(number_of_pieces)

            # Validate positive values
            if unit_price <= 0 or number_of_pieces <= 0:
                flash('The unit price and quantity must be greater than zero.', 'error')
                return redirect(url_for('purchase_form'))
        except ValueError:
            flash('Please enter correct values for price and quantity.', 'error')
            return redirect(url_for('purchase_form'))

        # Process the purchase
        total_cost = round(unit_price * number_of_pieces, 2)
        if balance >= total_cost:
            balance -= total_cost  # Restar el costo total de la cuenta
            flash(f'Successful purchase! Product: {product_name}, Total: {total_cost:.2f}€', 'success')

            # Update inventory
            product_found = False
            for item in inventory:
                if item['product_name'] == product_name:

                    # Calculate the new weighted average price
                    total_existing_value = item['unit_price'] * item['stock_quantity']
                    total_new_value = unit_price * number_of_pieces
                    new_stock_quantity = item['stock_quantity'] + number_of_pieces
                    new_unit_price = round((total_existing_value + total_new_value) / new_stock_quantity, 2)

                    # Update the product in inventory
                    item['unit_price'] = new_unit_price
                    item['stock_quantity'] = new_stock_quantity
                    product_found = True
                    break

            if not product_found:
                # Add the new product to inventory
                inventory.append({
                    'product_name': product_name,
                    'unit_price': unit_price,
                    'stock_quantity': number_of_pieces
                })

            # Registro de la operación en el historial
            operation_history.append({
                'type': 'Purchase',
                'date': datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                'amount': total_cost,
                'new_balance': balance,
                'product': product_name,
                'cost': total_cost
            })

            # Guardar el historial actualizado en el archivo
            write_history_to_file(operation_history)

        else:
            flash('You do not have enough balance to make the purchase.', 'error')

    return render_template('purchase-form.html', balance=round(balance, 2), inventory=inventory)


@app.route('/sale-form', methods=["GET", "POST"])
def sale_form():
    global balance, inventory
    unit_price = None

    # Process the sale
    if request.method == "POST":
        product_name = request.form['product_name']
        number_of_pieces = request.form['number_of_pieces']

        if not product_name or not number_of_pieces:
            flash('Please complete all fields.', 'error')
            return redirect(url_for('sale_form'))

        found_product = None

        # Display the find items in inventary and add automatically the price, only manual add the quantity
        for item in inventory:
            if item['product_name'] == product_name:
                found_product = item
                unit_price = found_product['unit_price']
                flash(f'Product "{product_name}" founded in the inventary. Price: {unit_price}€', 'success')
                break

        if not found_product:
            flash(f'The product "{product_name}" is not available.', 'error')
            return redirect(url_for('sale_form'))

        if found_product['stock_quantity'] >= int(number_of_pieces):
            found_product['stock_quantity'] -= int(number_of_pieces)
            sale_amount = unit_price * int(number_of_pieces)
            balance += sale_amount
            flash(f'Successful purchase! Product: {product_name}, Total: {sale_amount}€', 'success')

            operation_history.append({
                'type': 'Sale',
                'date': datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                'amount': sale_amount,
                'new_balance': balance,
                'product': product_name,
                'cost': sale_amount
            })

            # Guardar el historial actualizado en el archivo
            write_history_to_file(operation_history)

        else:
            flash(f'There is not enough stock of "{product_name}" to make the sale.', 'error')

        return redirect(url_for('sale_form'))

    return render_template('sale-form.html', balance=balance, inventory=inventory, unit_price=unit_price)


@app.route('/balance-change-form', methods=["GET", "POST"])
def balance_change_form():
    global balance

    # Manages add or subtrac operation to the global balance
    if request.method == "POST":
        operation_type = request.form['operation_type']
        change_value = request.form['change_value']

        if not operation_type or not change_value:
            flash('Please complete all fields.', 'error')
            return redirect(url_for('balance_change_form'))

        try:
            change_value = float(change_value)
        except ValueError:
            flash('Please enter a valid numerical value for the change.', 'error')
            return redirect(url_for('balance_change_form'))

        if operation_type == 'add':
            balance += change_value
            flash(f'The balance has been increased by  {change_value}€! New balance: {balance}€', 'success')

            operation_history.append({
                'type': 'Add',
                'date': datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                'amount': change_value,
                'new_balance': balance,
                'product': '',
                'cost': 0,
            })

        elif operation_type == 'subtract':

            if balance >= change_value:
                balance -= change_value
                flash(f' The balance has been reduced by {change_value}€! New balance: {balance}€', 'success')

                operation_history.append({
                    'type': 'Subtract',
                    'date': datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                    'amount': -change_value,
                    'new_balance': balance,
                    'product': '',
                    'cost': 0,
                })
            else:
                flash('Insufficient balance to carry out this operation.', 'error')

        # Guardar el historial actualizado en el archivo
        write_history_to_file(operation_history)

        return redirect(url_for('balance_change_form'))

    return render_template('balance-change-form.html', balance=balance)


import datetime
from flask import render_template, request, flash, redirect, url_for


@app.route('/history/', methods=['GET', 'POST'])
def history():
    global operation_history

    # Inicializamos las variables
    start_date = request.args.get('start_date')  # Obtener los datos del formulario de tipo GET
    end_date = request.args.get('end_date')      # Usamos 'args' para obtener datos del GET
    show_table = False  # Inicialmente no mostrar la tabla

    # Si el formulario ha sido enviado (POST), procesamos el filtrado
    if request.method == 'POST':
        # Obtener las fechas desde el formulario
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Filtrar si se ha proporcionado al menos una fecha
        if start_date or end_date:
            try:
                # Convertir las fechas proporcionadas en formato 'dd-mm-yyyy' a objetos datetime.date
                if start_date:
                    start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
                if end_date:
                    end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

                # Filtrar las operaciones según las fechas
                filtered_history = [
                    op for op in operation_history
                    if (not start_date or datetime.datetime.strptime(op['date'].split()[0], '%d-%m-%Y').date() >= start_date) and
                       (not end_date or datetime.datetime.strptime(op['date'].split()[0], '%d-%m-%Y').date() <= end_date)
                ]

                if filtered_history:
                    show_table = True  # Mostramos la tabla si hay operaciones filtradas
                else:
                    flash('No hay operaciones para las fechas seleccionadas.', 'warning')
            except ValueError:
                flash('Formato de fecha no válido. Usa dd-mm-yyyy.', 'error')
                return redirect(url_for('history'))
        else:
            # Si no se proporcionan fechas, mostrar todas las operaciones
            filtered_history = operation_history
            show_table = True  # Siempre mostrar la tabla si no hay filtros

    else:
        # Si el método es GET (la primera carga de la página), no mostrar la tabla
        filtered_history = []
        show_table = False

    return render_template('history.html',
                           operation_history=filtered_history,
                           start_date=start_date,
                           end_date=end_date,
                           show_table=show_table)



if __name__ == '__main__':
    app.run(debug=True)
