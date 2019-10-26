from tkinter import *
import os
import shutil
import webbrowser

######################################################################################################################################################################
######################################################### MA BIBLIOTHEQUE VIRTUELLE #################################################################################
######################################################################################################################################################################


############## Classe pour faire un PLACEHOLDER (ce n'est pas moi qui l'ai faite ) #####################################################################

class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


########## Ouverture des fenetres #####################################################################################################################@


def ouvertureDeFenetre(bibli, tk = True, titreDeFenetre = "Ma Bibliothèque Virtuelle.", fenetreDappel = "" ):
    ''' Fonction qui ouvre une fenêtre de la bibliothèque virtuelle '''


    global bibliotheque
    global toutLesMots

    if tk == True : # si c'est la fenetre principale
        fenetre = Tk()
        chargementDesDonnees(bibliotheque, toutLesMots)
    else :
        fenetreDappel.destroy()
        fenetre = Toplevel()
        fenetre.grab_set() #on ne peut appuyer sur les boutons que de la derniere fenetre ouverte


    fenetre.resizable(0, 0) #empécher la fenetre de changer de taille

    label = Label(fenetre, text= titreDeFenetre)
    label.pack()

    textLivre = Label(fenetre, text="?")
    textLivre.pack()

    biblioImage = PhotoImage(file="image/biblio.gif")

    canvas = Canvas(fenetre,width=615, height=500)
    canvas.pack()

    boutonCreer=Button(fenetre, text="Créer un livre/sous-bibliothèque", command = lambda: createBook(bibli), cursor = 'question_arrow')
    boutonCreer.pack(side=RIGHT)

    boutonSave=Button(fenetre, text="Sauvegarder/actualiser", command = lambda: save(fenetre, bibli,canvas, textLivre, livreImage, sousBibliImage, listeDeLivreBouton), cursor = 'question_arrow')
    boutonSave.pack(side=LEFT)

    boutonTrie=Button(fenetre, text="Trier les livres", command = lambda: TriBook(bibli), cursor = 'question_arrow')
    boutonTrie.pack(side=RIGHT)


    boutonResearch=Button(fenetre, text="Rechercher un livre", command = lambda: ResearchBook(toutLesMots), cursor = 'question_arrow')
    boutonResearch.pack(side=LEFT)

    canvas.create_image(10, 10, anchor=NW, image=biblioImage)

    livreImage = PhotoImage(file="image/livre.gif")
    sousBibliImage = PhotoImage(file="image/sousBibli.gif")

    listeDeLivreBouton = [] #liste pour stocker les boutons qui contiennent les livres

    actualisation(fenetre, bibli,canvas, textLivre, livreImage, sousBibliImage, listeDeLivreBouton)

    fenetre.mainloop()



##################### charger les données à l'ouverture de la bibliothèque ########################################################################@


def chargementDesDonnees(bibli,toutLesMots,file = '/', cheminBibli = '' ):
    ''' Fonction recursive qui lit tout ce qu'il ya dans le fichier bibliotheque et créer les livres en fonction '''

    fileCopy = file

    for livreOuSousBibli in os.listdir('bibliotheque' + file) :

        if os.path.isdir('bibliotheque' + file + livreOuSousBibli): # un sous dossier éuivaut à une sous-bibliotheque
            creationDeSousBibli(bibli, livreOuSousBibli[:-3], int(livreOuSousBibli[-3:]))
            file +=  livreOuSousBibli + '/'
            chargementDesDonnees(bibli[livreOuSousBibli[:-3]], toutLesMots,  file = file)
        else :
            if livreOuSousBibli != '.DS_Store' : # fichier caché sur mac qui est lu par 'listDir' et qui m'a fait perdre de nombreuses heures pour trouver le problème
                f = open('bibliotheque' + file + livreOuSousBibli, 'r')
                #print(livreOuSousBibli)
                lignes  = f.readlines()
                texteDuResume = lignes[7]
                for i in range(len(lignes)) :
                    if i > 7 :
                        texteDuResume += lignes[i]

                creationDeLivre(bibli, lignes[0][:-1], lignes[1][:-1], int(lignes[6][:-1]) ,annee = lignes[2][:-1], resume = texteDuResume, lienTexte =lignes[3][:-1], avis =lignes[4][:-1], note =lignes[5][:-1])
                ensembleDesMots = " ".join(lignes)
                ensembleDesMots = ensembleDesMots.replace('\n', '')
                ensembleDesMots = ensembleDesMots.split(' ')
                for mot in ensembleDesMots :
                    toutLesMots.append(mot)
                f.close()
                # les [-1] enlève les sauts de lignes
        file = fileCopy




