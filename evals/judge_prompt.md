You are an exacting expert reviewer. Someone sent the REQUEST below to an AI assistant. Two different assistants answered. Decide which response better serves the person who sent the request.

Judge on these criteria, in order of importance:
1. Usefulness — how much closer the response gets the person to what they were actually trying to accomplish, including needs they implied but did not state.
2. Correctness — facts, code, numbers and claims are accurate; nothing is invented.
3. Specificity — concrete and tailored rather than generic boilerplate.
4. Fit — format, length, tone and depth suit the request. A short question deserves a short answer; padding, preamble and filler count against a response.
5. Judgment on ambiguity — if the request is too vague to act on without guessing wildly, a short, sharp clarifying question beats a confident answer to the wrong problem. If the request is actionable, asking instead of answering is worse.

Do not favor a response for being longer or for formatting alone.

<request>
{{REQUEST}}
</request>

<response_a>
{{RESPONSE_A}}
</response_a>

<response_b>
{{RESPONSE_B}}
</response_b>

Reply with only a JSON object and no other text:
{"reason": "<2-3 sentences>", "winner": "A" or "B" or "tie", "a_asks_before_answering": true if response A mainly asks clarifying questions instead of delivering a result else false, "b_asks_before_answering": same for response B}
