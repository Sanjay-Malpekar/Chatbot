from typing import Any, Text, Dict, List, Union
#from dotenv import load_dotenv


from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType

import requests

import firebase_admin
from firebase_admin import db
from firebase_admin import firestore

cred_obj = firebase_admin.credentials.Certificate('Firebasekey.json')
default_app = firebase_admin.initialize_app(cred_obj,{'databaseURL':'https://rasa-78cd0-default-rtdb.firebaseio.com/'})
ref = db.reference('/')
ref_firestore = firestore.client()


user_id = "A8UXKPR88WG8P"

# import json
# import os

#load_dotenv()

# airtable_api_key = "keygndbwgYAXGKCM0"#os.getenv("AIRTABLE_API_KEY")
# base_id = "appK9sTQeYGRttlxy"#os.getenv("BASE_ID")
# table_name = "Table%201"#os.getenv("TABLE_NAME")


# def create_health_log(confirm_exercise, exercise, sleep, diet, stress, goal):
#     request_url = f"https://api.airtable.com/v0/{base_id}/{table_name}?api_key={airtable_api_key}"

#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#         "Authorization": f"Bearer {airtable_api_key}",
#     }
#     data = {
#         "fields": {
#             "Exercised?": confirm_exercise,
#             "Type of exercise": exercise,
#             "Amount of sleep": sleep,
#             "Stress": stress,
#             "Diet": diet,
#             "Goal": goal,
#         }
#     }
#     try:
#         response = requests.post(
#             request_url, headers=headers, data=json.dumps(data)
#         )
#         response.raise_for_status()
#     except requests.exceptions.HTTPError as err:
#         raise SystemExit(err)

#     print(response.status_code)
#     return response


# class ValidateHealthForm(Action):

#     def name(self) -> Text:
#         return "health_form"

#     def run(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> List[EventType]:
#         requried_slots = ["confirm_exercise", "exercise",
#                           "sleep", "stress", "diet", "goal","option_select","address","payment_options"]

#         for slot_name in requried_slots:
#             if tracker.slots.get(slot_name) is None:
#                 return[SlotSet("requested_slot", slot_name)]

#         return[SlotSet("requested_slot", "None")]


# class ActionSubmit(Action):

#     def name(self) -> Text:
#         return "action_submit"

#     def run(
#         self,
#         dispatcher,
#         tracker: Tracker,
#         domain: "DomainDict"
#     ) -> List[Dict[Text, Any]]:

#         confirm_exercise = tracker.get_slot("confirm_exercise")
#         exercise = tracker.get_slot("exercise")
#         sleep = tracker.get_slot("sleep")
#         stress = tracker.get_slot("stress")
#         diet = tracker.get_slot("diet")
#         goal = tracker.get_slot("goal")
        

#         response = create_health_log(
#             confirm_exercise=confirm_exercise,
#             exercise=exercise,
#             sleep=sleep,
#             stress=stress,
#             diet=diet,
#             goal=goal
#         )

#         dispatcher.utter_message(
#             text="Thanks, your answers have been recorded!")
#         return []
def retrieve_data(Category):
    
    for i in range(3):
        cat = 'Sub_Category' + '/' + str(i)
        result = ref.child('Products').order_by_child(cat).equal_to(Category).limit_to_first(5).get()
        if result is not None:
            return list(result.values())

def retrieve_data_from_recommender_api(userid):
    recommended_products = requests.get("https://5000-amethyst-cheetah-xx8wdzkp.ws-us04.gitpod.io/{userid}")
    

    return recommended_products.json()['Recommended_Products'][:5]

class ActionRecommender(Action):

    def name(self) -> Text:
        return "action_recommend_products"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict"
    ) -> List[Dict[Text, Any]]:
        
        # user_id = "A8UXKPR88WG8P"
        #Checking if the user is new 
        users = ref_firestore.collection('User').where('user_id','==',user_id).stream()
        
        if len([user.id for user in users]) > 0:
            recommend_products = retrieve_data_from_recommender_api(user_id)

            recommend_products_list =[]
            for product in recommend_products:
                refer = 'Products' + '/' + str(product)
                result = ref.child(refer).get()
                recommend_products_list.append(result)
            
            for i in range(len(recommend_products_list)):
                dispatcher.utter_message(
                    text ="Product Title: {}".format(recommend_products_list[i]['title']),
                    image = recommend_products_list[i]['image'][0]
                    )
            dispatcher.utter_message(text="If you liked the products type 1..5 according to the product you want! ;)")
        else:
            
            dispatcher.utter_message(text = "You seems a new User So, Here goes our Top 5 products! ;)")
            
            Popular_products = ['B000VRMV1I','B000U6H08O','B000PGJ3IE','B000P4M1F8','B000EHTY0Q']
 
            recommend_products_list =[]
            for product in Popular_products:
                refer = 'Products' + '/' + str(product)
                result = ref.child(refer).get()
                recommend_products_list.append(result)
            
            for i in range(len(recommend_products_list)):
                dispatcher.utter_message(
                    text ="Product Title: {}".format(recommend_products_list[i]['title']),
                    image = recommend_products_list[i]['image'][0]
                    )
            dispatcher.utter_message(text="If you liked the products type 1..5 according to the product you want! ;)")
        
            
        return[SlotSet("products_list", recommend_products_list)]

