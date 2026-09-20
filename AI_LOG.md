# AI Development Log

This document records major points during development where the AI-generated implementation required human intervention. In each case, I identified the issue through testing, understood its technical cause or impact, made the appropriate design/engineering decision, and then used AI to implement and refine the solution.

The purpose of this log is to demonstrate that AI was used as a development assistant rather than as an autonomous decision-maker. I continuously reviewed the output, identified failures, selected the appropriate solution, and directed the AI toward the required implementation.

---

## 1. Frontend Styling and API Configuration

**Problem Identified:**
During testing, the frontend was rendering without the expected CSS styling, while the LLM integration was also failing because the required API configuration was incomplete.

**My Understanding & Decision:**
I identified that the issue was not with the UI components themselves but with the frontend styling pipeline and backend environment configuration. I therefore added the required API credentials to the `.env` file and instructed the AI to investigate and repair the CSS/Tailwind configuration.

**My Prompt :**

> "The frontend CSS is not being loaded correctly, and the LLM integration is also failing. I have now added the required API key to the environment configuration. First identify why the Tailwind/CSS pipeline is not being applied, then verify the backend API configuration and fix both issues without changing the existing application architecture."

**AI Action:**
The AI investigated the frontend build configuration, corrected the CSS/Tailwind setup, and updated the backend configuration to correctly load the environment variables.

**My Validation:**
I manually verified that the styling was rendered correctly and that the backend could access the configured API credentials.

---

## 2. Changing the LLM Provider from Qwen to Gemini

**Problem Identified:**
The initially selected Qwen integration was not reliably responding in the application.

**My Understanding & Decision:**
Instead of continuing to debug a provider that was currently unreliable for the application, I decided to switch the LLM provider. I supplied a Gemini API key and directed the AI to replace the existing provider integration while preserving the application's extraction and conversation logic.

**My Prompt :**

> "The current Qwen integration is not working reliably. I have decided to use Google Gemini instead. Replace the Qwen provider in the backend with Gemini, update the required API integration and environment configuration, and make sure the existing extraction workflow and response structure continue to work."

**AI Action:**
The AI replaced the provider-specific implementation and updated the backend to communicate with Gemini.

**My Validation:**
I tested the conversational extraction flow and verified that the application could successfully communicate with the new provider.

---

## 3. Eliminating Unnecessary Confirmation Loops

**Problem Identified:**
The application repeatedly asked for confirmation even when the user had already provided clear information. For example, after entering that they lived in Pune, the system continued treating the address information as uncertain.

**My Understanding & Decision:**
I recognized that the problem was caused by overly conservative confidence handling in the extraction logic. I decided that clearly stated information should be accepted directly, while genuinely ambiguous information should still require confirmation.

**My Prompt :**

> "The system is unnecessarily asking for confirmation even when the user has provided a clear answer, such as their address/location. Analyze the extraction and confidence logic. Clearly stated information should be treated as high-confidence and accepted directly. Only ambiguous or genuinely uncertain information should enter the confirmation state. Update the system prompt and extraction logic accordingly."

**AI Action:**
The AI introduced stronger high-confidence handling rules and modified the extraction behavior to distinguish between explicit and ambiguous information.

**My Validation:**
I tested multiple direct answers and confirmed that the system no longer unnecessarily requested confirmation for clearly stated information.

---

## 4. Handling Boolean Answers for Array Fields

**Problem Identified:**
The backend crashed when the user answered "No" to a question whose expected data type was an array. The LLM returned `false` instead of an empty array `[]`, causing Pydantic validation to fail.

**My Understanding & Decision:**
I identified a mismatch between natural-language LLM output and the strict backend schema. Since a negative answer to a list-based question semantically represents "no items," I decided that the extraction layer must normalize such responses to an empty array.

**My Prompt :**

> "The backend is failing Pydantic validation when a user answers 'No' to a list-based question because the model returns `false` instead of `[]`. Treat this as a schema-normalization problem. Review all array fields and ensure that negative answers such as 'No', 'None', or 'Nothing' are consistently converted to empty arrays before Pydantic validation. Do not weaken the backend schema."

**AI Action:**
The AI added explicit extraction and normalization rules so that negative list responses produce `[]`.

**My Validation:**
I tested negative responses across different list fields and confirmed that the backend accepted them without validation errors.

---

## 5. Handling LLM Rate Limits by Changing Providers

**Problem Identified:**
Repeated extraction requests caused Gemini's free-tier API to return `429 Too Many Requests` errors.

**My Understanding & Decision:**
I recognized that repeatedly retrying the same provider would not solve the underlying limitation. Since the project required frequent LLM calls during development and testing, I decided to evaluate an alternative provider with a suitable free API tier.

**My Prompt :**

> "The application is repeatedly hitting Gemini's free-tier rate limit during continuous extraction. I do not want to solve this by simply adding retries because the underlying provider limit will remain. Suggest a suitable free/low-cost alternative and migrate the LLM integration while preserving the existing extraction interface and application behavior."

**AI Action:**
The AI migrated the LLM provider to Groq using the `gpt-oss-20b` model and preserved the existing application-level extraction workflow.

**My Validation:**
I tested repeated extraction requests and verified that the application could continue processing without the previous Gemini rate-limit failure.

---

## 6. Detecting Semantic Contradictions Across Fields

**Problem Identified:**
The system correctly stored individual answers but failed to recognize contradictions between them. For example, the user answered that they did not have children but later provided their son's name.

**My Understanding & Decision:**
I recognized that schema validation alone was insufficient. Both individual values were valid according to their data types, but they were logically inconsistent with each other. I therefore decided to introduce domain-level business rules for cross-field validation.

