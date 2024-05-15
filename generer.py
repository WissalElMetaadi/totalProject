from fpdf import FPDF
# Create the instance of FPDF class for the complete cahier des charges, with adjusted text to avoid encoding issues
pdf_full = FPDF()

# Add a page
pdf_full.add_page()

# Set font and add a main title
pdf_full.set_font("Arial", 'B', 16)
pdf_full.cell(0, 10, "Cahier des Charges", ln=True, align='C')
pdf_full.cell(0, 10, "Systeme de Vision par Ordinateur pour la Station-Service Total Tunisie", ln=True, align='C')
pdf_full.ln(10)

# Introduction
pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "I. Introduction", ln=True)
pdf_full.set_font("Arial", size=10)
intro_text = (
    "Ce document definit les specifications et les exigences necessaires pour le developpement et la mise en oeuvre d'un "
    "systeme avance de vision par ordinateur a la station-service Total Tunisie. Le projet vise a ameliorer l'efficacite "
    "operationnelle, la securite, l'experience utilisateur, tout en integrant des elements de marketing cible et de durabilite "
    "environnementale."
)
pdf_full.multi_cell(0, 10, intro_text)

# Objectives
pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "II. Objectifs du Projet", ln=True)
pdf_full.set_font("Arial", size=10)
objectives_text = (
    "Optimisation Operationnelle: Automatisation du suivi du trafic et des services pour une gestion plus efficace des ressources, "
    "reduction des temps d'attente lors des pics d'affluence. Securite Amelioree: Installation de systemes de surveillance avances pour "
    "augmenter la securite des clients et du personnel. Experience Client Amelioree: Developpement d'interfaces utilisateur intuitives "
    "pour faciliter l'acces aux services et informations de la station. Marketing Cible: Utilisation des donnees collectees pour offrir des "
    "promotions et des services personnalises aux moments les plus opportuns. Developpement Durable: Emploi de technologies qui reduisent "
    "l'empreinte ecologique de la station-service et ameliorent l'efficacite energetique."
)
pdf_full.multi_cell(0, 10, objectives_text)

# Key Features
pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "III. Fonctionnalites Cles", ln=True)
pdf_full.set_font("Arial", size=10)
features_text = (
    "Detection et Classification des Vehicules: Utilisation de modeles avances comme YOLOv8 pour identifier et classifier les types de vehicules "
    "en temps reel. Reconnaissance des Plaques d'Immatriculation: Integration de technologie OCR pour capturer et analyser les plaques, facilitant "
    "le suivi precis des vehicules. Analyse de Trafic et Reporting: Comptage des vehicules par categorie et par zone (entree, sortie, lavage, etc.), "
    "analyse des tendances de trafic pour une gestion proactive des ressources. Interfaces Utilisateurs: Creation de dashboards specifiques pour "
    "differents types d'utilisateurs: administrateurs, clients, techniciens, et analystes."
)
pdf_full.multi_cell(0, 10, features_text)

pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "III. Fonctionnalites Cles", ln=True)
pdf_full.set_font("Arial", size=10)
features_text = (
    "Detection et Classification des Vehicules: Utilisation de modeles avances comme YOLOv8 pour identifier et classifier les types de vehicules "
    "en temps reel. Reconnaissance des Plaques d'Immatriculation: Integration de technologie OCR pour capturer et analyser les plaques, facilitant "
    "le suivi precis des vehicules. Analyse de Trafic et Reporting: Comptage des vehicules par categorie et par zone (entree, sortie, lavage, etc.), "
    "analyse des tendances de trafic pour une gestion proactive des ressources. Interfaces Utilisateurs: Creation de dashboards specifiques pour "
    "differents types d'utilisateurs: administrateurs, clients, techniciens, et analystes."
)
pdf_full.multi_cell(0, 10, features_text)








# Continuing to add the remaining sections to the PDF

# IV. Specifications Techniques
pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "IV. Specifications Techniques", ln=True)
pdf_full.set_font("Arial", size=10)
specs_text = (
    "Materiel: Le projet tirera parti des cameras CCTV deja installees par Total pour la surveillance. Cela permet une integration efficace "
    "avec l'infrastructure existante, reduisant les couts et accelerant le deploiement du systeme. Capacite de Traitement: En raison des ressources "
    "disponibles actuellement, le traitement des donnees se fera de maniere non temps reel. Les ordinateurs de haute performance seront utilises pour "
    "gerer le flux de donnees, assurant une analyse efficace sans necessiter un traitement immediat. Logiciels et Processeurs: Nous utiliserons des "
    "logiciels avances et des processeurs adaptes pour optimiser la gestion des donnees et l'analyse. Cette approche permet de maximiser les performances "
    "des systemes en place tout en preparant le terrain pour des ameliorations futures lorsque des ressources supplementaires deviendront disponibles."
)
pdf_full.multi_cell(0, 10, specs_text)

# V. Exigences Operationnelles
pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "V. Exigences Operationnelles", ln=True)
pdf_full.set_font("Arial", size=10)
operational_text = (
    "Formation et Support: Mise en place de programmes de formation pour tous les utilisateurs du systeme et fourniture d'un support technique continu. "
    "Maintenance: Etablissement d'un calendrier de maintenance reguliere pour garantir le fonctionnement optimal du systeme."
)
pdf_full.multi_cell(0, 10, operational_text)

# VI. Livrables
pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "VI. Livrables", ln=True)
pdf_full.set_font("Arial", size=10)
deliverables_text = (
    "Systeme Complet: Livraison d'un systeme de vision par ordinateur fonctionnel et teste. Documentation Technique: Fourniture de manuels d'utilisation, "
    "de guides de maintenance et de documentation technique detaillee. Rapports de Validation: Presentation de rapports detailles demontrant la conformite "
    "aux exigences et l'efficacite du systeme."
)
pdf_full.multi_cell(0, 10, deliverables_text)

# VII. Calendrier
pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "VII. Calendrier", ln=True)
pdf_full.set_font("Arial", size=10)
schedule_text = (
    "Planification: Le projet sera execute en phases distinctes, chacune avec des jalons clairement definis pour assurer le suivi et l'evaluation des progres."
)
pdf_full.multi_cell(0, 10, schedule_text)

# VIII. Budget
pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "VIII. Budget", ln=True)
pdf_full.set_font("Arial", size=10)
budget_text = (
    "Estimations Budgetaires: Preparation d'un budget detaille qui couvre tous les aspects du projet, y compris le materiel, le logiciel, le developpement, "
    "la formation et le support."
)
pdf_full.multi_cell(0, 10, budget_text)

# IX. Responsabilites
pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "IX. Responsabilites", ln=True)
pdf_full.set_font("Arial", size=10)
responsibilities_text = (
    "Roles des Parties Prenantes: Definition precise des responsabilites pour chaque intervenant, assurant une collaboration efficace et une execution fluide du projet."
)
pdf_full.multi_cell(0, 10, responsibilities_text)

# X. Approbations
pdf_full.set_font("Arial", 'BU', 12)
pdf_full.cell(0, 10, "X. Approbations", ln=True)
pdf_full.set_font("Arial", size=10)
approvals_text = (
    "Processus d'Approbation: Obtention des approbations necessaires de toutes les parties prenantes avant de proceder a la phase de developpement pour garantir "
    "l'alignement et le soutien tout au long du projet."
)
pdf_full.multi_cell(0, 10, approvals_text)





# Save the complete PDF
pdf_output_path = "Cahier_des_Charges_Complet_Final.pdf"
pdf_full.output(pdf_output_path)

pdf_output_path
