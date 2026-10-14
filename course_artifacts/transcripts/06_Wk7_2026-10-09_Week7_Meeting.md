# CIS4910 - Group 3 - Project MS2 - Senior Project Meeting (Week 7)

- **Date:** October 9, 2026, 8:26 PM
- **Duration:** 1h 10m 29s
- **Participants:** 
  - **Sponsors (Microsoft):** Chad Hage, Bradley Lawrence
  - **Student Team:** Bruno Rocha, Ross Volenec, Kapil Srikanth, Joseph Bressani

---

## Executive Summary & Key Takeaways

### 1. Chad's Live "ADHD Factory" End-to-End Demo
- **Factory Launcher (`factory-launcher`):** Chad demonstrated his updated `ADHD` GitHub template repository, which now includes a full multi-agent software factory (`VOC`, `product-owner`, `associate-product-owner`, `kanban`, `full-stacker`, `squad`, `factory`, `factory-launcher`) and extracted skills (including **Weighted Shortest Job First (WSJF)** prioritization and **Chronicle Tips** for tracking token/AI credit usage per card).
- **Live 1-Hour Build:** During the meeting, Chad ran `@factory-launcher` with the prompt: *"Create the most impressive to-do agentic app with an M365 Agent SDK integration."* Over the course of the 1-hour call, the factory interviewed Chad, generated BDD/TDD specs, hydrated a Kanban board, wrote the backend/frontend/M365 agent code, generated Azure deployment scripts, and **automatically launched Playwright to run a live interactive demo** of both the M365 Agent and Web UI with >85% test coverage.

### 2. Student Team Updates & First Benchmark Demo
- **Detailed Design Document (DDD) & Updated SRS:** Bruno and Joseph shared the updated High-Level Architecture (HLA) Mermaid diagrams and constraints section for the DDD (due the following Sunday, presenting Friday).
- **Feature Matrix:** Ross created an agentic specification that parses official platform documentation across 7 categories for baseline IDE/CLI capabilities (starting with VS Code Copilot and Copilot CLI).
- **First Benchmark Demo (`benchmark-start-v1`):** Kapil demonstrated the team's first live benchmark test on the baseline To-Do app:
  - **Task:** Read `add-delete-endpoint.md` to implement a `DELETE` task endpoint and UI button.
  - **Anti-Cheating Harness:** The 9 acceptance criteria tests were placed *outside* the agent's accessible directory so the harness could not fake or modify the tests to pass.
  - **Initial Empirical Results:** Both **Google Antigravity** (defaulting to Gemini Flash 3.8) and **GitHub Copilot CLI** (auto-selecting GPT Luna 5.1) passed all 9 tests. However, **Copilot completed the task in ~1 minute**, whereas **Antigravity took ~6.5 minutes**. Codex and Claude Code were also tested and were much faster than Antigravity.

### 3. Sponsor Coaching: "Always Be Demoing (ABD)"
- **ABD Mindset:** Chad emphasized **"Always Be Demoing" (ABD)** every single week—or even mid-week by posting a recorded video link in GitHub Issues on Tuesday for Wednesday feedback. Citing **Parkinson's Law** (*work expands to fill the time allotted*), Chad encouraged the team not to wait until demos are "pretty" or "perfect," as an early demo that reveals a wrong direction is even more valuable for course correction.
- **M365 Copilot & WorkIQ:** Brad and Chad shared how they use M365 Copilot with WorkIQ to summarize weekly accomplishments, track Kanban timelines from emails/Teams/OneDrive, and query enterprise-wide knowledge. (The students checked their USF accounts and found they have `Copilot Chat Basic`, which lacks WorkIQ OneDrive integration, though they can still attach Excel/task lists manually).

---

## Full Meeting Transcript

*Kapil Srikanth started transcription*

**Chad Hage (0:04):** Let me see. Is this it? Wait a minute, which one is this one? Okay, so... Yeah, check this out. So it's a little clunky, but here, let me share my screen. So by now, you guys saw this repo that I shared with you...

**Kapil Srikanth (0:40):** Yeah, from last week, yeah.

**Chad Hage (0:40):** ...that I call ADHD, right? So ADHD, you know, Agentic-Driven Hybrid Development, it's a play on words. I actually did a significant push to what's in here. So you'll see that right now, everything's been moved under `agents`, and this is kind of like all the different agents that you get in here. So there's a `voc`, `product-owner`, `associate-product-owner`, `kanban`, `full-stacker`, `squad`, `factory`, `factory-launcher`. `factory-launcher` was a big, you know, move—it blew my mind what it actually ended up doing. So the skills that I extracted are in here, right? And so anyway, and by the way, I marked this as a template in GitHub, right?

**Kapil Srikanth (1:24):** Mhm.

**Chad Hage (1:39):** So when I want to start a new project, and you can see, like, way up here, all it is is that you run `factory-launcher`. You guys see my screen?

**Kapil Srikanth (1:51):** Yes, sir.

**Chad Hage (1:52):** Yeah, so `factory-launcher`, it launched this. And by the way, `factory-launcher`, the agent has the skill to determine whether it's a new factory that you're launching versus an existing factory that it's resuming. So in this case, it determined that it was a brand new factory, you know, and all I did was I cloned—obviously, as you can see, it's cloned in here, right? And so it started, you know, the interviewing process and it asked me like, what am I trying to do? Blah, blah, blah. It took like the narrative of the business idea or the, you know, the vision, right? So, as you can see, a bunch of interviews and then it said, okay, now... It took about 24 steps, 23 minutes, 4 seconds in total, and then boom, right? So what did that look like when it was done? It created this thing called `ci-agent`. This was all generated by the `factory`, the `squad`, the `full-stacker`—an actual agent that runs in M365, runs on a web app. Let me see here. Maybe I should stop sharing because I might switch to some things first. But let me see... Yeah, here is the actual... So, this is actually the demo of that agent running in the emulator, by the way. It was all generated by `factory` with running the `factory-launcher`, anyway. So yeah, but this is a pipeline or a factory, if you want to call it a factory, that is built right now specifically for GitHub Copilot and GitHub, VS Code specifically, right? So if I take these agents and these skills, port them over to Claude, they may do nothing. I don't know. I'm betting they will do something, but it will be completely underwhelming. Right? Versus, you know, here, let me show you what I would mean by that. So... Here, let's do a to-do app. Right, let's call the app `todo-app`. Okay, so now all I would need to do is... If I go in here, I guess I can just go on, if I'm doing it correctly, if I'm following, you know, the steps properly, I would go into GitHub and clone it. Yeah, let me do it correctly. All right, so we're going in here. And let's just do `factory-launcher`. Sometimes it's fast getting all the sign-ins and everything out of the way. Sometimes...

**Kapil Srikanth (6:55):** Mhm.

**Chad Hage (6:57):** ...it takes its sweet little time. I'm not going to subject you to all these, because it is somewhat a lengthy process, but... So there you go. So it says, okay, you're trying to create a new factory. Explain what it refers to, rename the existing app. I'm going to say, create a new `factory-launcher`. Oh, it didn't initialize. Wait a minute. It did not initialize those agents. Yeah, they're in here.

**Kapil Srikanth (7:33):** What's that? Ohh, they are. Is it because do you have to type it like `factory-launcher`?

