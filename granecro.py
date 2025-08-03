from typing import Literal
from collections import namedtuple
import base64
import pandas as pd
import random
import streamlit as st
import time


# so the user can't click the execute action button more than once
if 'execute_button' in st.session_state and st.session_state.execute_button == True:
    st.session_state.running = True
else:
    st.session_state.running = False

###########################################################################
Card = namedtuple("Card", ["card_image",
                           "card_type",
                           "card_text",
                           "card_level",
                           "card_admittance_thesis_price",
                           "card_admittance_sanity_price",
                           "card_admittance_course_level_prerequisite",
                           "card_admittance_magic_prerequisite",
                           "card_credits",
                           "card_study_buddy_1_effect",
                           "card_study_buddy_2_effect",
                           "card_learning_effect"])


cards: list[Card] = [
    Card('abyssal_language', 'course', 'Abyssal language', 'C', 0, 1, '', '', 2, '', '', 'B'),
    Card('heraldry_of_the_astrals', 'course', 'Heraldry of the Astrals', 'C', 0, 1, '', '', 2, '', '', ''),
    Card('holy_animals', 'course', 'Holy animals', 'C', 0, 1, '', '', 2, '', '', 'W'),
    Card('history_of_the_void', 'course', 'History of the Void', 'A2', 0, 3, '', '', 10, '2@', '', 'B'),
    Card('advanced_blood_rituals', 'course', 'Advanced blood rituals', 'A', 0, 3, '', '', 10, '1@', '1C,1T,1@', 'B/W'),
    Card('transference_of_life', 'course', 'Transference of life', 'A', 0, 3, '', 'W,W,B,B', 12, '3C', '', 'B/W'),
    Card('speaking_with_the_dead', 'course', 'Speaking with the dead', 'A1', 0, 3, '', '', 10, '2C', '', 'W'),
    Card('soul_mending', 'course', 'Soul mending', 'B', 0, 2, 'A1', '', 5, '2@', '1T,1C', 'W'),
    Card('conjuring_spirit_knights', 'course', 'Conjuring spirit knights', 'B', 0, 2, '', 'W', 5, '2C', '', 'W'),
    Card('poison_brewing', 'course', 'Poison brewing', 'B', 0, 2, '', 'B', 5, '1C', '1C,1T', 'B'),
    Card('spellbook_writing', 'course', 'Spellbook writing', 'B', 0, 2, '', '', 5, '1C', '1C', ''),
    Card('practice_magic_staffs', 'course', 'Practice: Magic staffs', 'B', 0, 2, '', 'W,B', 5, '1@', '1C,1@', 'B/W'),
    Card('invoking_shadowspawns', 'course', 'Invoking shadowspawns', 'B', 0, 2, 'A2', '', 5, '2@', '1C', 'B'),
    Card('defense_against_curses', 'course', 'Defense against curses', 'B', 0, 2, '', 'B,W,W', 7, '2C', '', 'W'),
    Card('drain_spell_seminar', 'course', 'Drain spells seminar', 'B', 0, 2, '', 'B,B,W', 7, '1C,1T', '', 'B'),
    Card('graveyards_of_the_realm', 'course', 'Graveyards of the realm', 'B', 0, 2, '', '', 5, '1@', '', ''),
    Card('tired', 'tired', 'TIRED', '', 0, '', '', '', '', '', '', ''),
    Card('tired', 'tired', 'TIRED', '', 0, '', '', '', '', '', '', ''),
    Card('sanity_boost', 'sanity_recovery', '@', '', 0, '', '', '', '', '', '', ''),
    Card('sanity_boost', 'sanity_recovery', '@', '', 0, '', '', '', '', '', '', '')
]

expansion_cards: list[Card] = [
    Card('tired', 'tired', 'TIRED', '', 0, '', '', '', '', '', '', ''),
    Card('sigils_of_power', 'course', 'Sigils of power', 'W', 1, 1, '', '', 3, '2@', '', ''),
    Card('banishing_the_undead', 'course', 'Banishing the undead', 'W', 1, 1, '', '', 3, '2C', '', 'W'),
    Card('dream_invasion', 'course', 'Dream invasion', 'W', 1, 1, '', '', 3, '2C', '', 'B'),

]

