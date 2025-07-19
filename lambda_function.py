# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import csv
import requests
import io
import calendar

import csv
from io import StringIO

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

google_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtpL8ewuV75OIuxt_PW5c4I5HU-I_Z43JIrBw_9jyUUk6xWlWVx9vi4mqmEPyObUut3KWyolWIQ4lB/pub?output=csv"
def load_restaurant_data_from_url(url):
    """
    Fetches the CSV file from the given URL and parses it into a list of dictionaries.
    """
    response = requests.get(url)
    if response.status_code == 200:
        csv_data = StringIO(response.text)  # Use StringIO to read CSV content as a file-like object
        reader = csv.DictReader(csv_data)
        return list(reader)
    else:
        logger.error(f"Failed to retrieve CSV: {response.status_code}")
        return []


restaurants_data = load_restaurant_data_from_url(google_csv_url)

def search_restaurants(cuisine, cost_type, location):
    filtered_restaurants = [
        r for r in restaurants_data
        if (cuisine.lower() in r['cuisine'].lower() and
            cost_type.lower() in r['cost_type'].lower() and
            location.lower() in r['city'].lower())
    ]
    return filtered_restaurants



class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello! Welcome Would you like to now your zodiac sign? or Find out restaurant?"
        reprompt_text = "You can ask 'Show me a average indian restaurant in delhi today' or When were you born?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class FindRestaurantIntentHandler(AbstractRequestHandler):
    """Handler for Find Restaurant Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("FindRestaurantIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        cuisine = slots.get("cuisine").value
        cost_type = slots.get("costType").value
        location = slots.get("location").value
        
        cost_type_slot = slots.get("costType")
        if cost_type_slot.resolutions and cost_type_slot.resolutions.resolutions_per_authority:
            resolved_value = cost_type_slot.resolutions.resolutions_per_authority[0].values[0].value.name
        
        # Failsafe: If no resolved value, use the original value
        if resolved_value:
            cost_type = resolved_value
            logger.info(f"resolved value found. Using resolved_value value: {resolved_value}")
        else:
            logger.info(f"Resolved Value not found Using original vlaue: {cost_type}")
        

        restaurants = search_restaurants(cuisine, resolved_value, location)

        if not restaurants:
            speak_output = f"Sorry, I couldn't find any {cuisine} restaurants in {location} with {resolved_value} pricing."
        else:
            # List the restaurant names for the user
            restaurant_names = ", ".join([r['restaurant_name'] for r in restaurants])
            speak_output = f"I found the following {cuisine} restaurants in {location}: {restaurant_names}. Enjoy!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )



class CaptureZodiacSignIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaptureZodiacSignIntent")(handler_input)

    def filter(self, X):
        date = X.split()
        month = date[0]
        month_as_index = list(calendar.month_abbr).index(month[:3].title())
        day = int(date[1])
        return (month_as_index,day)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        year = slots["year"].value
        month = slots["month"].value
        day = slots["day"].value
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQvr5YePK4pXg0rUOZYEDCh_KMa8gG-E8o7sFjD_Ngww2L2mpXz6Olak7ARSzd9Ng/pub?gid=1494965002&single=true&output=csv"
        response = requests.get(url)
        csv_content = response.content
        row = csv_content.decode('utf-8').splitlines()
        rows = row[1:] # excluding the first row

        zodiac = ''
        month_as_index = list(calendar.month_abbr).index(month[:3].title())
        usr_dob = (month_as_index,int(day))
        for sign in rows:
            start, end , zodiac = sign.split(',')
            if self.filter(start) <= usr_dob <= self.filter(end):
                zodiac = zodiac
                break

        speak_output = 'I see you were born on the {day} of {month} {year}, which means that your zodiac sign will be {zodiac}.'.format(month=month, day=day, year=year, zodiac=zodiac)


        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CaptureZodiacSignIntentHandler())
sb.add_request_handler(FindRestaurantIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()