**Chad Hage (7:38):** Okay. No, no, no. It's just still not finished initializing. I'm going a little too fast for it.

**Kapil Srikanth (7:44):** Okay. I see.

**Chad Hage (7:50):** Yeah, here, let's do that. Stop it. And you know what I'm going to do? One thing that I noticed helps it a lot is if I come in here and I do `git init`. There it is. Right. So now... Let's see. See, it's still trying to load. Okay. So one of the things that you also have to be on the lookout for is where you're running your... Yeah, they changed this. Because this is supposed to be running `Local`, because right now it's not seeing the agents.

**Kapil Srikanth (9:12):** Right.

**Chad Hage (9:15):** And okay. Yeah, see, none of the agents loaded, that's why. I notice it does take a little bit of time for it to finish initializing this repo or initializing this directory. But once it initializes it, it will then start seeing the agents. Let's try it one more time. There we go. Finally, I found the agent. Take a minute. There you go: *"Create the most impressive to-do agentic app with an M365 Agent SDK integration"*, right? Something like that. So right now what it's doing, it's going and delegating all the different tasks to the different sub-agents that are in there. There you go. So it's asking me if I want, you know, to name a workspace so I can save the actual files that are going to be generated. And we'll just go through and ask a bunch of questions. Like the other demo that I showed you, it took about 24 minutes worth of questions and answers back and forth.

**Kapil Srikanth (12:57):** Mm-hmm.

**Chad Hage (13:02):** And then it started generating the test-driven development. It started with the documentation, BDD, TDD, test coverage, and then generated the code. I'm just clicking through here, by the way, guys. Otherwise, I would typically spend more time thinking through the answers.

**Kapil Srikanth (13:26):** Mhm.

**Chad Hage (13:27):** But yeah, so it goes through and methodically produces, you know, an actual code base that is production-worthy, in other words. Okay.

**Kapil Srikanth (13:41):** So when you're clicking through, does it also like ask about permissions and stuff? Because when I was doing the testing, yeah, Antigravity was just asking me, am I allowed to run `npm test` and whatnot? So okay, it's like that.

**Chad Hage (13:45):** Yeah. Absolutely. Yeah, then it will actually capture. So one of the steps in here when you go through this, it will actually present you with like a contract, like, hey, this is what you've agreed to. And it will use it as a sign-off and then it will record it and then it will go and start building off of it.

**Kapil Srikanth (14:08):** Mhm. Okay, yeah, sure.

**Chad Hage (14:19):** Anyway, so just kind of giving you an example of, you know, this is with GitHub Copilot, VS Code specifically. Will not work on like Claude Code to my knowledge. I've tried it, it didn't work. I don't think it will work with Codex. I don't think it will work with any other...

**Kapil Srikanth (14:28):** Mhm.

**Chad Hage (14:40):** ...harness to be completely frank.

**Kapil Srikanth (14:48):** Is there like a specific reason? I know you said that earlier, but I was just curious.

**Chad Hage (14:53):** Well, yeah, because this GitHub, well, okay, so I could make it work if I alter the structure. It's not a huge undertaking to do it, but the way that this has been created is specifically for GitHub Copilot and specifically with VS Code.

**Kapil Srikanth (15:08):** Mhm.

**Chad Hage (15:12):** As a matter of fact, I actually played around a little bit with exporting the skills and the agents to work with M365 Copilot. So I kind of see what needs to be done. I tried to do it for Claude Code and I just didn't have enough time.

**Kapil Srikanth (15:12):** Yeah. Okay. So it works for M365 Copilot?

**Chad Hage (15:38):** M365 Copilot because it, yeah, it was just a repackaging. It's like a repackaged application file.

**Kapil Srikanth (15:43):** Okay. OK.

**Chad Hage (15:48):** Yeah. Alright, so.

**Kapil Srikanth (15:51):** So this thing is just going to keep running for like 20 plus minutes now.

**Chad Hage (15:54):** Yeah, yeah, maybe by the end of your update, I'll show you what came out of this.

**Kapil Srikanth (16:02):** Okay, sounds good.

**Chad Hage (16:07):** Hey, Brad.

**Kapil Srikanth (16:09):** Good afternoon, Brad.

**Chad Hage (16:12):** All right, so. Let's look at...

**Bradley Lawrence (16:19):** Hey, good afternoon. Sorry, I was typing a message and I couldn't hit the mute button.

**Chad Hage (16:43):** Alright, so for this week, let's start with... This one, Bruno.

**Bruno Rocha (16:50):** That's mine. All right, let me share the document. Make sure I have the right one first. So as of right now, it is mostly done, give or take, peer review, all that kind of stuff.

**Chad Hage (17:16):** And just to let you know, guys, when I look at these items, I start by looking at the blockers first. If there's no blocker, then I read the rest of it. So just...

**Bruno Rocha (17:23):** Yeah. Yeah.

**Kapil Srikanth (17:26):** Yeah.

**Bruno Rocha (17:27):** But overall, as of right now, there shouldn't be any, obviously barring any review from you. So our current drafts, main things, let me go here, purpose. The main things we want for you to take a look at is... Where was it? HLA (High-Level Architecture), we changed it up a little bit, slightly. This is, I believe, I don't remember if it was Ross or Joseph that threw this in here. I think it was Ross who did the original one, then I don't know who made the updates.

**Joseph Bressani (17:58):** The original one should be in there still.

**Kapil Srikanth (18:01):** Yeah, the original one's further down, I believe. Yes, this one's the...

**Bruno Rocha (18:01):** Is it in there? Yes, this is the original.

**Joseph Bressani (18:05):** Yeah.

**Bruno Rocha (18:07):** This is our original one. This is what we showed you in the SRS. Yeah, and then this is the new one, more simplified version. Yeah, green is the implementation, amber is the pilot, and this is all, I believe, done with Mermaid again, correct?

**Joseph Bressani (18:27):** Yeah.

**Bruno Rocha (18:27):** Right, yeah.

**Kapil Srikanth (18:28):** Yeah, that's perfect.

**Bruno Rocha (18:31):** Other than that, most of it is just the same from the SRS, just runs in here. And other things of note would be... I think it's up. The constraints, is there anything that you would want changed or added? Because we don't necessarily have any constraints, like project-wise, but more so just as a general thing. This is more just simplistic things that are not necessarily attached to a project, but what I could think of in the moment.

**Chad Hage (19:09):** Yeah, I mean, to me, this is more for Scott and Ken, right? They want this document. To me, I've already discussed these, you know, with you in terms of what are the hard, you know, what are the specs, right?

**Bruno Rocha (19:14):** Yeah, yeah, yeah.

**Kapil Srikanth (19:27):** Yeah.

**Bruno Rocha (19:28):** Yeah. But that's mainly what I've been working on. Joseph and all you guys have contributed as well. But this has been our main thing since it is due next Sunday and we're presenting the document as well as PowerPoint on Friday. So that was my main focus for this week.

**Chad Hage (19:39):** Okay.

**Kapil Srikanth (19:40):** OK.

**Chad Hage (19:42):** Right.

**Bruno Rocha (19:48):** Other than that, no real blockers really, just yeah, just keep working on it, editing and make sure it looks good before we submit it.

