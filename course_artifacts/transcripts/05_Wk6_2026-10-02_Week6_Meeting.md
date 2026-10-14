# CIS4910 - Group 3 - Project MS2 - Senior Project Meeting (Week 6)

- **Date:** October 2, 2026, 8:35 PM
- **Duration:** 47m 33s
- **Participants:** 
  - **Sponsor (Microsoft):** Chad Hage
  - **Student Team:** Bruno Rocha, Ross Volenec, Kapil Srikanth, Joseph Bressani

---

## Executive Summary & Key Takeaways

### 1. Vibe Coding vs. Spec-Driven Development (SDD) & ADHD Demo
- **Vibe Coding vs. SDD:** Chad demonstrated the difference between plain "vibe coding" (giving GitHub Copilot a single prompt like *"Create a to-do app"*, where it runs wild without governance) versus **Spec-Driven Development (SDD)** using **GitHub SpecKit** (`specify`).
- **SDD Core Concepts:** SpecKit structures development around a **Constitution**, **Specification**, **Plan/Design**, **Tasks**, **Implementation**, and **Coverage Map**. SpecKit supports multiple CLI agents (Claude Code, GitHub Copilot, Gemini CLI, CodeBuddy, etc.), whereas Google Antigravity, Meta Muse (Spark 1.1), and Codex have their own approaches.
- **Agent-Driven Hybrid Development (ADHD):** Chad demoed his open-source Exchange Online Protection configuration repo, illustrating how he uses custom agents (`Kanban`, `Coworker`, `Cohort`, `VOC`) and reusable skills (`skill.md`).
  - **Token & Context Efficiency:** Invoking a specialized `@Kanban` agent reads specific backlog/board files directly instead of scanning thousands of repo files, saving massive amounts of tokens and preventing context pollution.
  - **Extracting Skills:** Reusable capabilities (like capturing Voice of the Customer questionnaires) should be extracted from individual agents into `.github/skills/` so all agents can share them under the governance of a Constitution.

### 2. Evaluating Security, OBO & Adversarial Testing
- **On-Behalf-Of (OBO):** Every harness acts on behalf of the developer (`OBO`) and generates visible files locally or in the repo. The team should inspect generated outputs to see if a pipeline leaks hardcoded passwords, connection strings, or database names.
- **Adversarial AI Evaluation:** Chad suggested having one AI pipeline generate the application and feeding that output into a competing AI pipeline/harness to audit it and find security holes or deficiencies.

### 3. Team Division of Labor & Task Management Insights
- **Lane Assignments:**
  - **Kapil:** Google Antigravity / Gemini
  - **Ross:** GitHub Copilot
  - **Joseph:** OpenAI Codex
  - **Bruno:** Anthropic Claude Code
- **Overcoming Sequential Bottlenecks in Kanban:** Chad shared a real-world lesson from running 12 parallel agents (4 cohorts of 3 coworkers). Initially, token usage was low and execution was slow because tasks in the Kanban board were composite/sequential, forcing 11 agents to wait on Agent #1. Reworking the Kanban agent prompt to **decompose composite tasks into atomic cards** and keeping **3 iterations of ready cards hydrated** unlocked true parallelism and exponential velocity.

---

## Full Meeting Transcript

*Kapil Srikanth started transcription*

**Bruno Rocha (0:03):** Early, I, yeah, uh, it's been a week.

**Chad Hage (0:04):** Ohh, I was gonna say, jeez, time flies, man.

**Kapil Srikanth (0:04):** Yeah.

**Bruno Rocha (0:09):** It's been a week, that's all.

**Chad Hage (0:10):** All right. So I just want to get that out of the way. I did read your posts. I did read your, you know, input. So thank you for that. It helps us use this time more efficiently because now I'm able to focus. If I want to demo something to you, if I want to share something with you, instead of using the time just to figure out what happened, we're now using the time to kind of actually unblock...

**Kapil Srikanth (0:10):** Mhm.

**Chad Hage (0:34):** ...and sprint ahead. Does that make sense?

**Kapil Srikanth (0:37):** Yeah.

**Ross Volenec (0:38):** Yeah.

**Chad Hage (0:38):** So I did want to make sure that I'm, and I mentioned last week that I would do this. So here, let me show you what I do. There are a few things that I want to share with you. So I mentioned to you SpecKit by now. Have you guys taken a look at SpecKit at all?

**Kapil Srikanth (0:52):** Yeah, yeah, a little bit.

**Chad Hage (0:55):** Yeah, so...

**Ross Volenec (0:55):** I have it on my other monitor here.

**Chad Hage (0:57):** Okay, so SpecKit, I would say that that is probably the bar, you know, and you can see it right there, right? You know, SpecKit is a spec-driven development. This is where you develop the spec. It's under the spec-driven development category. You know, now I think GitHub, it's GitHub developed, so that means it's Microsoft, right? You choose the process that you want to work with. You know, when we first put this out, it was strictly for GitHub Copilot, and as you can see now, we've extended it to all other development agents. You know, if you guys came back and said, you know, Chad, after looking at SpecKit, we think this project makes more sense to just do SpecKit with Gemini, SpecKit with...

**Kapil Srikanth (1:49):** Yeah.

