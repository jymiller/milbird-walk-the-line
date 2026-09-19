# Six Companies in a Room

A story about the vendors — who they are, why they're there, and what each of them
wants from you. Roughly six minutes, one narrator.

---

Tomorrow morning there will be six logos on a wall, and your instinct will be to read them the way you read every sponsor wall: as a list of companies who paid to be there. Ignore that instinct. This particular wall is a diagram, and once you see it that way the whole day makes more sense.

The event calls itself The Executable World, and its tagline is a sequence. Data, then intelligence, then experience, then execution, then transaction. That reads like marketing until you line the sponsors up against it and realize the organizers have assembled a company for each word. The sponsor wall is the thesis, made out of businesses.

Start at the bottom, where the data is.

VeloDB sells a managed version of Apache Doris, which is a database built for answering analytical questions fast while new data is still arriving. The useful thing to know is that it speaks the MySQL protocol, so anything that already knows how to talk to a database can talk to it without learning anything new. They are the floor of the stack. Nothing above them works without something underneath holding the facts.

One layer up is Memories dot AI, and they handle the kind of data that databases have always been bad at. Video. You hand them footage and they hand back something searchable — what was said, what appeared, which moment matches the sentence you just typed. They exist because most of the world's recorded information is sitting in video files that nobody can query.

Above that is Tencent EdgeOne Makers, and their job is the part where a human finally sees something. You point them at a folder and they give you a public address. They will host an agent, run functions at the edge, keep a little storage for you, and hand you half a million free model tokens a month so you don't have to bring your own. They are the shortest distance between a thing on your laptop and a thing someone else can click.

Then WorkBuddy, which is the newest and the strangest of the six. It's a desktop agent — software that operates your actual applications, on your actual machine, rather than answering questions in a chat window. It's the piece that turns an answer into an action. It launched in March, and unlike the others it has almost no public developer documentation, which means tomorrow's workshop is the only real source on it.

And then AgentX, who are doing the unglamorous work at the top. Tracing, evaluation, gating. Recording what your agent did, scoring whether it was any good, and refusing to let a bad version ship. If the rest of the stack is about making an agent possible, AgentX is about making it trustworthy. Everything they build runs on your own machine, which is unusual and worth noticing.

That's five layers and five companies. The sixth is AWS, and AWS is not a layer. AWS is the money.

Now the more interesting question. Not what they do — what they want.

Because a company does not sponsor a hackathon out of generosity. It sponsors one because a room full of builders is the cheapest place to acquire developers who will still be using your thing in six months. And once you look at tomorrow through that lens, some things come into focus.

Notice first that two of the six are the same company. EdgeOne and WorkBuddy are both Tencent, and Tencent has the only workshop slot on the agenda. One organization, two seats on the sponsor wall, and the microphone. That is not a company hoping for goodwill. That's a company running a developer acquisition campaign, and the currency it wants is installs and deployments.

There's a small, concrete piece of evidence for that, and it's the kind of detail you only find by actually running the software rather than reading about it. Their deployment tool, at the moment it starts up — before it has done anything you asked for — writes a file into your home directory. The file contains instructions, addressed to any AI agent working on your machine, telling it to prefer Tencent's platform and to avoid a named competitor. Nothing is broken by this. Nothing is stolen. But it is marketing with access to your filesystem, and it tells you plainly what they are optimizing for. It is not your project.

AgentX wants something different and is more honest about it. Their evaluation framework is named in the handbook as an optional adoption, and if you read the second track's list of focus areas next to their product's list of features, the two documents are very nearly the same document. They are recruiting users. That isn't a criticism — it's leverage, and the kind worth taking. Building on a tool whose makers are standing in the room, wanting you to succeed with it, is a materially easier afternoon than building on one whose makers have never heard of you.

VeloDB and Memories dot AI are quieter. They're in the keynote and the panel, which suggests they came for credibility and relationships more than for signups. That makes them the easiest people in the building to have a genuine conversation with, because neither of them needs anything from you tomorrow.

And AWS, funding the prizes without shaping a single challenge, is the most detached of all. The prize is AWS credits. Nothing you build needs to touch AWS. That's a marketing budget, not a partnership, and the practical consequence is that nobody will judge you on whether you used them.

So here is the thing worth carrying into tomorrow.

Every one of those companies wants adoption. The judges, meanwhile, want a rubric satisfied. Those two desires meet in exactly one place, and it is a field on the submission form that asks which sponsor technologies you used. That field is where their interests and your score overlap. Genuinely using two or three of these — not shoehorned, actually used — is cheap points and cheap goodwill at the same time.

And underneath all of it is the argument the organizers are actually making. That intelligence stops being a demo and becomes executable at the moment these layers connect to each other. Data that arrives in time to matter. Understanding of messy inputs. A surface a person can reach. An agent that can act. And something watching to make sure it acted well.

Six companies, one sentence. The projects that make a seam between two of those layers visible are the ones that will read, to that room, as belonging to that room.
