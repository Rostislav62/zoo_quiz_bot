# Two-Step Quiz Bot (TSQ)

## Overview

### Problem
Moscow Zoo needs guardians for its animals but lacks interactive ways to engage potential supporters.

### Solution
A Telegram bot with a two-step quiz that identifies a user's totem animal from 40 zoo inhabitants, supports Russian and English, collects feedback and statistics, and promotes the guardianship program.

### Impact
Increases interest in the guardianship program by entertaining and engaging users through an interactive experience.

## About the Project
TSQ is a Telegram bot developed for Moscow Zoo to determine a user's totem animal via a two-stage quiz:
1. **Mini-Quiz** (5 questions): Identifies the category (Mammals, Birds, Reptiles, Amphibians).
2. **Main Quiz** (20 questions): Selects a unique totem animal with 800 custom responses.

This project showcases my skills in building AI agents, from database management to Telegram API integration.

## Features
- **Unique Responses**: 800 humorous and factual answers for 20 questions across 40 animals.
- **Interactivity**: End-of-quiz buttons ("Restart", "Share", "Guardianship", "Feedback") and admin commands (`/stats`, `/feedback`).
- **Database**: SQLite (`zoo_quiz.db`) stores questions, answers, and feedback.
- **Localization**: Supports Russian and English languages.

## How It Works
1. User starts with `/start`, selects a language, and enters their name.
2. Completes the mini-quiz to determine a category.
3. Answers 20 questions in the main quiz.
4. Receives their totem animal with a photo, link, and interactive buttons.

## Technologies
- **Python 3.10**: Core language.
- **aiogram 2.21**: Telegram Bot API framework.
- **SQLite**: Data storage.
- **JSON**: Format for initial data migration.
- **Git**: Version control.

## Installation
1. Clone the `TSQ` branch:
   ```bash
   git clone -b TSQ https://github.com/Rostislav62/zoo_quiz_bot.git
   cd zoo_quiz_bot
2. Set up a virtual environment: 
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
4. Configure the bot token in config.py:
   BOT_TOKEN = "your_bot_token_here"
5. Initialize the database:
   ```bash
   python3 db_setup.py
   python3 db_migrate.py
   python3 setup_mini_quiz_db.py
   python3 update_animals_from_site.py
   python3 update_categories.py
   python3 update_questions.py
   python3 add_main_quiz_answers.py
6. Launch the bot:
    ```bash
   python3 main.py

## Usage
    - Start the bot with /start.
    - Choose a language (RU/EN), enter your name, and complete the quiz.
    - Use buttons to restart, share results, learn about guardianship, or leave feedback.
    - Admins can view stats (/stats) and feedback (/feedback).

## Demo
    Watch a short demo video:  (to be updated).

## Author 
    Rostislav — AI agent developer. 
    This bot is part of my portfolio, demonstrating expertise in intelligent bot creation.

## License
    MIT License