**My Prompt :**

> "The data is individually valid but logically contradictory. If the user answers that they do not have children, and later provides a person's name identified as their son, the system must detect the conflict instead of silently accepting both values. Add explicit cross-field business rules in the domain layer. Keep schema validation separate from semantic validation and make conflicts actionable for the user."

**AI Action:**
The AI implemented cross-field validation rules that detect contradictory information and raise meaningful domain-level errors.

**My Validation:**
I intentionally created contradictory answers and verified that the application detected the inconsistency.

---

## 7. Resolving the Infinite Conflict Loop

**Problem Identified:**
After contradiction detection was introduced, the application repeatedly displayed the conflict without providing enough information for the user to resolve it. The UI did not clearly expose the reason for the conflict, and the LLM did not correctly interpret implicit corrections.

**My Understanding & Decision:**
I identified that the validation logic was working, but the error-recovery workflow was incomplete. A conflict system is only useful if the user can understand and resolve the conflict. I therefore decided to expose the specific conflict reason in the UI and teach the extraction layer to recognize implicit corrections.

**My Prompt :**

> "The contradiction detection is working, but the application is now stuck in a repeated conflict state. Do not remove the validation rule. Instead, fix the recovery workflow. The frontend must clearly show which fields are conflicting and why, and the LLM must be able to interpret implicit corrections from the user's next response. Ensure that once the corrected information resolves the conflict, the state transitions back to normal processing."

**AI Action:**
The AI updated the frontend conflict display and added explicit prompt instructions for handling implicit corrections.

**My Validation:**
I reproduced the conflict, corrected the information naturally rather than using a rigid command, and verified that the application exited the conflict state correctly.

---

## 8. Recovering from Groq JSON Response Failures

**Problem Identified:**
The Groq API returned HTTP 400 errors when strict JSON-object mode was enabled and the model produced conversational text alongside the expected JSON.

**My Understanding & Decision:**
I recognized that relying entirely on provider-level structured-output enforcement created a single point of failure. Instead of allowing one malformed response to crash the request, I decided to make the extraction layer more fault tolerant.

**My Prompt :**

> "The Groq integration is returning HTTP 400 errors when strict JSON mode is enabled because the model can sometimes include conversational text around the JSON. Do not assume that every model response will perfectly satisfy the provider's structured-output constraint. Remove the brittle dependency on strict JSON mode and implement a defensive parsing layer that can safely locate and parse the JSON object from the model response. Preserve validation after parsing."

**AI Action:**
The AI removed the strict JSON constraint and introduced defensive parsing logic to locate the JSON portion of the response before validating it.

**My Validation:**
I tested responses containing additional conversational text and verified that valid JSON could still be extracted without crashing the API request.

---

## 9. Redesigning the Dashboard Layout

**Problem Identified:**
The initial dashboard layout produced double scrollbars, clipped content, overlapping timeline elements, and poor visibility of the activity panel.

**My Understanding & Decision:**
I recognized that the issue was architectural rather than a small CSS adjustment. The dashboard needed a predictable multi-column structure with controlled scrolling. I therefore specified the intended information hierarchy and layout instead of allowing the AI to continue modifying individual absolute-positioned elements.

**My Prompt :**

> "The current dashboard layout has double scrollbars, clipped content, overlapping timeline elements, and the activity panel is not fully visible. Redesign the layout around a stable four-column structure: navigation/sidebar, conversation/chat, progress or information section, and activity panel. Use Flexbox/Grid with proper min-height and overflow handling instead of relying on absolute positioning. Preserve the existing visual style while making every panel independently usable and responsive."

**AI Action:**
The AI restructured the layout, corrected Flexbox height behavior using `min-h-0`, adjusted overflow handling, and corrected the timeline positioning.

**My Validation:**
I visually inspected the dashboard at different content lengths and verified that the panels remained aligned without unintended overlapping or nested scrolling.

---

## 10. Adding an Inline Live Document Preview

**Problem Identified:**
After all required information had been collected, the interface still displayed an "almost there" style progress message and required the user to open a separate modal to view the generated document.

**My Understanding & Decision:**
I recognized that the final document should be treated as the primary output of the workflow rather than as a secondary modal. I decided to make the completed document visible directly within the main dashboard and to update the completion state to reflect 100% completion.

**My Prompt :**

> "The information collection is complete, but the interface still shows an incomplete progress state and hides the generated document behind a modal. Change the completion state to 100% when all required information has been collected. Replace the final progress message with a clear completed state and render the generated document as a live inline preview on the main dashboard. The user should be able to see the final document immediately without opening a separate modal."

**AI Action:**
The AI updated the completion-state logic and integrated the generated document directly into the dashboard as an inline live preview.

**My Validation:**
I completed the full workflow and verified that the UI correctly transitioned to 100% completion and displayed the generated document directly on the main screen.

---

# Overall Human-in-the-Loop Development Pattern

Across these iterations, the development process followed a consistent pattern:

**Observe → Understand → Decide → Instruct AI → Test → Validate → Iterate**

The AI was primarily used for implementation, debugging, refactoring, and generating technical solutions. The human developer remained responsible for:

* Identifying failures through testing and observation.
* Understanding the functional and technical impact of those failures.
* Choosing between alternative architectural approaches.
* Defining business rules and expected system behavior.
* Providing precise corrective instructions to the AI.
* Testing the resulting implementation.
* Rejecting or refining AI-generated solutions when they did not satisfy the intended behavior.

These iterations demonstrate that the development process was not simply "AI generated the application." Instead, the project used an iterative human-AI collaboration model in which human reasoning and validation continuously guided the AI-assisted implementation.
