import streamlit as st
import anthropic
from PIL import Image
import matplotlib.pyplot as plt

api_key = st.secrets["api_key"]

# Function to call Claude AI API and get a personalized meal plan
def get_meal_plan(api_key, name, fasting_sugar, pre_meal_sugar, post_meal_sugar, dietary_preferences, goal, exclusions):
    # Initialize the Claude AI client with the provided API key
    client = anthropic.Anthropic(api_key=api_key)
    
    # Define the prompt to send to Claude AI
    prompt = (
        f"My name is {name}. My goal is {goal}. My fasting sugar level is {fasting_sugar} mg/dL, "
        f"my pre-meal sugar level is {pre_meal_sugar} mg/dL, and my post-meal sugar level is {post_meal_sugar} mg/dL. "
        f"My dietary preferences are {dietary_preferences}, and I want to avoid {exclusions}. "
        "Please provide a personalized meal plan that can help me manage my blood sugar levels effectively, "
        "along with any additional tips or exercises that could support my goal."
    )
    
    # Call Claude AI API
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=300,
        temperature=0.7,
        system="You are a world-class nutritionist who specializes in diabetes management.",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    raw_context = message.content
    itinerary = raw_context[0].text
    return itinerary

# Streamlit app
st.set_page_config(page_title="DiaPlate 🍽️", page_icon="🍽️", layout="centered")

# Add a banner image
banner = Image.open("diaplate_banner.png")
st.image(banner, use_column_width=True)

st.title("Welcome to DiaPlate 🍽️")

st.write("""
**Your Personalized Meal Planning Companion** - Designed for managing diabetes with tailored meal plans that align with your lifestyle and health goals.
Enter your details below to start your journey toward better health! 🌟
""")

# Sidebar inputs for user details, sugar levels, and dietary preferences
st.sidebar.header("👤 Personalize Your Plan")

name = st.sidebar.text_input("Your Name")
goal = st.sidebar.selectbox("Health Goal", options=["Maintain Weight", "Lose Weight", "Gain Weight"])
fasting_sugar = st.sidebar.number_input("Fasting Sugar Levels (mg/dL)", min_value=0, max_value=500, step=1)
pre_meal_sugar = st.sidebar.number_input("Pre-Meal Sugar Levels (mg/dL)", min_value=0, max_value=500, step=1)
post_meal_sugar = st.sidebar.number_input("Post-Meal Sugar Levels (mg/dL)", min_value=0, max_value=500, step=1)
dietary_preferences = st.sidebar.text_input("Dietary Preferences (e.g., vegetarian, low-carb)")
exclusions = st.sidebar.text_input("Foods to Avoid (e.g., nuts, dairy)")

# Display a pie chart for dietary preferences
if dietary_preferences:
    preferences = dietary_preferences.split(", ")
    fig, ax = plt.subplots()
    ax.pie([1]*len(preferences), labels=preferences, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.sidebar.pyplot(fig)

# Generate meal plan button
if st.sidebar.button("Generate Meal Plan"):
    if not name:
        st.sidebar.warning("Please enter your name to personalize your experience.")
    else:
        meal_plan = get_meal_plan(api_key, name, fasting_sugar, pre_meal_sugar, post_meal_sugar, dietary_preferences, goal, exclusions)
        st.write(f"Hi {name}, based on your input, here is a personalized meal plan to help you achieve your goal:")
        st.markdown(meal_plan)

        # Add images to represent meal suggestions
        meal_images = {
            "breakfast": Image.open("breakfast.png"),
            "lunch": Image.open("lunch.png"),
            "dinner": Image.open("dinner.png"),
            "snack": Image.open("snack.png")
        }

        st.image([meal_images["breakfast"], meal_images["lunch"], meal_images["dinner"], meal_images["snack"]], width=150, caption=["Breakfast", "Lunch", "Dinner", "Snack"])

        # Add a download button
        st.download_button(
            label="📥 Download Meal Plan",
            data=meal_plan,
            file_name=f"{name}_DiaPlate_Meal_Plan.pdf",
            mime="pdf"
        )
        
        # Suggest physical activities
        st.write("🔄 **Suggested Physical Activities**")
        st.write("Regular physical activity is crucial for managing diabetes. Consider incorporating daily walks, yoga, or light resistance training into your routine.")
