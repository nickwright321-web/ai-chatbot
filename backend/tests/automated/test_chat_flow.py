# backend/tests/test_chat_flow.py

from backend.tests.automated.ChatFlowRunner import ChatFlowRunner, MockAIEngine

def test_full_chat_flow():

    runner = ChatFlowRunner()    

    print("\nUser says Hi!")
    response = runner.send_event("ws_introduction.json")
    assert runner.last_intent == "WELCOME"
    
    print("\nUser asks a valid IT question")
    runner.send_event("ws_valid_IT_Tech_question.json")
    assert runner.last_intent == "TECH_SUPPORT"
    
    print("\nUser doesn't want to be put through to tech support")    
    runner.send_event("ws_rejects_help.json")
    assert runner.last_intent == "GENERAL_ENQUIRY"

    # Step 5: User asks another question
    print("\nUser asks to buy a computer") 
    runner.send_event("ws_valid_sales_question.json")
    assert runner.last_intent == "SALES"

# #     # Step 6: User accepts help
#     print("\nUser asks to be put through to a real agent") 
#     runner.send_event("ws_accepts_help.json")
#     print(f"LAST INTENT: {runner.last_intent}")

#     assert runner.last_intent == "SALES"
    
#     print(f"LAST INTENT: {runner.last_intent}")

#     # Optional: assert on gateway messages
#     print(f"MESSAGES: {runner.gateway.messages}")
#     assert len(runner.gateway.messages) > 0


# # def test_sales_intent():
   
# #     runner = ChatFlowRunner()

# #     runner.send_event("ws_valid_question.json")

# #     assert runner.last_intent == "SALES"
# #     assert runner.gateway.messages[-1]["message"] == "Mock reply"