**Chad Hage (19:55):** All right, next up is... Let's see here. Who's `lost-soul`?

**Joseph Bressani (20:07):** Well, that's me.

**Chad Hage (20:09):** All right, there you go.

**Kapil Srikanth (20:09):** Yeah.

**Joseph Bressani (20:12):** So, I don't really have much to share.

**Chad Hage (20:14):** Oh, Joseph, okay.

**Joseph Bressani (20:16):** But we worked on the SRS, the second version of it, and also the DDD. I think me, Kapil, and Ross got some stuff on the demo, but Kapil will show you more of that after.

**Chad Hage (20:32):** Okay.

**Kapil Srikanth (20:32):** Yeah.

**Joseph Bressani (20:33):** And after that, like you did respond about the timeline, but I was hoping that like we had like AI could make a timeline, but like we don't know if it's like kind of valid in a sense. So we're just hoping to like get a more concrete one.

**Chad Hage (20:49):** Okay.

**Joseph Bressani (20:49):** That was all from me.

**Chad Hage (20:53):** Okay. So when I'm looking here, it says, *"I'd like to create a timeline to track progress."* It's not exactly a blocker. So, like, what is it that you're really struggling with here on this one?

**Joseph Bressani (21:12):** Just something what we could show you, 'cause like we just update like as we go week to week and like whatever we were working on, we show you, but like the timeline would tell us like you want to see this or at least progress of this, like, you know, just some way to quantifiably show we made progress instead of, "yeah, we've been working on this." That's like my idea of the timeline.

**Chad Hage (21:39):** Right. Yeah, and here, let me see. Do you have access to Copilot, M365 Copilot within USF?

**Bruno Rocha (21:53):** I believe we get it.

**Kapil Srikanth (21:53):** Yeah, yeah, M365.

**Joseph Bressani (21:55):** I think so.

**Chad Hage (21:56):** M365.

**Kapil Srikanth (21:58):** Yeah, we have access to that.

**Chad Hage (22:01):** Okay, because I mean, that's one of the things that I use regularly to just help me, you know, plan things out or, you know, try to keep things on track across everything that I'm doing. Let me see here.

**Ross Volenec (22:20):** Are there any specific tools in, is it Office 365? Like...

**Chad Hage (22:28):** One second. So this is, I'll show you the prompt in a sec. So this is something for the month of October, right? So it's kind of like pointing out on which day I have maybe a little too much load and some days that I have less load in terms of delivery commitments. And I just turned it into a Kanban, right? So like, these are things that I call `Avoid Doing`. These are in my `To-Do`. I try to keep, you know, no more than three items in my `In Progress` and move things into `Done` when they complete. This is across everything that I'm working on, across all my customers, you know, so on and so forth. So that is being done by this thing called M365 Copilot. Right? And so this is the prompt. It just goes through all my emails, all my IMs, all my, you know, Teams messages, my OneDrive files, et cetera, through everything that I have in WorkIQ and just categorizes it by, you know, `Avoid Doing`, `To-Do`, `In Progress`, `Done`—very simple prompt, it generated this. Is that the kind of timeline you're thinking about? Help me understand a little bit better.

**Joseph Bressani (24:05):** Oh.

**Chad Hage (24:06):** Yeah!

**Bruno Rocha (24:08):** I think it's more...

**Joseph Bressani (24:08):** I mean, the timeline, yeah, go ahead.

**Bruno Rocha (24:11):** I think it's more so like, for you, like, hey, what do you want to see come two weeks from now? That way we can kind of plan out towards that point. So, like, let's say, like, oh, I want a live demo by like week X. That way we know for us, like, okay, we should probably prioritize this, this, this, that way we can get to the goal that Chad wants two weeks from now. If you want a live demo, we know to get that live demo done by that two weeks.

**Chad Hage (24:38):** Yeah, I mean, I think the most important part is start from that final presentation on December 4th, I think, and work your way backwards, right? If you're able to demo to me every week, that's great. If not, the longer you wait, the higher my expectations will be, because just like the suspense is killing me, right?

**Bruno Rocha (24:45):** Mm.

**Kapil Srikanth (24:47):** Yeah.

**Bruno Rocha (24:56):** Right.

**Kapil Srikanth (24:58):** Yeah.

**Chad Hage (24:59):** But I'm expecting, you know, I'm expecting a demo every time we meet. I don't want you to hold off, you know, and kind of like do a buildup. If you're off in left field and we need to course correct, I want to know, you know, as quickly as possible. If you're feeling, you know...

**Bruno Rocha (25:04):** Okay.

**Chad Hage (25:17):** ...less secure about the demo, then let's talk offline, one-on-one, reach out to me. But yeah, every week I'm expecting a demo.

**Bruno Rocha (25:27):** Gotcha. Makes sense. All right.

**Chad Hage (25:30):** Brad, feel free to share what you do for productivity and keeping things flowing because I mean that's how we are expected to show to the customer every time we interact with them.

**Bradley Lawrence (25:40):** Yeah, I mean, I use Copilot to summarize, you know, what I need to get done for the week, what I have done for the week, and I ship that out both to my manager to let him stay informed of what's going on. And then I'll use it also to look for things that I might be missing, right? It's actually gotten really better at that. I'll say, hey, what haven't I considered that I should be trying to do with this particular customer or this account? Or were there some announcements this week that I should convey to my customer, right? Like new product announcements or retirements. Like that's a big one that just came up that's messing up a lot of customers with one of the tools I use a lot, Copilot Studio. We're retiring some models next month and we're replacing them, right? That happens all the time, except the new models you can't even use yet, right? So nobody can actually say, spin up a test environment and just make sure everything works with the new models. It's just like a hard switch. And I'm like, well, crap, I need to figure out some way to test this for our customers. So things like that, you know, it's not just doing work like working on some code or building out, you know, some presentations. It's everything else that it helps with. What's really powerful is like all my meetings, you know, I try to get them all recorded, have all the notes, and it really helps when like 2 months later, I'm like, hey, I remember talking about this somewhere, right? Who was that with? Right? It finds it, right? And you know, stuff like that just really helps. But probably the number one thing that's pretty impressive is when I try to work on a solution or a proposal for a customer, I basically have all the knowledge of everyone at Microsoft at my fingertips, right? Because I actually will craft something like, hey, my customer is facing this type of business problem, X, Y, and Z, maybe these platforms, these are their goals. Has anyone at Microsoft done something similar?

**Chad Hage (28:04):** Mhm.

**Bradley Lawrence (28:17):** And every single time the answer has been yes, and usually multiple times. And it goes and finds all the materials, all the issues that they ran into, how they ended up doing the solution, did it work, et cetera, et cetera. And now it can take all that knowledge across a couple hundred thousand people over a decade's worth of material and apply it, which could have never been done before. So stuff like that, it just really changed the game. And the thing that really makes it apparent is I work with one client that's highly regulated. And they are so strict on things, they don't allow most of their meetings to be recorded. You have to apply for access just to even turn on Copilot, just to even get a transcription. Because a lot of what this client works on, if it ends up in the news, it could be very bad. You would hear about it, you know. They're not necessarily doing evil things. It's just the nature of their work. And they have a lot of data regulations. So going back to meetings with no Copilot, no automatic transcription, and doing notes by hand, ew. Plus, you miss things. Whereas before, nothing got missed, right? Or now nothing gets missed. And going back to that manual, it's like, wow, this is so painful. And they recognize it and they're doing everything they can in their power to help their employees because they realize how much productivity they're losing by being this strict. So yeah, that's my thing.

