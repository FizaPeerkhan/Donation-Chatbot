from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import joblib
import json
import random
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Load chatbot resources
try:
    model = joblib.load("chatbot_model.pkl")
    with open("intents.json", "r", encoding="utf-8") as file:
        intents_data = json.load(file)

    # Create dictionary: {tag: [responses]}
    responses = {intent['tag']: intent['responses'] for intent in intents_data['intents']}
    logger.info("✅ Chatbot resources loaded successfully.")

except Exception as e:
    logger.error(f"❌ Error loading chatbot resources: {str(e)}")
    raise RuntimeError(f"Chatbot initialization failed: {str(e)}")

# Chatbot response API
@csrf_exempt
def chatbot_response(request):
    if request.method == "GET":
        user_message = request.GET.get("message", "").strip().lower()
    elif request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_message = data.get("message", "").strip().lower()
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

    if not user_message:
        return JsonResponse({"error": "Empty message"}, status=400)

    try:
        # Predict tag (model returns a string, e.g., "greeting")
        predicted_tag = model.predict([user_message])[0]
        logger.debug(f"Predicted tag: {predicted_tag}")

        # Get appropriate response
        response_list = responses.get(predicted_tag, ["I'm not sure how to respond to that."])
        reply = random.choice(response_list)

    except Exception as e:
        logger.error(f"❌ Processing error: {str(e)}")
        reply = f"Oops! Something went wrong: {str(e)}"

    return JsonResponse({"response": reply})

# Renders chatbot homepage
def chatbot_home(request):
    return render(request, 'chatbot_home.html')

# Health check route
def health_check(request):
    try:
        assert model and responses
        return JsonResponse({"status": "ok"})
    except Exception as e:
        logger.critical(f"Health check failed: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