**Chad Hage (2:01):** ...you know, the other flavors, right? But for now, I just want you to know that it was initially my, and that's how fast the industry is moving by the way, but my initial thought was: This is the bar, this is where we are. You know, this is how you use GitHub Copilot without SpecKit. You can create a skill, you can create an actual agent, and I'll show you that in a second. There's documentation on that here, by the way. This is like, if you just downloaded the stock GitHub Copilot and install it into Visual Studio Code, right? These are things that are out-of-the-box available to you just because you have GitHub Copilot as a harness. SpecKit takes that and elevates it to the next level for SDD purposes. Here's an article on the different SDDs that are out there...

**Kapil Srikanth (2:39):** Yeah.

**Chad Hage (2:53):** ...that I found that I want to share with you. Well, you know, you'll see that they all have the concept of a constitution, a spec, a design, some tasks, some implementation, right? Excuse me. I'm counting on noise canceling to cancel out my cough, but my allergies are killing me and I really hope that I'm not blowing anybody's, you know, eardrums when I do that.

**Ross Volenec (3:17):** You're good.

**Kapil Srikanth (3:18):** No, you're good. I totally get allergies. I have allergies too.

**Bruno Rocha (3:19):** You're fine.

**Chad Hage (3:24):** Very recently, Muse has been in the news lately, and I think Grok is also coming on the scene with a lot of automation. You know, this is where I think maybe Muse is an interesting one. Grok, I don't know how much they're doing for developers, but you know, usually typically Facebook and Meta, they have a significant amount of contribution to the developer world. So this would be an interesting one, right? Spec-driven development and Google Antigravity. So this is a Google document. So Google has something official, right? I tried to stay away from the unofficial stuff. So I just wanted to make sure I'm steering you guys in the direction that I was, you know, hoping that you'd already landed on. If this is exactly where you are, that's great. If not, then let's use this as a, you know, the moment where we all lock in. I know we got aligned, you know, week in and week out, or I mentioned the, you know, forming, storming, norming. I want to think that we're at that, you know, norming stage, you know, but at the end of the day, the proof is in the pudding, as they say, so it's going to be down to what you've been able to package up, do a demo on, and...

**Kapil Srikanth (4:39):** Yeah.

**Chad Hage (4:44):** ...you know, incrementally and gradually prepare for the actual demo on December 3rd or 4th. All right, is this helping?

**Ross Volenec (4:55):** Yes, this is giving me some ideas.

**Kapil Srikanth (4:55):** Yes.

**Chad Hage (4:56):** OK, how close are you if 1 is like totally in opposite field and 10 is spot on?

**Bruno Rocha (4:56):** Yeah.

**Chad Hage (5:07):** Just go around the table, you know, Bruno, how close are you to what I just shared?

**Bruno Rocha (5:14):** I would say maybe a 6.

**Chad Hage (5:16):** And you know, it's okay if it's a 1, because a 1 says that I'm glad we had this conversation. A 6 says, you know, welcome aboard. Now I'm expecting to be at a 9 by, you know, next week.

**Bruno Rocha (5:17):** I say 6. Right.

**Kapil Srikanth (5:29):** Mhm.

**Chad Hage (5:30):** Is that fair?

**Bruno Rocha (5:31):** So maybe a 5.

**Chad Hage (5:34):** Okay. Fair. All right. And you know, Bruno went first, so Kapil and Ross, what do you guys say?

**Bruno Rocha (5:35):** Maybe a 5.65.

**Chad Hage (5:44):** Joseph gets a little bit of a, you know, pass on this one, but...

**Kapil Srikanth (5:50):** Yeah, I would say about a 6 or 7, honestly. I think we're getting there.

**Chad Hage (5:56):** Fantastic. Fantastic. Ross, what do you think?

**Ross Volenec (6:02):** I have mixed feelings on this. I think that this project is kind of like asking two things, two main things that we need to be working on. And we've been putting a lot of time into creating a pipeline for evaluating the foundation models themselves, because I feel like, you know, the emphasis on security, the emphasis on evidence-based metrics, that's where my mind has been at, like getting actual results in a way that's automated, because like these things are moving so fast, it doesn't make sense for us to just like evaluate them once they're done. So I feel like we're doing okay on that end.

**Chad Hage (6:30):** Okay. Yeah.

**Ross Volenec (6:42):** You know, but there's also this portion here that you're sharing with us that I feel like we could be aligning better with, that we need to come up with a more holistic methodology.

**Chad Hage (6:48):** Yeah. So, do I get a number between 1 and 10?

**Ross Volenec (6:56):** I think overall, maybe a 4. I think we have some work to do to come...

**Chad Hage (7:01):** I appreciate it. I appreciate the candor. I really do. I mean, I'm glad you're, you know, you're putting it out there because if you didn't, then I would have zero ways of knowing that it's closer to a 4. Okay, so that's good. So here, let me put it in perspective, right? So this is, I call this the GitHub Copilot plain demo, right, as you can see here. Can you guys see my screen?

**Ross Volenec (7:24):** Yes.

**Chad Hage (7:24):** Yeah, so this is GitHub plain, you know, this is what happens when you download GitHub Copilot and you have VS Code. So VS Code with GitHub Copilot. So I can say, you know, and I'm using `Agent` as a mode here, and Microsoft defaults me to GPT-5.6 because I'm an employee. But otherwise, most people would probably end up on `Auto`. Yeah, here, let's put it in the `Auto`. And I might have a version that's probably slightly ahead of everyone else, if that makes sense. Not intentionally, it's just because we're on dogfood versions, okay? So if I came in and I said, hey, *"Create a to-do app for me"*, right? I just did Auto Copilot, you know, Agent. This is what most people would download, GitHub Copilot, right? Just prompt, plain. No harness, no nothing. I mean no SpecKit, no nothing, right? So while it's doing that, I mean, it's starting to create something, right? We know that. That's vibe coding. Does everybody agree that that's vibe coding?

