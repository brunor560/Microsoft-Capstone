# CIS4910 - Group 3 - Project MS2 - Senior Project Meeting (Week 3)

- **Date:** September 11, 2026
- **Time:** 7:33 PM (UTC) / 3:33 PM (EDT)
- **Duration:** 56m 39s
- **Attendees:** Chad Hage (Sponsor), Bradley Lawrence (Sponsor), Ross Volenec, Bruno Rocha, Kapil Srikanth, Joseph Bressani

---

## Executive Summary & Key Takeaways

* **Student Resources & Credits:** Each student has access to a 12-month, $100 Azure credit (totaling $400 across the team) alongside over a dozen "forever free" Azure services (including Azure Static Web Apps) and a 90-day free M365 Sandbox tenant via their `.usf.edu` IDs.
* **Harness vs. Model Focus:** Chad reiterated that the evaluation must focus on the end-to-end **developer experience and harness ecosystem** (e.g., GitHub Copilot, Claude Code, Codex, Google Antigravity) from idea/backlog to production, rather than comparing 10 different foundation models inside a single harness.
* **Target Depth (Microsoft L100–L400):** Deliverables and the final white paper/microsite should aim for **Level 250 to L300** (practitioner/architectural depth on par with Microsoft Ignite sessions), avoiding high-level L100 summaries.
* **Evaluation Metrics & Weighting Review:**
  * *Proposed Weights:* Functionality (35%), Security (25%), Code Quality & Refactoring (20%), Cost Effectiveness (10%), and Automation/Autonomy (10%).
  * *Refining "Functionality":* Expand to evaluate how harnesses handle context management, MCPs, IDE extensions, developer preference files, and adherence to specs.
  * *Refining "Automation" to "Autonomy":* Frame around **Human-in-the-Loop** (milestone-by-milestone sign-off) vs. **Human-on-the-Loop** (autonomous execution unless the loop is defective). Reward proper, benevolent human intervention rather than strictly penalizing it.
  * *Refining "Security":* Evaluate across three Microsoft pillars: **Secure by Design** (code vulnerabilities), **Secure by Default** (safe out-of-the-box configuration), and **Zero Trust** (entitlements, RBAC, and secret/token handling for both end-users and developers). Existing scanners like TruffleHog or GitLeaks are approved as long as outputs are harmonized across pipelines.
  * *New Metric Suggestion:* Consider adding **Adaptability** (ability to swap between cloud-hosted LLMs and local LLMs).
* **Target Persona:** The primary customer for the framework is a Chief Architect or Chief Development Officer deciding which ecosystem to license for a large engineering organization (weighing license cost vs. engineering headcount and fault tolerance).
* **Schedule Adjustment:** Weekly meetings were moved to **Fridays from 4:30 PM to 5:30 PM EDT** (expanded from 30 minutes to 1 full hour).

---

## Cleaned Transcript

**Chad Hage (0:03):** ...on the team, I expect that you provide your own updates. And then together we'll go through them, and they're date-based. So if you miss this week, it's going to be—I think it's Saturday to Friday, right? I believe that's how I set it up. But yeah, that's all this is doing. I think that December 4th is typically when the final presentations are. If that's incorrect, give me the actual date and I'll replace this. But I just counted—the first Friday in December is usually it, if that's accurate. Okay.

**Bruno Rocha (0:39):** Yeah, that's correct.

**Kapil Srikanth (0:41):** Yeah, sounds about right.

**Chad Hage (0:43):** All right. I did give some time here in case there was some post-work that you needed to finish up—not that I'm expecting you to, but I always like to run the project to the ground. And that's my update for this week. 

Oh, before I actually turn it over: under Student Resources, you should see by now that you have a 12-month-long $100 Azure credit using your `usf.edu`. That's why it was important to get you into GitHub with your `usf.edu` ID. Each one of you will get a $100 Azure credit that's good for 12 months. I know that's not a whole lot, but when you actually put it in perspective, last time I counted, I want to say there are over a dozen free services that are forever free. Depending on how you end up trying to conduct this project from your point of view, I personally can see a path to the finish line with all these free services and that $100 individual credit. So collectively, you have about $400 if you were to pool your dollars together. 