def creationDeLivre(bibli, titre, auteur, position, fenetre = 'pas de fenetre' , annee = "?", resume ="?" , lienTexte ="?", avis ="?", note ="?") :
    ''' Fonction qui créé un livre (mais pas graphiquement) dans la bibliothèque. '''

    bibli[titre] = {"Titre" : titre, "Auteur" : auteur, "Année de publication" : annee, "Résumé" : resume, "Texte" : lienTexte, "Avis" : avis, "Note" : note, "Position"  : position}
    if fenetre != "pas de fenetre" : # si cette fonction a été appellé à partir d'une fenetre secondaire on ferme cette fenetre
        fenetre.destroy()

def creationDeSousBibli(bibli, titre, position, fenetre = 'pas de fenetre' ) :
    ''' Fonction qui crée une sous-bibliothèque (mais pas graphiquement) dans la bibliothèque. '''

    bibli[titre] = {"Titre" : titre, "Position"  : position}
    if fenetre != "pas de fenetre" :
        fenetre.destroy()

############################################ Ensemble des fonctions pour créer les livres et les sous-biblis   #################################################


def createBook(bibli):
    ''' Fonction qui renvoie vers d'autre fonction en fonction du choix de l'utilisateur pour créer un livre ou une sous-bibliothèque'''

    fenetre = Toplevel()
    fenetre.grab_set() #on ne peut appuyer sur les boutons que de la derniere fenetre ouverte
    fenetre.resizable(0, 0) #empécher la fenetre de changer de taille

    valueRadio = StringVar()
    boutonRadioBook = Radiobutton(fenetre, text="Créer un livre", variable=valueRadio, value='1',command = lambda: createBook_book(bibli, fenetre, boutonRadioBook, boutonRadioBibli))
    boutonRadioBibli = Radiobutton(fenetre, text="Créer une sous-bibliothèque",variable=valueRadio , value='2', command = lambda: createBook_bibli(bibli, fenetre, boutonRadioBook, boutonRadioBibli))
    boutonRadioBook.pack()
    boutonRadioBibli.pack()


def createBook_book(bibli, fenetre, boutonRadioBook, boutonRadioBibli):
    '''Fonction qui prend les choix de l'utilisateur et renvoie vers la création du livre'''

    boutonRadioBook['state'] = 'disabled'
    boutonRadioBibli['state'] = 'disabled'

    placeholderTitre = EntryWithPlaceholder(fenetre, "Titre : (obligatoire) ")
    placeholderAuteur = EntryWithPlaceholder(fenetre, "Auteur : (obligatoire) ")
    placeholderAnnee = EntryWithPlaceholder(fenetre, "Année de publication :")
    placeholderLienTexte = EntryWithPlaceholder(fenetre, "Texte complet :")
    placeholderNote = EntryWithPlaceholder(fenetre, "Note :")
    placeholderAvis = EntryWithPlaceholder(fenetre, "Avis :")

    textPosition = Label(fenetre, text="Position dans la bibliothèque :")
    spinBoxPosition = Spinbox(fenetre, from_= 1, to=53)


    placeholderResume = Text(fenetre, height = "4", padx = 10, pady = 10, highlightbackground = 'grey')
    placeholderResume.insert(INSERT, "Résumé : ")

    placeholderTitre.pack()
    placeholderAuteur.pack()
    placeholderAnnee.pack()
    placeholderLienTexte.pack()
    placeholderNote.pack()
    placeholderAvis.pack()
    placeholderResume.pack()
    textPosition.pack()
    spinBoxPosition.pack()

    boutonCreer=Button(fenetre, text="Créer un livre", command = lambda:  creationDeLivre(bibli, placeholderTitre.get(), placeholderAuteur.get(), int(spinBoxPosition.get()), fenetre ,placeholderAnnee.get(), placeholderResume.get("1.0",END),placeholderLienTexte.get(), placeholderAvis.get(), placeholderNote.get())
, cursor = 'question_arrow')
    boutonCreer.pack()

