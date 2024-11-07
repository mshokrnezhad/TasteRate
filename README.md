# TasteRate

<div align="center">
  <img src="TasteRate.png" alt="drawing" width="600"/>
</div>


TasteRate is a Python code that leverages Large Language Models (LLMs) to analyze and summarize unstructured, natural-language data from restaurant reviews. These reviews are qualitative, and the code uses agent design frameworks to fetch, summarize, and score each review. TasteRate can answer questions like "How good is Subway as a restaurant?" or "What would you rate In N Out?" by returning a calculated score based on food and service quality.

## AutoGen in TasteRate

The primary framework that TasteRate employs to develop multi-agent workflows is AutoGen, which involves several LLMs collaborating. AutoGen allows you to define "control flows" or "conversation flows" between LLMs, enabling them to interact and solve complex tasks as a team. With AutoGen, TasteRate defines a network of LLM agents for efficient data processing, reasoning, and evaluation. TasteRate relies on the **GPT-4o-mini model** for its operations due to its cost efficiency, providing similar performance to GPT-4o but at a significantly reduced cost.

### Features of AutoGen in TasteRate

TasteRate leverages several key features of the AutoGen framework:

- **ConversableAgent**: This agent handles interactions between LLMs, managing communication and execution of tasks in a multi-agent workflow.
- **initiate_chat**: This function initiates a conversation between agents defined using ConversableAgent, allowing them to communicate and collaborate to solve tasks.

### Recommended Architecture

The architecture for TasteRate using AutoGen involves several agents working sequentially:

- **Entry Point Agent**: Manages the overall workflow, initiates conversations, and ensures that tasks are executed in the correct sequence.
- **Assistant Agent**: Extracts the restaurant name from user queries, ensuring proper identification of entities.
- **Review Analysis Agent**: Responsible for analyzing fetched reviews and assigning scores based on predefined criteria.

### Note on Challenges with AutoGen

During the development of TasteRate, some challenges were encountered while using the AutoGen framework:

- When restricting the number of interactions between agents, the agents sometimes did not execute their assigned functions correctly.
- There was difficulty in finding ways to stall interactions in order to run functions first, and then continue interactions between agents once the function execution was complete.
- Adding the results of function calls directly into the chat history for passing to other agents was also challenging, limiting effective collaboration.

## Swarm in TasteRate

OpenAI's Swarm is the other framework that TasteRate utilizes to develop multi-agent workflows. While similar to AutoGen, Swarm is specifically designed for educational purposes.

### Features of Swarm in TasteRate

TasteRate capitalizes on several key features of the Swarm framework:

- **Agent**: Defines agents in Swarm, including their name, instructions, and model.
- **client.run**: Initiates conversations between the agents defined using Agent, enabling communication and collaboration to complete tasks.

### Recommended Architecture

In utilizing Swarm to extract the name of a restaurant from user queries, the architecture involves multiple agents working sequentially:

- **Entry Point Agent**: Manages the overall workflow, initiates conversations, and extracts the restaurant name from the user query.
- **Extractor & Fetcher Agents**: Transforms the extracted name into a format that can be saved in the data file.

### Note on Challenges with AutoGen

Throughout the development of TasteRate, certain challenges arose when using the Swarm framework:

- LLMs lack stability, producing varying outputs in different runs, which compromises their reliability in production environments. This is why we used Swarm to just implement the initial step of TasteRate.
- LLMs execute assigned functions based on the queries they receive and autonomously make decisions, resulting in unpredictable function execution. I was unable to find a method to ensure that LLMs consistently execute specific functions, nor could I effectively manage the passing of results between LLMs after or before processing.

## Setup: Environment Variables, Virtual Environment, and Dependencies

To use TasteRate, we recommend setting up a virtual environment. 

- To run autogen-related coode, install the required packages from `requirements_autogen.txt`.
- Regarding Swarm, check [here](https://github.com/openai/swarm) to see the installation instructions.

To access LLM capabilities, create your own API Key by following [OpenAI Documentation](https://platform.openai.com/docs/quickstart). Store this API key in an environment variable named `OPENAI_API_KEY`.

## TasteRate Workflow

### Step 1: Extract the Restaurant Name

The restaurant name is extracted from the function arguments provided by the entrypoint agent.

### Step 2: Retrieve Reviews

The reviews for the extracted restaurant name are retrieved using the `fetch_restaurant_data` function.

### Step 3: Analyze Reviews to Extract Scores

The Review Analysis Agent analyzes the fetched reviews to extract scores for food quality and customer service using the adjectives provided in each review.

Keywords corresponding to each score:

- **Score 1/5**: awful, horrible, disgusting
- **Score 2/5**: bad, unpleasant, offensive
- **Score 3/5**: average, uninspiring, forgettable
- **Score 4/5**: good, enjoyable, satisfying
- **Score 5/5**: awesome, incredible, amazing

The agent assigns scores by analyzing the adjectives used in the review text.

### Step 4: Calculate the Overall Score

The overall score is calculated using the extracted food and customer service scores by applying the `calculate_overall_score` function to aggregate these scores into a final rating for the restaurant.

## TasteRate Codebase

- **`main_autogen.py`**: The implementation of TasteRate based on AutoGen. It includes code for all steps.
- **`main_swarm.py`**: The implementation of TasteRate based on Swarm. It includes only Step 1.
- **`requirements.txt`**: Lists all required packages for TasteRate.
---

## Thank You 🙏

Thank you for exploring TasteRate with me! I hope you find this repository helpful and inspiring as you delve into analyzing restaurant reviews with LLMs. Feel free to fork the repo and make contributions. I will review them as soon as possible, and your contributions will be merged into the main repository.