Whenever you navigate to the GitHub and go to the GitHub Pages, you have options in here: Student Resources, and it's going to take you through some of the resources that I curated for you, starting with the Azure $100-per-student credit good for 12 months. This will take you through the process of verification and it will also show you the different services that are forever free as well. You can also, depending on how you guys want to do this project—again, you choose the workload—if you wanted to set up an actual sandbox, which is a full M365 tenant, you could do that. What this will do is give you Exchange, it will give you your own actual M365 tenant just like the one that USF and Microsoft use, and we'll tie these two together. Both of these resources are available to you for free as a student. The M365 Sandbox is available for free for anyone for 90 days, but the student one is slightly different, just to give you a heads-up. And then all the GitHub educational stuff is available for free with that verifiable `usf.edu` ID.

I took some time to also curate—I played around with my prompts to tweak them and fine-tune them to make them verifiable so that none of this stuff is a hallucination. Wherever I couldn't verify, I found some literature—like I couldn't actually go through the process to sign up because I would go through each one of these processes until it asked me to verify my ID, and then it would not let me pass a certain point because I don't have an `.edu` ID. But you should be able to get past that because you do have an `.edu` ID. That's what I mean by verified versus not verified. This one here, for example, I was able to verify because I followed the path and it let me through even without an `.edu` ID. 

So that's kind of giving you a good lay of the land as to what's out there. I'm not telling you that you've got to build a single pipeline for every one of these things. I'm just giving you a jump start on where you can save yourself some time. This one is table stakes right here for the Microsoft pipeline. If you guys want to draw from a hat or something on how you would choose the other ones, I'll leave it up to you. I just want to see at least this versus as many as you can put parallel to it as possible. 

And with that, that's pretty much the update that I have. I'm thinking every week we'll come in—if you come in here and add your updates right before the call, then we'll jump straight to it. If not, during the call, feel free to update and we'll just go ahead. If there's nothing blocked and you just want to discuss the progress, that's great. If there are blockers, I'll be able to see them in advance. If you were to enter an update, say, on Tuesday of that week, it will still show up for that week. And by the way, I'm following the repo, so I will get notified on Tuesday that you're blocked on Tuesday. So now you have at least two avenues to convey any blockers or any updates: the Teams channel as well as the GitHub repo. Questions, comments?

**Bruno Rocha (6:37):** No, this all looks really good, yeah.

**Ross Volenec (6:38):** Makes sense to me.

**Kapil Srikanth (6:39):** Yeah, I think all of us were able to get access to Azure, I believe, right?

**Chad Hage (6:41):** All right. Fantastic.

**Bruno Rocha (6:48):** Yeah, I have it. Only thing from us is that during class for this week, we had to do a PowerPoint presenting things like the Epic and all that kind of stuff. Our main thing was just hoping we could show you what we talked about in class, and from there, see if you have any talking points or anything where maybe we're going the wrong way.

**Chad Hage (7:04):** Yeah, absolutely. Are you able to actually create your updates by going to this page and adding an update?

**Bruno Rocha (7:15):** Yes, let me try right now.

**Chad Hage (7:16):** I think also I saw Brad join. Brad, just want to catch you up—we just went through some of the stuff that I've shared with the students here. So ideally what would happen here: we would come in, kick off the call, your updates would be in here, we would jump to the ones that are blocked, otherwise we would move on to completed and planned. If everything looks reasonable and you're not pointing yourself towards a ditch, I will support you and commend you. If I see that you're about to drive off of a cliff or into a ditch, I'll point that out. If you insist on driving into a ditch, I will empathize and we'll do whatever we can to pull you out of the ditch.

**Kapil Srikanth (8:11):** Yeah, that makes sense.

**Chad Hage (8:15):** All right, who wants to take over the screen sharing?

**Bruno Rocha (8:20):** Does anyone have it open already, by any chance? Yeah, I can do it.

**Kapil Srikanth (8:31):** Ideally, we just want to show the PowerPoint. Ross, I don't have access to the notes panel. I don't know if anyone else has that problem.