ci_path = "img/"
ci_suffix = ".png"

# for debugging purposes
# st.write("<div style='font-size:12px; '>DEV " + str(st.session_state) + "</div>", unsafe_allow_html=True)
# st.dataframe(data)

st.logo(ci_path+"ginlogo.png",link="https://bulgur007.itch.io/graduate-in-necromancy")
# st.html("<span style='font-size:36px'>Graduate in Necromancy! </span><span style='font-size:12px'>by <a href='https://bulgur007.itch.io/graduate-in-necromancy'>Bulgur007, read the rules here</a></span>")
st.markdown("# Graduate in Necromancy! <span style='font-size:12px'>by <a href='https://bulgur007.itch.io/graduate-in-necromancy'>Bulgur007, read the rules here</a></span>  ", unsafe_allow_html=True)
# st.markdown("by [Bulgur007](https://bulgur007.itch.io/graduate-in-necromancy)")

MAX_THESIS = 5

MAX_SANITY = 5
MIN_SANITY = -2

POINTS_LEVEL_EASY = 35
POINTS_LEVEL_MEDIUM = 40
POINTS_LEVEL_HARD = 45

###########################################################################

# support functions
def image_to_base64(image_path) -> str:
    with open(image_path, "rb") as img_file:
        base64_string = base64.b64encode(img_file.read()).decode('utf-8')
    return base64_string


def check_thesis_price(p) -> bool:
    if p == 0:
        return True  # no thesis prerequisite
    
    if st.session_state.thesis_state > 1 and st.session_state.thesis_state - int(p) >= 0:
        return True
    
    st.write(f"You don't have the Thesis prerequisite, it needs {p} and you have {st.session_state.thesis_state}")
    return False


def check_magic_prerequisities(p) -> bool:
    if p == "":
        return True  # no magic prerequisites
    p = p.split(",")

    learned_magic = st.session_state.magic_state.copy()
    checked = []
    for i1 in p:
        for i2 in learned_magic:
            if i1 in i2:
                checked.append(i1)
                learned_magic.remove(i2)
                break

    def magic_to_word(x) -> Literal['dark', 'dark or light', 'light'] | None:
        if x == "W":
            return "light"
        elif x == "B":
            return "dark"
        elif x == "B/W":
            return "dark or light"
        return None

    if len(checked) == len(p):
        return True
    else:
        present_magic = st.session_state.magic_state
        if len(present_magic) == 0:
            present_magic = "nothing so far"
        else:
            present_magic = "just, ".join([magic_to_word(x) for x in present_magic])

        st.write(f"You don't have magic prerequisites, it needs "
                 f"{', '.join([magic_to_word(x) for x in p])}. You learned {present_magic}.")
        return False


def check_course_level_prerequisites(l) -> bool:
    if l == "":
        return True
    else:
        if l in st.session_state.course_level_state:
            return True
        else:
            st.write(f"You don't have prerequisite {l}.")
            return False


def effect_study_buddy(card_id, study_buddy_order) -> None:
    effects = st.session_state.data.loc[card_id]['study_buddy_'+str(study_buddy_order)+'_effect'].split(",")

    for e in effects:
        count = int(e[0])
        etype = e[1]

        if etype == "@":
            st.session_state.sanity += count
        elif etype == "T":
            if st.session_state.thesis_state + count < 5:
                st.session_state.thesis_state += count
            else:
                st.session_state.thesis_state = 5
        elif etype == "C":
            st.session_state.credits_state += count

###########################################################################

