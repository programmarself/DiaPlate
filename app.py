import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
from fpdf import FPDF

# Temporarily disable API key usage
# api_key = st.secrets["claude_ai"]["api_key"]

# Mock function to simulate meal plan generation
def get_meal_plan(name, fasting_sugar, pre_meal_sugar, post_meal_sugar, dietary_preferences, goal, exclusions):
    # This function will return a placeholder meal plan since the API call is disabled
    return (
        f"Hi {name}, here is a mock meal plan for you based on your input:\n\n"
        f"Fasting Sugar: {fasting_sugar} mg/dL\n"
        f"Pre-Meal Sugar: {pre_meal_sugar} mg/dL\n"
        f"Post-Meal Sugar: {post_meal_sugar} mg/dL\n"
        f"Dietary Preferences: {dietary_preferences}\n"
        f"Foods to Avoid: {exclusions}\n\n"
        f"Your goal is {goal}, so we suggest maintaining a balanced diet rich in vegetables, whole grains, and lean proteins. "
        f"Stay hydrated, and avoid foods high in sugar. Consider engaging in light physical activities such as walking or yoga."
    )

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

# Streamlit app
st.set_page_config(page_title="DiaPlate 🍽️", page_icon="🍽️", layout="centered")

# Add a banner image
banner = Image.open("diaplate_banner.png")
st.image(banner, use_column_width=True)

st.title("Welcome to DiaPlate 🍽️")
st.text("Developed By : Irfan Ullah Khan")

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
        # Since the API is disabled, use the mock meal plan function
        meal_plan = get_meal_plan(name, fasting_sugar, pre_meal_sugar, post_meal_sugar, dietary_preferences, goal, exclusions)
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
        
        # Suggest physical activities
        st.write("🔄 **Suggested Physical Activities**")
        st.write("Regular physical activity is crucial for managing diabetes. Consider incorporating daily walks, yoga, or light resistance training into your routine.")
