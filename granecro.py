from collections import namedtuple
import pandas as pd
import streamlit as st
import time
import base64
import random


###########################################################################
Card = namedtuple("Card", ["card_image",
                           "card_type",
                           "card_text",
                           "card_level",
                           "card_admittance_sanity_price",
                           "card_admittance_course_level_prerequisite",
                           "card_admittance_magic_prerequisite",
                           "card_credits",
                           "card_study_buddy_1_effect",
                           "card_study_buddy_2_effect",
                           "card_learning_effect"])



###########################################################################

ci_path = "images/"
ci_suffix = ".tiff"

data = pd.read_csv("granecro-cards.csv", sep=";").fillna("")

#st.write("<div style='font-size:12px; '>DEV " + str(st.session_state) + "</div>", unsafe_allow_html=True)
#st.dataframe(data)

##########################################################################

st.logo(ci_path+"ginlogo.png",link="https://bulgur007.itch.io/graduate-in-necromancy")
st.markdown("# Graduate in Necromancy! <span style='font-size:12px'>by <a href='https://bulgur007.itch.io/graduate-in-necromancy'>Bulgur007, read the rules here</a></span>  ", unsafe_allow_html=True)
#st.markdown("by [Bulgur007](https://bulgur007.itch.io/graduate-in-necromancy)")

###########################################################################

MAX_SANITY = 5
MIN_SANITY = -2

###########################################################################
# support functions
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        base64_string = base64.b64encode(img_file.read()).decode('utf-8')
    return base64_string


def check_magic_prerequisities(p):
    if p == "":
        return True # no magic prerequisites
    #return True
    p = p.split(",")

    learned_magic = st.session_state.magic_state.copy()
    checked = []
    for i1 in p:
        for i2 in learned_magic:
            if i1 in i2:
                checked.append(i1)
                learned_magic.remove(i2)
                break

    def magic_to_word(x):
        if x == "W":
            return "light"
        elif x == "B":
            return "dark"
        elif x == "B/W":
            return"dark or light"

    if len(checked) == len(p):
        #st.write("Magic is enough.")
        return True
    else:
        present_magic = st.session_state.magic_state
        if len(present_magic) == 0:
            present_magic = "nothing so far"
        else:
            present_magic = "just "+", ".join([magic_to_word(x) for x in present_magic])

        st.write(f"You don't have magic prerequisites, it needs "
                 f"{', '.join([magic_to_word(x) for x in p])}. You learned {present_magic}." ) # + str(len(checked)) + str(len(p))
        return False

def check_course_level_prerequisites(l):

    #return True
    if l=="":
        return True
    else:
        if l in st.session_state.course_level_state:
            return True
        else:
            st.write(f"You don't have prerequisite {l}.")
            return False

    # learned_courses = st.session_state.s[1]['courses'] + st.session_state.s[1]['courses']
    # learned_levels = []
    # for c in learned_courses:
    #     #st.write(c)
    #     learned_levels.append(data.loc[c[0]]['level'])
    # if l in learned_levels or l == "":
    #     return True
    # else:
    #     st.write(f"You don't have prerequisite {l}.")
    #     return False

def effect_study_buddy(card_id, study_buddy_order):
    effects = data.loc[card_id]['study_buddy_'+str(study_buddy_order)+'_effect'].split(",")

    for e in effects:
        count = int(e[0])
        etype = e[1]

        if etype == "@":
            st.session_state.sanity += count
        elif etype == "T":
            st.session_state.thesis_state += count
        elif etype == "C":
            st.session_state.credits_state += count


###########################################################################
# UI


