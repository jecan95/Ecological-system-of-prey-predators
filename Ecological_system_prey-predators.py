#Jean Gun
#Projet: Systèmes écologiques proie-prédateur
import numpy as np
from tkinter import Tk, Canvas, Button, RIGHT, LEFT
from random import random
from scipy.integrate import odeint

#Variables
# Dimension de l'automate
NbL = 20  # hauteur du tableau
NbC =  20 # largeur du tableau
taille = 20 #taille de la cellule

#Choix pour la simulation 
presence_intermediaire = False #Prèsence ou non de l'espèce intermédiaire
presence_obstacle = False #Prèsence ou non d'obstacles


RepPro = 0.001 #coefficient de répartition pour les proies
RepPred = 0.005 #coefficient de répatition pour les prédateurs
RepInt = 0.001 #coefficient de répartition pour l'espèce intermédiaire
T = 20 #Limitation temporelle

# Définition des matrices d'évolution de l'automate
pop = np.zeros((NbL,NbC),dtype=int)
etat = np.zeros((NbL,NbC),dtype=int)
Nbpas = 0

# Définition de l'alphabet de l'automate dans un dictionnaire Python
state = {"PROIE":0,"PREDATEUR":1,"VIDE":2, "INTERMEDIAIRE": 3, "OBSTACLE":4}

# Définition des couleurs associées
ColorPro = "yellow"
ColorPred = "red"
ColorVide = "green"
ColorInt = "orange"
ColorObs = "Brown"

#Les effectifs de population au temps initial
NbPro = 5 #effectif initiale pour les proies
NbPred = 5 #effectif initiale pour les prédateurs
NbInt = 5 #effectif initiale pour l'espèce intermédiaire

#Coefficients pour l'équation Lokta-Volterra
alpha_LV = 1 #taux de reproduction des proies
beta_LV = 1 #taux de décès des proies du à la prédation
delta_LV = 1 #taux de reproduction des prédateurs
gamma_LV = 1 #taux de décès des prédateurs
t = np.linspace(0,5,30) #Variable temporelle pour la résolution
#des équations de Lokta-Volterre

#Coefficients pour diverses fonctions qui servira dans l'étude des 
#variables non constantes du modèle étudié
A = 1
B = 1

#Fonctions
#Modèle Proie-Prédateur de Lokta-Volterre
def Lokta_Volterra(z,t,alpha, beta, delta, gamma):
    global A,B
    x = z[0]
    y = z[1]
    dxdt = alpha * x - beta * x * y
    dydt = exp_(t,B,A) * x * y - gamma * y
    return dxdt, dydt  

#Fonctions qui servent à étudier notre modèle si les variables sont des
#fonctions dépendant du temps
def lin(t, B, A):
    return A + B*t

def exp_asym(t,B,A):
    return A*(1 - np.exp(-B*t))

def exp_(t,B,A):
    return A*np.exp(B*t)

#Fonction de traitement du clic gauche de la souris et du placement
#des obstacles durant la simulation
def obstacle(event):
    global taille, NbObs
    s = 0
    x, y = event.x//taille, event.y//taille
    if (etat[x,y] == state["VIDE"]) & (s <= 1):
        etat[x,y] = state["OBSTACLE"]
        s += 1
        canvas.itemconfig(pop[x][y], fill=ColorObs)

# Initialisation de l'automate
def Initialisation_Automate(presence_intermediaire, presence_obstacle):
# répartition aléatoire sur la grille des différentes espèces
    global taille, NbL, NbC
    global RepPro, RepPred, RepInt, NbPro, NbPred, NbInt
    etat[0:NbL,0:NbC] = state["VIDE"] 
    p, q, r = 0, 0, 0
    while (p != NbPro) or (q != NbPred):
        for i in range(NbL):
            for j in range(NbC):
                if (random() < RepPro) & (p !=NbPro) & (etat[i,j] == state["VIDE"]):
                    etat[i,j] = state["PROIE"]  
                    p += 1

                if (random() < RepPred) & (q != NbPred) &(etat[i,j] == state["VIDE"]):
                    etat[i,j] = state["PREDATEUR"]  
                    q += 1
    
    if (presence_intermediaire == True):
        while (p != NbPro) or (q != NbPred) or (r != NbInt):
            for i in range(NbL):
                for j in range(NbC):
                    if (random() < RepPro) & (p !=NbPro) & (etat[i,j] == state["VIDE"]):
                        etat[i,j] = state["PROIE"]  
                        p += 1

                    if (random() < RepPred) & (q != NbPred) & (etat[i,j] == state["VIDE"]):
                        etat[i,j] = state["PREDATEUR"]  
                        q += 1
                        
                    if (random() < RepInt) & (r != NbInt) & (etat[i,j] == state["VIDE"]):              
                        etat[i,j] = state["INTERMEDIAIRE"]  
                        r += 1
                    
# création de la grille d'affichage
    for i in range(NbL):
        for j in range(NbC):
            if etat[i,j] == state["VIDE"]:
                color = ColorVide
                
            if etat[i,j] == state["PROIE"]:
                color = ColorPro
                
            if etat[i,j] == state["PREDATEUR"]:
                color = ColorPred
                
            if etat[i,j] == state["INTERMEDIAIRE"]:
                color = ColorInt
            
            pop[i,j] = canvas.create_rectangle((i*taille, j*taille,\
                        (i+1)*taille, (j+1)*taille), outline="gray", fill=color)

# Dessiner les différentes cases
def draw(NbL,NbC):
    for x in range(NbL):
        for y in range(NbC):
            if etat[x,y] == state["PROIE"]:
                couleur = ColorPro
                
            if etat[x,y] == state["PREDATEUR"]:
                couleur = ColorPred
                
            if etat[x,y] == state["VIDE"]:
                couleur = ColorVide
                
            if etat[x,y] == state["INTERMEDIAIRE"]:
                couleur = ColorInt
            
            if etat[x,y] == state["OBSTACLE"]:
                couleur = ColorObs
                
            canvas.itemconfig(pop[x][y], fill=couleur)
            
            
#Fonction permettant le déplacement des prédateurs
#La règle, c'est que la fonction va comparer les parties du plateau qui sont 
#divisées en quatre parties: le nord-ouest(NO), le sud-est (SE),le nord-est (NE)
#et le sud-ouest(SO) et le prédateur se déplace en diagonale d'une case vers 
#la partie où il y a le plus de proies
#Cas: prèsence de l'espèce intermédiaire
def deplacement_predateur1(NbL,NbC):
    global etat
    temp = etat.copy()  # sauvegarde de l'état courant
    print("DEPLACEMENT PREDATEUR(S)")
    for i in range(NbL):
        for j in range(NbC):
            NO, NE, SO, SE = 0, 0, 0, 0
            if etat[i,j] == state["PREDATEUR"]: 
                
