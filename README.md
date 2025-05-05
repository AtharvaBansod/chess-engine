## ♟️ Chess AI Bot with Real-Time Multiplayer (Research-Oriented )

A research-driven Python-based Chess AI leveraging **NegaMax algorithm with Alpha-Beta pruning**, custom **state management**, and **real-time multiplayer gameplay** powered by **Socket.IO** and **Redis Pub/Sub**. Designed for scalability, performance, and extensibility, this system forms the backbone of a modern chess engine with real-time interaction and AI intelligence.

---

### Table of Contents

* [Overview](#overview)
* [Key Features](#key-features)
* [Architecture](#architecture)
* [AI Design (NegaMax + Alpha-Beta)](#ai-design-negamax--alpha-beta)
* [Multiplayer Infrastructure](#multiplayer-infrastructure)
* [State Management](#state-management)
* [Technologies Used](#technologies-used)
* [Setup Instructions](#setup-instructions)
* [Future Enhancements](#future-enhancements)
* [Research Goals](#research-goals)

---

## Overview

This project is an advanced chess platform built with a focus on:

* **Algorithmic Intelligence** via game-tree search and pruning
* **Scalable Communication** via event-driven architecture
* **Efficient State Handling** using custom serialization and move tracking

The goal is not just to build a working chess app, but to explore **AI design patterns**, **real-time distributed systems**, and **domain-specific decision modeling**.

---

## Key Features

* ♟️ **AI Bot with NegaMax & Alpha-Beta pruning** (configurable depth)
* 🌐 **Real-Time Multiplayer** using Socket.IO and Redis pub-sub model
* 🧩 **Custom GameState Engine** built from scratch (no python-chess dependency)
* 🔄 **Deterministic Move Generation** and in-memory board logic
* 🧠 **Support for Move Hints**, best-move evaluation, and board state scoring
* 🔧 **Modular & Decoupled Components** for AI, logic, and network transport

---

## Architecture

```txt
Client (React) <-- Socket.IO --> Flask Backend
                                    |
                             Redis Pub/Sub
                                    |
                        GameState & AI Logic (Python)
```

* **Socket.IO** enables low-latency real-time messaging.
* **Redis** acts as a message broker for multiplayer session coordination.
* **GameState** handles move validation, turn tracking, and board rendering.

---

## AI Design (NegaMax + Alpha-Beta)

The core of the AI lies in a **recursive NegaMax search tree** with:

* **Position Evaluation** function using material balance and positional weights
* **Depth-limited Search** with configurable difficulty levels
* **Alpha-Beta Pruning** for optimized search space

```python
def negaMax(board, depth, alpha, beta, isMaximizing):
    if depth == 0 or game_over(board):
        return evaluate(board)
    for move in generate_moves(board):
        apply(move)
        score = -negaMax(new_board, depth-1, -beta, -alpha, not isMaximizing)
        undo(move)
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return alpha
```

---

## Multiplayer Infrastructure

* **Socket.IO (Server-side)** listens for events like `move`, `join`, `resign`
* **Redis Pub/Sub** enables real-time session updates across multiple server instances
* **Room Management**: Each game is encapsulated in a socket room, backed by Redis topic

---

## State Management

* **GameState Class** encapsulates board, player turns, history, and check/checkmate detection
* **Move Class** abstracts movement, captures, promotions, and notation
* **Stateless Frontend → Smart Backend**: All game logic resides in backend for integrity

```python
game_state.makeMove(move)
valid_moves = game_state.getValidMoves()
```

---

## Technologies Used

| Layer               | Technology                         |
| ------------------- | ---------------------------------- |
| AI Engine           | Python, NegaMax + Alpha-Beta       |
| Multiplayer         | Socket.IO, Redis                   |
| Backend Framework   | Flask (can be upgraded to FastAPI) |
| State Logic         | Pure Python (no external engine)   |
| Frontend (Optional) | React + Socket.IO Client           |

---


## Future Enhancements

* [ ] Openings book and Transposition Tables
* [ ] MCTS or Reinforcement Learning-based engine variant
* [ ] Support for PGN/FEN formats
* [ ] Spectator mode and match history

---

## Research Goals

* Investigate the efficiency of NegaMax in sparse versus dense game states.
* Evaluate distributed state synchronization latency using Redis pub/sub.
* Study real-time decision-making in adversarial zero-sum environments.
* Develop plug-in AI models for comparative analysis (Minimax, MCTS, NeuralNet, etc.)

---

## References

* *Artificial Intelligence: A Modern Approach* – Russell & Norvig
* AlphaZero Research by DeepMind
* Redis Pub/Sub Architecture
* Socket.IO and Event-based Network Systems

---