**Kapil Srikanth (8:42):** Yes, yeah.

**Chad Hage (8:43):** Yeah, okay. So what's the difference between vibe coding and spec-driven development and engineering that's based on, you know, what I call the agent-driven hybrid development? Hybrid meaning, you know, human, either in the loop or on the loop. Right? Mind you, this is one of the pipelines. This is only one of the pipelines. The other pipelines, you know, are Antigravity, you know, Facebook Muse, whatever they call it now, Codex has their own, you know, and Anthropic Claude Code, etc., etc., right? So, we can see this thing is going, you know, and I happen to have a lot of tokens, so if it's gonna struggle, I'm gonna be fine, but if you didn't have a lot of tokens, you're probably gonna be screwed, right? So, here's where I, you know, in parallel, here's the same exact thing with SpecKit, right? Yeah. So I think I installed SpecKit here. `specify`. First of all, let me do this. Okay, so here I'm going to say `specify`. I hope that install finished. And we're going to say `todo-app`. Actually, yeah, that's fine. Okay. Oh, here. Sorry. You see what I'm saying? So here's what I just did: a GitHub Copilot plain, right? Nothing fancy, just vibe coded this, right?

**Kapil Srikanth (10:36):** Mhm. Yeah.

**Chad Hage (10:49):** Right. This right here is the SpecKit equivalent of that same exact thing. So far, so good. And what it's going to do is going to ask me, okay, which harness do you want, right? I'm going to say `copilot`. And so by the way, if I had one of the other ones, you know, I would choose the other ones where I was looking to see, you know, and that's why in the beginning of the call, I said, you know, maybe SpecKit has sort of leapt so far ahead that maybe the other, you know, companies have given up. I don't know. I'm looking forward to seeing what you guys come up with, right? It's asking me what do I want to use for shell? Do I want to use POSIX, you know, Bash shell, or do I want to use PowerShell? I'll just use Bash. What did it say? No matching release, okay. So... Let's see, did I create anything in here? I didn't create that. Meanwhile, this guy is off and running, right? It's wanting to iterate. It's going off on its own. I don't know if it's actually building what I want. It went out to the web, it found something for a to-do, and it started building stuff. You guys see what I'm talking about?

**Kapil Srikanth (11:54):** Mm. Yeah.

**Chad Hage (12:07):** Yeah, and so let's put that in perspective a little bit. So when we go back to SpecKit, what SpecKit is allowing me to do is allow me to create what's called a constitution, right? So in our constitution, we're going to actually define... They keep changing stuff. See this right here? These are the different commands. So I can say, once I initialize it for my project, I should be able to come in here and say, hey, I want to specify my constitution (`/speckit.constitution`). I want to specify that the `/speckit.specify`, that's where we start, right? But then I want to take my constitution and take my requirements and do a plan (`/speckit.plan`), then I want to break them down into tasks (`/speckit.tasks`), then I want to implement (`/speckit.implement`), right? And then I want to create a coverage map. And all this is supposed to, you know, step the project through all the different phases. Meanwhile, what's happening to my tokens, my credentials, my securables, you know, my connection strings? Does that start to make sense of how it's supposed to fit together?

**Ross Volenec (13:25):** Yes.

**Chad Hage (13:27):** I heard one yes. One out of three.

**Bruno Rocha (13:29):** Could you re-explain it again one more time? I'm a little confused.

**Kapil Srikanth (13:33):** Yeah.

**Chad Hage (13:33):** Yeah, so as I'm doing these, SpecKit has its own opinion on how it should handle, you know, my credentials. It's going to ask me, hey, you're trying to actually log in to your Azure account, to your M365 account, so can you please put your password in here? And I just put my password. Did it end up...

**Bruno Rocha (13:36):** Ohh.

**Chad Hage (13:51):** ...in a GitHub repo? Did it end up on my local machine? Did it leave my local machine, right? So that's how SpecKit does it. It has an opinion on how to handle it. How does Claude Code do it? How does Codex do it, right? When we're trying to accomplish the same things, when we're trying to take an app, something like a to-do, right? And just flow it from like, hey, you know, build me a to-do app. This is vibe coded. I didn't enter anything in here. So it's really not doing anything. It's just storing it locally. Do you agree? Right. So now here's something that I actually want to also share. So I can actually come in...

**Bruno Rocha (14:24):** Yeah.

**Kapil Srikanth (14:24):** Right.

**Bruno Rocha (14:26):** Yeah.

**Chad Hage (14:31):** ...and say `/create`... What's that?

**Kapil Srikanth (14:36):** No, nothing, nothing. I was just... Yeah, you misspelled it, so I just didn't want you to accidentally do something.

