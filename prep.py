#-*- coding: utf-8 -*-
import spacy 
import csv
import unicodedata
import pandas as pd
import re 
import math 
import os,sys
import collections
import random
import numpy as np
import psutil
from sklearn import preprocessing
from collections import Counter
from collections import defaultdict
from gensim.corpora import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.matutils import sparse2full
from datetime import datetime


keywords = ['βήχας,βηχω,βηχεις,βηχει,βηχουμε,βηχετε,βηχουν,βηξω,βηξεις,βηξει,βηξουμε,βηξετε,βηξουν,εβηξα,εβηξες,εβηξε,βηξαμε,βηξατε,εβηξαν\
            ,βηχας,βηχα',\
            'γρίπη,γριπη,γριπης',\
            'Η1Ν1,Η1Ν1,H1N1',\
            'πυρετός,πυρετος,πυρετο,πυρετου,πυρετων,πυρετοι',\
            'άρρωστος,αρρωστος,αρρωστη,αρρωστο,αρρωστα,αρρωστοι,αρρωστια,αρρωστιες,αρρωστες,αρρωστησα,αρρωστησες,αρρωστησε,αρρωστησαμε,αρρωστησατε,αρρωστησαν,αρρωστου,αρρωστης,αρρωστου,αρρωστων',\
            'ντεπόν,ντεπον,ντεπόν',\
            'πνευμονία,πνευμονία,πνευμονιας,πνευμονιων',\
            'εμβόλιο,εμβολιο,εμβολια,εμβολιων,εμβολιου',\
            'πονόλαιμος,πονολαιμος,πονολαιμοι,πονολαιμο,πονολαιμου,πονολαιμων',\
            'πονοκέφαλος,πονοκεφαλος,πονοκεφαλοι,πονοκεφαλο,πονοκεφαλου,πονοκεφαλων',\
            'ρίγος,ριγος,ριγη,ριγους,ριγων',\
            'αντιβίωση,αντιβιωση,αντιβιωσης,αντιβιωσεις,αντιβιωσεων',\
            'εγώ,μου,εμενα,εγω,εμεις,εμας,μας'] # ισως χρειαζεται το "με", αλλα υπαρχει αμφισημια

keyword_dict = {}

categories = ['TEMP','HIGH','LOW','RAIN','SPEED','HIGH.1']

counties = ['Αττική','Κρήτη','Δυτικής Ελλάδας','Κεντρικής Μακεδονίας','Πελοποννήσου','Βόρειου Αιγαίου','Ηπείρου','Θεσσαλίας','Νοτίου Αιγαίου','Ανατολικής Μακεδονίας και Θράκης','Ιονίων Νήσων','Στερεάς Ελλάδας','Δυτικής Μακεδονίας']
geo_map = {'Αττική':'Αττική',\
           'Κρήτη':'Κρήτη',\
           'Δυτικής Ελλάδας':'Δυτικής Ελλάδας',\
           'Κεντρικής Μακεδονίας':'Κεντρικής Μακεδονίας',\
           'Πελοποννήσου':'Πελοππόνησος',\
           'Βόρειου Αιγαίου':'Βόρειο & Ανατολικό Αιγαίο',\
           'Ηπείρου':'Ήπειρος',\
           'Θεσσαλίας':'Θεσσαλίας',\
           'Νοτίου Αιγαίου':'Νοτίου Αιγαίου',\
           'Ανατολικής Μακεδονίας και Θράκης':'Θράκη',\
           'Ιονίων Νήσων':'Νησιά_Ιονίου',\
           'Στερεάς Ελλάδας':'Στερεάς Ελλάδας',\
           'Δυτικής Μακεδονίας':'Δίκτυο_Κοζάνης'}
months = ['Ιανουάριο','Φεβρουάριο','Μάρτιο','Απρίλιο','Μάιο','Ιούνιο','Ιούλιο','Αύγουστο','Σεπτέμβριο','Οκτώβριο','Νοέμβριο','Δεκέμβριο']

distribution = {'county':{},\
                'keyword':{}}
                
double_distribution = { 'Αττική':{},\
                        'Κρήτη':{},\
                        'Δυτικής Ελλάδας':{},\
                        'Κεντρικής Μακεδονίας':{},\
                        'Πελοποννήσου':{},\
                        'Βόρειου Αιγαίου':{},\
                        'Ηπείρου':{},\
                        'Θεσσαλίας':{},\
                        'Νοτίου Αιγαίου':{},\
                        'Ανατολικής Μακεδονίας και Θράκης':{},\
                        'Ιονίων Νήσων':{},\
                        'Στερεάς Ελλάδας':{},\
                        'Δυτικής Μακεδονίας':{}}   

        