**Bruno Rocha (8:44):** Does everyone see the presentation?

**Ross Volenec (8:50):** Yes.

**Bruno Rocha (8:51):** All right. This is what we presented in class. This is our current problem statement slash solution. We think based off last meeting, this is where we're aiming towards, but let us know if there's anything that we're missing. Our solution is to build a framework that runs direct comparisons across all AI models, producing quantifiable results showing where each excels and fails, constraints, deliverables...

**Chad Hage (9:19):** So let's pause on that for a second. I don't know if you're going to actually focus as much on the model per se, as much as I'd like you to focus on the developer experience in that ecosystem. Because if you take, for example, GitHub Copilot, GitHub Copilot can activate Claude Opus 4.8, Claude Opus 5, right? So am I looking for you guys to do GitHub Copilot with 10 different models, or am I looking to see, hey, here is the Claude Code A to Z? If you're using Claude Code, you take a napkin that has some ideas on it, translate it into a backlog, translate it into something that goes into production, and let's see if you can actually point out the pros and cons, right? Did it handle developer authentication and tokens well? Did it leak anything that was detrimental to the development team? That's what we're looking for: the actual pipelines, right, versus one harness to many models. Does that clarify the objective?

**Kapil Srikanth (10:42):** Yeah.

**Joseph Bressani (10:43):** Yeah, I was going to ask if it was just the different harnesses you're going to compare. Like Claude Code has a different structure than Codex, and they have different commands or how you connect the MCP servers. So we're focusing on the user experience versus the actual information we're getting.

**Chad Hage (10:50):** Exactly. The developer experience, yeah. Are you as a developer or a development team putting your business or your team at risk by using one of these—Claude Code versus GitHub Copilot versus Codex versus Antigravity, right? And which one does a better interpretation of the requirements to code, and adheres to architectural guidance? Like if you say, "These are the patterns that need to be followed," well, GitHub Copilot does a crappy job of following the patterns, but Codex does a great job—things like that. Does that make sense?

**Joseph Bressani (11:39):** Yeah, so there's also like Claude Code and Claude Code CLI. Would you want those two to be compared as well, or would they be on the same level?

**Chad Hage (11:50):** I'm willing to be convinced. I would say that there is a justification for why the CLI deserves a seat at the table. To me, if you're using a CLI versus the GUI, it's first of all about where you're more comfortable as a developer. Number two, generally speaking, the CLI has trailed, in my opinion, the full IDE. Where I see the CLI the most exercised is with GitOps-type practices—people doing CI/CD pipelines, very little coding, because obviously you need an IDE to really do meaningful coding. So if for some reason you want to convince not me, but convince the world—the audience who you're building this for—that the CLI deserves to be in that class, sure, go for it. I would love to see what you come up with.

**Joseph Bressani (13:04):** Okay, yeah.

**Ross Volenec (13:27):** ...evidence-based metrics and then also include...

**Chad Hage (13:28):** Yeah, I want to clarify what I meant by that. Thank you for the question. Usually what I meant by that is that what you guys are producing—a lot of times people think of the white paper as an academic product, which it is in many ways. But also when you think of Microsoft Ignite, a lot of the things that we put on stage are actual products, and we also put out the guidance on how to make use of that product. That's where something like a white paper or a microsite is dedicated to bringing that level of knowledge. 

We look at the world in levels at Microsoft:
* **Level 100** is like you can have just headlines about it.
* **Level 200**, you can talk to a boardroom about it.
* **Level 300 and 400**, you're expected to be able to actually do something meaningful, and **400** is considered the expert level.

What I was really referring to there is that typically when you go to an Ignite-like event, they'll put that level—L300 or L200—right there on the events. What I'm expecting to see would be on par with at least 200, ideally 300 or above. I don't want you to aim for 400 because that's an expert level and I'm not trying to give you something that is elusive in terms of a target, but someone who's actually gotten their feet wet and hands dirty with these harnesses and pipelines, in my opinion, should be able to put out easily a 200, if not a 300 level. I want to hear what Brad thinks about that—if I'm being a little too pie-in-the-sky, let me know, but I think 300 should be a level that you should aim for. Hey, Brad, you're on mute if you're around.

