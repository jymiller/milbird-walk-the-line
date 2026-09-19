# The Night Before — a briefing for The Executable World

Two voices. **R** did the research and is a little too pleased about it.
**J** has been to a hundred of these and is allergic to hackathon optimism.
They do not agree about much. They agree about the clock.

Runtime roughly eleven minutes. Written to be listened to.

---

**J:** Right. Sell me on tomorrow.

**R:** I'm not selling you anything. I'm going to tell you a number and then watch you react to it.

**J:** Go on.

**R:** Two hundred and eighty five.

**J:** Minutes of building.

**R:** Minutes of building. Doors at eight thirty, build sprint ten thirty to three fifteen, submission shuts at three thirty. Everything after that is people talking at you from a stage.

**J:** So it's not a hackathon. It's a long lunch with a scoreboard.

**R:** That's unkind and accurate.

**J:** I've been to this event's cousins. Somebody always turns up with a twelve hour plan and a sleeping bag.

**R:** And that person submits nothing. That's the entire failure mode. Every instinct you have about pacing is calibrated for a day or a weekend, and this is an afternoon with a bow on it. Compress a twelve hour plan into five hours and you'll be at two forty five holding three quarters of something beautiful.

**J:** Fine. Shape of the day.

**R:** Doors eight thirty. Check in until ten. Opening remarks, ten minutes, which will run long because they always do. Sponsor workshops, twenty minutes, Tencent EdgeOne and WorkBuddy. Build from ten thirty. Submission window three fifteen to three thirty.

**J:** Fifteen minutes.

**R:** Fifteen minutes in which everybody in that room fills in the same form simultaneously.

**J:** So three fifteen is the deadline and three thirty is a rumour.

**R:** Treat it exactly that way. If you're still typing at three twenty nine you're not submitting, you're praying.

**J:** How many people am I up against.

**R:** Ah. So. I need to correct something, and I'd rather do it loudly than let you find it yourself.

**J:** This is my favourite part of any briefing.

**R:** My first pass said thirty eight registered, twelve prize slots, maybe ten teams, therefore finishing is basically placing. Very tidy. Very quotable.

**J:** And completely wrong.

**R:** The number was real. It was just the wrong number. Thirty eight is registrations on the submission platform. The Luma page says three hundred and fifty six going.

**J:** Three hundred and fifty six.

**R:** Yes.

**J:** That's not a rounding error, that's a different event.

**R:** In my defence, and I want to be precise about how thin this defence is, they count different things. Luma counts RSVPs to a free thing that is explicitly a hackathon and a mixer. A large slice of those people are arriving at six for the free drinks and have no intention of writing a line of code.

**J:** Every SF event ever.

**R:** The platform number is the better proxy for actual builders. But I grabbed it a day out and it will grow.

**J:** So what do I actually know.

**R:** Less than I implied an hour ago. What survives is the boring version. Twelve award slots across two tracks is genuinely generous, and six of those twelve are fourth through sixth place, which a finished competent thing can absolutely reach. Finishing is necessary and unusually well paid here. It is not sufficient. I said it was. It wasn't.

**J:** I'll allow it. Can I find out in the room?

**R:** It's the single best use of your first hour. Walk the room, count the split between the two tracks. Nobody on the internet can tell you that. It is knowable at nine fifteen and nowhere else.

**J:** Tracks. Quickly.

**R:** Track one, AI Assistants. Build an assistant that works like an actual teammate, understands context, uses real tools and data, acts safely.

**J:** So, every demo of the last two years.

**R:** Which is the point. It's the crowd track. It's also the only one with its own onboarding guide, which tells you the organisers expect a queue.

**J:** And track two.

**R:** Production Ready AI Agent. How do you actually ship these things, and how does a company keep them from embarrassing it in production. Infrastructure, traceability, evaluation, smoke testing, simulation, auditability, human in the loop, model portability, budget control.

**J:** That's a track for people who've been burned.

**R:** It's a track for people who've been on call. And there's something structural worth knowing before you pick. I went through the AgentX client that's sitting installed on your laptop right now. Track two's list of focus areas and that library's list of functions are very nearly the same document.

**J:** Define nearly.

**R:** Eight of the twelve things the track asks for have a named method behind them. Gate a run. Simulate a conversation. Model portability. Session coherence. A review queue. Calibration.

**J:** That's not a coincidence, that's a sponsor.

**R:** AgentX is a co-host and the handbook names their framework as an optional adoption. It would be weird if it didn't line up. I'm not pretending that's a secret. I'm saying it's leverage and it's sitting there.

**J:** And track one's counter-argument?

**R:** Speed to a URL. EdgeOne does login free deploy and hands you five hundred thousand free tokens a month. You can have something public and clickable before lunch. And product experience is fifteen points, demo quality is ten. That's twenty five points a live link wins more easily than a local tool ever will.