**Chad Hage (14:41):** Yeah, no worries. Um, what's going on? Okay. Let's see what's going on here. Why is it not loading? I must have done something to mine. Oh, I know why. I switched my account. I have an internal account and an external account. So it switched to my external account and that's why it's not loading my GitHub Copilot shortcuts. Anyhow, I'll switch it back in a second. But for example, when I do `/create-skill`, you know, this is something that I call... If you look at this, so where's the preview? So I call it Agent-Driven Hybrid Development, right? ADHD. And so here's an example, right? So this is a to-do list, you know, captured, and each one of these is VOC, which stands for Voice of the Customer. So these are kind of requirements intake, right? Let's see here. I want to switch to... And so for example, when I came in and I said, let's see if it's letting me, yeah, so it's only letting me create a pull request, but I should be able to create a skill. And let's see if it does it: *"Create a skill VOC, capture the voice of the customer through questionnaire. Minimum 3 questions, maximum 10 questions."* So what I'm doing here is I'm building a skill, yeah? Okay.

**Kapil Srikanth (16:37):** Mhm.

**Chad Hage (16:51):** So, I'm saying *"See VOC1 for template."* OK, let's see if it does, even though I'm not logged in with that account, it might still do it. Right. Okay. Let's see if it does it. So how do we know if it did it under the `.github` directory? I will see a `skills` folder get created and that skill will get added in it. Let's see if it does it without me having to change accounts. If it's smart enough, it will do it. And so while I was doing that, oh, there it is. You see that?

**Kapil Srikanth (17:33):** Yeah.

**Chad Hage (17:34):** There it is.

**Kapil Srikanth (17:35):** Yeah, it's gonna create `skills.md` or `skill.md`.

**Chad Hage (17:39):** It added it under `voc` and I could go on and on and on adding these all day long, right? With me so far?

**Ross Volenec (17:45):** Okay.

**Kapil Srikanth (17:46):** Yeah.

**Chad Hage (17:46):** And the same thing here with agents. So, and this guy is still going. I don't know what it's doing. It's running wild, right?

**Bruno Rocha (17:46):** Yes.

**Kapil Srikanth (17:53):** No, I think he's done, right?

**Chad Hage (17:56):** Yeah, I said create skill. I didn't specify what and what did it do? It created a skill. What does the skill do? Yeah, okay. So let's take it all into, here's a repo for example, right? So check this out. So if you go to...

**Kapil Srikanth (17:59):** Oh.

**Chad Hage (18:17):** This is my GitHub repos, right? So there's an example right here, Exchange Online Protection. So here's my repo. Right? And so this repo right here, for example, under `samples` and `scripts`, right, so these are the scripts that I created right here, so it's a Contoso configuration. If you wanted to configure your own Exchange Online, this would be a good way to, you know, kind of do all the unit testing, all the different, you know, integration testing, tell you if you have a hardened Exchange Online. If you are, you know, USF and you want to roll out Exchange Online—this is the service that gives you guys your `usf.edu` e-mail, by the way—how do you know that you have it configured correctly? How do you know that you've hardened it? And so this is the project that I've created, for example, that's doing that right now as we speak. And what I've done in here is I've come in and I've created a bunch of agents and skills and you can see this is a reoccurring theme. This is something that I've come up with. I'm not using SpecKit, but you know I can come in and I can say, you know, for example, here: `@Kanban tell me what the latest status is`, right? And so the `Kanban` is an agent.

**Kapil Srikanth (19:38):** Agents.

**Chad Hage (19:40):** That goes out and checks my backlog and checks my Kanban board, right?

**Kapil Srikanth (19:44):** Yeah.

**Chad Hage (19:46):** And so why is that important? Because if I didn't create this agent, typing this exact message right here, this prompt, what would happen?

**Ross Volenec (20:02):** They wouldn't understand the question.

**Chad Hage (20:04):** No, it would, but you know what it would do? It's going to go through my entire code base to try to figure out, am I trying to, you know, do something versus, ah, it goes in here and it reads this and it tries to use this as a prompt. Now imagine what that does to your token usage.

**Kapil Srikanth (20:23):** It would explode it.

**Chad Hage (20:23):** Giving it that same exact prompt without this agent means go scan through the thousands and thousands of files, put them in the context, figure out what it means, and then come back with an answer. Versus `Kanban` agent has exact instructions, this is the repeatable prompt, and it's going through and executing it, knowing that it's going to go and look for this Kanban file, knowing that it has to look for this backlog file, and it came back and it gave me this message. Are you guys getting what the difference is here?

**Ross Volenec (21:00):** It's much more directed.

**Kapil Srikanth (21:00):** Yeah.

**Chad Hage (21:01):** Exactly. Without this agent, my token usage would have been exponential.

**Kapil Srikanth (21:08):** Right, it would have exploded. Yeah. My instinct would have been that it would just be an inconsistent output because, you know, you don't have the agent correcting it.

**Chad Hage (21:10):** Okay. It may be, but at the same time, imagine when you're doing that with something that needs credentials. Imagine when you're doing that with something that needs, you know, a connection string, right? Imagine when you're doing that with something that needs a certificate. You have no control over how the model is going to reason based on your prompt versus this gives you the Constitution—in the case of SpecKit, SpecKit calls it a Constitution, right? Why is it a Constitution? Because it has actual, you know, contracts, right? So, here what I've done is I've created a contract called `Kanban`, a contract called `Coworker`, and a contract called `Cohort`. So, check this out when I come in and I do one of these. Can you guys see my screen right here?

**Kapil Srikanth (22:05):** Yeah.

**Ross Volenec (22:05):** Yes.