**Chad Hage (29:56):** Absolutely. Do you guys have M365 Copilot available to you?

**Bruno Rocha (30:02):** We do, I just checked, we do.

**Kapil Srikanth (30:04):** Yeah, we should.

**Chad Hage (30:08):** Launch Copilot, either in the browser or in the dedicated app. The easiest way to know whether you have access to this information, because there's lots of different versions, unfortunately, the easiest way to tell whether it has WorkIQ turned on is to look at the...

**Bruno Rocha (30:10):** Ohh. Okay.

**Chad Hage (30:28):** ...where your icon, like where your profile picture is, and it will say either `Basic` or `Premium`. And then you'll see `WorkIQ` show up throughout. And that tells you if you see `WorkIQ`, that means it has access to your OneDrive, your SharePoint, your, you know, Word docs, emails, Teams messages, et cetera, et cetera.

**Bruno Rocha (30:35):** It's Basic. It's Work Basic.

**Chad Hage (30:53):** It says Basic.

**Bruno Rocha (30:54):** Yeah, Basic and then Work.

**Chad Hage (30:58):** Okay, that's different. Maybe the academic version is different.

**Bruno Rocha (31:00):** Here, I can just send a screenshot. Makes it easier.

**Kapil Srikanth (31:05):** Yeah, mine says `Work` next to my name and then below it says `Copilot Chat Basic` in parentheses.

**Chad Hage (31:12):** Yeah, yeah, you guys don't have the premium version, which may or may not have WorkIQ.

**Bruno Rocha (31:18):** That's what it says.

**Chad Hage (31:19):** It's weird, but yeah.

**Kapil Srikanth (31:20):** Yeah, that's what mine says as well.

**Chad Hage (31:23):** You can, you know, the easiest way to tell is to ask it to list the last five files you modified on your OneDrive, and if it cannot do that, then WorkIQ is turned off. But be that as it may, if you give it a list of, you know, the action items that you guys have already agreed to do in an Excel, if you attach that Excel, it will turn it into a timeline. I mean, it will do that same beautiful, you know, look and feel. It's just not going to go find it in your chat, especially because you guys are doing your interactions on Discord, I think, right?

**Kapil Srikanth (31:59):** Yeah.

**Joseph Bressani (31:59):** Yeah.

**Bruno Rocha (31:59):** Yeah, yeah.

**Chad Hage (31:59):** Yeah, so it's not going to find your conversation on Discord. If you had your conversation on Teams, it will find the conversation, it will find the transcripts, it will find, you know, the notes, et cetera, and it will harvest those for you and it will generate that timeline on your behalf. Something to think about. All right, let's see who's next.

**Kapil Srikanth (32:28):** Also, I just typed that now, *"What's the last thing I modified on my OneDrive?"* and it says it can't view or query OneDrive content, so.

**Chad Hage (32:37):** Yeah, when it says Basic at the bottom, it's usually an indication that it cannot access that.

**Kapil Srikanth (32:42):** Gotcha.

**Chad Hage (32:43):** Yeah, Ross, I think your update is next.

**Ross Volenec (32:48):** Right, I've made some progress on the feature matrix. I was hoping to have something demo ready, but something came up at work and I was running a little late this afternoon. So right now, I'm thinking that, like, as far as scope goes, to keep this from like spiraling out of control, my initial focus is to limit the scope to the actual like IDEs themselves and like the default inbuilt documented feature set. So right now what I've got is a specification. I guess it's kind of like the skills that you've been showing us. And I gave it to an agent, ChatGPT-based, and I had it go through the documentation for a few different specifications for Copilot via VS Code, Copilot CLI, just to get a baseline going. And it appeared to work. I've got 7 categories here. I wish I had time to pretty this up and show it off, but I think this is going in the right direction. And right now I'm trying to limit it in the sense that like SpecKit that you showed us, I consider that to be like an add-on. And I don't want to get into add-ons just yet. I feel like that's something that, you know, if we have time, that might be something that we can include after the fact. But right now, I feel like just focusing on getting the baseline capabilities through documentation is the smartest way to focus our energy at this point. Does that make sense? What are your thoughts on the subject?

**Chad Hage (34:37):** Yeah, I mean, I think I wanted to give you guys some head start on where you could go to look for ways to jumpstart the, you know, the exercise with GitHub Copilot, GitHub itself, VS Code—that Microsoft ecosystem. Remember, we said this is all about comparing the pipelines in adjacent fashion: so the Anthropic with Claude Code, OpenAI with Codex, GitHub Copilot with VS Code. You know, SpecKit is an...

**Ross Volenec (35:05):** Mhm.

**Kapil Srikanth (35:16):** Mhm.

**Chad Hage (35:18):** ...add-on, if you want to call it that, or extension, that happens to, you know, if you said, hey, I'm going to take SpecKit and run it across Claude, GitHub Copilot, and, you know, Codex. I mean, like, okay, now you've got something interesting. The objective is to see, like I showed you guys what we're able to do with...

**Ross Volenec (35:35):** Right.

**Chad Hage (35:40):** ...GitHub Copilot, VS Code, a GitHub account, an Azure subscription, and, you know, a beginning of a prompt that expresses something that you would put on a whiteboard or, you know, a demand item, right? And so, we're going from whiteboard all the way, you know, to an instance that can be tested in a live environment using GitHub Copilot, using GitHub itself as your GitHub Actions if you want to do the builds, VS Code, and Azure. So that's the pipeline, right?

**Ross Volenec (36:17):** Mhm. Right.

**Chad Hage (36:21):** You know, what would happen if you did that with Claude Code, whether you wire it to GitLab or GitHub itself, you know, I just want to see that side by side.

**Ross Volenec (36:38):** Mhm.

**Chad Hage (36:38):** Right? And are you guys able to get traction? I'm having a little bit of difficulty understanding where, like, what's preventing you guys from demoing at this point?

**Kapil Srikanth (36:54):** Uh, I can show off a little bit of a demo right now.

**Chad Hage (37:00):** Great.

**Ross Volenec (37:05):** Um, I guess I'm just, you know, things are moving pretty fast, so I feel like using, for example, like Microsoft just introduced MCP this week, isn't that right? So I just feel like the field is moving so fast, just having...

**Chad Hage (37:18):** OK.

**Ross Volenec (37:25):** ...like an agentic skill that will behave in a way that can go out and get the current assessment of like the documented abilities of some of these platforms. Now, do we want to have like, I think what you're saying is that, you know, it's good to have the core abilities and then the extensions as well would be part of that as well and then try to get like a cross-sampling of how they interact with the different platforms, the IDEs, the pipelines. Do you see that as something that is necessary for this to be valuable?

