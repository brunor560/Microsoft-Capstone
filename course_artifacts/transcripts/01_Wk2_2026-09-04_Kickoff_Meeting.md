# CIS4910 - Group 3 - Project MS2 - Senior Project Meeting (Kickoff)

- **Date:** September 4, 2026, 7:43 PM
- **Duration:** 34m 32s
- **Participants:** 
  - **Sponsors (Microsoft):** Chad Hage, Bradley Lawrence
  - **Student Team:** Bruno Rocha, Ross Volenec, Kapil Srikanth, Joseph Bressani

---

## Executive Summary & Key Takeaways

### 1. Project Scope & Core Objective
- **End-to-End Developer Loop:** The goal is to evaluate how existing AI software development ecosystems/harnesses handle the full development loop—from "napkin/whiteboard/Voice of the Customer (VOC)" requirements decomposition to specs, architecture alteration, testing, production deployment, and telemetry feedback ("it's a loop, not a runway").
- **Focus on Orchestration over Architecture:** The evaluation is not testing the students' ability to design software architecture, nor is it testing the raw intelligence of foundation models on complex code. Instead, it assesses the **pipeline setup, harness orchestration, token efficiency, and security principles** (e.g., preventing AI slop, protecting developer identity/OIDCs, keeping secrets/tokens out of config or wiki files).
- **Common Codebase ("Guinea Pig"):** Use a simple, rudimentary application (e.g., a To-Do app or basic shopping cart) that exercises a UI, an API, and a persistence backend. Compare how different ecosystems (Microsoft/GitHub Copilot, Google, Meta, Anthropic/Claude Code, etc.) handle this common codebase.

### 2. Deliverables & Definition of Ready / Done
- **Evidence-Based Management:** Opinions must be backed by empirical evidence, reproducible test cases, acceptance signals, and telemetry/cost data.
- **Core Deliverables:**
  1. **Working Pipeline & Demo:** A repeatable, traceable demonstration showing a demand item dropping into the loop and appearing in a live/test environment (1 through 10 deliverables shown A-to-Z by the end of the semester).
  2. **Comparison Matrix:** A consolidated evaluation comparing the different pipelines/harnesses.
  3. **White Paper / Documentation:** A "North Star" write-up explaining findings and methodology (similar to Microsoft Learn/Docs).
- **Guardrails & Security:** Must strictly adhere to USF and FERPA guidelines. Rigorous monitoring is active on the provided Azure tenant; out-of-scope workloads will be flagged and shut down immediately.

### 3. Logistics, Access & Cadence
- **Cadence:** Weekly touchpoints on **Fridays at 3:30 PM** via Microsoft Teams.
- **Communication:** Use Microsoft Teams (`@Chad` or `@Brad`) as the primary communication channel. Provide a brief executive summary pre-read in the GitHub communication repo/chat prior to Friday calls. Escalate technical/Azure/LLM blockers early.
- **Environment Setup:** Students must use their `@usf.edu` emails/GitHub accounts to accept invites to the communication repository and the Microsoft Azure tenant/subscription. Students should also activate their free GitHub Student Developer Pack licenses.

---

## Full Meeting Transcript

*Kapil Srikanth started transcription*

**Chad Hage (0:03):** ...organize yourself as a team to optimize your productivity. Available to give you some thoughts, some input, what we've seen work in the past, what we've seen fail in the past. So, you know, we've been involved in both scenarios, so feel free to use that as you feel it's necessary for your success. Regarding the scope, I know this one is a little interesting. So what we are seeing right now is that there are different offerings or maybe even ecosystems out there when it comes to software development. Software development is one of the more mature scenarios when it comes to AI and large language models. In fact, we were both Brad and I were on an internal call recently, and you know, my mind was blown when I started realizing, and they were talking about how up until now, everything we've seen done with AI has been pretty much done with a language model. And can you imagine when you start seeing a science model, you know, as your option to combine with a language model? And so the productivity gains that are, you know, up ahead are going to be exponential, even to what we are seeing today. And so this is why it makes, you know, it's interesting for me. I think this is one of those topics that makes sense. What I'd like to see is how do the existing loops for developers, you know, if you were to take the, you know, the ones that are out there that are promoting themselves or positioning themselves as that end-to-end loop from what I call, you know, call it napkin, whiteboard, voice of the customer, whatever it is, wherever the requirement or the demand is uncovered, you know, all the way until it reaches production and back feeding into the actual creating the feedback loop, right? And so that's the loop I'm looking for. I do have some examples that I'm happy to show you of what I've looked at if you need those. But that in a nutshell is the scope. So going from like, hey, I get a some kind of a demand item, let's call it a backlog item, a story, etc. How does it get decomposed? How does it enter the, you know, the specs? How do the specs of that working repo treat that demand item? And then how does the Architecture get altered, not necessarily by you as an engineer, but you're essentially orchestrating the LLM, the, you know, the model and the loop with the existing harnesses, and then in the process, what I'm looking for is to understand which loop is treating secured development according to principles, which ones are essentially leaving gaps, you know, kind of like try to note down what is the empirical evidence, what are you seeing? That's the high level. Any questions, any comments? I mean, I know you've read the document and it was appealing enough for you guys to say, hey, this is something I want to work on. But is that helping bring more clarity to what we're trying to do?

