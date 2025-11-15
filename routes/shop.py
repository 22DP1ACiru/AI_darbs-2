from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from models import Product, CartItem, Order, OrderItem
from database import db
from flask_login import current_user, login_required
from forms import AddToCartForm, CheckoutForm
from chatbot_integration.chatbot_service import ChatbotService

# Create a Flask blueprint for the shop module
shop_bp = Blueprint('shop', __name__, template_folder='../templates')

# Initialize the chatbot service
chatbot_service = ChatbotService()

def get_products_from_db():
    """
    Fetches all products from the database and formats them into a string.
    This string can then be provided to the chatbot for reference.
    """
    try:
        products = Product.query.all()  # Retrieve all products from DB
        if not products:
            return "There are currently no products available in the shop."
        
        product_list_str = "CURRENT PRODUCT INVENTORY:\n"
        product_list_str += "=" * 50 + "\n"
        
        for p in products:
            # Check stock availability
            stock_status = "In Stock" if p.stock > 0 else "Out of Stock"
            product_list_str += f"• {p.name}\n"
            product_list_str += f"  Price: ${p.price:.2f}\n"
            product_list_str += f"  Stock: {p.stock} ({stock_status})\n"
            if p.description:
                # Truncate long descriptions to 100 characters
                desc = p.description[:100] + "..." if len(p.description) > 100 else p.description
                product_list_str += f"  Description: {desc}\n"
            product_list_str += "\n"
        
        return product_list_str
    except Exception as e:
        # Catch any DB errors and log them
        print(f"Error fetching products from DB: {e}")
        return "I was unable to access the product catalog."

@shop_bp.route('/chatbot', methods=['POST'])
def chatbot():
    """
    Endpoint to handle chatbot requests from the frontend.
    Provides product info to the chatbot for more informed responses.
    """
    try:
        data = request.get_json()  # Get JSON payload from request
        if not data:
            return jsonify({'status': 'error', 'response': 'No data provided'}), 400
        
        user_message = data.get('message')
        chat_history = data.get('chat_history', [])
        
        # Validate user input
        if not user_message or not user_message.strip():
            return jsonify({'status': 'error', 'response': 'Empty message'}), 400
        
        # Get product info from database
        products_info = get_products_from_db()
        
        # Get chatbot response based on user message, history, and product info
        response_data = chatbot_service.get_chatbot_response(
            user_message=user_message,
            chat_history=chat_history,
            products_info=products_info
        )
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Chatbot endpoint error: {str(e)}")
        return jsonify({'status': 'error', 'response': 'Internal server error. Please try again later.'}), 500

@shop_bp.route('/shop')
def product_list():
    """
    Display a list of all products in the shop.
    """
    products = Product.query.all()
    return render_template('shop/product_list.html', title='Shop', products=products)

@shop_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    """
    Display a single product's details and handle "Add to Cart" functionality.
    """
    product = Product.query.get_or_404(product_id)  # Get product or 404 if not found
    form = AddToCartForm()
    
    if form.validate_on_submit():  # Handle form submission
        if not current_user.is_authenticated:
            flash('You need to log in to add items to your cart.', 'info')
            return redirect(url_for('auth.login', next=request.url))

        quantity = form.quantity.data
        if quantity <= 0:
            flash('Quantity must be at least 1.', 'danger')
            return redirect(url_for('shop.product_detail', product_id=product.id))

        if product.stock < quantity:
            flash(f'Insufficient stock. Only {product.stock} left.', 'danger')
            return redirect(url_for('shop.product_detail', product_id=product.id))

        # Check if item is already in user's cart
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        if cart_item:
            cart_item.quantity += quantity  # Update quantity if already in cart
        else:
            cart_item = CartItem(user_id=current_user.id, product_id=product.id, quantity=quantity)
        
        db.session.add(cart_item)
        db.session.commit()
        flash(f'{quantity} x {product.name} added to your cart!', 'success')
        return redirect(url_for('shop.cart'))
    
    return render_template('shop/product_detail.html', title=product.name, product=product, form=form)

@shop_bp.route('/cart')
@login_required
def cart():
    """
    Display the current user's shopping cart.
    """
    cart_items = current_user.cart_items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', title='Your Cart', cart_items=cart_items, total_price=total_price)

@shop_bp.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    """
    Remove an item from the user's cart.
    """
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        flash('You are not authorized to remove this item.', 'danger')
        return redirect(url_for('shop.cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'success')
    return redirect(url_for('shop.cart'))

@shop_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """
    Handle the checkout process: validate cart, create order, update stock, and clear cart.
    """
    cart_items = current_user.cart_items.all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('shop.product_list'))

    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    checkout_form = CheckoutForm()

    if checkout_form.validate_on_submit():
        # Create new order
        new_order = Order(user_id=current_user.id, total_amount=total_amount, status='Processing')
        db.session.add(new_order)
        db.session.flush()  # Flush to get order ID

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
                flash(f'Not enough stock for {product.name}. Please adjust your cart.', 'danger')
                return redirect(url_for('shop.cart'))
            product.stock -= item.quantity  # Deduct stock
            db.session.add(order_item)
            db.session.delete(item)  # Remove from cart
        
        db.session.commit()
        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('shop.purchase_history'))
    
    return render_template('checkout.html', title='Checkout', cart_items=cart_items, total_amount=total_amount, form=checkout_form)

@shop_bp.route('/purchase_history')
@login_required
def purchase_history():
    """
    Display all past orders of the current user.
    """
    orders = current_user.orders.order_by(Order.order_date.desc()).all()
    return render_template('purchase_history.html', title='Purchase History', orders=orders)
