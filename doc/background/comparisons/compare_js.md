# Comparing Panel and JavaScript

Whenever you evaluate any Python framework for building JavaScript/HTML/CSS web apps, it's important to consider the baseline alternative of just writing JavaScript, HTML, and CSS directly. Writing JS/HTML/CSS will give you full control over all aspects of the resulting applications, allowing you to tailor the complete look and feel and behavior to match even the most precise requirements. Moreover, JS/HTML/CSS apps can be deployed on any web server without needing any special consideration to running a Python process, which makes deployment and scaling much more straightforward.

Given those advantages, here's why you would want to use a high-level Python framework instead:

- Does the app depend on sources of data or other tools already available in Python? If so it will normally be much easier to build in a Python framework like Panel.

- Do the people building the app normally work in Python? If so, they are likely to be much more productive in Python, both directly for writing the app's code and indirectly by being able to use all of their usual support tools and infrastructure (and from not having to learn JS).

- Do the people who know what the app should do normally work in Python? If so, with a Python framework like Panel they can express precisely what they mean for the app to do, without having to formalize their requirements, throw the specification over the wall to some external person or group, and go through a lengthy back and forth to iron out all the details.

- Are the functional requirements for the app unclear or evolving? If so, Panel is a good choice, because Panel app code is very lightweight and high level, expressing complex functionality with a few lines of modular, recomposable code. Adding new components, rearranging them, trying out different options, etc. are all very quick to do in Panel, making even complete reorganizations quick to do. A native JS/HTML/CSS app of similar user-level complexity will generally require vastly more code and more complex code, making it much more difficult to adapt to high-level needs as they become clearer or evolve over time.

- Is the purpose and configuration of the app largely already fixed, with feedback and iteration focusing on styling, details of user interactions, etc.? If so a native JS/HTML/CSS app may be more appropriate, to allow all those details to be adjusted arbitrarily. That said, building a Panel app as a prototype is still a great way to nail down the overall functionality quickly, ready for such adjustments before sharing with a large audience, and you may find that Panel's behavior is already customizable enough even for that case.

- In short, what's more important, the look and feel, precise positioning, styling, etc., or what the app _does_? If the latter, Panel lets you focus on that.