**Bruno Rocha (3:23):** Definitely does, yeah, 100 percent.

**Chad Hage (3:25):** Okay. In terms of... I'm very much evidence-based management. If there is, I value your opinion, but I want the evidence. I will value your opinion significantly more or exponentially more when it's backed by evidence. So, when you have, you know, an observation, if you can bring along that assertion, that test case, that data that was produced that says, this is what's going on, and here's how I know that, because you have the actual test data to back it, then it becomes a matter of evaluating whether we conducted the test correctly, whether we set up the harness correctly versus, you know, a matter of opinion, you know, a comparison. Okay. So definitely high emphasis on evidence-based outputs, acceptance signals, that loop itself, you know, a lot of times I see engineers and individuals think primarily of the path out to the world, but ignore the return path coming back into the development loop. Okay? And so I want you guys to think about, it's a loop, it's not a runway. So runways usually help us take off, but you have to think about the landing as well. And creating that, you know, that virtuous cycle, that loop is what I'm looking for. Does that help explain what I mean by expectations on deliverables?

**Ross Volenec (5:00):** Yes. I had one question about that. I'm not super familiar with software development in industry or with AI in that capacity. I'm here to learn about that kind of stuff. Are there any good specific metrics that we should be looking at when we're evaluating the efficacy of...

**Chad Hage (5:13):** Excellent.

**Ross Volenec (5:19):** ...AI-based software development.

**Chad Hage (5:22):** Yeah, and so that's a great question. So, especially if you've, I mean, when you're doing software development for commercial software, whether you're doing, you know, development on, you know, a driver for a hardware, you know, at the end of the day, today, more than ever, we're seeing everything being software-defined or software-based. So, even if you're working on a chip or if you're working on a, you know, something that is typically in the past was going to end up being burned on a chip, it is going more towards the route of, hey, can I make this more of an abstraction layer and then let the software, you know, kind of run with the use case on top of that. So to be more specific and to zoom in a little bit more, what I'm looking for, and I gave some examples in the submission form, you know, for example, we know that because it's a Microsoft sponsored project, so right off the bat, you know that GitHub Copilot, all the GitHub assets, especially since you're students, they're available to you under the student license for free. So please do take advantage of that. From an Azure perspective, I will provide an area in Azure as a subscription with a resource group for you to target whatever your loop that you end up creating ends up producing. I'll give you some guidance on what choices to make to manage, you know, the budget and so on and so forth. But this is less about, you know, can you architect something that's going to, you know, run optimally? I want to see more attention paid: Are we able to secure the, you know, the identity of the developer? Are we able to efficiently take a demand item and see it show up in the actual test environment or an environment because it went through the loop and the actual models and the skills that you have in place picked it up, understood that this is a demand item, it generated the necessary test cases, it gave you the test coverage, or your specs set up in a way that give you the ability to produce software through your loop in an efficient and effective manner versus did you design the software correctly? Now, as a software developer, as you get more experience and become more seasoned, you'll be able to look at an architecture and say, yeah, this is architected correctly versus that's not architected correctly. This is not an architectural, you know, assessment in any way. I'm not looking for you to come up with a good architecture. I'm looking for you to come up with a good orchestration because let's face it, the LLM itself has access to virtually every architecture under the sun. But, you know, am I going to expect you guys to say, ah, it came up with architecture A and it should have gone with architecture B? Less of that, if you do, that's great. I would really be, you know, that would be a good, a very impressive way to, you know, call that out. But more or less, what I want to say is that your setup, your loop, did not blow away, you know, a million tokens trying to do, you know, some kind of a loop that was even unnecessary because that tells me that the way you've set up your specs, the way you've set up your harness, the way you've set up your environment is where the deficiency is. So I'm looking more for the optimal setup of the pipeline rather than, you know, judge you or gauge you on your architectural problems. Does that make sense?