stop_words = {'τούτου', 'ύστερα','ή', 'αλλοιώς', 'ειχατε', 'ετουτοι', 'μονάχα', 'μοναχα', 'τέτοιου', 'κάποιες', 'όσον', 'καθενός', 'οσουδήποτε', 'πιο', 'καμποσες', 'καλως', 'καμποσοι', 'ταύτη', 'τουλάχιστον', 'ποσην', 'αλλα', 'όπου', 'πρωτύτερα', 'καποιαν', 'αυτοί', 'δεξια',  'οτιδηποτε', 'αλλων', 'δηλαδή', 'αραγε', 'ήμασταν', 'έκαστος', 'τότε', 'τόσης', 'υπό', 'αλλου', 'λοιπόν', 'ου', 'αρκετες', 'μήπως', 'μερικών', 'πάνω', 'τελευταια', 'περυσι', 'εχτές', 'κάμποσος', 'μεμιας', 'αδιάκοπα', 'εκει', 'τουτες', 'εκείνοι', 'εκαστου', 'ποιού', 'γύρω', 'πόσους', 'έτερο', 'ε', 'πρώτος', 'μία', 'λιγότερο', 'συνεπώς', 'εσας', 'ίσια', 'διόλου', 'ειδεμη', 'τουλαχιστο', 'όσες', 'αυτου', 'λίγο', 'ετουτες', 'αλλοι', 'μπορεί', 'μεμιάς', 'όλους', 'μόνης', 'περιπου', 'δεξιά', 'γρήγορα', 'περί', 'πούθε', 'ήσουν', 'χωρίς', 'παρά', 'όλων', 'εκεινου', 'ετερον', 'τους', 'ακομη', 'οποιασδήποτε', 'εκαστο', 'καθως', 'εν', 'εκεινους', 'πολλοί', 'ετουτων', 'εκάστων', 'ποσους', 'τόσο', 'αυτην', 'τούτες', 'προπερσι', 'πουθε', 'ταύτος', 'οποιους', 'εναντιον', 'κατιτι', 'αυτά', 'εκεινον', 'σαν', 'ποση', 'οπουδηποτε', 'κάμποσες', 'οποιες', 'εκείνη', 'όλοι', 'καθετί', 'τέτοιον', 'ετουτο', 'οσωνδηποτε', 'εκείνους', 'μεσω', 'τοσα', 'κανέναν', 'κανενα', 'οποιου', 'εκαστα', 'μελει', 'παντως', 'τέτοιαν', 'τουτης', 'οποιδήποτε', 'αυτών', 'ιδια', 'τον', 'έκαστοι', 'να', 'ετέρου', 'οτου', 'καθεμιας', 'οποιωνδηποτε', 'τούτος', 'αρκετα', 'δικός', 'διχως', 'προχτές', 'συνάμα', 'οσωνδήποτε', 'βεβαιότατα', 'μονους', 'ποιές', 'σχεδόν', 'ετερου', 'εντωμεταξυ', 'ουδε', 'οποίαν', 'όλως', 'τριτη', 'τέτοιες', 'αι', 'προχθες', 'καλώς', 'ίδιοσ', 'τιποτα', 'μόνους', 'μεσώ', 'επιπλεον', 'ίδια', 'οποιουσδηποτε', 'ανά', 'βέβαια', 'οποίοι', 'κάτι', 'αυτούς', 'άλλη', 'οσον', 'κανείς', 'τελευταίος', 'ιδίας', 'τουτο', 'μεσα', 'λοιπα', 'οσοδηποτε', 'πόση', 'θα', 'ετούτην', 'μερικα', 'αλλαχου', 'τέτοιος', 'κατοπιν', 'τοσους', 'ιδιο', 'αλλιώς', 'έστω', 'τέτοιους', 'γι', 'έγκαιρα', 'χωρις', 'εκαστους', 'συχνων', 'οποιοσδήποτε', 'είχαν', 'όσους', 'μερικούς', 'οποιαν', 'ποιας', 'πόσες', 'καμποσος', 'αναμεταξυ', 'τρίτη', 'τούτον', 'οπότε', 'όλα', 'αλλιώτικα', 'πρωτη', 'επειτα', 'αλλιωτικα', 'εκεινην', 'ποσοι', 'ημουν', 'ανάμεσα', 'τώρα', 'πολλοι', 'ετερους', 'δικο', 'άλλην', 'νωρίς', 'πολλες', 'παντου', 'ηταν', 'καμίας', 'πολλους', 'ανωτερω', 'μόνοι', 'τι', 'ετεραι', 'ταυτου', 'δε', 'είμαστε', 'οποιας', 'ίσως', 'κανεν', 'ετούτους', 'έχει', 'έκαστη', 'επομενως', 'ώσπου', 'ενός', 'εκείνων', 'μαζι', 'απεναντι', 'μόνες', 'όποια', 'πρόπερσι', 'ποιαν', 'πού', 'μακρυά', 'άλλης', 'ποσος', 'πρώτη', 'οσηδηποτε', 'συναμα', 'άμεσα', 'μεταξυ', 'τουτοι', 'ωχ', 'προχθές', 'μερικων', 'κάποιας', 'ολον', 'τελευταίο', 'ολο', 'οποιαδηποτε', 'μολονότι', 'όποιος', 'ταδε', 'εδω', 'ουτε', 'επομενη', 'οποιανδηποτε', 'ποιον', 'πρεπει', 'κάμποσα', 'λοιπον', 'οποιουδήποτε', 'οσοιδηποτε', 'κατι', 'μονο', 'οσεσδηποτε', 'κανεις', 'ευτυχως', 'υπόψη', 'τες', 'ήσαστε', 'τετοιες', 'νωρις', 'προκειμενου', 'οσουσδήποτε', 'τετοιους', 'αλλην', 'τοι', 'ταύτες', 'δηθεν', 'συχνός', 'οποιων', 'κακώς', 'ήμαστε', 'όσων', 'είχες', 'χωριστα', 'αυτος', 'έκαστην', 'επισης', 'ιδιοσ', 'κάτω', 'μέσα', 'εαν', 'καμιαν', 'ξανα', 'όλου', 'μελλεται', 'πολλούς', 'είθε', 'καθεμίας', 'ναι', 'πολλές', 'τελικα', 'ήσασταν', 'κατ', 'δικοί', 'ίσαμε', 'πλάι', 'οι', 'τόσου', 'εκείνην', 'σου', 'κάποιος', 'μιας', 'επάνω', 'μ', 'αυτοι', 'οσονδηποτε', 'διαρκώς', 'συχνως', 'αντίς', 'τέτοια', 'τέτοιο', 'μονομιάς', 'εκαστης', 'άξαφνα', 'αλλον', 'ιδίως', 'είχατε', 'γυρω', 'ήτοι', 'μερικους', 'ενος', 'τίποτα', 'άλλοι', 'πουθενά', 'εκαστον', 'οσοιδήποτε', 'κανεναν', 'έως', 'καμια', 'οποιουδηποτε', 'αλλη', 'εαυτον', 'του', 'εμπρός', 'αλλης', 'πρωτα', 'καποιες', 'δίπλα', 'συχνοι', 'οσην', 'αλλοιώτικα', 'οπου', 'εκαστες', 'οσης', 'πλαι', 'ότι', 'αφοτου', 'συχνοί', 'ολως', 'εκάστου', 'εχουμε', 'ταυτα', 'μονος', 'καλά', 'σεις', 'όταν', 'πάντα', 'συχνούς', 'παντού', 'είσαστε', 'τούτην', 'τουτος', 'τοσης', 'επειδή', 'δήθεν', 'οσουσδηποτε', 'ωστόσο', 'στη', 'όσην', 'εφεξής', 'κοντά', 'αυτη', 'υπέρ', 'ήδη', 'ειχαν', 'αντίπερα', 'ειδεμή', 'οποιανδήποτε', 'οποιοι', 'οποιον', 'ολογυρα', 'καποιον', 'συχνή', 'κάποια', 'δηλαδη', 'τοτε', 'αντι', 'κυρίως', 'εντός', 'μητε', 'οποιοδηηποτε', 'έκαστον', 'εκεινοι', 'προτου', 'ετερας', 'ιδιας', 'οποτεδήποτε', 'τοσοι', 'καπου', 'ποσης', 'αμέσως', 'δεν', 'κάποιο', 'έγιναν', 'εαυτο', 'οποίας', 'πρωτο', 'μιαν', 'άλλες', 'ποιών', 'ιδιος', 'οποίου', 'εκεινων', 'τίποτε', 'εκείνο', 'ετερος', 'τετοιων', 'μακαρι', 'πάλι', 'ιδιων', 'αυτο', 'αυτόν', 'ειμαστε', 'στον', 'έγινε', 'απο', 'συχνώς', 'ηδη', 'οσηνδηποτε', 'ποιοι', 'ειχα', 'κανενας', 'ος', 'πλεον', 'οσα', 'τετοιο', 'εσείς', 'ετέρας', 'αν', 'γιατί', 'οσοσδήποτε', 'τοσου', 'απέναντι', 'ειχε', 'ιδιες', 'τούτοις', 'α', 'εκεινα', 'ήταν', 'εαυτούς', 'οσεσδήποτε', 'μονομιας', 'ολα', 'άνευ', 'ξαφνικά', 'συχνής', 'ολος', 'κάποτε', 'ακόμα', 'όλη', 'ήμουν', 'κατά', 'ποιοί', 'παρα', 'τόσες', 'ετουτου', 'προ', 'εχουν', 'ειμαι', 'ενα', 'ταχα', 'κάμποσον', 'τού', 'ο', 'οσοσδηποτε', 'μετ', 'κάποιοι', 'μεταξύ', 'συχνόν', 'πολλά', 'καποιο', 'εντελως', 'αλλιως', 'ίδιες', 'γιατι', 'ολόγυρα', 'εκείνου', 'καποια', 'κυριως', 'κάποιου', 'κάμποση', 'μονης', 'εσένα', 'ήττον', 'αλλο', 'τα', 'διολου', 'πόσης', 'ομως', 'πολύ', 'εκεί', 'μπορούν', 'δικά', 'κάπως', 'εαυτους', 'ετούτο', 'αυτων', 'ετέρα', 'πρέπει', 'ς', 'εχοντας', 'εισαι', 'πάρα', 'όποτε', 'ποιόν', 'ετουτους', 'πόσος', 'πίσω', 'ισαμε', 'όσο', 'μονων', 'οποτε', 'εκαστη', 'καποιων', 'κάμποσης', 'άλλα', 'ποιάς', 'άνω', 'πολυ', 'άλλοτε', 'ετούτων', 'ολοι', 'μόνων', 'ιδιαν', 'πια', 'οποτεδηποτε', 'αυτό', 'πάντοτε', 'ποιος', 'τελευταιος', 'εντελώς', 'ταυτοταυτον', 'ίδιος', 'δικοι', 'οποιο', 'έκανε', 'άρα', 'οσησδήποτε', 'ίδιων', 'τοσων', 'τωρα', 'μόνη', 'τοσ', 'επομένως', 'κάμποσοι', 'στις', 'αυτες', 'μεχρι', 'μονες', 'καποιου', 'υπ', 'μερικοι', 'πολλα', 'έναν', 'των', 'εξής', 'ολου', 'τόση', 'υπο', 'συν', 'έτερη', 'τις', 'εκτός', 'αλλοτε', 'ησουν', 'πέρσι', 'άμα', 'κακα', 'οποιωνδήποτε', 'συχνές', 'συχνό', 'αυτης', 'αρκετά', 'οποιεσδηποτε', 'διαρκως', 'περσι', 'μα', 'έτερες', 'πάντως', 'συχνάς', 'εαυτου', 'αυριο', 'προχτες', 'αναμεσα', 'διπλα', 'συχνης', 'έχω', 'ιδιον', 'κάποιους', 'ποτέ', 'κτλ', 'εδώ', 'ακριβως', 'εξω', 'εγιναν', 'εκαστοι', 'τυχόν', 'αλλαχού', 'λιγοτερο', 'ποιούς', 'χωριστά', 'θ', 'κοντα', 'έκαστες', 'έχουμε', 'ετερη', 'εκεινης', 'κάμποσην', 'παλι', 'καμποση', 'εκείνον', 'λοιπά', 'αλλοιως', 'τουτου', 'εκείνα', 'όσοι', 'αλλοιωτικα', 'μερικές', 'οσηδήποτε', 'αναμεταξύ', 'μερικες', 'ούτε', 'αλλες', 'μπρος', 'καμίαν', 'παντοτε', 'σας', 'εγκαιρα', 'προκειται', 'ετέραι', 'έχετε', 'εισαστε', 'καπως', 'μέλει', 'καμποσον', 'μαζί', 'πρωτες', 'τελικά', 'μη', 'καμποσα', 'ητοι', 'έξαφνα', 'καμποσην', 'εξ', 'εκείνες', 'καθενας', 'ολων', 'κατα', 'καθώς', 'πρωτυτερα', 'εχετε', 'είστε', 'εξαφνα', 'κανενός', 'στων', 'ετσι', 'ίδιον', 'τοσος', 'επόμενη', 'μακάρι', 'ευθύς', 'ετούτον', 'καθενα', 'την', 'εγινε', 'κάμποσου', 'κανενος', 'στο', 'τυχον', 'ετούτης', 'εγκαιρως', 'οταν', 'ταύτα', 'καποιας', 'τέτοιοι', 'μπορει', 'ταυτες', 'ορισμένα', 'στου', 'είχα', 'αλλους', 'οπουδήποτε', 'πόσοι', 'τρία', 'μονοι', 'τόσοι', 'κατω', 'όλες', 'εκτος', 'περίπου', 'ιδίου', 'εξαιτίας', 'ολονεν', 'ιδία', 'λόγω', 'ιδιοι', 'τοσο', 'έπειτα', 'ετερες', 'οποια', 'τούτων', 'περισσοτερο', 'κάμποσο', 'καθε', 'είσαι', 'ακομα', 'ποτε', 'αντί', 'τρεις', 'έχουν', 'τουτην', 'καθεμία', 'εσύ', 'καμία', 'ισια', 'καθετι', 'δεινα', 'ένα', 'ακριβώς', 'οποίο', 'όσος', 'καμποσης', 'τοσες', 'ανωτέρω', 'στην', 'έχομε', 'έτερης', 'οποιασδηποτε', 'ξανά', 'ορισμενα', 'όχι', 'ολωσδιολου', 'ποιό', 'κάποιον', 'ετέρων', 'τετοιοι', 'άλλο', 'τουλαχιστον', 'συχνου', 'πιθανον', 'συνεπως', 'τέτοιας', 'μεθαύριο', 'ολότελα', 'μείον', 'καθεμια', 'συχνην', 'ποιά', 'όλο', 'πλέον', 'εκεινη', 'υπερ', 'έτσι', 'τούτο', 'ετουτη', 'εσάς', 'οσονδήποτε', 'ταύτην', 'μονην', 'τόσην', 'όπως', 'έκαστης', 'όποιον', 'τούτα', 'όμως', 'απ', 'κιολας', 'αύριο', 'ολην', 'τουτη', 'εφεξης', 'ησασταν', 'ετερο', 'συχνος', 'μάλιστα', 'μηπως', 'τούτους', 'ωσάν', 'αφότου', 'αξαφνα', 'εγκαίρως', 'αυτού', 'οσοδήποτε', 'ενώ', 'κάνεν', 'άραγε', 'συχνον', 'ώστε', 'οποιος', 'ταύτου', 'εκάστους', 'αυτός', 'περι', 'πανω', 'εσεις', 'οποιεσδήποτε', 'πώς', 'ητανε', 'είχε', 'κάθε', 'οσες', 'αρκετές', 'της', 'είμαι', 'καθενος', 'ορισμένων', 'εκαστος', 'έχεις', 'εις', 'ίδιαν', 'μην', 'περα', 'τετοιον', 'εύγε', 'δα', 'συγχρόνως', 'ωστε', 'δείνα', 'δικούς', 'ετούτοι', 'ενας', 'καποιους', 'καποιοι', 'εαυτό', 'αυτα', 'ήτανε', 'αδιακοπα', 'τετοιος', 'κατιτί', 'ότου', 'υπόψιν', 'όσης', 'μαλιστα', 'αφου', 'ιδιου', 'ιδιως', 'πρώτα', 'έξι', 'αρα', 'ωσοτου', 'τελικως', 'εχω', 'συχνο', 'βεβαιοτατα', 'μόνην', 'ετούτα', 'ανω', 'περισσότερο', 'ισως', 'δικό', 'ποιο', 'ευτυχώς', 'ετερα', 'επίσης', 'ηττον', 'όποιες', 'ω', 'ταυτη', 'ποσες', 'οποία', 'δι', 'ημαστε', 'εάν', 'ετούτες', 'μερικά', 'τετοια', 'ταυτης', 'τετοιας', 'οσαδήποτε', 'τοσον', 'επειδη', 'ορισμένες', 'εξίσου', 'ανευ', 'έκαστα', 'εντωμεταξύ', 'πέρα', 'από', 'που', 'καμποσο', 'οπως', 'μόνου', 'ιι', 'εως', 'πουθενα', 'ποιες', 'ίδιοι', 'προς', 'μόνος', 'τοσην', 'έτεροι', 'κάπου', 'ετούτος', 'εξήσ', 'αυτους', 'όποιοι', 'ετουτα', 'δια', 'στης', 'υποψη', 'τουτων', 'ταύτοταύτον', 'τόσος', 'αντις', 'ταύτης', 'τέτοιων', 'οχι', 'ωστοσο', 'άλλον', 'όσου', 'καμποσου', 'καθένας', 'τούς', 'ειχαμε', 'τοση', 'ειθε', 'εκεινες', 'εξι', 'οποιουσδήποτε', 'ουδέ', 'τούτη', 'κιόλας', 'έχοντας', 'έκαστο', 'μερικοί', 'πρώτο', 'κανένας', 'μάλλον', 'είχαμε', 'οσουδηποτε', 'προκειμένου', 'οποιονδήποτε', 'ειχες', 'κακά', 'ορισμενων', 'αντιπερα', 'εχομε', 'μειον', 'υποψιν', 'παντα', 'όποιο', 'κακως', 'ταύτων', 'άλλων', 'οποιδηποτε', 'ησαστε', 'καθένα', 'τετοιου', 'μονου', 'καμιας', 'αφού', 'κατόπιν', 'ι', 'ειστε', 'έξω', 'λιγακι', 'καθολου', 'μηδε', 'κάμποσους', 'τόσους', 'όλος', 'συχνας', 'έτερους', 'η', 'συχνες', 'ετούτου', 'ετουτης', 'συχνους', 'αυτον', 'οποίων', 'εαυτού', 'τούτοι', 'οσοι', 'και', 'τουτοις', 'εκείνης', 'αρχικά', 'δίχως', 'εκεινο', 'εαυτόν', 'ποιων', 'κάποιαν', 'μονη', 'αυτής', 'γρηγορα', 'εαυτών', 'ορισμένως', 'οποιοδηήποτε', 'πλην', 'ετουτος', 'καποιος', 'εκαστην', 'πρώτες', 'εκεινος', 'οσησδηποτε', 'μια', 'τάχατε', 'ευθυς', 'μετα', 'μήδε', 'είναι', 'λιγο', 'οτι', 'πόσην', 'ωσαν', 'οποιαδήποτε', 'τουτα', 'άλλους', 'οσηνδήποτε', 'συγχρονως', 'μολις', 'μήτε', 'ξαφνικα', 'εντος', 'ταυτος', 'λιγάκι', 'είτε', 'εχεις', 'τόσον', 'ποιου', 'μέσω', 'ταυτων', 'κ', 'αυτήν', 'δικος', 'ακόμη', 'εναντίον', 'τούτης', 'ολους', 'συχνήν', 'καθόλου', 'τουτους', 'δικα', 'μεθαυριο', 'εξαιτιας', 'εκανε', 'εαυτων', 'ποιός', 'ετεροι', 'ταυτην', 'αλλά', 'οση', 'ωσπου', 'οσου', 'τελευταιο', 'αποψε', 'ειτε', 'οποίους', 'επί', 'ποια', 'μολονοτι', 'καποτε', 'καλα', 'τιποτε', 'αυτή', 'κάμποσων', 'εναν', 'τουτον', 'ταχατε', 'ετουτον', 'οσων', 'πέρι', 'ως', 'οσος', 'όση', 'εχτες', 'εξησ', 'εμπρος', 'κλπ', 'τελευταία', 'τόσων', 'καμποσων', 'μετά', 'δικους', 'οσους', 'ολες', 'ορισμενες', 'επι', 'ένας', 'ειναι', 'δικου', 'πριν', 'εκείνος', 'σχεδον', 'μόνο', 'πισω', 'όλην', 'εσυ', 'ημασταν', 'εξης', 'οσαδηποτε', 'μέχρι', 'ευγε', 'ας', 'ποιάν', 'τετοιαν', 'εξισου', 'ολοτελα', 'ίδιους', 'κάποιων', 'πιθανόν', 'μέλλεται', 'ίδιο', 'ολη', 'έτερον',  'ολης', 'ενω', 'οποιονδηποτε', 'το', 'μόλις', 'αμα', 'έτερος', 'μπορουν', 'πέρυσι', 'στα', 'τόσα', 'προτού', 'εστω', 'τρια', 'οποιοσδηποτε', 'τάχα', 'δικού', 'επανω', 'ετούτη', 'βεβαια', 'εσενα', 'πότε', 'ορισμενως', 'μακρυα', 'ετερων', 'υστερα', 'αρχικα', 'αυτές', 'οτιδήποτε', 'εχει', 'όλης', 'ποιους', 'συχνη', 'στους', 'αλλού', 'για', 'καμποσους', 'όσα', 'τελικώς', 'μεν', 'τάδε', 'οσο', 'κανένα', 'ιδιους', 'ιιι', 'πρωτος', 'άλλος', 'μαλλον', 'λογω', 'ανα', 'οποίες', 'αμεσως', 'τη', 'τουλάχιστο', 'ετουτην', 'συχνών', 'αμεσα', 'ολονέν', 'συχνού', 'οποίος', 'όλον', 'πως', 'ολωσδιόλου', 'εκαστων', 'ωσότου', 'απόψε', 'αλλος', 'επιπλέον', 'σε', 'ετερης', 'πρόκειται'}
sp = spacy.load('el_core_news_md')
tweets = pd.read_csv("C:\\Users\\User\\Desktop\\Διπλωματική\\batch.csv")
token_dict = {}   


