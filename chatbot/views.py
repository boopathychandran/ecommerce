from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import openai
import google.generativeai as genai
from login.models import Product, Coupon

# Create your views here.

@csrf_exempt
def chat_response(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'response': "I didn't catch that. How can I ayudar today?"})

        # --- Context Aggregation ---
        user_name = request.user.username if request.user.is_authenticated else "Guest"
        
        # 1. Inventory Support
        products = Product.objects.all().order_by('-is_featured', '-created_at')[:15]
        inventory_context = "Available Products:\n"
        for p in products:
            inventory_context += f"- {p.name} (₹{p.price}, Slug: {p.slug})\n"

        # 2. User Specific Context
        personal_context = f"User: {user_name}\n"
        cart_summary = "Your cart is currently empty."
        order_summary = "No recent orders found."
        
        if request.user.is_authenticated:
            from login.models import Cart, Order
            # Cart Info
            try:
                cart = Cart.objects.get(user=request.user)
                if cart.items.exists():
                    items_str = ", ".join([f"{i.product.name} (x{i.quantity})" for i in cart.items.all()])
                    cart_summary = f"Your cart has {cart.item_count} items: {items_str}. Total: ₹{cart.total_price}"
            except Cart.DoesNotExist: pass
            
            # Order Info
            recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:3]
            if recent_orders.exists():
                order_summary = "Your recent orders:\n"
                for o in recent_orders:
                    order_summary += f"- Order #{o.id}: {o.status.upper()} (₹{o.total_price})\n"
        
        personal_context += f"Cart Status: {cart_summary}\nOrder Status: {order_summary}\n"

        # 3. Promotions
        coupons = Coupon.objects.filter(is_active=True)
        active_promos = "Active Discounts: " + (", ".join([f"{c.code} ({c.discount_percent}% off)" for c in coupons if c.is_valid()]) or "None at the moment.")

        # --- AI System Instruction ---
        system_instruction = f"""
        Identity: You are 'Chandran AI', a high-tech assistant for Chandran Electronics.
        Atmosphere: Professional, futuristic, helpful. Use Markdown.
        
        Context:
        {personal_context}
        {inventory_context}
        {active_promos}
        
        Capabilities:
        - Suggest products using: [Product Name](/product/slug/)
        - If the user wants to add to cart, suggest it and say you can't do it directly yet (but provide the link).
        - If they want to pay, redirect them to [/payment/](/payment/).
        - Be concise.
        """

        # --- LOCAL LOGIC ENGINE (Immediate Fallback) ---
        local_response = None
        user_msg_low = user_message.lower()
        
        if any(word in user_msg_low for word in ['what products', 'show', 'buy', 'inventory']):
            local_response = f"I have several cutting-edge items! {inventory_context.replace('Available Products:', 'Our top picks:')}\nCheck them out: [View All Products](/ecommerce/)"
        elif 'cart' in user_msg_low:
            local_response = f"{cart_summary}. Want to [Checkout](/cart/)?"
        elif 'order' in user_msg_low:
            local_response = f"{order_summary}"
        elif 'checkout' in user_msg_low or 'payment' in user_msg_low:
             local_response = "Ready to upgrade your gear? [Proceed to Payment](/payment/)"

        # --- AI CALLS ---
        ai_response_text = None

        # Try Gemini first
        gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
        if gemini_key and gemini_key not in [None, '', 'your_gemini_api_key_here']:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                full_prompt = f"{system_instruction}\n\nUser: {user_message}"
                res = model.generate_content(full_prompt)
                if res and hasattr(res, 'text'):
                    ai_response_text = res.text
            except Exception as e:
                print(f"Gemini API Error: {e}")

        # Try OpenAI Fallback
        if not ai_response_text:
            openai_key = getattr(settings, 'OPENAI_API_KEY', None)
            if openai_key and openai_key not in [None, '', 'your_openai_api_key_here']:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    completion = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_message}]
                    )
                    ai_response_text = completion.choices[0].message.content
                except Exception as e:
                    print(f"OpenAI API Error: {e}")

        # Final Response Logic
        final_response = ai_response_text or local_response or "Our systems are currently calibrating. I'm here to help with products, cart, and orders—what tech are we looking for?"
        
        return JsonResponse({'response': final_response})

    except Exception as e:
        return JsonResponse({'response': f"Neural Link Error: {str(e)}"}, status=500)