**Ross Volenec (9:03):** Yes, thank you.

**Chad Hage (9:04):** And for that matter, that's why in the actual form, the submission form, I left it up to you guys. You want to pick up a to-do as your, you know, common repo or common code base that you want to put through that loop and show how the Microsoft loop compares to the Google one, for example, and compares to the, you know, Facebook one, to the Meta one, et cetera. That's up to you. Pick a very rudimentary, you know, code base. Don't go, you know, crazy trying to, you know, recreate Fortnite or anything. If that's what you guys want to do, then, you know, have at it. But I mean, just a simple to-do, you know, a little bit more than hello world, but nothing too elaborate in terms of your common code base. So, very early on, I'd like to see that set up, and I'd like you to, you know, be able to explain why you chose the code base you chose, but it's not intended to be crippling. I do want it to be, you know, the ability to exercise the different components of, you know, a UI, an API, and a backend for persistence, perhaps, you know, those are the criteria that we're looking for versus just something that is super static, for example. Okay. Questions, comments? Okay, I'll take the silence as we're on the same page. So we talked about the deliverables a little bit, a working pipeline. There is a paper component. I mean, I think one of the things that a lot of people misunderstand is that Microsoft is in the business of putting out papers because our audience, our customers expect us to provide that North Star. So believe it or not, you know, if you want to call it a white paper, whatever you want to call it, but having that write-up, having that explanation as to what you identified, that is a very commonly shipped Microsoft product. In fact, Microsoft Learn and Microsoft Docs, those two products, there's teams that work on nothing but producing those docs. And they treat it very much like a software development lifecycle, independent of the actual products that those documents describe. A comparison matrix is something that I'm definitely interested in, you know, seeing how this is, how you arrive at that, whether you guys, you know, take each one of these, you know, pipelines and tackle it together, swarm it, or you decide to divide and conquer. This is going to tell me how you are able to bring back that knowledge and consolidate it. And so that's what we're looking for in here. And then of course, you know, it would be really interesting to see how you demoed, you know, it would be really awesome to see you demo at the end of the year, even if it's canned or video or whatever. But, you know, being able to say, you know, here's how a prompt goes from, or here's how I drop something in the, you know, in the voice of the customer bucket, and it shows up in the live site, and here's a telemetry that, you know, was generated by it. Make sense?

**Bruno Rocha (12:11):** Yes, Sir.

**Ross Volenec (12:12):** Yes.

**Chad Hage (12:13):** All right, let's talk about the definition of ready. So I want to make sure the problem is clear. I want to make sure the outcomes and acceptance criteria are testable, that you guys can go and understand, you know, how to reach a pass-fail on everything we're discussing here. If after today you still feel like, hey, I don't know how to actually reach a definitive...

**Kapil Srikanth (12:13):** Yeah.

**Chad Hage (12:32):** ...pass or fail. Meaning if I think about this on Friday, I'm coming up with one outcome. If I think about it on Saturday or Monday, I'm coming up with a different outcome. Come back and let's talk about it because I want to make sure that we have a clear understanding of the acceptance criteria that we've talked about. The same for inputs, dependencies, limits, you know, whatever is known, you know, if you're still unclear about those after today, please ask and please let me know. We'll make sure that those are all in place. Some of this is going to happen via e-mail. Some of it is going to happen via Teams. We're going to discuss a little later how we're going to do all that. Security, privacy, and cost are considered. So again, everything you do is going to be, you know, respect the guidelines from USF, FERPA, you know, any information you use needs to adhere to the same rigor that you would see with any project. If you do anything that is out of bounds or outside the lines of what's acceptable of this project, it is going to get flagged very quickly. We always talk about how, you know, there's rigorous monitoring. And what happens is when you do that, the workload will get shut down, your project will be, you know, put on hold, and that's going to impact your grade. So you're going to have access to some really powerful stuff. Use it wisely, you know, stay within the lines of, you know, the guardrails of what this project is about and everything will be fine. If you feel tempted to try something that is out of the scope, just know that there will be consequences. Our evaluation method, I think, you know, it's really more about how much of that evidence are you capturing, you know, throughout the project, I'll give you feedback. If I see gaps, if I see that, you know, you're setting up your pipeline in a way that is suboptimal, you know, that's going to be part of the back and forth that we'll do throughout. But that's going to be, you know, my evaluation method. In terms of what Dr. Christensen or Scott, for that matter, your professors, they have their evaluation methods and I'm sure they've covered those with you. And then the owner of iteration of scope are set. You know, at some point, you guys are going to get together and figure out who's going to own what. And I'm just expecting you guys to communicate that to me so that we know how to proceed from here. Any comments, questions, concerns about this?