def generate_ngrams(token, n):
    ngrams = zip(*[token[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
                  
def get_tokens(tweets):
    count = 0
    for id in tweets['id']:    
        try:
            count = count+1
            print (count)
            place = tweets.loc[tweets['id'] == id,"place"].iloc[0]
            if(place == "e"):
                continue
            text = sp( ( tweets.loc[tweets['id'] == id,"text"].iloc[0] ).lower() );
            indexes = [m.span() for m in re.finditer('#\w+',(tweets.loc[tweets['id'] == id,"text"].iloc[0] ).lower(),flags=re.IGNORECASE)];#φιτανχει χαςταγκ
            for start,end in indexes:
                text.merge(start_idx=start,end_idx=end); #ftiakse to printarisma twn hashtag
            
            tokens = [strip_accents(token.text) for token in text if ( ( not token.is_space \
                                                                        and not token.is_stop\
                                                                        and not token.is_oov\
                                                                        and not token.is_punct\
                                                                        and not token.like_num \
                                                                        and not token.like_url ) or ( keyword_dict.get( strip_accents(token.text) ) ) ) ]
            
            token_dict[id] = tokens
        except Exception as inst:
            error_file.write("ID %s Error %s " % ( tweet_id ,inst))
    return token_dict        
    
def get_count(tweet_tokens): #υπολογίζει τον αριθμό των tweets στα οποία εμφανίζεται η κάθε λέξη 
    token_count = {}
    count = 0
    for tweet in tweet_tokens: #iter einai o arithmos twn tweets    
        try:
            count = count+1
            #print (count)
            counts = Counter(tweet_tokens[tweet]) # ftoakse dict me ton arithmo emfanisewn sto sygkekrimeno tweet
            seen = {}
            for token in tweet_tokens[tweet]:
                if (token not in keyword_dict):
                    if (token in seen):
                        continue
                    if (token in token_count):
                        token_count[token]+= counts[token]
                    else:
                        token_count[token] = counts[token]
                    seen[token] = "yes"
                else:
                    if (token in seen):
                        continue
                    if (keyword_dict[token] in token_count):
                        token_count[keyword_dict[token]]+= counts[token]
                    else:
                        token_count[keyword_dict[token]]= counts[token]
                    seen[token] = "yes"
            #token_freq.update(Counter(token_dict[iter]))
        #for iter in token_count:
            #print ((iter,token_count[iter] ),'\n') # ftiakse to counter sthn arxh epaize alla meta diagrafei prouparxouses times
        except Exception as inst:
            error_file.write("ID %s Error %s " % ( tweet ,inst))
            continue
    return token_count

def heavy_tokens(token_count,tweet_tokens):
    heavy_tokens_dict = defaultdict(list)# einai dict of lists
    for tweet in tweet_tokens:
        for token in tweet_tokens[tweet]:
            if token in keyword_dict:
                if token_count[keyword_dict[token]] >=5:
                #if tweet in heavy_tokens_dict:
                    heavy_tokens_dict[tweet].append(token)
            else:
                if token_count[token] >=5:
                #if tweet in heavy_tokens_dict:
                    heavy_tokens_dict[tweet].append(token)
    return heavy_tokens_dict
    
def make_vec (token_dict): #
    vectors = defaultdict(list)
    count = 0
    for tweet in token_dict:
        try:
            count=count+1
            print(count)
            for token in token_dict[tweet]:
                if(keyword_dict.get(strip_accents(token))):
                    doc = sp(keyword_dict.get(strip_accents(token)))
                    vectors[tweet] = np.concatenate((vectors[tweet],doc.vector),axis=0)     
                else:
                    doc = sp(token)
                    vectors[tweet] = np.concatenate((vectors[tweet],doc.vector),axis=0)
        except Exception as inst:
            error_file.write("ID %s Error %s " % ( tweet ,inst))
            continue
    return vectors

def f_tf_idf(token_dict):
    tf_idf = collections.defaultdict(dict)
    doc_number = len(token_dict)
    for tweet in token_dict:
        try:
            tweet_length = len(token_dict[tweet]) #posa tokens exei to kathe tweet
            buffer = [] #edw tha bazw to tfidf gia kathe token
            counts = Counter(token_dict[tweet])
            for token in counts:
                if (token in keyword_dict):
                    buffer.append( ( counts[token]/tweet_length )*math.log(doc_number/token_count[keyword_dict[token]]) )
                else:
                    buffer.append( ( counts[token]/tweet_length )*math.log(doc_number/token_count[token]) )
            tf_idf[tweet] = buffer
        except Exception as inst:
            error_file.write("ID %s Error %s " % ( tweet ,inst))
            continue
    return tf_idf
  
def find_county(tweet_id):
    place = tweets.loc[tweets['id'] == tweet_id,"place"].iloc[0]
    split = place.split(',')
    #print(split)
    try:
        if ('Περιφέρεια' in place ): # an den einai mono ellada
            my_index = 0
            for index in range(len(split)):
                if ("Περιφέρεια" in split[index]):
                    my_index = index
                    place  = split[my_index].replace("[","")
                    place  = split[my_index].replace("]","")
                    for item in counties:
                        if item in place:
                            place = item
                    return place
    except Exception as inst:
        error_file.write("ID %s Error %s " % ( tweet_id ,inst))
        return ""
    return ""       
    
def get_dist(x):
    if (x == 'county'):
        for tweet_id in tweets['id']:
            county = find_county(tweet_id)
            if (county!=""):
                if not county in distribution['county']: #an de to exw ksanabalei bale to 
                    distribution['county'][county] = 1
                else:    #alliws auksise to
                    distribution['county'][county] += 1
    if x == 'keyword':
        distribution['keyword'] = get_count(token_dict)
    if x == 'count_key':
        for id in token_dict:
            counts = Counter(token_dict[id])
            for token in counts:
                if(keyword_dict.get(strip_accents(token))):
                    county = find_county(id)
                    if (county!=""):
                        if (keyword_dict.get(strip_accents(token)) in double_distribution[county]):
                            double_distribution[county][keyword_dict[strip_accents(token)]]+=1
                        else :
                            double_distribution[county][keyword_dict[strip_accents(token)]] = 1
                       
def is_personal(tweet_id):
    for token in token_dict[tweet_id]:
        if(keyword_dict.get(strip_accents(token))):
            if (keyword_dict.get(strip_accents(token))=='εγώ'):
                return 1
    return 0            

def get_weather_info(tweet_id):
    info_row = []
    name= " "
    place = find_county(tweet_id)
    timestamp = tweets.loc[tweets['id'] == tweet_id,"date"].iloc[0]
    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    week = datetime.date(dt).isocalendar()[1]
    found = 0
    extra = ['Σεπτέμβριο','Οκτώβριο','Νοέμβριο','Δεκέμβριο']
    if(dt.year==2019 and (months[dt.month-1] in extra)):
       # print("This is null")
        info_row = [week,-999,-999,-999,-999,-999,-999]
        return info_row
    for filename in os.listdir('C:\\Users\\User\\Desktop\\Διπλωματική\\meteo_files'):
        try:
            if (place == ""):
                info_row = [week,-999,-999,-999,-999,-999,-999]
                break
            if ( (geo_map[place] in filename ) and (months[dt.month-1] in filename) and (str(dt.year) in filename) and filename.endswith(".csv") ):
                #print(filename)
                name = 'C:\\Users\\User\\Desktop\\Διπλωματική\\meteo_files\\'+geo_map[place] + " "+ str(dt.year) + " " + months[dt.month-1]+".csv"
                dataframe = pd.read_csv(name)
                day_row = dataframe.iloc[[dt.day-1]]
                info_row.append(week)
                for category in categories:
                    if(category not in day_row):
                        info_row.append(-999)
                    else:
                        #print(round(day_row[category][dt.day-1] , 3))
                        info_row.append(round(day_row[category][dt.day-1] , 3)) #3 digits precision
                found = 1
                break    
        except Exception as inst:
            print(inst)
            print("this is thw filename :" +  str(filename))
            print("this is the name = " + name)
            continue
    if(found==0):
        #print("this was null")
        info_row = [week,-999,-999,-999,-999,-999,-999]
    return info_row
    
def normalize(dict):
    min=0;max=0
    norm  = lambda x: 2*(x-min)/(max-min) -1
    vectorized_norm = np.vectorize(norm)
    norm_tf_idf = {}
    norm_vectors = {}
    if(type( dict[random.choice(list(dict.keys()))] ) == list): # if its not numpy array
        for key in dict:
            if key in null_keys:
                continue
            if(len(dict[key])>0):            
                if (np.amin(np.asarray(dict[key]))<min):
                    min = np.amin(np.asarray(dict[key]))
                elif (np.amax(np.asarray(dict[key]))>max):
                    max = np.amax(np.asarray(dict[key]))
        for key in dict:
            if key in null_keys:
                continue
            if(len(dict[key])>0):
                length = len(dict[key])#added that
                norm_tf_idf[key] = np.asarray(vectorized_norm(dict[key]))
                #norm_tf_idf[key] = np.pad( np.asarray(vectorized_norm(dict[key])) , (0,30-length) )  
        return dict_to_numpy(norm_tf_idf,30)
    else:                                                 # if it already is
        for key in dict:
            if(key in null_keys):
                continue
            if(len(dict[key])>0): 
                if (np.amin(dict[key])<min):
                    min = np.amin(dict[key])
                elif (np.amax(dict[key])>max):
                    max = np.amax(dict[key])
        for key in dict:
            if(key in null_keys):
                continue
            if(len(dict[key])>0):
                length2 = len(dict[key]) #added that
                norm_vectors[key] = vectorized_norm(dict[key])
                #norm_vectors[key] = np.pad( np.reshape(vectorized_norm(dict[key]),(int(length2/300),300)) , ((0,9000-length2),(0,0) ) )
        return dict_to_numpy(norm_vectors,300)

def write_to_csv(dict): # αυτες τις 2 φτιαχτες , περνα σαν παραμετρο τπτ αλλο γτ παιρνει μνημη
    number = 0
    myfile = open("rest_data.csv", "w",encoding='utf8',newline='')  
    w = csv.writer(myfile)
      # ftiakse kai auto edw gia to csv
    w.writerow(['ID','Personal','County','Week','Temp','Max Temp','Min Temp','Rain','AWS','Max Wind'])
    for key in dict:
        if key in null_keys:
            continue
        number+=1
        place = find_county(key)
        meteo = get_weather_info(key) 
        w.writerow([key,is_personal(key),place,*meteo])     
        print("wrote " + str(number))
    myfile.flush()  

def dict_to_numpy(dict,pad_length):
    count = 0
    if(pad_length == 300):
        for key in dict:
            if(len(dict[key])<9000):
                value = np.pad(dict[key],(0,9000-len(dict[key])))
            else: 
                value = dict[key]
            if(count==0):
                final = value
                count+=1
                #print(value) 
                #print(final)
                final = np.stack((final,value),axis=0)
                continue
            #print(value) 
            #print(final)
            final = np.vstack([final,value])
    else:    
        for key in dict:
            if(len(dict[key])<30):
                value = np.pad(dict[key],(0,30-len(dict[key])))
            else: 
                value = dict[key]
            if(count==0):
                final = value
                count+=1
               # print(value) 
                #print(final)
                final = np.stack((final,value),axis=0)
                continue
            #print(value) 
            #print(final)
            final = np.vstack([final,value])
    return final

for word_string in keywords:
    word_list = word_string.split(",")
    for word in word_list[1:]:
        keyword_dict[word] = word_list[0] 

for w in stop_words:
    sp.vocab[w].is_stop = True

error_file = open("Prep Errors.txt",'w')

token_dict = get_tokens(tweets) #kane ta tokens

token_count = get_count(token_dict) #bres to count tou kathe token στο dict που σου δινω

vector_dict = make_vec(token_dict)

tf_idf = f_tf_idf(token_dict)

null_keys=[]
keys = []  
for key in tf_idf:
    place = find_county(key)
    if(place == ""):
        null_keys.append(key)
        continue
    keys.append(key) 
      
norm_tf = normalize(tf_idf)
norm_vec = normalize(vector_dict)

write_to_csv(keys) 

df = pd.read_csv("C:\\Users\\User\\Desktop\\Διπλωματική\\twitter_files\\rest_data.csv")
with open('batch_keys.txt', 'w') as f:
    for item in keys:
        f.write("%s,%s,%s\n" % (item , df.loc[df['ID'] == item,"County"].iloc[0], df.loc[df['ID'] == item,"Week"].iloc[0]))
max_abs_scaler = preprocessing.MaxAbsScaler()
col_names= ['Week','Temp','Max Temp','Min Temp','Rain','AWS','Max Wind']

scaler = max_abs_scaler.fit(df[col_names].values)
features = scaler.transform(df[col_names].values)
df[col_names] = features

df.to_csv('Norm Features.csv')

numpy_rest = df.drop(columns=['ID','County','Week']).to_numpy()

np.save('Norm Vectors.npy',norm_vec)
np.save('Norm Tf-Idf.npy',norm_tf)
np.save('Norm Rest.npy',numpy_rest)



process = psutil.Process(os.getpid())
print(process.memory_info()[0])


