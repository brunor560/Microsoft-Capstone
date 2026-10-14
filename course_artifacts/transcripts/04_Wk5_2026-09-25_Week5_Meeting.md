# CIS4910 - Group 3 - Project MS2 - Senior Project Meeting (Week 5)

- **Date:** September 25, 2026, 8:33 PM
- **Duration:** 38m 3s
- **Participants:** 
  - **Sponsor (Microsoft):** Chad Hage *(Bradley Lawrence absent due to travel)*
  - **Student Team:** Bruno Rocha, Ross Volenec, Kapil Srikanth, Joseph Bressani

---

## Meeting Notes (from `Meeting with Chad : 2026 Sep 25.pdf`)

- **Critical Path (MoSCoW):** Must, Should, Could, Won't
- **Framework vs. Specific Implementations:** Multidimensional
- **SRS Feedback:**
  - Clear up TBD issues?
  - Make sure the SRS is geared towards broader framework and not just the pipeline focus.
- **Platforms / Harnesses Discussed:**
  - Google Antigravity
  - Claude Code
  - GitHub Copilot
  - VS Code
- **Security Principles:** Secure by Design, Secure by Default — How can developers achieve that? How does that translate between development platforms?
- **New EPIC Statement / Executive Persona:**
  > *"I'm a client wanting to buy 10,000 seats for my institution. Which platform do I go with? What's the overall score? How does that score break down?"*
- **Core Distinction:** This is not about any specific model; this is about the **harness**.
- **Baseline Testing Idea:** Evaluate one model between platforms, or evaluate how common features (like GitHub `/create-agent` or `/create-skill`) apply across different platforms.
- **Takeaway:** Framework approach is resonating with Chad.

---

## Executive Summary & Key Takeaways