**Chad Hage (22:06):** So I said, I'm going to start 4 cohorts. Well, gee, what's a cohort? Let's go check it out. This is a cohort. Cohort has 3 coworkers, right? And it's expecting me to say the name of the cohort, the word `start`, and it gives it an example. So these are all the things that are passed into the cohort. And when I do that, check this out. I just activated $3 \times 4$, right? So 12 agents that are working right now, and check this out, they're all working...

**Kapil Srikanth (22:33):** Mhm.

**Chad Hage (22:41):** ...simultaneously in parallel because I fine-tuned this prompt to allow me to do that. Otherwise, if you did something like that, it would go and try to look for your word "cohort" in your code base. And especially let's say you're doing a project where the word "cohort" is an actual business entity, and it will be all over the place, as you can imagine. OK. Is this helping?

**Kapil Srikanth (23:06):** Yeah, yeah.

**Ross Volenec (23:06):** Yes.

**Bruno Rocha (23:07):** Yes.

**Chad Hage (23:08):** Okay, so what does Meta Muse with, you know, with the Meta, what do you call it? So Meta has Spark, right? So Spark 1.1, how does Spark 1.1, you know, handle all this? And how does the Google Gemini with Antigravity handle all this? You know, and that's where I was looking for your creativity with your, you know, originality and what I've shown you so far to see how we can bring this to fruition. I know that you can use GitHub SpecKit with all sorts of, you know, agent coders. The reason why I know that is because SpecKit tells us so, right? The folks at SpecKit tell us that you can use it with all these different... where is the installation? Yeah, look at the prerequisites right here. So you can do Claude Code, GitHub Copilot, CodeBuddy, Gemini, but these are CLI. Notice that they're not integrated with the IDE. Aha, so how does SpecKit inject itself in CodeBuddy and Gemini is through the CLI, which means if you're in the IDE on those tools—and by the way, like Gemini and Antigravity is not even, I don't know if there's a dedicated IDE or if it's in the browser—but anyway, in here, it's going to be through the CLI, the Pi coding agent, and Oh My Pi are the ones that are supported. So Codex is not on the list. So how does Codex do it? How does Meta Muse Spark do it, right? Is this starting to make sense?

**Kapil Srikanth (25:10):** Yeah.

**Bruno Rocha (25:11):** Yeah.

**Chad Hage (25:12):** Is it a hittable target?

**Ross Volenec (25:13):** The different...

**Chad Hage (25:18):** Do you guys think you can hit this target or is it still like a moonshot?

**Ross Volenec (25:24):** I've been...

**Bruno Rocha (25:24):** Uh.

**Ross Volenec (25:25):** ...thinking about this a lot this week, about how we can compare different dev-facing interfaces, tools, whatever you want to call them, harnesses. The only thing that comes to mind right now is just throwing a feature matrix at these things, and you know, like a weighted scoring system with that.

**Chad Hage (25:45):** Yeah.

**Ross Volenec (25:46):** But I'm not sure how exciting that sounds, but...

**Chad Hage (25:48):** Well, I mean, that's a start. We evolve from there. And here's the other thing, by the way, guys, check this out.

**Kapil Srikanth (25:48):** Yeah.

**Chad Hage (25:54):** Every one of them are going to have to show you what they're generating. Nothing is going to do anything in secret. Whether you do a vibe coding, single prompt, no framework whatsoever, they have to generate the file because it's doing it on your behalf. Everything in here is OBO. Okay, On-Behalf-Of, on behalf of who? On your behalf, on behalf of the actual developer. Is that making sense? So all these things are doing are generating stuff. Right, and so if it generates something and you go into what is generated and you see the hardcoded password, well, that's an "oh shit" moment, right? If you see a hardcoded, you know, database name. Right. And so I think when you start running these pipelines, when you start running—and I call it a pipeline because it's the harness, it's the SDD kit, you know, and then it's whatever the LLM that's downstream of it, right? So if you're using, you know, the Gemini one, Gemini Flash as the model with Antigravity as the IDE, right? What is the SDD?

**Kapil Srikanth (27:03):** Mm-hmm. Mhm.

**Chad Hage (27:14):** And by the way, Google does have one. I showed you earlier, right? It's in my post. So if you go to my post, I've pointed out the ones that I was able to find. But yeah, so they're going to generate something and you're going to be able to see it. You're going to be able to inspect it. In fact, I would like for you to at least, you know, use the LLM to inspect its own output because it's going to generate so much crap, right?

**Ross Volenec (27:43):** Mhm.

**Chad Hage (27:43):** So why don't you do like a, you know, it would be really awesome if you guys feel like you're inclined to it. You know, what would really be cool is generate something with Muse Spark and give it to, you know, SpecKit or give it to GitHub Copilot and tell it to break it, find all the holes in it.

**Ross Volenec (28:05):** Mhm.

**Chad Hage (28:05):** I don't know; it'll be fun.

**Ross Volenec (28:08):** Have an adversarial layer, I guess.

**Chad Hage (28:10):** Yeah, yeah, let them go at each other. Let them point out where the actual deficiencies are.

**Kapil Srikanth (28:10):** Yeah, that is pretty intuitive. You know, when people use AI, usually they ask one AI to do something and then they ask the other AI, how bad does it suck?

**Chad Hage (28:20):** OK. Yeah. So you might want to start with that. But I wanted to make sure that we're bringing it closer to where, you know, you're able to, and I understand the first couple of weeks, the first three weeks, you had to get the SRS nailed down, you had to get some, you know, housekeeping stuff done. Right. That's, I don't know how much of that we still have pending, but I want to get about 10,000-foot altitude. What's that?