**Chad Hage (38:02):** Well, I mean, so here's the thing. Whether you use individual skills in a harness or whether you use an agent with skills, if you go and look at that agent definition file, you'll see that it's got, you know, essentially prompts that define its boundaries, that define its skills, that define its purpose, things like that, right? Down to the skill level, it's where you're grounding that particular agent or that particular, you know, skill itself. You're grounding it with what is the reference. And in the skill, you're also, whether it's in the agent or the skill, you're also expressing what connections or what connectors your harness can actually activate. That's really what you're doing. What is going to be consistent a month from now, a year from now, and a month ago is the idea that writing code, slinging code by hand, you know, is just gone. I would spend more time crafting an agent and a skill, or a set of agents and skills, or a factory, like I showed you, for example, versus sitting down and writing a single app. Because once I do that, I can pretty much crank out any app I want, regardless of the language, regardless of the architecture, regardless of the cloud that I'm targeting. In fact, like in the last, you know, three, four days, I've cranked out like half a dozen, you know, examples, right? Because I was trying to test this repo that I shared with you, right? And so what we now know is that the idea of whether you're going to use the Microsoft factory—because we came out with a factory product as well, right?—or whether you build your own factory, whether you use SpecKit, whether you use what Anthropic thinks is the best way to, you know, create that pipeline, or what Google thinks is the best way. That's what we're really trying to put side by side in Q3, Q4 of 2026, towards the last four months of 2026. Will that change in January 2027? Probably, right? But as of today, if you were starting a project, what are your choices? What are your options?

**Ross Volenec (40:49):** Gotcha. Okay. Yeah, so I feel like I'm on the right track with how I'd like to approach this. And I think that you've given me some good context here that I can continue to work with. So thank you for that.

**Chad Hage (40:58):** Okay. Yeah, I mean, I didn't see any blockers listed in your issue that you logged, so I took that as a, you know, good sign. There was some progress that you mentioned, but guys, let's get in the habit of demoing. I feel like there's a little bit of apprehension, maybe I'm reading too much between the lines.

**Ross Volenec (41:11):** Mhm.

**Chad Hage (41:25):** Just feel, you know, confident to show what you have. It's better that you show the demo and it turns out to be wrong than to sit on a demo that you never showed.

**Kapil Srikanth (41:38):** Yeah.

**Chad Hage (41:38):** Does that make sense? I hope that makes sense.

**Bruno Rocha (41:45):** It does, yeah.

**Joseph Bressani (41:46):** Yeah.

**Chad Hage (41:47):** Okay. It's not ABC, it's ABD: Always Be Demoing. If you're in sales, it's ABC.

**Bruno Rocha (41:57):** I think Kapil has a pseudo-demo, I guess, to show.

**Kapil Srikanth (42:04):** Yeah, something.

**Chad Hage (42:07):** I mean, if you're worried that I'm going to call your demo ugly, I'll just go ahead and say it's ugly now, so that way you get it out of the way. I'm just kidding with you. Don't get, you know, too defensive about it.

**Bruno Rocha (42:13):** Yeah.

**Kapil Srikanth (42:13):** OK, yeah, no, I wasn't sure. I can share. Yeah, that's cool. OK, you see that? OK, so...

**Chad Hage (42:19):** Yeah. Okay, let's see it.

**Kapil Srikanth (42:26):** This is the repo that we've been working in, and so this first demo is just testing the four harnesses with Claude Code, Codex, me—this one's Antigravity—and then Copilot, there we go, that's the 4th one. I always forget Copilot, sorry.

**Chad Hage (42:49):** OK, so let me pause you right there. So it sounds like you guys have decided to divide and conquer the work where some of you are taking the documentation and working on it, some of you are taking the, you know, like the research and working on it, and some of you are taking the assembly and working on it. Is that an accurate assessment of how you're working as a team?

**Kapil Srikanth (43:11):** Yeah.

**Bruno Rocha (43:12):** Yeah, but I feel like we prioritize at least almost knowing at least a little bit of something what's going on. That way it's not, if you ask me like what the demo's going to be, I have no clue what's going on, is the point.

**Joseph Bressani (43:13):** Yeah.

**Chad Hage (43:26):** And the reason why I bring that up is that on December 4th, if one of you ends up coming down with a cold and that happens to be the person that runs the demo, what are you going to do?

**Kapil Srikanth (43:26):** Yeah.

**Bruno Rocha (43:33):** Right. Right.

**Kapil Srikanth (43:35):** Yeah, don't worry. It's good because every time I was updating them on what I was doing, because I was testing it out with Antigravity, so that was what I was doing first. And then with the rest of them, I shared the prompts I used, the `.md` file that I...

**Chad Hage (43:37):** Right, just be mindful of that, right?

**Kapil Srikanth (43:55):** ...gave to them and I believe Ross and Joseph were also able to run theirs with similar effects. So we're on the same page with this one. So, yeah, a few weeks ago, we made this little to-do app, and that's just the starting code base for this. And we're just testing this. This initial test is just testing adding a delete option to the baseline, so each of the harnesses is going to add that to there. Can you see the Antigravity or can you see that? Okay, cool. We each ran this. We gave it this entire `benchmark-start-v1`...

**Chad Hage (44:38):** Yeah. Okay, yeah.

**Joseph Bressani (44:41):** Yeah.

**Kapil Srikanth (44:55):** ...right here. And we told it to read this, so `add-delete-endpoint.md`, which is the instructions, and complete the tasks. And, you know, it ran through for roughly 6.5 minutes or so, and yeah, it implemented the changes and it passed all of the tests that it was required to run for it, and then independently, so the agent harness doesn't have access to the acceptance criteria so it can't like fake its own score. We put it outside of its context. And running this, it was able to pass all of the 9 tests that we provided it where it wasn't allowed to modify anything, and it was able to...

**Chad Hage (46:01):** Okay.

**Kapil Srikanth (46:02):** ...test some invalid circumstances here that would fail. And you can see, yeah, the delete key works, so if I create it, yeah, it can delete just fine for Antigravity. And yeah, it's a rather short demo, but this is like what we're planning on building on because from what we understand, it's like this and comparing the performance and the token usage, security concept. So we'll be checking the, you know, security and scoring it with what Joseph came up with a few weeks ago with the scoring matrix.

**Chad Hage (46:43):** Let me understand what I'm seeing here. So using Antigravity, you guys introduced a feature that's called Add Task and Delete Task, two features or two user stories. And Antigravity took those two features, coded them, pushed them out to an...

**Kapil Srikanth (46:46):** Okay. Yes. Yeah.

**Chad Hage (47:03):** ...environment that you can test on and declare the, you know, the cards done. Is that an accurate understanding of what I just saw?

**Kapil Srikanth (47:05):** Mhm. Yeah, pretty accurate.

**Chad Hage (47:17):** Okay, okay. So now can you do the same with Claude Code, with Codex, GitHub Copilot, side by side?

**Kapil Srikanth (47:19):** Yeah.

**Ross Volenec (47:27):** We tested the same pipeline through Copilot CLI, at least.

**Kapil Srikanth (47:31):** Yeah, so right now I believe all of us have ran it. We just need to push it to the repo, so...

**Chad Hage (47:43):** Okay.