### 1. Critical Path & MoSCoW Prioritization
- Chad introduced the **MoSCoW** method (**M**ust, **S**hould, **C**ould, **W**on't) to define the project's critical path. The critical path consists strictly of the **Must** items (and avoiding **Won't** items that shoot the team in the foot).

### 2. Extensible Evaluation Framework & Business Persona
- **Framework over Point-in-Time:** The team's SRS concept of building a *reusable framework* strongly resonated with Chad. If a new pipeline (e.g., Meta Muse, new Claude Code, Google Antigravity) or a new evaluation category emerges six months from now, the framework should allow plugging it in and adjusting weights without a complete rewrite.
- **The Executive Buyer Persona:** Frame the output for a Chief Development Officer or institution buyer deciding where to cut a check for 1,000 to 40,000 seats. For example, if Claude Code scores 9.5 overall ($100/seat) and GitHub Copilot scores 9.0 ($50/seat), a buyer can drill down into the **Security/Compliance** sub-score (e.g., Copilot 8.5 vs. Claude Code 6.5) to make an informed, evidence-backed purchasing decision.

### 3. Harness vs. Foundation Model
- **Evaluating the Harness:** The focus is on how the *harness* (IDE integration, `/create-agent`, `/create-skill`, `.github/agents` vs. local `.md` files, server-side vs. local agent execution, MCP support, secret/token handling for Zero Trust) operates, rather than just benchmarking raw LLM intelligence.
- **Establishing a Baseline ("The Bar"):** The team identified a challenge: Claude Code only runs Anthropic models, while Copilot/Cursor/Antigravity can run multiple models. The team will research how to establish a fair, objective baseline methodology before doing major development.

### 4. Team Progress Updates
- **SRS Presentation:** The team completed and presented their SRS slide deck for their professors (Dr. Ken Christensen and Scott). They will update the SRS Word document to emphasize the broader evaluation framework rather than just a single prototype pipeline.
- **Prototype Pipeline:** Ross built an initial AutoGen-based prototype pipeline spinning up a Docker container, connecting to Azure (using GPT-4o-mini), running basic tests in isolation, and outputting JSON telemetry artifacts.
- **Next Steps:** Bruno and Kapil are working on the comparison demo UI, while the whole team will align on the objective scoring/baseline methodology.

---

## Full Meeting Transcript

*Kapil Srikanth started transcription*

**Chad Hage (0:05):** Updates to the GitHub issues. Thank you for that. That made a lot more sense as to kind of get a sense for where you guys are at. I did try, you know, try to reply or post back some comments, but yeah, take it away.

**Bruno Rocha (0:19):** Mhm.

**Kapil Srikanth (0:23):** Mm.

**Bruno Rocha (0:23):** We honestly have been mainly focusing on this week. We had our SRS presentation. So that was the main thing we're working on this week. That's why there's not a whole lot of updates in terms of the actual project itself. So that's why we're just going to go through a PowerPoint view and see if you have any comments, questions, concerns about what we've gone through so far with the SRS stuff. Then we'll just keep moving forward after.

**Chad Hage (0:44):** Yeah, I mean, I did go through it. That was really helpful. See, that's kind of like what I was hoping for. But that was really helpful. I get a sense for where you guys are at with us. I mean, by the way, that SRS is a deliverable. So you were working on the project. It's just a different type of deliverable.

**Bruno Rocha (0:48):** Yeah.

**Kapil Srikanth (0:58):** Okay.

**Bruno Rocha (0:58):** Yes. Yeah.

**Kapil Srikanth (1:02):** Right, yeah.

**Chad Hage (1:03):** And so, you know, your number one customer is Doctor, you know, Ken Christensen is your number one customer. Scott is, you know, 1B, like 1A, 1B.

**Bruno Rocha (1:16):** Mhm.

**Chad Hage (1:16):** You know, I'm obviously the sponsor, but yeah, so I'm all for you guys making sure that you have what you need to be able to pass this, you know, the scores at the end of the semester, and that includes the completion of that document. I did see a lot of things that were still, I guess you can call them TBDs or, you know, things that are still and need to be fleshed out.

**Bruno Rocha (1:46):** Right.

**Kapil Srikanth (1:47):** Right.

**Chad Hage (1:48):** And that's fine. I presume, you know, at some point, you know, I'm all for iterative and incremental. The gist of it, I think, is still a little bit... I think, you know, to try to map. Let me describe it as such. Do you guys have a good sense of what I mean when I say the critical path?

**Bruno Rocha (2:15):** Yes.

**Chad Hage (2:16):** Does critical path mean anything?

**Ross Volenec (2:19):** Like a kind of like the minimum viable product, like the specific thing, the targets that we need to hit.

**Chad Hage (2:27):** No, it's not the minimum viable product. It's more of the, here's everything that must be done and anything else that is on that line that is not required needs to go away. Right? So if you think like, if it's, you know, one way that I've used in the past is called MoSCoW.

**Ross Volenec (2:40):** Okay.

**Chad Hage (2:48):** M-S-C-W. M stands for Must, S stands for Should, the C stands for Could, and the W stands for Won't. Like we must do this, we should do that. We could do this other thing, but we will not do, you know, this one particular thing. Does that make sense?

**Ross Volenec (3:11):** Yes.

**Bruno Rocha (3:12):** Right.

**Kapil Srikanth (3:12):** Yes, yeah.

**Chad Hage (3:13):** Yeah. So, you know, when you look at a critical path and applying MoSCoW as the way to figure out your critical path, it's only the Must, not the Should, not the Could. You know, maybe there is room for the Won't do that, because those are typically things that, you know, are gonna shoot yourself in the foot with.

**Kapil Srikanth (3:35):** Mmh.

**Chad Hage (3:39):** That makes sense. So figure out what the Musts are, and that becomes your critical path. Everything else is a Should, Could, and a Won't.

**Ross Volenec (3:51):** So I was looking at the initial document you gave us at the beginning of the semester today, and just to make sure that we weren't getting off track. And it seems like the core deliverable is, you know, like educational materials regarding different pipelines, different agent models, and then evidence-based conclusions based on, you know, where things are effective, things to, you know, look out for for developers, that kind of thing, and then the microsite to show the results, is that still correct, right? Like, the pipeline that we're working on is like is a means to that end to get the evidence that we need to support our conclusions.

**Chad Hage (4:31):** Yeah, and so I like how one of the things, one of the items that I read described it as a framework, which I actually like. It's not so complete that, you know, that is so rigid, that is so fixed to the tools that you will identify today. I like that part, right? And yeah, so that's cool, right? So in like, let's say six months from now, somebody wants to take that and say, hey, there's a complete, you know, lineup of different pipeline providers. Today, GitHub Copilot, you know, with SpecKit and VS Code, for example, or whatever your IDE is, that's one pipeline, right? But let's say tomorrow you want to plug another pipeline in or two or three pipelines side by side. I like the framework...

**Kapil Srikanth (5:30):** Mmh.

**Chad Hage (5:35):** ...aspect of it. I like how you guys, you know, took that approach. But yeah, the idea is that, you know, as a developer today, I, you know, and the Chief Development Officer architect choosing a, you know, the harness, the, you know, the IDE, the path to production. Is Claude Code, you know, versus Codex versus GitHub Copilot? Because here's the way the arc of this leads to, guys. If you go, if you say, hey, GitHub Copilot achieves, and I'm making this number up, let's say based on your framework and your methodology, you say with GitHub Copilot, with Visual Studio Code, and GitHub as your GitHub Actions, etc., and you give it a score of 9, right? And relative to that, you know, Anthropic, you know, Claude Code scores a 9.5, and Codex scores an 8. Well, how does that translate from a business standpoint? The business effect of this is going to be, hey, I, as let's say USF, I'm going to license the, you know, the product that you guys gave the highest score to. And that's like, let's say 100 bucks a year for a student, and I have 40,000 students. I'm making these numbers up, but suddenly that report, that output you're producing drives decisions.

**Kapil Srikanth (7:22):** Right.

**Chad Hage (7:23):** Am I making sense?

**Kapil Srikanth (7:25):** Yeah, yeah.

**Chad Hage (7:26):** Now let's take that a little bit further and say, you know what, I want to know why they gave 9.5 to Claude Code and 9 to GitHub Copilot. Like they're so close and the cost differential, GitHub Copilot is going to be a $50 per seat, whereas Claude Code is $100 per seat. And then I start digging deeper and it shows that actually on the security aspect, GitHub Copilot scored an, you know, an 8.5, and Claude Anthropic code, you know, the Claude Code scored a 6.5. Well, now it's a no-brainer.

**Kapil Srikanth (8:03):** Right.

**Chad Hage (8:03):** Even though the overall made it seem like I need to go with Claude Code, when I zoomed in and I looked at the actual key area that I care the most about, right? And that could be, you know, when it comes to how, you know, secrets are handled, that could be for compliance, for example. So I like the framework because...

**Kapil Srikanth (8:09):** Anthropic. It.

**Chad Hage (8:26):** ...it made me feel like you guys are getting it. I should be able to introduce more things that I want to evaluate by simply modifying, you know, the actual evaluation without changing the methodology. If I just add more things that I want to evaluate, all I'm doing is I'm changing the weights, right? Or I'm changing the parameters that I want to evaluate the pipeline against, number one or two. But also I could change the entire pipeline. I could put, you know, Meta Muse against, you know, Gemini with the...

**Kapil Srikanth (8:48):** Yeah.

**Chad Hage (9:04):** What's the name of that Google tool? I forgot the name of it, anyway. But yeah, so is that making more sense?

**Bruno Rocha (9:17):** Yes, yeah.

**Kapil Srikanth (9:17):** Yes, yeah.

**Ross Volenec (9:18):** Yes, like just, you know, as a framework instead of like the specific software that we're creating is the interesting part of this, it sounds like.

**Chad Hage (9:30):** Yeah, that's why I was saying, like, if you guys pick a to-do app, or you can, I mean, I just wanted something a little bit more than hello world, because then you can introduce requirements, right? What a to-do, I mean, you can choose whatever you want. I'm not telling you what to choose. I'm leaving it up to you guys. And I hope that that doesn't turn into analysis paralysis. But the point is...

**Kapil Srikanth (9:37):** Right. Yeah.

**Chad Hage (9:49):** ...pick something that you can introduce requirements to, which necessitate introducing test cases to, which then necessitates to do a CI/CD pipeline augmentation or refactoring, which then necessitates the refactoring of existing code and introduction of new code. Right, and then the deployment has to happen, and you can show the journey from what I call whiteboard or napkin, where the requirement was imagined, all the way to where it can be interacted with in a live scenario. For example, production or staging, or you know, one of the slots, is that clear?

**Bruno Rocha (10:38):** Yes, at least to me, yeah.

**Ross Volenec (10:39):** Yes.

**Chad Hage (10:41):** Okay, was that the understanding you had before you wrote the, you know, the SRS that you guys did? Is that the same understanding you had when you submitted your requirements? Or is it different?

**Bruno Rocha (10:56):** I mean, I wouldn't say necessarily it's too different. I would say there's less of emphasis on the framework aspect, more so than there ideally is on the paper right now. So that's something that we can add more of emphasis on as a whole. We do mention that it's meant to be expanded upon in the future, just not to the extent that we wanted. If that makes sense.

**Ross Volenec (11:21):** I was thinking that the SRS document is a little too specific to the prototype pipeline that we're making, that we're going to have to branch out a bit from here.

**Kapil Srikanth (11:29):** True.

**Chad Hage (11:35):** Okay, I mean, the sooner we start seeing what your interpretation of that in that form of an actual pipeline, whether it's on GitHub Copilot or one of the other, you know, platforms, the sooner we'll be able to say, yeah, this is it. No, that's not it. But yeah, for now, I mean, I'm all for you guys getting the documentation caught up to where you need to be. Yeah, that's par for the course. Keep doing what you're doing.

**Ross Volenec (12:12):** All right.

**Bruno Rocha (12:12):** Who wants to present the SRS? Does anyone have it up already?

**Ross Volenec (12:19):** Are we presenting the SRS document or?

**Chad Hage (12:19):** Well, if you want to point out something specific that you need my attention to, I already reviewed it.

**Bruno Rocha (12:24):** Ohh, perfect.

**Kapil Srikanth (12:25):** Okay.

**Ross Volenec (12:25):** Okay.

**Chad Hage (12:25):** And I think I gave you my feedback on it. I, you know, you acknowledge that there's a lot of TBDs in there, unless there's a different version out there that's more complete and you want to submit it. You know, I saw you put the link to it, so I think I have the most recent version.

**Kapil Srikanth (12:31):** True.

**Bruno Rocha (12:40):** Uh, let me see, just a...

**Kapil Srikanth (12:42):** Do you have the sorry, do you have the live version like the?

**Ross Volenec (12:42):** That.

**Chad Hage (12:48):** It's on SharePoint, right?

**Joseph Bressani (12:50):** It should be, it should be live, but...

**Kapil Srikanth (12:50):** Yeah, yeah, okay. It's on SharePoint, so it should be the live version.

**Ross Volenec (12:51):** Yes.

**Bruno Rocha (12:53):** Yeah, it's under your comment. Yeah, yep, that's most up to date.

**Chad Hage (12:54):** Yeah.

**Joseph Bressani (13:01):** You saw around, I think it was 15 slides.

**Bruno Rocha (13:07):** Yes, 15.

**Chad Hage (13:08):** Yes.

**Bruno Rocha (13:10):** Yeah, then that was the most up-to-date one then. And then Scott has us not touch the PowerPoint itself. We're not allowed to touch it after we present it. And then he wants us to submit it as is. But then for, I believe for the document, the actual Word doc we're allowed to touch. So then from there we can, we'll ensure that like...

**Kapil Srikanth (13:29):** Yeah, yeah, because that's good something.

**Bruno Rocha (13:34):** We talk more about creating a framework more so than we already have it.

**Kapil Srikanth (13:41):** I didn't see the feedback though. I don't know. I didn't see that. Like, where is it?

**Bruno Rocha (13:48):** Um... It's on Joseph's comment.

**Kapil Srikanth (13:51):** Yeah. Because I looked at the comments of Joseph. I saw the PowerPoint and the Word, but I didn't see a... Uh, like, because, uh, I mean, Chad, you said that you put some feedback, so I was just wondering where that was.

**Chad Hage (14:15):** On which one?

**Kapil Srikanth (14:17):** For the SRS document, I believe you said you provided some feedback to us. I was just wondering where that was.

**Chad Hage (14:22):** No, no, I provided the feedback here on the call. I see that you have some TBDs. I see some things that are still, you know, like I think that's not the final version is what I'm trying to say. And it sounds like you'll iterate on that document. But wait a minute, if you said that Scott said you can't touch it after today.

**Kapil Srikanth (14:25):** Ohh, ohh.

**Bruno Rocha (14:26):** Okay.

**Kapil Srikanth (14:28):** Okay, yeah.

**Bruno Rocha (14:31):** Yes.

**Kapil Srikanth (14:36):** Right.

**Chad Hage (14:43):** What am I missing?

**Bruno Rocha (14:43):** We can't touch the slides. The slides we cannot touch, but the document itself we can.

**Kapil Srikanth (14:45):** We can't touch the slides, but the doc we can.

**Joseph Bressani (14:49):** The one you probably saw was the one on, I think we submitted it on Tuesday. And that was, it was an incomplete version of it at the time. It was just like what we had.

**Chad Hage (14:49):** You can't touch the slides, but the document. Yeah. Okay. Yeah, because that's what I was kind of confused by that statement.

**Joseph Bressani (15:04):** So I don't think we had the TBDs.

**Kapil Srikanth (15:08):** Yeah, the TBDs were changed by...

**Joseph Bressani (15:08):** The TBDs or the epics and stuff, we didn't add any of the requirements in at the time.

**Chad Hage (15:15):** Gotcha, gotcha. Okay. Yeah, yeah. I just want you guys to have a good, polished presentation at the end of the year. And, you know, if you say that that's your, you know, final presentation for the end of the year, then I'm going to say, how did we miss that? But if you're saying that that's not...

**Kapil Srikanth (15:17):** Yep, so the current SharePoint.

**Chad Hage (15:34):** ...the one that was submitted, and you have the ability to make it polished. I mean, I just want you guys to know that I have a vested interest in making sure you guys shine at the end of the year. My name is next to your name, so.

**Kapil Srikanth (15:47):** Right.

**Chad Hage (15:50):** So is Brad's too, and Microsoft, so we have a vested interest in making sure that this is well put together.

**Bruno Rocha (15:52):** Yeah.

**Kapil Srikanth (15:53):** Yeah. Uh-huh.

**Chad Hage (15:58):** Okay.

**Kapil Srikanth (15:59):** Where is Brad? I'm just curious.

**Chad Hage (16:01):** He's traveling today. We're both traveling, but he's traveling by air, I'm traveling by land, so.

**Kapil Srikanth (16:03):** Ohh, okay. Oh, someone got the short end of the stick.

**Chad Hage (16:10):** No, no, he's just out of state. I'm local, but I'm just...

**Kapil Srikanth (16:13):** Ohh, okay, okay.

**Bruno Rocha (16:13):** Oh, okay. And then quick question regarding the API key holding and how to properly deal with the security stuff. I know you said you saw my comment regarding adding it as a volatile variable instead, would that be enough security or would that have to be like increased? Because my current thought process with it is just that it would be volatile from where as soon as the user exits out of the website, it will automatically be cleared. But is that necessarily enough to ensure the security is fine or would that need more security on top of that?

**Chad Hage (16:54):** So I want to make sure that we're talking about this in terms of apples to apples, right? So the way that when you say, you know, for example, when you are using, and I'll, guys, I'll probably reference GitHub Copilot more often than anything else, because that's what I use on a daily basis, a daily driver.

**Kapil Srikanth (17:12):** Yeah, that's fair.

**Bruno Rocha (17:13):** Mhm. Yeah.

**Chad Hage (17:16):** Antigravity, that's the name of the, you know, the product that Google puts out there. Their IDE is called Antigravity and even Claude Code. I do Claude Code, maybe less than 20% everything else and GitHub Copilot is 80%.

**Bruno Rocha (17:22):** Mhm. Mhm.

**Chad Hage (17:32):** I was just looking at my usage for the month. I'm like at 1.2 million tokens. So, and it's all GitHub Copilot, right?

**Kapil Srikanth (17:38):** Mhm.

**Bruno Rocha (17:40):** Mhm.

**Chad Hage (17:41):** But anyway, so the point that I'm trying to make here: I'm more interested in you guys exposing how the GitHub Copilot architecture handles tokens, handles secure development. You know, like if you can actually tune it, if you can actually say, hey, through prompting, through skills, through the actual...

**Bruno Rocha (18:01):** Mhm.

**Chad Hage (18:08):** ...features of the GitHub Copilot harness itself. This is how developers who are trying to do secure by design, secure by default, and zero trust can achieve that. That's what I'm looking for, right?

**Bruno Rocha (18:12):** Mm.

**Kapil Srikanth (18:23):** Thank you.

**Bruno Rocha (18:23):** Okay. Okay.

**Chad Hage (18:24):** And then when you take that same methodology and move it to, let's say, Antigravity, and all of a sudden, Antigravity does not honor any of those settings. Well, does it honor a different setting to achieve the same outcome? Or is it like, hey, forget about it. There's no such thing as zero trust on Antigravity.

**Bruno Rocha (18:38):** Okay.

**Chad Hage (18:43):** I don't know the answer to that because I didn't spend the time to figure out Antigravity. I'm hoping that you guys would tell me, right? But I know Claude Code, there are certain features in GitHub Copilot that are missing in Claude Code. And I know that the opposite is also true. You know, I think my impression with Claude Code, the harness is sort of...

**Bruno Rocha (18:48):** Right, okay. Yeah.

**Kapil Srikanth (18:49):** Mm.

**Bruno Rocha (18:55):** Mhm. Mhm.

**Chad Hage (19:03):** ...you know, the basic harness just to get the... where Anthropic flexes its muscles is with the model, so you're gonna see like Opus, you know, 4.6, Opus 5, you know, Sonnet, whereas GitHub Copilot...

**Bruno Rocha (19:14):** Mm-hmm.

**Kapil Srikanth (19:15):** Okay.

**Bruno Rocha (19:21):** Mhm.

**Chad Hage (19:23):** ...you know, it doesn't care about which model you want to use. It's up to you. So you'll see that GitHub Copilot, for example, is going to have significantly, you know, additional features when it comes to MCPs and understanding extensions in VS Code. And like GitHub Copilot understands VS Code really, really well, and it knows...

**Kapil Srikanth (19:43):** It is.

**Bruno Rocha (19:44):** Mhm.

**Chad Hage (19:44):** ...you know, what kind of extensions do you have available and it knows, you know, where your subscriptions are and things like that, right? So, that's when you are looking at, again, your persona is that individual decision maker who is trying to choose...

**Kapil Srikanth (20:23):** Mhm.

**Chad Hage (20:23):** Am I paying? Am I cutting a check to Anthropic? Am I cutting a check to, you know, GitHub? Am I cutting a check to, you know, Google?

**Bruno Rocha (20:23):** True.

**Kapil Srikanth (20:27):** Yeah. OpenAI, yeah, or whatever, yeah, yeah.

**Chad Hage (20:33):** You see, that's the part that you guys are able to demystify by putting this framework together.

**Bruno Rocha (20:43):** Okay, understood.

**Chad Hage (20:45):** Yeah?

**Bruno Rocha (20:46):** Yeah.

**Kapil Srikanth (20:47):** Right, because our score will help drive the decision, right?

**Bruno Rocha (20:48):** Okay.

**Chad Hage (20:51):** Right, and then when you do get a little bit more traction, what I think you might be able to start pointing out is the part where you say, hey, for these types of, you know, use cases, right, that skill will play nice across all the different pipelines, all the different harnesses with, you know, regardless of which model you have, whether it's, you know, Gemini Flash versus, you know, that's why this is not about the model as much as it is about the harness, right?

**Kapil Srikanth (21:17):** Mhm. Okay. Yeah.

**Bruno Rocha (21:31):** Understood, yeah, yeah.

**Chad Hage (21:32):** In fact, if anything, maybe you actually run an apples to apples where you say, hey, because, you know, this model happens to be available across all the different pipelines, that becomes your bar. I don't know what that model is. It might be GPT-5.6. I don't know. You guys need to say, hey, we're selecting this model to be the bar that we run all the harnesses against and then score them because it's available across all the different pipelines. Right?

**Bruno Rocha (21:49):** Mhm.

**Kapil Srikanth (21:53):** Mhm. Right.

**Chad Hage (22:08):** But then, if you actually take the Claude Code harness and pair it with, you know, Opus 5, suddenly you have additional, you know, features that weren't there with 5.6. I don't know. Is this helping?

**Bruno Rocha (22:30):** No, it is. It is.

**Kapil Srikanth (22:30):** Yeah, yeah, a lot, yeah.

**Ross Volenec (22:31):** Yes.

**Chad Hage (22:38):** I mean, like, I'm on a daily basis so immersed in the GitHub Copilot user experience and the pipeline to, you know, from like what I call whiteboard to a test environment or to some kind of an environment where I can deploy to that I haven't had a chance to really apply...

**Bruno Rocha (22:39):** I think. Mm-hmm.

**Chad Hage (22:57):** ...all the capabilities or all the features and benefits that I know GitHub Copilot can do, but I was looking to do something with Claude Code. I'll give you a very basic example. In GitHub Copilot, I can do a lot of the slash commands. Like you do `/` and then it gives you the ability to specify like, hey, I want to see, you know, like the one I use quite a bit, it's called `/create-agent`, `/create-skill`, right? Well, I was in, you know, Claude Code and I tried to do `/`, but it didn't understand what `create-agent` means.

**Kapil Srikanth (23:31):** Mhm.

**Chad Hage (23:39):** You know what I'm saying? So now if I want to create an agent in Claude Code, well, how do I do that? Well, I can craft it. At the end of the day, it's an `.md` file that gets generated, but in GitHub Copilot today, meaning the engineers who developed that harness have made it so that I can just do `/create-agent`, describe what the agent needs to do, and then boom, it does all the, you know, mechanics of what needs to happen under the hood for that agent to become part of that repo.

**Bruno Rocha (24:07):** Mhm.

**Kapil Srikanth (24:07):** Mhm.

**Chad Hage (24:12):** You see what I'm saying?

**Kapil Srikanth (24:13):** Yeah.

**Ross Volenec (24:14):** Mhm.

**Bruno Rocha (24:14):** Right, yeah.

**Chad Hage (24:16):** And so now if I'm doing an enterprise development and I have a team that finds all the different highly reusable skills or agents across the teams and I can create a repo, then every new project that starts ends up, you know, cloning or forking that. And all of a sudden you have, just to give you an example, I have in one of, and I'll demo this to you guys next week, but one of my agents is called a Scrum Master. The other one is called, you know, a Full Stack Developer. I have an agent called Full Stack Developer, right? And I can run, you know, 4 agents, and I have an agent called, you know, Scrum Team, right? So Scrum Team goes and creates 4 sub-agents called Full Stack Developers, adds a, you know, Scrum Master, for example. I can't do that with Anthropic Claude Code. I'd have to actually manually craft it. And if I go sit there and create the `.md` files and store them in very specific locations in that harness in Claude Code, yeah, it will honor them, but there's probably a different way to do it in Claude Code, right?

**Kapil Srikanth (25:09):** Okay.

**Bruno Rocha (25:23):** Mm-hmm.

**Chad Hage (25:24):** Is that helping?

**Bruno Rocha (25:27):** It is, yeah.

**Ross Volenec (25:27):** Yes.

**Kapil Srikanth (25:28):** Yeah.

**Chad Hage (25:28):** Yeah. And I haven't found a way to do it in, you know, Antigravity, but I'm sure that if I put it in a repo, you know, I don't know, maybe it will, maybe it won't. I don't know. I haven't tried it with Antigravity.

**Ross Volenec (25:46):** So in our final white paper, you would want to see like an educational portion talking about some of these features and how they translate between different platforms.

**Chad Hage (25:55):** Yeah, I mean, at the end of the day, I think the white paper concept was a back and forth with Ken, you know, and for me, what I would like to see is that ability to say, hey, what you described as a framework is exactly what I was looking for. But Ken and I went back via e-mail and we said, well, we can do a white paper. I said, that's fine. But ideally, the next version of, you know, Meta Muse or a next version of Claude Code comes out, you know, your framework simply pulls latest and reruns it and it gives it a score based on the categories that we've identified. And if, you know, tomorrow a new category comes up and, you know, suddenly it becomes hypercritical for everybody to be measured against that new category, adding a new category should not require a rewrite.

**Kapil Srikanth (26:52):** Mhm.

**Ross Volenec (26:52):** Right.

**Chad Hage (26:54):** Okay.

**Kapil Srikanth (26:55):** Yeah, it shouldn't break down or anything once new models or such come out, yeah.

**Chad Hage (27:02):** Right. All right.

**Bruno Rocha (27:14):** All right, I think that... does anyone else have any questions?

**Chad Hage (27:16):** So, let's go real quick. Do you have stuff that's planned for next week? Is there...

**Ross Volenec (27:22):** Mhm.

**Chad Hage (27:25):** You know, does each one of you know what you're gonna focus on coming out of today's call? Or does anyone need, you know, to have like a breakout session to discuss more? Either way, it's important to know.

**Bruno Rocha (27:41):** I'm working with Kapil a lot to finalize getting at least some base level model of comparisons eligible in the demo. Right now, it's just a blank page that shows nothing. Our goal is to finish that by next week. That way Friday, we have some sort of demo for you. That's me and Kapil's main thing.

**Chad Hage (28:00):** Okay. Have you guys decided on, are you guys going to work on all the harnesses at the same time or are you going to break it down? Each one of you going to take a harness or what's your strategy? I don't have a preference. I'm just more curious than trying to direct in any way.

**Ross Volenec (28:02):** I uh...

**Bruno Rocha (28:15):** Um... As of right now, we're just going to do all of them at once, like, not like saying like who is doing, who's busy, who's not. Me and Kapil will just split up amongst each other. Realistically, it'll be a joint effort. We already have a call kind of scheduled-ish rough time. We're both going to work on it. So then that'll just mean it'll be us, but then depending on how...

**Kapil Srikanth (28:34):** Yeah, yeah.

**Bruno Rocha (28:38):** ...much workload, we have other things, we'll kind of split it off into Joseph and Ross as well, 'cause technically on the paper, like, I'm technically the Anthropic person, Joseph's technically like the Copilot, like stuff like that, but realistically there's too much to get done to where there's no need to have each person do one thing, if that makes sense, where they can be prioritized somewhere else.

**Chad Hage (28:58):** Yeah, and again, I wanted to see how you guys kind of strategize, you know, because in my mind's eye, I was thinking like, you either break it down by, I'll take, you know, one pipeline, one harness, and you'll take, you know, the next one. And then we'll just all implement all the features, or you can say, you know, by feature and then you have to get the feature working across all the pipelines. So either horizontal by feature or vertical by pipeline. That's what I would, you know...

**Kapil Srikanth (29:36):** Mhm.

**Chad Hage (29:36):** That's what I would be thinking in terms of those are the two strategies.

**Bruno Rocha (29:37):** Mhm.

**Chad Hage (29:41):** Anyway, those are the two strategies that I came up with. I'm sure I can think of other ones, but I didn't want to spend too much time on that. I wanted to see what you guys would come up with.

**Bruno Rocha (29:47):** Mm.

**Kapil Srikanth (29:49):** Yeah.

**Ross Volenec (29:49):** Right. As far as my update goes, that kind of ties into that. I spent some time this week putting together a prototype pipeline. It's not ready to demo yet, but I was able to get an AutoGen-based pipeline. It's spinning up a Docker container and exposing only the appropriate code for security reasons. And it is able to connect to Azure. I got it set up to use, I think it was GPT-4o-mini, just because it was cheap. And I got it to create the, it ran some tests in the container, just some basic tests. And it was able to create the JSON as an artifact for telemetry. So it is functional. It still needs a bit of work, but that's what I've been focusing on. And my goal is that, as you said, we will be able to have specific tasks that we can feed into the pipeline, change up the models relatively easily, and then have a series of modular tests that we can expand as we go. So as far as developing different pipelines simultaneously, I was hoping to get this one pipeline running, and we can learn what we can from it, and then perhaps apply it to other pipelines as well.

**Chad Hage (31:13):** Okay. Any blockers?

**Bruno Rocha (31:20):** As of right now, no, at least for me and Kapil, but also we haven't necessarily got too deep into it to have a blocker, if that makes sense. Like, we've both been just a little busy this week to where we didn't have enough time to really dive deep enough to obtain a blocker. So that's our thing. Then we'll add something to the GitHub if there is something that has come up.

**Kapil Srikanth (31:22):** Yeah. Yeah.

**Bruno Rocha (31:39):** I'm hoping nothing does. Fingers crossed. But as of right now, no.

**Kapil Srikanth (31:39):** Yeah, fingers crossed.

**Joseph Bressani (31:45):** I do have a question about the, so you mentioned like a baseline for like, if I guess...

**Chad Hage (31:46):** Okay. Mhm.

**Joseph Bressani (31:56):** Copilot has 5.6, and then OpenAI has 5.6, and Cursor has 5.6, Antigravity at 5.6. How would we tie Claude Code into that? Because Claude Code wouldn't have an OpenAI model. So are we looking for VS Code wrappers where everyone's able to use a whole range of models or we're looking for just the harness and we just try to change the grading category if we can't all get the same model as a baseline for each?

**Chad Hage (32:33):** And that's exactly why I was asking, like, how are you going to actually achieve that, right? I don't know what the bar ends up being, to be completely frank. I did not have an answer in mind when I said that. But I was interested in seeing, how are you guys going to say, this is our bar. Because I knew that that was going to come up as a potential, you know, wrinkle. And I'll be completely, you know, frank and candid with you. I have not spent the time to research of how I would justify my methodology. So, good question. Excellent question, because I was curious as to how you guys were going to come up with a, you know, what your bar is going to be.

**Ross Volenec (33:20):** I think that's probably something that we should focus on before, like any major development at this point, is just to spend a lot of time thinking about the tests and, you know, what is objective, what is subjective, and what exactly we should be focusing on as far as the scoring goes.

**Chad Hage (33:29):** Mhm. I think, yeah, I think you're right.

**Kapil Srikanth (33:45):** Yeah, so all four of us will try and research that. Yeah, all four of us will research that and we'll come together at our usual time and then we'll compare notes and hopefully we'll find an answer.

**Bruno Rocha (33:45):** We'll figure that out, yeah. Yeah. So then in that case, then, like we might push the demo a little bit in that case, depending on how much we can get into that, we'll push it a little bit. And we'll see, because I believe this is week 5, I believe, if I'm not mistaken. Yeah, then we might push the demo a little bit, maybe to the following week then, depending on how much we can...

**Kapil Srikanth (34:10):** Yeah, this is week 5.

**Ross Volenec (34:10):** Yes.

**Bruno Rocha (34:17):** ...really get into it. For context, because, to be frank, like, after our meeting time with you, we usually sit here for the next half hour, kind of discussing internally and like, hey, what's what we're going to do this next week? And then we meet Monday as well. So then, and then sometimes Tuesday.

**Chad Hage (34:36):** Here, take a look at this repo that I just posted in the chat. I don't know if one of you wants to present it, just to share your screen so I can kind of do the over the shoulder. Like here, for example, you know, if you are looking at using the GitHub built-in features, you can see where it says `Agents` right in between `Pull requests` and `Actions`.

**Ross Volenec (34:50):** I got it.

**Bruno Rocha (34:50):** Alright.

**Kapil Srikanth (34:54):** Okay. Ohh. Yeah.

**Chad Hage (35:08):** Yeah, and so click on that and you'll see there's, yeah, if you click on `Agents`, you'll see that there is nothing because I intentionally did not use the GitHub Agents to implement this code. But if you go back to `Code`...

**Kapil Srikanth (35:09):** No, not right there. Yeah.

**Chad Hage (35:26):** ...and click on `.github`. You see `agents` there.

**Kapil Srikanth (35:32):** Mmh.

**Chad Hage (35:34):** See `agents`? Yeah. So just an example, you know, like I created those as agents, just, but that's more portable across pipelines, across harnesses. That's just an example.

**Kapil Srikanth (35:35):** Yeah, and there's stuff.

**Chad Hage (35:48):** Right.

**Bruno Rocha (35:49):** Okay.

**Chad Hage (35:49):** Now, you can say, but Chad, what you're missing out on is by not using Agents in GitHub, that means these agents can only run locally, which is true, right? Versus having the agents implemented in GitHub, right? Now my agents can run server-side, even when I'm not on my desktop to run them.

**Bruno Rocha (36:11):** Ah.

**Chad Hage (36:12):** Right? And so, this is just an example of one of the features that could be evaluated when I say evaluate the pipeline. Now, if you're using GitHub Copilot with GitHub as the, you know, repository provider, that's, you know, that's an integration feature that...

**Bruno Rocha (36:13):** Yeah.

**Chad Hage (36:32):** ...really shines, right? But you break your integration with Claude Code, because Claude Code does not have a good harness for the Agents feature on GitHub, for example, right?

**Kapil Srikanth (36:49):** Yeah.

**Bruno Rocha (36:49):** Yeah.

**Chad Hage (36:50):** Is that making sense?

**Bruno Rocha (36:52):** Yes.

**Ross Volenec (36:53):** Yes.

**Kapil Srikanth (36:53):** Yeah.

**Bruno Rocha (36:54):** Yes.

**Chad Hage (36:57):** And so again, you know, think of when I said the microsite or the white paper, I keep going back to that audience that I mentioned earlier, those individuals that have to make a decision. Do I give, you know, my next team of 100, 200, 1,000 developers, engineers, etc., am I giving them Ferraris when I give them Anthropic Claude Code, or am I giving them, you know, Ford Fiestas and it just happens to have a Ferrari badge on it, you know.

**Kapil Srikanth (37:27):** Ish.

**Bruno Rocha (37:30):** Mhm.

**Kapil Srikanth (37:31):** Yeah.

**Chad Hage (37:33):** No offense to any, you know, but I mean, that's what I'm talking about in terms of integration, these features, you know, if you're going to write a check.

**Bruno Rocha (37:33):** Okay.

**Chad Hage (37:45):** All right, guys, I gotta jump on another call, but... Hopefully, this was helpful.

**Ross Volenec (37:53):** Yep, absolutely. Thank you, Chad. Thank you.

**Bruno Rocha (37:53):** All right, no worries. Thank you, sir. Have a good one.

**Kapil Srikanth (37:54):** Yeah, yeah.

**Chad Hage (37:55):** All right, thank you. All right, bye-bye.

**Kapil Srikanth (37:56):** Thank you, thank you. Have a great weekend.

**Ross Volenec (37:57):** Have a good one.

**Joseph Bressani (37:59):** Take care.

*Kapil Srikanth stopped transcription*