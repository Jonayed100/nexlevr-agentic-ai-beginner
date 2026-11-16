# Workflows vs Agents: A Short Design Doc

Task 3 of the Beginner track of the NEXLEVR Agentic AI Developer internship.

**Author:** Jonayed Hossain

## Summary

Use a **workflow** when you can write the steps down in advance. Use an
**agent** when you cannot, because the right next step depends on what was
just discovered. Most business automations are the first kind, so the
default should be a workflow, with an agent only for the part that needs it.

## Definitions

**Workflow.** The developer decides the steps and their order. An AI model
may do the work inside a step (classify this, summarise that), but the code
controls what happens next.

```
Input -> Step 1 -> Step 2 -> Step 3 -> Output      (path fixed in code)
```

**Agent.** The model decides the steps. It is given a goal and a set of
tools, and it loops: choose a tool, read the result, choose again, until it
judges the goal is met.

```
Goal -> Model -> Tool -> Result -> Model -> Tool -> ... -> Answer
                 (path chosen by the model at run time)
```

## Trade-offs

| | Workflow | Agent |
|---|---|---|
| Who chooses the next step | Code | Model |
| Predictability | Same path every run | Path varies between runs |
| Cost and speed | Known number of model calls | Unknown; can be many |
| Debugging | Check each step separately | Must read the whole trace |
| Testing | Test each step with fixed inputs | Needs evaluation on many scenarios |
| Handles unexpected cases | Only those planned for | Can adapt |
| Risk when wrong | Fails at a known step | Errors compound over turns |

## When a simple automation should beat a free-running agent

Choose the workflow when any of these is true:

1. **The steps are known.** If you can draw the flowchart, build the
   flowchart.
2. **Mistakes are expensive.** Money, legal text, customer data and
   anything irreversible need a fixed path and explicit checks.
3. **Volume is high.** Thousands of runs a day need predictable cost and
   latency.
4. **It must be audited.** "It always does A, then B, then C" is easy to
   explain to a manager or a regulator.

Choose an agent when all of these are true:

1. The number and order of steps cannot be known in advance.
2. The task is valuable enough to justify higher cost and slower runs.
3. Mistakes are cheap or caught before they matter (a human reviews, or the
   agent only has read-only tools).
4. Success can be measured, so the agent can be evaluated.

## Three business examples

### 1. Invoice processing for an accounting team

**Task.** Read incoming supplier invoices (PDF), extract supplier, amount
and due date, match to a purchase order, and queue for payment.

**Analysis.** Every invoice follows the same path: extract, validate,
match, route. Errors cost real money. Volume is high and auditors will ask
how it works.

**Recommendation: workflow.** Use a model only for the extraction step,
then plain code for validation (does the total equal the line items?) and
matching. Send anything that fails a check to a person. An agent adds cost
and unpredictability with no benefit.

### 2. Customer support for an online shop

**Task.** Answer customer messages: order status, returns, delivery
problems, product questions, complaints.

**Analysis.** Most messages are typically a few known types (where is my
order, how do I return this). The rest are unusual and need several lookups
and some judgement.

**Recommendation: workflow first, agent for the remainder.** A router
classifies each message. Common types go to fixed flows (look up order,
reply from a template). Only unclassified or multi-issue messages go to an
agent that has read-only tools (order lookup, policy search) and must hand
over to a human for refunds or anything irreversible.

### 3. Competitor research for a marketing agency

**Task.** "Find out what our client's three main competitors launched this
quarter and how customers reacted."

**Analysis.** The steps cannot be listed in advance. What to search next
depends on what the last search found; some competitors need five lookups
and some need twenty. The output is a draft report that a strategist reads
before it goes anywhere, so mistakes are caught.

**Recommendation: agent.** Give it search and page-reading tools, a turn
limit, and a requirement to cite a source for every claim. Keep a human
review step before the report reaches the client.

## Connection to my Task 2

My daily trends digest is built as an agent because the task asked for
one, and it is a good way to learn the tool-use loop. In production I would
rebuild it as a workflow: the steps are always "fetch 5 feeds, then
summarise", so code should fetch the feeds and the model should be called
once to write the digest. That would be cheaper, faster and easier to
test. It is a small example of the main point of this doc.

## Decision checklist

Before building, ask in this order:

1. Can a single model call with a good prompt do it? Stop there.
2. Can I write the steps down? Build a workflow.
3. Is only one part unpredictable? Build a workflow with an agent in that
   part.
4. Is the whole task open-ended, valuable, measurable and safe to get
   wrong? Build an agent, with limits and human review.