def createBook_bibli(bibli, fenetre, boutonRadioBook, boutonRadioBibli):
    '''Fonction qui prend les choix de l'utilisateur et renvoie vers la création d'une sous-bibliothèque'''


    boutonRadioBook['state'] = 'disabled'
    boutonRadioBibli['state'] = 'disabled'

    placeholderTitre = EntryWithPlaceholder(fenetre, "Nom :")
    textPosition = Label(fenetre, text="Position dans la bibliothèque :")
    spinBoxPosition = Spinbox(fenetre, from_= 100, to=107)

    placeholderTitre.pack()
    textPosition.pack()
    spinBoxPosition.pack()

    boutonCreer=Button(fenetre, text="Créer une sous-bibliotheque", command = lambda: creationDeSousBibli(bibli, placeholderTitre.get(), int(spinBoxPosition.get()), fenetre = fenetre), cursor = 'question_arrow')
    boutonCreer.pack()


############################################ Ensemble des fonctions pour faire et actualiser l'interface graphique et sauvegarder les données #################################################


def save(fenetre,bibli,canvas, textLivre, livreImage,sousBibliImage, listeDeLivreBouton):
    ''' Fonction qui sauvegarde les données'''

    textLivre.config(text = "Données sauvegardées, interface graphique actualisée.")
    actualisation(fenetre, bibli,canvas, textLivre, livreImage,sousBibliImage, listeDeLivreBouton)

    shutil.rmtree('bibliotheque')
    os.mkdir('bibliotheque')

    global bibliotheque
    creationDeFichierLivreOuDeDossierSousBibli(bibliotheque)

###  faire et actualiser l'interface graphique  ###

def actualisation(fenetre, bibli,canvas, textLivre, livreImage, sousBibliImage, listeDeLivreBouton):
    '''Actualise l'interface graphique '''


    x = 60
    y = 100

    for livreBouton in listeDeLivreBouton :
        livreBouton[1].destroy()


    for livre in bibli.keys() :

        if type(bibli[livre]) == type(bibli) : # ne considère pas ce qui n'est pas des dictionnnaires comme des livres

            if bibli[livre]['Position'] <17 :
                createButtonBook(bibli,fenetre, livreImage, canvas, x + (bibli[livre]['Position']-1)*49/2 ,y, bibli[livre], textLivre, listeDeLivreBouton )
            elif bibli[livre]['Position'] >=17 and bibli[livre]['Position'] <38 :
                createButtonBook(bibli,fenetre, livreImage, canvas, x + (bibli[livre]['Position']-17)*49/2 ,y +160, bibli[livre], textLivre, listeDeLivreBouton )
            elif bibli[livre]['Position'] >=38 and bibli[livre]['Position'] <54 :
                createButtonBook(bibli,fenetre, livreImage, canvas, x + (bibli[livre]['Position']-38)*49/2 + 4*49/2 + 37  ,y + 320, bibli[livre], textLivre, listeDeLivreBouton  )
            elif bibli[livre]['Position'] >=100 and bibli[livre]['Position'] <104 :
                createButtonBook(bibli,fenetre, sousBibliImage, canvas, x + (bibli[livre]['Position']-100)*49/2 + 16*49/2 + 41  ,y, bibli[livre], textLivre, listeDeLivreBouton )
            elif bibli[livre]['Position'] >=104 and bibli[livre]['Position'] <108 :
                createButtonBook(bibli,fenetre, sousBibliImage, canvas, x + (bibli[livre]['Position']-104)*22  ,y + 320, bibli[livre], textLivre, listeDeLivreBouton  )


def createButtonBook(bibli, fenetre, image, canvas, x, y, livre, textLivre, listeDeLivreBouton ) :
    ''' Fonction qui créer graphiquement des boutons sous la forme de livre qui sont consultable en cliquant dessus, en passant dessus le texte de la fenêtre se modifie'''

    bouton=Button(fenetre, text="consulter", command = lambda: consulterLivre(bibli, livre), cursor = 'question_arrow')


    bouton.bind("<Enter>", lambda event : hoverBook(livre, textLivre))
    bouton.bind("<Leave>", lambda event : quitHoverBook(textLivre))
    bouton.config(image=image,width="25",height="100")
    canvas.create_window(x, y ,window=bouton)
    listeDeLivreBouton.append([livre,bouton])


def hoverBook(livre, textLivre):
    ''' Fonction qui change le texte de la fenetre et affiche le nom d'un livre'''

    if livre['Position']<100 :
        texte = livre['Titre'] + ' (livre) '
    else :
        texte = livre['Titre'] + ' (sous-bibliothèque) '

    textLivre.config(text = texte)


