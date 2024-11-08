# TasteRate

<div align="center">
  <img src="TasteRate.png" alt="drawing" width="600"/>
</div>


TasteRate is a Python code that leverages Large Language Models (LLMs) to analyze and summarize unstructured, natural-language data from restaurant reviews. These reviews are qualitative, and the code uses agent design frameworks to fetch, summarize, and score each review. TasteRate can answer questions like "How good is Subway as a restaurant?" or "What would you rate In N Out?" by returning a calculated score based on food and service quality.

Implementing TasteRate serves as an incentive to explore different LLM-based agent design frameworks. So far, we have successfully tested AutoGen, Swarm, and MetaGPT.

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

### Note on Challenges with Swarm

Throughout the development of TasteRate, certain challenges arose when using the Swarm framework:

- LLMs lack stability, producing varying outputs in different runs, which compromises their reliability in production environments. This is why we used Swarm to just implement the initial step of TasteRate.
- LLMs execute assigned functions based on the queries they receive and autonomously make decisions, resulting in unpredictable function execution. I was unable to find a method to ensure that LLMs consistently execute specific functions, nor could I effectively manage the passing of results between LLMs after or before processing.

## MetaGPT in TasteRate

MetaGPT is the other framework that TasteRate utilizes, an advanced agent-based framework designed for orchestrating complex multi-agent workflows with LLMs. MetaGPT provides a flexible and scalable environment for agents to interact, execute functions, and pass data seamlessly.

### Features of MetaGPT in TasteRate

TasteRate leverages several key features of the MetaGPT framework:

- **Custom Action Classes**: By importing Action from metagpt.actions, TasteRate defines custom actions that agents can perform. This allows for fine-grained control over agent behaviors and tasks, enabling agents to execute specific functions required for the application's workflow.
- **Advanced Logging**: Utilizing logger from metagpt.logs, TasteRate implements robust logging mechanisms. This feature tracks agent interactions, function executions, and workflow progress, which enhances debugging, monitoring, and maintenance of the codebase.

### Recommended Architecture

The following agents of MetaGPT are used in the TasteRate application:
- **Extract Agent**: The Extract Agent is tasked with extracting the restaurant name from the user's query. It employs a prompt template to parse the user's input meticulously, focusing on identifying the restaurant name accurately. The agent ensures that the extracted name adheres to a specific output format ("the name is: XXX") with no additional text, which standardizes the data for downstream processing. The extraction process is handled asynchronously using the run method, enhancing efficiency. Additionally, the agent implements the extract_name static method to parse the AI model's response, isolating the restaurant name cleanly and reliably.
- **Compare Agent**: The Compare Agent plays a critical role in verifying the accuracy of the extracted restaurant name by comparing it with a list of known restaurant names to find the best match. It receives the extracted name and a list of possible names, then utilizes a prompt template to identify the entry most similar to the extracted name. By ensuring that the selected entry follows the specific output format ("the entry is: XXX") with no extra text, the agent maintains consistency and prepares the data for the next steps. The compare_names static method is implemented to parse the AI model's response effectively, enhancing the reliability of the restaurant identification process, especially in cases of typos or ambiguous inputs from the user.
- **Analyze Agent**: The Analyze Agent focuses on processing the fetched reviews to extract quantifiable scores for food quality and customer service. It leverages a detailed prompt that includes predefined adjective mappings to translate descriptive words into numerical scores. By examining each review, the agent assigns a food_score and a customer_service_score based on the adjectives present in the text. The results are outputted in a structured JSON format, ensuring consistency and ease of use in later stages. The get_prompt static method constructs tailored analysis prompts based on the reviews, enabling the AI model to perform accurate and context-specific evaluations.

By defining custom actions (Extract, Compare, Analyze) using the Action class, TasteRate ensures that each agent performs its designated task accurately and efficiently. This approach allows for fine-grained control over agent behaviors and tasks, promoting a robust and maintainable codebase. Each agent operates within a well-defined scope, reducing complexity and improving the overall reliability of the application.

Additionally, logging with logger from metagpt.logs enhances transparency and aids in debugging by tracking agent interactions, function executions, and workflow progress. This comprehensive logging mechanism provides valuable insights into the system's operations, making it easier to monitor performance and troubleshoot any issues that arise. The combination of structured actions and detailed logging contributes to the stability and effectiveness of the TasteRate application.

### Note on Challenges with MetaGPT

I succeeded in implementing TasteRate by just using single agents, and there were no challenges. It works perfectly. Function calling is clear. Multi-agent implementation may present some challenges.

## Setup: Environment Variables, Virtual Environment, and Dependencies

To use TasteRate, we recommend setting up a virtual environment. 

- To run autogen-related coode, install the required packages from `requirements_autogen.txt`.
- Regarding Swarm, check [here](https://github.com/openai/swarm) to see the installation instructions.
- To run MetaGPT .ipynb check [here](https://github.com/geekan/MetaGPT) to see how to pass requirements.

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
- **`requirements_autogen.txt`**: Lists all required packages for TasteRate.
- **`main_swarm.py`**: The implementation of TasteRate based on Swarm. It includes only Step 1.
- **`main_metagpt.ipynb`**: Using MetaGPT to implement TasteRate. 

---

## Thank You 🙏

Thank you for exploring TasteRate with me! I hope you find this repository helpful and inspiring as you delve into analyzing restaurant reviews with LLMs. Feel free to fork the repo and make contributions. I will review them as soon as possible, and your contributions will be merged into the main repository.