**Kapil Srikanth (47:43):** Right over here, these are the results that Antigravity produced. I did have to, for the acceptance case, make an addition because there was an oversight on my part. Because it was like IDs, it's supposed to recognize like `01` as a valid ID, but because the zero was in front, it was saying it was an invalid ID, so I had to adjust that in order to do that because of an oversight, so that's what the corrected test is, where in Antigravity... Let's see, when doing a supplemental check, it found a mismatch and it reran it. So that was the human-in-the-loop to check for a mismatch. And I believe Ross was able to publish his or push his into the repo as well. Yeah, Copilot. Which produced this, and it created an `.md` file as instructed by the prompt over here. And what I noticed is that Antigravity took a really long time and Copilot didn't take a long time at all. And I believe it was the same for Codex and Claude Code. Antigravity was by far the longest. So from our early testing, that's what I noticed from this.

**Ross Volenec (49:33):** I think it was, it should say in here, but I think the model that it used was GPT Luna 5.1 or something like that. And it took a little over a minute as opposed to what, 6 plus minutes.

**Joseph Bressani (49:40):** Yeah, Luna.

**Kapil Srikanth (49:47):** Yeah, mine's 6.5 minutes for yours.

**Chad Hage (49:48):** Antigravity used Luna?

**Kapil Srikanth (49:51):** No, no, no. He's referring to Copilot. I used Flash 3.8. That was the basic model. And for now...

**Joseph Bressani (49:52):** No, Antigravity used Gemini Flash.

**Ross Volenec (49:52):** Copilot.

**Chad Hage (49:53):** Ohh, Copilot, yeah, yeah, yeah.

**Kapil Srikanth (50:03):** So these are the models that are available: Sonnet and Opus 4.6, which are a little bit older models, but they can still be useful in data testing.

**Chad Hage (50:14):** But are you guys having to actually specify the models to get the, you know, the actual framework to do the work correctly, or are you able to just let it decide? Is there an Auto feature on Antigravity?

**Kapil Srikanth (50:29):** Uh, right.

**Ross Volenec (50:32):** There is Auto, at least for Copilot.

**Kapil Srikanth (50:35):** No, yeah, there's no Auto for Antigravity. It defaults to Flash 3.8.

**Chad Hage (50:42):** Gotcha. Yeah. Okay. So if you leave it on Flash, have you been able to like get the baseline of what is the efficiency? How often does it actually, you know, generate garbage versus get it correct? How often does it, you know, leak your credentials versus recognize that this is a, you know, a secret or a credential and that needs to be handled...

**Ross Volenec (50:44):** And then Copilot was automatic.

**Chad Hage (51:05):** ...with care?

**Kapil Srikanth (51:08):** Yeah, right now we're busy like further implementing that. It needs further testing.

**Chad Hage (51:13):** Okay. Okay.

**Ross Volenec (51:18):** I...

**Chad Hage (51:18):** But you guys are starting to understand what you're able to do with these, you know, pipelines, as I call them, with these factories, right? And there is the default mode of each one. You know, it sounds like with Antigravity, they default to...

**Kapil Srikanth (51:18):** Yeah. 3.8 Flash.

**Chad Hage (51:37):** ...3.8 Flash. And if you don't change it, and if you don't know that you have these other models, right, it's going to behave in a certain way. Just like when you go on GitHub Copilot, we have an Auto mode, which happens to try to, you know, I think by now they introduced a new...

**Kapil Srikanth (51:45):** Mhm.

**Chad Hage (51:57):** ...configuration called `Balanced`. If you don't change anything in GitHub Copilot, you're going to have `Auto` for model, `Balanced` for, you know, in terms of how deep does it think between efficient and, you know, deep thinking, and, you know, the actual...

**Kapil Srikanth (52:00):** Yeah.

**Chad Hage (52:17):** ...handoff, you know, `Interactive` versus `Autopilot`. So those are the three different modes. If you don't change anything, it's going to ask you for every single decision. It's going to use `Auto`, which means it selects the model. And then there's going to be the...

**Kapil Srikanth (52:23):** Mhm.

**Chad Hage (52:36):** ...you know, the `Balanced` weights or the `Balanced` tuning for how much dwelling or how much deep thinking does it do, and that produces a certain interpretation of that same requirement. So, if I take that Add Task and Delete Task, that's our requirement, put it through the four or five pipelines simultaneously and just benchmark it.

**Kapil Srikanth (53:01):** Right.

**Chad Hage (53:01):** That's number one. Does that make sense?

**Ross Volenec (53:04):** The AutoGen pipeline that I've been working on, that was the main goal, because, like, we've got the, you know, Antigravity versus the model, it's decoupled, so like the feature matrix in my mind is to evaluate like the front end and the pipeline is to evaluate the models themselves, and when you say, like, you know, exposing secrets, we do have...

**Kapil Srikanth (53:06):** Yeah.

**Ross Volenec (53:25):** ...that pipeline set up. It does need to be cleaned up because I've been pivoting a little bit.

**Chad Hage (53:30):** And see, personally, I don't think the model itself can be held accountable on its own for exposing your secrets. The model is the model, right? It's the harness and the MCP tools that you have and the way that you've, you know, configured it that decides whether—the model itself does not say, oh, it's a secret, I'm going to leak it.

**Kapil Srikanth (53:38):** No. Yeah.

**Ross Volenec (53:38):** Mm.

**Chad Hage (53:50):** Right? In fact, if anything, if the model is doing its job, it's going to say, hey, by the way, that's a secret, harness. Are you sure you want to leak it? Right? And so it comes down to what are the defaults that are shipped with each one of these pipelines, with each one of these factories, and...

**Ross Volenec (53:59):** Mhm.

**Chad Hage (54:08):** ...which ones are tuned for professional, you know, production-grade development versus which ones are essentially the equivalent of a prototype hobbyist that are going to, if you point it to production, you probably are putting your organization at risk.

**Kapil Srikanth (54:28):** Mhm.

**Chad Hage (54:30):** Right. Does that make sense?

**Ross Volenec (54:33):** Yes.

**Chad Hage (54:34):** I'm starting to sound more like Bobcat Goldthwait here by the second.

**Kapil Srikanth (54:34):** Yes. Yeah, are you alright?

**Chad Hage (54:42):** Ah, I'm losing my voice; my vocal cords are shot.

**Kapil Srikanth (54:44):** Uh, yeah, last week I know you were coming down with something, so is this the same thing?

**Chad Hage (54:49):** Yeah, I think I'm done, but now I'm trying to recover and I just haven't stopped talking all week between calls and it's alright.

**Kapil Srikanth (54:57):** Gotcha. Okay.

**Chad Hage (54:59):** It's all good.

**Kapil Srikanth (55:00):** Alright, as long as you're doing alright.

**Chad Hage (55:02):** Yeah, yeah, I'm fine. I'm past the coming down with something now. I'm kind of recovering, but my voice is gone.

**Kapil Srikanth (55:12):** Okay.

**Bruno Rocha (55:12):** Mm.

**Chad Hage (55:15):** Um, yeah, alright. So I think we covered everyone, right?

**Kapil Srikanth (55:21):** Oh yeah, yeah.

**Bruno Rocha (55:22):** Yeah.

**Chad Hage (55:23):** Okay, so what are your plans for next week? What can we expect next week? Can we start seeing the rhythmic demos?

