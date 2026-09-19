# Ten Planes — the five minute version

**R** ran the research. **J** wants to know if any of it survives contact with a keyboard.

---

**J:** Ten planes. Before you start — is this real, or did you just invent a taxonomy?

**R:** Fair opening. Start with what I went looking for and did not find. There is no canonical diagram for this. I expected Anthropic to have one, because they have thought about it more carefully than almost anyone.

**J:** And?

**R:** They publish four separate decompositions and never draw one picture — a managed-agents post splitting a system into session, harness and sandbox; the agentic loop; a feature table of skills, subagents, hooks and MCP; and the workflows-versus-agents essay. Four cuts through the same object, no composite.

**J:** And the wider field?

**R:** Mostly analogy. Agent-OS papers, the LLM-as-operating-system framing, MemGPT paging context like virtual memory. Some useful, a lot of it metaphor that never constrains a single design decision — decoration, not architecture.

**J:** Hence building one.

**R:** Three, from deliberately different framings — an operating system, a factory line, and a control-plane split. Three judges scored them on different criteria. One won unanimously.

**J:** Give me its argument in a sentence.

**R:** Every guarantee the system needs must live on the deterministic side of exactly one boundary, and the model must only ever produce proposals.

**J:** That's it?

**R:** Everything else is a corollary, and the corollaries are where it gets useful. Here's the first one, and it's the one that will annoy people. The harness is only two planes.

**J:** Two.

**R:** A context compiler and a turn loop. That's it. The thing that decides which tokens exist on this call, and the thing that runs turns and decides when to stop.

**J:** So everything else people put in their harness —

**R:** Is platform. Durable state, policy, scheduling, the tool registry — if your harness owns those, it isn't a harness, it's a pet container with a nicer name. And that isn't purity. A harness owning nothing durable is disposable: kill it, restart it, swap the framework next quarter. A harness holding your state is one you're married to.

**J:** What's the most expensive mistake in here?

**R:** A vocabulary one. Memory products sell you storage; your context compiler does the part that determines quality. Different planes, and the market deliberately blurs them. Storing everything an agent ever saw is easy and several vendors will sell you that. Deciding which eight thousand tokens go into *this* call — what's compacted, what's fetched just in time, what carries a trust label because it came off a web page — that's where quality lives. Nobody sells it, and nobody should.

**J:** Give me one more corollary.

**R:** Subagents are a context-economy device, never a security one. Spawning one buys a clean window and precisely zero containment. Isolation comes from narrowing what the agent may do, plus a sandbox. Nothing at this event — honestly nothing in the field — isolates agents from each other. Only their effects.

**J:** All right. The vendors. Where do they land?

**R:** EdgeOne takes inference, loop hosting and execution — its sandbox is the best primitive in the room. AgentX takes evidence and distribution. VeloDB and Memories.ai take state, and the source half of context.

**J:** And the gaps?

**R:** Two rows come back empty. Mediation — the thing that decides whether a proposed action is allowed to happen. And process — durable execution, so a crash at tool call fourteen of thirty doesn't restart from zero and re-send the emails.

**J:** Somebody must be close on mediation.

**R:** VeloDB has a read-only MCP endpoint. Genuinely deterministic, structurally enforced, you cannot write through it. And this is the sharpest thing the research produced: it is worth almost nothing.

**J:** Why?

**R:** The same warehouse stays fully writable over Stream Load and the MySQL wire, different credentials, no equivalent gate. Enforcement attached itself to a transport, not to the agent. And that generalises: every "we gave it a read-only MCP server, it's governed" claim is an accident of which verbs one server filters, on one of several paths to the same resource.

**J:** So where does the gate go?

**R:** At the effect. Once. With every transport that reaches the resource routed through it. Not at the client, per protocol.

**J:** What surprised you in the build order?

**R:** Mediation comes third — before the loop. Most people build the loop and add policy later. Here it's concrete: EdgeOne agent endpoints are public the moment they deploy, per their own docs. Deploy before auth is in the middleware and you've published an open endpoint that spends your tokens.

**J:** Last thing. What's wrong with this research?

**R:** One real flaw, and it's in the document. AWS was scored absent on all ten planes because it funds prizes rather than setting a challenge. But Bedrock AgentCore sells identity, gateway, policy, runtime and memory — exactly the two planes I just told you nobody covers.

**J:** So your headline finding is partly an artifact of your own scoping.

**R:** Partly, yes. Strip the rule and it reads: one sponsor sells both missing planes, and you were told to hand-build one and buy the other elsewhere. Related — only AgentX was ever actually run. Every other strong rating is a documentation read.

**J:** The architecture though?

**R:** The architecture stands. The scoreboard has a thumb on it, and the write-up says so in its own limitations section — which is the only reason I'd trust the rest of it.
