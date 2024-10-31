
from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
import json
import math
from dotenv import load_dotenv

# Load environment variables from a .env file (e.g., for API keys)
load_dotenv()


def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:  # Function to fetch restaurant reviews from a data file
    # Dictionary to store restaurant reviews
    restaurant_reviews = {}

    # Open and read the restaurant-data.txt file, assuming each line contains: RestaurantName.
    with open("restaurant-data.txt", "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            try:
                # Split each line into restaurant name and review
                name, review = line.split(". ", 1)
                name = name.strip()
                review = review.strip()
                # Store review in the dictionary under the corresponding restaurant name
                if name not in restaurant_reviews:
                    restaurant_reviews[name] = []
                restaurant_reviews[name].append(review)
            except ValueError:
                # Skip lines that do not match the expected format
                continue

    # Find reviews for the specified restaurant (case insensitive search)
    reviews = []
    for key in restaurant_reviews.keys():
        if restaurant_name.lower() in key.lower():
            reviews.extend(restaurant_reviews[key])

    # Return the reviews if found, otherwise return a "No reviews found" message
    return {restaurant_name: reviews} if reviews else {restaurant_name: ["No reviews found for this restaurant."]}


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:  # Function to calculate the overall score of a restaurant
    # Check if the lists are empty or if they have different lengths
    if not food_scores or not customer_service_scores or len(food_scores) != len(customer_service_scores):
        return {restaurant_name: 0.0}

    # Number of reviews
    N = len(food_scores)
    total_score = 0.0

    # Calculate the geometric mean score (penalizing food quality more than service quality)
    for food_score, service_score in zip(food_scores, customer_service_scores):
        total_score += math.sqrt(food_score ** 2 * service_score)

    # Calculate the final overall score, ensure it has at least 3 decimal places
    overall_score = (total_score / (N * math.sqrt(125))) * 10
    overall_score = round(overall_score, 3)

    return {restaurant_name: overall_score}


def extract_function_arguments(chat_result):  # Function to extract arguments for a function call from a chat result
    # Check if chat_result and chat_history exist
    if chat_result and chat_result.chat_history:
        # Iterate through chat history messages
        for message in chat_result.chat_history:
            # Look for tool calls in the message
            if "tool_calls" in message:
                for tool_call in message["tool_calls"]:
                    # If the function is "fetch_restaurant_data", extract its arguments
                    if tool_call["function"]["name"] == "fetch_restaurant_data":
                        arguments = tool_call["function"]["arguments"]
                        return eval(arguments)
    return None


def get_review_analyzer_prompt(reviews: List[str]) -> str:  # Function to generate a prompt for the review analyzer
    # Define the prompt for the review analyzer to extract food and service scores from reviews
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


def extract_scores(reviews_data: Dict) -> [List[int], List[int]]:  # type: ignore # Function to extract scores from the review analysis
    # Initialize lists to store food and service scores
    food_scores = []
    customer_service_scores = []

    # Extract scores for each review
    for review in reviews_data.get("reviews", []):
        food_scores.append(review.get("food_score", 0))
        customer_service_scores.append(review.get("customer_service_score", 0))

    return food_scores, customer_service_scores


def main(user_query: str):  # Main function to process the user query and calculate the overall score for a restaurant
    # Define system messages for each agent
    entrypoint_system_message = "You are a supervisor willing to control a chat process."
    assistant_system_message = "You are a food addict knowing the full name of every restaurant."
    analyzer_system_message = "You are an analysis expert tasked with providing accurate, detailed assessments based on specified guidelines."

    # Load LLM configuration with OpenAI API key
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.getenv("OPENAI_API_KEY")}]}

    # Initialize the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent", system_message=entrypoint_system_message, llm_config=llm_config)
    entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    # Initialize the assistant agent responsible for extracting the restaurant name
    assistant_agent = ConversableAgent("assistant_agent", system_message=assistant_system_message, llm_config=llm_config)
    assistant_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)

    # Initialize the analyzer agent responsible for analyzing reviews
    analyzer_agent = ConversableAgent("analyzer_agent", system_message=analyzer_system_message, llm_config=llm_config)

    # Step 1: Extract the restaurant name from the user query
    result = entrypoint_agent.initiate_chat(
        assistant_agent,
        message=f"{user_query} Do not add any markdown. Do not add any word to the name mentioned in the query but correct the mentioned name if any character is missed.",
        summary_method="last_msg",
        max_turns=1
    )
    # Extract the restaurant name from the function arguments
    restaurant_name = extract_function_arguments(result).get("restaurant_name")

    # Step 2: Retrieve reviews for the extracted restaurant name
    reviews = fetch_restaurant_data(restaurant_name).get(restaurant_name)

    # Step 3: Analyze the reviews to extract food and service scores
    result = entrypoint_agent.initiate_chat(
        analyzer_agent,
        message=get_review_analyzer_prompt(reviews),
        summary_method="last_msg",
        max_turns=1,
    )
    # Parse the analyzed results to extract scores
    analyzed_results = json.loads(result.chat_history[1]["content"])
    food_scores, customer_service_scores = extract_scores(analyzed_results)

    # Step 4: Calculate the overall score based on the extracted scores
    score = calculate_overall_score(restaurant_name, food_scores, customer_service_scores)

    # Print the overall score for the restaurant
    print(score)


# Run the main function if the script is executed directly
if __name__ == "__main__":
    main("What is the overall score for In N Out?")
    # Example queries:
    # "What is the overall score for taco bell?"
    # "How good is the restaurant Chick-fil-A overall?"
    # "What is the overall score for Krispy Kreme?"
