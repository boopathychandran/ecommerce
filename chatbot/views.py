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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            gemini_error = None
            openai_error = None
            
            if not user_message:
                return JsonResponse({'response': "I didn't catch that. Could you please repeat?"})

            # 1. Try Google Gemini (Best Free Option)
            gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
            print(f"DEBUG: Gemini Key found: {bool(gemini_key)}, Key start: {gemini_key[:5] if gemini_key else 'None'}")
            
            if gemini_key and gemini_key != 'your_gemini_api_key_here':
                try:
                    genai.configure(api_key=gemini_key)
                    # Fetch user info for personalization
                    user_name = request.user.username if request.user.is_authenticated else "Guest"
                    
                    # Fetch product data
                    products = Product.objects.all()
                    product_context = "\nAvailable Inventory:\n"
                    for p in products:
                        product_context += f"- [ID: {p.id}] {p.name}: ₹{p.price} (Category: {p.category}). Description: {p.description}\n"

                    # Fetch available coupons
                    coupons = Coupon.objects.filter(is_active=True)
                    coupon_context = "\nAvailable Coupons:\n"
                    for c in coupons:
                        if c.is_valid():
                            coupon_context += f"- {c.code}: {c.discount_percent}% OFF\n"

                    # System prompt integration for Gemini
                    system_instruction = f"""
                    You are 'Chandranbot', the advanced AI Shopping Assistant for 'Chandran Electronics'.
                    The current user is: {user_name}
                    
                    {product_context}
                    {coupon_context}
                    
                    Your Mission:
                    1. Help {user_name} find the PERFECT product from our inventory above.
                    2. If a user asks for something we DON'T have, suggest the closest alternative from our list.
                    3. ALWAYS mention the price and why it's a good choice.
                    4. When recommending a product, you MUST use this format to link to it: [Product Name](/product/ID/)
                    5. Provide shipping info (Free > ₹5000) and support info (+91 98765 43210) when relevant.
                    6. If a user asks for discounts or coupons, tell them about the ones in the list above.
                    
                    Rules:
                    - Be proactive! If they are looking for a laptop, don't just say 'we have laptops', say 'I recommend the [Yoga Book 2](/product/12/) because it has great battery life!'
                    - Mention coupons if the user is hesitant about price or asks for deals.
                    - Keep responses friendly, professional, and under 80 words.
                    - Use Markdown for bolding and lists.
                    """
                    
                    model = genai.GenerativeModel('gemini-flash-latest')
                    chat = model.start_chat(history=[
                        {"role": "user", "parts": [system_instruction]},
                        {"role": "model", "parts": ["Understood. I am ready to assist customers of Chandran Electronics."]}
                    ])
                    
                    response = chat.send_message(user_message)
                    return JsonResponse({'response': response.text})
                except Exception as e:
                    gemini_error = str(e)
                    print(f"Gemini Error: {e}")
                    # Don't return error yet, try OpenAI fallback

            # 2. Try OpenAI (Paid Option)
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if api_key and api_key != 'your_openai_api_key_here':
                try:
                    client = openai.OpenAI(api_key=api_key)
                    # Re-use or fetch context for OpenAI
                    if 'product_context' not in locals():
                        user_name = request.user.username if request.user.is_authenticated else "Guest"
                        products = Product.objects.all()
                        product_context = "\nAvailable Inventory:\n"
                        for p in products:
                            product_context += f"- [ID: {p.id}] {p.name}: ₹{p.price}. {p.description}\n"
                    
                    if 'coupon_context' not in locals():
                        coupons = Coupon.objects.filter(is_active=True)
                        coupon_context = "\nAvailable Coupons:\n"
                        for c in coupons:
                            if c.is_valid():
                                coupon_context += f"- {c.code}: {c.discount_percent}% OFF\n"

                    system_instruction = f"You are Chandranbot, a helpful AI shopping assistant for Chandran Electronics. Help user {user_name} find products and apply coupons. Use format [Name](/product/ID/) for links.\n\n{product_context}\n{coupon_context}"
                    completion = client.chat.completions.create(
                        model="gpt-4o", 
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_message}
                        ],
                        max_tokens=150
                    )
                    return JsonResponse({'response': completion.choices[0].message.content.strip()})
                except Exception as e:
                    openai_error = str(e)
                    print(f"OpenAI Error: {e}")

            # 3. Fallback to Rule-based Logic (Offline Mode)
            user_message = user_message.lower()
            if 'hello' in user_message or 'hi' in user_message:
                response_text = "Hello! I am your AI customer support assistant."
            elif 'shipping' in user_message or 'delivery' in user_message:
                response_text = "We offer free shipping on orders over ₹5000."
            elif 'contact' in user_message or 'support' in user_message:
                response_text = "Contact us at +91 98765 43210."
            else:
                extra_info = ""
                if gemini_error or openai_error:
                    extra_info = f" (Debug: Gemini={gemini_error}, OpenAI={openai_error})"
                response_text = f"I am currently offline. Please configure my Gemini Brain to make me smart!{extra_info}"
            
            return JsonResponse({'response': response_text})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
