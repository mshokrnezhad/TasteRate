from typing import Dict, List
from autogen import ConversableAgent
import sys
import os


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
    # TODO
    # This function takes in a restaurant name, a list of food scores from 1-5, and a list of customer service scores from 1-5
    # The output should be a score between 0 and 10, which is computed as the following:
    # SUM(sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * sqrt(125)) * 10
    # The above formula is a geometric mean of the scores, which penalizes food quality more than customer service.
    # Example:
    # > calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    # {"Applebee's": 5.048}
    # NOTE: be sure to that the score includes AT LEAST 3  decimal places. The public tests will only read scores that have
    # at least 3 decimal places.
    pass


def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    # TODO
    # It may help to organize messages/prompts within a function which returns a string.
    # For example, you could use this function to return a prompt for the data fetch agent
    # to use to fetch reviews for a specific restaurant.
    pass


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

# Do not modify the signature of the "main" function.


def main(user_query: str):
    entrypoint_system_message = "You are a food critic. You get my query with the name of a resturant and provide accurate and insightful reviews about that restaurant."
    assistant_system_message = "You are an assistant willing to help precisely."
    analyzer_system_message = "You are an analysis expert tasked with providing accurate, detailed assessments based on specified guidelines."

    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

    # the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent", system_message=entrypoint_system_message, llm_config=llm_config)

    # the assistant agent parsing the quesy to extract the resturant name
    assistant_agent = ConversableAgent("assistant_agent", system_message=assistant_system_message, llm_config=llm_config)
    assistant_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)

    analyzer_agent = ConversableAgent("analyzer_agent", system_message=analyzer_system_message, llm_config=llm_config)

    # extracting the resturant name
    result = entrypoint_agent.initiate_chat(
        assistant_agent,
        message=f"Return the arguments of the function based on this query: {user_query}. Do not add any markdown.",
        summary_method="last_msg",
        max_turns=1
    )
    resturant_name = extract_function_arguments(result).get("restaurant_name")

    # retriving reviews based on the extracted resturant name
    reviews = fetch_restaurant_data(resturant_name).get(resturant_name)
    # temp_reviews = [reviews[0]]

    result = entrypoint_agent.initiate_chat(
        analyzer_agent,
        message=get_review_analyzer_prompt(reviews),
        summary_method="last_msg",
        max_turns=1,
    )


# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])
