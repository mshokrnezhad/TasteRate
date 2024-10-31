from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
import json
import math
from dotenv import load_dotenv
load_dotenv()  # This loads environment variables from .env


def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    # Read the reviews from a file named restaurant-data.txt
    restaurant_reviews = {}

    # Assuming restaurant-data.txt is in the format:
    # RestaurantName. Review
    with open("restaurant-data.txt", "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                name, review = line.split(". ", 1)
                name = name.strip()
                review = review.strip()
                if name not in restaurant_reviews:
                    restaurant_reviews[name] = []
                restaurant_reviews[name].append(review)
            except ValueError:
                continue  # Skip any line that doesn't match the expected format

    # Search for reviews for the specified restaurant name
    reviews = []
    for key in restaurant_reviews.keys():
        if restaurant_name.lower() in key.lower():
            reviews.extend(restaurant_reviews[key])

    return {restaurant_name: reviews} if reviews else {restaurant_name: ["No reviews found for this restaurant."]}


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    # Check if the lists are empty or have different lengths
    if not food_scores or not customer_service_scores or len(food_scores) != len(customer_service_scores):
        return {restaurant_name: 0.0}

    # Number of reviews
    N = len(food_scores)
    total_score = 0.0

    # Calculate the weighted geometric mean score
    for food_score, service_score in zip(food_scores, customer_service_scores):
        total_score += math.sqrt(food_score ** 2 * service_score)

    # Final overall score calculation
    overall_score = (total_score / (N * math.sqrt(125))) * 10
    overall_score = round(overall_score, 3)  # Ensure at least 3 decimal places

    return {restaurant_name: overall_score}


def extract_function_arguments(chat_result):
    # Check if the chat_result and chat_history exist
    if chat_result and chat_result.chat_history:
        # Iterate through the chat history
        for message in chat_result.chat_history:
            # Look for tool calls in the message
            if "tool_calls" in message:
                for tool_call in message["tool_calls"]:
                    # Find the specific function call for "fetch_restaurant_data"
                    if tool_call["function"]["name"] == "fetch_restaurant_data":
                        # Extract and parse the arguments
                        arguments = tool_call["function"]["arguments"]
                        return eval(arguments)
    return None


def get_review_analyzer_prompt(reviews: List[str]) -> str:
    prompt = (
        "Analyze the following restaurant reviews and extract two scores for each review:\n"
        "1. food_score (1-5)\n"
        "2. customer_service_score (1-5)\n\n"
        "Use the following adjective mappings to determine the scores:\n"
        "- Score 1: awful, horrible, disgusting\n"
        "- Score 2: bad, unpleasant, offensive\n"
        "- Score 3: average, uninspiring, forgettable\n"
        "- Score 4: good, enjoyable, satisfying\n"
        "- Score 5: awesome, incredible, amazing\n\n"
        "Each review contains exactly two adjectives, one for food and one for customer service.\n\n"
        "Provide the results in the following JSON format without adding any markdown:\n"
        "{\n"
        "  \"reviews\": [\n"
        "    {\n"
        "      \"food_score\": <int>,\n"
        "      \"customer_service_score\": <int>\n"
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}"
    )
    # Append the reviews
    for review in reviews:
        prompt += f"\n- \"{review}\""
    return prompt


def extract_scores(reviews_data: Dict) -> [List[int], List[int]]:  # type: ignore
    # Initialize empty lists for scores
    food_scores = []
    customer_service_scores = []

    # Iterate through each review and extract scores
    for review in reviews_data.get("reviews", []):
        food_scores.append(review.get("food_score", 0))
        customer_service_scores.append(review.get("customer_service_score", 0))

    return food_scores, customer_service_scores


def main(user_query: str):
    entrypoint_system_message = "You are a supervisor wiolling to controll a chat process."
    assistant_system_message = "You are a food adict knowing the full name of every resturant."
    analyzer_system_message = "You are an analysis expert tasked with providing accurate, detailed assessments based on specified guidelines."

    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.getenv("OPENAI_API_KEY")}]}

    # the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent", system_message=entrypoint_system_message, llm_config=llm_config)
    entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    # the assistant agent parsing the quesy to extract the resturant name
    assistant_agent = ConversableAgent("assistant_agent", system_message=assistant_system_message, llm_config=llm_config)
    assistant_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)

    analyzer_agent = ConversableAgent("analyzer_agent", system_message=analyzer_system_message, llm_config=llm_config)

    print(user_query)

    # extracting the resturant name
    result = entrypoint_agent.initiate_chat(
        assistant_agent,
        message=f"{user_query} Do not add any markdown. Do not add any word to the name mentioned in the query but correct the mentioned name if any charachter is missed.",
        summary_method="last_msg",
        max_turns=1
    )
    resturant_name = extract_function_arguments(result).get("restaurant_name")

    # retriving reviews based on the extracted resturant name
    reviews = fetch_restaurant_data(resturant_name).get(resturant_name)
    # temp_reviews = [reviews[0]]

    # extracting scores
    result = entrypoint_agent.initiate_chat(
        analyzer_agent,
        message=get_review_analyzer_prompt(reviews),
        summary_method="last_msg",
        max_turns=1,
    )
    analyzed_results = json.loads(result.chat_history[1]["content"])
    food_scores, customer_service_scores = extract_scores(analyzed_results)

    # calculating the overal score
    score = calculate_overall_score(resturant_name, food_scores, customer_service_scores)

    print(score)


if __name__ == "__main__":
    main("What is the overall score for In N Out?")
    # "What is the overall score for taco bell?"
    # "What is the overall score for In N Out?"
    # "How good is the restaurant Chick-fil-A overall?"
    # "What is the overall score for Krispy Kreme?"