def quitHoverBook(textLivre):
    ''' Fonction qui change le texte de la fenetre et affiche '?' '''
    textLivre.config(text = '?')



### sauvegarder les données ###



def creationDeFichierLivreOuDeDossierSousBibli(bibli, file = '') :
    '''Fonction recursive qui apelle les fonctions correspondantes pour sauvegarder tout les livres et sousBibli '''

    fileCopy = file
    for livreOuSousBibli in bibli :

        if type(bibli[livreOuSousBibli]) == type(bibli) :
            # ne considère pas ce qui n'est pas des dictionnnaires comme des livres

            if int(bibli[livreOuSousBibli]['Position']) < 100 :
                creationDeFichierLivre(bibli[livreOuSousBibli], file )
            else :
                creationDeDossierSousBibli( bibli[livreOuSousBibli], file )
                file += livreOuSousBibli + str(bibli[livreOuSousBibli]['Position']) + '/'
                creationDeFichierLivreOuDeDossierSousBibli(bibli[livreOuSousBibli], file)
            file = fileCopy


def creationDeFichierLivre(livre, file ) :
    ''' Créer un fichier txt qui représentele livre '''

    fichier = open( 'bibliotheque/' + file + livre['Titre'] + '.txt' , "w")
    fichier.write(livre['Titre'] + '\n')
    fichier.write(livre['Auteur']+ '\n')
    fichier.write(livre['Année de publication']+ '\n')
    fichier.write(livre['Texte']+ '\n')
    fichier.write(livre['Avis']+ '\n')
    fichier.write(livre['Note']+ '\n')
    fichier.write(str(livre['Position'])+ '\n')
    fichier.write(livre['Résumé']+ '\n')
    fichier.close()

def creationDeDossierSousBibli( sousBibli, file) :
    ''' Créer un dossier qui représente la sous bibli'''

    os.mkdir('bibliotheque/'+ file + sousBibli['Titre'] + str(sousBibli['Position']))



####################################################  Fonction pour trier les livre ###############################################################

def TriBook(bibli):
    ''' Fonction qui ouvre la fenetre pour faire le tri des livres et demander le critère de tri '''


    fenetre = Toplevel()
    fenetre.grab_set() #on ne peut appuyer sur les boutons que de la derniere fenetre ouverte
    fenetre.resizable(0, 0) #empécher la fenetre de changer de taille

    textTri = Label(fenetre, text="Trier les livres par : ")
    textTri.pack()

    choices = Variable(fenetre, ('Titre', 'Auteur', 'Année de publication'))
    listbox = Listbox(fenetre, listvariable=choices, selectmode="browse")
    listbox.insert('end', 'Note')
    label = Label(fenetre, text='')

    listbox.bind('<<ListboxSelect>>', lambda event :show_selection(label, choices, listbox))


    button = Button(fenetre, text='Ok', command = lambda: tri(fenetre, bibli, label.cget("text") ))

    listbox.pack()
    label.pack()
    button.pack()

def show_selection(label, choices, listbox):
    ''' change le texte pour montrer le choix de l'utilisateur '''
    choices = choices.get()
    text = ""
    for index in listbox.curselection():
        text += choices[index]

    label.config(text=text)



def tri(fenetre, conteneurDeslivres, critere) :
    ''' Fonction qui trie les livres selon un critère '''
    liste = []

    for critereDuLivre, livre in conteneurDeslivres.items():

        if type(conteneurDeslivres[critereDuLivre]) == type(conteneurDeslivres) : # ne considère pas ce qui n'est pas des dictionnnaires comme des livres
            if livre["Position"]<100:
                liste.append(livre[critere])
    liste.sort()


    for i in range(len(liste)):
        compteur = 0 #compte le nombre de livre livre qui ont la même valeur pour le critere donné
        for critereDuLivre, livre in conteneurDeslivres.items():
            if type(conteneurDeslivres[critereDuLivre]) == type(conteneurDeslivres) : # ne considère pas ce qui n'est pas des dictionnnaires comme des livres
                if livre["Position"]<100:
                    if liste[i] == livre[critere] :
                        livre["Position"] = i+1 - compteur # pour éviter de superposer les livres pendant le tri
                        compteur += 1


    fenetre.destroy()


####################################################  Fonction pour faire la recherche de livre à partir d'un mot ###############################################################


