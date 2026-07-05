"""
faq_data.py
25 curated FAQs on Generative AI & Large Language Models.
Written from scratch for the StudyDesk FAQ helper (same general domain as
the brief, original wording throughout).
"""

FAQS = [
    (
        "What is a large language model?",
        "A large language model, or LLM, is a neural network trained on huge amounts "
        "of text so it can predict, understand, and produce human-like language. "
        "GPT-4, Claude, Gemini, and LLaMA are all examples. They're built on the "
        "Transformer architecture and learn mainly by guessing the next word over "
        "and over across billions of examples."
    ),
    (
        "What is generative AI?",
        "Generative AI describes systems that produce new content — text, images, "
        "audio, code, or video — instead of just labelling or analysing what already "
        "exists. Chatbots built on LLMs, image tools like Stable Diffusion, and AI "
        "music generators are all part of this category."
    ),
    (
        "What is the Transformer architecture?",
        "The Transformer is the neural network design behind almost every modern LLM. "
        "Introduced in 2017, it swaps out older recurrent processing for a mechanism "
        "called self-attention, which lets the model look at an entire sequence at "
        "once instead of one word at a time. That parallelism is a big part of why "
        "training got so much faster."
    ),
    (
        "How does the attention mechanism work?",
        "Attention lets a model decide how much each word in a sentence should influence "
        "its understanding of every other word. Each token gets turned into a Query, "
        "Key, and Value; comparing Queries against Keys produces attention scores, "
        "which then weight the Values. Multi-head attention just runs several of these "
        "comparisons in parallel, each catching a different kind of relationship."
    ),
    (
        "What is hallucination in an LLM?",
        "Hallucination is when a model states something false, invented, or nonsensical "
        "while sounding completely confident about it. It happens because the model is "
        "optimised to produce fluent, plausible-sounding text, not to check facts "
        "against reality. Grounding techniques like RAG, along with RLHF, are common "
        "ways teams try to cut down on it."
    ),
    (
        "What is RAG or retrieval-augmented generation?",
        "RAG is a setup where, before answering, the model first pulls relevant "
        "passages from an external knowledge source — documents, a database, a "
        "search index — and includes them in its prompt. This keeps answers grounded "
        "in real, current information and reduces the need to retrain the model every "
        "time facts change."
    ),
    (
        "What does fine-tuning an LLM mean?",
        "Fine-tuning takes a model that's already been pre-trained and trains it "
        "further on a smaller, focused dataset so it performs better at a specific job "
        "— say, legal document review or customer support. Common approaches include "
        "full fine-tuning, LoRA, QLoRA, and instruction fine-tuning, each trading off "
        "cost against how much the model's behaviour actually shifts."
    ),
    (
        "What is prompt engineering?",
        "Prompt engineering is the skill of wording your input so an LLM gives you the "
        "output you actually want. It covers things like zero-shot prompts (just ask), "
        "few-shot prompts (show a couple of examples first), chain-of-thought prompts "
        "(ask it to reason step by step), and ReAct-style prompts that mix reasoning "
        "with taking actions."
    ),
    (
        "What is RLHF or reinforcement learning from human feedback?",
        "RLHF trains a model using human judgement rather than pure statistics. People "
        "rank several model responses from best to worst, that ranking trains a reward "
        "model, and the LLM is then nudged (typically via a method called PPO) to "
        "produce outputs the reward model scores highly. It's a major part of how "
        "assistants like Claude and ChatGPT get aligned with what people actually want."
    ),
    (
        "What are embeddings in AI?",
        "An embedding is a list of numbers — a vector — that represents a word, "
        "sentence, or document in a way that captures its meaning. Items with similar "
        "meaning end up close together in that vector space. Beyond powering the "
        "model internally, embeddings are also used on their own for semantic search "
        "and for retrieval in RAG systems."
    ),
    (
        "What's the difference between GPT and BERT?",
        "GPT is decoder-only and trained to predict the next word in a sequence, which "
        "makes it naturally suited to generating text. BERT is encoder-only and trained "
        "by hiding random words and having the model guess them from context in both "
        "directions, which makes it stronger at understanding tasks like classification "
        "rather than open-ended generation."
    ),
    (
        "What is tokenisation in LLMs?",
        "Tokenisation is the step where raw text gets chopped into smaller pieces — "
        "tokens — before the model can process it. A token might be a whole word, part "
        "of a word, or a single character, depending on the scheme. Most current LLMs "
        "rely on Byte-Pair Encoding or SentencePiece, and the number of tokens a piece "
        "of text uses directly affects both context-window space and API cost."
    ),
    (
        "What is a context window?",
        "The context window is the maximum amount of text, measured in tokens, an LLM "
        "can take in and work with during a single exchange — prompt and response "
        "combined. GPT-4 tops out around 128K tokens and Claude 3 goes up to 200K, "
        "which is enough headroom to hand a model an entire book or codebase at once."
    ),
    (
        "What does temperature control in LLM generation?",
        "Temperature is a setting that controls how random an LLM's word choices are. "
        "At temperature 0, it always picks the single most likely next token, giving "
        "consistent, repeatable output. Turn it up toward 0.8–1.0 and the model takes "
        "more risks, which can make writing feel more creative but also less reliable. "
        "Top-p sampling does a related job in a slightly different way."
    ),
    (
        "What is a vector database used for in AI?",
        "A vector database is built to store and quickly search through huge numbers "
        "of embedding vectors using approximate nearest-neighbour lookups. It's the "
        "backbone of most RAG pipelines: documents get embedded and stored ahead of "
        "time, and at query time the question's embedding is compared against that "
        "store to pull back the closest matches. Pinecone, Weaviate, Chroma, and FAISS "
        "are well-known examples."
    ),
    (
        "What's the difference between zero-shot and few-shot learning?",
        "Zero-shot means asking a model to handle a task with no examples at all, "
        "relying purely on what it already learned during pre-training. Few-shot means "
        "slipping a handful of example input-output pairs into the prompt first, which "
        "usually sharpens accuracy on niche tasks without changing a single model "
        "weight."
    ),
    (
        "What are AI agents or LLM agents?",
        "An LLM agent uses the language model as a reasoning core that can plan multi-step "
        "tasks and actually take actions — calling APIs, running code, searching the "
        "web, reading and writing files — checking its own progress until it reaches "
        "a goal. LangChain, AutoGPT, CrewAI, and Claude's own tool-use features are all "
        "frameworks built around this pattern."
    ),
    (
        "What is LoRA or low-rank adaptation?",
        "LoRA is a way to fine-tune a model cheaply by freezing almost all of its "
        "original weights and only training small added matrices inserted into each "
        "layer. That cuts the memory and compute needed dramatically while still "
        "getting results close to a full fine-tune. QLoRA takes it further by also "
        "compressing the base model down to 4-bit precision."
    ),
    (
        "What's the difference between open-source and closed-source LLMs?",
        "Closed-source models — GPT-4, Claude, Gemini — are only reachable through an "
        "API; you can't inspect or change their weights. Open-source models — LLaMA 3, "
        "Mistral, Falcon, Gemma — publish their weights, so anyone can run them "
        "locally, fine-tune them, or study how they work. The performance gap between "
        "the two camps has been shrinking fast."
    ),
    (
        "What is multimodal AI?",
        "A multimodal model can take in and produce more than one kind of data in the "
        "same system — text alongside images, audio, or video. GPT-4o, Claude 3, and "
        "Gemini Ultra all work this way, typically using a separate encoder per "
        "modality and then merging those representations before the language part "
        "generates a response."
    ),
    (
        "What's the difference between training and inference in LLMs?",
        "Training is the expensive, one-time (or occasional) process of adjusting a "
        "model's weights using gradient descent over huge datasets. Inference is just "
        "using that already-trained model to answer a real query — far cheaper and "
        "fast enough to happen live. Most of the day-to-day engineering work in "
        "deployed LLM products is about squeezing inference cost and latency down."
    ),
    (
        "What is quantisation in LLMs?",
        "Quantisation shrinks a model's weights from higher-precision formats like "
        "32-bit or 16-bit floats down to smaller ones like 8-bit integers, or even "
        "4-bit with formats like GGUF. That cuts the model's memory footprint and "
        "speeds up inference, usually at only a small cost to output quality. Tools "
        "like llama.cpp and bitsandbytes make this practical on ordinary consumer "
        "hardware."
    ),
    (
        "What is chain-of-thought prompting?",
        "Chain-of-thought prompting asks the model to work through its reasoning step "
        "by step before landing on a final answer, rather than jumping straight to a "
        "conclusion. It noticeably helps with multi-step problems in maths, logic, and "
        "code. A zero-shot version just adds a phrase like 'let's think step by step'; "
        "a few-shot version shows worked examples first."
    ),
    (
        "What is a system prompt in LLMs?",
        "A system prompt is an instruction set placed ahead of the actual conversation "
        "that shapes how the model behaves — its tone, persona, and any rules it must "
        "follow. The end user never sees it directly, but it quietly governs every "
        "reply that follows. Companies use system prompts to turn a general-purpose "
        "model into something tailored, like a support assistant for a specific "
        "product."
    ),
    (
        "What is Constitutional AI?",
        "Constitutional AI is Anthropic's approach to training models that are "
        "helpful, harmless, and honest without depending purely on human labelling for "
        "every judgement call. Instead, a written set of principles — the "
        "'constitution' — guides the model as it critiques and rewrites its own draft "
        "answers, which scales up the supervision behind alignment. It's part of how "
        "the Claude models are trained."
    ),
]