# UI
def show_playground(message="", main_content=None) -> None:
    if message != "":
        st.markdown("<center>"+message+"</center>", unsafe_allow_html=True)
        st.markdown("", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])

    with col1:
        if "sanity" in st.session_state:
            st.markdown(f"**Sanity:** {str(int(st.session_state.sanity))} / {MAX_SANITY}")
        if "thesis_state" in st.session_state:
            st.markdown(f"**Thesis:** {str(int(st.session_state.thesis_state))} / {MAX_THESIS}")
        if "credits_state" in st.session_state:
            st.markdown(f"**Credits:**  {str(int(st.session_state.credits_state))} / {st.session_state.difficulty}")

        st.markdown("###### Semester 1")
        img_base64 = image_to_base64(ci_path + "back.png")
        if len(st.session_state.s1) == 0:
            image_string = f"<image src='data:image/jpeg;base64,{img_base64}' style='opacity: 0.3;' width='50'/>"
        else:
            image_string = f"<image src='data:image/jpeg;base64,{img_base64}' width='50'/>"
        st.html(image_string)
        st.markdown(f"Cards: {len(st.session_state.s1)}")

        st.markdown("###### Semester 2")
        if len(st.session_state.s2) == 0 or st.session_state.current_semester == 1:
            image_string = f"<image src='data:image/jpeg;base64,{img_base64}' style='opacity: 0.3;' width='50'/>"
        else:
            image_string = f"<image src='data:image/jpeg;base64,{img_base64}' width='50'/>"
        st.html(image_string)
        if len(st.session_state.s2) == 12 and not st.session_state.use_expansion:
            st.markdown(f"Cards: {len(st.session_state.s2)} [FULL]")
        elif len(st.session_state.s2) == 14 and st.session_state.use_expansion:
            st.markdown(f"Cards: {len(st.session_state.s2)} [FULL]")
        else:
            st.markdown(f"Cards: {len(st.session_state.s2)}")

    with col2:
        if main_content:
            main_content()
        else:
            st.html("<div style='height:280px;'></div>")

        if len(st.session_state.s[1]['courses']) > 0:
            s1_col_num = len(st.session_state.s[1]['courses']) + 1
            col_config = []
            for i in range(s1_col_num):
                if i == 0:
                    col_config.append(1)
                else:
                    col_config.append(20)
            s1_cols = st.columns(col_config)
            s1_cols[0].write("S1")

            for i, item in enumerate(st.session_state.s[1]['courses'], 1):
                image = st.session_state.data.loc[item[0]]['card_image']
                s1_cols[i].image(ci_path + image + ci_suffix, width=150)

                if item[1] > 0:
                    image_string = ""
                    for ii in range(0, item[1]):
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

            for i, item in enumerate(st.session_state.s[2]['courses'], 1):
                image = st.session_state.data.loc[item[0]]['card_image']
                s2_cols[i].image(ci_path + image + ci_suffix, width=150)
                if item[1] > 0:
                    image_string = ""
                    for ii in range(0, item[1]):
                        img_base64 = image_to_base64(ci_path + "back.png")
                        image_string += f"<image src='data:image/jpeg;base64,{img_base64}' width='40'/>"
                    s2_cols[i].html(image_string)

############################################################################

def deal_decks() -> None:
    if st.session_state.use_expansion:
        st.session_state.s1 = list(st.session_state.data.sample(14).index)
    else:
        st.session_state.s1 = list(st.session_state.data.sample(12).index)

    st.session_state.s2 = list(st.session_state.data[~st.session_state.data.index.isin(st.session_state.s1)].index)


def reset_game() -> None:
    st.session_state.clear()
    st.write("Resetting the game...")
    time.sleep(2)
    st.rerun()