#On va comparer les différentes parties du tableau pour 
#savoir où va se déplacer les prédateurs
                for xNO in range(i):
                    for yNO in range(j):
                        if etat[xNO,yNO] == state["PROIE"]\
                        or etat[xNO,yNO] == state["INTERMEDIAIRE"]:
                            NO += 1
                            
                for xNE in range(i,NbL):
                    for yNE in range(j):
                        if etat[xNE,yNE] == state["PROIE"]\
                        or etat[xNE,yNE] == state["INTERMEDIAIRE"]:
                                NE += 1
                            
                for xSO in range (i):
                    for ySO in range(j,NbC):
                        if etat[xSO,ySO] == state["PROIE"]\
                        or etat[xSO,ySO] == state["INTERMEDIAIRE"]:
                            SO += 1
                            
                for xSE in range(i,NbL):
                    for ySE in range(j,NbC):
                        if etat[xSE,ySE] == state["PROIE"]\
                        or etat[xSE,ySE] == state["INTERMEDIAIRE"]:
                            SE += 1
                            
                print("il y a", NO,"proie(s) dans la zone nord-ouest")
                print("il y a", NE,"proie(s) dans la zone nord-est")
                print("il y a", SO,"proie(s) dans la zone sud-ouest")
                print("il y a", SE,"proie(s) dans la zone sud-est")                
                
