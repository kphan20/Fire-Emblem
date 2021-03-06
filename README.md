# Fire-Emblem

This is my foray into game development in Python. It is a passion project in which I am attempting to combine the three GBA Fire Emblem games into one. As I began planning the project, I realized that there was a lot to be done. I had to:

- Learn Python to a greater degree and choose a game development framework to learn (pyglet)
- Create a map editor
- Find/make art resources
- Gather the statistics of the units that I want to include in the game
- Learn networking for multiplayer feature

However, I saw this as a great learning opportunity, allowing me to get familiarity with:

- Planning a project from beginning to end
  - Bit of a learning curve here - I started with various TODO comments and am moving towards Azure DevOps to do pseudo scrum planning (really just a way for me to keep track of features/tasks)
- General game development and architectures
- Designing a web scraper and storing the data in an appropriate manner
- Interfacing with MongoDB
- Socket programming

While this project is very much still a work in progress, and many hitches have been encountered (inconsistency of scraped data sources, debugging visual glitches, expanding project scope, and more), but here is what has been currently developed:

- The beginnings of various game objects (characters, tiles, weapons, etc.)
- A recursive algorithm that calculates the available squares a unit can move
- A pathfinding algorithm that calculates how the character would navigate to a square and draws arrows denoting the path
- Drawing of the map based on documents stored in MongoDB
- A moving camera when panning across the map
- Scraping of FE8 character information and storage as JSON
  - I am considering other alternatives for this, such as a local database
- The browser map editor (which allows for saving maps to MongoDB)
  - The repo for this project is [here](https://github.com/kphan20/Fire-Emblem-Map-Maker).

I would like to develop the game to what I originally envisioned - a multiplayer PvP game with a drafting phase that allows players to pick characters/weapons from the GBA games.
