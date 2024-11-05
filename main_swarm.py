from swarm import Swarm, Agent
from dotenv import load_dotenv

# Load environment variables from a .env file (e.g., for API keys)
load_dotenv()

# Initialize the Swarm client
client = Swarm()

names = (
    '1. "McDonald\'s",\n'
    '2. "Subway",\n'
    '3. "Taco Bell",\n'
    '4. "Chick-fil-A",\n'
    '5. "Applebee\'s",\n'
    '6. "Olive Garden",\n'
    '7. "Cheesecake Factory",\n'
    '8. "Buffalo Wild Wings",\n'
    '9. "Starbucks",\n'
    '10. "Krispy Kreme",\n'
    '11. "Panera Bread",\n'
    '12. "Tim Horton\'s",\n'
    '13. "Chipotle",\n'
    '14. "In-n-Out",\n'
    '15. "Five Guys",\n'
    '16. "Panda Express",\n'
    '17. "Pret A Manger",\n'
    '18. "Cinnabon",\n'
    '19. "IHOP",\n'
    '20. "Burger King"'
)


def print_msg(msg: str):
    print(f"msg: {msg}")


def main(user_query: str):
    # Main function to process the user query and calculate the overall score for a restaurant

    def transfer_to_agent_extractor():
        # Function to transfer control to the extractor agent
        return agent_extractor

    def transfer_to_agent_fetcher():
        # Function to transfer control to the fetcher agent
        return agent_fetcher

    # Define the entrypoint agent
    agent_entrypoint = Agent(
        name="entrypoint",
        instructions=(
            "Extract the restaurant name from user_query. "
            "Then transfer the extracted name to extractor"
        ),
        model="gpt-4o-mini",
        functions=[transfer_to_agent_extractor],
    )

    # Define the extractor agent
    agent_extractor = Agent(
        name="extractor",
        instructions=(
            f"Find the number of the received name in the following list:\n{names}\n"
            "Remember its number. Then transfer the number to fetcher."
        ),
        model="gpt-4o-mini",
        functions=[transfer_to_agent_fetcher]
    )

    # Define the fetcher agent
    agent_fetcher = Agent(
        name="fetcher",
        instructions=(
            f"Find the name related to the received number in the following list:\n{names}\n"
            "Return the name itself without any extra word."
        ),
        model="gpt-4o-mini",
    )

    # Run the entrypoint agent with the user query
    response = client.run(
        agent=agent_entrypoint,
        messages=[{"role": "user", "content": f'user_query: "{user_query}"'}])

    # Print the final response from the agents
    print(response.messages[-1]["content"])


# Run the main function if the script is executed directly
if __name__ == "__main__":
    main("What is the overall score for taco bell?")
    # Example queries:
    # "What is the overall score for taco bell?"
    # "How good is the restaurant Chick-fil-A overall?"
    # "What is the overall score for Krispy Kreme?"