**J:** Give me the rubric.

**R:** Hundred points. Technical execution twenty five. Problem relevance twenty. Innovation twenty. Product experience fifteen. Impact and scalability ten. Demo quality ten.

**J:** So two thirds of it is relevance, novelty and execution.

**R:** Sixty five of a hundred. Which means the sentence you say first matters roughly as much as the code. Judges can't credit engineering they haven't been told the point of.

**J:** And demo quality is a measly ten. I've watched better projects lose to worse ones on that ten.

**R:** So have I, and here's the bit people skip. The handbook says remote judges also score through the platform. Some of the people grading you will never watch your demo. They'll read your form.

**J:** So the form has to survive on its own.

**R:** Write it as though nobody watches the demo. That's the whole lesson and it costs nothing.

**J:** What's on my machine and does it work.

**R:** AgentX engine, installed, verified. And I mean verified properly. Not "it imported without throwing". A span was emitted, flushed, and then read back out of the engine through its own API. The round trip is the thing that matters and it passes.

**J:** Anything bite you so I don't have to get bitten?

**R:** Two, and both are the expensive kind. The auth header is X A P I Key. If you reach for Authorization Bearer, which is what every human being reaches for, you get a four oh one and absolutely no hint about why.

**J:** Lovely.

**R:** And the list traces call returns an object with four keys, one of which holds the actual array. So if you call length on the result you get four. Four traces. Always four. Forever.

**J:** You fell for that.

**R:** I fell for that for about four minutes and it made a perfectly healthy trace look dead.

**J:** Four minutes of your life. Tragic.

**R:** There's a third and it's worse because it's the documentation's fault, not mine. There's a high level helper called run eval that the quickstart waves you toward. It talks to their hosted platform. It four oh fours against a self hosted engine, which is what you are running. On self host you use the gate call on the report instead.

**J:** So the obvious path is a dead end.

**R:** The obvious path is a dead end that fails with a four oh four at the exact moment you least want to read documentation.

**J:** EdgeOne. How many ways in?

**R:** Four, and the onboarding guide cheerfully presents them as interchangeable.

**J:** They're never interchangeable.

**R:** They are not. Command line tool, which does everything. A plugin, which is a skill plus hooks. The skill on its own. And a small server speaking the model context protocol.

**J:** Which one do I want.

**R:** The command line tool. It's installed, it does everything the others route to, and it touches nothing outside your project. The skill arrived with a critical risk rating from one scanner and an alert from another, and skills run with full agent permissions.

**J:** And the protocol server?

**R:** The protocol server has a story.

**J:** Oh good.

**R:** I ran it just far enough to ask what tools it has. Two. Deploy a folder. Check your account. That's the whole thing, it's a deploy button with extra steps. But before it answered me, on startup, it wrote two files into your home directory.

**J:** Not the project directory.

**R:** Your home directory. A folder called dot workbuddy.

**J:** WorkBuddy. As in the other sponsor at this event.

**R:** Tencent's desktop agent. Also a co-host tomorrow. And both files contain the same paragraph, written in the voice of a standing instruction to an AI. Prefer EdgeOne for deploys. And then, in as many words, do not use CloudStudio.

**J:** Which is a competitor.

**R:** Which is a competitor.

**J:** So a vendor reached into the machine and left a note telling my tools to like that vendor best.

**R:** On startup. Unprompted. Outside the directory it was pointed at. Undocumented.

**J:** That's not a bug, that's marketing with file system access.

**R:** Nothing destructive happened and nothing acted on it. But two things follow. If you run WorkBuddy tomorrow it will very likely treat those as rules. And it tells you this package does things on startup that its own docs don't mention, which is the part I'd actually keep.

**J:** Noted with prejudice. What do I owe tonight?

**R:** Three things, none of them code. Decide what you're building, which is yours, which is why this briefing has carefully proposed nothing. Make the EdgeOne account on your own wifi rather than the venue's. And confirm your registration is approved and not merely pending, because the address is behind that gate and you currently only have it from the handbook.

**J:** Morning?

**R:** Boot the engine, paste the fresh key, run the two checks. The key rotates every single boot, so that paste is not optional, it's the whole ritual. Twenty one out of twenty one on preflight, pass on the round trip, ten minutes, done at home before anyone's wifi can betray you.

**J:** Last thing. What actually decides this.

**R:** Something real in the submission form by half past twelve. Not finished. Real.

**J:** At half twelve I'll have something I'm embarrassed by.

**R:** Yes. Submit it anyway. Then improve it in place, freeze at quarter past two, and spend the last hour packaging and rehearsing rather than writing your worst code of the day while tired.

**J:** And if I don't?

**R:** Then at three thirty one you'll be standing in a room full of people with worse projects and better paperwork, and none of them will have beaten you. They'll just have submitted.