def show_playground(context, main_content=False, message = ""):
    #st.write("Playground context: " + context)
    if message!= "":
        st.markdown("<center>"+message, unsafe_allow_html=True)
        st.markdown("", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])

    with col1:
        if "sanity" in st.session_state:
            st.markdown("**Sanity:** " + str(int(st.session_state.sanity)) + "/5 @  ")
        if "thesis_state" in st.session_state:
            st.markdown("**Thesis:** " + str(int(st.session_state.thesis_state))+ "/5  ")
        if "credits_state" in st.session_state:
            st.markdown("**Credits:** " + str(int(st.session_state.credits_state))+ "/45 C")

        if st.session_state.current_semester == 1:
            st.markdown("###### Semester 1")
        else:
            st.markdown("###### Semester 1")

        #st.image(ci_path + "back.png", width=100)
        img_base64 = image_to_base64(ci_path + "back.png")

        if len(st.session_state.s1) == 0:
            image_string = f"<image src='data:image/jpeg;base64,{img_base64}' style='opacity: 0.3;' width='50'/>"
        else:
            image_string = f"<image src='data:image/jpeg;base64,{img_base64}' width='50'/>"

        st.html(image_string)
        st.markdown(f"Cards: {len(st.session_state.s1)}")

        if st.session_state.current_semester == 2:
            st.markdown("###### Semester 2")
        else:
            st.markdown("###### Semester 2")
        #st.image(ci_path + "back.png", width=100)

        if len(st.session_state.s2) == 0 or st.session_state.current_semester == 1:
            image_string = f"<image src='data:image/jpeg;base64,{img_base64}' style='opacity: 0.3;' width='50'/>"
        else:
            image_string = f"<image src='data:image/jpeg;base64,{img_base64}' width='50'/>"

        st.html(image_string)
        if len(st.session_state.s2) == 12:
            st.markdown(f"Cards: {len(st.session_state.s2)} [FULL]")
        else:
            st.markdown(f"Cards: {len(st.session_state.s2)}")

    with col2:
        if main_content:
            main_content()
        else:
            st.html("<div style='height:280px;'></div>")

        if len(st.session_state.s[1]['courses']) > 0:
            s1_col_num  = len(st.session_state.s[1]['courses']) + 1
            col_config = []
            for i in range(s1_col_num):
                if i == 0:
                    col_config.append(1)
                else:
                    col_config.append(20)
            s1_cols = st.columns(col_config)
            s1_cols[0].write("S1")

            for i,item in enumerate(st.session_state.s[1]['courses'],1):
                image = data.loc[item[0]]['image']
                s1_cols[i].image(ci_path + image + ci_suffix, width=150)

                #img_base64 = image_to_base64(ci_path + image + ci_suffix)
                #image_string = f"<image src='data:image/jpeg;base64,{img_base64}' width='150'/>"
                #s1_cols[i].html(image_string)

                if item[1] > 0:
                    image_string = ""
                    for ii in range(0,item[1]):
                        img_base64 = image_to_base64(ci_path+"back.png")
                        image_string += f"<image src='data:image/jpeg;base64,{img_base64}' width='40'/>"
                    s1_cols[i].html(image_string)

        if len(st.session_state.s[2]['courses']) > 0:
            s2_col_num = len(st.session_state.s[2]['courses']) + 1
            col_config = []
            for i in range(s2_col_num):
                if i == 0:
                    col_config.append(1)
                else:
                    col_config.append(20)

            s2_cols = st.columns(col_config)
            s2_cols[0].write("S2")

            for i, item in enumerate(st.session_state.s[2]['courses'],1):
                image = data.loc[item[0]]['image']
                s2_cols[i].image(ci_path + image + ci_suffix, width=150)
                if item[1] > 0:
                    image_string = ""
                    for ii in range(0, item[1]):
                        img_base64 = image_to_base64(ci_path + "back.png")
                        image_string += f"<image src='data:image/jpeg;base64,{img_base64}' width='40'/>"
                    s2_cols[i].html(image_string)


############################################################################
def deal_decks():
    st.session_state.s1 = list(data.sample(12).index)
    st.session_state.s2 = list(data[~data.index.isin(st.session_state.s1)].index)


def reset_game():
    st.session_state.clear()
    st.write("I am resetting game.")
    time.sleep(1)
    st.rerun()


def start_game():
    st.session_state.game_started = True
    st.session_state.current_state = "turn card"
    st.write("Game started! Click 'Turn Card' to begin.")

    deal_decks()
    st.session_state.sanity = 3
    st.session_state.thesis_state = 0
    st.session_state.credits_state = 0
    st.session_state.magic_state = []
    st.session_state.course_level_state = []
    st.session_state.s = {}
    st.session_state.s[1] = {}
    st.session_state.s[1]['courses'] = []

    st.session_state.s[2] = {}
    st.session_state.s[2]['courses'] = []

    st.session_state.current_semester = 1

    # time.sleep(2)
    st.rerun()


def turn_card():
    # st.write("It's time to turn a card!")
    st.session_state.current_state = "use card"

    if len(st.session_state.s1) > 0:
        st.session_state.current_card = st.session_state.s1.pop()
    elif len(st.session_state.s2) > 0:
        st.session_state.current_card = st.session_state.s2.pop()
    else:
        st.session_state.current_state = "end game"