**Kapil Srikanth (15:32):** I think he said he's on a client call right now.

**Chad Hage (15:34):** Oh, he is? Okay, I didn't see the chat. Never mind, we'll catch up with Brad. Have you heard those terms before—the 100, 200, 300, and 400?

**Ross Volenec (15:53):** Not specifically, but I've got some pulled up here and I'm getting an idea for it.

**Chad Hage (16:00):** Yeah, so I would expect that for your final presentation—that is what I was really trying to say in that comment I made last week. If you leave it at L100, it's going to be subpar in my opinion. 200 is where you might start scratching the surface in terms of the level of detail and expertise that I'm looking for. If you go for 300, when you look back at this, this could be part of your portfolio going forward, and if you're expecting someone at Microsoft to look at your resume, they're going to want to see at least L300. So let's call it 250. Don't be below 200.

**Ross Volenec (17:10):** I think a well-defined set of specifications to begin with would probably get us to a 200 level.

**Chad Hage (17:16):** Yeah, and go see the examples on Ignite. Ignite is a public website. See what we cover at the Level 200 and Level 300. Maybe you look at it and think that's achievable, and come back with feedback. I'm happy to adjust.

**Ross Volenec (17:32):** Sounds good. Makes sense. Thank you.

**Bruno Rocha (17:46):** Right. So for constraints: you gave us a microsite detailing usage and results; budget is the $100 Azure credit across all four of us; evidence-based comparison, like you said last time, we need evidence to prove anything here realistically; and security-conscious design, so we don't want to break any token usage or leak anything.

**Chad Hage (18:17):** On that slide real quick: first of all, if you put your repo as a public GitHub repo, then GitHub lets you host microsites for free, but if you have a preferred way to make your site accessible, I have no preference. It's not a requirement, it's just a suggestion. So microsite, yes—GitHub Pages was just my suggestion for a free way to host your microsite if you make your repo public. My comment is just about it being listed as a constraint, that's all.

**Bruno Rocha (18:52):** Right. Speaking for myself, I have experience with GitHub Pages for my personal website, so realistically it will be through GitHub Pages. Next is Requirements—Kapil, I think this was your slide.

**Kapil Srikanth (19:16):** Yeah, that was me. We gathered four main features that you wanted:
1. The microsite.
2. Using the agents/harnesses that we select—right now we're really looking at the big four: Copilot, Claude Code, Codex, and Gemini/Antigravity, and we'll add more depending on what we're looking for with test cases.
3. Security—we don't want any of the agents to leak API keys or passwords and things like that.
4. The white paper and auditing the costs, tokens used, and time for tasks on each of the agents so we can properly measure that and see which ones are good or bad for certain processes.

**Chad Hage (20:25):** Like it.

**Ross Volenec (20:27):** On the subject of security, are you okay if we use existing tools like TruffleHog or GitLeaks to evaluate the code to try to pull secrets out? Because that would make it a lot easier for us to automate.

**Chad Hage (20:38):** Absolutely. I'm not going to dictate which tools. What I do want to see is a uniform benchmark. If you say, "I used tool X with Codex, but I used tool Y with another," then I'm going to expect a translation or harmonization layer so that the output can be apples-to-apples. What I want to steer you away from is saying, "Well, this one is good if you only measure it with that." Make sure the outputs are harmonized so that what you're producing can be compared in an apples-to-apples manner, because otherwise if every single tool uses its preferred way to grade it, everybody gets an A.

**Kapil Srikanth (21:33):** Yeah, you don't want cherry-picking for sure. Next slide: this was one of the user stories that we had. We came up with 12, but I felt like just putting this one with the acceptance criteria as a start so the PowerPoint wouldn't be too long. Looking at this story right here, I think it might be too much for one week—we should probably split this one and a few of the other stories into smaller stories. This is basically saying using GitHub to create the microsite with the database and passing the baseline test cases that we're going to make for it.

