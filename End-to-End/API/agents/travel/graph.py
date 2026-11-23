from langgraph.graph import StateGraph, START, END
from agents.models.state import TravelState
from agents.tools.aviation_stack import search_flights
from agents.tools.tavily import tavily_search
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage
from agents.llm.llm import get_llm

_, llm_with_tools, _ = get_llm()


def get_travel_graph(checkpointer):
    def flight_node(state: TravelState):
        query = state["user_query"]
        flight_data = search_flights(query)
        return {
            "flight_results": flight_data,
            "messages": [AIMessage(content="Flights results fetched")],
            "llm_calls": state.get("llm_call", 0) + 1,
        }

    def hotel_node(state: TravelState):
        query = f"Best hotels for {state['user_query']}"
        hotel_results = tavily_search(query)
        return {
            "hotel_results": hotel_results,
            "messages": [AIMessage(content="FHotel information fetched")],
            "llm_calls": state.get("llm_call", 0) + 1,
        }

    def itinerary_node(state: TravelState):
        prompt = f"""
    Create a complete travel itinerary.

    User Query:
    {state['user_query']}

    Flight Results:
    {state['flight_results']}

    Hotel Results:
    {state['hotel_results']}

    Make the itinerary practical, budget-aware, and easy to follow
        """
        response = llm_with_tools.invoke(
            [
                SystemMessage(content="You are an expert travel planner."),
                HumanMessage(content=prompt),
            ]
        )
        return {
            "itinerary": response.content,
            "messages": [response],
            "llm_calls": state.get("llm_call", 0) + 1,
        }

    def final_node(state: TravelState):
        final_prompt = f"""
    Generate the final travel response for the user.

    User Request
    {state['user_query']}

    Flights:
    {state['flight_results']}

    Hotels:
    {state['hotel_results']}

    Itinerary:
    {state['itinerary']}

    Format the final answer beautifully using these sections:

    1. Triple Summary
    2. Flight Information
    3. Hotel Suggestions
    4. Day-by-Day Itinerary
    5. Estimated Budget
    6. Final Recommendadtions

    Important:
    - Be clear and practical
    - Mention that live flight API may not provide ticket prices if pricing is unavailable
    - Keep the response useful for travel planning
    """

        response = llm_with_tools.invoke(
            [
                SystemMessage(
                    content="You are a professional AI travel booking assistant."
                ),
                HumanMessage(content=final_prompt),
            ]
        )

        return {"messages": [response], "llm_calls": state.get("llm_call", 0) + 1}

    graph_builder = StateGraph(TravelState)
    graph_builder.add_node("flight_node", flight_node)
    graph_builder.add_node("hotel_node", hotel_node)
    graph_builder.add_node("itinerary_node", itinerary_node)
    graph_builder.add_node("final_node", final_node)

    graph_builder.add_edge(START, "flight_node")
    graph_builder.add_edge("flight_node", "hotel_node")
    graph_builder.add_edge("hotel_node", "itinerary_node")
    graph_builder.add_edge("itinerary_node", "final_node")
    graph_builder.add_edge("final_node", END)

    graph = graph_builder.compile(checkpointer=checkpointer)
    return graph