class ActionSearchProvider(Action):

    def name(self) -> Text:
        return "action_search_products"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict"
    ) -> List[Dict[Text, Any]]:
       
        Category = tracker.get_slot("category_type")

        products = retrieve_data(Category)

        if products is None:
            dispatcher.utter_message(
                text = "Sorry But we are not able to find Products related to the your Category :(!"
                )
        else:
            for i in range(len(products)):
                dispatcher.utter_message(
                    text ="Product Title: {}".format(products[i]['title']),
                    image = products[i]['image'][0]
                    )
            dispatcher.utter_message(text="If you liked the products type 1..5 according to the product you want! ;)")
        return[SlotSet("products_list", products)]



class ActionLookupAddress(Action):

    def name(self) -> Text:
        return "action_address_lookup"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict"
    ) -> List[Dict[Text, Any]]:
        
        # user_id = "A8UXKPR88WG8P"
        #Checking if the user is new 
        users = ref_firestore.collection('User').where('user_id','==',user_id).stream()

        if len([user.id for user in users]) > 0:
            address_list = ref_firestore.collection(u'User').document(user_id).collection(u'address').limit(2).stream()
            
            address = []
            for addr in address_list:
                address.append(addr.to_dict())

            if len(address) == 0:
                dispatcher.utter_message(text="We could not Found address? Can you please help us with the address here!")
                return[]
            else:
                if len(address) == 1:
                    dispatcher.utter_message(
                        text="Here is your lastest address we found please pick one!",
                        buttons = [{'title': address[0]['address'], 'payload': '/address_found'}])
            
                elif len(address) == 2:
                    dispatcher.utter_message(
                        text="Here is your lastest address we found please pick one!",
                        buttons = [{'title': address[0]['address'], 'payload': '/address_found'},{'title': address[1]['address'], 'payload': '/address_found'}])
                
                return[SlotSet("address", address[0]['address'])]
        else:
            dispatcher.utter_message(text="We could not Found address? Can you please help us with the address here!")
            return[]

class ActionAddAddress(Action):

    def name(self) -> Text:
        return "action_add_address"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict"
    ) -> List[Dict[Text, Any]]:

        current_address = tracker.latest_message['text']

        # user_id = "A8UXKPR88WG8P"
        ref_firestore.collection(u'User').document(user_id).set({u'user_id': user_id})
        ref_firestore.collection(u'User').document(user_id).collection(u'address').document().set({u'address': current_address})
        
        dispatcher.utter_message(
           text="Your Address has been added Successfully!")
        return[SlotSet("address", current_address)]
    
class ActionPlaceOrder(Action):

    def name(self) -> Text:
        return "action_order_placed"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict"
    ) -> List[Dict[Text, Any]]:

        # user_id = "A8UXKPR88WG8P"

        address_selected = tracker.get_slot("address")

        Payment_selected = tracker.get_slot("payment_type")

        option_selected = tracker.get_slot('option_select')

        product = tracker.get_slot('products_list')

        dict_data = {'ProdID': product[int(option_selected)-1]['ProdID'],
        'payment_type': Payment_selected,
        'brand': product[int(option_selected)-1]['brand'],
        'address': address_selected,
        'image': product[int(option_selected)-1]['image'],
        'price': product[int(option_selected)-1]['price'],
        'rating': product[int(option_selected)-1]['rating'],
        'title': product[int(option_selected)-1]['title']}

        ref_firestore.collection(u'User').document(user_id).set({u'user_id': user_id})
        ref_firestore.collection(u'User').document(user_id).collection(u'cart').document().set(dict_data)

        dispatcher.utter_message(text="Your Order has been Placed! Thank You :)")
        
        return []