**Bruno Rocha (15:02):** No, sir.

**Chad Hage (15:04):** All right, let's talk about definition of done. So we want a working demo of what you put together. So if you pick 3 pipelines, 4 pipelines, that's up to you. But they need to have an actual working demo where you drop a demand item and it shows up in an environment somewhere and you can show the traceability through the different portions of the loop. What did the LLM do? How did it react? What was the effect of the specs that you put in place? What was the effect of the skills that you chose to activate? How did you optimize between, you know, the different skills and the MCP sources that you tied into? All of that is part of what I'm expecting in that working artifact. Testable, again, if it's just take my word for it, it's going to be probably, you know, looked at unfavorably. The best way to address that is have test scenario, have test data, make the evidence back the statement. Evidence like cost are captured. Again, you know, telemetry, logging, all of those, you'll see that the actual LLMs are really good at proposing those. You just need to kind of fine tune and know how to get the LLM to do this type of architecture, right? And so I'll work with you. I'll provide the mentorship, the guidance to help you figure this out. But yeah, we want evidence. As you can see, the word evidence shows up in this paper quite a bit. Again, how are you protecting the developers' security? Are you protecting the project security? How are you protecting the security of the data? Does one pipeline have an inherent compromise? Does another pipeline do a better job at, you know, handling OIDCs, for example? That's the kind of stuff we're looking for here. The last thing you want to do is have your PAT or your tokens end up in, you know, some kind of a wiki file or some kind of a, you know, a config file on the server, right? Because that is definitely something that you wouldn't do as a developer, hopefully. And so you wouldn't want your LLM to do that. Documentation, again, that white paper is what I'm looking for in terms of documentation. It should be part of your final demo. And, you know, we want to be able to look at that demo week in and week out, ideally. But let's talk about the, you know, I think we've covered, you know, what the actual working agreement is: the evidence over opinion, you know, keeping the decisions and demos reproducible, you know, especially these days when everything is driven from a repo, everything is continuously integrated and continuously tested. I do want you to escalate blockers early in case you're stuck, reach out to Brad or myself and let us know. So, any thoughts, questions, comments?

**Bruno Rocha (18:06):** I know you said you were going to mention it later, but how often do you want us to communicate with you in terms of like check-ins and if you want to do maybe like a weekly Teams? I know you're a busy person, so I don't know how, based on your workload, like how much you want us to communicate with you in that kind of aspect.

**Chad Hage (18:16):** Yeah. Communicate as often as you need to. Messages on Teams will be looked at, especially if you do the `@` name. So put `@Chad` or `@Brad`, that'll get our attention. We both get hundreds if not thousands of messages daily and hundreds or thousands of emails daily. And that's not even accounting what we get from our friends and family, right? So just use the technology for what it's meant, `@` my name or `@` Brad's name, put it in Teams. I think that's going to be your best bet to get our attention. I do favor a weekly cadence. You know, we're just so happened we're flowing through this and we're on the cadence topic. Right. So what I like usually is a weekly touch point. We treat the weekly in a similar manner to how most people do a daily stand up, but we're not going to meet daily and do this. So I expect you guys to have a high frequency interactions, whether that's daily for you or, you know, multiple times a day or once every other day, I'll leave that up to you. Okay? What we'll be able to do is provide feedback. If we see evidence of friction or deceleration, we'll point that out. And then we'll make ourselves available to assist you on addressing those, because we've seen most scenarios that occur in a development team. Brad and I have seen it. I think it would be very difficult to uncover a scenario that we haven't seen yet. In terms of blockers, you know, especially when it comes to the underlying technology, Azure related blockers, LLM related blockers, bring those to my attention earlier. I can either change the requirement or I can help you unblock the technical blocker itself. I personally appreciate a brief pre-read if you put that, especially now with, you know, if you set up your agents, they can produce that for you, right? So make it executive summary level, put it in the chat, you know, or prepare it somewhere so we can at least glance at it before we jump on the call. That way I may be able to come prepared with a solution or help you unblock something before, instead of waiting for it for a 3:30 on a Friday. Okay. And we make sure that the decisions that you're coming up with are recorded continuously, so that way you have a record of what we do, you know, what we're discussing and it helps you for down the road. Did that answer your question?

