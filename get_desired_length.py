def find_constructions(text, N):
    words = text.split()
    constructions = []
    for i in range(len(words)):
        construction = words[i]
        j = i + 1
        while j < len(words) and len(construction) + len(words[j]) + 1 <= N:
            construction += ' ' + words[j]
            j += 1
        if len(construction) == N:
            constructions.append(construction)
    return constructions

text = """Hi there,
I'm Becky Kane, editor of Doist's blog Ambition & Balance. I wanted to reach out with a warm welcome to the newsletter. I'm really glad you're here!
In recent weeks, we've seen a big uptick in traffic with people seeking guidance on how to transition to remote work. If that describes you, I wanted to pull out some of our best articles to get started with:
For team leaders looking to manage & support newly remote employees:
 Doist's CEO Amir explains what asynchronous communication is and why he believes it's the key to successful remote teamwork
 Doist's Head of Marketing Brenna gives actionable advice for managers on how to build a strong foundation of trust remotely
 We cover all of the remote collaboration tools we rely on and how we use each to keep 73 team members in over 25 countries moving in the same direction
For anyone struggling to stay productive & sane while working from home:
 5 habits for crafting the perfect remote workday – Full disclosure: If the "perfect" work from home day exists, I've never experienced it. But getting these 5 habits down certainly got me closer.
 Why it's so hard to prove your value at work and how to do it anyway – When you work from home, how does your boss know you're doing a good job? How do you know, for that matter? Remote work veteran Jeremey DuVall walks you through how to identify and communicate the value you're creating at work even when it's hard to measure.
 Having trouble staying focused at home? Reador at least skim) The Complete Guide to Deep Work , then follow the example of folks like Elon Musk and Jack Dorsey and start time blocking your day . These two related concepts are productivity game-changers.
On a final note, remote work is challenging even under the best circumstances. It's completely normal to feel less than optimally productive right now. Be kind and patient with yourself and your coworkers. We'll all get through this together.
If you have any questions or topics you'd like to see covered on Ambition & Balance, don't hesitate to reply to this email. Rest assured, all replies to becky@doist.com will go to a real inbox checked by a real humanme).
Thanks and see you in the next newsletter,
Becky and the Doist team
============================================================
 A newsletter from the Doist team
Creating tools for a more fulfilling way to work and live.
 Todoist
| Twist
You’re receiving this email because you subscribed to Ambition & Balance the Todoist Blog).
 Subscription preferences"""
N = 10
result = find_constructions(text, N)
print(result)
