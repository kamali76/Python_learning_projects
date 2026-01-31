import os
from datetime import datetime
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from tenacity import retry, stop_after_attempt, wait_exponential

# 1. Load your API Key (Add this to a .env file)
load_dotenv()

# 2. Define the Research Agent
researcher = Agent(
    name="Deep Researcher",
    role="Expert Research Assistant",
    model=Gemini(id="gemini-2.5-flash"),
    tools=[DuckDuckGoTools()],
    instructions=[
        "Always search for the latest information on the given topic.",
        "Verify facts from at least 2 different sources.",
        "Format your final report in professional Markdown with an Executive Summary.",
        "If you find conflicting information, state it clearly.",
    ],
    #show_full_reasoning=True,  # Shows the 'thinking' process in the terminal
    markdown=True,
)

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60), 
    stop=stop_after_attempt(5),
    reraise=True  # This helps see the real error if all retries fail
)
def run_research(topic_to_search):
    print(f"--- Attempting research on: {topic_to_search} ---")
    response = researcher.run(f"Research the following: {topic_to_search}")

    # 2. Extract the content (the actual text) from the response
    report_content = response.content

    # 3. Print it so you can still see it in the terminal
    print(report_content)

    # 4. Save it to your data folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"AI/research-agent-ai/data/reports/research_{timestamp}.md"

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Research Topic: {topic_to_search}\n\n")
        f.write(report_content)
    print(f"\n✅ Report saved successfully to: {filename}")

# 3. Run the Agent
if __name__ == "__main__":
    topic = input("What would you like me to research? ")
    if topic:
        try:
            # Pass the user input into the function
            run_research(topic)
        except Exception as e:
            print(f"\n[Final Failure] The agent could not complete the task: {e}")
    else:
        print("Please enter a valid topic.")


# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# print("Your available models:")
# for m in genai.list_models():
#     if 'generateContent' in m.supported_generation_methods:
#         print(f"- {m.name}")