**Bruno Rocha (20:52):** Yes, sir. Perfect. Thank you.

**Chad Hage (20:54):** So I'm comfortable with 3:30 on Friday afternoons. If you want to push it back to 4, that's fine by me. I'll leave it up to you guys. But sometime in the afternoon is always going to be better than the morning for now. Most of my customers are looking for morning slots, so afternoon slots tend to be more open. If it has to be in the morning, we'll find a spot that will align. But yeah, just does anyone object to having the same time on Fridays?

**Ross Volenec (21:26):** Friday works for me.

**Bruno Rocha (21:27):** No, I'm good.

**Kapil Srikanth (21:28):** That works for me.

**Chad Hage (21:28):** Yeah. All right, so I'm going down. So I did actually, so guys, take your time when you hop on this microsite, put the actual repo out there with a link, make the decisions that you want to make and document them in here, and then put them in the chat for Brad and I, and then we will...

**Joseph Bressani (21:29):** Yeah, it works for me.

**Chad Hage (21:48):** ...go with your decisions. If there's something that is TBD, I'm going to look at it. But the floor is yours. This is your project. We're here to support you. We want to know what decisions are made, what blockers are stopping you from going forward. Use this tool if you want to, you know, get some assistance to figure out how to actually get a kickoff going, but other than that, what do you have in terms of questions for either Brad or I?

**Kapil Srikanth (22:18):** Yeah, I had a question about, so you mentioned earlier that you would give like access to like Azure or something. Do you know when that'll be? Like, can you give an idea?

**Chad Hage (22:28):** Yes. So one of the things that I wanted to do is to confirm that you're able to join the repo because I invited you to the repo. I think one of you was already using the USF ID. As soon as you have your USF IDs, you'll have access to the Azure subscription. It's already in the repo, you just have to accept the invite.

**Ross Volenec (23:00):** Yeah, I use my personal GitHub account, so I'll have to set that up.

**Kapil Srikanth (23:01):** OK.

**Chad Hage (23:05):** Yeah, I debated whether I should ask you guys to use the, you know, the personal one or go with the USF one. Ultimately, I decided to go with the USF one. It's appropriate. At some point, if you guys want to invite your personal one, you know, that's up to you. I would not mind if you fork this. I mean, this repo is useless. This is not the repo I'm talking about the actual work that you guys will be producing. This is just meant to be, you know, in lieu of a PowerPoint. That's all.

**Kapil Srikanth (23:32):** Mhm.

**Chad Hage (23:33):** It's a slightly more intelligent PowerPoint slide because it allows me, it allows you guys to, you know, enter some data and save it and export it and etc. That's all.

**Kapil Srikanth (23:44):** Okay, so we would need to create like a GitHub with our student e-mail, is that if I'm understanding that correctly?

**Chad Hage (23:51):** Yeah. As a matter of fact, I think where is the repo... I think it's in here, could have a link to the repo here somewhere. Oh, down at the bottom, sorry. I was right there as a matter of fact. Open repository. Yeah, so this is the repo, and if you come in here, it's going to tell you this is a communication repo only. You know, you can go back to the view that I had, but any information that I have in terms of what you need will be in here, and there will be an actual Azure folder that I'll release that I'm going to commit, and it's going to have everything you need in terms of access to Azure.

**Kapil Srikanth (24:44):** Okay, thank you.

**Chad Hage (24:45):** And in terms of your access as invitees, you're already collaborators. Use passkey... Ohh, is it because I'm using my camera? One sec.

**Bruno Rocha (25:06):** I believe so, yeah.