def start_game() -> None:
    st.session_state.game_started = True
    st.session_state.current_state = "turn card"
    
    game_cards = cards.copy()
    if st.session_state.get("use_expansion"):
        game_cards.extend(expansion_cards)

    st.session_state.data = pd.DataFrame(game_cards)
    st.session_state.data = st.session_state.data.rename(columns={
        'card_type': 'type',
        'card_text': 'text',
        'card_level': 'level',
        'card_admittance_thesis_price': 'admittance_thesis_price',
        'card_admittance_sanity_price': 'admittance_sanity_price',
        'card_admittance_course_level_prerequisite': 'admittance_course_level_prerequisite',
        'card_admittance_magic_prerequisite': 'admittance_magic_prerequisite',
        'card_credits': 'credits',
        'card_study_buddy_1_effect': 'study_buddy_1_effect',
        'card_study_buddy_2_effect': 'study_buddy_2_effect',
        'card_learning_effect': 'learning_effect'
    })
    
    deal_decks()

    st.write("Game started! Click 'Turn Card' to begin.")

    st.session_state.current_semester = 1
    st.session_state.sanity = 3
    st.session_state.thesis_state = 0
    st.session_state.credits_state = 0
    st.session_state.magic_state = []
    st.session_state.course_level_state = []
    st.session_state.s = {
        1: {'courses': []},
        2: {'courses': []},
    }
    st.rerun()


def turn_card() -> None:
    st.session_state.current_state = "use card"

    if len(st.session_state.s1) > 0:
        st.session_state.current_card = st.session_state.s1.pop()
    elif len(st.session_state.s2) > 0:
        st.session_state.current_card = st.session_state.s2.pop()
    else:
        st.session_state.current_state = "end game"


def use_card() -> None:
    c1use, c2use = st.columns(2)

    with c1use:
        if "current_card" in st.session_state:
            card_image_file = st.session_state.data.loc[st.session_state.current_card]['card_image']
            st.image(ci_path + card_image_file + ci_suffix, width=200)
        else:
            st.write("No card ?")
            st.stop()

    card_details = dict(st.session_state.data.loc[st.session_state.current_card])

    actions = []
    # find possible actions
    if (card_details['type'] == "sanity_recovery"
            and st.session_state.sanity < MAX_SANITY):
        actions.append('Recover sanity point')

    if (card_details['type'] == "course"
            and (st.session_state.sanity - card_details['admittance_sanity_price'] >= MIN_SANITY)
            and check_magic_prerequisities(card_details['admittance_magic_prerequisite'])
            and check_thesis_price(card_details['admittance_thesis_price'])
            and check_course_level_prerequisites(card_details['admittance_course_level_prerequisite'])):
        actions.append('Enroll yourself to the course')

    if st.session_state.use_expansion:
        if (card_details['type'] == "course"
                and st.session_state.current_semester == 1
                and len(st.session_state.s2) < 14):
            actions.append('Leave for the next semester')
    else:
        if (card_details['type'] == "course"
                and st.session_state.current_semester == 1
                and len(st.session_state.s2) < 12):
            actions.append('Leave for the next semester')

    if len(st.session_state.s[st.session_state.current_semester]['courses']) > 0:
        for item in st.session_state.s[st.session_state.current_semester]['courses']:
            cd = dict(st.session_state.data.loc[item[0]])
            buddy_slots = 0
            if cd['study_buddy_1_effect'] != "":
                buddy_slots += 1
            if cd['study_buddy_2_effect'] != "":
                buddy_slots += 1
            if buddy_slots > item[1]:
                if cd['level'] == 'W' and card_details['type'] == 'tired':
                    actions.append(f"Raise Study Buddy for {cd['text']}")
                elif cd['level'] != 'W' and card_details['type'] != 'tired':
                    actions.append(f"Raise Study Buddy for {cd['text']}")

    if st.session_state.thesis_state < 5 and card_details['type'] != "tired":
        actions.append("Work on thesis")

    actions.append("Just discard")

    with c2use:
        action = st.selectbox("Select an action", actions)
        if st.button("Execute Action", disabled=st.session_state.get("running", False), key="execute_button"):
            st.write(f"Executing {action}...")
            # Add the logic for each action here
            if action == "Enroll yourself to the course":
                # add card to semester courses with 0 study buddies
                st.session_state.s[st.session_state.current_semester]['courses'].append(
                    (st.session_state.current_card, 0))
                # change sanity
                st.session_state.sanity += - int(card_details['admittance_sanity_price'])
                # add credits
                st.session_state.credits_state += card_details['credits']
                # add level
                st.session_state.course_level_state.append(card_details['level'])
                # subtract thesis (if needed):
                st.session_state.thesis_state -= int(card_details['admittance_thesis_price'])

                # add learned magic
                if card_details['learning_effect'] != "":
                    st.session_state.magic_state.append(card_details['learning_effect'])

                st.write(f"You have enrolled to '{card_details['text']}' for {int(card_details['admittance_sanity_price'])} sanity points!")
                time.sleep(2)
            elif "Raise Study Buddy" in action:
                for_card = action.replace("Raise Study Buddy for ", "")
                card_id = st.session_state.data.index[st.session_state.data["text"] == for_card].tolist()[0]

                semester_courses = st.session_state.s[st.session_state.current_semester]['courses'].copy()
                updated_courses = []
                for course in semester_courses:
                    if course[0] == card_id:
                        updated_courses.append((course[0], course[1]+1))
                        study_buddy_order = course[1]+1
                    else:
                        updated_courses.append((course[0], course[1]))

                st.session_state.s[st.session_state.current_semester]['courses'] = updated_courses

                effect_study_buddy(card_id, study_buddy_order)

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
                turn_card()
                st.rerun()
                # st.session_state.current_state = "turn card"