**Joseph Bressani (55:23):** Yeah.

**Kapil Srikanth (55:23):** Yes, yeah, yes.

**Bruno Rocha (55:30):** Yes, that's the main goal now.

**Joseph Bressani (55:31):** Yeah. More testing.

**Bruno Rocha (55:33):** That's also why we wanted the DDD done now. That way next week is just focusing on demos. So our goal is next week to show you a more realistic demo of what it would look like.

**Chad Hage (55:46):** Okay. After our conversation now, do you see any blockers? Do you see anything emerge out of this conversation that gives you the sense that you're going to be blocked?

**Bruno Rocha (56:05):** No, if anything, I feel like we're, I think all of us are a little more clear now that we are getting it.

**Kapil Srikanth (56:05):** No. Yeah.

**Chad Hage (56:11):** Okay. All right, I like the sound of that. While we were talking, so just to kind of bring it full circle. So that prompt that I showed you, it started cranking. So far, this is what it's produced so far.

**Kapil Srikanth (56:30):** Yeah, what does it say?

**Chad Hage (56:34):** Well, here's the thing. So we started here. I downloaded, I cloned this repo. I started the factory. What it did was it created the documentation, it captured, you know, the documentation. So this is all documented deliverables, it shipped those, right? Let's open that up so you guys can see what it did. `todo-app`. So this is all the, you know, the questions back and forth that it was asking.

**Kapil Srikanth (57:14):** Yes.

**Chad Hage (57:19):** So this is the Kanban it created. A little slow. They are loading. Surprisingly, my GPU, what's my GPU doing? Yeah. Actually, the CPU is what's pegged.

**Kapil Srikanth (58:01):** Yeah, your CPU was at 97, or now it is.

**Chad Hage (58:04):** Right. Yeah, and GPU is cranking hard too, both GPUs. Still trying to render this `.md` file.

**Kapil Srikanth (58:16):** How big is this file?

**Chad Hage (58:18):** It's not that big.

**Kapil Srikanth (58:19):** Yeah, I think we saw it last week, the Kanban file.

**Chad Hage (58:23):** This is a very small look.

**Kapil Srikanth (58:24):** Yeah.

**Chad Hage (58:25):** Yeah, so it created a product backlog. Here's the product backlog, created an iteration plan. Now, I didn't create it, it's the agents within that factory. The factory directive is: create one squad, it has at least one of these agents, and it orchestrated across all of them. You guys get what it's doing? So all of these were generated by the different agents in the package over here, right?

**Kapil Srikanth (59:02):** The `factory.md`.

**Chad Hage (59:04):** Yeah, so the `factory-launcher` launched the `factory`, the `factory` itself launched the `squad`, the `squad` launched a, you know, a demand collector, I call `voc` agent, and it launched a product manager or `product-owner` and three developers that I call `full-stackers`. And there's instructions in here that say, work as a council to figure out what the demand is. And these are the skills that they share in common. OK, and so, as a result of that...

**Kapil Srikanth (59:40):** Mhm.

**Chad Hage (59:43):** ...it has created—so that's the documented deliverables that were generated. And here's the source code that was generated for this agentic application. This is all while we were here, while you guys were giving your update, so this is the source, tests, the deployment code to deploy it to Azure, environment settings for different environments, and so on and so forth. All right.

**Kapil Srikanth (1:00:28):** Mhm.

**Bruno Rocha (1:00:29):** Yeah.

**Chad Hage (1:00:30):** So that's what we are doing with GitHub Copilot. SpecKit is something very similar to this. Not as much of a factory, but we obviously can tune SpecKit to do this. The alternative to this is just vibe coding. Right.

**Kapil Srikanth (1:00:51):** Right.

**Chad Hage (1:00:52):** But in here, I'm not actually vibe coding. I'm not doing anything. If anything, I would introduce a new card in the demand pipeline at the VOC level, at the Kanban, and it will drop it in the Kanban. Then the Kanban agent will prioritize that new demand item versus pre-existing demand items because I actually created a skill called Weighted Shortest Job First, which takes, you know, what is the economic benefit? What is the cost of development? And it calculates a score and it says, ah, based on this score, this card sits at #5 in the queue of 20. Right? So just because I give it a prompt, it's not going to stop what it's doing unless I tell it, stop what you're doing and do this. If I just say, hey, add this feature, the factory concept that you see here will take that demand item, put it in the queue, measure it against other demand items, prioritize it, and then tee it up for the next iteration. All right.

**Kapil Srikanth (1:02:05):** Mhm.

**Chad Hage (1:02:06):** And this is what this is actually, you know, doing all that right here. Anyway. I think it's waiting for me to press Allow. Yeah, the permissions, because it's acting on my behalf, I can set it to Autopilot and it will just keep running, but I wanted to show you guys, you know, what happens when you, and it's telling me every single step that is taken right now here.

**Kapil Srikanth (1:02:17):** Yeah, yeah. Right. Yeah, I saw the same thing when I was working with Antigravity. It always wants your input.

**Chad Hage (1:02:35):** All right. Okay. Well, I mean, I can turn this into Autopilot on GitHub Copilot, right?

**Kapil Srikanth (1:02:48):** Yeah. There's an option where it asks me, do you want to run `npm test` and you can put like `Allow this time` or `Always allow` or I think there are two more options.

**Chad Hage (1:03:03):** Yeah, and I think there is one skill in here that I added earlier today that taps into the Copilot...

**Kapil Srikanth (1:03:04):** Yeah.

**Chad Hage (1:03:14):** I forgot the name of it. Hold on one second. I think I have it here. So it allows it to actually query the last session and collect how many tokens were used. Oh, it's called Chronicle Tips. So Chronicle Tips is another API within Copilot. So now it is able to actually calculate how many tokens, how many AI credits were used per card that was marked completed. All right, we're out of time. Always be demoing, guys. I want to see more demos. You're doing good. The conversations tell me that you're doing good, but without the conversation, I look at your entries and I don't see demos. I don't see, you know, the things that make me feel like, you know, you're going at the velocity that you could be going at. So anything you can show ahead of time, don't hesitate. What's the worst that could happen? I could tell you, no, you're not on the right track, and then you'll course correct sooner.

**Kapil Srikanth (1:04:21):** Right, OK.

**Chad Hage (1:04:21):** Okay, but...

**Bruno Rocha (1:04:22):** Understood, yep.

**Chad Hage (1:04:24):** Don't be hesitant to demo.

**Bruno Rocha (1:04:27):** Yes, sir.

**Chad Hage (1:04:28):** A demo that shows you that you were headed in the wrong direction is just as valuable as one that gives you the confirmation that you are on the right track.

**Kapil Srikanth (1:04:37):** Okay.

**Chad Hage (1:04:38):** In fact, maybe even more valuable.

**Ross Volenec (1:04:40):** Chad, how would you feel about a video demo in our weekly updates? Would that work for you or would you prefer a live update, a live demo?

**Chad Hage (1:04:46):** If you post a video demo, a link to the video demo on the GitHub issues where I can watch what you're actually demoing, that's wonderful.

**Ross Volenec (1:04:59):** OK, perfect.

**Chad Hage (1:05:00):** Because then I can give you the feedback. If you post it on Tuesday and I'll give you feedback on Wednesday, by Friday you're that much further along.