#Ici, le prédateur effectue son déplacement
                if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                    if (etat[i - 1,j - 1] == state["VIDE"])\
                    & (NO >= NE)\
                    & (NO >= SO)\
                    & (NO >= SE):
                        print("déplacement nord-ouest")
                        temp[i,j] = state["VIDE"]
                        temp[i - 1,j - 1] = state["PREDATEUR"]
                    
                    elif (etat[i + 1,j - 1] == state["VIDE"])\
                    & (NE >= NO)\
                    & (NE >= SO)\
                    & (NE >= SE):
                        print("déplacement nord-est")
                        temp[i,j] = state["VIDE"]
                        temp[i + 1,j - 1] = state["PREDATEUR"]
                    
                    elif (etat[i - 1,j + 1] == state["VIDE"])\
                    & (SO >= NO)\
                    & (SO >= NE)\
                    & (SO >= SE):
                        print("déplacement sud-ouest")
                        temp[i,j] = state["VIDE"]
                        temp[i - 1,j + 1] = state["PREDATEUR"]
                    
                    elif (etat[i + 1,j + 1] == state["VIDE"])\
                    & (SE >= NO)\
                    & (SE >= SO)\
                    & (SE >= NE):
                        print("déplacement sud-est")
                        temp[i,j] = state["VIDE"]
                        temp[i + 1,j + 1] = state["PREDATEUR"]            
                    
                elif (i == 0) & (etat[NbL -1,j] == state["VIDE"]):
                    temp[NbL -1,j] = state["PREDATEUR"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme sud de l'échiquier")
                        
                elif (j == 0) & (etat[i,NbC -1] == state["VIDE"]):
                    temp[i,NbC -1] = state["PREDATEUR"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme est de l'échiquier")
                    
                elif (i == NbL - 1) & (etat[0,j] == state["VIDE"]):
                    temp[0,j] = state["PREDATEUR"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme nord de l'échiquier")
                    
                elif (j == NbC - 1) & (etat[i,0] == state["VIDE"]):
                    temp[i,0] = state["PREDATEUR"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme ouest de l'échiquier")
                
    etat = temp.copy()  # mise à jour de l'état courant

#Cas: Absence de l'espèce intermédiaire
def deplacement_predateur2(NbL,NbC):
    global etat
    temp = etat.copy()  # sauvegarde de l'état courant
    print("DEPLACEMENT PREDATEUR(S)")
    for i in range(NbL):
        for j in range(NbC):
            NO, NE, SO, SE = 0, 0, 0, 0
            if etat[i,j] == state["PREDATEUR"]: 
                
#On va comparer les différentes parties du tableau pour 
#savoir où va se déplacer les prédateurs
                for xNO in range(i):
                    for yNO in range(j):
                        if etat[xNO,yNO] == state["PROIE"]:
                            NO += 1
                            
                for xNE in range(i,NbL):
                    for yNE in range(j):
                        if etat[xNE,yNE] == state["PROIE"]:
                            NE += 1
                            
                for xSO in range (i):
                    for ySO in range(j,NbC):
                        if etat[xSO,ySO] == state["PROIE"]:
                            SO += 1
                            
                for xSE in range(i,NbL):
                    for ySE in range(j,NbC):
                        if etat[xSE,ySE] == state["PROIE"]:
                            SE += 1
                            
                print("il y a", NO,"proie(s) dans la zone nord-ouest")
                print("il y a", NE,"proie(s) dans la zone nord-est")
                print("il y a", SO,"proie(s) dans la zone sud-ouest")
                print("il y a", SE,"proie(s) dans la zone sud-est")                
                
#Ici, le prédateur effectue son déplacement
                if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                    if (etat[i - 1,j - 1] == state["VIDE"])\
                    & (NO >= NE)\
                    & (NO >= SO)\
                    & (NO >= SE):
                        print("déplacement nord-ouest")
                        temp[i,j] = state["VIDE"]
                        temp[i - 1,j -1] = state["PREDATEUR"]
                    
                    elif (etat[i + 1,j - 1] == state["VIDE"])\
                    & (NE >= NO)\
                    & (NE >= SO)\
                    & (NE >= SE):
                        print("déplacement nord-est")
                        temp[i,j] = state["VIDE"]
                        temp[i + 1,j -1] = state["PREDATEUR"]
                    
                    elif (etat[i - 1,j + 1] == state["VIDE"])\
                    & (SO >= NO)\
                    & (SO >= NE)\
                    & (SO >= SE):
                        print("déplacement sud-ouest")
                        temp[i,j] = state["VIDE"]
                        temp[i - 1,j + 1] = state["PREDATEUR"]
                    
                    elif (etat[i + 1,j + 1] == state["VIDE"])\
                    & (SE >= NO)\
                    & (SE >= SO)\
                    & (SE >= NE):
                        print("déplacement sud-est")
                        temp[i,j] = state["VIDE"]
                        temp[i + 1,j + 1] = state["PREDATEUR"]                                
                    
                elif i == 0:
                    temp[i,j] = state["VIDE"]
                    temp[NbL -1,j] = state["PREDATEUR"]
                    print("Déplacement à l'extreme sud de l'échiquier")
                        
                elif j == 0:
                    temp[i,j] = state["VIDE"]
                    temp[i,NbC -1] = state["PREDATEUR"]
                    print("Déplacement à l'extreme est de l'échiquier")
                    
                elif i == NbL - 1:
                    temp[i,j] = state["VIDE"]
                    temp[0,j] = state["PREDATEUR"]
                    print("Déplacement à l'extreme nord de l'échiquier")
                    
                elif j == NbC - 1:
                    temp[i,j] = state["VIDE"]
                    temp[i,0] = state["PREDATEUR"]
                    print("Déplacement à l'extreme ouest de l'échiquier")
                
                
    etat = temp.copy()  # mise à jour de l'état courant

#Fonction permettant le déplacement des proies
#La règle, c'est que la fonction va comparer les parties du plateau qui sont 
#divisées en quatre parties: le nord-ouest(NO), le sud-est (SE),le nord-est (NE)
#et le sud-ouest(SO) et la proie se déplace d'une case en diagonale vers la
# partie où il y a le moins de prédateurs
#Cas: prèsence de l'espèce intermédiaire
def deplacement_proie1(NbL,NbC):
    global etat
    temp = etat.copy()  # sauvegarde de l'état courant
    print("DEPLACEMENT PROIE(S)")
    for i in range(NbL):
        for j in range(NbC):
            NO, NE, SO, SE = 0, 0, 0, 0
            if etat[i,j] == state["PROIE"]: 
                
#On va comparer les différentes parties du tableau pour 
#savoir où va se déplacer les proies
                for xNO in range(i):
                    for yNO in range(j):
                        if etat[xNO,yNO] == state["PREDATEUR"]\
                            or etat[xNO,yNO] == state["INTERMEDIAIRE"]:
                            NO += 1
                            
                for xNE in range(i,NbL):
                    for yNE in range(j):
                        if etat[xNE,yNE] == state["PREDATEUR"]\
                            or etat[xNE,yNE] == state["INTERMEDIAIRE"]:
                            NE += 1
                            
                for xSO in range (i):
                    for ySO in range(j,NbC):
                        if etat[xSO,ySO] == state["PREDATEUR"]\
                            or etat[xSO,ySO] == state["INTERMEDIAIRE"]:
                            SO += 1
                            
                for xSE in range(i,NbL):
                    for ySE in range(j,NbC):
                        if etat[xSE,ySE] == state["PREDATEUR"]\
                            or etat[xSE,ySE] == state["INTERMEDIAIRE"]:
                            SE += 1
                            
                print("il y a", NO,"prédateur(s) dans la zone nord-ouest")
                print("il y a", NE,"prédateur(s) dans la zone nord-est")
                print("il y a", SO,"prédateur(s) dans la zone sud-ouest")
                print("il y a", SE,"prédateur(s) dans la zone sud-est")                
                
#Ici, la proie effectue son déplacement
                if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                    if (etat[i - 1,j - 1] == state["VIDE"])\
                    & (NO <= NE)\
                    & (NO <= SO)\
                    & (NO <= SE):
                        print("déplacement nord-ouest")
                        temp[i,j] = state["VIDE"]
                        temp[i - 1,j -1] = state["PROIE"]
                    
                    elif (etat[i + 1,j - 1] == state["VIDE"])\
                    & (NE <= NO)\
                    & (NE <= SO)\
                    & (NE <= SE):
                        print("déplacement nord-est")
                        temp[i,j] = state["VIDE"]
                        temp[i + 1,j -1] = state["PROIE"]
                    
                    elif (etat[i - 1,j + 1] == state["VIDE"])\
                    & (SO <= NO)\
                    & (SO <= NE)\
                    & (SO <= SE):
                        print("déplacement sud-ouest")
                        temp[i,j] = state["VIDE"]
                        temp[i - 1,j + 1] = state["PROIE"]
                    
                    elif (etat[i + 1,j + 1] == state["VIDE"])\
                    & (SE <= NO)\
                    & (SE <= SO)\
                    & (SE <= NE):
                        print("déplacement sud-est")
                        temp[i,j] = state["VIDE"]
                        temp[i + 1,j + 1] = state["PROIE"]
                
                elif (i == 0) & (etat[NbL -1,j] == state["VIDE"]):
                    temp[NbL -1,j] = state["PROIE"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme sud de l'échiquier")
                        
                elif (j == 0) & (etat[i,NbC -1] == state["VIDE"]):
                    temp[i,NbC -1] = state["PROIE"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme est de l'échiquier")
                    
                elif (i == NbL - 1) & (etat[0,j] == state["VIDE"]):
                    temp[0,j] = state["PROIE"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme nord de l'échiquier")
                    
                elif (j == NbC - 1) & (etat[i,0] == state["VIDE"]):
                    temp[i,0] = state["PROIE"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme ouest de l'échiquier")
                                                            
    etat = temp.copy()  # mise à jour de l'état courant

#Cas: Absence de l'espèce intermédiaire
def deplacement_proie2(NbL,NbC):
    global etat
    temp = etat.copy()  # sauvegarde de l'état courant
    print("DEPLACEMENT PROIE(S)")
    for i in range(NbL):
        for j in range(NbC):
            NO, NE, SO, SE = 0, 0, 0, 0
            if etat[i,j] == state["PROIE"]: 
                
#On va comparer les différentes parties du tableau pour 
#savoir où va se déplacer les proies
                for xNO in range(i):
                    for yNO in range(j):
                        if etat[xNO,yNO] == state["PREDATEUR"]:
                            NO += 1
                            
                for xNE in range(i,NbL):
                    for yNE in range(j):
                        if etat[xNE,yNE] == state["PREDATEUR"]:
                            NE += 1
                            
                for xSO in range (i):
                    for ySO in range(j,NbC):
                        if etat[xSO,ySO] == state["PREDATEUR"]:
                            SO += 1
                            
                for xSE in range(i,NbL):
                    for ySE in range(j,NbC):
                        if etat[xSE,ySE] == state["PREDATEUR"]:
                            SE += 1
                            
                print("il y a", NO,"prédateur(s) dans la zone nord-ouest")
                print("il y a", NE,"prédateur(s) dans la zone nord-est")
                print("il y a", SO,"prédateur(s) dans la zone sud-ouest")
                print("il y a", SE,"prédateur(s) dans la zone sud-est")                
                
#Ici, la proie effectue son déplacement
                if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                    if (etat[i - 1,j - 1] == state["VIDE"])\
                    & (NO <= NE)\
                    & (NO <= SO)\
                    & (NO <= SE):
                        print("déplacement nord-ouest")
                        temp[i,j] = state["VIDE"]
                        temp[i - 1,j -1] = state["PROIE"]
                    
                    elif (etat[i + 1,j - 1] == state["VIDE"])\
                    & (NE <= NO)\
                    & (NE <= SO)\
                    & (NE <= SE):
                        print("déplacement nord-est")
                        temp[i,j] = state["VIDE"]
                        temp[i + 1,j -1] = state["PROIE"]
                    
                    elif (etat[i - 1,j + 1] == state["VIDE"])\
                    & (SO <= NO)\
                    & (SO <= NE)\
                    & (SO <= SE):
                        print("déplacement sud-ouest")
                        temp[i,j] = state["VIDE"]
                        temp[i - 1,j + 1] = state["PROIE"]
                    
                    elif (etat[i + 1,j + 1] == state["VIDE"])\
                    & (SE <= NO)\
                    & (SE <= SO)\
                    & (SE <= NE):
                        print("déplacement sud-est")
                        temp[i,j] = state["VIDE"]
                        temp[i + 1,j + 1] = state["PROIE"]
                
                elif i == 0:
                    temp[i,j] = state["VIDE"]
                    temp[NbL -1,j] = state["PROIE"]
                    print("Déplacement à l'extreme sud de l'échiquier")
                        
                elif j == 0:
                    temp[i,j] = state["VIDE"]
                    temp[i,NbC -1] = state["PROIE"]
                    print("Déplacement à l'extreme est de l'échiquier")
                    
                elif i == NbL - 1:
                    temp[i,j] = state["VIDE"]
                    temp[0,j] = state["PROIE"]
                    print("Déplacement à l'extreme nord de l'échiquier")
                    
                elif j == NbC - 1:
                    temp[i,j] = state["VIDE"]
                    temp[i,0] = state["PROIE"]
                    print("Déplacement à l'extreme ouest de l'échiquier")
                        
    etat = temp.copy()  # mise à jour de l'état courant

#Fonction permettant le déplacement de l'espèce intermédiaire
#La règle, c'est que le programme va comparer les parties du plateau qui sont 
#divisées en quatre parties: le nord-ouest(NO), le sud-est (SE),le nord-est (NE)
#et le sud-ouest(SO) et la proie se déplace d'une case vers la partie où il y 
#a le moins de prédateurs et le plus de proies
def deplacement_intermediaire(NbL,NbC):
    global etat
    temp = etat.copy()  # sauvegarde de l'état courant
    print("DEPLACEMENT ESPECE INTERMEDIAIRE")
    for i in range(NbL):
        for j in range(NbC):
            NO1, NE1, SO1, SE1 = 0, 0, 0, 0
            NO2, NE2, SO2, SE2 = 0, 0, 0, 0            
            if etat[i,j] == state["INTERMEDIAIRE"]: 
                
#On va comparer les différentes parties du tableau pour 
#savoir où va se déplacer l'espèce intémédiaire
                for xNO in range(i):
                    for yNO in range(j):
                        if etat[xNO,yNO] == state["PREDATEUR"]:
                            NO1 -= 1
                        elif etat[xNO,yNO] == state["PROIE"]:
                            NO2 += 1
                            
                for xNE in range(i,NbL):
                    for yNE in range(j):
                        if etat[xNE,yNE] == state["PREDATEUR"]:
                            NE1 -= 1
                        elif etat[xNE,yNE] == state["PROIE"]:
                            NE2 += 1
                            
                            
                for xSO in range (i):
                    for ySO in range(j,NbC):
                        if etat[xSO,ySO] == state["PREDATEUR"]:                        
                            SO1 -= 1
                        elif etat[xSO,ySO] == state["PROIE"]:
                            SO2 += 1
                            
                for xSE in range(i,NbL):
                    for ySE in range(j,NbC):
                        if etat[xSE,ySE] == state["PREDATEUR"]:
                            SE1 -= 1
                        elif etat[xSE,ySE] == state["PROIE"]:
                            SE2 += 1
                            
                print("il y a", abs(NO1) ,"prédateur(s) dans la zone nord-ouest")
                print("Et il y a",NO2," proie(s) dans la meme zone")
                print("il y a", abs(NE1),"prédateur(s) dans la zone nord-est")
                print("Et il y a",NE2," proie(s) dans la meme zone")
                print("il y a", abs(SO1),"prédateur(s)dans la zone sud-ouest")
                print("Et il y a",SO2," proie(s) dans la meme zone")
                print("il y a", abs(SE1),"prédateur(s) dans la zone sud-est")
                print("Et il y a",SE2," proie(s) dans la meme zone")
                
                NO = NO1 + NO2
                NE = NE1 + NE2
                SO = SO1 + SO2
                SE = SE1 + SE2
#Ici, l'espèce intermédiaire effectue son déplacement
                if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                    if (etat[i - 1,j - 1] == state["VIDE"])\
                    & (NO >= NE)\
                    & (NO >= SO)\
                    & (NO >= SE):
                        print("déplacement nord-ouest")
                        temp[i - 1,j -1] = state["INTERMEDIAIRE"]
                        temp[i,j] = state["VIDE"]
                    
                    elif (etat[i + 1,j - 1] == state["VIDE"])\
                    & (NE >= NO)\
                    & (NE >= SO)\
                    & (NE >= SE):
                        print("déplacement nord-est")
                        temp[i,j] = state["VIDE"]
                        temp[i + 1,j -1] = state["INTERMEDIAIRE"]
                    
                    elif (etat[i - 1,j + 1] == state["VIDE"])\
                    & (SO >= NO)\
                    & (SO >= NE)\
                    & (SO >= SE):
                        print("déplacement sud-ouest")
                        temp[i - 1,j + 1] = state["INTERMEDIAIRE"]
                        temp[i,j] = state["VIDE"]
                    
                    elif (etat[i + 1,j + 1] == state["VIDE"])\
                    & (SE >= NO)\
                    & (SE >= SO)\
                    & (SE >= NE):
                        print("déplacement sud-est")
                        temp[i + 1,j + 1] = state["INTERMEDIAIRE"]
                        temp[i,j] = state["VIDE"]
                    
                    else:
                        temp[i,j] = state["INTERMEDIAIRE"]
                        print("Immobile")
                
                elif (i == 0) & (etat[NbL -1,j] == state["VIDE"]):
                    temp[NbL -1,j] = state["INTERMEDIAIRE"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme sud de l'échiquier")
                        
                elif (j == 0) & (etat[i,NbC -1] == state["VIDE"]):
                    temp[i,NbC -1] = state["INTERMEDIAIRE"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme est de l'échiquier")
                    
                elif (i == NbL - 1) & (etat[0,j] == state["VIDE"]):
                    temp[0,j] = state["INTERMEDIAIRE"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme nord de l'échiquier")
                    
                elif (j == NbC - 1) & (etat[i,0] == state["VIDE"]):
                    temp[i,0] = state["INTERMEDIAIRE"]
                    temp[i,j] = state["VIDE"]
                    print("Déplacement à l'extreme ouest de l'échiquier")
                
                else:
                    temp[i,j] = state["INTERMEDIAIRE"]
                    print("Immobile")
                        
    etat = temp.copy()  # mise à jour de l'état courant

#Fonction qui permet l'apparition de nouveaux effectifs avec les équations de
#Lokta-Volterre dans les deux populations
#Principe: Les coefficients liés à la reproduction seront multipliés par une valeur
#arbitraire mais permettant une reproduction importante
#De plus, la répartition des nouveaux nés se fera à proximité d'un congénère
#Cas: Présence de l'espèce intermédiaire
def reproduction1(NbL,NbC):
    global etat, t, alpha_LV, beta_LV, delta_LV, gamma_LV
    temp = etat.copy()  # sauvegarde de l'état courant
    print("PHASE REPRODUCTION")
    p,q,r = 0,0,0
    eff_proie, eff_intermediaire, eff_predateur = 0,0,0
    
    for i in range(NbL):
        for j in range(NbC):
            if etat[i,j] == state["PROIE"]:
                eff_proie += 1
            if etat[i,j] == state["INTERMEDIAIRE"]:
                eff_intermediaire += 1
            if etat[i,j] == state["PREDATEUR"]:
                eff_predateur += 1
    
    z01 = [eff_proie,eff_intermediaire]
    z02 = [eff_intermediaire, eff_predateur]
    z03 = [eff_proie,eff_predateur]
   
#Résolution de des équations du modèle Lokta Volterra avec les nouvelles
#effectifs de population
    res = odeint(Lokta_Volterra,z01,t,args=(alpha_LV,beta_LV/6,delta_LV,gamma_LV/3))
    tabPro1,tabInt1 = res.T
    res =  odeint(Lokta_Volterra,z02,t,args=(alpha_LV,beta_LV/6,delta_LV,gamma_LV/3))
    tabInt2, tabPred1 = res.T
    res =  odeint(Lokta_Volterra,z03,t,args=(alpha_LV,beta_LV/6,delta_LV,gamma_LV/3))
    tabPro2,tabPred2 = res.T
                
#Répartition des nouvelles effectifs à proximité des anciennes
    Delta_Proie = int(tabPro1[1] + tabPro2[1]) - int(tabPro1[0] + tabPro2[0])
    Delta_Intermediaire = ( int(tabInt1[1]) + int(tabInt2[1]) ) \
        - (int( tabInt1[0]) + int(tabInt2[0]) )
    Delta_Predateur = int(tabPred1[1] + tabPred2[1]) - int(tabPred1[0] + tabPred2[0])

#Dans le cas, où l'une des deux populations ne peuvent pas accroitre leurs
#populations 
    if (Delta_Proie <= 0):
        print("La population des proies n'a pas pu s'accroitre")
    
    if (Delta_Intermediaire <= 0):
        print("L'espèce intermédiaire n'a pas pu s'accroitre")
        
    if (Delta_Predateur <= 0):
        print("La population des prédateurs n'a pas pu s'accroitre")
        
    if (Delta_Predateur > 0):
        print("Il y aura en tout",Delta_Predateur,"nouveau(x) prédateur(s)")
        
#Répartion pour le ou les nouveau(x) "né(s)" parmi les prédateurs
        for i in range(NbL):
            for j in range(NbC):
                if etat[i,j] == state["PREDATEUR"]:
                    if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                        if (etat[i + 1,j] == state["VIDE"]):
                            if (p != Delta_Predateur):
                                temp[i + 1,j] = state["PREDATEUR"]  
                                p += 1
                        if (etat[i - 1,j] == state["VIDE"]):
                            if (p != Delta_Predateur):
                                temp[i - 1,j] = state["PREDATEUR"]  
                                p += 1
                        if (etat[i,j + 1] == state["VIDE"]):
                            if (p != Delta_Predateur):
                                temp[i,j + 1] = state["PREDATEUR"]  
                                p += 1
                        if (etat[i,j - 1] == state["VIDE"]):
                            if (p != Delta_Predateur):
                                temp[i,j -1] = state["PREDATEUR"]  
                                p += 1
                    
                    elif (i == 0) & (temp[NbL - 1,j] == state["VIDE"]) :
                        if (p != Delta_Predateur):
                            temp[NbL - 1,j] = state["PREDATEUR"]
                            p += 1
                        
                    elif (j == 0) & (temp[i,NbC -1] == state["VIDE"]):
                        if (p != Delta_Predateur):
                            temp[i,NbC -1] = state["PREDATEUR"]
                            p += 1
                    
                    elif (i == NbL - 1) & (temp[0,j] == state["VIDE"]):
                        if (p != Delta_Predateur):
                            temp[0,j] = state["PREDATEUR"]
                            p += 1
                    
                    elif (j == NbC - 1) & temp[0,j] == state["VIDE"]:
                        if (p != Delta_Predateur):
                            temp[i,0] = state["PREDATEUR"]
                            p += 1
        
    if (Delta_Intermediaire > 0):
        print("l'effectif de l'espèce intermédiare\
              s'accroit de",Delta_Intermediaire)
        
#Répartion pour le ou les nouveau(x) "né(s)" parmi l'espèce intermédiaire
        for i in range(NbL):
            for j in range(NbC):
                if etat[i,j] == state["INTERMEDIAIRE"]:
                    if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                        if (etat[i + 1,j] == state["VIDE"]):
                            if r != Delta_Intermediaire:
                                temp[i + 1,j] = state["INTERMEDIAIRE"]  
                                r += 1
                        if etat[i - 1,j] == state["VIDE"]:
                            if (r != Delta_Intermediaire):
                                temp[i - 1,j] = state["INTERMEDIAIRE"]  
                                r += 1
                        if etat[i,j + 1] == state["VIDE"]:
                            if (r != Delta_Intermediaire):
                                temp[i,j + 1] = state["INTERMEDIAIRE"]  
                                r += 1
                        if etat[i,j - 1] == state["VIDE"]:
                            if (r != Delta_Intermediaire):
                                temp[i,j -1] = state["INTERMEDIAIRE"]  
                                r += 1
                    
                    elif (i == 0) & (temp[NbL - 1,j] == state["VIDE"]) :
                        if (r != Delta_Intermediaire):
                            temp[NbL - 1,j] = state["INTERMEDIAIRE"]
                            r += 1
                        
                    elif (j == 0) & (temp[i,NbC -1] == state["VIDE"]):
                        if (r != Delta_Intermediaire):
                            temp[i,NbC -1] = state["INTERMEDIAIRE"]
                            r += 1
                    
                    elif (i == NbL - 1) & (temp[0,j] == state["VIDE"]):
                        if (r != Delta_Intermediaire):
                            temp[0,j] = state["INTERMEDIAIRE"]
                            r += 1
                    
                    elif (j == NbC - 1) & temp[0,j] == state["VIDE"]:
                        if (r != Delta_Intermediaire):
                            temp[i,0] = state["INTERMEDIAIRE"]
                            r += 1
                                          
    if (Delta_Proie > 0):
        print("Il y aura en tout",Delta_Proie,"nouvelle(s) proie(s)")

#Répartion pour le ou les nouveau(x) "né(s)" parmi les proies        
        for i in range(NbL):
            for j in range(NbC):
                if etat[i,j] == state["PROIE"]:
                    if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                        if (etat[i + 1,j] == state["VIDE"]):
                            if (q != Delta_Proie):
                                temp[i + 1,j] = state["PROIE"]  
                                q += 1
                        if (etat[i - 1,j] == state["VIDE"]):
                            if (q != Delta_Proie):
                                temp[i - 1,j] = state["PROIE"]  
                                q += 1
                        if (etat[i,j + 1] == state["VIDE"]):
                            if (q != Delta_Proie):
                                temp[i,j + 1] = state["PROIE"]  
                                q += 1
                        if (etat[i,j - 1] == state["VIDE"]):
                            if (q != Delta_Proie):
                                temp[i,j -1] = state["PROIE"]  
                                q += 1
                    
                    elif (i == 0) & (temp[NbL - 1,j] == state["VIDE"]) :
                        if (q != Delta_Proie):
                            temp[NbL - 1,j] = state["PROIE"]
                            q += 1
                        
                    elif (j == 0) & (temp[i,NbC -1] == state["VIDE"]):
                        if (q != Delta_Proie):
                            temp[i,NbC -1] = state["PROIE"]
                            q += 1
                    
                    elif (i == NbL - 1) & (temp[0,j] == state["VIDE"]):
                        if (q != Delta_Proie):
                            temp[0,j] = state["PROIE"]
                            q += 1
                    
                    elif (j == NbC - 1) & temp[0,j] == state["VIDE"]:
                        if (q != Delta_Proie):
                            temp[i,0] = state["PROIE"]
                            q += 1
                    
    etat = temp.copy() # mise à jour de l'état courant

#Cas: Absence de l'espèce intermédiaire
def reproduction2(NbL,NbC):
    global etat, t, alpha_LV, beta_LV, delta_LV, gamma_LV
    temp = etat.copy()  # sauvegarde de l'état courant
    print("PHASE REPRODUCTION")
    p,q = 0,0
    eff_proie, eff_predateur = 0,0
    for i in range(NbL):
        for j in range(NbC):
            if etat[i,j] == state["PROIE"]:
                eff_proie += 1
            if etat[i,j] == state["PREDATEUR"]:
                eff_predateur += 1
    
    z0 = [eff_proie,eff_predateur]
   
#Résolution de des équations du modèle Lokta Volterre avec les nouvelles
#effectifs de population
    res = odeint(Lokta_Volterra,z0,t,args=(alpha_LV,beta_LV/6,delta_LV,gamma_LV/3))
    tabPro,tabPred = res.T 
                
#Répartition des nouvelles effectifs à proximité des anciennes
    Delta_Proie = int(tabPro[1]) - int(tabPro[0])
    Delta_Predateur = int(tabPred[1]) - int(tabPred[0])

#Dans le cas, où l'une des deux populations ne peuvent pas accroitre leurs
#populations 
    if (Delta_Proie <= 0):
        print("La population des proies n'a pas pu s'accroitre")
    
    if (Delta_Predateur <= 0):
        print("La population des prédateurs n'a pas pu s'accroitre")
        
    if (Delta_Predateur > 0):
        print("Il y aura en tout",Delta_Predateur,"nouveau(x) prédateur(s)")
        
#Répartion pour le ou les nouveau(x) "né(s)" parmi les prédateurs
        for i in range(NbL):
            for j in range(NbC):
                if etat[i,j] == state["PREDATEUR"]:
                    if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                        if (etat[i + 1,j] == state["VIDE"]):
                            if (q != Delta_Predateur):
                                temp[i + 1,j] = state["PREDATEUR"]  
                                q += 1
                        if (etat[i - 1,j] == state["VIDE"]):
                            if (q != Delta_Predateur):
                                temp[i - 1,j] = state["PREDATEUR"]  
                                q += 1
                        if (etat[i,j + 1] == state["VIDE"]):
                            if (q != Delta_Predateur):
                                temp[i,j + 1] = state["PREDATEUR"]  
                                q += 1
                        if (etat[i,j - 1] == state["VIDE"]):
                            if (q != Delta_Predateur):
                                temp[i,j -1] = state["PREDATEUR"]  
                                q += 1
                    
                    elif (i == 0) & (temp[NbL - 1,j] == state["VIDE"]) :
                        if (q != Delta_Predateur):
                            temp[NbL - 1,j] = state["PREDATEUR"]
                            q += 1
                        
                    elif (j == 0) & (temp[i,NbC -1] == state["VIDE"]):
                        if (q != Delta_Predateur):
                            temp[i,NbC -1] = state["PREDATEUR"]
                            q += 1
                    
                    elif (i == NbL - 1) & (temp[0,j] == state["VIDE"]):
                        if (q != Delta_Predateur):
                            temp[0,j] = state["PREDATEUR"]
                            q += 1
                    
                    elif (j == NbC - 1) & temp[0,j] == state["VIDE"]:
                        if (q != Delta_Predateur):
                            temp[i,0] = state["PREDATEUR"]
                            q += 1
                                          
    if (Delta_Proie > 0):
        print("Il y aura en tout",Delta_Proie,"nouvelle(s) proie(s)")

#Répartion pour le ou les nouveau(x) "né(s)" parmi les proies        
        for i in range(NbL):
            for j in range(NbC):
                if etat[i,j] == state["PROIE"]:
                    if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                        if (etat[i + 1,j] == state["VIDE"]):
                            if (p != Delta_Proie):
                                temp[i + 1,j] = state["PROIE"]  
                                p += 1
                        if (etat[i - 1,j] == state["VIDE"]):
                            if (p != Delta_Proie):
                                temp[i - 1,j] = state["PROIE"]  
                                p += 1
                        if (etat[i,j + 1] == state["VIDE"]):
                            if (p != Delta_Proie):
                                temp[i,j + 1] = state["PROIE"]  
                                p += 1
                        if (etat[i,j - 1] == state["VIDE"]):
                            if (p != Delta_Proie):
                                temp[i,j -1] = state["PROIE"]  
                                p += 1
                    
                    elif (i == 0) & (temp[NbL - 1,j] == state["VIDE"]) :
                        if (p != Delta_Proie):
                            temp[NbL - 1,j] = state["PROIE"]
                            p += 1
                        
                    elif (j == 0) & (temp[i,NbC -1] == state["VIDE"]):
                        if (p != Delta_Proie):
                            temp[i,NbC -1] = state["PROIE"]
                            p += 1
                    
                    elif (i == NbL - 1) & (temp[0,j] == state["VIDE"]):
                        if (p != Delta_Proie):
                            temp[0,j] = state["PROIE"]
                            p += 1
                    
                    elif (j == NbC - 1) & temp[0,j] == state["VIDE"]:
                        if (p != Delta_Proie):
                            temp[i,0] = state["PROIE"]
                            p += 1
                    
    etat = temp.copy() # mise à jour de l'état courant

#Fonction qui régit les paramètres pour le chasse
#Principe: si un prédateur et une proie se trouvent cote à cote sur le plateau 
#la proie sera "dévorée"
#Cas: Présence de l'espèce intermédiaire
def chasse1(NbL,NbC,Nbpas):
    global etat
    manger_proie, manger_intermediaire = 0,0
    temp = etat.copy()  # sauvegarde de l'état courant
    for i in range(NbL):
        for j in range(NbC):
            if etat[i,j] == state["PROIE"]:
                if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                    if etat[i + 1,j] == state["PREDATEUR"]\
                        or etat[i + 1,j] == state["INTERMEDIAIRE"]: 
                        temp[i,j] = state["VIDE"]
                        manger_proie += 1
                    
                    elif etat[i - 1,j] == state["PREDATEUR"]\
                        or etat[i - 1,j] == state["INTERMEDIAIRE"]:
                        temp[i,j] = state["VIDE"]
                        manger_proie += 1
                    
                    elif etat[i,j + 1] == state["PREDATEUR"]\
                        or etat[i,j + 1] == state["INTERMEDIAIRE"]: 
                        temp[i,j] = state["VIDE"]
                        manger_proie += 1
                    
                    elif etat[i,j - 1] == state["PREDATEUR"]\
                        or etat[i,j - 1] == state["INTERMEDIAIRE"]:
                        temp[i,j] = state["VIDE"]
                        manger_proie += 1
                    
                elif (i == 0) & (etat[NbL -1,j] == state["PREDATEUR"])\
                    or (etat[NbL -1,j] == state["INTERMEDIAIRE"]):
                    temp[i,j] = state["VIDE"]
                    manger_proie += 1
                        
                elif (j == 0) & (etat[i,NbC -1] == state["PREDATEUR"])\
                    or (etat[i,NbC -1] == state["INTERMEDIAIRE"]):
                    temp[i,j] = state["VIDE"]
                    manger_proie += 1
                    
                elif (i == NbL - 1) & (etat[0,j] == state["PREDATEUR"])\
                    or (etat[0,j] == state["INTERMEDIAIRE"]):
                    temp[i,j] = state["VIDE"]
                    manger_proie += 1
                    
                elif (j == NbC - 1) & (etat[i,0] == state["PREDATEUR"])\
                    or (etat[i,0] == state["INTERMEDIAIRE"]):
                    temp[i,j] = state["VIDE"]
                    manger_proie += 1
            
            if etat[i,j] == state["INTERMEDIAIRE"]:
                if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                    if etat[i + 1,j] == state["PREDATEUR"]: 
                        temp[i,j] = state["VIDE"]
                        manger_intermediaire += 1
                    
                    elif etat[i - 1,j] == state["PREDATEUR"]:
                        temp[i,j] = state["VIDE"]
                        manger_intermediaire += 1
                    
                    elif etat[i,j + 1] == state["PREDATEUR"]: 
                        temp[i,j] = state["VIDE"]
                        manger_intermediaire += 1
                    
                    elif etat[i,j - 1] == state["PREDATEUR"]:
                        temp[i,j] = state["VIDE"]
                        manger_intermediaire += 1
                
                elif (i == 0) & (etat[NbL -1,j] == state["PREDATEUR"]):
                    temp[i,j] = state["VIDE"]
                    manger_intermediaire += 1
                        
                elif (j == 0) & (etat[i,NbC -1] == state["PREDATEUR"]):
                    temp[i,j] = state["VIDE"]
                    manger_intermediaire += 1
                    
                elif (i == NbL - 1) & (etat[0,j] == state["PREDATEUR"]):
                    temp[i,j] = state["VIDE"]
                    manger_intermediaire += 1
                    
                elif (j == NbC - 1) & (etat[i,0] == state["PREDATEUR"]):
                    temp[i,j] = state["VIDE"]
                    manger_intermediaire += 1
                        
                    
    if manger_proie != 0:
        print("PROIE(S) CHASSEE(S)")
        print("Il y a eu", manger_proie, " proie(s) chassée(s)")
    
    if manger_intermediaire != 0:
        print("ESPECE INTERMEDIAIRE CHASSEE")
        print("Parmi l'espèce intermédiaire, il y a eu", manger_intermediaire\
              ,"mort(s) à cause de la chasse")
            
    etat = temp.copy() # mise à jour de l'état courant
    
#Cas: Absence de l'espèce intermédiaire
def chasse2(NbL,NbC,Nbpas):
    global etat
    manger = 0
    temp = etat.copy()  # sauvegarde de l'état courant
    for i in range(NbL):
        for j in range(NbC):
            if etat[i,j] == state["PROIE"]:
                if (0 < i < NbL - 1) & (0 < j < NbC - 1):
                    if etat[i + 1,j] == state["PREDATEUR"]: 
                        temp[i,j] = state["VIDE"]
                        manger += 1
                    
                    elif etat[i - 1,j] == state["PREDATEUR"]:
                        temp[i,j] = state["VIDE"]
                        manger += 1
                    
                    elif etat[i,j + 1] == state["PREDATEUR"]: 
                        temp[i,j] = state["VIDE"]
                        manger += 1
                    
                    elif etat[i,j - 1] == state["PREDATEUR"]:
                        temp[i,j] = state["VIDE"]
                        manger += 1
                
                elif (i == 0) & (etat[NbL -1,j] == state["PREDATEUR"]):
                    temp[i,j] = state["VIDE"]
                    manger += 1
                        
                elif (j == 0) & (etat[i,NbC -1] == state["PREDATEUR"]):
                    temp[i,j] = state["VIDE"]
                    manger += 1
                    
                elif (i == NbL - 1) & (etat[0,j] == state["PREDATEUR"]):
                    temp[i,j] = state["VIDE"]
                    manger += 1
                    
                elif (j == NbC - 1) & (etat[i,0] == state["PREDATEUR"]):
                    temp[i,j] = state["VIDE"]
                    manger += 1
                        
    if manger != 0:
        print("PROIE(S) CHASSEE(S)")
        print("Le(s) prédateur(s) ont consommé",manger, "proie(s)")
            
    etat = temp.copy() # mise à jour de l'état courant

#Fonction qui provoque la diminition des effectifs des deux populations avec 
#les équations de Lokta-Volterre
#Principe: Les coefficients liés à au deces seront multipliés par une valeur
#arbitraire mais permettant une réelle diminution des populations
#Cas: Présence de l'espèce intermédiaire
def mort1(NbL,NbC):
    global etat, t, alpha_LV, beta_LV, delta_LV, gamma_LV
    temp = etat.copy()  # sauvegarde de l'état courant
    print("PHASE MORT")
    p,q,r = 0,0,0
    eff_proie, eff_intermediaire, eff_predateur = 0,0,0
    for i in range(NbL):
        for j in range(NbC):
            if etat[i,j] == state["PROIE"]:
                eff_proie += 1
            if etat[i,j] == state["INTERMEDIAIRE"]:
                eff_intermediaire += 1
            if etat[i,j] == state["PREDATEUR"]:
                eff_predateur += 1
    
    z01 = [eff_proie,eff_intermediaire]
    z02 = [eff_intermediaire, eff_predateur]
    z03 = [eff_proie,eff_predateur]
   
#Résolution de des équations du modèle Lokta Volterra avec les nouvelles
#effectifs de population
    res = odeint(Lokta_Volterra,z01,t,args=(alpha_LV,beta_LV/6,delta_LV,gamma_LV/3))
    tabPro1,tabInt1 = res.T
    res =  odeint(Lokta_Volterra,z02,t,args=(alpha_LV,beta_LV/6,delta_LV,gamma_LV/3))
    tabInt2, tabPred1 = res.T
    res =  odeint(Lokta_Volterra,z03,t,args=(alpha_LV,beta_LV/6,delta_LV,gamma_LV/3))
    tabPro2,tabPred2 = res.T
                

    Delta_Proie = int(tabPro1[1] + tabPro2[1]) - int(tabPro1[0] + tabPro2[0])
    Delta_Intermediaire = ( int(tabInt1[1]) + int(tabInt2[1]) ) \
        - (int( tabInt1[0]) + int(tabInt2[0]) )
    Delta_Predateur = int(tabPred1[1] + tabPred2[1]) - int(tabPred1[0] + tabPred2[0])

#Dans le cas où le delta est positif
    if (Delta_Proie > 0):
        print("Pas de mort(s) parmi la ou les proie(s)")
        
    if (Delta_Intermediaire > 0):
        print("Pas de mort(s) parmi l'espèce intermédiaire'")
        
    if (Delta_Predateur > 0):
        print("Pas de mort(s) parmi la ou les prédéteur(s)")

    if (Delta_Proie <= 0):
        Delta_Proie = abs(Delta_Proie)
        print("Il y a",Delta_Proie,"décès parmi les proies")
        for i in range(NbL):
            for j in range(NbC):
#Répartition du ou des deces parmi les proies
                if etat[i,j] == state["PROIE"]:
                    if (q != Delta_Proie):
                        temp[i,j] = state["VIDE"]  
                        q += 1
                    
    if (Delta_Intermediaire <= 0):
        Delta_Intermediaire = abs(Delta_Intermediaire)
        print("Il y a",Delta_Intermediaire,"décès parmi l'espèce intermédiaire")
        for i in range(NbL):
            for j in range(NbC):
#Répartition du ou des deces parmi l'espèce intermédiaire 
                if etat[i,j] == state["INTERMEDIAIRE"]:
                    if (r != Delta_Intermediaire):
                        temp[i,j] = state["VIDE"]  
                        r += 1

    if (Delta_Predateur <= 0):
        Delta_Predateur = abs(Delta_Predateur)
        print("Il y a",Delta_Predateur,"décès parmi les prédateurs")
        for i in range(NbL):
            for j in range(NbC):
#Répartition du ou des deces parmi les prédateurs
                if etat[i,j] == state["PREDATEUR"]:
                    if (p != Delta_Predateur):
                        temp[i,j] = state["VIDE"]  
                        p += 1
                        
    etat = temp.copy() # mise à jour de l'état courant

#Cas: Absence de l'espèce intermédiaire
def mort2(NbL,NbC):
    global etat, t, alpha_LV, beta_LV, delta_LV, gamma_LV
    temp = etat.copy()  # sauvegarde de l'état courant
    print("PHASE MORT")
    p,q = 0,0 
    eff_proie, eff_predateur = 0,0
    for i in range(NbL):
        for j in range(NbC):
            if etat[i,j] == state["PROIE"]:
                eff_proie += 1
            if etat[i,j] == state["PREDATEUR"]:
                eff_predateur += 1
    
    z0 = [eff_proie,eff_predateur]
   
#Résolution de des équations du modèle Lokta Volterra avec les nouvelles
#effectifs de population
    res = odeint(Lokta_Volterra,z0,t,args=(alpha_LV/3,beta_LV,delta_LV/6,gamma_LV))
    tabPro,tabPred = res.T 
                

    Delta_Proie = int(tabPro[1]) - int(tabPro[0])
    Delta_Predateur = int(tabPred[1]) - int(tabPred[0])

#Dans le cas, où l'une des deux différences est positif
    if (Delta_Proie > 0):
        print("Pas de mort(s) parmi la ou les proie(s)")
        
    if (Delta_Predateur > 0):
        print("Pas de mort(s) parmi la ou les prédéteur(s)")

    if (Delta_Proie <= 0):
        Delta_Proie = abs(Delta_Proie)
        print("Il y a",Delta_Proie,"décès parmi les proies")
        for i in range(NbL):
            for j in range(NbC):
#Répartition  du ou des deces parmi les proies
                if etat[i,j] == state["PROIE"]:
                    if (p != Delta_Proie):
                        temp[i,j] = state["VIDE"]  
                        p += 1
                    
    if (Delta_Predateur <= 0):
        Delta_Predateur = abs(Delta_Predateur)
        print("Il y a",Delta_Predateur,"décès parmi les prédateurs")
        for i in range(NbL):
            for j in range(NbC):
#Répartition du ou des deces parmi les prédateurs
                if etat[i,j] == state["PREDATEUR"]:
                    if (q != Delta_Predateur):
                        temp[i,j] = state["VIDE"]  
                        q += 1
    etat = temp.copy() # mise à jour de l'état courant

#Donne à chaque pas un évènement à "déclencher
def phase(NbL,NbC,Nbpas):
    global  T, fenetre, presence_intermediaire
    
    if presence_intermediaire == True:
    
        chasse1(NbL, NbC, Nbpas)
    
        if Nbpas == T:
            print("Simulation terminée")
            fenetre.destroy()
        
        if Nbpas % 4 == 0:
            deplacement_predateur1(NbL, NbC)
    
        if Nbpas % 3 == 0:
            deplacement_intermediaire(NbL, NbC)
    
        if Nbpas % 2 == 0:
            deplacement_proie1(NbL, NbC)
    
        elif Nbpas % 5 == 0:
            reproduction1(NbL,NbC)
    
        else:
            mort1(NbL, NbC)
    
    elif presence_intermediaire == False:
        
        chasse2(NbL, NbC, Nbpas)
    
        if Nbpas == T:
            print("Simulation terminée")
            fenetre.destroy()
        
        elif Nbpas % 5 == 0:
            reproduction2(NbL,NbC)
            
        elif Nbpas % 3 == 0:
            deplacement_predateur2(NbL, NbC)            
        
        elif Nbpas % 2 == 0:
            deplacement_proie2(NbL, NbC)
    
        else:
            mort2(NbL, NbC)

       
    else:
        print("ERREUR")
        fenetre.destroy()
    
# Calculer et dessiner les pas
def iterer(NbL,NbC,Nbpas):
    phase(NbL,NbC,Nbpas)        
    draw(NbL,NbC)

# Animation pas à pas
def pasapas():
    global Nbpas,NbL,NbC
    iterer(NbL,NbC,Nbpas) 
    Nbpas += 1

#Programme
# Définition de l'interface graphique
fenetre = Tk()
fenetre.title("Système écologique proie-prédateur")
canvas = Canvas(fenetre, width=taille*NbC+1, height=taille*NbL+1, highlightthickness=0)
fenetre.wm_attributes("-topmost", True)

# Condition pour déclencher la mise en place des obstacles par l'utilisateur
if presence_obstacle == True:
    canvas.bind("<Button-1>", obstacle)
canvas.pack()

# Définition des boutons de commande
bou1 = Button(fenetre,text='Quitter', width=8, command=fenetre.destroy)
bou1.pack(side=RIGHT)
bou2 = Button(fenetre, text='Pas', width=8, command=pasapas)
bou2.pack(side=LEFT)

# lancement de l'automate
Initialisation_Automate(presence_intermediaire, presence_obstacle)
fenetre.mainloop()