**Chad Hage (25:08):** Yeah.

**Kapil Srikanth (25:08):** Yeah.

**Chad Hage (25:10):** Only one camera at a time. There we go. Yeah. Oh, I see you guys already did it. Excellent. So after the call, I'll do the commit and you'll have all the necessary information for accessing that Azure. And you're going to get invites to those e-mail addresses to join the tenant first.

**Kapil Srikanth (25:34):** Yeah. Officially.

**Chad Hage (25:42):** ...and then you'll be able to access the subscription.

**Kapil Srikanth (25:47):** Okay.

**Chad Hage (25:50):** Awesome.

**Bruno Rocha (25:53):** One more question, sorry. I know you said for the AI models themselves, it doesn't necessarily matter which ones you use. Obviously, we already kind of discussed which ones we're going to use. Do you necessarily have a preference for which tier model we use? So would you rather use the free version, the most expensive version, or is that kind of up to us to decide?

**Joseph Bressani (25:53):** Ohh.

**Chad Hage (25:54):** Sure, go ahead. That's literally the crux of this project, right? So when you run it with, I mean, let me put it this way. When you let the harness decide, you know, what are the trade-offs versus saying, hey, when I chose Opus 5, right, this was the benefit.

**Bruno Rocha (26:29):** Right.

**Chad Hage (26:30):** Right, and does Opus 5 with GitHub Copilot yield better output than say, you know, Opus 5 on Claude Code, right? So again, you guys are going to take this. I'm confident that you're going to spend about, you know, whatever amount of time you need to spend and figure out how you divide and conquer. So step one is I want to see how you're going to divide and conquer this. The second part is now I want to, if you're going to demonstrate it, I want to see it backed by empirical evidence, which is some kind of a test.

**Bruno Rocha (26:52):** Hey.

**Chad Hage (27:06):** And it has to be a repeatable task versus, you know, I sat behind my, you know, machine and I clicked on things. Did I answer your question?

**Bruno Rocha (27:17):** Makes sense. Thank you. Yes, Sir.

**Ross Volenec (27:17):** So, that would look like we structured prompts in a way, so like we got that one test set where the prompt is tailored to say, like, spend, use the maximum amount of reasoning on this, and then we have another that says, use the most cost effective amount of reasoning on this or something like that, just to determine.

**Joseph Bressani (27:17):** Ohh.

**Chad Hage (27:33):** Yeah.

**Ross Volenec (27:36):** And then we...

**Chad Hage (27:37):** I mean, the reason why I chose a low intensity, you know, application like a to-do or whatever, right, is that the amount of reasoning to figure out the code itself should be minimal. The amount of reasoning that you need to figure out if you're compromising the loop is where the actual rubber meets the road. Does that make sense? So the developer experience is where I'm looking for your ability to distinguish. Is it going to struggle trying to reason through how to architect a to-do app? Absolutely not, right? But what we know is that behind the scene, while you see a fancy looking to-do app, it's slop unless you set up the specs correctly, unless you protect, you know, data privacy correctly, unless you, you know, manage the developer credentials correctly. That's what I'm looking for. So I'm not looking for a fancy application. I'm looking for something that even if you develop like a to-do list or something that is low intensity, like a shopping cart, whatever it may be, something very, very bread and butter these days. What you don't want to end up shipping is something that ends up being the equivalent of AI slop because it looks pretty, but behind the scene, it's garbage. You don't want the substance to be of what's behind the scene, even if the user experience is decent, minimal, but decent. You know, I'm not impressed by good looking websites and web apps. I'm looking for it to pass a code review and a pull request. Does that make sense?

**Ross Volenec (29:22):** Yes.

**Kapil Srikanth (29:23):** Yeah.

**Chad Hage (29:26):** Excellent.

**Joseph Bressani (29:26):** I do have another question, if you don't mind me asking.

**Chad Hage (29:31):** Yeah, yeah.

**Joseph Bressani (29:32):** So there's 10 deliverables that were in the original document. Is there any different priorities would you like to focus on or is all the demos like equal in weight?