**Ross Volenec (1:05:07):** Okay, great.

**Kapil Srikanth (1:05:07):** Alright, sounds good.

**Bruno Rocha (1:05:09):** Sounds good. Yeah, we'll do that.

**Chad Hage (1:05:10):** All right.

**Bruno Rocha (1:05:12):** Yes, Sir.

**Ross Volenec (1:05:13):** All right, appreciate it, Chad.

**Chad Hage (1:05:15):** Always remember, Parkinson's Law: Work will always expand to fill the time that it's allotted. So if you give yourself till Friday, you're going to take the same tasks and you're going to see them stretch to, you know, fill the time you gave yourself. If you just get in the...

**Kapil Srikanth (1:05:15):** Yeah. Mhm.

**Chad Hage (1:05:33):** ...mode of constantly, you know, demoing as soon as you finish something, you'll get the feedback that much sooner.

**Kapil Srikanth (1:05:42):** Right.

**Bruno Rocha (1:05:43):** Yeah, fair enough.

**Ross Volenec (1:05:43):** OK.

**Chad Hage (1:05:43):** All right.

**Kapil Srikanth (1:05:44):** Yeah, Chad, just to, you know, clarify, what I showed you, what we're working on currently, we're on the right path with that, right?

**Chad Hage (1:05:51):** Yeah, I mean, I like what you showed with Antigravity. You know, I want to see them side by side, right? Yeah.

**Kapil Srikanth (1:05:57):** Okay, yeah, we could do that, because I was the main one ready to present, but next week we'll have all of us, I think.

**Bruno Rocha (1:05:57):** Yeah.

**Chad Hage (1:06:05):** Well, that's why my question to you, I was trying to understand, are all of you kind of taking upstream pieces and you're the one assembling them or each one of you taking one, you know, silo and taking it from A to Z? That's still unclear to me. Like, is one of you the Anthropic Claude Code guy and the other one is the Codex guy and you're the Antigravity guy or are you the one that's doing all of them and they're feeding you input? I don't know yet.

**Kapil Srikanth (1:06:33):** No, no, each one of us is doing, like, I'm Antigravity, Joseph's Codex. Yeah, we're doing it like that. And I was just making sure we were all feeding each of the harnesses the same prompts so that we could actually have a good comparison. Yeah.

**Chad Hage (1:06:42):** Okay. All right, so... Good, good. Perfect.

**Kapil Srikanth (1:06:56):** All of us are communicating there. It's not just me doing everything.

**Chad Hage (1:06:58):** Sounds good.

**Bruno Rocha (1:07:00):** Yeah.

**Chad Hage (1:07:03):** Yeah, don't make one person the bottleneck. If you choose to do that, I hope you have a good reason for that. But it sounds like you're, you know, dividing and conquering the way I would divide and conquer. So yeah, definitely. Oh, it's demoing right now.

**Bruno Rocha (1:07:03):** Yeah. No.

**Kapil Srikanth (1:07:06):** Mm. Yes. Yeah, that's what we're doing.

**Bruno Rocha (1:07:13):** Yeah.

**Chad Hage (1:07:21):** It started the demo as a matter of fact.

**Kapil Srikanth (1:07:23):** Oh, oh, there we go.

**Chad Hage (1:07:25):** So, alright, cool. Alright, guys, enjoy the weekend.

**Kapil Srikanth (1:07:31):** Yeah.

**Bruno Rocha (1:07:32):** All right, you as well. Take care.

**Joseph Bressani (1:07:32):** Have a great weekend.

**Kapil Srikanth (1:07:33):** Alright, you too.

**Ross Volenec (1:07:33):** Thank you, you as well.

**Bruno Rocha (1:07:34):** Thank you, Brad.

**Ross Volenec (1:07:35):** Hope your voice gets better.

**Chad Hage (1:07:37):** Wait, do you guys want to see the demo?

**Joseph Bressani (1:07:37):** Yeah.

**Bruno Rocha (1:07:39):** Yeah, sure. Yeah.

**Kapil Srikanth (1:07:39):** Uh, sure, please.

**Ross Volenec (1:07:39):** Yeah.

**Joseph Bressani (1:07:41):** Sure.

**Bruno Rocha (1:07:42):** Yeah.

**Chad Hage (1:07:42):** It's literally doing a demo asking me to sign off.

**Kapil Srikanth (1:07:44):** Okay.

**Bruno Rocha (1:07:48):** Ohh.

**Kapil Srikanth (1:07:48):** "I am your task assistant."

**Chad Hage (1:07:53):** Here we go.

**Kapil Srikanth (1:07:54):** "Allow in this session."

**Chad Hage (1:08:00):** So I created the, whatchamacallit. Yeah, see that? It's adding a task plan. This is all being done by Playwright. I'm not touching anything.

**Kapil Srikanth (1:08:12):** Mhm. Who is Alex Wilber?

**Chad Hage (1:08:18):** That's a demo user that's built into the SDK.

**Kapil Srikanth (1:08:20):** Okay, that's what I guessed.

**Chad Hage (1:08:23):** Yeah. So there you go. So in the span of one hour, we went from prompt to backlog to plan to code, and now it's doing a demo. It's finished an MVP. All I'm doing is just pressing `Allow in this session`, which I could say `Allow to all`. There you go. And now, oh, that was the agent. This is the web UI. It built both UIs.

**Kapil Srikanth (1:08:57):** This is the to-do that it just added the plan to demo.

**Chad Hage (1:09:09):** Well, yeah, it built an agent and a web UI. This is the web UI.

**Kapil Srikanth (1:09:14):** Yeah.

**Chad Hage (1:09:16):** The other one was an M365 agent that talks to the same back end, to the same API and MCP.

**Kapil Srikanth (1:09:19):** Mhm.

**Bruno Rocha (1:09:23):** Mhm.

**Kapil Srikanth (1:09:24):** Yeah.

**Chad Hage (1:09:27):** And I believe I saw something in here around test coverage. The test coverage requirement is 85% minimum, but I believe it will be closer to 100%.

**Kapil Srikanth (1:09:40):** Mmh.

**Chad Hage (1:09:46):** I hope you're having fun. I'm looking forward to seeing what you're going to be done with next week.

**Kapil Srikanth (1:09:48):** Mhm. Sounds good.

**Bruno Rocha (1:09:54):** Well, sounds good. Yes, sir.

**Chad Hage (1:09:54):** All right. All right, bye. Take care.

**Joseph Bressani (1:09:57):** Have a great week. See ya. Have a good week.

**Chad Hage (1:09:57):** Appreciate it. You too.

**Kapil Srikanth (1:09:58):** Alright, have a great weekend, Chad and Brad.

**Bruno Rocha (1:10:01):** Have a good one.

**Kapil Srikanth (1:10:07):** Good work, boys. I think that went pretty well.

**Bruno Rocha (1:10:09):** I think so.

**Joseph Bressani (1:10:10):** You think?

**Bruno Rocha (1:10:11):** I think so. Better than I expected. Wait, should we stop the recording?

**Kapil Srikanth (1:10:23):** Oh yeah, let me stop that. There we go.

*Kapil Srikanth stopped transcription*