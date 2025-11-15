# routes/shop.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from models import Product, CartItem, Order, OrderItem
from database import db
from flask_login import current_user, login_required
from forms import AddToCartForm, CheckoutForm
from chatbot_integration.chatbot_service import ChatbotService

shop_bp = Blueprint('shop', __name__, template_folder='../templates')

# Инициализация чатбота — будет запущена при импорте chatbot_service в app.py
chatbot_service = ChatbotService()

def get_products_from_db():
    """Возвращает список товаров в виде строки для промпта"""
    try:
        products = Product.query.all()
        if not products:
            return "Pašlaik nav pieejamu preču veikalā."
        lines = []
        for p in products:
            lines.append(f"- {p.name}: {p.price:.2f} EUR, noliktavā {p.stock} gab.")
        return "Pieejamās preces:\n" + "\n".join(lines)
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return "Nevarēju ielādēt preču sarakstu."

# === МАРШРУТЫ МАГАЗИНА ===
@shop_bp.route('/shop')
def product_list():
    products = Product.query.all()
    return render_template('shop/product_list.html', title='Veikals', products=products)

@shop_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddToCartForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Lai pievienotu grozam, jāpiesakās.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        quantity = form.quantity.data
        if quantity <= 0:
            flash('Daudzumam jābūt vismaz 1.', 'danger')
            return redirect(url_for('shop.product_detail', product_id=product.id))
        if product.stock < quantity:
            flash(f'Nepietiek noliktavā. Pieejami tikai {product.stock} gab.', 'danger')
            return redirect(url_for('shop.product_detail', product_id=product.id))
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(user_id=current_user.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)
        db.session.commit()
        flash(f'{quantity} x {product.name} pievienots grozam!', 'success')
        return redirect(url_for('shop.cart'))
    return render_template('shop/product_detail.html', title=product.name, product=product, form=form)

@shop_bp.route('/cart')
@login_required
def cart():
    cart_items = current_user.cart_items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', title='Tavs grozs', cart_items=cart_items, total_price=total_price)

@shop_bp.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        flash('Nav atļauts dzēst šo preci.', 'danger')
        return redirect(url_for('shop.cart'))
    db.session.delete(cart_item)
    db.session.commit()
    flash('Prece izņemta no groza.', 'success')
    return redirect(url_for('shop.cart'))

@shop_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = current_user.cart_items.all()
    if not cart_items:
        flash('Tavs grozs ir tukšs!', 'warning')
        return redirect(url_for('shop.product_list'))
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    form = CheckoutForm()
    if form.validate_on_submit():
        order = Order(user_id=current_user.id, total_amount=total_amount, status='Apstrādājas')
        db.session.add(order)
        db.session.flush()
        for item in cart_items:
            order_item = OrderItem(order_id=order.id, product_id=item.product_id,
                                 quantity=item.quantity, price=item.product.price)
            product = Product.query.get(item.product_id)
            if product.stock < item.quantity:
                db.session.rollback()
                flash(f'Nepietiek {product.name} noliktavā.', 'danger')
                return redirect(url_for('shop.cart'))
            product.stock -= item.quantity
            db.session.add(order_item)
            db.session.delete(item)
        db.session.commit()
        flash('Pasūtījums veiksmīgi noformēts!', 'success')
        return redirect(url_for('shop.purchase_history'))
    return render_template('checkout.html', title='Noformēšana', cart_items=cart_items,
                           total_amount=total_amount, form=form)

@shop_bp.route('/purchase_history')
@login_required
def purchase_history():
    orders = current_user.orders.order_by(Order.order_date.desc()).all()
    return render_template('purchase_history.html', title='Pirkumu vēsture', orders=orders)

# === ЧАТБОТ ENDPOINT ===
@shop_bp.route('/chatbot', methods=['POST'])
def chatbot():
    """Обрабатывает запросы к чатботу"""
    try:
        data = request.get_json(silent=True) or {}
        message = data.get('message', '').strip()
        history = data.get('history', [])
        if not message:
            return jsonify({'response': 'Lūdzu, ievadiet ziņojumu.'}), 400
        response = chatbot_service.get_chatbot_response(message, history)
        return jsonify(response)
    except Exception as e:
        print(f"[CHATBOT ERROR] {e}")
        return jsonify({'response': 'Servera kļūda.'}), 500