def ResearchBook(toutLesMots):
    ''' Fonction qui créé fenêtre pour rechercher un livre à partir d'un mot'''

    FreqtoutLesMots = frequenceMot(toutLesMots)

    fenetre = Toplevel()
    fenetre.grab_set() #on ne peut appuyer sur les boutons que de la derniere fenetre ouverte
    fenetre.resizable(0, 0) #empécher la fenetre de changer de taille

    textResearch = Label(fenetre, text="Rechercher un/des livre(s) à partir du mot suivant :")
    textResearch.pack()

    vplaceholderMot = StringVar()
    placeholderMot = Entry(fenetre, textvariable= vplaceholderMot)
    placeholderMot.pack()

    vplaceholderMot.trace("w", lambda name, index, mode, vplaceholderMot=vplaceholderMot: autoCompletion(devineMot, list(FreqtoutLesMots), placeholderMot))

    mot = list(FreqtoutLesMots)[0][0]

    devineMot = Button(fenetre, text='proposition : ' + mot , command = lambda: changeMot(vplaceholderMot, devineMot.cget("text")) )
    devineMot.pack()

    global bibliotheque
    listText= []
    button = Button(fenetre, text='Rechercher', command = lambda: Recherche(bibliotheque,placeholderMot.get(),fenetre, listText) )
    button.pack()

    quelLivre = Label(fenetre, text = 'Ce mot est présent dans le(s) livre(s) suivant(s) :')
    quelLivre.pack()


def frequenceMot(liste):
    '''Fonction qui prend en entrée un texte et retourne les mots uniques et leur fréquence'''
    frequences = []

    for mot_liste in liste:
        frequences.append((mot_liste,liste.count(mot_liste)))
    return set(frequences)


def autoCompletion(devineMot, listFreqMot, placeholderMot ):
    ''' Fonction qui prend un ensemble de mot avec leur fréquence et fait un système d'autocomplétion avec'''

    mot = listFreqMot[0][0] #le premier mot
    listeSelectionFreq = [0] #sa fréquence associée
    listeSelectionMot = [' ']# pour pas que la liste soit vide

    if len(placeholderMot.get())>2 : #si on a commencé à écrire plus de 3 lettre :
        for i in range (len(listFreqMot)) :
            if len(listFreqMot[i][0])> len(placeholderMot.get()) : # ne regarde dans la liste de mot des des livres que ceux dont le nombre de lettres est supérieur à l'entrée
                compteur = 0
                for numeroLettre in range(len(placeholderMot.get())) :
                    if placeholderMot.get()[numeroLettre] == listFreqMot[i][0][numeroLettre] : #à chaque lettres rentrés qui  correspondent à celles d'un mot du livre
                        compteur += 1
                if compteur == len(placeholderMot.get()) : #si toute les lettres correspondent on met le mot dans une liste et sa fréquence dans une autre
                    listeSelectionMot.append(listFreqMot[i][0])
                    listeSelectionFreq.append(int(listFreqMot[i][1]))

        mot = listeSelectionMot[listeSelectionFreq.index(max(listeSelectionFreq))] #on prend le mot qui correspond et qui a la plus grande fréquence


    devineMot.config(text= 'proposition : ' + mot  ) #on propose le mot en l'affichant


def changeMot(vplaceholderMot, mot) :
    ''' Change le mot à rechercher avec le mot proposer par l'autocompletion'''
    vplaceholderMot.set(mot[14:])