**Chad Hage (29:44):** Yeah, so I mean, I think once you start orchestrating, right, you're going to see that there's going to be a natural order, right? You know, you can't, you're going to see the structure is going to dictate which ones are going to emerge first. But the final demo, it should be able to say, here's 1 through 10, right? Throughout the actual project, if you decide, hey, we're gonna, I decided based on what I'm looking at here, I'm gonna start on, you know, for example, you know, something like around the pull request reviews. I want to showcase that on week one. I'm okay with that, right? Because based on your research, that's what, or based on your examination or analysis of the problem, that's where you think is the best place to start. That's great. That's fine. At the end, I want to see the full A-to-Z.

**Joseph Bressani (30:40):** Okay, thank you.

**Chad Hage (30:40):** Think of it like how they make movies in Hollywood. Sometimes they shoot like, you know, the last scene first, right? But you'll always see the same movie flow the same way, and it looks, you know, put together well, even if the acting or the plot sucks. Is that helpful?

**Joseph Bressani (31:04):** Yeah, we just we could target certain areas first and work overall to complete the overall goal.

**Chad Hage (31:14):** Okay. I like the sound of that. Brad, what do you have to offer to the students on this one? Anything you want to add? I know you're under the weather, so I'm trying to take it easy on you.

**Bradley Lawrence (31:28):** Yeah, you know, just one of the things when it comes to your team working together: make sure nobody goes off in a silo, and you really want to ensure that your team is collaborating well and communicating well, so that you don't run into any issues when you need to integrate, you know, everyone's work together and stuff like that. And yeah, that's mainly it. I think you covered everything already, Chad.

**Chad Hage (32:00):** Excellent.

**Bradley Lawrence (32:00):** I just always like to highlight, you know, that communication among the team.

**Chad Hage (32:05):** Yeah, and we'll point that out if we see that, but yeah, that's a good callout. Alright, so I look forward to seeing you guys set up this as a reoccurring.

**Bruno Rocha (32:21):** Yes, we'll do that right after this meeting.

**Joseph Bressani (32:22):** Yes.

**Kapil Srikanth (32:22):** Yeah.

**Chad Hage (32:23):** All right, excellent. And then what I'll do is I'll push the last commit that I made and that's going to add some additional resources to the repo. If you're not following it, follow it, so then you'll get the notification when it gets updated. But I just want to be clear, this is not where I expect you guys to commit your work. This is simply a communication repo. From here on out, I expect you guys to, you know, create the repo where you'll... or maybe you'll end up with multiple repos. I'm really excited to see what you're gonna come up with.

**Bruno Rocha (33:00):** And would you want us to add you to, we already created a second repo, would you want us to add you to that as well, or keep that just the four of us, or how do you want us to go about that?

**Chad Hage (33:09):** I'm more interested in what your... So I don't want to go and do code review and pull request reviews. I want you to show me how your pipeline is doing that. So the only time I'll ask you to invite me to the repo is that if I'm seeing reasons to second guess what your setup is saying.

**Bruno Rocha (33:18):** Right.

**Kapil Srikanth (33:19):** Okay.

**Bruno Rocha (33:19):** Right, OK. Sounds good.

**Kapil Srikanth (33:34):** Alright, perfect.

**Chad Hage (33:35):** Does that make sense?

**Joseph Bressani (33:35):** Yeah.

**Bruno Rocha (33:36):** Yes, sir.

**Chad Hage (33:38):** All right. Great question though. I like that. I like the way you're thinking. Shows that we're on the same wavelength. All right, gentlemen. Enjoy the long weekend. If you have any questions that come up after today's call, feel free to put them in the chat. Again, I keep a close eye on Teams. E-mail is, you know, second to Teams only, but feel free to reach out if you have any questions.

**Bruno Rocha (33:50):** Right.

**Chad Hage (34:08):** ...and we'll do what we can to help you unblock.

**Bruno Rocha (34:12):** Sounds good.

**Kapil Srikanth (34:12):** All right, yep, sounds great. Brad, thank you for your time.

**Joseph Bressani (34:14):** Yeah, thank you.

**Chad Hage (34:14):** All right. Thank you for your time.

**Bruno Rocha (34:14):** Thank you for your time, sir. My pleasure. Thank you. Bye.

**Chad Hage (34:16):** Take care. All right, bye-bye.

**Joseph Bressani (34:22):** That was something.

**Bruno Rocha (34:22):** All right, fire.

**Kapil Srikanth (34:22):** Hey, good work, boys.

**Ross Volenec (34:22):** Well...

*Kapil Srikanth stopped transcription*