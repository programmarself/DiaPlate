import streamlit as st
import anthropic
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from fpdf import FPDF

# Load API key from Streamlit secrets
api_key = st.secrets["api_key"]

# Function to overlay text on the banner image
def overlay_text_on_image(image_path, text, font_size=50, font_color=(255, 255, 255)):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate the position for the text to be centered
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]  # Get the width and height from the bounding box
    width, height = image.size
    position = ((width - text_width) // 2, (height - text_height) // 2)
    
    # Overlay the text on the image
    draw.text(position, text, font=font, fill=font_color)
    return image

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

# Function to generate PDF from the meal plan
def generate_pdf(meal_plan, name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, meal_plan)
    return pdf.output(dest='S').encode('latin1')

# Streamlit app configuration
st.set_page_config(page_title="DiaPlate 🍽️", page_icon="🍽️", layout="centered")

# Initialize form values
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Overlay title on the banner image
banner_with_title = overlay_text_on_image("diaplate_banner.png", "Welcome to DiaPlate 🍽️", font_size=70)
st.image(banner_with_title, use_column_width=True)

st.title("Welcome to DiaPlate 🍽️")

st.write("""
**Your Personalized Meal Planning Companion** - Designed for managing diabetes with tailored meal plans that align with your lifestyle and health goals.
Enter your details below to start your journey toward better health! 🌟
""")

# Sidebar inputs for user details, sugar levels, and dietary preferences
st.sidebar.header("👤 Personalize Your Plan")

name = st.sidebar.text_input("Your Name", key="name")
goal = st.sidebar.selectbox("Health Goal", options=["Maintain Weight", "Lose Weight", "Gain Weight"], key="goal")
fasting_sugar = st.sidebar.number_input("Fasting Sugar Levels (mg/dL)", min_value=0, max_value=500, step=1, key="fasting_sugar")
pre_meal_sugar = st.sidebar.number_input("Pre-Meal Sugar Levels (mg/dL)", min_value=0, max_value=500, step=1, key="pre_meal_sugar")
post_meal_sugar = st.sidebar.number_input("Post-Meal Sugar Levels (mg/dL)", min_value=0, max_value=500, step=1, key="post_meal_sugar")
dietary_preferences = st.sidebar.text_input("Dietary Preferences (e.g., vegetarian, low-carb)", key="dietary_preferences")
exclusions = st.sidebar.text_input("Foods to Avoid (e.g., nuts, dairy)", key="exclusions")

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

        # Generate PDF and provide download button
        pdf_data = generate_pdf(meal_plan, name)
        st.download_button(
            label="📥 Download Meal Plan as PDF",
            data=pdf_data,
            file_name=f"{name}_DiaPlate_Meal_Plan.pdf",
            mime="application/pdf"
        )
        
        # Suggest physical activities
        st.write("🔄 **Suggested Physical Activities**")
        st.write("Regular physical activity is crucial for managing diabetes. Consider incorporating daily walks, yoga, or light resistance training into your routine.")

        # Reset form fields after generating the meal plan
        st.session_state.name = ""
        st.session_state.goal = "Maintain Weight"
        st.session_state.fasting_sugar = 0
        st.session_state.pre_meal_sugar = 0
        st.session_state.post_meal_sugar = 0
        st.session_state.dietary_preferences = ""
        st.session_state.exclusions = ""
        st.session_state.form_submitted = False
        st.experimental_rerun()