**Chad Hage (23:04):** I'm just curious when I read that as a story: *"As an engineer/researcher, I want a standardized full-stack application (UI, API, database) and an isolated testbed so that competing..."*—first, whether you use a database or just a persistent data store versus ephemeral data store is up to you. Second, the part that is a little confusing for me: are you envisioning with this story that you have one application and competing pipelines/harnesses are essentially iterating on the same instance, or is each pipeline delivering an instance side-by-side? In my mind, I'm reading this as the various pipelines you're going to create are all trying to compete to push an update to the same instance. That was never a requirement from me, but if that's what you guys decided, I'll align to it.

**Kapil Srikanth (24:20):** Yeah, that's kind of what I had in mind when creating this—all four of the agents competing on the same codebase.

**Chad Hage (24:35):** Same instance or the same codebase?

**Kapil Srikanth (24:38):** Same codebase.

**Chad Hage (24:40):** Okay, same codebase is fine, because then you can deploy that same codebase on four different instances, right? Same instance—you're definitely bumping up the complexity there. It would be nice to see how you resolve merge conflicts generated by the different harnesses, but that's more of a GitHub repo integration. To me, I'm happy if you can show me the same codebase deployed in four different instances and say, "This instance was A-to-Z Codex, this instance was A-to-Z Gemini/Antigravity," etc. One instance per harness is fine in my opinion, unless you want to crank up the complexity volume.

**Kapil Srikanth (26:10):** Yeah, that makes sense. We were thinking about creating a small codebase as a beta test first, and then going on to a bigger codebase. Next slide is Joseph's.

**Joseph Bressani (26:37):** These metrics we might have to change, especially after you mentioned that we're grading the harnesses instead of strictly the models. What we graded was:
* **Functionality (35%):** Making sure our code actually works as intended.
* **Security (25%):** Making sure the AI isn't deleting our entire database, no prompt injection issues, etc.
* **Code Quality and Refactoring (20%):** Optimized codebase, reuse of functions, maintainability.
* **Cost Effectiveness (10%):** How well it uses input and output tokens and how much it costs.
* **Automation (10%):** One-shot prompt where it doesn't need to ask a bunch of questions trying to understand what you're trying to get at.

**Chad Hage (27:56):** What's functionality? Can you break that down for me a little bit?

**Ross Volenec (27:59):** We have a little bit more information on the next slides too.

**Joseph Bressani (28:03):** Yeah, it's basically if it's correct or not—if it works as intended. The tests were adding a feature, debugging an issue, refactoring the codebase, and prompt injection.

**Chad Hage (28:07):** I like where you guys are headed with that. If I were to make one comment: on **Automation**, it gets a little foggy because everything is automated at this point, right? I would say **Autonomy**, and by now you should be thinking **Developer-in-the-Loop** versus **Developer-on-the-Loop**. I would love to see that broken down in those terms.

**Ross Volenec (29:15):** Could you provide a little bit more information on that? Because I had broken this down into human intervention required, merge failed, agent turn count, or needing additional prompting.

**Chad Hage (29:31):** You're going to see a lot of these AI-driven scenarios broken down into two modes:
* **Human-in-the-Loop:** Going from one milestone to the next and coming back to the human and saying, "Okay, I'm done, what do I do next?"
* **Human-on-the-Loop:** An increased level of autonomy for the agent, where the agent only comes to the human when the actual loop is defective.

It would be really cool if you put that Automation metric in the context of in-the-loop versus on-the-loop—which harness or UX provider is more in-the-loop heavy versus on-the-loop? For example, in GitHub Copilot, it used to have Edit, Ask, and Agent modes, and now we're just down to Agent. That shows you the rapid movement from in-the-loop toward on-the-loop.

**Joseph Bressani (31:06):** My intention with Automation was kind of like a `/goal`—you work towards this goal until you're done with one prompt, without asking questions, and whoever does it best gets the highest score.

**Chad Hage (31:33):** Yeah, we're in the same neighborhood. My recommendation for next week: do a little brainstorming around that and come up with a clearer statement on what you're trying to accomplish there, using the word *autonomy* rather than *no assistance*.

**Ross Volenec (32:24):** To go into these in a little more detail:
* **Functionality:** Code must be functional above all else; failures are penalized based on severity.
* **Security:** Using existing tools to assign ratings and