@st.dialog("End")
def end_game() -> None:
    if (st.session_state.credits_state >= st.session_state.difficulty
            and st.session_state.sanity >= 0
            and st.session_state.thesis_state == 5):
        st.markdown("## You have won!")
        st.balloons()
    else:
        st.markdown("## You have lost!")
    
        if st.session_state.credits_state < st.session_state.difficulty:
            st.markdown(f"You got insufficient credits ({int(st.session_state.credits_state)} credits and you need {int(st.session_state.difficulty)})")
        if st.session_state.thesis_state < 5:
            st.markdown(f"Your thesis is not finished")
        if st.session_state.sanity < 0:
            st.markdown(f"You are insane (sanity < 0)")
    st.write("Game over. Thank you for playing!")


def main() -> None:
    col1, col2, col3 = st.columns(3)

    action = None
    points_map = {}

    if not st.session_state.get("game_started", False):
        with col2:
            st.checkbox("Use expansion?", key="expansion")

            if st.session_state.get("expansion"):
                difficulties = ["Hard (52 points)", "Medium (50 points)", "Easy (45 points)"]
                points_map = {
                    "Hard (52 points)": 52,
                    "Medium (50 points)": 50,
                    "Easy (45 points)": 45
                }
                st.session_state.use_expansion = True
            else:
                difficulties = ["Hard (45 points)", "Medium (40 points)", "Easy (35 points)"]
                points_map = {
                    "Hard (45 points)": POINTS_LEVEL_HARD,
                    "Medium (40 points)": POINTS_LEVEL_MEDIUM,
                    "Easy (35 points)": POINTS_LEVEL_EASY
                }
                st.session_state.use_expansion = False
            action = st.selectbox("Difficulty", difficulties)

    if col3.button("Reset", key="Reset"):
        reset_game()

    if 'game_started' not in st.session_state:
        st.session_state.game_started = False

    if 'current_state' not in st.session_state or st.session_state.current_state == "":
        st.session_state.current_state = "start game"

    if st.session_state.current_state == "start game":
        if col1.button("Start Game"):
            st.session_state.difficulty = points_map[action]
            start_game()
    elif st.session_state.current_state == "turn card":
        if st.button("Turn Card"):
            st.write("Turning card ...")
            time.sleep(3)

        show_playground(message="It's time to turn a card!")
        turn_card()
    elif st.session_state.current_state == "use card":
        show_playground(message="Choose action for the card", main_content=use_card)

        if st.session_state.current_state == "end game":
            end_game()
    elif st.session_state.current_state == "end game":
        end_game()


if __name__ == "__main__":
    main()
