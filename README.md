# socra
![logo](https://socra.com/images/og/socra_1400x700.png)


🧬 Let your codebase improve itself with AI, from the command line.

[![Release Notes](https://img.shields.io/github/v/release/socra/socra.svg?style=flat-square)](https://github.com/socra/socra-python/releases)
[![PyPI - License](https://img.shields.io/pypi/l/socra?style=flat-square)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/socra?style=flat-square)](https://pypistats.org/packages/socra)
[![GitHub star chart](https://img.shields.io/github/stars/socra/socra-python?style=flat-square)](https://star-history.com/#socra/socra-python)
[![Open Issues](https://img.shields.io/github/issues-raw/socra/socra-python?style=flat-square)](https://github.com/socra/socra-python/issues)
[![X](https://img.shields.io/twitter/url/https/twitter.com/socra_ai.svg?style=social&label=Follow%20%40socra_ai)](https://twitter.com/socra_ai)


## Installation
First, install the library:
```bash
pip install socra
```

Next, be sure to set an `OPENAI_API_KEY` environment variable. `socra` currently uses OpenAI for LLM requests, but aim to add multiple providers in the near future. See [OpenAI's docs](https://platform.openai.com/docs/quickstart) if you don't yet have an API key.


## 🤔 What is socra?

**socra** is an open-source system for enabling rapid code mutation and improvement on any codebase from the command line using large language models (LLMs) and other AI application techniques.

Unlike other LLM-based approaches to software development, `socra` improves your code without the need to use a web-app, install a new editor, or use any other unergonomic interface. Code is mutated directly from the command line, freeing you up to use your favorite tools for the human part of software development.

`socra` aims to be an essential command line tool for you, as useful as your favorite version control system or native terminal commands.

## Motivation

### Biological Mutations

In biology, genetic [mutation](https://en.wikipedia.org/wiki/Mutation) is the ultimate source of all genetic variation, and is the substrate on which evolution and natural selection act. Most mutations are relatively small in proportion to the overall genome of an organism, and may be beneficial, neutral, or harmful to the organism in a particular environment.

Selection pressure provides a probabilistic feedback mechanism for mutations providing some benefit to an organizm to persist across time. That is, over many iterations, genetic mutations providing some benefit to an organism in a particular environment tend to persist.

Through this process, genetic lineages form and give rise to earth's numerous species, each with its own genetic code and adaptations.

### Current State of Software

There is **quite a lot of code** existing in the world, much of it quickly becoming dead weight and unuseful. Engineers typically love building new things, but rarely enjoy maintaining software for decades.

Some interesting stats about code repos:
- Top open-source projects can have over [10,000 distinct contributors](https://octoverse.github.com/2022/state-of-open-source).
- GitHub reported having more than [420 million repositories in 2023](https://en.wikipedia.org/wiki/GitHub).
- Many code repositories have 1 million or more lines of code.

### socra as an Intelligent Replicator

With this biological and market backdrop, let's draw some comparisons to software code.

Until now, helpful mutations to code generally fall under the following categories:

1. **Human**: (hopefully) intelligent human actors aiming to improve or add some functionality to a project they have a vested interest in, using any number of tools to ease the development process (text editors, extensions, conversational chat bots)
2. **Deterministic Bot**: bots built to deterministically make some mutation. For example, a bot to automatically update project dependencies, format and lint code, run some tests, etc.

There also exist other ways to mutate code, like changing characters at random, but these types of changes are rarely productive and usually introduce errors and break code.

This project aims to introduce the following **third** method for generating helpful code mutations:

3. **socra**: random (or targeted) intelligent code mutations introduced entirely by AI and verified only by humans.


## Usage

From your favorite terminal, make sure `socra` is installed:
```bash
socra --version
```

To quickly improve any file or directory


## Concepts

### Node
A `node` represents an object in a hierarchy. `node` can have exactly one parent and zero or more children. Some node types can have children, and others can't (leaf nodes).

### Action
An `action` is a functional unit with defined input and output parameters. Actions can implement regular functions, use AI, call other actions, or any combination thereof. In this way, actions are incredibly flexible functional units.

### Capability
Capabilities strictly define one object's capabilities on another. For example, an agent may have differing capabilities based on its model type, the node it is interacting with, and other criteria. Capabilities start with `can_`.

### API
An API is a set of rules that connect one application to another. In `socra`, an API is typically used to connect `nodes`, `actions`, and `capabilities` together internally.

### Executor
Executors use APIs and an objective to work toward a goal.

For example, an agent `executor` can interact with a File API for a codebase in order to achieve an objective, perform some action, or instantiate another executor (one more suitable for the task at hand, for example)

