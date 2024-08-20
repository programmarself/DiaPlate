import streamlit as st
import anthropic
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from fpdf import FPDF

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

# Function to create a PDF of the meal plan
def create_pdf(meal_plan, name):
    pdf = FPDF()
    pdf.add_page()
    
    # Set title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"{name}'s DiaPlate Meal Plan", ln=True, align='C')
    
    pdf.ln(10)  # Add a line break
    
    # Add meal plan text
    pdf.set_font("Arial", "", 12)
    for line in meal_plan.split('\n'):
        pdf.multi_cell(0, 10, line)
    
    # Output the PDF as a binary string
    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output

# Function to overlay text on the banner image
def overlay_text_on_image(image_path, text, font_size=50, font_color=(255, 255, 255)):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Load a font
    font = ImageFont.truetype("arial.ttf", font_size)
    
    # Calculate the position for the text to be centered
    text_width, text_height = draw.textsize(text, font=font)
    width, height = image.size
    position = ((width - text_width) // 2, (height - text_height) // 2)
    
    # Overlay the text on the image
    draw.text(position, text, font=font, fill=font_color)
    return image

# Streamlit app
st.set_page_config(page_title="DiaPlate 🍽️", page_icon="🍽️", layout="centered")

# Add a banner image with title overlay
banner_with_title = overlay_text_on_image("diaplate_banner.png", "Welcome to DiaPlate 🍽️", font_size=70)
st.image(banner_with_title, use_column_width=True)

st.title("Your Personalized Meal Planning Companion")

st.write("""
**Designed for managing diabetes with tailored meal plans that align with your lifestyle and health goals.**
Enter your details below to start your journey toward better health! 🌟
""")

# Initialize session state for form fields
if 'name' not in st.session_state:
    st.session_state['name'] = ''
if 'goal' not in st.session_state:
    st.session_state['goal'] = ''
if 'fasting_sugar' not in st.session_state:
    st.session_state['fasting_sugar'] = 0
if 'pre_meal_sugar' not in st.session_state:
    st.session_state['pre_meal_sugar'] = 0
if 'post_meal_sugar' not in st.session_state:
    st.session_state['post_meal_sugar'] = 0
if 'dietary_preferences' not in st.session_state:
    st.session_state['dietary_preferences'] = ''
if 'exclusions' not in st.session_state:
    st.session_state['exclusions'] = ''

# Sidebar inputs for user details, sugar levels, and dietary preferences
st.sidebar.header("👤 Personalize Your Plan")

name = st.sidebar.text_input("Your Name", value=st.session_state['name'])
goal = st.sidebar.selectbox("Health Goal", options=["Maintain Weight", "Lose Weight", "Gain Weight"], index=["Maintain Weight", "Lose Weight", "Gain Weight"].index(st.session_state['goal']))
fasting_sugar = st.sidebar.number_input("Fasting Sugar Levels (mg/dL)", min_value=0, max_value=500, step=1, value=st.session_state['fasting_sugar'])
pre_meal_sugar = st.sidebar.number_input("Pre-Meal Sugar Levels (mg/dL)", min_value=0, max_value=500, step=1, value=st.session_state['pre_meal_sugar'])
post_meal_sugar = st.sidebar.number_input("Post-Meal Sugar Levels (mg/dL)", min_value=0, max_value=500, step=1, value=st.session_state['post_meal_sugar'])
dietary_preferences = st.sidebar.text_input("Dietary Preferences (e.g., vegetarian, low-carb)", value=st.session_state['dietary_preferences'])
exclusions = st.sidebar.text_input("Foods to Avoid (e.g., nuts, dairy)", value=st.session_state['exclusions'])

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

        # Create the PDF
        pdf_file = create_pdf(meal_plan, name)

        # Modify the download button for PDF
        st.download_button(
            label="📥 Download Meal Plan as PDF",
            data=pdf_file,
            file_name=f"{name}_DiaPlate_Meal_Plan.pdf",
            mime="application/pdf"
        )
        
        # Clear the session state for new input
        st.session_state['name'] = ''
        st.session_state['goal'] = 'Maintain Weight'
        st.session_state['fasting_sugar'] = 0
        st.session_state['pre_meal_sugar'] = 0
        st.session_state['post_meal_sugar'] = 0
        st.session_state['dietary_preferences'] = ''
        st.session_state['exclusions'] = ''
        
        # Suggest physical activities
        st.write("🔄 **Suggested Physical Activities**")
        st.write("Regular physical activity is crucial for managing diabetes. Consider incorporating daily walks, yoga, or light resistance training into your routine.")