def use_card():
    #st.write("Choose an action for the card:")

    c1use, c2use = st.columns(2)

    with c1use:
        if "current_card" in st.session_state:
            #st.write(f"{st.session_state.current_card}")
            card_image_file = data.loc[st.session_state.current_card]['image']
            st.image(ci_path + card_image_file + ci_suffix, width=200)

            #img_base64 = image_to_base64(ci_path + card_image_file + ci_suffix)
            #image_string = f"<image src='data:image/jpeg;base64,{img_base64}' width='200'>"
            #st.html(image_string)

        else:
            st.write("No card ?")
            st.stop()

    card_details = dict(data.loc[st.session_state.current_card])
    #st.write(card_details)

    actions = []
    # find possible actions
    if (card_details['type'] == "course" and (st.session_state.sanity - card_details['admittance_sanity_price'] >= MIN_SANITY)
            and check_magic_prerequisities(card_details['admittance_magic_prerequisite'])
            and check_course_level_prerequisites(card_details['admittance_course_level_prerequisite'])):
        actions.append('Enroll yourself to the course')
    elif card_details['type'] == "sanity_recovery" and st.session_state.sanity < MAX_SANITY:
        actions.append('Recover sanity point')

    if card_details['type'] == "course" and st.session_state.current_semester == 1 and len(st.session_state.s2) < 12:
        actions.append('Leave for the next semester')

    if len(st.session_state.s[st.session_state.current_semester]['courses']) > 0 and card_details['type']!="tired":
        for item in st.session_state.s[st.session_state.current_semester]['courses']:
            cd = dict(data.loc[item[0]])
            #st.write(cd)
            buddy_slots = 0
            if cd['study_buddy_1_effect'] != "":
                buddy_slots += 1
            if cd['study_buddy_2_effect'] != "":
                buddy_slots += 1
            if buddy_slots > item[1]:
                actions.append(f"Raise Study Buddy for {cd['text']}")

    if st.session_state.thesis_state < 5 and card_details['type'] != "tired":
        actions.append("Work on thesis")

    actions.append("Just discard")

    with c2use:
        action = st.selectbox("Select an action", actions)  # , on_change=st.rerun()
        if st.button("Execute Action"):
            st.write(f"Executing {action}...")
            # Add the logic for each action here
            if action == "Enroll yourself to the course":

                # ad card to semester courses with 0 study buddies
                st.session_state.s[st.session_state.current_semester]['courses'].append(
                    (st.session_state.current_card, 0))
                # change sanity
                st.session_state.sanity += - int(card_details['admittance_sanity_price'])

                # add credits
                st.session_state.credits_state += card_details['credits']

                # add level
                st.session_state.course_level_state.append(card_details['level'])

                # add learned magic
                if card_details['learning_effect'] != "":
                    st.session_state.magic_state.append(card_details['learning_effect'])

                st.write(f"You have enrolled to '{card_details['text']}' for {int(card_details['admittance_sanity_price'])} sanity points!")
                time.sleep(1)
            elif "Raise Study Buddy" in action:
                for_card = action.replace("Raise Study Buddy for ","")
                card_id = data.index[data["text"] == for_card].tolist()[0]

                semester_courses = st.session_state.s[st.session_state.current_semester]['courses'].copy()
                updated_courses = []
                for course in semester_courses:
                    if course[0] == card_id:
                        updated_courses.append((course[0],course[1]+1))
                        study_buddy_order = course[1]+1
                    else:
                        updated_courses.append((course[0], course[1]))

                st.session_state.s[st.session_state.current_semester]['courses'] = updated_courses

                effect_study_buddy(card_id,study_buddy_order)

                st.write(f"Raise 'Study Buddy for card {card_id}' action performed!")
            elif action == "Work on thesis":
                st.session_state.thesis_state += 1
            elif action == "Recover sanity point":
                st.session_state.sanity += 1
            elif action == "Leave for the next semester":
                st.session_state.s2.append(st.session_state.current_card)

            if len(st.session_state.s1) == 0:
                if st.session_state.current_semester == 1:
                    st.session_state.sanity += 3
                st.session_state.current_semester = 2

                if st.session_state.sanity > MAX_SANITY:
                    st.session_state.sanity = MAX_SANITY

                random.shuffle(st.session_state.s2)

            if len(st.session_state.s2) == 0:
                st.session_state.current_state = "end game"
            else:
                st.session_state.current_state = "turn card"


@st.dialog("End")
def end_game():
    if st.session_state.credits_state > 44 and st.session_state.sanity >= 0 and st.session_state.thesis_state > 4:
        st.markdown("## You have won!")
        st.balloons()
    else:
        st.markdown("## You have lost!")
    
        if st.session_state.credits_state < 45:
            st.markdown(f"You got insufficient credits ({st.session_state.credits_state} credits and you need 45)"
        if st.session_state.thesis_state < 5:
            st.markdown(f"Your thesis is not finished")
        if st.session_state.sanity < 0:
            st.markdown(f"You are insane (sanity < 0)")
    st.write("Game over. Thank you for playing!")


def main():
    col1,col2 = st.columns([5,1])
    if col2.button("Reset"):
        reset_game()

    if 'game_started' not in st.session_state:
        st.session_state.game_started = False

    if 'current_state' not in st.session_state or st.session_state.current_state == "":
        st.session_state.current_state = "start game"

    if st.session_state.current_state == "start game":
        if st.button("Start Game"):
            start_game()
    elif st.session_state.current_state == "turn card":
        if st.button("Turn Card"):
            st.write("Turning card ...")
            time.sleep(3)
            
        show_playground("Turn Card", message="It's time to turn a card!")
        turn_card()


    elif st.session_state.current_state == "use card":
        show_playground("Use Card", main_content=use_card, message="Choose action for the card")
        
        if st.session_state.current_state == "turn card":
            st.write("Returning to 'Turn Card' state...")
            time.sleep(1)
            st.rerun()
        elif st.session_state.current_state == "end game":
            end_game()
            #st.rerun()

    elif st.session_state.current_state == "end game":
        end_game()


if __name__ == "__main__":
    main()
