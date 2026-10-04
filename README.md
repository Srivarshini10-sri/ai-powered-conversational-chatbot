# 🤖 AI-Powered Conversational Chatbot with Real-Time Web Search

An AI-powered conversational chatbot that combines a **local Large Language Model (Llama 3.2)** with **real-time web search** to provide useful and up-to-date responses.

The chatbot runs locally using **Ollama**, provides an interactive interface using **Gradio**, and uses **DuckDuckGo search** to retrieve current information from the web.

---

## 📌 Project Overview

Traditional AI chatbots that use only local language models may provide outdated information because they do not have direct access to current web data.

This project solves this problem by combining:

- Local AI-based conversation
- Real-time web search
- Current web information
- Natural-language processing
- Conversational history

The chatbot searches the web when required, provides the retrieved information to the local Llama 3.2 model, and generates a relevant response for the user.

---

## 🎯 Problem Statement

Traditional AI chatbots powered by local language models may provide useful responses, but they often lack access to real-time and updated information.

As a result, they may provide outdated or incomplete answers for questions related to current news, elections, prices, events, and other rapidly changing information.

Therefore, there is a need for an AI-powered conversational chatbot that can combine a local language model with real-time web search to provide more relevant, current, and reliable responses to users.

---

## 💡 Proposed Solution

The proposed system combines a locally running AI language model with a real-time web search mechanism.

When the user asks a question:

1. The chatbot receives the user's query.
2. The system performs a web search.
3. Relevant web results are collected.
4. The search information is provided to the Llama 3.2 model.
5. Llama 3.2 processes the information.
6. The chatbot generates a natural-language response.
7. Relevant web sources are displayed to the user.

This approach allows the chatbot to provide both **AI-generated conversational responses** and **current web-based information**.

---

## ✨ Key Features

- 💬 User-friendly conversational chatbot interface
- 🧠 Natural-language conversation
- 🌐 Real-time web search
- 🔎 Current information retrieval
- 🤖 Local AI model processing
- 🦙 Llama 3.2 language model
- ⚡ Ollama-based local model execution
- 🔐 No paid AI API key required
- 📝 Conversation history during the session
- 🔗 Displays relevant web sources
- 🎯 Accuracy-focused responses
- ⚠️ Error handling for web search and AI model failures
- 💻 Runs locally on the user's computer

---

## 🏗️ System Architecture

```text
                 ┌─────────────────────┐
                 │        USER         │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  CHATBOT INTERFACE  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    WEB SEARCH       │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  WEB INFORMATION    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │      AI MODEL       │
                 │     Llama 3.2       │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ GENERATED RESPONSE  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │        USER         │
                 └─────────────────────┘
