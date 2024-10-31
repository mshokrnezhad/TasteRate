# TasteRate

<div align="center">
  <img src="TasteRate.png" alt="drawing" width="600"/>
</div>


TasteRate is a Python code that leverages Large Language Models (LLMs) to analyze and summarize unstructured, natural-language data from restaurant reviews. These reviews are qualitative, and the code uses AutoGen framework to fetch, summarize, and score each review. TasteRate can answer questions like "How good is Subway as a restaurant?" or "What would you rate In N Out?" by returning a calculated score based on food and service quality.

## AutoGen Framework in TasteRate

TasteRate uses the AutoGen framework to create multi-agent workflows that involve multiple LLMs working together. AutoGen allows you to define "control flows" or "conversation flows" between LLMs, enabling them to interact and solve complex tasks as a team. With AutoGen, TasteRate defines a network of LLM agents for efficient data processing, reasoning, and evaluation. TasteRate relies on the **GPT-4o-mini model** for its operations due to its cost efficiency, providing similar performance to GPT-4o but at a significantly reduced cost.

### Features of AutoGen in TasteRate

TasteRate leverages several key features of the AutoGen framework:

- **ConversableAgent**: This agent handles interactions between LLMs, managing communication and execution of tasks in a multi-agent workflow.
- **initiate_chat**: This function initiates a conversation between agents defined using ConversableAgent, allowing them to communicate and collaborate to solve tasks.

## Setup: Environment Variables, Virtual Environment, and Dependencies

To use TasteRate, we recommend setting up a virtual environment and installing the required packages from `requirements.txt`.

To access LLM capabilities, create your own API Key by following [OpenAI Documentation](https://platform.openai.com/docs/quickstart). Store this API key in an environment variable named `OPENAI_API_KEY`.

## TasteRate Components

### Recommended Architecture

The architecture for TasteRate involves several agents working sequentially:

- **Entry Point Agent**: Manages the overall workflow, initiates conversations, and ensures that tasks are executed in the correct sequence.
- **Assistant Agent**: Extracts the restaurant name from user queries, ensuring proper identification of entities.
- **Review Analysis Agent**: Responsible for analyzing fetched reviews and assigning scores based on predefined criteria.

### TasteRate Codebase

- **`main.py`**: The main implementation of TasteRate. It includes code for data fetching, analysis, and scoring.
- **`requirements.txt`**: Lists all required packages for TasteRate.

### TasteRate Workflow

#### Step 1: Extract the Restaurant Name

The restaurant name is extracted from the function arguments provided by the entrypoint agent.

#### Step 2: Retrieve Reviews

The reviews for the extracted restaurant name are retrieved using the `fetch_restaurant_data` function.

#### Step 3: Analyze Reviews to Extract Scores

The Review Analysis Agent analyzes the fetched reviews to extract scores for food quality and customer service using the adjectives provided in each review.

Keywords corresponding to each score:

- **Score 1/5**: awful, horrible, disgusting
- **Score 2/5**: bad, unpleasant, offensive
- **Score 3/5**: average, uninspiring, forgettable
- **Score 4/5**: good, enjoyable, satisfying
- **Score 5/5**: awesome, incredible, amazing

The agent assigns scores by analyzing the adjectives used in the review text.

#### Step 4: Calculate the Overall Score

The overall score is calculated using the extracted food and customer service scores by applying the `calculate_overall_score` function to aggregate these scores into a final rating for the restaurant.

---

## Thank You 🙏

Thank you for exploring TasteRate with me! I hope you find this repository helpful and inspiring as you delve into analyzing restaurant reviews with LLMs. Feel free to fork the repo and make contributions. I will review them as soon as possible, and your contributions will be merged into the main repository.
