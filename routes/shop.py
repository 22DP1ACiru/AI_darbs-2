from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from models import Product, CartItem, Order, OrderItem
from database import db
from flask_login import current_user, login_required
from forms import AddToCartForm, CheckoutForm

# Importējam čatbota servisu
from chatbot_integration.chatbot_service import ChatbotService

shop_bp = Blueprint('shop', __name__, template_folder='../templates')

# Inicializējam čatbota servisu (izmanto Hugging Face API)
chatbot = ChatbotService()

def get_products_from_db():
    """
    Saņem visus produktus no datubāzes un formatē uz vienkāršu tekstu LLM promptam.
    """
    try:
        products = Product.query.all()
        if not products:
            return "Veikalā šobrīd nav pieejamu preču."
        product_list_str = "Pieejamo preču saraksts:\n"
        for p in products:
            product_list_str += f"- Nosaukums: {p.name}, Cena: €{p.price:.2f}, Krājumi: {p.stock}\n"
        return product_list_str
    except Exception as e:
        print(f"Kļūda, iegūstot preces no DB: {e}")
        return "Nevarēju piekļūt produktu katalogam."

@shop_bp.route('/shop')
def product_list():
    # Rāda visas preces
    products = Product.query.all()
    return render_template('shop/product_list.html', title='Shop', products=products)

@shop_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    # Parāda konkrētās preces detaļas un pievienošanu grozam
    product = Product.query.get_or_404(product_id)
    form = AddToCartForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Jums jāielogojas, lai pievienotu grozam.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        quantity = form.quantity.data
        if quantity <= 0:
            flash('Daudzumam jābūt vismaz 1.', 'danger')
            return redirect(url_for('shop.product_detail', product_id=product.id))
        if product.stock < quantity:
            flash(f'Nepietiek krājumu. Pieejami: {product.stock}.', 'danger')
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
    # Rāda lietotāja grozu
    cart_items = current_user.cart_items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', title='Your Cart', cart_items=cart_items, total_price=total_price)

@shop_bp.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    # Noņem preci no groza, pārbauda īpašumtiesības
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        flash('Jums nav tiesību dzēst šo preci.', 'danger')
        return redirect(url_for('shop.cart'))
    db.session.delete(cart_item)
    db.session.commit()
    flash('Prece izņemta no groza.', 'success')
    return redirect(url_for('shop.cart'))

@shop_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Apstrādā pasūtījumu un samazina preču krājumus
    cart_items = current_user.cart_items.all()
    if not cart_items:
        flash('Jūsu grozs ir tukšs!', 'warning')
        return redirect(url_for('shop.product_list'))

    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    checkout_form = CheckoutForm()

    if checkout_form.validate_on_submit():
        new_order = Order(user_id=current_user.id, total_amount=total_amount, status='Processing')
        db.session.add(new_order)
        db.session.flush()
        for item in cart_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            product = Product.query.get(item.product_id)
            if product.stock < item.quantity:
                db.session.rollback()
                flash(f'Nepietiek krājumu {product.name}. Lūdzu, pielāgojiet grozu.', 'danger')
                return redirect(url_for('shop.cart'))
            product.stock -= item.quantity
            db.session.add(order_item)
            db.session.delete(item)
        db.session.commit()
        flash('Pasūtījums veiksmīgi veikts!', 'success')
        return redirect(url_for('shop.purchase_history'))
    return render_template('checkout.html', title='Checkout', cart_items=cart_items, total_amount=total_amount, form=checkout_form)

@shop_bp.route('/purchase_history')
@login_required
def purchase_history():
    # Rāda lietotāja pirkumu vēsturi
    orders = current_user.orders.order_by(Order.order_date.desc()).all()
    return render_template('purchase_history.html', title='Purchase History', orders=orders)

@shop_bp.route("/chatbot", methods=["POST"])
def chatbot_endpoint():
    # 1. SOLIS — Iegūst lietotāja jautājumu un čata vēsturi
    data = request.get_json()
    user_message = data.get("message", "")
    chat_history = data.get("history", [])

    # 2. SOLIS — Iegūst sarakstu ar produktiem (iekļauj tekstā promptam)
    products_prompt = get_products_from_db()
    bot_prompt_message = f"{products_prompt}\n{user_message}"

    # 3. SOLIS — Sūta pieprasījumu uz čatbotu un atgriež atbildi
    response = chatbot.get_chatbot_response(bot_prompt_message, chat_history)
    return jsonify(response)