**Ross Volenec (28:59):** We have a detailed design document two weeks out.

**Chad Hage (29:05):** Okay. Is this helping?

**Kapil Srikanth (29:10):** Yeah, yeah, for sure.

**Ross Volenec (29:10):** Yes, this is giving me a better idea of how to approach this.

**Bruno Rocha (29:11):** Yes, yeah.

**Chad Hage (29:14):** Okay, and see, now that I've put that in perspective, this is where my, you know, imagination in the beginning, before meeting you guys and getting to know you, you know, you're extremely bright individuals, but I had no idea who I was going to be working with. So I was like, it'll be really interesting to see if the group ends up deciding to, you know, divide and conquer. Hey, I'm going to take, you know, Muse Spark, you take the Gemini SDD, you know, Ross takes, you know, the GitHub Copilot plain, and then, you know, Joseph takes, I don't know how you guys wanted to split the, you know, split the baby sort of thing, right? Or do you say, hey, I'm gonna focus on security, you focus on connections, you focus on, I don't know. So this is where I was looking for you guys to come back and say, hey, we've looked at this and it makes more sense for each one of us to do a layer across or to own one pipeline from A-Z and tell you, you know, what we found. That's up to you.

**Kapil Srikanth (30:26):** Yeah, I mean, that's where we were kind of going, you know, in our doc, like we define each one of us as like one specific, like, I'm Google, Ross is Copilot, right? GitHub Copilot.

**Chad Hage (30:41):** OK.

**Kapil Srikanth (30:47):** Bruno is Codex and Joseph is, oh no, Joseph's Codex, Bruno is Claude. So yeah, that's how we were planning on, that's how we decided to split.

**Chad Hage (30:54):** Yeah, yeah, if you want to do it vertically versus horizontally, that's totally up to you. And I have, you know, I want to know why, but I'm not going to steer you one way or another.

**Ross Volenec (31:08):** I think we're going to have to end up with a little bit of a hybrid approach there, where we each have our lane, but like if we start like collecting features for comparison, there may be a time one person finds a feature that the others don't have, and you know, we'll have to come back and figure that out.

**Chad Hage (31:24):** Oh, sure. Yeah, yeah. I mean, I'm expecting you guys to collaborate at the end of the day, but this is a collaboration. I mean, here's the thing. If you do this and you do this well, you're going to have such a deeper experience with the various pipelines that are on the market today. You know, and I'll be a little jealous because I get to play around with GitHub Copilot all day long. That's where I work. That's who Microsoft tells me I need to, you know, become well-versed in. You guys will have gotten at least, you know, first level, maybe second level, third level, even across multiple, you know, of these pipelines, and I think that's awesome. I think it's a lot of fun, but yeah, cool.

**Ross Volenec (32:23):** I have one question before we wrap up here. Yesterday we talked a little bit about task management and just like keeping milestones. I was wondering if you had any insights about, you know, like any ideas that you have as a professional about how you approach handling tasks within teams.

**Chad Hage (32:40):** Are you talking about tasks across the four of you or help me understand what you mean by tasks?

**Ross Volenec (32:45):** I think Joseph was talking about like a Kanban approach where we would, you know, like have a list of tasks and be able to see who's assigned to what.

**Chad Hage (32:54):** Yeah, you know, I'll be frank with you. The idea of... That's really a tough question because up until recently, about say probably maybe two, three years ago, the concept was the ideal team size was no less than 3, no more than 10, right? If you've ever read the Scrum Guide, if you ever read any of those documents, they said, you know, don't put too many people on one team because the communication lines start crisscrossing. But too few, you're not really building a team. You're just trying to get people to get along. You know, like if two people cannot get something done, they just have, you know, they don't like each other. Right? When you get to three people, that's when you really have a team. That's how the Scrum Guide describes it at least, right?

**Kapil Srikanth (33:34):** Mhm. True.

**Chad Hage (33:48):** And one of the things that I started noticing when I first started doing agent-driven development or spec-driven development or agent-driven, you know, hybrid development, as I call it, is that I realized very quickly. So right now, for example, this code base right here, which is public, by the way, you can go and grab this. This is all, you know, under open source, this Exchange configure it. Nothing in here is secret, it's all open source. So I'm collaborating on this with one more person who is on my team, but each one of us has...

**Kapil Srikanth (34:11):** Yeah.

**Chad Hage (34:22):** ...12 of our own agents working simultaneously. We've got like 24 agents working at different intervals, right? And so it becomes kind of the, and what I noticed in here, and I know I'm probably giving you a long-winded answer to your question, but there is a Kanban file. The concept of Kanban is here, right? So as you can see, the Kanban is constantly being refreshed and updated.

**Ross Volenec (34:30):** Mhm.

**Chad Hage (34:45):** And there's a lot of stuff in here, you know, that was added every single time we ran this. One of the things that was really interesting was that the Kanban agent, right? So this Kanban agent is the one that said, I ran the cohorts in parallel and I noticed it was taking too long to finish a round. And then I was doing some investigation and it said, well, the Kanban, your board is not set up for parallelism. Right? And in my mind, it's like, what do you mean it's not set up for parallelism? Of course, I want to set it up for parallelism, right? And so what it was doing, even though I had a board, I had items on the to-do list and the to-do bucket, until the first item finished, it couldn't start on the second item. And I had 12 agents waiting for agent #1 to finish.

