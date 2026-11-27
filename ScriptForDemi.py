"""
Script to create a web app with streamlit to propose Demi what to do on Sunday night."

I wanna make a sequence of questions that she has to answer in a form, and after that,
depending on her answers, I will have a score that will tell me what to do on Sunday night
between the options: "Ice Skating with the lights", "Arcade", "Live music".
Indipendently from what she scores we'll go to her room to watch a movie in the end, but I want to decide 
what to do before that based on her answers.
But in the end she will know what I suggest depending on the score, but she can still choose what to do.

The questions will be about her mood, the weather, and her preferences for activities. 
Each answer will have a score associated with it, and at the end of the form, 
the total score will determine the suggested activity.

The scoring system will be as follows:
- How much would you like to do something physically active? (1-5)
- How much of a problem would it be to travel to the activity? (1 = Very problematic, 5 = Not a problem)
- How important it is to talk to each other during the activity? (1 = Not important, 5 = Very important)

And the relative scores for each activity will be:
- Ice Skating with the lights: 5, 2.5, 2
- Arcade: 3, 4, 4
- Live music: 1, 1, 5

In the end she will also have the option to choose whether she wants to eat something after that, and she can choose if she wants to
already decide or leave it for later.
If she wants to decide, the options will be:
- Pizza
- Gyoza and Ramen to try if we don't want to eat that much
- Korean fried chicken

I wanna make the form disappear after she submits it.
"""

import streamlit as st
import smtplib
from email.message import EmailMessage

EMAIL_SENDER       = "francrscopicaro@gmail.com" # Il mio indirizzo email
EMAIL_RECIPIENT    = "francrscopicaro@gmail.com" # L'indirizzo email di destinazione
ACTIVITIES = [
    "Ice Skating with the lights",
    "Arcade",
    "Live music",
]

def send_mail(activity, food):
    msg = EmailMessage()
    msg['Subject'] = "Sunday Night Activity Suggestion"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    msg.set_content(f"The chosen activity is {activity}, and the food choice is {food}.")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, st.secrets["email"]["app_password"])
        server.send_message(msg)




st.title("Sunday Night Activities")
st.write("Let's find out what we should do on Sunday night!")

submit_button = False
if not st.session_state.get("activity_submitted", False):
    with st.form(key='activity_form'):
        st.markdown("Did you really think I forgot about you? I could never.\nI just had to install all the stuff on this new laptop," \
        "but now we're more than ready to decide what to do!\n" \
        "But now I have a few questions for you to help me decide what we should do.")
        
        physical_activity = st.slider("How much would you like to do something physically active?", 1, 5, 3)
        travel_problem = st.slider("How much of a problem would it be to travel to the activity? (1 = Not a problem, 5 = Very problematic) (At most is 40 minutes by tram {20 tram + 20 walk})", 1, 5, 3)
        talk_importance = st.slider("How important is it to talk to each other during the activity? (1 = Not important, 5 = Very important)", 1, 5, 3)
        
        submit_button = st.form_submit_button(label='Submit')

if not st.session_state.get("activity_submitted", False) and submit_button:
    def prob_dist(input, val):
        return (input + val)*1.5
    
    # Calculate scores for each activity in euclidean distance style
    ice_skating_score = ((physical_activity-5)**2 + prob_dist(travel_problem, 2.5) + (talk_importance-2)**2)**0.5
    arcade_score = ((physical_activity-3)**2 + prob_dist(travel_problem, 4) + (talk_importance-4)**2)**0.5
    live_music_score = ((physical_activity-1)**2 + prob_dist(travel_problem, 1) + (talk_importance-5)**2)**0.5

    # Determine the suggested activity based on the highest score
    scores = {
        "Ice Skating with the lights": ice_skating_score,
        "Arcade": arcade_score,
        "Live music": live_music_score
    }
    
    suggested_activity = min(scores, key=scores.get)  # Get the activity with the lowest score (closest match)
    
    st.session_state.activity_submitted = True
    st.session_state.suggested_activity = suggested_activity
    st.rerun()

if st.session_state.get("activity_submitted", False):
    suggested_activity = st.session_state.suggested_activity
    st.write(f"Based on your answers, my suggestion is: **{suggested_activity}**.")

    if not st.session_state.get("activity_choice_submitted", False):
        with st.form(key="activity_choice_form"):
            chosen_activity = st.selectbox(
                "Which activity would you like to do?",
                ACTIVITIES,
                index=ACTIVITIES.index(suggested_activity),
            )
            activity_choice_submit_button = st.form_submit_button(label="Choose this activity")

        if activity_choice_submit_button:
            st.session_state.chosen_activity = chosen_activity
            st.session_state.activity_choice_submitted = True
            st.rerun()

    if st.session_state.get("activity_choice_submitted", False):
        chosen_activity = st.session_state.chosen_activity
        st.write(f"You chose: **{chosen_activity}**.")

        if not st.session_state.get("food_decision_submitted", False):
            with st.form(key="food_decision_form"):
                st.markdown("Would you like to decide what to eat after the activity or do you wanna leave it to Sunday night?\n"
                         "Keep in mind that I didn't forget what we said and the incredible fact that you never saw "
                         "the movies we talked about, so remember that after the activity we either go to eat something and then have to "
                         "watch the movie, or we go directly to watch the movie, your choice.")
                food_decision = st.radio("Choose an option:", ["Decide now", "Decide later"])
                food_decision_submit_button = st.form_submit_button(label="Submit")

            if food_decision_submit_button:
                if food_decision == "Decide later":
                    send_mail(chosen_activity, "Decide later")
                    st.session_state.food_choice = "Decide later"
                    st.session_state.food_submitted = True
                st.session_state.food_decision = food_decision
                st.session_state.food_decision_submitted = True
                st.rerun()

        if (
            st.session_state.get("food_decision_submitted", False)
            and st.session_state.food_decision == "Decide now"
            and not st.session_state.get("food_submitted", False)
        ):
            with st.form(key="food_choice_form"):
                food_choice = st.selectbox(
                    "What would you prefer to eat?",
                    [
                        "Pizza (Always a nice idea)",
                        "Gyoza and Ramen (I saw a cute place close to you)",
                        "Korean fried chicken (Same as Gyoza and Ramen)",
                        "Something else that you know in your surroundings",
                    ],
                )
                food_choice_submit_button = st.form_submit_button(label="Submit")

            if food_choice_submit_button:
                send_mail(chosen_activity, food_choice)
                st.session_state.food_choice = food_choice
                st.session_state.food_submitted = True
                st.rerun()

        if st.session_state.get("food_submitted", False):
            food_choice = st.session_state.food_choice
            if food_choice == "Decide later":
                st.write("You can decide what to eat later.")
            else:
                st.write(f"You have chosen to eat: **{food_choice}** after the activity.")
    
