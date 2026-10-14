# CIS4910 - Group 3 - Project MS2 - Senior Project Meeting (Week 4)

- **Date:** September 18, 2026
- **Time:** 8:37 PM (UTC) / 4:37 PM (EDT)
- **Duration:** 55m 47s
- **Attendees:** Chad Hage (Sponsor), Ross Volenec, Bruno Rocha, Kapil Srikanth, Joseph Bressani

---

## Executive Summary & Key Takeaways

* **Individual Progress Updates:**
  * **Ross:** Presented a high-level architecture diagram and design document for an AutoGen + LiteLLM + OpenTelemetry orchestration layer that spins up ephemeral Docker containers (without API tokens) to test agent-generated code and output JSON telemetry.
  * **Bruno:** Demoed an initial prototype UI for the microsite (built with Claude Sonnet) featuring project overview pages and a live prompt comparison interface.
  * **Kapil:** Demoed a local web interface designed to log user prompts alongside structured test cases and specifications, plus a baseline To-Do app.
  * **Joseph:** Refined the evaluation metrics and testing plan in the GitHub updates, shifting the cost metric toward token efficiency to account for free-tier usage.
* **Key Sponsor Feedback — Team Alignment & "Forming, Storming, Norming":**
  * Chad observed that while each team member is making strong individual progress, the team is currently **diverging unintentionally** (working in separate silos and seeing each other's work for the first time during the Friday call).
  * Chad emphasized that **80% of the capstone's value** is learning how to move quickly from *Forming* and *Storming* into true *Norming* as a cohesive engineering team.
* **Continuous Communication vs. "Stopping to Communicate":**
  * Chad shared his philosophy on **Continuous Communication** (inspired by Lean Six Sigma): status meetings where people stop working just to find out what others are doing are a form of waste. Instead, work should organically radiate status (via Discord, GitHub Issues, or in-person syncs) so the team is aligned *before* Friday's meeting, allowing the Friday call to focus on unblocking and iterating.
* **Architectural & Technical Clarifications:**
  * **GitHub Pages vs. App Hosting:** The GitHub Pages microsite is strictly for showcasing documentation, findings, and telemetry dashboards. The "guinea pig" To-Do application and any Docker containers do *not* need to run inside GitHub Pages—they can be hosted on Azure (e.g., Azure Static Web Apps or Azure Container Apps).
  * **Handling Secrets in Containers:** Ross raised the question of how to push PRs or handle credentials without exposing secrets inside an ephemeral Docker sandbox. Chad noted that evaluating how each ecosystem natively solves this (e.g., Azure Key Vault, GitHub Secrets, OIDC) and where other pipelines fall short is a core research finding of the project.
  * **Rapid Prototyping (80/20 Rule):** Avoid generating mountains of LLM design text ("AI slop") before testing; build working prototypes early to identify the 20% that works (referencing Tom Chi's Google Glass TED Talk on rapid prototyping).

---

## Cleaned Transcript

**Ross Volenec (0:03):** Okay, this is probably pretty hard to see, so I'm going to zoom in here.

**Chad Hage (0:09):** I can zoom in. I'm good.

**Ross Volenec (0:11):** Anyway, the general idea is that we're going to have our localhost as the orchestration layer. That will handle the prompting. We give the prompt to the orchestration layer, and then we will spin up an ephemeral Docker container. The Docker container will not get any API tokens or anything; it will just get the agent's results and try to merge it in. The testing will take place in the Docker container. If there are any blockers, we've got human-in-the-loop, so it will come back and ask us and take as many turns as it needs to. 

We're looking at AutoGen for handling the agents themselves, and we're going to be using LiteLLM with OpenTelemetry to create a JSON file that will be our output. We merge that back into the GitHub archive, CI/CD does its checks as a referee, and then boom, we've got the metrics. We can push those to the microsite and create some actual usable evidence as far as the performance goes. And Joseph came up with the formulation for exactly how we're going to score these runs. If you see any points of failure here, I'd love some feedback.

**Chad Hage (1:51):** I mean, this is a diagram on a piece of paper. I like where you're going with that.

**Ross Volenec (1:56):** I do have more details, but yes, this is just the high-level look.

**Chad Hage (1:59):** Right. Until I see the actual results of a test that you've conducted—does it explain what you're going to try to do to compile and make sense of the data? Yeah, but we need to see the data go through it and come out the other end to make a decision. As far as the diagram is concerned, I think it's clear. It's very eloquent. I want to see the data and I want to see the tests.

**Ross Volenec (2:51):** I agree. And if I had provided this to you sooner as a blocker, then I could have probably gotten started on this. I'm going to spend some time over the weekend to get the prototype out the door and hopefully have something ready by Monday.

**Chad Hage (3:02):** Look, guys, I want you to understand that when you put something in place, I'm going to look at it. If this is the deliverable, I'm saying it's good, right? But on its own, it's just a proposed diagram. If you have more, then show me what you got.

**Ross Volenec (3:30):** This is not all I have. I spent some time creating a document that I could hand to an agent and potentially have it knocked out within a few hours to really lock in the design.

**Chad Hage (4:36):** Okay, so I'm a little confused by this. What is the code in here supposed to do? Why is this not an actual Python file that you're putting in somewhere and running?

**Ross Volenec (4:55):** I probably don't have a very effective software engineering workflow—I don't have industry experience. So my workflow is I've just been brainstorming with Gemini, and then I have it create a design document, and I'm going to give that to another agent to actually implement it.

**Chad Hage (4:59):** Okay, and that's fine. I appreciate the transparency, guys. I need to know where I can add value by telling you: look, an LLM is a language model. It's designed to spit out words. When you tell an LLM, "Hey, go create more words," it's a field day—that's what it was designed to do. I'm sure you've heard the term "AI slop." I don't want that for you guys, and I'm not calling this AI slop...

**Ross Volenec (5:52):** This *is* AI slop, but I hope it's at least useful enough that I can create a prototype that we can start working on.

**Chad Hage (5:53):** Aha, so now we're getting somewhere, right? I want that prototype. Don't wait until you have a mountain of slop to figure out that you had mostly slop. Always remember, there's an 80/20 rule: 80% of what you're going to get is probably unnecessary because that's how LLMs make money—they burn tokens. If there's 20% that's worth holding on to here, what is it? The sooner you can get to it, the sooner you'll iterate and go to the next iteration. 

I like the direction you're going, and I want you to continue to go in that direction, but I want the empirical evidence to speak louder than the optics of just scrolling through a document. Remember, you don't always get to have the voiceover. What happens if your peers had to talk to what you are showing us? Also, if you had shown me this on Tuesday, I would have told you by Wednesday what I just said right now. Imagine that feedback coming to you on a Monday or Tuesday and what the impact would be on our conversation today on Friday.

**Ross Volenec (8:11):** Yes. Just for clarity, my perspective on these meetings was that this would be our point of contact and I didn't want to bother you throughout the week.

**Chad Hage (8:39):** You have access to me. If you're over-dipping or double-dipping in the access that I've given you, believe me, you will know. If you choose to make this a meeting of "Here's where I've been stuck for the last four days," then you reap what you sow. I respect your accomplishments getting to this stage of your collegiate career—you got to senior year in capstone based on making good decisions. Continue to do that.

**Bruno Rocha (9:35):** Understood. All right, I will go ahead and share my screen. I know we said no slop, but this is going to be full slop—this is just a baseline as to what the vision is for the microsite.

**Chad Hage (9:50):** That's fine. Ross took one for the team by going first, so now the others owe him!

**Bruno Rocha (10:02):** This is just a visual of what it might look like in the future. On the main microsite, we have a project overview and deliverables—that's more for optics for the other fellow students in the class of what our actual project is. Then the actual real thing: the live comparison. Fully transparent, it does not work yet because I don't have API keys yet—that's something we're working on this weekend. Basically, the idea is that the user enters a prompt, say, *"Create a Tic-Tac-Toe game in Python."* From there, it will run the comparison between all four harnesses, and eventually do a live comparison of token costs, accessibility, readability, and the metrics that Joseph mentioned, so the user can see the outcome across all four.

**Chad Hage (11:39):** Question: Kapil and Ross, is this the first time you guys are seeing this, or have you seen this before?

**Bruno Rocha (11:58):** I showed them yesterday. I've been very stressed out this past week, so Tuesday and Wednesday I didn't do much, and then worked on it Thursday to Friday.

**Chad Hage (12:01):** Believe me, I expect you guys to get even more stressed out near exams and finals, so I get it. I just needed to know if this was something Bruno came up with on his own and this is the first time the team is seeing it, versus an actual decision you guys took as a group. 

I put a link in the chat to a TED Talk video by **Tom Chi** (former head of Google X / Moonshot, behind Waymo and Google Glass). It's about engineering and rapid prototyping—reaching the things that are going to work early, and finding the things that are not going to work even earlier. It offers a lot of insight into the experimentation phase, which is where you guys are right now. 

I like the direction, and I like that you're driving AI rather than letting AI drive you. Out of curiosity, which model did you use to generate this site? GPT-5.6?

**Bruno Rocha (15:29):** No, it was Sonnet 5. I'm an Anthropic fanboy.

**Chad Hage (15:34):** Oh, okay! It looks a lot like what GPT is trained on. And just to explain why I was a little harsher on Ross earlier: in my advisory role at Microsoft, I deliver documents to customers as a product, so in a professional services capstone, Ross's design doc would be a product in its own right. This is an engineering capstone, so we need working prototypes. 

Before we move forward, remember the four things I look for in updates:
1. Progress
2. Decisions made (and how you got there)
3. Blockers
4. Next actions

Are there any blockers right now for Ross or Bruno?

**Bruno Rocha (18:22):** On my end, the main blocker I'm thinking of is finding a digestible way to present all the information at once on the site—showing Claude's output, OpenAI's output, etc., in an easy way so that during a live demo for our peers who haven't done the project, it isn't overly information-heavy.

**Chad Hage (19:12):** That's very valid. Have AI present some visualization suggestions first before you land on one. I also used to really like a JavaScript visualization library called **D3.js** (`d3js.org`), which has a lot of cool interactive components and widgets you can check out. Ross, did you have a question?

**Ross Volenec (22:43):** When it comes to integrating the pipeline with the website, as far as I'm aware, there's no way to interact with Docker directly from a GitHub Pages microsite. My current plan was just to run the tools and have the telemetry go to the website as a dashboard, but as far as a live demonstration goes, do you have any ideas about how we could integrate that?

**Chad Hage (23:27):** A couple of things: the microsite on GitHub Pages is simply to hold and showcase your findings. GitHub Pages hosts static web apps (HTML/CSS/JS or React/Angular running in the browser). You can't run server-side containers directly inside GitHub Pages, though a static web app can call an external HTTP endpoint if you handle CORS. 

However, I want to dispel the impression that your "guinea pig" application (the To-Do app) or your Docker containers need to live on GitHub Pages. If you host the guinea pig app on Azure in an Azure Static Web App or in a Docker container, that's totally cool. Your GitHub Pages microsite is just the dashboard/document that describes what you created and shows the telemetry and how you iterated on it. 

Also, if you're thinking about standing up Docker containers, now is a good time to set up your Azure student subscriptions early, because some educational benefits have a validation/review period.

**Ross Volenec (27:52):** That reminds me, I used my personal GitHub to get approved on the repo. Could I get my school account invited? I'll put it in the chat.

**Chad Hage (28:02):** Yes, put it in the chat and I'll make sure to invite it. All right, who wants to go next?

**Kapil Srikanth (29:01):** I can go next because my work was tied in a bit with Bruno's. Bruno shared the website he made, and I adjusted it a little bit and made another local web interface in VS Code (and uploaded it to our GitHub repo) to log the test cases and specifications that tie into the user's prompt—like adding priority tags or returning an error if a requirement title exceeds a certain length.

**Chad Hage (30:46):** Okay, so this is the To-Do list guinea pig app, and your pipeline is going to iterate on this app—adding features, removing features, fixing bugs.

**Kapil Srikanth (31:07):** Right, to make the user experience as streamlined as possible. I finished this late last night because of work for other classes, so this is probably the first time the rest of the team is seeing it in detail. Going forward, as soon as I do something, I'll put it in the shared updates on GitHub so we can get your feedback as soon as possible. I don't have any blockers to report right now.

**Chad Hage (32:48):** I appreciate the openness. Have you guys ever heard about the different stages of a team—**Forming, Storming, and Norming**?
* **Forming:** The honeymoon phase during the first couple of weeks ("Nice to meet you, we're on the same team").
* **Storming:** Where things feel a little uncomfortable because you're figuring out each other's dynamics while your grade is on the line.
* **Norming:** Where the team hits its stride and works together seamlessly.

We don't want to stay in Storming, but recognizing which stage you're in helps you understand what's going on. Joseph, you're up next—what has been completed, what do you have planned, and any blockers?

**Joseph Bressani (35:10):** I put most of my stuff in the weekly update. I created the metrics and testing plan, expanding on what you told me last week. I changed "cost" to "tokens" since we're focusing on free tiers, and added a couple more test cases. 

As for blockers: I'm a little shaky on how our website, AI models, and API keys are actually going to interact with the codebase we're testing against, and how we're going to incorporate the security issues we need to test.

**Ross Volenec (36:39):** If I may take an attempt to answer that: this is my fault because I haven't done a good job of explaining it to the team yet. We'll keep a sample default codebase (like the To-Do app) within our repository, and optionally accept an external GitHub repo. It will clone to the local drive and spin up an ephemeral Docker container to expose only that specific repo to the AI agent so it can't see anything else on the hard drive. 

That leads to a question I have for you, Chad: once we get the result from the AI agent and have the pull request, do we push it from inside the ephemeral Docker container, or retrieve that locally and push it? Because pushing from inside the Docker container would require exposing login credentials within the sandbox, which feels like a bad idea.

**Chad Hage (38:09):** Hold that question for a moment, because here's what I see after today's conversation: I see four super bright individuals who are currently going in somewhat different directions. You each have a good concept of what you're trying to do, but this is the moment where I need you guys to get on the same page. Consider this the last week where you can claim you didn't know you were on different pages. 

I'm a big proponent of *divergence before convergence*—if you intentionally agree to diverge to explore possibilities and then converge, that's fantastic. But right now, you're trying to converge and ending up diverging by coincidence because of communication gaps. You guys are on a Discord server, right? Why aren't these problems being presented and solved in Discord before Friday's call?

**Bruno Rocha (41:47):** I think the problems just aren't being presented properly enough in the Discord to begin with.

**Chad Hage (42:00):** Right. We need to solve the communication problem amongst the team first. 

Now, back to Ross's technical question about securing certificates and secrets: what you've exposed is one of the exact issues that surfaces when you do a project like this. Should you use **Azure Key Vault** (which has a free tier on Azure)? Should you use **GitHub Secrets**? There are a few different ways to solve this problem, and what I'm looking forward to seeing is how each pipeline handles it. With GitHub Copilot in the Microsoft ecosystem, using Azure Key Vault or GitHub Secrets is a walk in the park. When you try the same thing on Claude Code, AWS, or Meta Muse, does it play nice with Azure Key Vault or GitHub Secrets, or is there a big hole in that pipeline? That side-by-side comparison is one of the core findings I want you guys to uncover.

**Ross Volenec (47:09):** Yes—so you're more interested in getting us to work together, our design process, and the outputs of that process than the specific design choices themselves.

**Chad Hage (47:22):** Yes! You hit the nail on the head. Because this project is going to end in a few weeks, and you're going to land on a professional team that wants to know you can figure out how to be a productive team member. 80% of this project is how fast you guys can reach true **Norming**. Once you do that, the remaining 20% becomes easy.

**Ross Volenec (48:22):** One last question: you mentioned that you've written papers on continuous communication. Do you have anything you'd be happy to share with us, or any tips?

**Chad Hage (48:40):** I'll dig up the paper and share it, though it's about 12 years old. The core idea came from Lean Six Sigma and lean software development: **stopping to communicate versus continuous communication**. Think about an aircraft pilot—imagine if the pilot had to stop flying the plane in order to communicate with the tower. That would be a disaster. Yet in software development, we've created a model where in order to communicate, we have to stop working and hold status meetings or stand-ups. From a Lean perspective, pausing to communicate is waste. **Continuous communication** is where everything you do organically radiates what you're working on and where you're at, without having to stop. 

I challenge you guys to find a way—whether it's Discord, GitHub Issues, or meeting up at the Marshall Center—to keep continuous communication flowing so you're aligned throughout the week.

**Kapil Srikanth (53:48):** Going forward, we'll all be a lot more specific when discussing our issues to make sure we form the product properly. I'd like to think this upcoming week will be our most productive week by far.

**Chad Hage (55:09):** Excellent. Continuous communication, guys—keep it flowing. Take care, and have a good weekend!