**Ross Volenec (35:20):** Mm.

**Kapil Srikanth (35:25):** Okay.

**Ross Volenec (35:41):** The sequential bottleneck.

**Chad Hage (35:43):** Exactly, right? And then it was like, I would have never figured that that was the reason why tasks were taking too long. I thought the work was a lot. And it turns out it's just the way I had set up my backlog and my Kanban, right?

**Kapil Srikanth (35:43):** Yeah, it's very inefficient.

**Chad Hage (36:00):** And I did a little bit of investigating and it said, yeah, that's why it's taking too long because I have to wait until this one finishes, then I pass it on and so on. So I then spent some time and, you know, reworked the prompt for the Kanban agent so that it now has as part of its skill, right, the ability to identify items in the to-do bucket that are composite and decompose them into atomic cards. I don't know if what I'm saying is helping, but I ran into this because I'm like, now that I've solved it for me, how is it affecting my buddy who's in Dallas who's working on the same code base?

**Ross Volenec (36:47):** Mhm.

**Chad Hage (36:47):** Right, so far, what we've done is, and I use this concept here, as you can see, you know, I use the colors on this project; on another project, I use a different theme, I use city names instead of colors, right? And so what we do is we make sure that our board, our Kanban, right, actually one of the rules in our Constitution is to always have 3 iterations, cards ready for 3 iterations for up to 4 cohorts. So as it consumes the cards from the backlog, right, there is another agent that's constantly hydrating the to-do list with ready-to-go items. I don't know if that's answering the question you asked about, because I think you're asking more about the four of you, but it's a model for...

**Kapil Srikanth (37:41):** Mhm.

**Ross Volenec (37:50):** I think that does apply. Yeah, I hadn't really thought about, yeah, but like breaking down the tasks atomically does make sense.

**Chad Hage (37:54):** Yeah, you're just human versions of my agents. There's 4 of you, it's a cohort. Sorry, I didn't mean, you know, to offend you, but that's all you are to me. I'm just kidding. Right? You're just cooler, prettier looking versions of what I'm running in my cohorts. Yeah, I don't know if this is giving you any ideas...

**Ross Volenec (38:01):** Yeah.

**Chad Hage (38:17):** ...of how to tackle that. I'll be interested and I'll be curious, because that was one of the things that I wanted to uncover. Like, you know, I'm at a point right now, and I kind of questioned, like, am I going to go faster? I asked my buddy, who is a subject matter expert on this particular topic. He is an architect on this topic. And I asked him to take a look because I wanted to make sure I'm not introducing, you know, things inadvertently. And it turns out that he started seeing some things that he wanted to add. So now we're both collaborating. And, you know, so far we haven't had any collisions. But I would love to see what you guys come up with.

**Kapil Srikanth (39:02):** I had a question. So you mentioned that, you know, there is this huge bottleneck happening where everything was stalling. How did you find out that was the problem? I know you mentioned earlier that it's all public, like it tells you everything. But so I was just wondering how you managed to find it.

**Chad Hage (39:15):** Yeah, so that's a good question. When I saw the amount of time that it was taking to finish, you know, a card, and the amount of time it took to finish 12 cards, because of the duration, I was expecting my token usage to be through the roof. I'm like, these must be really expensive cards.

**Kapil Srikanth (39:41):** Okay. Right.

**Chad Hage (39:45):** And I went and checked my tokens, it was like minuscule. I'm like, what? What's going on here? You see what I'm saying?

**Kapil Srikanth (39:52):** Yeah, so that alerted you there was something you looked into, but how did you look into it?

**Chad Hage (40:00):** Well, I mean it worked for like half an hour and I was like, oh my god, my token usage has got to be...

**Kapil Srikanth (40:03):** Uh-huh.

**Chad Hage (40:07):** ...huge now, right? And I went out there and I was like, no, there's no token usage. I'm like, what the hell is it doing?

**Kapil Srikanth (40:09):** Yeah.

**Chad Hage (40:14):** And I started to ask, I mean, I asked the, you know, my Kanban agent, I said, you know, what were the tasks? How long did each task take? You know, I looked at the timestamp and it showed that it was sequential.

**Kapil Srikanth (40:31):** Oh, okay, so that's how you found out, you asked the agent. Okay, that makes sense.

**Chad Hage (40:34):** Yeah, yeah, yeah. I mean, I asked it to show me the metadata, right?

**Kapil Srikanth (40:41):** Yeah.

**Chad Hage (40:44):** But yeah, it was a lot of fun to uncover that because like I felt like I cracked a nut, which I did. And just to put it in perspective, guys, like this is where we're at now, right? So this particular one here, so check this out. This has 58 Done and 48 To-Do. So we're about a little bit past the halfway mark, right? And the rule is there's never going to be anything In Progress. When it's done, when it finishes, it finishes. If there's one in progress, then the next cohort goes and pulls. If there are less than two in progress, then no one pulls.

**Kapil Srikanth (41:07):** Right. Mmh.

**Chad Hage (41:20):** You see what I'm saying? So it's the prompt to set up the, you know, and you could get a little fancier if you want to introduce like, you know, Python scripts, things that are more, you know, controlled, you can do that. But yeah, so this is at 48 / 58. This was for the longest time, like 90-something...

**Kapil Srikanth (41:22):** Yeah.

