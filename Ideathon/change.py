import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_core.prompts import (PromptTemplate)
import datetime

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Set up page layout
st.set_page_config(
    page_title="FoodBridge - Connecting Surplus to Smiles",
    page_icon="🍽️",
    layout="wide"
)

# Session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Session state for chatbot memory
if "conversation" not in st.session_state:
    memory = ConversationBufferMemory()
    llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=groq_api_key)
    
    prompt_template = PromptTemplate(
        input_variables=["history", "input"],
        template="""
        You are the FoodBridge Assistant, helping users navigate the FoodBridge platform.
        
        FoodBridge connects event organizers with nearby NGOs to reduce food waste by donating surplus food.
        
        Key features include:
        1. Event organizers can list events with expected food surplus
        2. NGOs receive advance notifications about nearby events
        3. Location-based matching connects events with closest NGOs
        4. Optional transportation mediation services
        5. Real-time coordination between organizers and NGOs
        
        For event organizers: Help them list events, understand the process, and coordinate donations.
        For NGOs: Help them find nearby events, understand notification systems, and coordinate pickups.
        
        Previous conversation:
        {history}
        
        User: {input}
        FoodBridge Assistant:
        """
    )
    
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True,
        prompt=prompt_template
    )

# Dummy data for NGOs
if "ngos" not in st.session_state:
    st.session_state.ngos = [
        {"id": 1, "name": "Feed the Need", "location": "Downtown", "contact": "contact@feedtheneed.org"},
        {"id": 2, "name": "Food for All", "location": "Westside", "contact": "info@foodforall.org"},
        {"id": 3, "name": "Community Plate", "location": "Eastside", "contact": "help@communityplate.org"}
    ]

# Dummy event storage
if "events" not in st.session_state:
    st.session_state.events = []

# Sidebar Navigation
st.sidebar.title("🍽️ FoodBridge")
st.sidebar.write("Connecting Surplus to Smiles")
page_selection = st.sidebar.radio("Go to:", ["Home", "Event Organizer", "NGO", "Chatbot"])

# Update session state for navigation
st.session_state.page = page_selection

# **MAIN PAGE**
if st.session_state.page == "Home":
    st.title("🍽️ FoodBridge - Connecting Surplus to Smiles")
    
    st.markdown("""
    ### Turning Excess into Impact
    
    FoodBridge is an innovative platform that connects event organizers with nearby NGOs to minimize food waste 
    and provide nourishment to those in need.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("For Event Organizers")
        st.markdown("""
        - List your events with expected food surplus
        - Get connected with nearby NGOs
        - Coordinate food pickup seamlessly
        - Reduce waste while making a positive impact
        - Optional transportation assistance
        """)
        
    with col2:
        st.subheader("For NGOs")
        st.markdown("""
        - Receive advance notification of nearby events
        - Plan your food collection efficiently
        - Coordinate directly with event organizers
        - Location-based matching for optimal logistics
        - Ensure more food reaches those in need
        """)
    
    st.markdown("---")
    st.subheader("Get Started")
    st.write("Use the sidebar to navigate to your role.")

# **EVENT ORGANIZER PAGE**
elif st.session_state.page == "Event Organizer":
    st.title("🎉 Event Organizer Dashboard")

    tab1, tab2, tab3 = st.tabs(["List a New Event", "My Events", "Find NGOs"])

    with tab1:
        st.header("List a New Event")
        with st.form("event_form"):
            col1, col2 = st.columns(2)
            with col1:
                event_name = st.text_input("Event Name")
                event_date = st.date_input("Event Date", min_value=datetime.date.today())
                event_location = st.selectbox("Location", ["Downtown", "Westside", "Eastside", "Northside", "Southside"])
            with col2:
                expected_guests = st.number_input("Expected Number of Guests", min_value=1, value=100)
                expected_surplus = st.slider("Expected Food Surplus (meals)", 5, 500, 50)
                transport_help = st.checkbox("Need help with transportation")
            
            additional_info = st.text_area("Additional Information")
            submit_button = st.form_submit_button("List Event")
            
            if submit_button and event_name:
                new_event = {
                    "id": len(st.session_state.events) + 1,
                    "name": event_name,
                    "date": event_date,
                    "location": event_location,
                    "guests": expected_guests,
                    "surplus": expected_surplus,
                    "transport_help": transport_help,
                    "info": additional_info,
                    "status": "Listed",
                    "interested_ngos": []
                }
                st.session_state.events.append(new_event)
                st.success(f"Event '{event_name}' has been listed successfully!")

# **NGO PAGE**
elif st.session_state.page == "NGO":
    st.title("🏢 NGO Dashboard")
    
    tab1, tab2 = st.tabs(["Available Events", "My Commitments"])

    with tab1:
        st.header("Available Events")
        if not st.session_state.events:
            st.info("There are no events currently listed.")
        else:
            for event in st.session_state.events:
                if event['status'] == "Listed":
                    with st.expander(f"{event['name']} - {event['date'].strftime('%B %d, %Y')}"):
                        st.write(f"**Location:** {event['location']}")
                        st.write(f"**Expected Surplus:** {event['surplus']} meals")
                        if st.button(f"Express Interest #{event['id']}"):
                            event['interested_ngos'].append(1)
                            st.success(f"You expressed interest in '{event['name']}'. The organizer will be notified.")

# **CHATBOT PAGE**
elif st.session_state.page == "Chatbot":
    st.title("💬 FoodBridge Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = st.session_state.conversation.predict(input=prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)



