from agent_v2.agent import run_agent

if __name__ == "__main__":
    user_request = "Find all open critical incidents."
    result = run_agent(user_request)

    print("=== Final answer ===")
    print(result["final_answer"])
    print("\n=== Activity log ===")
    for step in result["activity_log"]:
        print("-", step)

    print("\n=== Tool trace ===")
    for call in result["tool_trace"]:
        print(call["tool_name"], "-> success:", call["success"])
