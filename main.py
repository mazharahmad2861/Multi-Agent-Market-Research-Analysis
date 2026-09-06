import gradio as gr

from agents import supervisor, config


def chat_with_agents(message, history):
    """
    Send the user's message to the supervisor
    and return the final response.
    """

    response = supervisor.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        },
        config
    )

    messages = response.get("messages", [])

    # Get the final assistant message
    for msg in reversed(messages):

        if getattr(msg, "type", None) == "ai":

            content = getattr(msg, "content", "")

            if content:
                return content

    return "No response was generated."


# ---------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------

demo = gr.ChatInterface(
    fn=chat_with_agents,
    title="Supervisor Multi-Agent System",
    description=(
        "Ask questions about companies, "
        "stock performance, or request visualizations."
    ),
    textbox=gr.Textbox(
        placeholder="Ask something...",
        container=True
    ),
)


if __name__ == "__main__":
    demo.launch()