**Chad Hage (41:40):** ...you know, to 13 or whatever. And then when we did the pruning and I said, can you remove the, you know, things that are causing dependency, it actually found some things that it could throw away. It was like, now that we want to do it this way, well, I no longer need this and I no longer need that. And that's how we ended up with the number that we have right now.

**Ross Volenec (42:03):** ...things a bit.

**Chad Hage (42:03):** Yeah, but the amount of the velocity was exponential. Okay.

**Kapil Srikanth (42:12):** Yeah, makes a lot of sense.

**Bruno Rocha (42:13):** Yeah.

**Ross Volenec (42:16):** Yeah, thanks for the demo, Chad.

**Chad Hage (42:18):** Yeah, that's why, you know, maybe it makes a little bit more sense now, why from the get-go I was, you know, insisting that whatever app you guys decide to use as your guinea pig is irrelevant, right?

**Kapil Srikanth (42:29):** Mhm.

**Chad Hage (42:30):** You know, on one of the other ones that I've created, I decided to separate my, not this one... Is it this one right here? Yeah, so for this one, what I've decided to do is separate my Kanban, right, into what I took out: I started extracting skills out of the actual agents, because I created agents at first, right? And then I said, you know, extract all the reusable skills out of each agent. And so now what it's doing is going through and any skill that is not exclusive to one agent, it starts to push it out into the actual `skills` directory. And when that happens, now you're able to let the other agents use a reusable skill, which is why the Constitution becomes even more important.

**Kapil Srikanth (43:22):** Mhm.

**Chad Hage (43:31):** Because you don't want these agents to just like, oh, I have a skill, let's go use it. Maybe it should, but is that right? I don't know, depending on the project.

**Kapil Srikanth (43:37):** Yeah.

**Ross Volenec (43:41):** Right.

**Chad Hage (43:42):** Make sense?

**Kapil Srikanth (43:42):** Mhm. Yeah.

**Chad Hage (43:45):** All right. Questions, comments?

**Ross Volenec (43:51):** I hadn't really encountered this in my own, like, AI agent experience, so this has been informative.

**Chad Hage (43:58):** Yeah, in the beginning I was just using a document to capture all my, you know, voice of the customer, you know, and there's just a log, you know, and then here you can just go and see the, you know, but I was like, okay, maybe I should not be doing this manually. Let me create an actual agent. And I was like, wait a minute, I don't want the voice of the customer to be an agent. I want it to be a skill. So I said, extract this and make it a skill. So now all my agents can reuse this skill. Is that making sense?

**Kapil Srikanth (44:29):** Yeah.

**Chad Hage (44:29):** Agent-skill, you know, relationship.

**Ross Volenec (44:32):** And I see you included the "create a skill for an agent" Ignite article. I need to look through this as well.

**Chad Hage (44:38):** Yeah, yeah. Take a look. Any questions come up, guys, keep the, you know, conversation going. I hope you're seeing the benefit and the value of having the, you know, the dialogue happen through the GitHub issues. I would say my experience so far is where these skills start to reach their limit is when you want to exercise a very specific MCP that GitHub Copilot itself or that VS Code is unable to actually tap into. So what do I mean by that? So as you can see here, for example, right? So this is what we call the Microsoft 365 Agents Toolkit. With it, I can build, you know, custom agents where you go beyond just the `skill.md`. With `skill.md`, you're going to be able to get any harness, any agent to use the actual GPT concept, right, to translate what you're saying into something that it can then present to an MCP. You guys clear on that when I say that? But let's say that something that you want done is not available to an MCP. What do you do then, right? So this is where you start looking at maybe Agents Toolkit, maybe building custom MCPs with some wrappers, stuff like that. I'm not asking you to go that far, but the primary objective of this project was to see how does Meta Muse Spark, how does Google Gemini Antigravity, or whatever IDE from Google, compare to, you know, the pipeline from Microsoft, which is GitHub Copilot, VS Code, and GitHub.

**Kapil Srikanth (46:21):** Mhm.

**Chad Hage (46:26):** And some, you know, usually Azure is the target, right? You can deploy them all to Azure. I mean, none of them are gonna fuss up. I mean, obviously, Gemini is gonna favor GCP.

**Kapil Srikanth (46:31):** Mhm.

**Chad Hage (46:40):** You can set up a free subscription on GCP. Oh, I feel like I'm leaving one out. Oh, the AWS one. You know. Makes sense?

**Bruno Rocha (46:55):** Yeah.

**Ross Volenec (46:56):** Yes.

**Chad Hage (46:56):** All right. Any questions, comments? Are we good to adjourn?

**Bruno Rocha (47:02):** I think so.

**Kapil Srikanth (47:03):** Yeah.

**Ross Volenec (47:04):** Excellent.

**Chad Hage (47:04):** Alright. Well, gentlemen, enjoy the weekend and look forward to seeing what you come up with by this time next Friday. In the meantime, keep the conversation going.

**Bruno Rocha (47:16):** Yes, sir, you as well.

**Kapil Srikanth (47:16):** Yep, will do. We appreciate the demo. Get better soon, Chad.

**Ross Volenec (47:16):** All right. Thank you, Chad. Enjoy your weekend.

**Chad Hage (47:21):** Thank you. I appreciate it. Take care.

**Bruno Rocha (47:22):** Yeah. Take care. Bye.

**Ross Volenec (47:22):** Yeah. Bye.

**Kapil Srikanth (47:25):** Bye.

*Kapil Srikanth stopped transcription*