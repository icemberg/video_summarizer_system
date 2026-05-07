from services.custom_youtube_tools import CustomYouTubeTools
from services.llm import GeminiService

tool = CustomYouTubeTools()
url = "https://www.youtube.com/watch?v=1vB7VjB20cc&list=PLZoTAELRMXVNNrHSKv36Lr3_156yCo6Nn&index=11"

print("Direct Tool Test:")
print("Video ID:", tool.get_youtube_video_id(url))
captions = tool.get_youtube_video_captions(url)
print("Captions len:", len(captions))
print("Captions preview:", captions[:100])

print("\nAgent Test:")
agent = GeminiService.create_agent(
    model_id="models/gemini-2.5-flash",
    tools=[tool],
    instructions=["Use the custom youtube tool to summarize."]
)
res = agent.run(f"Summarize the video: {url}")
print(res.content)