def Recherche(bibli, motARechercher, fenetre,  listText, file = '/', fileName = '/', premiereRecurrence = True) :
    ''' Fonction recursive qui recherche des livres selon un mot'''

    if premiereRecurrence == True : # pour ne pas que ça se lance lors de la récursion
        for texteACacher in listText :
            texteACacher.pack_forget() #efface les précédents résultats affichés par la fonction de recherche si elle a été lancé précedemment

    fileCopy = file #on sauvegarde le chemin de départ
    fileNameCopy = fileName #on sauvegarde le chemin de départ

    for livreOuSousBibli in os.listdir('bibliotheque' + file) :

        if os.path.isdir('bibliotheque' + file + livreOuSousBibli): # un sous dossier équivaut à une sous-bibliotheque
            file +=  livreOuSousBibli + '/' # on modifie le lien
            fileName +=  livreOuSousBibli[:-3] + '/' # on modifie le lien (-3 pour enlever le nombre qui correspond à la position
            # d'une sous-bibliothèque et qui est à la fin du nom du dossier représentnat la sous-bibli)
            Recherche(bibli[livreOuSousBibli[:-3]], motARechercher, fenetre,  listText,  file = file, fileName = fileName, premiereRecurrence = False) # on lance la récursion pour le faire aussi pour les livres dans la sous-bibli
        else :
            if livreOuSousBibli != '.DS_Store' : # fichier caché sur mac qui est lu par 'listDir' et qui m'a fait perdre de nombreuses heures pour trouver le problème
                f = open('bibliotheque' + file + livreOuSousBibli, 'r') #on ouvre un fichier txt correspondant à un livre
                lignes  = f.readlines()
                ensembleDesMots = " ".join(lignes)
                ensembleDesMots = ensembleDesMots.replace('\n', '')
                ensembleDesMots = ensembleDesMots.split(' ') # on créer ainsi une liste qui contient tout les mots de tout les livres de la bibliothèques
                pasDeuxFois = True
                for mot in ensembleDesMots : #pour chaque mot :
                    if mot == motARechercher and pasDeuxFois == True :
                        # on vérifie si c'est le mot qu'on souhaite rechercher,( pas deux fois permet que si le même livre contient plusieurs fois le mot à rechercher, il ne s'affiche qu'une fois)
                        pasDeuxFois = False
                        textAffiche = Label(fenetre, text = 'bibliotheque' + fileName + livreOuSousBibli[:-4]) #le -4 sert à enlever le .txt du fichier qui représente le livre
                        textAffiche.pack() #affiche le chemin du livre qui contient le le mot souhaité
                        listText.append(textAffiche) #stocke les labels affichés pour pouvoir les supprimer par la suite


                f.close()
        file = fileCopy #on réinitialise pour le prochaiin livre en redonnant le chemin de depart
        fileName = fileNameCopy #on réinitialise pour le prochaiin livre en redonnant le chemin de depart





####################################################  Fonction lié à la consultation d'un livre (consultation,modification, destruction...) ###############################################################



