import numpy as np
#Vectors of Attack Effectiveness against types
Normal = np.array((1,1,1,1,1,1,1,1,1,1,1,1,0.5,0,1,1,0.5,1))
Fire = np.array((1,0.5,0.5,1,2,2,1,1,1,1,1,2,0.5,1,0.5,1,2,1))
Water = np.array((1,2,0.5,1,0.5,1,1,1,2,1,1,1,2,1,0.5,1,1,1))
Electric = np.array((1,1,2,0.5,0.5,1,1,1,0,2,1,1,1,1,0.5,1,1,1))
Grass = np.array((1,0.5,2,1,0.5,1,1,0.5,2,0.5,1,0.5,2,1,0.5,1,0.5,1))
Ice = np.array((1,0.5,0.5,1,2,0.5,1,1,2,2,1,1,1,1,2,1,0.5,1))
Fighting = np.array((2,1,1,1,1,2,1,0.5,1,0.5,0.5,0.5,2,0,1,2,2,0.5))
Poison = np.array((1,1,1,1,2,1,1,0.5,0.5,1,1,1,0.5,0.5,1,1,0,2))
Ground = np.array((1,2,1,2,0.5,1,1,2,1,0,1,0.5,2,1,1,1,2,1))
Flying = np.array((1,1,1,0.5,2,1,2,1,1,1,1,2,0.5,1,1,1,0.5,1))
Psychic = np.array((1,1,1,1,1,1,2,2,1,1,0.5,1,1,1,1,0,0.5,1))
Bug = np.array((1,0.5,1,1,2,1,0.5,0.5,1,0.5,2,1,1,0.5,1,2,0.5,0.5))
Rock = np.array((1,2,1,1,1,2,0.5,1,0.5,2,1,2,1,1,1,1,0.5,1))
Ghost = np.array((0,1,1,1,1,1,1,1,1,1,2,1,1,2,1,0.5,1,1))
Dragon = np.array((1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,0.5,0))
Dark = np.array((1,1,1,1,1,1,0.5,1,1,1,2,1,1,2,1,0.5,1,0.5))
Steel = np.array((1,0.5,0.5,0.5,1,2,1,1,1,1,1,1,2,1,1,1,0.5,2))
Fairy = np.array((1,0.5,1,1,1,1,2,0.5,1,1,1,1,1,1,2,2,0.5,1))


typeOrder = ['normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting', 'poison', 'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy']
typeChart = np.stack([Normal, Fire, Water, Electric, Grass, Ice, Fighting, Poison, Ground, Flying, Psychic,
                     Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy])

# User Defined Variables
Q = 10
rho = 0.9
alpha = 1
beta = 1