def consulterLivre(bibli,livre) :
    ''' Fonction qui montre la fiche de lecture du livre.'''


    if livre['Position'] <100 :

        fenetre = Toplevel()
        fenetre.grab_set() #on ne peut appuyer sur les boutons que de la derniere fenetre ouverte
        fenetre.resizable(0, 0) #empécher la fenetre de changer de taille

        placeholderTitre = EntryWithPlaceholder(fenetre, livre['Titre'])
        placeholderAuteur = EntryWithPlaceholder(fenetre, livre['Auteur'])
        spinBoxValues = StringVar()
        spinBoxPosition = Spinbox(fenetre, from_= 1, to=53, textvariable= spinBoxValues)
        spinBoxValues.set(int(livre['Position']))
        placeholderAnnee = EntryWithPlaceholder(fenetre, livre['Année de publication'])
        placeholderLienTexte = EntryWithPlaceholder(fenetre, livre['Texte'])

        placeholderNote = EntryWithPlaceholder(fenetre, livre['Note'])
        placeholderAvis = EntryWithPlaceholder(fenetre, livre['Avis'])

        placeholderResume = Text(fenetre, height = "4", padx = 10, pady = 10, highlightbackground = 'grey')
        placeholderResume.insert(INSERT,livre['Résumé'])

        labelTitre = Label(fenetre, text='Titre :')
        labelAuteur = Label(fenetre, text='Auteur :')
        labelPosition = Label(fenetre, text="Position dans la bibliothèque :")
        labelAnnee = Label(fenetre, text='Année :')

        labelLienTexte = Label(fenetre, text='Lien du texte :')
        labelNote = Label(fenetre, text='Note :')
        labelAvis = Label(fenetre, text='Avis :')
        labelResume = Label(fenetre, text='Résumé :')

        labelTitre.grid(row=1,column=1)
        placeholderTitre.grid(row=1,column=2)
        labelAuteur.grid(row=2,column=1)
        placeholderAuteur.grid(row=2,column=2)

        labelAnnee.grid(row=3,column=1)
        placeholderAnnee.grid(row=3,column=2)
        labelLienTexte.grid(row=4,column=1)
        placeholderLienTexte.grid(row=4,column=2)
        labelNote.grid(row=5,column=1)
        placeholderNote.grid(row=5,column=2)
        labelAvis.grid(row=6,column=1)
        placeholderAvis.grid(row=6,column=2)
        labelResume.grid(row=7,column=1)
        placeholderResume.grid(row=7,column=2)

        labelPosition.grid(row=8,column=1)
        spinBoxPosition.grid(row=8,column=2)

        boutonTexteComplet=Button(fenetre, text="Voir le texte complet (si case 'lien du texte' remplit)", cursor = 'question_arrow', command = lambda: texteComplet(placeholderLienTexte.get()))
        boutonModify=Button(fenetre, text="Modifier", cursor = 'question_arrow', command = lambda: ModifyBook(fenetre, livre, {"Titre" : placeholderTitre.get(), "Auteur" : placeholderAuteur.get(), "Année de publication" : placeholderAnnee.get(), "Résumé" : placeholderResume.get("1.0",END), "Texte" : placeholderLienTexte.get(), "Avis" : placeholderAvis.get(), "Note" : placeholderNote.get(), "Position"  : spinBoxPosition.get()}) )
        boutonDestroy=Button(fenetre, text="Détruire", cursor = 'question_arrow',command = lambda: destruction(bibli,livre['Titre'], fenetre = fenetre))

        boutonTexteComplet.grid(row=11,column=2)
        boutonModify.grid(row=12,column=2)
        boutonDestroy.grid(row=13,column=2)


    else :

        fenetre = Toplevel()
        fenetre.grab_set() #on ne peut appuyer sur les boutons que de la derniere fenetre ouverte
        fenetre.resizable(0, 0) #empécher la fenetre de changer de taille

        placeholderTitre = EntryWithPlaceholder(fenetre, livre['Titre'])
        spinBoxValues = StringVar()
        spinBoxPosition = Spinbox(fenetre, from_= 100, to=107, textvariable= spinBoxValues)
        spinBoxValues.set(int(livre['Position']))

        labelTitre = Label(fenetre, text='Titre :')
        labelPosition = Label(fenetre, text='Position dans la bibliothèque :')

        labelTitre.grid(row=1,column=1)
        placeholderTitre.grid(row=1,column=2)
        labelPosition.grid(row=2,column=1)
        spinBoxPosition.grid(row=2,column=2)

        boutonRentrer=Button(fenetre, text="Rentrer dans la sous-bibliothèque", cursor = 'question_arrow',  command = lambda: ouvertureDeFenetre(livre, tk = False, titreDeFenetre = livre['Titre'], fenetreDappel = fenetre))
        boutonModify=Button(fenetre, text="Modifier", cursor = 'question_arrow', command = lambda: ModifyBook(fenetre, livre, {"Titre" : placeholderTitre.get(), "Position" : spinBoxPosition.get()}) )
        boutonDestroy=Button(fenetre, text="Détruire", cursor = 'question_arrow',command = lambda: destruction(bibli,livre['Titre'], fenetre = fenetre))

        boutonRentrer.grid(row=3,column=2)
        boutonModify.grid(row=4,column=2)
        boutonDestroy.grid(row=5,column=2)


def texteComplet(url):
    ''' Ouvre le navigateur et ouvre une page avec l'url donné (ici permet de voir le texte complet d'un livre)  '''
    webbrowser.open(url)


def ModifyBook(fenetre, livre, dicValeurEntree):
    ''' Fonction qui permet de modifier un livre '''

    if livre['Position'] <100 :

        livre['Titre'] = dicValeurEntree['Titre']
        livre['Position'] = int(dicValeurEntree['Position'])
        livre['Auteur'] = dicValeurEntree['Auteur']
        livre['Année de publication'] = dicValeurEntree['Année de publication']
        livre['Résumé'] = dicValeurEntree['Résumé']
        livre['Texte'] = dicValeurEntree['Texte']
        livre['Avis'] = dicValeurEntree['Avis']
        livre['Note'] = dicValeurEntree['Note']
    else :
        livre['Titre'] = dicValeurEntree['Titre']
        livre['Position'] = int(dicValeurEntree['Position'])

    fenetre.destroy()


def destruction(conteneurDuLivre,titreDulivre,fenetre = "pas de fenetre") :
    ''' Fonction qui détruit un livre.'''
    del conteneurDuLivre[titreDulivre]
    if fenetre != "pas de fenetre" :
        fenetre.destroy()



######################################################### lancement du programme #################################################################################

bibliotheque = {}
toutLesMots = []
ouvertureDeFenetre(bibliotheque)
